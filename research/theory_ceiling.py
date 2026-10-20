"""Exact order-blind Bayes ceilings for ordered Match-3.

The marked token can be cyclically rotated to the front. For its value a,
the label is positive iff two other tokens occur in the order x, f_a(x),
where f_a(x) = x^{-1} a^{-1}. This is a permutation of the group alphabet.
For a fixed multiset, absence of a hit imposes a reverse block order on
each supported path in the cycles of f_a. Its probability is zero when
a supported cycle occurs, and otherwise 1/D, where D is a product of
multinomial coefficients, one per path.

We enumerate local histograms inside each cycle and combine their exact
integer word counts by interleaving. This computes the entire posterior
distribution, without enumerating |G|**n words or sampling reorderings.

uv run --no-project --with numpy python research/theory_ceiling.py \
    --verify-a4 --output research/results/theory_ceiling.json
"""

import argparse
import collections
import itertools
import json
import math
import pathlib
import time
from fractions import Fraction
from functools import lru_cache

import numpy as np

import groups


def permutation_cycles(G, own):
    """Cycles of x -> x^{-1} own^{-1}, including fixed points."""
    successor = G.mul[G.inv, G.inv[own]]
    left = set(range(G.n))
    cycles = []
    while left:
        x = min(left)
        cycle = []
        while x in left:
            left.remove(x)
            cycle.append(x)
            x = int(successor[x])
        cycles.append(cycle)
    return cycles


def cycle_denominator(counts):
    """Return D with P(no hit | counts on this cycle)=1/D; 0 means impossible."""
    length = len(counts)
    if length == 1:
        return 0 if counts[0] >= 2 else 1
    if all(counts):
        return 0
    # A missing label cuts the directed cycle into disjoint paths.
    start = counts.index(0)
    denominator = 1
    run_size = 0
    run_factorials = 1
    for offset in range(1, length + 1):
        count = counts[(start + offset) % length]
        if count:
            run_size += count
            run_factorials *= math.factorial(count)
        else:
            denominator *= math.factorial(run_size) // run_factorials
            run_size = 0
            run_factorials = 1
    return denominator


def posterior(G, own, other):
    """Exact Fraction P(positive | own token, multiset of other tokens)."""
    counts = collections.Counter(map(int, other))
    denominator = 1
    for cycle in permutation_cycles(G, int(own)):
        part = cycle_denominator([counts[x] for x in cycle])
        if part == 0:
            return Fraction(1)
        denominator *= part
    return 1 - Fraction(1, denominator)


def compositions(total, length):
    """All nonnegative integer count vectors with the requested total."""
    if length == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, length - 1):
            yield (first,) + rest


@lru_cache(maxsize=None)
def cycle_word_distributions(length, max_tokens):
    """For each t, count all length-t words by their multiset's denominator D."""
    result = []
    for total in range(max_tokens + 1):
        distribution = collections.defaultdict(int)
        for counts in compositions(total, length):
            denominator = cycle_denominator(list(counts))
            words = math.factorial(total) // math.prod(math.factorial(c) for c in counts)
            distribution[denominator] += words
        assert sum(distribution.values()) == length ** total
        result.append(dict(distribution))
    return tuple(result)


@lru_cache(maxsize=None)
def combine_cycles(cycle_lengths, max_tokens):
    """Exact word distribution after combining disjoint alphabets by interleaving."""
    result = [{1: 1}] + [{} for _ in range(max_tokens)]
    alphabet_size = 0
    for length in cycle_lengths:
        local = cycle_word_distributions(length, max_tokens)
        combined = [collections.defaultdict(int) for _ in range(max_tokens + 1)]
        for old_total, old in enumerate(result):
            for extra in range(max_tokens + 1 - old_total):
                interleavings = math.comb(old_total + extra, extra)
                target = combined[old_total + extra]
                for old_d, old_words in old.items():
                    for local_d, local_words in local[extra].items():
                        target[old_d * local_d] += old_words * local_words * interleavings
        alphabet_size += length
        result = [dict(row) for row in combined]
        for total, row in enumerate(result):
            assert sum(row.values()) == alphabet_size ** total
    return result[max_tokens]


def exact_ceiling(name, n):
    """Compute the exact Bayes ceiling, including the entire posterior distribution."""
    start = time.monotonic()
    G = groups.get(name)
    types = collections.Counter(
        tuple(sorted(map(len, permutation_cycles(G, own)))) for own in range(G.n)
    )
    distribution = collections.defaultdict(int)
    for lengths, multiplicity in types.items():
        local = combine_cycles(lengths, n - 1)
        for denominator, words in local.items():
            distribution[denominator] += multiplicity * words
    total = G.n ** n
    assert sum(distribution.values()) == total
    positives = {}
    negatives = {}
    for denominator, words in distribution.items():
        assert denominator == 0 or words % denominator == 0
        negatives[denominator] = 0 if denominator == 0 else words // denominator
        positives[denominator] = words - negatives[denominator]
    N1 = sum(positives.values())
    N0 = sum(negatives.values())
    numerator = sum(
        max(positives[d] * N0, negatives[d] * N1) for d in distribution
    )
    ceiling = Fraction(numerator, 2 * N0 * N1)
    return {
        "group": name,
        "n": n,
        "k": 3,
        "method": "Exact integer cycle-histogram dynamic programming; no Monte Carlo.",
        "rooted_cyclic_words": str(total),
        "positive_words": str(N1),
        "negative_words": str(N0),
        "positive_rate_exact": str(Fraction(N1, total)),
        "positive_rate": N1 / total,
        "exact_ceiling": str(ceiling),
        "ceiling": float(ceiling),
        "posterior_values": len(distribution),
        "cycle_types": [
            {"lengths": list(lengths), "own_elements": multiplicity}
            for lengths, multiplicity in types.items()
        ],
        "denominator_word_counts": {
            str(d): str(count) for d, count in sorted(distribution.items())
        },
        "seconds": time.monotonic() - start,
    }


