"""
Brute-force checks of subset attention (polybench --model sfa, lm.py --arch sfa) against explicit
sums over subsets:

    python research/test_sfa.py

For every query q and arity m it enumerates the m-subsets S of the other tokens (multisets for the
bosonic variant), forms E_m = sum_S prod_{t in S} p_qt phi_t and N_m = sum_S prod_{t in S} p_qt, and
compares the vacuum-weighted ratio

    sum_i E_i mu^(m-i) / (m-i)!  /  sum_i N_i mu^(m-i) / (m-i)!       (mu = 0: E_m / N_m)

with the layer's Newton-identity value: exactly in float64, and to float32 tolerance on sharp attention.
It also checks that zero-initialised queries without a vacuum reproduce Newton attention, that arity 2
is softmax attention, and the causal (prefix) version used by the language model.
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
import polybench as pb  # noqa: E402


def brute(p, phi, K, mu=0.0, bose=False):
    """Explicit subset sums. p: [B, H, Q, T], phi: [B, H, T, r] -> list of K arrays [B, H, Q, r]."""
    B, H, Q, T = p.shape
    E = [np.ones((B, H, Q, phi.shape[-1]), complex)]
    N = [np.ones((B, H, Q, 1))]
    pick = itertools.combinations_with_replacement if bose else itertools.combinations
    for m in range(1, K):
        num = np.zeros((B, H, Q, phi.shape[-1]), complex)
        den = np.zeros((B, H, Q, 1))
        for S in pick(range(T), m):
            S = list(S)
            w = np.prod(p[..., S], -1)[..., None]  # [B, H, Q, 1]
            num += w * np.prod(phi[:, :, S], 2)[:, :, None]
            den += w
        E.append(num)
        N.append(den)
    out = []
    for m in range(K):
        num = sum(E[i] * mu ** (m - i) / math.factorial(m - i) for i in range(m + 1))
        den = sum(N[i] * mu ** (m - i) / math.factorial(m - i) for i in range(m + 1))
        out.append(np.where(den > 0, num / np.where(den > 0, den, 1), 0))
    return out


def worst(a, b):
    return max(float(np.max(np.abs(np.asarray(x) - y))) for x, y in zip(a, b))


def layer_cfg(**kw):
    c = argparse.Namespace(model="sfa", d=32, heads=2, rank=3, order=6, phase=2.0, readout="shared",
                           fnorm=0, vac=0.2, cap=0.0, qzero=0, stats="fermi", vpath=1, layers=1, recur=1, rawphase=0,
                           plen=3, wide=4, vdim=8, modes=8, nocubic=0, hops=0,
                           embed="table", pos=1, ffn=1, repeat=0)
    for k, v in kw.items():
        setattr(c, k, v)
    return c


def main():
    rng = np.random.default_rng(0)
    ok = True

    def check(name, err, tol):
        nonlocal ok
        good = err < tol
        ok &= good
        print(f"{'ok ' if good else 'FAIL'} {name}: max error {err:.2e} (tolerance {tol:g})")

    # 1. the Newton-identity moments against explicit subsets, both statistics, float64
    B, H, T, r, K = 2, 2, 7, 3, 6
    p = rng.random((B, H, T, T)) ** 3
    p[..., np.arange(T), np.arange(T)] = 0
    p /= p.sum(-1, keepdims=True)
    phi = rng.uniform(0.1, 1, (B, H, T, r)) * np.exp(1j * rng.uniform(0, 2 * np.pi, (B, H, T, r)))
    for mu in (0.0, 0.2):
        for bose in (False, True):
            got = pb.subset_moments(jnp.asarray(p), jnp.asarray(phi), K, mu, bose=bose)
            check(f"moments vs subsets ({'bosons' if bose else 'fermions'}, vacuum {mu}, float64)",
                  worst(got, brute(p, phi, K, mu, bose)), 1e-10)

    # 2. the whole layer: its arity read-outs are the brute-force moments, read by the shared projection
    x = jnp.asarray(rng.normal(size=(B, T, 32)))
    for qzero, vac in ((0, 0.2), (1, 0.0)):
        cfg = layer_cfg(qzero=qzero, vac=vac)
        a = pb.init(jax.random.PRNGKey(qzero), cfg, [4], 2, T)["layers"][0]["attn"]
        heads = lambda t: t.reshape(B, T, cfg.heads, -1).transpose(0, 2, 1, 3)
        s, pw, ph = pb.sfa_inputs(cfg, a, x, heads, 16)
        pw, ph = np.asarray(pw), np.asarray(ph)
        ref = brute(pw, ph, cfg.order, vac)
        feats = np.stack([ph * ref[m] for m in range(cfg.order)], 3)
        feats = np.concatenate([feats.real, feats.imag], -1).transpose(0, 2, 1, 3, 4)
        want = np.einsum("bthkc,hcd->btkd", feats, np.asarray(a["o"]["w"]).reshape(cfg.heads, 2 * cfg.rank, -1))
        want = want * np.asarray(a["alpha"])[None, None]
        c2 = layer_cfg(qzero=qzero, vac=vac, want_parts=True)
        got = pb.attention(c2, a, x)
        check(f"layer arity parts vs subsets (qzero={qzero}, float64)", float(np.max(np.abs(np.asarray(got) - want))), 1e-9)
        if qzero:
            # zero queries: uniform weights over the other tokens, Newton attention's e_m / C(T-1, m)
            others = [np.delete(ph, i, axis=2) for i in range(T)]
            for m in range(1, cfg.order):
                e = np.stack([sum(np.prod(o[:, :, list(S)], 2) for S in itertools.combinations(range(T - 1), m)) for o in others], 2)
                check(f"zero queries = Newton attention, arity {m + 1}", float(np.max(np.abs(ref[m] - e / math.comb(T - 1, m)))), 1e-12)
        # arity 2 is softmax attention over the other tokens with values phi, plus a sink of value 1
        sm = (np.einsum("bhqt,bhtc->bhqc", pw, ph) + vac) / (1 + vac)
        check(f"arity 2 = softmax attention (vacuum {vac})", float(np.max(np.abs(ref[1] - sm))), 1e-12)

    # 3. float32 on sharp attention, no cap, against the float64 subsets: the vacuum keeps it accurate
    x32 = jnp.asarray(rng.normal(size=(B, T, 32)) * 4, jnp.float32)
    for vac, tol in ((0.2, 1e-3), (0.0, None)):
        cfg = layer_cfg(vac=vac)
        a = jax.tree_util.tree_map(lambda t: t.astype(jnp.float32), pb.init(jax.random.PRNGKey(3), cfg, [4], 2, T)["layers"][0]["attn"])
        a["q"]["w"] = a["q"]["w"] * 8  # sharp attention
        heads = lambda t: t.reshape(B, T, cfg.heads, -1).transpose(0, 2, 1, 3)
        s_, pw, ph = pb.sfa_inputs(cfg, a, x32, heads, 16)
        got = pb.subset_moments(pw, ph, cfg.order, vac)
        ref = brute(np.asarray(pw, np.float64), np.asarray(ph, np.complex128), cfg.order, vac)
        err = worst(got, ref)
        if tol is None:
            print(f"     without a vacuum the same float32 read-out is off by {err:.2e} (largest weight {float(pw.max()):.6f})")
        else:
            check(f"float32 moments on sharp attention (vacuum {vac}) vs float64 subsets", err, tol)

    # 4. causal version (language model): subsets of the strict past, read at every position
    cl = argparse.Namespace(arch="sfa", heads=2, nheads=2, rank=3, order=5, phase=2.0, vac=0.2, cap=0.0, d=32)
    Tc = 8
    q = jnp.asarray(rng.normal(size=(B, 2, Tc, 16)))
    k = jnp.asarray(rng.normal(size=(B, 2, Tc, 16)))
    th = jnp.asarray(rng.normal(size=(B, 2, Tc, 3)))
    g = jnp.asarray(rng.random((B, 2, Tc, 3)))
    phic = g * jnp.exp(1j * th)
    A, pc = lm.causal_subset_moments(cl, q, k, phic)
    pc = np.asarray(pc)
    ref = brute(pc, np.asarray(phic), cl.order, cl.vac)
    check("causal moments vs subsets of the strict past (float64)", worst(A, ref), 1e-10)
    tri = np.tril(np.ones((Tc, Tc), bool), -1)
    check("causal weights live on the strict past only", float(np.abs(pc * ~tri).max()), 1e-15)
    # the first position has no past: every subset is empty slots, so every arity reads 1
    check("causal first position reads the vacuum", max(float(np.abs(np.asarray(A[m])[:, :, 0] - 1).max()) for m in range(cl.order)), 1e-12)

    print("all checks passed" if ok else "SOME CHECKS FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
