"""
Stage 0 of LOCAL.md: brute-force checks of ridge local-linear attention (lm.py --arch lla) and Parallax
(--arch plx) against their definitions, in float64:

    python research/test_local.py

(a) with the gate at zero, or lambda -> infinity, the layer is softmax attention;
(b) its weights equal an explicit per-query weighted ridge solve, and the closed form
    p (1 - (c_j - c_i).rho) / (1 - mu.rho) on query-centred moments;
(c) the subset expansion: the ridge fit is a normalised sum over subsets S of the past of every size
    m = 1..r+1, weighted lambda^(r+1-m) prod_{j in S} p_j (squared minors of the rows [1, c_j - c_i]), each
    contributing the value its affine fit predicts at the query; m = 1 alone is softmax; first order in
    1/lambda is the pair sector; at lambda = 0 only subsets of size r+1 remain;
(d) Parallax's streaming form (its eq. 14, with an online softmax over key blocks) equals its definition
    (eq. 8) and the covariance form o_SA - Sigma_KV rho;
(e) no weight falls on future tokens, and changing token t leaves every earlier output unchanged;
plus the FLOP counter (S0's softmax number is reproduced) and the init (every arm is softmax at init,
with exactly the softmax model's weights).
"""

import argparse
import itertools
import math
import pathlib
import sys

import jax

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import lm  # noqa: E402

rng = np.random.default_rng(0)
ok = True


def check(name, err, tol):
    global ok
    good = bool(err < tol)
    ok &= good
    print(f"{'ok ' if good else 'FAIL'} {name}: max error {err:.2e} (tolerance {tol:g})")


def softmax_rows(s):
    s = s - s.max(-1, keepdims=True)
    e = np.exp(s)
    return e / e.sum(-1, keepdims=True)


# ----------------------------------------------------------------------------- references (numpy, float64)


def ridge_b0(p, u, v, lam):
    """argmin_{b0, b1} sum_j p_j |v_j - b0 - b1 . u_j|^2 + lam |b1|^2, returns b0. u [n, r], v [n, dv]."""
    n, r = u.shape
    X = np.concatenate([np.ones((n, 1)), u], 1)
    pen = np.diag([0.0] + [lam] * r)
    beta = np.linalg.solve(X.T @ (p[:, None] * X) + pen, X.T @ (p[:, None] * v))
    return beta[0]


def jacobi_augmented(p, u, v, lam):
    """Jacobi's formula on the augmented design: rows sqrt(p_j)[1, u_j] (target sqrt(p_j) v_j) and r
    pseudo-rows sqrt(lam)[0, e_k] (target 0). LS = sum over (r+1)-row subsets of det^2 * exact fit / sum det^2."""
    n, r = u.shape
    rows = [np.sqrt(p[j]) * np.concatenate([[1.0], u[j]]) for j in range(n)]
    tgts = [np.sqrt(p[j]) * v[j] for j in range(n)]
    for k in range(r):
        e = np.zeros(r + 1); e[k + 1] = np.sqrt(lam)
        rows.append(e); tgts.append(np.zeros(v.shape[1]))
    rows, tgts = np.array(rows), np.array(tgts)
    num, den = 0.0, 0.0
    for S in itertools.combinations(range(len(rows)), r + 1):
        M = rows[list(S)]
        d = np.linalg.det(M)
        if abs(d) < 1e-14:
            continue
        num = num + d * d * np.linalg.solve(M, tgts[list(S)])[0]
        den += d * d
    return num / den


def subset_minor_form(p, u, v, lam, sizes=None):
    """The claimed expansion, term by term: subsets T of the data rows (|T| = m = 1..r+1) and coordinate sets
    A (|A| = m - 1), weight lam^(r+1-m) prod_T p_j det([1, u_{T,A}])^2, value b0 of the exact fit through T in
    the coordinates A. Returns numerator, denominator (so sectors can be compared)."""
    n, r = u.shape
    num, den = np.zeros(v.shape[1]), 0.0
    for m in range(1, min(n, r + 1) + 1):
        if sizes is not None and m not in sizes:
            continue
        for T in itertools.combinations(range(n), m):
            T = list(T)
            for A in itertools.combinations(range(r), m - 1):
                M = np.concatenate([np.ones((m, 1)), u[np.ix_(T, list(A))]], 1)
                d = np.linalg.det(M)
                if abs(d) < 1e-14:
                    continue
                w = lam ** (r + 1 - m) * np.prod(p[T]) * d * d
                num = num + w * np.linalg.solve(M, v[T])[0]
                den += w
    return num, den


