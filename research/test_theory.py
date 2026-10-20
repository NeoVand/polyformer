"""Constructive checks for THEORY.md; no training or fitted group representations.

uv run --no-project --with "jax[cpu]" --with optax --with numpy python research/test_theory.py
Add --exact-ceiling to enumerate all 12**6 A4 sequences (integer arithmetic).
Add --output research/results/theory_checks.json to save the audit.
"""

import argparse
import itertools
import json
import math
import pathlib
import time
from fractions import Fraction

import jax

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np

import groups
import polybench as pb


def standard_representation(m):
    """Permutation action restricted to sum-zero vectors, in an orthonormal basis."""
    perms, _, _, _ = groups._alternating(m)
    # Helmert columns, with fixed orientation; no eigenspace fitting.
    basis = np.zeros((m, m - 1))
    for j in range(m - 1):
        basis[:j + 1, j] = 1 / math.sqrt((j + 1) * (j + 2))
        basis[j + 1, j] = -(j + 1) / math.sqrt((j + 1) * (j + 2))
    P = np.zeros((len(perms), m, m))
    for i, p in enumerate(perms):
        P[i, list(p), np.arange(m)] = 1
    return np.einsum("ia,gij,jb->gab", basis, P, basis)


def faithful_rotations(name):
    """A4 tetrahedral 3; A5 self-dual exterior square of its standard 4."""
    if name == "A4":
        return standard_representation(4)
    if name != "A5":
        raise ValueError(name)
    R = standard_representation(5)
    pairs = list(itertools.combinations(range(4), 2))
    wedge = np.empty((60, 6, 6))
    for a, (i, j) in enumerate(pairs):
        for b, (k, l) in enumerate(pairs):
            wedge[:, a, b] = R[:, i, k] * R[:, j, l] - R[:, i, l] * R[:, j, k]
    # Orthonormal self-dual basis: (01+23), (02-13), (03+12), divided by sqrt(2).
    B = np.zeros((6, 3))
    B[[0, 5], 0] = 1 / math.sqrt(2)
    B[[1, 4], 1] = [1 / math.sqrt(2), -1 / math.sqrt(2)]
    B[[2, 3], 2] = 1 / math.sqrt(2)
    return np.einsum("ia,gij,jb->gab", B, wedge, B)


def check_representation(G, R):
    prod_error = np.max(np.abs(R[:, None] @ R[None] - R[G.mul]))
    orth_error = np.max(np.abs(R @ R.transpose(0, 2, 1) - np.eye(3)))
    traces = np.trace(R, axis1=-2, axis2=-1)
    gap = float(3 - np.max(traces[np.arange(G.n) != G.e]))
    multiplicities = traces @ G.char_el.conj().T / G.n
    assert prod_error < 1e-12 and orth_error < 1e-12
    assert np.max(np.abs(np.linalg.det(R) - 1)) < 1e-12 and gap > 0
    assert np.isclose(np.sum(np.abs(multiplicities) ** 2), 1)
    return dict(homomorphism_max_error=float(prod_error), orthogonality_max_error=float(orth_error),
                identity_trace_gap=gap, irrep_multiplicities=multiplicities.real.round(12).tolist())


def position_heads(G, R, seq, k, low=1e-7, high=0.75):
    """One head per position subset, with finite strictly positive sigmoid gates."""
    B, n = seq.shape
    subsets = list(itertools.combinations(range(n), k))
    gates = np.full((n, len(subsets)), low)
    for h, S in enumerate(subsets):
        gates[list(S), h] = high
    M = R[seq, None] * gates[None, :, :, None, None]
    F = np.asarray(pb.holonomy_sectors(jnp.asarray(M), k)[k - 1])
    trace = np.trace(F, axis1=-2, axis2=-1) / high ** k
    gap = 3 - np.max(np.trace(R, axis1=-2, axis2=-1)[np.arange(G.n) != G.e])
    member = gates == high  # the positional readout ignores heads not containing its query
    pred = np.any((trace > 3 - gap / 2) & member[None], axis=-1)
    truth = groups.match_labels(G, seq, k)
    assert np.array_equal(pred, truth)
    # A direct conservative contamination bound used in the proof.
    bound = 3 * (math.comb(n - 1, k - 1) - 1) * low / high
    assert bound < gap / 2
    return dict(n=n, k=k, sequences=B, heads=len(subsets), errors=int(np.sum(pred != truth)),
                gate_low=low, gate_high=high, contamination_bound=bound)


