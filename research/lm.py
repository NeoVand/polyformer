"""
Language models for the arity question: bytes (enwik8) or GPT-2 tokens (TinyStories, FineWeb-Edu).

    gpt     softmax attention + MLP, pre-LayerNorm, L layers
    hybrid  the same, plus a causal Newton attention branch beside each attention, MLP narrowed
    newton  Newton attention in place of softmax attention
    sfa     free-field attention: softmax attention whose weights also feed Newton's identities, so every
            arity up to K reads distinct subsets of the tokens the query selects (MLP narrowed); with
            --hops R it also reads walks A^l V (l = 2..R) along the same causal attention, and with
            --lookback each key first looks back along a learned causal hop (see walk_sector below)
    lla     ridge local-linear attention in a learned r-dimensional chart per head (--chart r): each query
            fits v ~ b0 + b1 (c_j - c_i) by weighted ridge least squares under its softmax weights and
            reads b0; a per-head gate starts at zero, so the layer starts as softmax (LOCAL.md)
    plx     Parallax (Zuo et al. 2026): softmax weights times (1 - rho_i.(k_j - kbar_i)), probe rho = W_R x,
            W_R = 0 at init

--opt muon trains the hidden matrices with Muon (Newton-Schulz, Moonlight's RMS matching) and everything
else with the same AdamW as --opt adamw.

Causal Newton attention: position t sees the tokens before it. Power sums are exclusive prefix
sums, P_j(t) = sum_{s<t} phi_s^j; Newton's identities give e_m(t), the sum over m-subsets of
earlier tokens; normalised by C(t, m) and multiplied by the query's own phases, they are the
arity m+1 features. The state is a fixed number of running sums: linear time, streaming.

    python research/lm.py --arch hybrid --steps 8000 --seed 0                       # enwik8 bytes
    python research/lm.py --arch sfa --data /data/tinystories --vocab 50304 \
        --ctx 512 --d 512 --layers 6 --heads 8 --tokens 400000000 --bf16 1          # GPT-2 tokens

prints one JSON line: the curve of held-out loss against steps, tokens and training FLOPs (every
power-sum and walk pass counted), plus induction probes when the context allows them.
"""

import argparse
import json
import math
import os
import pickle
import sys
import tempfile
import time

import jax
import jax.numpy as jnp
import numpy as np
import optax

BEYOND_ARCHS = ("beyond_a", "beyond_b", "beyond_c", "gated_delta", "prefix")
QKV_CONV_ARCHS = ("gpt", "plx", "beyond_a", "beyond_b", "beyond_c")


def qkv_conv_width(cfg):
    """Validate the optional shared attention-locality module; zero disables it."""
    width = getattr(cfg, "qkv_conv", 0)
    if type(width) is not int or width < 0:
        raise ValueError("qkv_conv must be a nonnegative integer")
    if width and cfg.arch not in QKV_CONV_ARCHS:
        raise ValueError(f"qkv_conv is supported only for {QKV_CONV_ARCHS}, not {cfg.arch!r}")
    return width