def subset_volume_form(p, u, v, lam, sizes=None):
    """The same expansion with the coordinate sets summed out (Cauchy-Binet): weight lam^(r+1-m) prod_T p_j
    det(D D^T), D the differences u_j - u_{j0} (a squared (m-1)-volume; 1 for m = 1), value the minimum-norm
    affine interpolant through T at the query (u = 0)."""
    n, r = u.shape
    num, den = np.zeros(v.shape[1]), 0.0
    for m in range(1, min(n, r + 1) + 1):
        if sizes is not None and m not in sizes:
            continue
        for T in itertools.combinations(range(n), m):
            T = list(T)
            Dm = u[T[1:]] - u[T[0]]
            vol = np.linalg.det(Dm @ Dm.T) if m > 1 else 1.0
            if vol < 1e-14:
                continue
            b1 = np.linalg.pinv(Dm) @ (v[T[1:]] - v[T[0]]) if m > 1 else np.zeros((r, v.shape[1]))
            f = v[T[0]] - u[T[0]] @ b1
            w = lam ** (r + 1 - m) * np.prod(p[T]) * vol
            num = num + w * f
            den += w
    return num, den


# ----------------------------------------------------------------------------- the layer, isolated


def lla_cfg(r, **kw):
    c = argparse.Namespace(arch="lla", d=32, layers=2, heads=2, nheads=2, chart=r, chart_init=1.0, lam0=0.7,
                           cap=0.0, hops=1, lookback=0, ctx=12, vocab=50, mlp=64, remat=0, rank=4, order=2)
    for k, v in kw.items():
        setattr(c, k, v)
    return c


def lla_layer_weights(lyr, q, k, gate=1.0):
    """The layer's corrected weights W = p (1 - g d), from lm.lla_correction, float64."""
    T = q.shape[2]
    s = np.einsum("bhtc,bhsc->bhts", q, k) / math.sqrt(q.shape[-1])
    s = np.where(np.tril(np.ones((T, T), bool)), s, -1e9)
    p = softmax_rows(s)
    d = np.asarray(lm.lla_correction(lyr, jnp.asarray(q), jnp.asarray(k), jnp.asarray(p)))
    return p, p * (1 - gate * d)