def quadratic_gates(m):
    """Interior finite-difference grid: baseline, singles, doubles, distinct pairs."""
    b, delta = 0.25, 0.25
    rows = [np.full(m, b)]
    singles, doubles, pairs = {}, {}, {}
    for a in range(m):
        t = np.full(m, b)
        t[a] += delta
        singles[a] = len(rows)
        rows.append(t)
        t = np.full(m, b)
        t[a] += 2 * delta
        doubles[a] = len(rows)
        rows.append(t)
    for a, c in itertools.combinations(range(m), 2):
        t = np.full(m, b)
        t[[a, c]] += delta
        pairs[a, c] = len(rows)
        rows.append(t)
    return np.array(rows), singles, doubles, pairs, delta


def native_match3(G, R, seq):
    """Token-only positive gates, actual holonomy kernel, no positional features.

    Each gate row has a faithful-rotation head and an identity-rotation head.
    Quadratic coefficient recovery returns identity-subset COUNTS, not an
    assumption that the trace of a sum detects an identity summand.
    """
    gates, singles, doubles, pairs, delta = quadratic_gates(G.n)
    H, d = len(gates), R.shape[-1]
    B, n = seq.shape
    pred = np.zeros_like(seq, dtype=bool)
    normalized_pred = np.zeros_like(seq, dtype=bool)
    max_count_error = 0.
    norm_inverse_error = 0.
    trace_table = np.trace(R, axis1=-2, axis2=-1)
    # One sequence at a time bounds memory; all heads are built and evaluated.
    for batch in range(B):
        s = seq[batch]
        w = gates[:, s].T
        matrices = np.concatenate([
            R[s, None] * w[:, :, None, None],
            np.eye(d)[None, None] * w[:, :, None, None],
        ], axis=1)[None]
        F = np.asarray(pb.holonomy_sectors(jnp.asarray(matrices), 3)[2])[0]
        # Verify inversion of the implemented epsilon RMS normalization on FULL features.
        x = F / math.comb(n - 1, 2)
        norm = np.sqrt(np.mean(x * x, axis=(1, 2, 3), keepdims=True) + 1e-6)
        z = x / norm
        recovered = z * np.sqrt(1e-6 / (1 - np.mean(z * z, axis=(1, 2, 3), keepdims=True)))
        norm_inverse_error = max(norm_inverse_error, float(np.max(np.abs(x - recovered))))
        # Trace divided by the own-token gate gives a homogeneous quadratic.
        Q = np.trace(F[:, :H], axis1=-2, axis2=-1) / w
        N = F[:, H:, 0, 0] / w
        Qz = np.trace(z[:, :H], axis1=-2, axis2=-1) / w
        Nz = z[:, H:, 0, 0] / w
        # Every nonzero recovered count has at least this normalized magnitude.
        count_margin = 1 / (math.comb(n - 1, 2) * math.sqrt(0.75 ** 6 / d + 1e-6))
        for a in range(G.n):
            for c in range(a, G.n):
                if a == c:
                    def coefficient(V):
                        return (V[:, doubles[a]] - 2 * V[:, singles[a]] + V[:, 0]) / (2 * delta ** 2)
                else:
                    def coefficient(V):
                        return (V[:, pairs[a, c]] - V[:, singles[a]] - V[:, singles[c]] + V[:, 0]) / delta ** 2
                tr, count = coefficient(Q), coefficient(N)
                tr_z, count_z = coefficient(Qz), coefficient(Nz)
                for i, own in enumerate(s):
                    products = [int(groups.ordered_product(G, np.array(p))) for p in
                                itertools.permutations([int(own), a, c])]
                    if G.e not in products:
                        continue
                    nonidentity = [p for p in products if p != G.e]
                    if not nonidentity:
                        hits = count[i]
                        hits_z = count_z[i]
                    else:
                        tau = trace_table[nonidentity[0]]
                        assert np.allclose(trace_table[nonidentity], tau)
                        hits = (tr[i] - tau * count[i]) / (d - tau)
                        hits_z = (tr_z[i] - tau * count_z[i]) / (d - tau)
                    # Independent integer reference for this exact root/content pair.
                    exact = 0
                    for j, l in itertools.combinations([q for q in range(n) if q != i], 2):
                        if sorted([int(s[j]), int(s[l])]) == [a, c]:
                            triple = s[sorted([i, j, l])]
                            exact += int(groups.ordered_product(G, triple) == G.e)
                    max_count_error = max(max_count_error, abs(float(hits) - exact))
                    pred[batch, i] |= hits > 0.5
                    normalized_pred[batch, i] |= hits_z > count_margin / 2
    truth = groups.match_labels(G, seq, 3)
    assert np.array_equal(pred, truth) and max_count_error < 1e-8
    assert np.array_equal(normalized_pred, truth)
    assert norm_inverse_error < 1e-8
    return dict(n=n, k=3, sequences=B, heads=2 * H, errors=int(np.sum(pred != truth)),
                max_identity_count_error=max_count_error, rms_inverse_max_error=norm_inverse_error,
                normalized_errors=int(np.sum(normalized_pred != truth)),
                gates=sorted(set(gates.ravel().tolist())))


