"""
Finite groups for GROUPS.md: cyclic Z_n and the alternating groups A_4 and A_5, with multiplication
tables, conjugacy classes and character tables, the ordered Match-k task over a group, and the
analysis that reads which irreducible representations a trained holonomy layer holds.

    python research/test_groups.py      # group axioms, character orthogonality, task labels, the layer

Conventions: elements are indices 0..|G|-1, mul[a, b] is the index of a*b, and a sequence's product is
taken in position order, g_1 g_2 ... g_k. Permutations compose as (a*b)(x) = a(b(x)).
"""

import itertools
import math

import numpy as np


class Group:
    def __init__(self, name, mul, e, classes, chars, dims):
        self.name, self.mul, self.e = name, mul, e
        self.n = mul.shape[0]
        self.inv = np.argmax(mul == e, axis=1)
        self.classes = classes          # list of index arrays
        self.chars = chars              # [irreps, classes] complex, the character table
        self.dims = np.asarray(dims)    # irrep dimensions, trivial first
        cls = np.zeros(self.n, int)
        for c, members in enumerate(classes):
            cls[members] = c
        self.cls = cls                  # class of every element
        self.char_el = chars[:, cls]    # [irreps, elements]

    @property
    def abelian(self):
        return bool((self.mul == self.mul.T).all())


def cyclic(n):
    a = np.arange(n)
    mul = (a[:, None] + a[None, :]) % n
    classes = [np.array([k]) for k in range(n)]
    chars = np.exp(2j * np.pi * np.outer(a, a) / n)  # chi_j(k) = exp(2 pi i j k / n)
    return Group(f"Z{n}", mul, 0, classes, chars, [1] * n)


def _alternating(m):
    perms = [p for p in itertools.permutations(range(m)) if _parity(p) == 0]
    index = {p: i for i, p in enumerate(perms)}
    mul = np.array([[index[tuple(a[b[x]] for x in range(m))] for b in perms] for a in perms])
    e = index[tuple(range(m))]
    return perms, index, mul, e


def _parity(p):
    seen, par = set(), 0
    for s in range(len(p)):
        if s in seen:
            continue
        L, x = 0, s
        while x not in seen:
            seen.add(x); x = p[x]; L += 1
        par ^= (L - 1) & 1
    return par


def _classes(mul, inv):
    n = mul.shape[0]
    left, out = set(range(n)), []
    while left:
        g = min(left)
        members = sorted({int(mul[mul[h, g], inv[h]]) for h in range(n)})
        out.append(np.array(members))
        left -= set(members)
    return out


def _cycle_type(p):
    seen, t = set(), []
    for s in range(len(p)):
        if s in seen:
            continue
        L, x = 0, s
        while x not in seen:
            seen.add(x); x = p[x]; L += 1
        t.append(L)
    return tuple(sorted(t, reverse=True))


def alternating4():
    perms, index, mul, e = _alternating(4)
    inv = np.argmax(mul == e, axis=1)
    cl = _classes(mul, inv)
    by_type = {}
    for c in cl:
        by_type.setdefault(_cycle_type(perms[c[0]]), []).append(c)
    three = by_type[(3, 1)]                        # the 3-cycles split into two classes of 4
    c = three[0][0]
    a, b = (three[0], three[1]) if mul[c, c] in three[1] else (three[1], three[0])
    classes = [by_type[(1, 1, 1, 1)][0], by_type[(2, 2)][0], a, b]   # e, (12)(34), c, c^2
    w = np.exp(2j * np.pi / 3)
    chars = np.array([[1, 1, 1, 1], [1, 1, w, w * w], [1, 1, w * w, w], [3, -1, 0, 0]], complex)
    return Group("A4", mul, e, classes, chars, [1, 1, 1, 3])


def alternating5():
    perms, index, mul, e = _alternating(5)
    inv = np.argmax(mul == e, axis=1)
    cl = _classes(mul, inv)
    by_type = {}
    for c in cl:
        by_type.setdefault(_cycle_type(perms[c[0]]), []).append(c)
    five = by_type[(5,)]                            # the 5-cycles split into two classes of 12
    c = five[0][0]
    a, b = (five[0], five[1]) if mul[c, c] in five[1] else (five[1], five[0])
    classes = [by_type[(1, 1, 1, 1, 1)][0], by_type[(2, 2, 1)][0], by_type[(3, 1, 1)][0], a, b]
    phi = (1 + math.sqrt(5)) / 2
    chars = np.array([[1, 1, 1, 1, 1],
                      [3, -1, 0, phi, 1 - phi],
                      [3, -1, 0, 1 - phi, phi],
                      [4, 0, 1, -1, -1],
                      [5, 1, -1, 0, 0]], complex)
    return Group("A5", mul, e, classes, chars, [1, 3, 3, 4, 5])


GROUPS = {"Z12": lambda: cyclic(12), "A4": alternating4, "Z60": lambda: cyclic(60), "A5": alternating5}
_cache = {}


def get(name):
    if name not in _cache:
        _cache[name] = GROUPS[name]()
    return _cache[name]


