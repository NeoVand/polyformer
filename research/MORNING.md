# Morning summary, 23 October 2026

Spend overnight: about $75 of the second $100 (metric 9.66, mechanism ≈ 4, natural proofs 42.05 incl. the
fallback, scale addendum ≈ 3, prover proxy 1.10, hardening 12.62 counted in the first). Nothing is running
except the symbol-agnostic chain test (≈ $8). Every branch is committed; the index is HANDOVER.md.

## What held
- Six seeds per arm on certified chains: plain tracker 0/6 exact at 256; invariance, NextLat, combination
  6/6; at 1,024 the combination 6/6 (LEAN_S).
- The single equation (Nerode metric) is exact alone on tier 1 (METRIC T8.1).
- Tier 2 is under-training: the combination is exact at 24k steps (METRIC §5).
- The 80k anomaly is a diluted term; scaling partners or μ with the data restores exactness (LEAN_S).
- Search with the exact tracker as imagination: one kernel call per solved problem vs 64/442 at equal
  success; drift hurts after long prefixes (PROVER_PROXY). Every solution is a Lean proof.
- The exact state is the Nerode partition: 960 pure clusters, an affine image of the tree string, rewrites
  as the induced permutation's linear map (MECHANISM).
- Code as a second domain: term exact 2/3 at 256 where the plain tracker is at 0.05–0.25 (EXEC_D).

## What did not
- Natural mathlib proofs, two readouts: the tracker learns the kind of step but never writes the content a
  tactic introduces; free-running 0.000 for every arm including the transformer. The obstacle is content
  generation at this size, not tracking (LEAN_N §10).
- Beyond length: nothing generalises to fresh atoms or a fifth atom (0.000); the symbol-agnostic fix is
  the one test still running (MECHANISM item 4).
- Language: the corrected metric test is not killed but what the state carries is the first-owner shortcut
  (METRIC T8.3′).
- Three of my overnight predictions were wrong in the right direction: NextLat alone is exact; the metric
  is the weakest clause incarnation on tier 2; NextLat does not leave an unminimised automaton.

## Decisions for you
1. Paper framing: three clauses with certification and a measured search saving (my recommendation), or
   the narrower "certified invariance" story.
2. Stage two: stop at the negative-with-reason, or fund the content route (a larger generator with
   premise retrieval, trackers for the determined steps) at an order of magnitude more.
3. Publish the overnight parts to the app (hardening, mechanism, prover proxy, natural-proof negative)
   now or after the symbol-agnostic result.

## Last result (06:30): the symbol-agnostic attempt did not bind
With fresh random atom embeddings per chain and a pointer readout, training learns the operators and leaves
the atoms at chance: the cross-entropy settles at exactly (4/9)·ln 4 on three of four runs and the state
ignores the atoms, so the tracker is exact nowhere, in distribution included (MECHANISM §5, $0). A linear
readout over random embeddings cannot bind an atom to its role; the fix needs a content-matching mechanism
(the state attends to the chain's atom embeddings and copies by similarity), which is the pointer network's
original form, not a linear head. This is the first design decision of the day if the systematicity axis
matters for the paper; it does for the dream.