def triple_audit(G):
    seq = np.array(list(itertools.product(range(G.n), repeat=3)))
    products = np.stack([groups.ordered_product(G, seq[:, p]) for p in itertools.permutations(range(3))], 1)
    identities = np.sum(products == G.e, axis=1)
    assert set(np.unique(identities)) <= {0, 3, 6}
    positive = groups.ordered_product(G, seq) == G.e
    commuting = G.mul[seq[:, 0], seq[:, 1]] == G.mul[seq[:, 1], seq[:, 0]]
    assert np.array_equal((identities == 6)[positive], commuting[positive])
    # Balanced Bayes prediction for n=3: some ordering succeeds.
    pred = identities > 0
    ceiling = .5 * (pred[positive].mean() + (~pred[~positive]).mean())
    cp = Fraction(len(G.classes), G.n)
    exact = 1 - (1 - cp) / (2 * (G.n - 1))
    assert abs(ceiling - float(exact)) < 1e-12
    return dict(n=3, sequences=len(seq), commuting_probability=str(cp),
                exact_ceiling=str(exact), ceiling=float(exact),
                ordering_identity_counts={str(v): int(np.sum(identities == v)) for v in (0, 3, 6)})


def softmax_certificates(rng):
    """Verify the two constructive softmax readouts, without optimization."""
    G = groups.cyclic(12)
    seq = rng.integers(G.n, size=(64, 8))
    values = G.char_el[:, seq].transpose(1, 2, 0)
    # The uniform attention output is the mean of all character-valued tokens.
    average = values.mean(axis=1)
    checks = []
    for k in (3, 4, 5):
        e = [np.ones_like(values)]
        powers = [8 * average[:, (r * np.arange(G.n)) % G.n][:, None] - values ** r
                  for r in range(1, k)]
        for degree in range(1, k):
            e.append(sum((-1) ** (r - 1) * e[degree - r] * powers[r - 1]
                         for r in range(1, degree + 1)) / degree)
        counts = np.mean(values * e[k - 1], axis=-1)
        truth = groups.match_labels(G, seq, k)
        assert np.max(np.abs(counts.imag)) < 1e-10
        assert np.array_equal(counts.real > .5, truth)
        checks.append(dict(group="Z12", n=8, k=k, sequences=64, errors=0))
    n, vocab = 7, 12
    words = rng.integers(vocab, size=(64, n))
    onehot = np.eye(vocab)[words]
    weights = (np.ones((n, n)) + (math.exp(1) - 1) * np.eye(n)) / (math.exp(1) + n - 1)
    attended = np.einsum("ht,btv->bhv", weights, onehot)
    recovered = np.einsum("th,bhv->btv", np.linalg.inv(weights), attended)
    error = float(np.max(np.abs(recovered - onehot)))
    assert error < 1e-12
    return dict(uniform_character_readout=checks, positional_sequence_reconstruction_error=error)


