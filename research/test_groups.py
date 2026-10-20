"""
Checks for GROUPS.md, run before any Modal grid:

    uv run --no-project --with "jax[cpu]" --with optax --with numpy python research/test_groups.py

1. Z12, A4, Z60 and A5 are groups of the right order, and only the cyclic ones commute.
2. Their character tables are orthogonal, sum to |G| in squared dimensions, the one-dimensional rows
   are homomorphisms, and the permutation action of A4 and A5 decomposes as trivial + standard.
3. rep_content reads exact representations correctly (rotations of Z_n, permutation matrices of A_n).
4. The ordered Match-3 labels agree with explicit loops; positive rates are printed.
5. holonomy_sectors equals the explicit sum over position-ordered subsets containing each position, and
   with commuting 2 x 2 rotations it is Newton attention's phi_i e_m(others).
6. The frozen character embedding has one-hot geometry (Gram = 81/2 I - 1/2 per copy), the rotated one
   the same Gram, and the models run forward and backward without NaN.
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
import groups  # noqa: E402
import polybench as pb  # noqa: E402

ok = True


def check(name, good, detail=""):
    global ok
    ok &= bool(good)
    print(f"{'ok ' if good else 'FAIL'} {name}{': ' + detail if detail else ''}")


def main():
    rng = np.random.default_rng(0)

    # 1. group axioms
    for name, order, abelian in (("Z12", 12, True), ("A4", 12, False), ("Z60", 60, True), ("A5", 60, False)):
        G = groups.get(name)
        m = G.mul
        assoc = (m[m[:, :, None], np.arange(G.n)[None, None]] == m[np.arange(G.n)[:, None, None], m[None]]).all()
        ident = (m[G.e] == np.arange(G.n)).all() and (m[:, G.e] == np.arange(G.n)).all()
        inv = (m[np.arange(G.n), G.inv] == G.e).all()
        latin = all(len(set(row)) == G.n for row in m) and all(len(set(col)) == G.n for col in m.T)
        check(f"{name}: order {G.n}, associative, identity, inverses, Latin square, abelian={G.abelian}",
              G.n == order and assoc and ident and inv and latin and G.abelian == abelian)

    # 2. character tables
    for name in ("Z12", "A4", "Z60", "A5"):
        G = groups.get(name)
        sizes = np.array([len(c) for c in G.classes])
        gram = (G.chars * sizes) @ G.chars.conj().T / G.n
        check(f"{name}: {len(G.dims)} irreps, rows orthonormal, sum d^2 = |G|",
              np.allclose(gram, np.eye(len(G.dims))) and (G.dims ** 2).sum() == G.n and sizes.sum() == G.n)
        one = [i for i, d in enumerate(G.dims) if d == 1]
        hom = all(np.allclose(G.char_el[i][G.mul], np.outer(G.char_el[i], G.char_el[i])) for i in one)
        check(f"{name}: the {len(one)} one-dimensional characters are homomorphisms", hom)
    for name, m, want in (("A4", 4, [1, 0, 0, 1]), ("A5", 5, [1, 0, 0, 1, 0])):
        G = groups.get(name)
        perms = [p for p in itertools.permutations(range(m)) if groups._parity(p) == 0]
        P = np.zeros((1, G.n, m, m))
        for i, p in enumerate(perms):
            P[0, i, list(p), range(m)] = 1   # P e_x = e_{p(x)}, so P_a P_b = P_{a*b}
        rc = groups.rep_content(G, P)
        check(f"{name}: permutation action = trivial + standard ({want})",
              rc["top"][0]["hom_err"] < 1e-12 and np.allclose(rc["top"][0]["mult"], want), str(rc["top"][0]["mult"]))

    # 3. rep_content on rotations of Z12: R(2 pi j k / n) holds the characters j and -j
    G = groups.get("Z12")
    j = 5
    ang = 2 * np.pi * j * np.arange(G.n) / G.n
    R = np.stack([np.stack([np.cos(ang), -np.sin(ang)], -1), np.stack([np.sin(ang), np.cos(ang)], -1)], -2)[None]
    rc = groups.rep_content(G, R)
    check("Z12: a rotation by 2 pi 5k/12 holds characters 5 and 7, mass 2/11",
          rc["held"] == [5, 7] and abs(rc["mass"] - 2 / 11) < 1e-3, f"held {rc['held']} mass {rc['mass']}")
    for name, want in (("A5", {2: 0.0, 3: 18 / 59, 4: 34 / 59, 5: 1.0, 8: 1.0}),
                       ("A4", {2: 2 / 11, 3: 1.0}), ("Z60", {2: 1.0}), ("Z12", {2: 1.0})):
        G = groups.get(name)
        got = {d: round(groups.plancherel(G, groups.reachable(G, d)), 4) for d in want}
        check(f"{name}: reachable Plancherel mass by head dimension", all(abs(got[d] - want[d]) < 1e-4 for d in want), str(got))

    # 4. task labels against explicit loops, and positive rates
    for name, n in (("Z12", 6), ("A4", 6), ("Z60", 11), ("A5", 11)):
        G = groups.get(name)
        tok, tgt, msk = groups.task_gmatch(rng, 64, name, n, 3)
        g = tok[:, 1:, 0]
        ref = np.zeros_like(tgt[:, 1:])
        for b in range(64):
            for i, j, l in itertools.combinations(range(n), 3):
                if G.mul[G.mul[g[b, i], g[b, j]], g[b, l]] == G.e:
                    ref[b, [i, j, l]] = 1
        _, tg, _ = groups.task_gmatch(np.random.default_rng(1), 4096, name, n, 3)
        check(f"{name}, n = {n}: labels match explicit loops; BOS unscored", (ref == tgt[:, 1:]).all() and (msk[:, 0] == 0).all(),
              f"positive rate {tg[:, 1:].mean():.3f}")
    # order matters for A5: the same multiset in another order can change the label
    G = groups.get("A5")
    g = np.random.default_rng(2).integers(0, G.n, (2000, 11))
    a = groups.match_labels(G, g, 3)
    b = groups.match_labels(G, g[:, ::-1], 3)[:, ::-1]
    Z = groups.get("Z60")
    za = groups.match_labels(Z, g, 3)
    zb = groups.match_labels(Z, g[:, ::-1], 3)[:, ::-1]
    check("reversing the sequence changes A5 labels, never Z60 labels", (a != b).mean() > 0.05 and (za == zb).all(),
          f"A5 labels changed on {(a != b).mean():.1%} of positions")

    # 5. holonomy_sectors against explicit subsets, float64
    B, T, H, d, K = 2, 6, 2, 3, 4
    M = jnp.asarray(rng.normal(size=(B, T, H, d, d)))
    F = holo = pb.holonomy_sectors(M, K)
    worst = 0.0
    Mn = np.asarray(M)
    for m in range(K):
        ref = np.zeros((B, T, H, d, d))
        for S in itertools.combinations(range(T), m + 1):
            P = np.broadcast_to(np.eye(d), (B, H, d, d)).copy()
            for t in S:
                P = P @ Mn[:, t]
            for i in S:
                ref[:, i] += P
        worst = max(worst, float(np.abs(np.asarray(holo[m]) - ref).max()))
    check("holonomy sectors = explicit sums over position-ordered subsets containing i (float64)", worst < 1e-10, f"max error {worst:.1e}")
    # commuting rotations: F_m = phi_i e_m(others) with phi = g exp(i theta), read as [[Re, -Im], [Im, Re]]
    th = rng.uniform(0, 2 * np.pi, (B, T, H))
    gt = rng.uniform(0.2, 1, (B, T, H))
    rot = np.stack([np.stack([np.cos(th), -np.sin(th)], -1), np.stack([np.sin(th), np.cos(th)], -1)], -2) * gt[..., None, None]
    F2 = pb.holonomy_sectors(jnp.asarray(rot), K)
    phi = gt * np.exp(1j * th)
    worst = 0.0
    for m in range(K):
        e = np.zeros((B, T, H), complex)
        for i in range(T):
            others = np.delete(phi, i, axis=1)
            e[:, i] = sum(np.prod(others[:, list(S)], 1) for S in itertools.combinations(range(T - 1), m)) if m else 1
        z = phi * e
        worst = max(worst, float(np.abs(np.asarray(F2[m])[..., 0, 0] - z.real).max()), float(np.abs(np.asarray(F2[m])[..., 1, 0] - z.imag).max()))
    check("with commuting 2 x 2 rotations the sectors are Newton attention's phi_i e_m(others)", worst < 1e-10, f"max error {worst:.1e}")

    # 6. character embedding geometry
    cards = np.array([[(v // 3 ** a) % 3 for a in range(4)] for v in range(81)])
    tok = jnp.asarray(np.concatenate([np.full((1, 4), 3), cards])[None])
    for emb in ("char", "charrot"):
        c = argparse.Namespace(embed=emb, d=192)
        X = np.asarray(pb.char_embed(c, tok))[0]
        Xc = X[1:, :80]
        gram = Xc @ Xc.T
        want = 81 / 2 * np.eye(81) - 1 / 2
        check(f"--embed {emb}: card Gram matrix = 81/2 I - 1/2 (one-hot geometry), mean 0, BOS separate",
              np.allclose(gram, want, atol=1e-4) and np.allclose(X[1:].mean(-1), 0, atol=1e-6) and X[0, 160] == 4.0)

    # forward and backward: holonomy layer on A5, softmax on frozen characters, Newton on Z60
    for task, extra in (("g3_a5", dict(model="holo", gdim=5, heads=8, order=3, pos=0, embed="table", d=64)),
                        ("g3_z12", dict(model="holo", gdim=2, heads=16, order=3, pos=0, embed="table", d=64)),
                        ("zs4", dict(model="sa", embed="char", pos=0, d=192)),
                        ("g3_z60", dict(model="newton", rank=16, order=3, readout="shared", fnorm=1, pos=0, embed="table", d=64))):
        cfg = argparse.Namespace(task=task, layers=1, heads=4, phase=2.0, fnorm=1, ffn=1, repeat=0, recur=1, rawphase=0,
                                 readout="shared", rank=32, order=6, wide=4, vdim=8, plen=3, modes=16, nocubic=0, dh=0)
        for k, v in extra.items():
            setattr(cfg, k, v)
        gen, vocabs, C, _ = pb.TASKS[task]
        t, y, mk = gen(np.random.default_rng(0), 8)
        p = pb.init(jax.random.PRNGKey(0), cfg, vocabs, C, t.shape[1])

        def loss(p):
            lg = pb.forward(cfg, p, jnp.asarray(t))
            return (jax.nn.logsumexp(lg, -1) - jnp.take_along_axis(lg, jnp.asarray(y)[..., None], -1)[..., 0]).mean()

        l, g = jax.value_and_grad(loss)(p)
        finite = bool(jnp.isfinite(l)) and all(bool(jnp.isfinite(x).all()) for x in jax.tree_util.tree_leaves(g))
        check(f"{task} / {extra['model']}: forward and backward finite", finite, f"loss {float(l):.3f}")
        if extra["model"] == "holo":
            U = pb.holo_mats(cfg, p["layers"][0]["attn"], jnp.asarray(rng.normal(size=(5, 64))))
            orth = float(jnp.abs(jnp.einsum("thij,thkj->thik", U, U) - jnp.eye(cfg.gdim)).max())
            det = np.asarray(jnp.linalg.det(U))
            check(f"  its rotations are orthogonal with determinant 1 (d = {cfg.gdim})", orth < 1e-9 and np.allclose(det, 1), f"{orth:.1e}")
            rc = pb.holo_rep_content(cfg, p)
            check(f"  untrained rep_content runs (reachable mass {rc['reachable_mass']})", "held" in rc, f"hom_err quantiles {rc['hom_err_q']}")

    print("all checks passed" if ok else "SOME CHECKS FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
