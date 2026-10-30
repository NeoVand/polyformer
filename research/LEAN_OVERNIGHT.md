# Lean program at $100: the overnight plan

23 October 2026. Budget raised from $12 per stage to $100 for the Lean program. What changes: we can run
three seeds everywhere, carry a scale axis, add a second certified domain for generality, and reach the
natural-proof stage tonight. What does not change: every run is registered before it spends, each stage
gates the next, and the kill rules stay.

## Allocation (gated; totals are caps, expected spend is lower)

| block | what | cap | gate |
|---|---|---|---|
| H | **Hardening of stage one**: fair transformer control (depth and steps swept to exactness at training length, FLOP ratio stated); tier 2 (distributivity, size-changing); the floor lever (final LR ÷10; μ = 3), with exactness at 4,096 steps | $12 | none: runs first |
| S | **Scale axis on stage one**: tracker width 64 / 128 / 256 / 512 and data 5k / 20k / 80k chains, R and R+I, 2 seeds; claim: the effect does not shrink with size or data, and the plain tracker's drift does not vanish with more data at fixed length (the theorem says it cannot) | $15 | H's tier-1 numbers hold |
| D | **Second certified domain**: the code-execution generator already built on `claude/gallant-panini-8f54d6` (interpreter traces, alpha-renaming and reordering as certified equivalences); R, R+I, control, T, 3 seeds; same registered shape as LEAN_S1 | $10 | none: independent |
| N | **Stage two, natural mathlib proofs**: re-trace the Data/ slice with positions ($2); canonical renaming; train on proofs of ≤ 4 tactics, test at 8–15 and ≥ 16 under the novel-premises split; tracker at 10–50M parameters; arms R, R+I (alpha-renaming and independent-reordering partners, kernel-certified by re-running swapped pairs), control, T; 3 seeds at the headline cell; metrics exact match per step and first divergent step | $45 | H passes tier 2 or the fair-T control |
| P | **Prover proxy** (if budget remains): on recorded ReProver search trees, score candidate tactics by the tracker's imagined k-step state against the kernel's; measure how many kernel calls an exact tracker would have saved at equal proofs found. No live search | $10 | N shows exact match above the transformer at ≥ 8 tactics |
| reserve | reruns, failed jobs, the unexpected | $8 | |

## Order tonight

1. H and D start together (independent; ~90 min).
2. S starts when H's tier-1 reruns confirm the registered result (~2 h).
3. N's data step (re-tracing, canonicalisation, partner certification) starts immediately since it costs
   $2 and takes the longest; N's training starts when H passes.
4. P only if N is positive and the reserve allows.

## Registered claims for the paper, by block

- H: T exact at 8 and collapsed by 256 at ≤ 2× FLOPs; R+I exact at 256 on tier 2 on 3/3; the floor falls
  ≥ 2× under either lever.
- S: R+I exact at 256 at every width and data size; R's exact-seed rate does not rise above 1/2 with 4×
  data at fixed training length.
- D: R+I exact at 256 statements on 3/3; R drifts; T collapses; control destroys; growth predicts drift.
- N: R+I exact-match per step above R and T at 8–15 and ≥ 16 tactics by a registered margin; first
  divergent step later; the growth diagnostic holds on natural proofs.
- P: kernel calls saved at equal proofs, a number with a confidence interval.

## What I will not do with the money

No new mixers, no language runs, no unregistered sweeps, nothing above a block's cap without a note in
this file and Neo's word.

## Amendment (novelty check, 23 Oct)
Block H gains two registered arms on tier 1: **NextLat** (next-token loss plus next-latent prediction given
the next token, stop-gradient target, d = 1, as in arXiv 2511.05963) and **NextLat + invariance**. Prediction:
NextLat alone improves over R but is not exact at 256 on 3/3 (its published generalisation is 3× at > 95%);
the combination is exact. This is the comparison the paper needs; see NOVELTY.md.
