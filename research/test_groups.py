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
7. Word problems (section 7): S5's determinants from characters match explicit matrices, which irreps
   fit SO(d), the word-task labels against composed permutations, the commuting ceiling, the S5 = A5 x| Z2
   decomposition, the causal holonomy sectors and prefix product against explicit sums, the DeltaProduct
   scan against an explicit loop, and how many Householders an element needs (Cartan-Dieudonne).
8. Interleaved swap programs match a literal interpreter, their order-blind Bayes ceiling is exact,
   a hand-built SO(3) gated sector executes the queried namespace, and the matrix-state baseline is correct.
"""

import argparse
import collections
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
    for name, order, abelian in (("Z12", 12, True), ("A4", 12, False), ("Z60", 60, True), ("A5", 60, False), ("S5", 120, False)):
        G = groups.get(name)
        m = G.mul
        assoc = (m[m[:, :, None], np.arange(G.n)[None, None]] == m[np.arange(G.n)[:, None, None], m[None]]).all()
        ident = (m[G.e] == np.arange(G.n)).all() and (m[:, G.e] == np.arange(G.n)).all()
        inv = (m[np.arange(G.n), G.inv] == G.e).all()
        latin = all(len(set(row)) == G.n for row in m) and all(len(set(col)) == G.n for col in m.T)
        check(f"{name}: order {G.n}, associative, identity, inverses, Latin square, abelian={G.abelian}",
              G.n == order and assoc and ident and inv and latin and G.abelian == abelian)

    # 2. character tables
    for name in ("Z12", "A4", "Z60", "A5", "S5"):
        G = groups.get(name)
        sizes = np.array([len(c) for c in G.classes])
        gram = (G.chars * sizes) @ G.chars.conj().T / G.n
        check(f"{name}: {len(G.dims)} irreps, rows orthonormal, sum d^2 = |G|",
              np.allclose(gram, np.eye(len(G.dims))) and (G.dims ** 2).sum() == G.n and sizes.sum() == G.n)
        one = [i for i, d in enumerate(G.dims) if d == 1]
        hom = all(np.allclose(G.char_el[i][G.mul], np.outer(G.char_el[i], G.char_el[i])) for i in one)
        check(f"{name}: the {len(one)} one-dimensional characters are homomorphisms", hom)
    for name, m, want in (("A4", 4, [1, 0, 0, 1]), ("A5", 5, [1, 0, 0, 1, 0]), ("S5", 5, [1, 0, 1, 0, 0, 0, 0])):
        G = groups.get(name)
        perms = [p for p in itertools.permutations(range(m)) if name == "S5" or groups._parity(p) == 0]
        assert perms == G.perms
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

    # Swap-program benchmark: exhaustive short-program interpreter, key isolation, exact Bayes ceiling.
    pairs = list(itertools.combinations(range(4), 2))
    programs = np.asarray(list(itertools.product(range(6), repeat=3)))
    worst_swap = 0
    for q in range(4):
        got = groups.swap_program_labels(programs, np.full(len(programs), q), namespaces=1)
        ref = []
        for program in programs:
            state = dict(enumerate(range(4)))
            for instruction in program:
                a, b = pairs[instruction]
                state[a], state[b] = state[b], state[a]
            ref.append(state[q])
        worst_swap += np.count_nonzero(got != ref)
    check("swap3: all 216 single-namespace programs x four queries match a literal interpreter", worst_swap == 0)
    tok, tgt, msk = groups.task_swap_program(rng, 1024)
    instructions, query = tok[:, 1:-1, 0], tok[:, -1, 0] - 12
    key = query // 4
    selected = np.stack([row[row // 6 == k] % 6 for row, k in zip(instructions, key)])
    ref = groups.swap_program_labels(selected, query % 4, namespaces=1)
    check("swap3: distractor namespace never changes query answer; BOS/instructions unscored",
          np.array_equal(tgt[:, -1], ref) and (msk[:, :-1] == 0).all() and (msk[:, -1] == 1).all()
          and (tok[:, 0, 0] == 20).all())
    reverse = groups.swap_program_labels(instructions[:, ::-1], query)
    check("swap3: instruction order changes answers", (reverse != tgt[:, -1]).mean() > 0.1,
          f"reversal changes {(reverse != tgt[:, -1]).mean():.1%}")
    num, den = groups.swap_order_blind_ceiling()
    check("swap3: exact order-blind Bayes ceiling is 67/108 = 62.037...%",
          num * 108 == den * 67, f"{num}/{den} = {num / den:.9f}")
    # A hand-built SO(3) head selects one namespace. At the query its arity-four sector is
    # precisely the three selected swaps' product, including when distractors are interleaved.
    basis, _ = np.linalg.qr(np.eye(4)[:, :3] - np.eye(4)[:, 3, None])
    perm = np.eye(4)[np.arange(4)]
    swaps = []
    for a, b in pairs:
        P = perm.copy()
        P[[a, b]] = P[[b, a]]
        swaps.append(-basis.T @ P @ basis)  # sign-twisted standard representation of S4
    rotations = np.asarray(swaps)
    permutations = list(itertools.permutations(range(4)))
    index = {p: i for i, p in enumerate(permutations)}
    matrices = []
    for p in permutations:
        P = np.zeros((4, 4))
        P[list(p), np.arange(4)] = 1
        matrices.append((-1) ** groups._parity(p) * basis.T @ P @ basis)
    matrices = np.asarray(matrices)
    product_ids = np.asarray([[index[tuple(a[b[x]] for x in range(4))] for b in permutations] for a in permutations])
    check("S4: the sign-twisted standard representation is a faithful SO(3) homomorphism",
          np.allclose(np.linalg.det(matrices), 1)
          and np.allclose(matrices[:, None] @ matrices[None], matrices[product_ids])
          and len(np.unique(np.round(matrices, 10).reshape(24, 9), axis=0)) == 24)
    sample = tok[:32, :, 0]
    mats = np.zeros((32, sample.shape[1], 2, 3, 3))
    for h in range(2):
        for i in range(1, sample.shape[1] - 1):
            ids = sample[:, i]
            mats[:, i, h] = rotations[ids % 6] * (ids // 6 == h)[:, None, None]
        mats[:, -1, h] = np.eye(3)
    sector = np.asarray(pb.holonomy_sectors(jnp.asarray(mats), 4)[3])[:, -1]
    decoded = []
    for b in range(len(sample)):
        q = int(query[b])
        # There are three transpositions, hence sign=-1; restore the trivial coordinate.
        P = -basis @ sector[b, q // 4] @ basis.T + np.ones((4, 4)) / 4
        decoded.append(int(P[:, q % 4].argmax()))
    check("swap3: hand-built SO(3) gated arity-four heads exactly execute both namespaces",
          np.array_equal(decoded, tgt[:32, -1]) and np.allclose(np.linalg.det(rotations), 1))

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

    prefix = np.asarray(pb.orthogonal_prefix(M))
    ref = np.broadcast_to(np.eye(d), (B, H, d, d)).copy()
    worst = 0.0
    for t in range(T):
        ref = Mn[:, t] @ ref
        worst = max(worst, float(np.max(np.abs(prefix[:, t] - ref))))
    check("matrix-state baseline recurrence agrees with explicit left-multiplied prefix products",
          worst < 1e-10, f"max error {worst:.1e}")

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
                        ("g3_z60", dict(model="newton", rank=16, order=3, readout="shared", fnorm=1, pos=0, embed="table", d=64)),
                        ("swap3", dict(model="orthornn", gdim=6, heads=4, pos=0, embed="table", d=64))):
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

    word_checks(rng)
    print("all checks passed" if ok else "SOME CHECKS FAILED")
    sys.exit(0 if ok else 1)


def perm_mats(perms):
    m = len(perms[0])
    P = np.zeros((len(perms), m, m))
    for i, p in enumerate(perms):
        P[i, list(p), range(m)] = 1
    return P


def standard(perms):
    """The standard representation: permutation matrices on the sum-zero subspace, orthonormal basis."""
    m = len(perms[0])
    Bz = np.linalg.qr(np.concatenate([np.ones((m, 1)), np.eye(m)[:, : m - 1]], 1))[0][:, 1:]
    return np.einsum("xa,gxy,yb->gab", Bz, perm_mats(perms), Bz)


def householders(Q, tol=1e-9):
    """Cartan-Dieudonne, constructively: unit u_1..u_r with Q = H_1 ... H_r, H = I - 2 u u^T, r = rank(Q - I)."""
    d = Q.shape[0]
    us, R = [], Q.copy()
    while np.abs(R - np.eye(d)).max() > tol:
        x = np.eye(d)[np.argmax(np.linalg.norm(R - np.eye(d), axis=0))]
        u = R @ x - x
        u /= np.linalg.norm(u)
        us.append(u)
        R = (np.eye(d) - 2 * np.outer(u, u)) @ R       # now fixes x and everything R fixed
    return us


def word_checks(rng):
    S5, A5 = groups.get("S5"), groups.get("A5")

    # determinants from characters against explicit matrices; which irreps fit SO(d)
    std = standard(S5.perms)
    sgn = S5.char_el[1].real
    check("S5: the standard representation (explicit) is a homomorphism with character chi_4, det = sign",
          np.allclose(np.einsum("aij,bjk->abik", std, std), std[S5.mul]) and np.allclose(np.trace(std, axis1=1, axis2=2), S5.char_el[2].real)
          and np.allclose(np.linalg.det(std), sgn))
    dets = {i: groups.irrep_det(S5, i) for i in range(7)}
    hom = all(np.allclose(dets[i][S5.mul], np.outer(dets[i], dets[i])) for i in range(7))
    want = {0: 1, 1: -1, 2: -1, 3: -1, 4: 1, 5: -1, 6: -1}           # 1 = trivial, -1 = sign
    check("S5: det of every irrep (from characters) is a character; only 1 and 5 have det 1",
          hom and all(np.allclose(dets[i], 1 if v == 1 else sgn) for i, v in want.items()))
    check("A5, A4: every irrep has det 1 (A5 perfect; A4's 3 is the tetrahedral rotation group)",
          all(np.allclose(groups.irrep_det(groups.get(n), i)[np.isclose(groups.get(n).chars[i].imag, 0).all() * np.ones(groups.get(n).n, bool)], 1)
              for n in ("A5", "A4") for i in range(len(groups.get(n).dims)) if np.allclose(groups.get(n).chars[i].imag, 0)))
    ker = [i for i in range(7) if (np.isclose(S5.char_el[i], S5.dims[i]).sum() == 1)]
    reach = {d: groups.reachable(S5, d) for d in (2, 3, 4, 5, 6, 7)}
    first = min(d for d in reach if set(reach[d]) & set(ker))
    check("S5: faithful irreps are 4, 4', 5, 5', 6; the first SO(d) holding one is d = 5 (5, or 4 + sign)",
          ker == [2, 3, 4, 5, 6] and first == 5 and reach[4] == [1] and reach[5] == [1, 2, 3, 4], str(reach))
    got = {d: round(groups.plancherel(S5, reach[d]), 4) for d in reach}
    check("S5: reachable Plancherel mass in SO(d)", got == {2: round(1 / 119, 4), 3: round(1 / 119, 4), 4: round(1 / 119, 4),
                                                         5: round(58 / 119, 4), 6: round(83 / 119, 4), 7: 1.0}, str(got))

    # Householders per element (Cartan-Dieudonne): A5 in its 3-dimensional irrep needs 2, S5 in the standard 4
    w2 = np.zeros((60, 6, 6))
    pairs = list(itertools.combinations(range(4), 2))
    stdA = standard(A5.perms)
    for g in range(60):
        M = stdA[g]
        for r, (i, j) in enumerate(pairs):
            for c, (k, l) in enumerate(pairs):
                w2[g, r, c] = M[i, k] * M[j, l] - M[i, l] * M[j, k]
    Pj = 3 / 60 * np.einsum("g,gij->ij", A5.char_el[1].real, w2)          # projector onto the irrep 3
    Qb = np.linalg.svd(Pj)[0][:, :3]
    r3 = np.einsum("ia,gij,jb->gab", Qb, w2, Qb)
    hom3 = np.allclose(np.einsum("aij,bjk->abik", r3, r3), r3[A5.mul]) and np.allclose(np.trace(r3, axis1=1, axis2=2), A5.char_el[1].real)
    nA = [len(householders(r3[g])) for g in range(60)]
    recon = all(np.allclose(np.linalg.multi_dot([np.eye(3)] + [np.eye(3) - 2 * np.outer(u, u) for u in householders(r3[g])] + [np.eye(3)]), r3[g]) for g in range(60))
    check("A5: the icosahedral 3 (from wedge^2 of the standard) is a rotation group; every element is <= 2 Householders",
          hom3 and np.allclose(np.linalg.det(r3), 1) and recon and max(nA) == 2, f"Householders per element: {collections.Counter(nA)}")
    nS = [len(householders(std[g])) for g in range(120)]
    rank = [int(np.linalg.matrix_rank(std[g] - np.eye(4), tol=1e-9)) for g in range(120)]
    check("S5: in the standard 4 every element is rank(Q - I) <= 4 Householders (minimal), only the 24 five-cycles need 4",
          max(nS) == 4 and nS.count(4) == 24 and nS == rank, f"Householders per element: {sorted(collections.Counter(nS).items())}")
    need = {n: groups.householders_needed(groups.get(n)) for n in ("A4", "A5", "S5")}
    check("fewest Householders per token for an exact faithful representation: A4 2, A5 2, S5 4", need == {"A4": 2, "A5": 2, "S5": 4}, str(need))

    # word-task labels against permutations composed directly
    for name in ("A5", "S5"):
        G = groups.get(name)
        tok, tgt, msk = groups.task_word(np.random.default_rng(3), 32, name, 16, "class")
        _, sgt, _ = groups.task_word(np.random.default_rng(3), 32, name, 16, "stab")
        good = True
        for b in range(32):
            p = tuple(range(5))
            for t in range(16):
                q = G.perms[tok[b, t + 1, 0]]
                p = tuple(p[q[x]] for x in range(5))                      # (p * q)(x) = p(q(x))
                good &= G.perms[tgt[b, t + 1]] == p and sgt[b, t + 1] == (p[4] == 4)
        _, big, _ = groups.task_word(np.random.default_rng(4), 4096, name, 16, "stab")
        check(f"{name}: word-problem labels = composed permutations, stabiliser labels = fixes 4; BOS unscored",
              good and (msk[:, 0] == 0).all() and tok[:, 0, 0].tolist() == [G.n] * 32, f"stabiliser rate {big[:, 1:].mean():.3f}")
    # commuting ceiling: exact for abelian groups, exact at the first two positions, then falls to chance
    cz = groups.word_commuting_ceiling("Z60", 8, "class", samples=200, perms=32)
    ca = groups.word_commuting_ceiling("A5", 8, "class", samples=400, perms=128)
    check("commuting ceiling: Z60 exact at every position; A5 exact at t = 1, 2 and near 1/2 at t = 3",
          np.allclose(cz["per_pos"], 1) and np.allclose(ca["per_pos"][:2], 1) and 0.45 < ca["per_pos"][2] < 0.62,
          f"A5 {np.round(ca['per_pos'], 3)}")
    # S5 = A5 x| Z2: with p_s the parity of g_1..g_s and tau = (01), h_s = tau^p_{s-1} g_s tau^p_s is even and
    # g_1 ... g_t = h_1 ... h_t tau^p_t, so two layers (parity, then A5) suffice in principle
    tau = S5.perms.index((1, 0, 2, 3, 4))
    g = np.random.default_rng(5).integers(0, 120, (500, 16))
    par = (S5.char_el[1].real[g] < 0).astype(int)
    pp = np.cumsum(par, 1) % 2
    prev = np.concatenate([np.zeros((500, 1), int), pp[:, :-1]], 1)
    t_or_e = lambda bits: np.where(bits == 1, tau, S5.e)
    h = S5.mul[S5.mul[t_or_e(prev), g], t_or_e(pp)]
    lhs = groups.prefix_products(S5, g)
    rhs = S5.mul[groups.prefix_products(S5, h), t_or_e(pp)]
    check("S5 = A5 x| Z2: every h_s is even and g_1...g_t = h_1...h_t tau^p_t",
          (S5.char_el[1].real[h] > 0).all() and (lhs == rhs).all())

    # causal holonomy sectors and the prefix product against explicit sums (float64)
    B, T, H, d, K = 2, 6, 2, 3, 4
    M = rng.normal(size=(B, T, H, d, d))
    U = rng.normal(size=(B, T, H, d, d))
    F = [np.asarray(f) for f in pb.holonomy_causal(jnp.asarray(M), jnp.asarray(U), K, 1)]
    worst = 0.0
    for m in range(K):
        ref = np.zeros((B, T, H, d, d))
        for i in range(T):
            for S in itertools.combinations(range(i), m):
                P = np.broadcast_to(np.eye(d), (B, H, d, d)).copy()
                for t in S + (i,):
                    P = P @ M[:, t]
                ref[:, i] += P
        worst = max(worst, float(np.abs(F[m] - ref).max()))
    pref = np.zeros((B, T, H, d, d))
    P = np.broadcast_to(np.eye(d), (B, H, d, d)).copy()
    for i in range(T):
        P = P @ U[:, i]
        pref[:, i] = P
    worst = max(worst, float(np.abs(F[K] - pref).max()))
    check("causal holonomy sectors = explicit sums over subsets ending at i; prefix = U_0 ... U_i (float64)", worst < 1e-10, f"max error {worst:.1e}")
    th = rng.uniform(0, 2 * np.pi, (B, T, H))
    gt = rng.uniform(0.2, 1, (B, T, H))
    rot = np.stack([np.stack([np.cos(th), -np.sin(th)], -1), np.stack([np.sin(th), np.cos(th)], -1)], -2)
    F2 = pb.holonomy_causal(jnp.asarray(rot * gt[..., None, None]), jnp.asarray(rot), K, 1)
    phi = gt * np.exp(1j * th)
    worst = 0.0
    for m in range(K):
        for i in range(T):
            e = sum(np.prod(phi[:, list(S)], 1) for S in itertools.combinations(range(i), m)) if m else 1
            z = phi[:, i] * e
            worst = max(worst, float(np.abs(np.asarray(F2[m])[:, i, :, 0, 0] - z.real).max()))
    z = np.exp(1j * np.cumsum(th, 1))
    worst = max(worst, float(np.abs(np.asarray(F2[K])[..., 1, 0] - z.imag).max()))
    check("commuting 2 x 2 rotations: causal sectors are phi_i e_m(phi_0..phi_{i-1}), the prefix a phase", worst < 1e-10, f"max error {worst:.1e}")

    # DeltaProduct scan against an explicit loop, and S_t = S_0 A_1 ... A_t for the transitions
    B, T, H, nh, dk = 2, 7, 2, 3, 4
    q = rng.normal(size=(B, T, H, dk))
    k = rng.normal(size=(B, T, H, nh, dk)); k /= np.linalg.norm(k, axis=-1, keepdims=True)
    v = rng.normal(size=(B, T, H, nh, dk))
    be = rng.uniform(0, 2, (B, T, H, nh))
    o = np.asarray(pb.deltaprod_scan(*(jnp.asarray(t) for t in (q, k, v, be))))
    S = np.zeros((B, H, dk, dk)); ref = np.zeros_like(q)
    Ssum = np.zeros((B, H, dk, dk))
    A = [np.zeros((B, H, dk, dk)) for _ in range(T)]
    W = [np.zeros((B, H, dk, dk)) for _ in range(T)]
    for t in range(T):
        A[t] = np.broadcast_to(np.eye(dk), (B, H, dk, dk)).copy()
        for j in range(nh):
            kk = k[:, t, :, j]
            S = S + be[:, t, :, j, None, None] * np.einsum("bhv,bhk->bhvk", v[:, t, :, j] - np.einsum("bhvk,bhk->bhv", S, kk), kk)
            Hj = np.eye(dk) - be[:, t, :, j, None, None] * np.einsum("bhi,bhj->bhij", kk, kk)
            A[t] = A[t] @ Hj
            W[t] = W[t] @ Hj + be[:, t, :, j, None, None] * np.einsum("bhv,bhk->bhvk", v[:, t, :, j], kk)
        ref[:, t] = np.einsum("bhvk,bhk->bhv", S, q[:, t])
        Ssum = Ssum @ A[t] + W[t]
    check("DeltaProduct scan = explicit delta-rule loop; S_t = S_(t-1) A_t + W_t, A_t = prod_j (I - beta k k^T)",
          np.abs(o - ref).max() < 1e-10 and np.abs(Ssum - S).max() < 1e-10, f"max error {np.abs(o - ref).max():.1e}")

    # --hh: the transitions are products of generalised Householders, U (I - beta k k^T) applied in order
    cfg = argparse.Namespace(gdim=4, heads=3, hh=3, phase=2.0, beta0=0.0)
    a = {"s": {"w": jnp.asarray(rng.normal(size=(8, 3 * 3 * 4))), "b": jnp.zeros(36)},
         "hb": {"w": jnp.asarray(rng.normal(size=(8, 9))), "b": jnp.zeros(9)}}
    xx = jnp.asarray(rng.normal(size=(5, 8)))
    Uh = np.asarray(pb.holo_mats(cfg, a, xx))
    kk = np.array(xx @ a["s"]["w"]).reshape(5, 3, 3, 4); kk /= np.sqrt((kk ** 2).sum(-1, keepdims=True) + 1e-6)
    bb = 2 / (1 + np.exp(-np.asarray(xx @ a["hb"]["w"]))).reshape(5, 3, 3)
    ref = np.zeros((5, 3, 4, 4))
    for i in range(5):
        for h in range(3):
            ref[i, h] = np.linalg.multi_dot([np.eye(4)] + [np.eye(4) - bb[i, h, j] * np.outer(kk[i, h, j], kk[i, h, j]) for j in range(3)] + [np.eye(4)])
    check("--hh 3: holo_mats = H_1 H_2 H_3, H_j = I - beta_j k_j k_j^T", np.abs(Uh - ref).max() < 1e-10, f"max error {np.abs(Uh - ref).max():.1e}")

    # forward and backward on the word tasks
    for task, extra in (("wp_s5_16", dict(model="holo", gdim=5, heads=8, order=3, causal=1, prefix=1, pos=0)),
                        ("wp_a5_16", dict(model="holo", gdim=3, heads=8, order=0, causal=1, prefix=1, pos=0)),
                        ("wp_s5_16", dict(model="holo", gdim=5, heads=8, order=0, causal=1, prefix=1, pos=0, hh=4)),
                        ("ws_a5_16", dict(model="holo", gdim=2, heads=8, order=3, causal=1, prefix=1, pos=0)),
                        ("wp_s5_16", dict(model="deltaprod", nh=4, pos=0)),
                        ("wp_a5_16", dict(model="sa", causal=1, pos=1))):
        cfg = argparse.Namespace(task=task, layers=2, heads=4, phase=2.0, fnorm=1, ffn=1, repeat=0, recur=1, rawphase=0,
                                 readout="shared", rank=32, order=3, wide=4, vdim=8, plen=3, modes=16, nocubic=0, dh=0,
                                 embed="table", d=64, causal=0, prefix=0, nh=2, gdim=3, hh=0, beta0=0.0)
        for kk_, vv in extra.items():
            setattr(cfg, kk_, vv)
        gen, vocabs, C, _ = pb.TASKS[task]
        t, y, mk = gen(np.random.default_rng(0), 4)
        p = pb.init(jax.random.PRNGKey(0), cfg, vocabs, C, 65)

        def loss(p):
            lg = pb.forward(cfg, p, jnp.asarray(t))
            return (jax.nn.logsumexp(lg, -1) - jnp.take_along_axis(lg, jnp.asarray(y)[..., None], -1)[..., 0]).mean()

        l, gr = jax.value_and_grad(loss)(p)
        finite = bool(jnp.isfinite(l)) and all(bool(jnp.isfinite(x).all()) for x in jax.tree_util.tree_leaves(gr))
        # causality: changing the last token must not change any earlier logit
        t2 = t.copy(); t2[:, -1] = (t2[:, -1] + 1) % C
        l1, l2 = np.asarray(pb.forward(cfg, p, jnp.asarray(t))), np.asarray(pb.forward(cfg, p, jnp.asarray(t2)))
        causal = np.abs(l1[:, :-1] - l2[:, :-1]).max() < 1e-9 and np.abs(l1[:, -1] - l2[:, -1]).max() > 1e-6
        check(f"{task} / {extra['model']} (2 layers): forward and backward finite, causal", finite and causal, f"loss {float(l):.3f}")


if __name__ == "__main__":
    main()