def verify_exhaustive_a4(n=6, chunk=32768):
    """Independently enumerate every word and root, checking every posterior."""
    G = groups.get("A4")
    m, r = G.n, n - 1
    states = math.comb(m + r - 1, r)
    choose = np.array([[math.comb(a + j, j + 1) for j in range(r)] for a in range(m)])
    counts = np.zeros((2, m * states), dtype=np.int64)
    powers = m ** np.arange(n, dtype=np.int64)
    for lo in range(0, m ** n, chunk):
        ids = np.arange(lo, min(lo + chunk, m ** n))
        seq = (ids[:, None] // powers) % m
        labels = groups.match_labels(G, seq, 3)
        for root in range(n):
            other = np.sort(np.delete(seq, root, axis=1), axis=1)
            rank = choose[other, np.arange(r)].sum(axis=1)
            state = seq[:, root] * states + rank
            for label in (0, 1):
                counts[label] += np.bincount(
                    state[labels[:, root] == label], minlength=m * states
                )
    checked = 0
    empirical_distribution = collections.defaultdict(int)
    for other in itertools.combinations_with_replacement(range(m), r):
        rank = sum(math.comb(a + j, j + 1) for j, a in enumerate(other))
        for own in range(m):
            state = own * states + rank
            negative, positive = map(int, counts[:, state])
            expected = Fraction(positive, positive + negative)
            actual = posterior(G, own, other)
            assert actual == expected, (own, other, actual, expected)
            denominator = 0 if actual == 1 else (1 - actual).denominator
            empirical_distribution[denominator] += positive + negative
            checked += 1
    exact = exact_ceiling("A4", n)
    assert {
        str(d): str(count // n) for d, count in empirical_distribution.items()
    } == exact["denominator_word_counts"]
    return {
        "all_posteriors_match": True,
        "all_posterior_masses_match": True,
        "observation_states": checked,
        "enumerated_sequences": m ** n,
        "marked_examples": n * m ** n,
    }


def verify_a5_reorderings(seed=20261020):
    """Check exact posteriors against all 6! reorderings for every own element."""
    G = groups.get("A5")
    rng = np.random.default_rng(seed)
    permutations = np.array(list(itertools.permutations(range(6))))
    checked = 0
    for own in range(G.n):
        cycle = max(permutation_cycles(G, own), key=len)
        # Besides random multisets, force long paths and repeats. A length-ten
        # cycle with six consecutive distinct labels has negative posterior 1/720.
        width = min(6, max(1, len(cycle) - 1))
        structured = np.resize(np.array(cycle[:width]), 6)
        for other in (rng.integers(G.n, size=6), structured):
            words = np.concatenate([
                np.full((len(permutations), 1), own), other[permutations]
            ], axis=1)
            positive = int(groups.match_labels(G, words, 3)[:, 0].sum())
            assert posterior(G, own, other) == Fraction(positive, len(permutations))
            checked += 1
    return {
        "all_posteriors_match": True,
        "own_elements": G.n,
        "multisets": checked,
        "reorderings_per_multiset": len(permutations),
        "total_relabelled_sequences": checked * len(permutations),
        "seed": seed,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-a4", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    result = {
        "command": (
            "uv run --no-project --with numpy python research/theory_ceiling.py "
            "--verify-a4 --output research/results/theory_ceiling.json"
        ),
        "checks": {},
    }
    if args.verify_a4:
        result["checks"]["exhaustive_A4"] = verify_exhaustive_a4()
        print(json.dumps(result["checks"]["exhaustive_A4"]), flush=True)
    result["checks"]["A5_reorderings"] = verify_a5_reorderings()
    print(json.dumps(result["checks"]["A5_reorderings"]), flush=True)
    for name, n in (("A4", 6), ("A5", 11)):
        data = exact_ceiling(name, n)
        result["checks"][name] = data
        print(json.dumps({key: value for key, value in data.items()
                          if key not in ("denominator_word_counts", "cycle_types")}), flush=True)
    result["all_checks_passed"] = True
    if args.output:
        path = pathlib.Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2) + "\n")
    print("All exact posterior, counting, and Bayes-ceiling checks passed.")


if __name__ == "__main__":
    main()