def load(path="/root/enwik8"):
    if os.path.isdir(path):
        # tokenised corpus: uint16 GPT-2 ids written once by modal_run.tokenize
        mm = lambda n: np.memmap(os.path.join(path, n), dtype=np.uint16, mode="r")
        return mm("train.bin"), mm("val.bin")
    # enwik8's standard split is 90M / 5M / 5M bytes; smaller files split in the same proportion
    data = np.frombuffer(open(path, "rb").read(), dtype=np.uint8)
    n = len(data)
    return data[: n * 9 // 10], data[n * 9 // 10 : n * 19 // 20]


def dense(key, i, o, scale=1.0):
    return {"w": jax.random.normal(key, (i, o)) * scale / math.sqrt(i), "b": jnp.zeros(o)}


MM = None  # set to jnp.bfloat16 by --bf16: matmuls in bf16 with float32 accumulation


def mm(a, b, spec=None):
    if MM is None:
        return jnp.einsum(spec, a, b) if spec else a @ b
    a, b = a.astype(MM), b.astype(MM)
    if spec:
        return jnp.einsum(spec, a, b, preferred_element_type=jnp.float32)
    return jnp.matmul(a, b, preferred_element_type=jnp.float32)


def lin(p, x):
    return mm(x, p["w"]) + p["b"]


def ln_init(d):
    return {"g": jnp.ones(d), "b": jnp.zeros(d)}


def ln(p, x):
    mu = x.mean(-1, keepdims=True)
    var = ((x - mu) ** 2).mean(-1, keepdims=True)
    return (x - mu) / jnp.sqrt(var + 1e-5) * p["g"] + p["b"]


def init(key, cfg):
    D, L, T = cfg.d, cfg.layers, cfg.ctx
    conv_width = qkv_conv_width(cfg)
    ks = iter(jax.random.split(key, 16 + 16 * L))
    p = {"emb": jax.random.normal(next(ks), (cfg.vocab, D)) * 0.02, "pos": jax.random.normal(next(ks), (T, D)) * 0.02,
         "lnf": ln_init(D), "layers": []}
    for _ in range(L):
        lyr = {"ln1": ln_init(D), "ln2": ln_init(D)}
        if cfg.arch in ("gpt", "hybrid", "sfa", "lla", "plx") + BEYOND_ARCHS:
            lyr["qkv"] = dense(next(ks), D, 3 * D)
            lyr["o"] = dense(next(ks), D, D, scale=1 / math.sqrt(2 * L))
        if cfg.arch == "sfa":
            H, r, K = cfg.heads, cfg.rank, cfg.order
            lyr["th"] = dense(next(ks), D, H * r)
            lyr["g"] = dense(next(ks), D, H * r)
            lyr["no"] = dense(next(ks), H * 2 * r, D, scale=1 / math.sqrt(2 * L))
            # --alpha0: arities 2..K start switched off, so the layer starts as softmax attention
            # --fscale: the per-arity scale acts on the features, so the shared read-out runs once, not K times
            width = H * 2 * r if getattr(cfg, "fscale", 0) else D
            # --alpha0 1: arities 2..K start at zero; --alpha0 2: every arity does, so the layer starts as softmax
            lyr["alpha"] = jnp.ones((K, width)).at[1:].set(0.0 if cfg.alpha0 else 1.0).at[0].set(0.0 if cfg.alpha0 == 2 else 1.0)
        if cfg.arch in ("gpt", "sfa") and cfg.hops > 1:
            # walks A^l V for l = 2..R share the read-out o; their scales start at zero
            lyr["beta"] = jnp.zeros((cfg.hops - 1, D))
        if cfg.arch in ("gpt", "sfa") and cfg.lookback:
            # look-back hop on the keys: its own small queries and keys; the mix starts at zero
            lyr["lbq"] = dense(next(ks), D, cfg.heads * cfg.lbdim)
            lyr["lbk"] = dense(next(ks), D, cfg.heads * cfg.lbdim)
            lyr["gamma"] = jnp.zeros((cfg.heads, 1, D // cfg.heads))
        if cfg.arch in ("hybrid", "newton"):
            H, r, K = cfg.nheads, cfg.rank, cfg.order
            lyr["lnn"] = ln_init(D)
            lyr["th"] = dense(next(ks), D, H * r)
            lyr["g"] = dense(next(ks), D, H * r)
            lyr["no"] = dense(next(ks), H * 2 * r, D, scale=1 / math.sqrt(2 * L))
            lyr["alpha"] = jnp.ones((K, D))
        lyr["fc1"] = dense(next(ks), D, cfg.mlp)
        lyr["fc2"] = dense(next(ks), cfg.mlp, D, scale=1 / math.sqrt(2 * L))
        p["layers"].append(lyr)
    # local-regression parameters come from their own key stream, so every weight the layer shares with
    # softmax attention is initialised exactly as in the gpt model at the same seed
    xk = iter(jax.random.split(jax.random.fold_in(key, 7), L))
    for lyr in p["layers"]:
        H, dh = cfg.heads, D // cfg.heads
        if cfg.arch == "plx" and getattr(cfg, "plx_norm", 0):
            # as published: random W_R and an RMSNorm on rho over the head dimension (Qwen-3 style, one gain
            # vector shared by the heads); the gain starts at zero so the layer starts as softmax
            lyr["wr"] = dense(next(xk), D, D)
            lyr["rho_g"] = jnp.zeros(dh)
        elif cfg.arch == "plx":
            lyr["wr"] = {"w": jnp.zeros((D, D)), "b": jnp.zeros(D)}
        if cfg.arch == "lla":
            # chart R (r x dh per head): small and random, never zero (R = 0 is a saddle: the correction is
            # quadratic in R); ridge lambda per head through softplus; gate g per head at zero
            lyr["chart"] = jax.random.normal(next(xk), (H, cfg.chart, dh)) * cfg.chart_init / math.sqrt(dh)
            lyr["lam"] = jnp.full((H,), math.log(math.expm1(cfg.lam0)))
            lyr["gate"] = jnp.zeros((H,))
    if cfg.arch in BEYOND_ARCHS:
        import beyond_layers
        extra_keys = jax.random.split(jax.random.fold_in(key, 701), L)
        for lyr, ek in zip(p["layers"], extra_keys):
            extra = beyond_layers.init_layer(ek, cfg)
            # Keep the common QKV/output and MLP draw stream exactly matched to GPT.
            lyr.update({k: v for k, v in extra.items() if k not in ("qkv", "o")})
            if cfg.arch in ("gated_delta", "prefix"):
                lyr.pop("qkv")
                lyr.pop("o")
                lyr.update({k: v for k, v in extra.items() if k in ("qkv", "o")})
    if conv_width:
        import beyond_layers
        # Separate shared seed stream, after BEYOND extras: S/P/A/B/C receive
        # identical kernels, and every pre-existing model parameter is unchanged.
        conv_keys = jax.random.split(jax.random.fold_in(key, 703), L)
        for lyr, conv_key in zip(p["layers"], conv_keys):
            lyr["qkv_conv"] = beyond_layers.init_qkv_conv(conv_key, D, conv_width)
    return p


def project_qkv(lyr, x):
    """Project Q/K/V, then apply optional causal depthwise FIR without activation."""
    packed = lin(lyr["qkv"], x)
    if "qkv_conv" in lyr:
        import beyond_layers
        packed = beyond_layers.causal_depthwise_conv(packed, lyr["qkv_conv"])
    return jnp.split(packed, 3, -1)


def softmax_attention(cfg, lyr, x):
    B, T, D = x.shape
    H = cfg.heads
    q, k, v = project_qkv(lyr, x)
    sh = lambda t: t.reshape(B, T, H, D // H).transpose(0, 2, 1, 3)
    q, k, v = sh(q), sh(k), sh(v)
    if getattr(cfg, "lookback", 0):
        k = lookback_keys(cfg, lyr, x, k)
    s = capped_scores(cfg, q, k)
    mask = jnp.tril(jnp.ones((T, T), bool))
    s = jnp.where(mask, s, -1e9)
    A = jax.nn.softmax(s, -1)
    y = lin(lyr["o"], mm(A, v, "bhts,bhsc->bhtc").transpose(0, 2, 1, 3).reshape(B, T, D))
    return y + walk_sector(cfg, lyr, A, v)


LAM_MIN = 1e-3  # floor on the ridge, in chart units: keeps C + lambda I safely positive definite in float32


def packed_index(r):
    """Positions of the entries (i, j), i <= j, of a symmetric r x r matrix stored as its upper triangle."""
    idx, n = {}, 0
    for i in range(r):
        for j in range(i, r):
            idx[i, j] = idx[j, i] = n
            n += 1
    return idx


def ridge_probe(m1, m2, lam, rhs):
    """
    Solve (C + lam I) x = rhs per query, C = M2 - m1 m1^T the chart covariance under the query's weights, by
    an unrolled float32 Cholesky factorisation (r is small, so XLA fuses it into a few elementwise kernels).
    m1 [..., r], m2 [..., r(r+1)/2] packed upper triangle of M2, lam broadcastable to [...], rhs [..., r].
    """
    r = m1.shape[-1]
    idx = packed_index(r)
    a = lambda i, j: m2[..., idx[i, j]] - m1[..., i] * m1[..., j] + (lam if i == j else 0.0)
    L = {}
    for j in range(r):
        L[j, j] = jnp.sqrt(jnp.maximum(a(j, j) - sum(L[j, t] ** 2 for t in range(j)), 0.5 * LAM_MIN))
        for i in range(j + 1, r):
            L[i, j] = (a(i, j) - sum(L[i, t] * L[j, t] for t in range(j))) / L[j, j]
    y = []
    for i in range(r):
        y.append((rhs[..., i] - sum(L[i, t] * y[t] for t in range(i))) / L[i, i])
    x = [None] * r
    for i in reversed(range(r)):
        x[i] = (y[i] - sum(L[t, i] * x[t] for t in range(i + 1, r))) / L[i, i]
    return jnp.stack(x, -1)


def lla_correction(lyr, q, k, p):
    """
    Ridge local-linear attention in a learned chart. Per head, c_j = R k_j (keys) and c_i = R q_i (query).
    Query i fits v_j ~ b0 + b1 (c_j - c_i) by least squares with weights p_ij and ridge lambda on b1 only,
    and reads b0. Its weights on the values are exactly

        p_ij (1 - (c_j - m1_i) . rho_i),   rho_i = (C_i + lambda I)^{-1} (m1_i - c_i),

    with m1_i = sum_j p_ij c_j and C_i = sum_j p_ij c_j c_j^T - m1_i m1_i^T (the closed form
    p_ij (1 - (c_j - c_i).rho~_i) / (1 - mu_i.rho~_i), rho~_i = (Sigma_i + lambda)^{-1} mu_i on moments centred at
    the query, is the same thing by Sherman-Morrison and needs no denominator in this form). Returns
    d_ij = (c_j - m1_i) . rho_i, so the local-linear weights are p (1 - d). One moment pass (values [c, cc^T]),
    one r x r solve per query, one score pass rho_i . c_j.
    """
    R = lyr["chart"]
    ck = jnp.einsum("bhtd,hrd->bhtr", k, R, precision=HI)
    cq = jnp.einsum("bhtd,hrd->bhtr", q, R, precision=HI)
    # shift the chart by the first key, which every query sees: the fit is translation invariant, so this is
    # exact, and it removes any offset shared by all keys before the moments (less cancellation in float32)
    ref = ck[:, :, :1]
    ck, cq = ck - ref, cq - ref
    r = ck.shape[-1]
    iu = np.triu_indices(r)
    vals = jnp.concatenate([ck, ck[..., iu[0]] * ck[..., iu[1]]], -1)
    mom = jnp.einsum("bhqt,bhtc->bhqc", p, vals, precision=HI)
    m1, m2 = mom[..., :r], mom[..., r:]
    lam = (jax.nn.softplus(lyr["lam"]) + LAM_MIN)[None, :, None]
    rho = ridge_probe(m1, m2, lam, m1 - cq)
    t = jnp.einsum("bhqr,bhtr->bhqt", rho, ck, precision=HI)
    return t - (rho * m1).sum(-1, keepdims=True)


def plx_correction(cfg, lyr, x, k, p):
    """Parallax (Zuo et al. 2026, eq. 8): weights p_ij (1 - t_ij + tbar_i), t_ij = rho_i . k_j, rho_i = W_R x_i;
    returns t - tbar."""
    B, T, D = x.shape
    rho = lin(lyr["wr"], x).reshape(B, T, cfg.heads, -1).transpose(0, 2, 1, 3)
    if "rho_g" in lyr:
        rho = rho / jnp.sqrt((rho ** 2).mean(-1, keepdims=True) + 1e-6) * lyr["rho_g"]
    t = mm(rho, k, "bhtc,bhsc->bhts")
    return t - (p * t).sum(-1, keepdims=True)


def local_attention(cfg, lyr, x, stats=None):
    """Causal softmax attention whose weights are corrected by local-linear regression (lla) or Parallax (plx).
    The corrected weights still sum to one and stay on the causal past; one A V product as in softmax."""
    B, T, D = x.shape
    H = cfg.heads
    q, k, v = project_qkv(lyr, x)
    sh = lambda t: t.reshape(B, T, H, D // H).transpose(0, 2, 1, 3)
    q, k, v = sh(q), sh(k), sh(v)
    s = jnp.where(jnp.tril(jnp.ones((T, T), bool)), capped_scores(cfg, q, k), -1e9)
    A = jax.nn.softmax(s, -1)
    if cfg.arch == "lla":
        # gated: softmax + g (LLA - softmax), g per head, zero at init
        W = A * (1 - lyr["gate"][None, :, None, None] * lla_correction(lyr, q, k, A))
    else:
        W = A * (1 - plx_correction(cfg, lyr, x, k, A))
    o = mm(W, v, "bhts,bhsc->bhtc")
    if stats is not None:
        # correction-to-output ratio (Parallax's COR), per layer: |o - o_SA| / |o_SA|, and the weight range
        o_sa = mm(A, v, "bhts,bhsc->bhtc")
        stats.append({"cor": jnp.mean(jnp.linalg.norm(o - o_sa, axis=-1) / (jnp.linalg.norm(o_sa, axis=-1) + 1e-6)),
                      "wmin": W.min(), "wmax": W.max()})
    return lin(lyr["o"], o.transpose(0, 2, 1, 3).reshape(B, T, D))


def lookback_keys(cfg, lyr, x, k):
    """
    Each key looks back along a learned causal hop before it is scored: k~_u = k_u + gamma * sum_{u'<u}
    B[u, u'] k_{u'}, with B a softmax over the strict past. The query's score on u is then a path
    q -> u' <- u: q matches what u looks back to and reads u. With B on the previous token this is an
    induction head in ONE layer (q finds the token after an earlier copy of itself), which plain backward
    walks cannot form: q -> j -> j + 1 needs a forward step. gamma starts at zero.
    """
    B_, T, D = x.shape
    H = cfg.heads
    sh = lambda t: t.reshape(B_, T, H, -1).transpose(0, 2, 1, 3)
    bq, bk = sh(lin(lyr["lbq"], x)), sh(lin(lyr["lbk"], x))
    past = jnp.tril(jnp.ones((T, T), bool), -1)
    sb = jnp.where(past, mm(bq, bk, "bhtc,bhsc->bhts") / math.sqrt(bq.shape[-1]), -1e9)
    Bm = jax.nn.softmax(sb, -1) * past  # position 0 has no past: its row is all zeros
    return k + lyr["gamma"][None] * mm(Bm, k, "bhts,bhsc->bhtc")


def walk_sector(cfg, lyr, A, v):
    """
    Causal walks along the layer's own attention: W_l = A^l V for l = 2..R, the value where a walker that
    starts at the query stands after l hops (each hop stays in the past), read by the attention's output
    projection with a per-hop scale that starts at zero. Cost: one attention-sized pass per extra hop.
    """
    if getattr(cfg, "hops", 1) <= 1:
        return 0.0
    B, H, T, dh = v.shape
    out, w = 0.0, mm(A, v, "bhts,bhsc->bhtc")  # W_1, the attention output itself
    for l in range(cfg.hops - 1):
        w = mm(A, w, "bhts,bhsc->bhtc")
        out = out + lin(lyr["o"], w.transpose(0, 2, 1, 3).reshape(B, T, H * dh)) * lyr["beta"][l]
    return out


HI = jax.lax.Precision.HIGHEST


def subset_moments(p, phi, K, mu=0.2):
    """
    Arity read-outs of a weighted token set with a Poisson vacuum, for m = 0..K-1:

        A_m(q) = [z^m] e^{mu z} prod_t (1 + z p_qt phi_t)  /  [z^m] e^{mu z} prod_t (1 + z p_qt)

    Without the vacuum (mu = 0) this is the mean of prod_{t in S} phi_t over distinct m-subsets S drawn with
    probability proportional to prod_{t in S} p_qt (a k-DPP with a diagonal kernel); A_1 is then softmax
    attention with values phi, and uniform p gives Newton attention. The vacuum lets a subset hold empty
    slots (value 1) at price mu each, so the read-out is a mixture of arities m, m - 1, ..., weighted by
    e_i(p) mu^(m-i) / (m-i)!. It is also what makes Newton's identities safe in float32: the denominator is
    at least mu^m / m!, so the error stays near eps ((1 + mu) / mu)^m however sharp p is. In power sums the
    vacuum is one term, mu added to the first. p: [B, H, Q, T] (zero on excluded tokens, rows summing to
    at most 1), phi: [B, H, T, r] complex. The power sums are K - 1 attention passes with weights p^j and
    values phi^j, at full float32 precision: TF32 matmuls would break the cancellations.
    """
    pj, fj, P, Z = p, phi, [], []
    for j in range(1, K):
        P.append(jnp.einsum("bhqt,bhtc->bhqc", pj, fj.real, precision=HI)
                 + 1j * jnp.einsum("bhqt,bhtc->bhqc", pj, fj.imag, precision=HI) + (mu if j == 1 else 0.0))
        Z.append(pj.sum(-1, keepdims=True) + (mu if j == 1 else 0.0))
        pj, fj = pj * p, fj * phi
    sign = lambda j: (-1.0) ** (j - 1)
    one = jnp.ones(p.shape[:3] + (phi.shape[-1],), phi.dtype)
    E, N = [one], [jnp.ones(p.shape[:3] + (1,), p.dtype)]
    for m in range(1, K):
        E.append(sum(sign(j) * E[m - j] * P[j - 1] for j in range(1, m + 1)) / m)
        N.append(sum(sign(j) * N[m - j] * Z[j - 1] for j in range(1, m + 1)) / m)
    if mu > 0:
        return [E[m] / N[m] for m in range(K)]
    # no vacuum: exact canonical read-outs, zero where no m-subset has weight (ill-conditioned in float32)
    return [E[0]] + [jnp.where(N[m] > 1e-30, E[m] / jnp.where(N[m] > 1e-30, N[m], 1.0), 0.0) for m in range(1, K)]

def capped_scores(cfg, q, k):
    s = mm(q, k, "bhtc,bhsc->bhts") / math.sqrt(q.shape[-1])
    return cfg.cap * jnp.tanh(s / cfg.cap) if cfg.cap else s


def causal_subset_moments(cfg, q, k, phi):
    """The query's softmax weights on the strict past, and the arity read-outs over distinct subsets of
    earlier tokens. q, k: [B, H, T, dh]; phi: [B, H, T, r] complex."""
    T, K = q.shape[2], cfg.order
    past = jnp.tril(jnp.ones((T, T), bool), -1)
    p = jax.nn.softmax(jnp.where(past, capped_scores(cfg, q, k), -1e9), -1) * past
    # the vacuum also covers positions with fewer than m earlier tokens: their subsets fill with empty slots
    return subset_moments(p, phi, K, cfg.vac), p


def sfa_attention(cfg, lyr, x):
    """Subset attention: causal softmax attention, plus every arity up to K over distinct subsets of the
    earlier tokens drawn with the same weights, each arity RMS-normalised and read by one projection."""
    B, T, D = x.shape
    H, r, K = cfg.heads, cfg.rank, cfg.order
    q, k, v = jnp.split(lin(lyr["qkv"], x), 3, -1)
    sh = lambda t: t.reshape(B, T, H, -1).transpose(0, 2, 1, 3)
    q, k, v = sh(q), sh(k), sh(v)
    if getattr(cfg, "lookback", 0):
        k = lookback_keys(cfg, lyr, x, k)
    s = jnp.where(jnp.tril(jnp.ones((T, T), bool)), capped_scores(cfg, q, k), -1e9)
    A = jax.nn.softmax(s, -1)
    y = lin(lyr["o"], mm(A, v, "bhts,bhsc->bhtc").transpose(0, 2, 1, 3).reshape(B, T, D))
    y = y + walk_sector(cfg, lyr, A, v)
    th = cfg.phase * sh(lin(lyr["th"], x))
    phi = jax.nn.sigmoid(sh(lin(lyr["g"], x))) * jnp.exp(1j * th)
    A, _ = causal_subset_moments(cfg, q, k, phi)
    fs = 0.0
    for m in range(K):
        f = phi * A[m]
        f = jnp.concatenate([f.real, f.imag], -1).transpose(0, 2, 1, 3).reshape(B, T, H * 2 * r)
        f = f / jnp.sqrt((f ** 2).mean(-1, keepdims=True) + 1e-6)
        if getattr(cfg, "fscale", 0):
            fs = fs + f * lyr["alpha"][m]
        else:
            y = y + lin(lyr["no"], f) * lyr["alpha"][m]
    return y + lin(lyr["no"], fs) if getattr(cfg, "fscale", 0) else y


def newton_attention(cfg, lyr, x):
    """Causal Newton attention with normalised per-arity features and one shared read-out."""
    B, T, D = x.shape
    H, r, K = cfg.nheads, cfg.rank, cfg.order
    th = cfg.phase * lin(lyr["th"], x).reshape(B, T, H, r)
    g = jax.nn.sigmoid(lin(lyr["g"], x).reshape(B, T, H, r))
    phi = g * jnp.exp(1j * th)  # [B, T, H, r]
    pw = [phi]
    for _ in range(K - 2):
        pw.append(pw[-1] * phi)
    # exclusive prefix sums: position t sees s < t
    P = [jnp.cumsum(w, 1) - w for w in pw]
    e = [jnp.ones_like(phi)]
    for m in range(1, K):
        e.append(sum((-1) ** (j - 1) * e[m - j] * P[j - 1] for j in range(1, m + 1)) / m)
    t = np.arange(T)
    feats = []
    for m in range(K):
        norm = np.array([math.comb(int(tt), m) if tt >= m else 0 for tt in t], np.float64)
        inv = jnp.asarray(np.where(norm > 0, 1.0 / np.maximum(norm, 1), 0.0), jnp.float32)[None, :, None, None]
        f = phi * e[m] * inv
        f = jnp.concatenate([f.real, f.imag], -1).reshape(B, T, H * 2 * r)
        # every arity on one scale before the shared read-out
        f = f / jnp.sqrt((f ** 2).mean(-1, keepdims=True) + 1e-6)
        feats.append(lin(lyr["no"], f) * lyr["alpha"][m])
    return sum(feats)


def block(cfg, lyr, x, stats=None):
    if cfg.arch in BEYOND_ARCHS:
        import beyond_layers
        normed = ln(lyr["ln1"], x)
        update = beyond_layers.apply_layer(cfg, lyr, normed)
        if stats is not None:
            rms = lambda y: jnp.sqrt(jnp.mean(y * y) + 1e-12)
            record = {"update_rms": rms(update)}
            if cfg.arch.startswith("beyond_"):
                content, _, _ = beyond_layers.content_attention(cfg, lyr, normed)
                no_precision_cfg = argparse.Namespace(**{**vars(cfg), "ablate": "precision"})
                local_constant, _, _ = beyond_layers.content_attention(no_precision_cfg, lyr, normed)
                record.update({
                    "composition_over_content": rms(update - content) / rms(content),
                    "precision_over_content": rms(content - local_constant) / rms(content),
                })
                if cfg.arch == "beyond_a":
                    no_coupling_cfg = argparse.Namespace(**{**vars(cfg), "ablate": "coupling"})
                    no_transport_parameters = lyr
                    if getattr(cfg, "ablate", "none") == "precision":
                        no_transport_parameters = {
                            **lyr, "wr": jax.tree_util.tree_map(jnp.zeros_like, lyr["wr"])
                        }
                    no_transport = (
                        content if getattr(cfg, "ablate", "none") == "composition" else
                        beyond_layers.apply_layer(no_coupling_cfg, no_transport_parameters, normed)
                    )
                    record["matrix_over_content"] = rms(no_transport - content) / rms(content)
                    record["transport_over_content"] = rms(update - no_transport) / rms(content)
                else:
                    record["matrix_over_content"] = rms(update - content) / rms(content)
                # A nonzero readout could be a constant identity feature.
                # Measure changing rotations separately on this held-out batch.
                source = normed
                if cfg.arch == "beyond_c" and getattr(cfg, "ablate", "none") != "coupling":
                    source = source + jnp.tanh(lyr["context_mix"]) * content
                _, _, _, gh, gd, gnh, _ = beyond_layers._dims(cfg)
                vectors = beyond_layers._lin(cfg, lyr["group_vectors"], source)
                vectors = vectors.reshape(*source.shape[:2], gh, gnh, gd)
                transitions = beyond_layers.householder_products(vectors)
                identity_distance = transitions - jnp.eye(gd, dtype=transitions.dtype)
                record["transition_identity_frob_mean"] = jnp.mean(
                    jnp.linalg.norm(identity_distance, axis=(-2, -1))
                )
                if source.shape[1] > 1:
                    left, right = transitions[:, :-1], transitions[:, 1:]
                    commutator = left @ right - right @ left
                    record["adjacent_commutator_frob_mean"] = jnp.mean(
                        jnp.linalg.norm(commutator, axis=(-2, -1))
                    )
                else:
                    record["adjacent_commutator_frob_mean"] = jnp.asarray(0.0)
            stats.append(record)
        x = x + update
    if cfg.arch == "sfa":
        x = x + sfa_attention(cfg, lyr, ln(lyr["ln1"], x))
    if cfg.arch in ("gpt", "hybrid"):
        x = x + softmax_attention(cfg, lyr, ln(lyr["ln1"], x))
    if cfg.arch in ("lla", "plx"):
        x = x + local_attention(cfg, lyr, ln(lyr["ln1"], x), stats)
    if cfg.arch in ("hybrid", "newton"):
        x = x + newton_attention(cfg, lyr, ln(lyr["lnn"], x))
    return x + lin(lyr["fc2"], jax.nn.gelu(lin(lyr["fc1"], ln(lyr["ln2"], x))))


def forward(cfg, p, idx, stats=None):
    T = idx.shape[1]
    x = p["emb"][idx]
    if getattr(cfg, "pos", 1):
        x = x + p["pos"][None, :T]
    f = jax.checkpoint(lambda lyr, x: block(cfg, lyr, x)) if getattr(cfg, "remat", 0) else (lambda lyr, x: block(cfg, lyr, x))
    for lyr in p["layers"]:
        x = f(lyr, x) if stats is None else block(cfg, lyr, x, stats)
    x = ln(p["lnf"], x)
    return mm(x, p["emb"].T)


def make_opt(name, sched, wd=0.1):
    """
    adamw: the S0 optimizer (clip 1.0, AdamW with weight decay 0.1 on every parameter).
    muon:  the hidden matrices (qkv, o, fc1, fc2, W_R; the chart R per head) take Muon updates: Nesterov
           momentum 0.95, five Newton-Schulz steps, Moonlight's RMS matching (update RMS 0.2 x rate, so the
           rates sit on AdamW's scale), decoupled weight decay 0.1. Embeddings (tied with the head), positions,
           norms, biases, gates and lambda take the same AdamW as above, at the same rate.
    """
    clip = optax.clip_by_global_norm(1.0)
    # Gated DeltaNet's timescale parameters retain the published no-decay
    # convention. All pre-existing architecture parameter masks remain unchanged.
    def decay_mask(params):
        return jax.tree_util.tree_map_with_path(
            lambda path, _: getattr(path[-1], "key", None) not in ("A_log", "dt_bias"), params
        )

    if name == "adamw":
        return optax.chain(clip, optax.adamw(sched, weight_decay=wd, mask=decay_mask))
    from optax.contrib import _muon as mu

    def dims(params):
        def spec(path, x):
            keys = [getattr(k, "key", None) for k in path]
            if keys[-1] == "chart":
                return mu.MuonDimensionNumbers(reduction_axis=2, output_axis=1)  # each head's r x dh map
            if keys[0] == "layers" and keys[-1] == "w" and x.ndim == 2:
                return mu.MuonDimensionNumbers(reduction_axis=0, output_axis=1)
            return None
        return jax.tree_util.tree_map_with_path(spec, params)

    leaf = lambda x: x is None or mu._is_weight_dim_nums(x) or isinstance(x, mu._masking.MaskedNode)

    def labels(params):
        return jax.tree.map(lambda d, x: "muon" if d is not None else "adam", dims(params), params, is_leaf=leaf)

    def masked_dims(params):
        # the muon branch sees a masked tree: MaskedNode where a parameter belongs to the AdamW branch
        return jax.tree.map(lambda d, lab: d if lab == "muon" else mu._masking.MaskedNode(), dims(params),
                            labels(params), is_leaf=leaf)

    muon = optax.chain(
        mu.scale_by_muon(beta=0.95, nesterov=True, weight_dimension_numbers=masked_dims),
        mu.scale_by_shape(weight_dimension_numbers=masked_dims, consistent_rms=0.2),
        optax.add_decayed_weights(wd),
        optax.scale_by_learning_rate(sched),
    )
    return optax.chain(clip, optax.partition(
        {"muon": muon, "adam": optax.adamw(sched, weight_decay=wd, mask=decay_mask)}, labels
    ))


def flops_per_token(cfg, T):
    """
    Forward FLOPs per token, counted for what each layer has to compute (causal attention: a query sees
    (T + 1) / 2 keys on average), the same way for every architecture. Training costs three times this.
    Every power-sum pass, Newton recursion, read-out, look-back and walk pass is included.
    """
    D, L, V, H = cfg.d, cfg.layers, cfg.vocab, cfg.heads
    conv_width = qkv_conv_width(cfg)
    if cfg.arch in BEYOND_ARCHS:
        import beyond_layers
        return L * (beyond_layers.forward_flops(cfg, cfg.arch, T) + 4 * D * cfg.mlp) + 2 * D * V
    ta = (T + 1) / 2
    lyr = 2 * (4 * D * D + 2 * D * cfg.mlp) + 2 * 2 * ta * D + 5 * ta * H        # projections, MLP, QK, AV, softmax
    # BEYOND arms count this in beyond_layers.forward_flops above; count it
    # here only for the ordinary softmax/Parallax implementations.
    lyr += 6 * conv_width * D
    if cfg.arch == "sfa":
        r, K = cfg.rank, cfg.order
        lyr += 2 * 2 * D * H * r                                                   # phases and gates
        lyr += 5 * ta * H                                                          # strict-past softmax
        lyr += (K - 1) * (2 * ta * 2 * r * H + 2 * ta * H)                         # power-sum passes, powers of p
        reads = 1 if getattr(cfg, "fscale", 0) else K
        lyr += 8 * K * K * r * H + reads * 2 * 2 * r * H * D + K * 6 * 2 * r * H     # Newton recursion, read-out(s), RMS, scales
    if cfg.arch in ("hybrid", "newton"):
        r, K = cfg.rank, cfg.order
        lyr += 2 * 2 * D * cfg.nheads * r + 8 * K * K * r * cfg.nheads + K * 2 * 2 * r * cfg.nheads * D
        if cfg.arch == "newton":
            lyr -= 2 * 4 * D * D + 2 * 2 * ta * D + 5 * ta * H
    if getattr(cfg, "hops", 1) > 1:
        lyr += (cfg.hops - 1) * (2 * ta * D + 2 * D * D)                          # A^l V passes and their read-outs
    if getattr(cfg, "lookback", 0):
        lb = cfg.lbdim * H
        lyr += 2 * 2 * D * lb + 2 * ta * lb + 5 * ta * H + 2 * ta * D              # look-back scores and key mixing
    if cfg.arch == "plx":
        # Parallax's one-pass kernel (Algorithm 1): rho projection, S2 = rho K^T, P2 = P1 * S2, its row sum,
        # O2 = P2 V, and the epilogue
        lyr += 2 * D * D + 2 * ta * D + 3 * ta * H + 2 * ta * D + 3 * D
        lyr += 4 * D if getattr(cfg, "plx_norm", 0) else 0                          # RMSNorm on rho
    if cfg.arch == "lla":
        r = cfg.chart
        w = r + r * (r + 1) // 2                                                   # moment values [c, cc^T]
        lyr += 2 * 2 * D * r + H * r * (r + 1) // 2                                 # chart c_q, c_k; outer products
        lyr += 2 * ta * w * H                                                       # pass 1: moments under p
        lyr += H * (r * (r + 1) + r ** 3 / 3 + 2 * r * r + 4 * r)                   # covariance, Cholesky, solves
        # pass 2 of a fused kernel recomputes the scores and softmax, then rho.c, the weights, one A V (counted
        # above as softmax's)
        lyr += 2 * ta * D + 5 * ta * H + 2 * ta * r * H + 3 * ta * H
    return L * lyr + 2 * D * V


def save_final_checkpoint(cfg, params, artifact_dir):
    """Write our own trusted final checkpoint; never load an external pickle."""
    os.makedirs(artifact_dir, exist_ok=True)
    destination = os.path.join(artifact_dir, "final.pkl")
    payload = {
        "schema": 1,
        "cfg": vars(cfg).copy(),
        "params": jax.tree_util.tree_map(lambda x: np.asarray(jax.device_get(x)), params),
        "versions": {"jax": jax.__version__, "optax": optax.__version__, "numpy": np.__version__},
        "created_unix": time.time(),
    }
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=artifact_dir, prefix=".final.", suffix=".tmp",
                                         delete=False) as output:
            temporary = output.name
            pickle.dump(payload, output, protocol=pickle.HIGHEST_PROTOCOL)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary is not None and os.path.exists(temporary):
            os.unlink(temporary)
    return {"path": destination, "bytes": os.path.getsize(destination), "schema": 1}


def final_ablation_losses(cfg, params, bx, by, batch_size):
    """Final-only interventions on exactly the original val_big sample.

    Reuse trained parameters without selecting a rate, checkpoint or seed.
    B has no coupling operation to remove.
    """
    if not cfg.arch.startswith("beyond_"):
        return {}
    modes = ["composition", "precision"]
    if cfg.arch in ("beyond_a", "beyond_c"):
        modes.append("coupling")
    results = {}
    for mode in modes:
        ablated_cfg = argparse.Namespace(**{**vars(cfg), "ablate": mode})

        def make_losses(config):
            @jax.jit
            def losses(p, x, y):
                logits = forward(config, p, x)
                return optax.softmax_cross_entropy_with_integer_labels(logits, y).sum()
            return losses

        score = make_losses(ablated_cfg)
        total = 0.0
        for start in range(0, len(bx), batch_size):
            total += float(score(params, bx[start:start + batch_size], by[start:start + batch_size]))
        value = total / (len(bx) * bx.shape[1])
        if not math.isfinite(value):
            raise FloatingPointError(f"nonfinite final {mode} ablation loss")
        results[mode] = round(value, 5)
        if getattr(cfg, "progress", 0):
            print(json.dumps({"final_ablation": mode, "val_big": results[mode],
                              "arch": cfg.arch, "seed": cfg.seed}), file=sys.stderr, flush=True)
    return results


def main():
    global MM
    ap = argparse.ArgumentParser()
    ap.add_argument("--arch", default="gpt")
    ap.add_argument("--d", type=int, default=256)
    ap.add_argument("--layers", type=int, default=4)
    ap.add_argument("--heads", type=int, default=4)
    ap.add_argument("--mlp", type=int, default=0)
    ap.add_argument("--nheads", type=int, default=4)
    ap.add_argument("--rank", type=int, default=32)
    ap.add_argument("--order", type=int, default=4)
    ap.add_argument("--phase", type=float, default=2.0)
    # subset attention: Poisson vacuum (price of an empty slot) and an optional tanh cap on the logits
    ap.add_argument("--vac", type=float, default=0.2)
    ap.add_argument("--alpha0", type=int, default=0)
    ap.add_argument("--cap", type=float, default=0.0)
    ap.add_argument("--fscale", type=int, default=0, help="per-arity scales on the features: one read-out instead of K")
    # walks A^l V up to R hops, and the look-back hop on keys (with its per-head width)
    ap.add_argument("--hops", type=int, default=1)
    ap.add_argument("--lookback", type=int, default=0)
    ap.add_argument("--lbdim", type=int, default=16)
    # local-regression attention: chart dimension r, chart init scale (std of c_j at init), initial ridge
    ap.add_argument("--chart", type=int, default=8)
    ap.add_argument("--chart_init", type=float, default=0.5)
    ap.add_argument("--lam0", type=float, default=1.0)
    ap.add_argument("--opt", default="adamw", help="adamw | muon")
    ap.add_argument("--plx_norm", type=int, default=0, help="Parallax with RMSNorm on rho (gain 0 at init, W_R random)")
    ap.add_argument("--qkv_conv", type=int, default=0,
                    help="optional causal depthwise QKV width, no activation; shared S/P/A/B/C backbone")
    ap.add_argument("--pos", type=int, default=1, help="learned positions; disabled for position-free word diagnostics")
    ap.add_argument("--gdim", type=int, default=5, help="BEYOND small orthogonal matrix dimension")
    ap.add_argument("--nh", type=int, default=4, help="matrix transition / DeltaProduct microsteps")
    ap.add_argument("--beta_max", type=float, default=2.0, help="delta update range; 1 for canonical Gated DeltaNet")
    ap.add_argument("--delta_key_ratio", type=float, default=0.75, help="Gated DeltaNet key width / model width")
    ap.add_argument("--delta_v_expand", type=float, default=2.0, help="Gated DeltaNet value width / key width")
    ap.add_argument("--ablate", default="none", help="BEYOND component ablation")
    ap.add_argument("--ctx", type=int, default=256)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--micro", type=int, default=1, help="split each batch into this many accumulated micro-batches")
    ap.add_argument("--steps", type=int, default=8000)
    ap.add_argument("--tokens", type=float, default=0, help="training tokens; overrides --steps")
    ap.add_argument("--warmup", type=int, default=0)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=0, help="initialisation and data order")
    ap.add_argument("--data", default="/root/enwik8")
    ap.add_argument("--vocab", type=int, default=256)
    ap.add_argument("--bf16", type=int, default=0)
    ap.add_argument("--remat", type=int, default=0)
    ap.add_argument("--vseqs", type=int, default=512, help="held-out sequences")
    ap.add_argument("--vbig", type=int, default=0, help="also score this many other held-out sequences at the end")
    ap.add_argument("--evals", type=int, default=16, help="evenly spaced evaluations")
    ap.add_argument("--early", type=int, default=0, help="also evaluate every this many steps early in training")
    ap.add_argument("--early_until", type=int, default=0, help="last step of the early evaluations (default: a fifth)")
    ap.add_argument("--probe", type=int, default=0, help="repeated-random-token induction probe")
    ap.add_argument("--group_init", choices=("paired", "random"), default="paired")
    ap.add_argument("--delta_unroll", type=int, default=1)
    ap.add_argument("--progress", type=int, default=0, help="emit evaluation progress to stderr for durable run logs")
    ap.add_argument("--save-final", type=int, default=0,
                    help="atomically save cfg and final parameters to BEYOND_ARTIFACT_DIR/final.pkl")
    ap.add_argument("--ablations", type=int, default=0,
                    help="final-only component losses for candidates on the same 1024 val_big sequences")
    cfg = ap.parse_args()
    artifact_dir = os.environ.get("BEYOND_ARTIFACT_DIR")
    if cfg.save_final and not artifact_dir:
        ap.error("--save-final 1 requires BEYOND_ARTIFACT_DIR")
    if cfg.ablations and cfg.arch.startswith("beyond_"):
        if cfg.vbig != 1024:
            ap.error("--ablations 1 requires --vbig 1024 for the registered held-out sample")
        if cfg.ablate != "none":
            ap.error("--ablations 1 requires an unablated training configuration (--ablate none)")
    if cfg.bf16:
        MM = jnp.bfloat16
    if not cfg.mlp:
        # matched parameters: the Newton branch's weights come out of the MLP
        D, H, r = cfg.d, cfg.nheads, cfg.rank
        newton = 2 * D * H * r + 2 * H * r * D
        attn = 4 * D * D
        per_layer = attn + 8 * D * D
        if cfg.arch in ("gpt", "lla", "plx") + BEYOND_ARCHS:
            cfg.mlp = 4 * D
        elif cfg.arch in ("hybrid", "sfa"):
            if cfg.arch == "sfa":
                newton = 2 * D * cfg.heads * r + 2 * cfg.heads * r * D
            cfg.mlp = max(D, int((per_layer - attn - newton) / (2 * D)))
        else:
            cfg.mlp = max(D, int((per_layer - newton) / (2 * D)))
    train, val = load(cfg.data)
    T = cfg.ctx
    if cfg.tokens:
        cfg.steps = int(cfg.tokens // (cfg.batch * T))
    rng = np.random.default_rng(cfg.seed)  # data order: the same for every model at a given seed
    vrng = np.random.default_rng(1234)

    def batch(src, g, n):
        i = g.integers(0, len(src) - T - 1, n)
        x = np.stack([src[j : j + T + 1] for j in i]).astype(np.int32)
        return x[:, :-1], x[:, 1:]

    vx, vy = batch(val, vrng, cfg.vseqs)
    params = init(jax.random.PRNGKey(cfg.seed), cfg)
    nparams = sum(int(x.size) for x in jax.tree_util.tree_leaves(params))
    nembed = int(params["emb"].size + params["pos"].size)
    warm = cfg.warmup or min(400, cfg.steps // 10)
    sched = optax.warmup_cosine_decay_schedule(0.0, cfg.lr, warm, cfg.steps, cfg.lr * 0.1)
    opt = make_opt(cfg.opt, sched)
    st = opt.init(params)
    fpt = flops_per_token(cfg, T)

    def loss_fn(p, x, y):
        lg = forward(cfg, p, x)
        return optax.softmax_cross_entropy_with_integer_labels(lg, y).mean()

    @jax.jit
    def step(p, st, x, y):
        if cfg.micro > 1:
            xs, ys = x.reshape(cfg.micro, -1, T), y.reshape(cfg.micro, -1, T)

            def acc(c, xy):
                l, g = jax.value_and_grad(loss_fn)(p, *xy)
                return jax.tree_util.tree_map(jnp.add, c, (l, g)), None

            zero = (jnp.zeros(()), jax.tree_util.tree_map(jnp.zeros_like, p))
            (l, g), _ = jax.lax.scan(acc, zero, (xs, ys))
            l, g = l / cfg.micro, jax.tree_util.tree_map(lambda t: t / cfg.micro, g)
        else:
            l, g = jax.value_and_grad(loss_fn)(p, x, y)
        up, st = opt.update(g, st, p)
        return optax.apply_updates(p, up), st, l

    @jax.jit
    def poslosses(p, x, y):
        # held-out loss at every position, summed over the batch
        lg = forward(cfg, p, x)
        return optax.softmax_cross_entropy_with_integer_labels(lg, y).sum(0)

    vb = max(1, min(64, cfg.vseqs) // cfg.micro)
    # induction probe: random tokens repeated once; an induction head predicts the second copy
    prng = np.random.default_rng(4321)
    half = T // 2
    rep = prng.integers(0, min(cfg.vocab, 50257), (32, half))
    rep = np.concatenate([rep, rep, rep[:, :1]], 1).astype(np.int32)
    rx, ry = rep[:, :T], rep[:, 1 : T + 1]

    def evaluate(p):
        per = np.zeros(T)
        for i in range(0, len(vx), vb):
            per += np.asarray(poslosses(p, vx[i : i + vb], vy[i : i + vb]))
        per /= len(vx)
        out = {"val": round(float(per.mean()), 4)}
        if T >= 512:
            # in-context learning score (Olsson et al.): loss at token 50 minus loss at token 500
            out["icl"] = round(float(per[40:60].mean() - per[490:510].mean()), 4)
        if cfg.probe:
            pr = np.zeros(T)
            for i in range(0, len(rx), vb):
                pr += np.asarray(poslosses(p, rx[i : i + vb], ry[i : i + vb]))
            pr /= len(rx)
            out["rep1"] = round(float(pr[1:half - 1].mean()), 4)   # first copy: nothing to copy from
            out["rep2"] = round(float(pr[half:].mean()), 4)        # second copy: an induction head copies
        return out

    marks = {max(1, round(cfg.steps * (i + 1) / cfg.evals)) for i in range(cfg.evals)}
    if cfg.early:
        marks |= set(range(cfg.early, (cfg.early_until or cfg.steps // 5) + 1, cfg.early))
    t0 = time.time()
    curve = []
    for it in range(cfg.steps):
        x, y = batch(train, rng, cfg.batch)
        params, st, l = step(params, st, x, y)
        if it + 1 in marks:
            tok = (it + 1) * cfg.batch * T
            row = {"step": it + 1, "tokens": tok, "flops": 3 * fpt * tok, "train": round(float(l), 4)}
            row.update(evaluate(params))
            row["secs"] = round(time.time() - t0, 1)
            curve.append(row)
            if cfg.progress:
                print(json.dumps({"progress": row, "arch": cfg.arch, "seed": cfg.seed}), file=sys.stderr, flush=True)
            if not math.isfinite(float(l)) or not math.isfinite(row["val"]):
                raise FloatingPointError(f"nonfinite training/evaluation loss at step {it + 1}")
    last = curve[-1]
    extra = {}
    if cfg.save_final:
        # Save before additional diagnostic compilation so trained parameters
        # survive interrupted or failed post-training ablations.
        extra["checkpoint"] = save_final_checkpoint(cfg, params, artifact_dir)
    if cfg.vbig:
        # a larger held-out set drawn with its own generator, scored once at the end (LOCAL.md's gate metric)
        bx, by = batch(val, np.random.default_rng(5678), cfg.vbig)
        tot = 0.0
        for i in range(0, len(bx), vb):
            tot += float(np.asarray(poslosses(params, bx[i : i + vb], by[i : i + vb])).sum())
        extra["val_big"] = round(tot / (len(bx) * T), 5)
        if cfg.ablations and cfg.arch.startswith("beyond_"):
            extra["ablation_val_big"] = final_ablation_losses(cfg, params, bx, by, vb)
            extra["ablation_delta_val_big"] = {
                name: round(value - extra["val_big"], 5)
                for name, value in extra["ablation_val_big"].items()
            }
    if cfg.arch in ("lla", "plx"):
        # what the trained layers use: gates, ridges and chart scale (lla), probe weight norm (plx), and the
        # correction-to-output ratio and weight range on one held-out batch
        stats = []
        forward(cfg, params, jnp.asarray(vx[:8]), stats)
        extra["cor"] = [round(float(s_["cor"]), 4) for s_ in stats]
        extra["wrange"] = [[round(float(s_["wmin"]), 3), round(float(s_["wmax"]), 3)] for s_ in stats]
        if cfg.arch == "lla":
            extra["gate"] = [[round(float(g), 4) for g in l["gate"]] for l in params["layers"]]
            extra["lam"] = [[round(float(jax.nn.softplus(a) + LAM_MIN), 4) for a in l["lam"]] for l in params["layers"]]
            extra["chart_norm"] = [round(float(jnp.linalg.norm(l["chart"])), 4) for l in params["layers"]]
        else:
            extra["wr_norm"] = [round(float(jnp.linalg.norm(l["wr"]["w"])), 4) for l in params["layers"]]
            if "rho_g" in params["layers"][0]:
                extra["rho_gain"] = [round(float(jnp.sqrt((l["rho_g"] ** 2).mean())), 4) for l in params["layers"]]
    if cfg.arch in BEYOND_ARCHS:
        usage = []
        forward(cfg, params, jnp.asarray(vx[:4]), usage)
        extra["component_usage"] = [{k: float(v) for k, v in row.items()} for row in usage]
        extra["component_parameters"] = [
            {
                name: np.asarray(layer[name]).tolist()
                for name in ("group_mix", "path_mix", "context_mix", "A_log", "dt_bias")
                if name in layer
            }
            for layer in params["layers"]
        ]
    out = {"arch": cfg.arch, "opt": cfg.opt, "plx_norm": cfg.plx_norm if cfg.arch == "plx" else None, "chart": cfg.chart if cfg.arch == "lla" else None,
           "chart_init": cfg.chart_init if cfg.arch == "lla" else None, "lam0": cfg.lam0 if cfg.arch == "lla" else None, "seed": cfg.seed, "params": nparams, "nonembed": nparams - nembed, "mlp": cfg.mlp,
           "layers": cfg.layers, "d": cfg.d, "rank": cfg.rank, "order": cfg.order, "vac": cfg.vac, "alpha0": cfg.alpha0,
           "cap": cfg.cap, "fscale": cfg.fscale, "hops": cfg.hops, "lookback": cfg.lookback, "lr": cfg.lr, "steps": cfg.steps,
           "tokens": cfg.steps * cfg.batch * T, "flops_per_token": fpt, "train_flops": 3 * fpt * cfg.steps * cfg.batch * T,
           "data": cfg.data, "val_loss": last["val"], "curve": curve, "secs": round(time.time() - t0, 1),
           "backend": jax.default_backend(), "versions": [jax.__version__, optax.__version__],
           "pos": cfg.pos, "gdim": cfg.gdim if cfg.arch in BEYOND_ARCHS else None,
           "nh": cfg.nh if cfg.arch in BEYOND_ARCHS else None,
           "beta_max": cfg.beta_max if cfg.arch == "gated_delta" else None,
           "delta_key_ratio": cfg.delta_key_ratio if cfg.arch == "gated_delta" else None,
           "delta_v_expand": cfg.delta_v_expand if cfg.arch == "gated_delta" else None,
           "ablate": cfg.ablate, **extra}
    if cfg.vocab == 256:
        out["val_bpc"] = round(last["val"] / math.log(2), 4)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