def ordered_product(G, g):
    """g: [..., k] element indices -> [...] index of g_1 g_2 ... g_k."""
    p = g[..., 0]
    for t in range(1, g.shape[-1]):
        p = G.mul[p, g[..., t]]
    return p


def match_labels(G, g, k):
    """g: [B, n] -> [B, n] bool: position i lies in some k positions i_1 < ... < i_k whose ordered product is e."""
    B, n = g.shape
    y = np.zeros((B, n), bool)
    for comb in itertools.combinations(range(n), k):
        hit = ordered_product(G, g[:, list(comb)]) == G.e
        if hit.any():
            y[:, list(comb)] |= hit[:, None]
    return y


def task_gmatch(rng, B, name, n, k=3):
    """Ordered Match-k over a group: a BOS token (index |G|), then n uniform elements; every element is
    scored on whether it completes some position-ordered k-product equal to the identity."""
    G = get(name)
    g = rng.integers(0, G.n, size=(B, n))
    y = match_labels(G, g, k).astype(np.int32)
    tok = np.concatenate([np.full((B, 1), G.n), g], 1)[..., None]
    tgt = np.concatenate([np.zeros((B, 1), np.int32), y], 1)
    msk = np.concatenate([np.zeros((B, 1)), np.ones((B, n))], 1)
    return tok, tgt, msk


def order_blind_ceiling(name, n, k=3, samples=4000, perms=64, seed=0):
    """
    The best balanced accuracy of any predictor that sees a position's element and the multiset of the others
    but not the order (Newton attention, or holonomy attention with commuting rotations). For every position
    it estimates p = P(label 1 | own element, multiset) by relabelling random reorderings of the sequence, then
    scores the best threshold on p against the true labels. Monte Carlo, so slightly optimistic.
    """
    G = get(name)
    rng = np.random.default_rng(seed)
    g = rng.integers(0, G.n, size=(samples, n))
    y = match_labels(G, g, k)
    p = np.zeros((samples, n))
    for _ in range(perms):
        P = np.argsort(rng.random((samples, n)), 1)              # P[s, q] = original position now at q
        yh = match_labels(G, np.take_along_axis(g, P, 1), k)
        np.add.at(p, (np.arange(samples)[:, None], P), yh)
    p /= perms
    best = 0.0
    for t in np.unique(np.round(p, 4)):
        pred = p >= t
        bal = 0.5 * (pred[y].mean() + (~pred[~y]).mean())
        best = max(best, bal)
    return float(best)


def plancherel(G, captured):
    """Share of the nontrivial Plancherel measure held by the irreps in `captured` (indices, trivial = 0)."""
    d = G.dims
    return float(sum(d[i] ** 2 for i in set(captured) if i != 0) / (G.n - 1))


def reachable(G, d):
    """Nontrivial irreps a head of real dimension d can hold: real irreps of dimension <= d, and complex
    one-dimensional irreps in conjugate pairs (a 2 x 2 rotation) when d >= 2."""
    out = []
    for i in range(1, len(G.dims)):
        real = np.allclose(G.chars[i].imag, 0)
        need = G.dims[i] if real else 2 * G.dims[i]
        if need <= d:
            out.append(i)
    return out


def rep_content(G, U, tol=0.5):
    """
    U: [H, |G|, d, d], the matrices one layer assigns to every group element (one per head).
    Returns per head the homomorphism error (mean ||U_a U_b - U_ab||_F / ||U_ab||_F over all pairs) and the
    irrep multiplicities <chi, chi_rho> of its character chi(g) = tr U_g, and the set of nontrivial irreps
    held with multiplicity >= 1/2 by some head whose homomorphism error is below tol.
    """
    U = np.asarray(U, np.float64)
    H, n, d, _ = U.shape
    prod = np.einsum("hacd,hbde->habce", U, U)            # [H, a, b, d, d]
    want = U[:, G.mul]                                    # [H, a, b, d, d]
    err = np.linalg.norm(prod - want, axis=(-2, -1)) / np.maximum(np.linalg.norm(want, axis=(-2, -1)), 1e-9)
    herr = err.mean((1, 2))
    chi = np.trace(U, axis1=-2, axis2=-1)                 # [H, |G|]
    mult = (chi @ G.char_el.conj().T).real / n            # [H, irreps]
    good = herr < tol
    held = sorted({int(i) for h in range(H) if good[h] for i in np.nonzero(mult[h] >= 0.5)[0] if i != 0})
    best = np.where(good[:, None], mult, -np.inf).max(0) if good.any() else np.full(mult.shape[1], np.nan)
    top = np.argsort(herr)[:4]
    return {"hom_err_q": [round(float(q), 3) for q in np.quantile(herr, [0.0, 0.1, 0.5, 0.9])],
            "good_heads": int(good.sum()), "of": H, "held": held, "mass": round(plancherel(G, held), 3),
            "best_mult": [None if not np.isfinite(b) else round(float(b), 2) for b in best],
            "top": [{"hom_err": round(float(herr[h]), 3), "mult": np.round(mult[h], 2).tolist()} for h in top]}
