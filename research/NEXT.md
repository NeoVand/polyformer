# Two cheap, decisive tests: loss dilution and algebraic ARC

Started 20 October 2026. Worktree `.claude/worktrees/arc`, branch `claude/arc-dilution` (from main). Owner: Astra
(Codex); Claude orchestrates. This file is the plan and the log; anyone resuming reads it first. Cap: $35 of Modal
in total ($15 for experiment 1, $20 for experiment 2). Never push or merge into main; do not touch `src/`; commit
often with `Co-Authored-By: Astra (Codex)`; use /bin/rm and /bin/mv -f.

Background: read research/GROUPS.md (sections 0, 5-7), research/THEORY.md, research/LOCAL.md section 0, and
`.claude/worktrees/beyond/research/BEYOND.md` (the last search: selection + estimation + composition candidates;
B was 0.4% better than raw softmax but 0.7% worse than softmax with a short causal convolution; removing its
composition branch changed loss by only +0.04). Reuse code from research/ (groups.py, polybench.py holo layer,
lm.py) and from the beyond worktree (beyond_layers.py: DeltaProduct/GDN baselines, convolved softmax) where useful.

## Experiment 1: is composition hidden by token-averaged loss? (cap $15)

Hypothesis: if composition-sensitive positions are a small fraction p of tokens, a gain delta there moves average
loss by only p*delta, so "language is low-order" may partly mean "the metric dilutes composition".
- Data: generated paired narratives (8-32 operations: ownership transfers, alias assignments, revocations,
  overwrites) where a pair differs by one early operation and has different correct final answers; held-out
  paraphrase templates and held-out lengths.
- 2x2 design: softmax + short causal conv vs the composition hybrid (B from BEYOND, or holonomy/DeltaProduct
  branch), each trained with ordinary token-averaged cross-entropy vs decision-weighted loss (equal weight per final
  semantic decision), identical token budgets, 3 seeds.
- Also measure p (share of tokens whose loss depends on composition) and the per-position loss gap, to quantify
  dilution directly.
- Pass: weighting raises the hybrid's paired exact-accuracy advantage by >= 15 points and the hybrid exceeds 90%.
  Report what happens to softmax under weighting.

## Experiment 2: algebraic ARC, rung 1 (cap $20)

Question: does a composing layer infer composed grid transformations from few examples better than softmax (with
and without test-time training), and does the advantage grow with composition depth?
- Data: ARC-format tasks generated from random compositions of 1-4 primitives: dihedral symmetries of the grid
  (D4), colour permutations, cyclic translations; a harder tier adds irreversible primitives (crop to object,
  gravity, flood fill). 3 demonstration pairs plus a held-out test input; small grids (e.g. 6x6 to 10x10, 10 colours).
- Arms: small softmax transformer; the same plus test-time training on the demos; versions with a holonomy or
  matrix-state composing layer; optionally a closed-form in-context operator solver (fit a linear operator on
  one-hot grid encodings from the demo pairs by least squares and apply it) as the "wrong-looking" baseline.
- Score exact-match accuracy on the test output, by composition depth and tier, 3 seeds.
- Pass: the composing arm beats the best softmax arm by >= 15 points at depth >= 3 on the invertible tier, with the
  gap growing with depth. Report the irreversible tier separately whatever it shows.

## Protocol

Brute-force tests of generators and layers first; seed-0 pilots; then write predictions with thresholds into this
file and commit them before the main grids; 3 seeds; honest reporting including failures. Append to the Log at each
milestone. Final message: both verdicts with numbers, cost, and what to do next (including whether rung 2,
in-context operator inference, and rung 3, real ARC-AGI-1 with a TRM-style recursive baseline, are justified).

## Log

- Plan written by Claude; Astra launched.
- 2026-10-20 19:26 UTC — Read the plan and required background; delegated independent scientific review and
  test-first implementations. Worktree is clean at `a18ff25` before new files. No paid jobs launched, $0 spent.
  Reuse the tested Householder/prefix/convolution implementation from beyond commit `0ea244d`; compare shared
  convolved softmax against the same plus a composition branch, avoiding a Parallax-estimation confound.
  Main-seed selection and all hyperparameters will be frozen after seed-0 pilots, before main results.
- 2026-10-20 19:27 UTC — Runner budget tests were written and observed failing before implementation, then pass
  after adapting the existing bounded runner. Separate caps are enforced at $15/$20 with $35 total; unresolved
  calls retain full reservations and never retry automatically. Pricing checked at https://modal.com/pricing:
  L4 $0.000222/s plus conservative CPU/RAM maxima, startup and idle allowances. Estimates are not invoices.
  Important design caveat recorded before results: invertible ARC primitives form a closed family, so sampled
  depth is not intrinsic operator complexity. We will measure reduced identities/ambiguity and state this limit.
- 2026-10-20 19:29 UTC — Both generator/layer test suites are written first and observed failing on missing
  implementation modules. Experiment 1 avoids answer-conditioned rejection: reciprocal transfers preserve the
  initial owner's counterfactual difference. Decision weighting will mean equal weight per final answer and
  zero narrative-token weight, explicitly the strongest version of the requested reweighting. Experiment 2
  consumes only demonstration input/output grids and query input, with output masking and task-reset TTT tests.
  No paid calls yet. Main comparisons will use fresh seeds 1/2/3, keeping seed 0 for pilots only.
