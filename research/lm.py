"""
Language models for the arity question: bytes (enwik8) or GPT-2 tokens (TinyStories, FineWeb-Edu).

    gpt     softmax attention + MLP, pre-LayerNorm, L layers
    hybrid  the same, plus a causal Newton attention branch beside each attention, MLP narrowed
    newton  Newton attention in place of softmax attention
    sfa     free-field attention: softmax attention whose weights also feed Newton's identities, so every
            arity up to K reads distinct subsets of the tokens the query selects (MLP narrowed); with
            --hops R it also reads walks A^l V (l = 2..R) along the same causal attention, and with
            --lookback each key first looks back along a learned causal hop (see walk_sector below)

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
import time

import jax
import jax.numpy as jnp
import numpy as np
import optax


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
    ks = iter(jax.random.split(key, 16 + 16 * L))
    p = {"emb": jax.random.normal(next(ks), (cfg.vocab, D)) * 0.02, "pos": jax.random.normal(next(ks), (T, D)) * 0.02,
         "lnf": ln_init(D), "layers": []}
    for _ in range(L):
        lyr = {"ln1": ln_init(D), "ln2": ln_init(D)}
        if cfg.arch in ("gpt", "hybrid", "sfa"):
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
    return p


def softmax_attention(cfg, lyr, x):
    B, T, D = x.shape
    H = cfg.heads
    q, k, v = jnp.split(lin(lyr["qkv"], x), 3, -1)
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


def block(cfg, lyr, x):
    if cfg.arch == "sfa":
        x = x + sfa_attention(cfg, lyr, ln(lyr["ln1"], x))
    if cfg.arch in ("gpt", "hybrid"):
        x = x + softmax_attention(cfg, lyr, ln(lyr["ln1"], x))
    if cfg.arch in ("hybrid", "newton"):
        x = x + newton_attention(cfg, lyr, ln(lyr["lnn"], x))
    return x + lin(lyr["fc2"], jax.nn.gelu(lin(lyr["fc1"], ln(lyr["ln2"], x))))


def forward(cfg, p, idx):
    T = idx.shape[1]
    x = p["emb"][idx] + p["pos"][None, :T]
    f = jax.checkpoint(lambda lyr, x: block(cfg, lyr, x)) if getattr(cfg, "remat", 0) else (lambda lyr, x: block(cfg, lyr, x))
    for lyr in p["layers"]:
        x = f(lyr, x)
    x = ln(p["lnf"], x)
    return mm(x, p["emb"].T)


def flops_per_token(cfg, T):
    """
    Forward FLOPs per token, counted for what each layer has to compute (causal attention: a query sees
    (T + 1) / 2 keys on average), the same way for every architecture. Training costs three times this.
    Every power-sum pass, Newton recursion, read-out, look-back and walk pass is included.
    """
    D, L, V, H = cfg.d, cfg.layers, cfg.vocab, cfg.heads
    ta = (T + 1) / 2
    lyr = 2 * (4 * D * D + 2 * D * cfg.mlp) + 2 * 2 * ta * D + 5 * ta * H        # projections, MLP, QK, AV, softmax
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
    return L * lyr + 2 * D * V


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
    ap.add_argument("--evals", type=int, default=16, help="evenly spaced evaluations")
    ap.add_argument("--early", type=int, default=0, help="also evaluate every this many steps early in training")
    ap.add_argument("--early_until", type=int, default=0, help="last step of the early evaluations (default: a fifth)")
    ap.add_argument("--probe", type=int, default=0, help="repeated-random-token induction probe")
    cfg = ap.parse_args()
    if cfg.bf16:
        MM = jnp.bfloat16
    if not cfg.mlp:
        # matched parameters: the Newton branch's weights come out of the MLP
        D, H, r = cfg.d, cfg.nheads, cfg.rank
        newton = 2 * D * H * r + 2 * H * r * D
        attn = 4 * D * D
        per_layer = attn + 8 * D * D
        if cfg.arch == "gpt":
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
    opt = optax.chain(optax.clip_by_global_norm(1.0), optax.adamw(sched, weight_decay=0.1))
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
    last = curve[-1]
    out = {"arch": cfg.arch, "seed": cfg.seed, "params": nparams, "nonembed": nparams - nembed, "mlp": cfg.mlp,
           "layers": cfg.layers, "d": cfg.d, "rank": cfg.rank, "order": cfg.order, "vac": cfg.vac, "alpha0": cfg.alpha0,
           "cap": cfg.cap, "fscale": cfg.fscale, "hops": cfg.hops, "lookback": cfg.lookback, "lr": cfg.lr, "steps": cfg.steps,
           "tokens": cfg.steps * cfg.batch * T, "flops_per_token": fpt, "train_flops": 3 * fpt * cfg.steps * cfg.batch * T,
           "data": cfg.data, "val_loss": last["val"], "curve": curve, "secs": round(time.time() - t0, 1),
           "backend": jax.default_backend()}
    if cfg.vocab == 256:
        out["val_bpc"] = round(last["val"] / math.log(2), 4)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
