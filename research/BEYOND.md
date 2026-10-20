# Beyond softmax and RNNs: three candidates, one day

Started 20 October 2026. Worktree `.claude/worktrees/beyond`, branch `claude/beyond` (from main a3a6a78). Owner:
Astra (Codex). Claude orchestrates. This file is the plan and the log; anyone resuming reads it first.

Neo's request, verbatim intent: "invent a new mechanism out of all of these insights to finally universally beat
softmax and RNN ... guess 3 possible candidates that on paper should have all the important and necessary
characteristics, maybe one will work. We have a whole day left and it is worth trying."

## What we know (the constraints a winner must respect)

From SEARCH.md, LOCAL.md, GROUPS.md, THEORY.md and the word problems (GROUPS section 7):

1. **Selection** (softmax's strength): content-addressed retrieval over a long context. Every layer that dropped it
   lost on language; MQAR and induction need it.
2. **Estimation**: softmax is a local-constant estimator; adding linear precision helps language a little but
   reliably (LLA in an 8-dim chart 0.4%, Parallax 0.75% at equal FLOPs, Muon; gains grew with tokens for Parallax).
3. **Composition**: what a layer can relate is set by the algebra its features compose in. Softmax composes
   nothing; commuting layers stop at an exact order-blind ceiling; non-commuting rotations learn group irreps and
   track A5/S5 in one layer, where softmax collapses. Matrix-state RNNs (Householder/DeltaProduct) also compose,
   and with enough steps match holonomy on word problems.
4. **Learnability beats expressivity**: native terms get learned, compositions over depth mostly do not; short
   products (low arity) act as a curriculum and speed learning; the optimizer (Muon) matters as much as the layer.
5. **Language at our scale is low-order**: higher arity never paid on FineWeb at 19M parameters / 400M tokens.

A universal winner plausibly needs **selection + linear-precision estimation + non-commuting composition**, cheap
enough to win at equal FLOPs, and learnable (short sectors first).

## Seeds from Claude (Astra decides; replace any with better ideas, and check prior art first)

- **A. Selective holonomy (non-abelian subset attention):** softmax selection weights p_ij feeding an ordered
  matrix product, e.g. y_i = read( sum_j p_ij * U_{i<-j} v_j ) with U_{i<-j} the path-ordered product of learned
  per-token rotations between j and i (a content-dependent, non-commuting generalisation of RoPE). Check PaTH
  attention (Householder-accumulated position encoding, 2025), CoPE, and Stick-breaking attention.
- **B. Tilted attention + composing state:** softmax with an exponential tilt for linear precision (KL projection of
  the softmax weights onto "weighted mean key = query", a few Newton steps, positive weights; LLA is its
  chi-square cousin) in one head group, and a DeltaProduct-style matrix-state branch in another, mixed per layer.
- **C. Group-valued residual stream:** tokens carry a learned element of SO(d) alongside the vector stream;
  attention composes group elements of the selected tokens (selection picks, composition combines) while the
  usual values carry content.

## Protocol (pre-register, as in every study here)

Stage 0 (tests): brute-force checks of each layer (causality, special cases reduce to softmax / RNN / holonomy).
Stage 1 (screen, cap $25): one-layer and two-layer diagnostics: MQAR, induction, A5/S5 word problems (GROUPS §7
tasks), ordered Match-3 over A5, plus an LLA-style regression probe. A candidate must match softmax on retrieval
and match the matrix RNN on state tracking to advance.
Stage 2 (language, cap $100): the S6 harness (`research/lm.py`, FineWeb-Edu, GPT-2 tokens, 6 layers d512, Muon),
100M-token rate sweep (3 rates) for each surviving candidate, then 400M tokens x 3 seeds against the existing
softmax and Parallax numbers in LOCAL.md and a Gated DeltaNet / DeltaProduct baseline at equal FLOPs (FLOP counter
`lm.flops_per_token` extended). **Headline go:** >= 1% lower held-out loss than softmax at equal FLOPs on 3/3
seeds, and not worse than the matrix-state RNN baseline, while passing Stage 1.
Total cap $150. Predictions and thresholds committed before each main grid. Negative results written up honestly.

## Rules

Work only here; commit often (`Co-Authored-By: Astra (Codex)`); never push or merge into main; do not touch `src/`.
Append a line to the Log at each milestone. Final message: which candidate (if any) passed which gate, with numbers.

## Log

- Plan written by Claude; Astra launched.