def nonfaithful_certificate():
    """A5 x Z3: 3D projection is not faithful but reflects commutativity."""
    A = groups.get("A5")
    R = faithful_rotations("A5")
    elements = np.arange(180)
    a, z = elements // 3, elements % 3
    mul = 3 * A.mul[a[:, None], a[None, :]] + (z[:, None] + z[None, :]) % 3
    projected = R[a]
    images_commute = np.max(np.abs(projected[:, None] @ projected[None] -
                                  projected[None] @ projected[:, None]), axis=(-2, -1)) < 1e-10
    assert np.array_equal(images_commute, mul == mul.T)
    kernel = np.flatnonzero(np.max(np.abs(projected - np.eye(3)), axis=(-2, -1)) < 1e-10)
    assert len(kernel) == 3
    return dict(group="A5 x Z3", dimension=3, kernel_size=len(kernel),
                all_pair_commutativity_reflection=True, checked_pairs=180 ** 2)


def exact_order_blind_ceiling(name="A4", n=6, k=3, chunk=32768):
    """Exact class counts for (own element, multiset of all other elements).

    Sorted multiset (a_0,...,a_{r-1}) is ranked by the colex combinadic
    sum_j C(a_j+j,j+1), a bijection onto 0..C(|G|+r-1,r)-1.
    Counts use all sequences and all marked positions; Bayes compares
    pos[o]/N_pos with neg[o]/N_neg. Final arithmetic is exact rational.
    """
    G = groups.get(name)
    r = n - 1
    states = math.comb(G.n + r - 1, r)
    counts = np.zeros((2, G.n * states), np.int64)
    choose = np.array([[math.comb(a + j, j + 1) for j in range(r)] for a in range(G.n)])
    powers = G.n ** np.arange(n, dtype=np.int64)
    start = time.monotonic()
    for lo in range(0, G.n ** n, chunk):
        ids = np.arange(lo, min(lo + chunk, G.n ** n), dtype=np.int64)
        seq = (ids[:, None] // powers[None]) % G.n
        y = groups.match_labels(G, seq, k)
        for i in range(n):
            other = np.sort(np.delete(seq, i, axis=1), axis=1)
            rank = choose[other, np.arange(r)].sum(axis=1)
            obs = seq[:, i] * states + rank
            for label in (0, 1):
                counts[label] += np.bincount(obs[y[:, i] == label], minlength=G.n * states)
    neg, pos = counts
    N0, N1 = int(neg.sum()), int(pos.sum())
    # Python ints prevent overflow if this routine is reused on larger examples.
    numerator = sum(max(int(p) * N0, int(q) * N1) for p, q in zip(pos, neg))
    ceiling = Fraction(numerator, 2 * N0 * N1)
    return dict(group=name, n=n, k=k, sequences=G.n ** n, marked_examples=N0 + N1,
                positive_examples=N1, negative_examples=N0, observation_classes=int((pos + neg > 0).sum()),
                exact_ceiling=str(ceiling), ceiling=float(ceiling), positive_rate=N1 / (N0 + N1),
                seconds=time.monotonic() - start)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exact-ceiling", action="store_true")
    ap.add_argument("--output")
    ap.add_argument("--sequences", type=int, default=12)
    args = ap.parse_args()
    rng = np.random.default_rng(20261020)
    result = {"seed": 20261020, "checks": {}}
    for name, n in (("A4", 6), ("A5", 11)):
        G = groups.get(name)
        R = faithful_rotations(name)
        data = {"representation": check_representation(G, R), "triples": triple_audit(G)}
        seq = rng.integers(G.n, size=(args.sequences, n))
        # Include duplicate-heavy and all-identity inputs; gates cannot select occurrences.
        seq[0] = G.e
        if len(seq) > 1:
            seq[1] = np.resize(np.array([G.e, 1, G.inv[1]]), n)
        data["native_token_gates"] = native_match3(G, R, seq)
        data["position_gates"] = []
        for k in (3, 4, 5):
            short = rng.integers(G.n, size=(64, 7))
            short[0] = G.e
            data["position_gates"].append(position_heads(G, R, short, k))
        result["checks"][name] = data
        print(json.dumps({name: data}), flush=True)
    if args.exact_ceiling:
        result["exact_A4_ceiling"] = exact_order_blind_ceiling()
        print(json.dumps(result["exact_A4_ceiling"]), flush=True)
    result["softmax"] = softmax_certificates(rng)
    result["nonfaithful"] = nonfaithful_certificate()
    result["all_checks_passed"] = True
    if args.output:
        path = pathlib.Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2) + "\n")
    print("All constructive, character, triple, and ceiling checks passed.")


if __name__ == "__main__":
    main()
