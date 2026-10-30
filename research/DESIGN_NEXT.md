# Designs prepared overnight (23 October)

## A. State-change readout for natural proofs (stage-two fallback)
If the registered natural-proof batch shows the base tracker not reaching in-distribution exactness, the
bottleneck is the readout (re-emitting a 256-token state), not the objective. Replace it with a change
readout: per tactic, predict (i) which goals close, (ii) which hypotheses are added, each as a short
structured record (goal index; hypothesis name slot, type tokens), (iii) a "no other change" flag; the
full state is reconstructed by applying the change to the previous canonical state, and exactness per step
is exactness of the change. The invariance term and the metric are measured on LN(slot) as before; the
reconstructed states are compared for the pair diagnostics. This mirrors the chain domain, where a rewrite
is a local change to a tree. Cost: the generator already has state_before/state_after; a diff is a few
lines; the head is tiny. Register: base per-step exactness ≥ 0.9 in distribution; then the same arms.

## B. Systematicity axis on chains
Length is one axis of generalisation; a prover needs new lemmas and new atoms too. Test: train on 4 atoms
and the four tier-1 lemmas; evaluate on (i) fresh atom names (alpha-renaming at test only), (ii) a held-out
lemma instance pattern (e.g. mul_assoc never seen at the root), (iii) five atoms. Arms R, R+NL, R+NL+I, R+M.
Prediction: the metric and the invariance arms, which tie states to behaviour, degrade less under (i) and
(iii) than NextLat alone; (ii) is hard for all and is reported as the limit.

## C. Why the invariance arm loses exactness at 80k chains (LEAN_S D1)
Hypotheses, in order of likelihood: (1) the delayed start is a fixed fraction of steps, so with 4× data per
epoch the term is on for fewer passes over each pair; (2) the number of certified partners per chain was
fixed, so the pair budget per step did not scale with the data; (3) the floor (∝ η/μ) is unchanged while
the base's drift per seed is smaller with more data, so the term's residual dominates. Cheap check: rerun
the 80k cell with partners scaled with the data and μ = 3 ($2).