def main():
    # ------------------------------------------------------------------ (c) the expansion on a single query
    for n, r in ((5, 2), (6, 3), (4, 3)):
        for lam in (0.0, 0.37, 5.0):
            if lam == 0.0 and n < r + 1:
                continue
            p = rng.random(n) ** 2; p /= p.sum()
            u = rng.normal(size=(n, r))
            v = rng.normal(size=(n, 3))
            ref = ridge_b0(p, u, v, lam) if lam > 0 else ridge_b0(p, u, v, 1e-300)
            if lam > 0:
                check(f"Jacobi on the augmented design = ridge fit (n={n}, r={r}, lambda={lam})",
                      float(np.abs(jacobi_augmented(p, u, v, lam) - ref).max()), 1e-10)
            num, den = subset_minor_form(p, u, v, lam)
            check(f"subset expansion, squared minors of [1, c_j - c_i] (n={n}, r={r}, lambda={lam})",
                  float(np.abs(num / den - ref).max()), 1e-10)
            num2, den2 = subset_volume_form(p, u, v, lam)
            check(f"subset expansion, volumes and min-norm fits (n={n}, r={r}, lambda={lam})",
                  float(np.abs(num2 / den2 - ref).max()), 1e-10)
            check(f"the two forms agree sector by sector (n={n}, r={r}, lambda={lam})",
                  max(float(np.abs(np.asarray(subset_minor_form(p, u, v, lam, {m})[0])
                                   - subset_volume_form(p, u, v, lam, {m})[0]).max()) for m in range(1, r + 2)), 1e-10)
            if lam > 0:
                n1, d1 = subset_minor_form(p, u, v, lam, {1})
                check(f"the m = 1 sector alone is softmax attention (n={n}, r={r})",
                      float(np.abs(n1 / d1 - p @ v).max()), 1e-12)
    # lambda = 0 with n > r + 1: only the top sector carries weight
    p = rng.random(7); p /= p.sum(); u = rng.normal(size=(7, 2)); v = rng.normal(size=(7, 2))
    num, den = subset_minor_form(p, u, v, 0.0, {3})
    check("lambda = 0: subsets of size r + 1 alone give the unregularised fit", float(np.abs(num / den - ridge_b0(p, u, v, 1e-300)).max()), 1e-10)
    # first order in 1/lambda is the pair sector: lambda (LLA - SA) -> N_2 - SA * D_2
    n2, d2 = subset_volume_form(p, u, v, 1.0, {2})
    lam = 1e7
    first = lam * (ridge_b0(p, u, v, lam) - p @ v)
    check("first order in 1/lambda = the pair sector, weights p_j p_l |c_j - c_l|^2", float(np.abs(first - (n2 - (p @ v) * d2)).max()), 1e-5)

    # ------------------------------------------------------------------ (a), (b) the layer itself
    B, H, T, dh = 2, 2, 9, 5
    for r in (1, 2, 4):
        cfg = lla_cfg(r, d=H * dh, heads=H)
        lyr = lm.init(jax.random.PRNGKey(r), cfg)["layers"][0]
        lyr["chart"] = jnp.asarray(rng.normal(size=(H, r, dh)))
        lyr["lam"] = jnp.asarray(rng.normal(size=(H,)))
        q = rng.normal(size=(B, H, T, dh)); k = rng.normal(size=(B, H, T, dh)) + 0.5  # a shared key offset
        v = rng.normal(size=(B, H, T, 3))
        p, W = lla_layer_weights(lyr, q, k)
        lam_h = np.asarray(jax.nn.softplus(lyr["lam"]) + lm.LAM_MIN)
        R = np.asarray(lyr["chart"])
        err_ridge = err_closed = err_exp = 0.0
        for b in range(B):
            for h in range(H):
                ck, cq = k[b, h] @ R[h].T, q[b, h] @ R[h].T
                for i in range(T):
                    pi, u = p[b, h, i, :i + 1], ck[:i + 1] - cq[i]
                    want = ridge_b0(pi, u, v[b, h, :i + 1], lam_h[h])
                    err_ridge = max(err_ridge, float(np.abs(W[b, h, i, :i + 1] @ v[b, h, :i + 1] - want).max()))
                    # the closed form on query-centred moments (LLA's eq. 8 with normalised weights)
                    mu = pi @ u
                    rho = np.linalg.solve((pi[:, None] * u).T @ u + lam_h[h] * np.eye(r), mu)
                    wc = pi * (1 - u @ rho) / (1 - mu @ rho)
                    err_closed = max(err_closed, float(np.abs(wc - W[b, h, i, :i + 1]).max()))
                    if i < 5 and r <= 2:
                        num, den = subset_volume_form(pi, u, v[b, h, :i + 1], lam_h[h])
                        err_exp = max(err_exp, float(np.abs(num / den - want).max()))
        check(f"(b) layer = explicit weighted ridge solve per query (r={r}, float64)", err_ridge, 1e-9)
        check(f"(b) layer = closed form p(1 - (c_j - c_i).rho)/(1 - mu.rho) (r={r})", err_closed, 1e-9)
        if r <= 2:
            check(f"(c) layer = subset expansion on causal prefixes (r={r})", err_exp, 1e-9)
        check(f"(e) layer weights on future tokens are exactly zero (r={r})", float(np.abs(np.triu(W, 1)).max()), 1e-300)
        check(f"(b) corrected weights sum to one (r={r})", float(np.abs(W.sum(-1) - 1).max()), 1e-12)
        _, W0 = lla_layer_weights(lyr, q, k, gate=0.0)
        check(f"(a) gate 0: weights are softmax exactly (r={r})", float(np.abs(W0 - p).max()), 1e-300)
        big = dict(lyr, lam=jnp.full((H,), 1e9))
        _, Wb = lla_layer_weights(big, q, k)
        check(f"(a) lambda = 1e9: weights are softmax to O(1/lambda) (r={r})", float(np.abs(Wb - p).max()), 1e-6)

    # float32 against float64 on sharp attention, a large shared key offset and a wide chart: the shifted
    # moments and the unrolled Cholesky keep the weights accurate at lambda = 1 and r = 16
    B32, T32, dh32, r32 = 2, 64, 16, 16
    cfg = lla_cfg(r32, d=H * dh32, heads=H)
    lyr = lm.init(jax.random.PRNGKey(9), cfg)["layers"][0]
    lyr["chart"] = jnp.asarray(rng.normal(size=(H, r32, dh32)) * 2 / math.sqrt(dh32))
    lyr["lam"] = jnp.full((H,), math.log(math.expm1(1.0)))
    q = rng.normal(size=(B32, H, T32, dh32)) * 3; k = rng.normal(size=(B32, H, T32, dh32)) * 3 + 4.0
    p64, W64 = lla_layer_weights(lyr, q, k)
    l32 = jax.tree_util.tree_map(lambda a: jnp.asarray(a, jnp.float32), lyr)
    d32 = lm.lla_correction(l32, jnp.asarray(q, jnp.float32), jnp.asarray(k, jnp.float32), jnp.asarray(p64, jnp.float32))
    W32 = np.asarray(p64, np.float32) * (1 - np.asarray(d32))
    print(f"     float32 weights: |W| up to {np.abs(W64).max():.2f}, largest softmax weight {p64.max():.4f}")
    check("float32 layer weights vs float64 (sharp attention, key offset 4, r = 16, lambda = 1)", float(np.abs(W32 - W64).max()), 1e-3)

    # ------------------------------------------------------------------ (d) Parallax
    cfgp = argparse.Namespace(arch="plx", d=H * dh, layers=1, heads=H, nheads=H, cap=0.0, hops=1, lookback=0, ctx=T,
                              vocab=20, mlp=16, remat=0, chart=1, chart_init=1.0, lam0=1.0)
    lyr = lm.init(jax.random.PRNGKey(1), cfgp)["layers"][0]
    lyr["wr"] = {"w": jnp.asarray(rng.normal(size=(H * dh, H * dh)) * 0.3), "b": jnp.asarray(rng.normal(size=H * dh) * 0.1)}
    x = rng.normal(size=(B, T, H * dh))
    q = rng.normal(size=(B, H, T, dh)); k = rng.normal(size=(B, H, T, dh)); v = rng.normal(size=(B, H, T, 3))
    s = np.where(np.tril(np.ones((T, T), bool)), np.einsum("bhtc,bhsc->bhts", q, k) / math.sqrt(dh), -np.inf)
    p = softmax_rows(s)
    d = np.asarray(lm.plx_correction(cfgp, lyr, jnp.asarray(x), jnp.asarray(k), jnp.asarray(p)))
    got = np.einsum("bhts,bhsc->bhtc", p * (1 - d), v)
    rho = (x @ np.asarray(lyr["wr"]["w"]) + np.asarray(lyr["wr"]["b"])).reshape(B, T, H, dh).transpose(0, 2, 1, 3)
    e_def = e_cov = e_str = 0.0
    for b in range(B):
        for h in range(H):
            for i in range(T):
                w = np.exp(s[b, h, i, :i + 1] - s[b, h, i, :i + 1].max())
                z = k[b, h, :i + 1] - q[b, h, i]                       # z_ij = k_j - q_i
                t = z @ rho[b, h, i]
                tb = (w @ t) / w.sum()
                coef = w * (1 - t + tb)
                o_def = coef @ v[b, h, :i + 1] / coef.sum()            # eq. 8, weighted form
                e_def = max(e_def, float(np.abs(o_def - got[b, h, i]).max()))
                pi = w / w.sum()
                vb, kb = pi @ v[b, h, :i + 1], pi @ k[b, h, :i + 1]
                skv = ((v[b, h, :i + 1] - vb) * pi[:, None]).T @ (k[b, h, :i + 1] - kb)
                e_cov = max(e_cov, float(np.abs(vb - skv @ rho[b, h, i] - got[b, h, i]).max()))
                # eq. 14 / Algorithm 1: online softmax over key blocks of 2, two accumulators
                m_r, d1, d2, O1, O2 = -np.inf, 0.0, 0.0, 0.0, 0.0
                for c0 in range(0, i + 1, 2):
                    js = list(range(c0, min(c0 + 2, i + 1)))
                    s1 = s[b, h, i, js]
                    m = max(m_r, s1.max())
                    alpha = np.exp(m_r - m) if np.isfinite(m_r) else 0.0
                    P1 = np.exp(s1 - m); m_r = m
                    P2 = P1 * (k[b, h, js] @ rho[b, h, i])
                    d1 = alpha * d1 + P1.sum(); d2 = alpha * d2 + P2.sum()
                    O1 = alpha * O1 + P1 @ v[b, h, js]; O2 = alpha * O2 + P2 @ v[b, h, js]
                o_str = O1 / d1 * (1 + d2 / d1) - O2 / d1
                e_str = max(e_str, float(np.abs(o_str - got[b, h, i]).max()))
    check("(d) Parallax layer = its definition (eq. 8, z = k - q, unnormalised kernel)", e_def, 1e-10)
    check("(d) Parallax layer = o_SA - Sigma_KV rho", e_cov, 1e-10)
    check("(d) Parallax streaming form (eq. 14, online softmax over key blocks) = the layer", e_str, 1e-10)
    # Parallax's correction is a pair sector with product weights and no volume selection:
    # -sum_j p_j (k_j - kbar).rho v_j = -1/2 sum_{j,l} p_j p_l ((k_j - k_l).rho)(v_j - v_l)
    b_, h_, i_ = 0, 1, T - 1
    pi, kk, vv, rr = p[b_, h_, i_], k[b_, h_], v[b_, h_], rho[b_, h_, i_]
    pair = -0.5 * sum(pi[j] * pi[l] * ((kk[j] - kk[l]) @ rr) * (vv[j] - vv[l]) for j in range(T) for l in range(T))
    check("(d) Parallax correction = a pair sum with weights p_j p_l and no volume factor",
          float(np.abs(pi @ vv + pair - got[b_, h_, i_]).max()), 1e-10)

    # Parallax with RMSNorm on rho (as published; gain 0 at init): the layer against eq. 8 with normalised rho
    cfgn = argparse.Namespace(**{**vars(cfgp), "plx_norm": 1})
    lyr = lm.init(jax.random.PRNGKey(1), cfgn)["layers"][0]
    lyr["rho_g"] = jnp.asarray(rng.normal(size=dh))
    d = np.asarray(lm.plx_correction(cfgn, lyr, jnp.asarray(x), jnp.asarray(k), jnp.asarray(p)))
    got = np.einsum("bhts,bhsc->bhtc", p * (1 - d), v)
    rho = (x @ np.asarray(lyr["wr"]["w"]) + np.asarray(lyr["wr"]["b"])).reshape(B, T, H, dh).transpose(0, 2, 1, 3)
    rho = rho / np.sqrt((rho ** 2).mean(-1, keepdims=True) + 1e-6) * np.asarray(lyr["rho_g"])
    o_def = np.zeros_like(got)
    for b in range(B):
        for h in range(H):
            for i in range(T):
                w = np.exp(s[b, h, i, :i + 1] - s[b, h, i, :i + 1].max())
                t = (k[b, h, :i + 1] - q[b, h, i]) @ rho[b, h, i]
                coef = w * (1 - t + (w @ t) / w.sum())
                o_def[b, h, i] = coef @ v[b, h, :i + 1] / coef.sum()
    check("(d) Parallax with RMSNorm on rho = its definition", float(np.abs(o_def - got).max()), 1e-10)

    # ------------------------------------------------------------------ (e) whole-model causality, init = softmax
    for arch, extra in (("lla", {}), ("plx", {}), ("plx", {"plx_norm": 1})):
        cm = lla_cfg(3, arch=arch, **extra)
        pm = lm.init(jax.random.PRNGKey(5), cm)
        pg = lm.init(jax.random.PRNGKey(5), argparse.Namespace(**{**vars(cm), "arch": "gpt"}))
        ids = jnp.asarray(rng.integers(0, 50, (1, 12)))
        same = max(float(jnp.abs(a - b).max()) for a, b in zip(jax.tree_util.tree_leaves({k_: v_ for k_, v_ in pg.items() if k_ != "layers"}),
                                                               jax.tree_util.tree_leaves({k_: v_ for k_, v_ in pm.items() if k_ != "layers"})))
        for la, lb in zip(pm["layers"], pg["layers"]):
            same = max(same, max(float(jnp.abs(la[n_][w_] - lb[n_][w_]).max()) for n_ in ("qkv", "o", "fc1", "fc2") for w_ in ("w", "b")))
        arch = arch + (" (RMSNorm on rho)" if extra else "")
        check(f"init: {arch} shares every softmax-model weight at the same seed", same, 1e-300)
        out0 = np.asarray(lm.forward(cm, pm, ids)); outg = np.asarray(lm.forward(argparse.Namespace(**{**vars(cm), "arch": "gpt"}), pg, ids))
        check(f"init: {arch} model output = softmax model output", float(np.abs(out0 - outg).max()), 1e-12)
        for lyr_ in pm["layers"]:
            if arch == "lla":
                lyr_["gate"] = jnp.ones_like(lyr_["gate"]) * 0.8
            elif "rho_g" in lyr_:
                lyr_["rho_g"] = jnp.ones_like(lyr_["rho_g"]) * 0.3
            else:
                lyr_["wr"]["w"] = jnp.asarray(rng.normal(size=lyr_["wr"]["w"].shape)) * 0.2
        base = np.asarray(lm.forward(cm, pm, ids))
        leak = 0.0
        for t in range(1, 12):
            ids2 = ids.at[0, t].set((ids[0, t] + 7) % 50)
            leak = max(leak, float(np.abs(np.asarray(lm.forward(cm, pm, ids2))[0, :t] - base[0, :t]).max()))
        check(f"(e) {arch} model: changing token t leaves every earlier output unchanged", leak, 1e-10)

    # gradients at init: the gate has a gradient; the chart has none until the gate opens; R = 0 is a saddle
    cm = lla_cfg(3)
    pm = lm.init(jax.random.PRNGKey(2), cm)
    ids = jnp.asarray(rng.integers(0, 50, (2, 12)))
    loss = lambda pp: jnp.mean(jax.nn.log_softmax(lm.forward(cm, pp, ids[:, :-1]))[..., 0] ** 2)
    g = jax.grad(loss)(pm)
    gg, gr = float(jnp.abs(g["layers"][0]["gate"]).max()), float(jnp.abs(g["layers"][0]["chart"]).max())
    print(f"     gradients at init: |dL/dgate| {gg:.2e}, |dL/dchart| {gr:.2e}")
    check("init: the chart has no gradient while the gate is closed", gr, 1e-300)
    check("init: the gate has a gradient (1 / |dL/dgate|)", 1.0 / max(gg, 1e-300), 1e8)
    for lyr_ in pm["layers"]:
        lyr_["gate"] = jnp.ones_like(lyr_["gate"])
    g1 = jax.grad(loss)(pm)
    check("open gate: the chart has a gradient (1 / |dL/dchart|)", 1.0 / max(float(jnp.abs(g1["layers"][0]["chart"]).max()), 1e-300), 1e8)
    for lyr_ in pm["layers"]:
        lyr_["chart"] = jnp.zeros_like(lyr_["chart"])
    g0 = jax.grad(loss)(pm)
    check("R = 0 is a stationary point for the chart even with the gate open", float(jnp.abs(g0["layers"][0]["chart"]).max()), 1e-300)

    # ------------------------------------------------------------------ FLOP counter
    s0 = argparse.Namespace(arch="gpt", d=512, layers=6, heads=8, mlp=2048, vocab=50304)
    check("FLOP counter: S0 softmax 6L reproduces 92,473,464 per token", abs(lm.flops_per_token(s0, 512) - 92473464.0), 0.5)
    print("     FLOPs per token at the S0 scale (ratio to softmax 6L):")
    base = lm.flops_per_token(s0, 512)
    for arch, r in (("plx", 0), ("lla", 1), ("lla", 2), ("lla", 4), ("lla", 8), ("lla", 16)):
        c = argparse.Namespace(**{**vars(s0), "arch": arch, "chart": r})
        f = lm.flops_per_token(c, 512)
        print(f"       {arch}{r or ''}: {f:,.0f} ({f / base:.4f})")
    # the counter's lla terms against an explicit tally for r = 8, one layer
    c8 = argparse.Namespace(**{**vars(s0), "arch": "lla", "chart": 8, "layers": 1})
    cg = argparse.Namespace(**{**vars(s0), "layers": 1})
    ta, D, H, r = 256.5, 512, 8, 8
    tally = (4 * D * r + H * 36 + 2 * ta * 44 * H + H * (72 + 512 / 3 + 128 + 32)
             + 2 * ta * D + 5 * ta * H + 2 * ta * 8 * H + 3 * ta * H)
    check("FLOP counter: lla r = 8 extra per layer matches an explicit tally", abs(lm.flops_per_token(c8, 512) - lm.flops_per_token(cg, 512) - tally), 1e-6)

    print("all checks passed" if ok else "SOME CHECKS FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
