# Paper skeleton (draft, night of 23 October 2026)

## Title candidates
- Certified invariance makes state trackers exact
- Three clauses of Nerode: exact state tracking from a kernel-certified objective
- Trackers that stay exact: a selection theorem and a proof kernel as the oracle

## Abstract (draft)
A recurrent tracker trained with the next-token loss learns transitions that are exact on some seeds and
drift on others, with identical training loss: we prove that a loss at training length L is blind to
per-step error below about 1/L while correctness at length N needs error below 1/N, so exact and
near-exact transitions share a flat minimum. We show that the Myhill–Nerode theorem supplies the missing
supervision in three clauses: output consistency (the primary loss), a right congruence (predicting the
next state, NextLat), and coarseness (an invariance loss over equivalent histories), and we state the
three as one bisimulation-metric fixed point. On rewrite chains certified step by step by the Lean 4
kernel, trackers trained with the congruence or coarseness clause are exact at 128 times the training
length on six of six seeds where the plain tracker drifts on all six and transformers collapse; the
combination is exact to 4,096 steps with the lowest floor; the same holds on interpreter-certified
programs. A search that uses the exact tracker as imagination pays one kernel call per solved problem
instead of 64 to 442 at equal success, and every solution is a Lean proof. We characterise the trivial
minima of invariance losses (common-mode directions, the trivial representation) and the conditions under
which the objective selects exactness (a primary loss dense in the state), which explain its failure on
natural-language narratives. [Natural mathlib proofs: result pending.]

## Contributions
1. The selection theorem (blindness of a length-L loss; first-order sensitivity of invariance; the floor
   as optimisation noise; the trivial representation as a saddle; growth not level). PROOFS.md A1–A6.
2. The three-clause reading of Nerode and the metric fixed point that contains them (EXACTNESS §7–8).
3. Kernel-certified exactness: Lean 4 certifies every step and every pair; 6/6 seeds exact at 256, 6/6 at
   1,024 for the combination; tier 2 partial; scale and data axes; two domains (LEAN_S1, LEAN_H, LEAN_S,
   EXEC_D).
4. The dream's mechanism measured: imagination search equals the kernel's search step for step, one
   kernel call per solved problem versus 64/442; drift matters after long certified prefixes
   (PROVER_PROXY).
5. Negative results with reasons: paraphrase invariance collapses (no distinction), decoder heads let the
   term collapse, unconditional self-prediction has a still-state minimum (PARA_INVARIANCE, LEAN_S1 4.1,
   SELFSTATE).

## Theorems to state (with proof pointers)
- Thm 1 (blindness and the threshold 1/(KL) vs 1/(KN)) — PROOFS A1.
- Thm 2 (admissible distances: invariant to every direction the readout discards; LN injective on
  centred parts) — PROOFS A2.
- Prop 3 (floor ∝ η_final/μ) — PROOFS A3; lever confirmed in LEAN_H item 4.
- Prop 4 (trivial representation: global minimiser of the term, slow saddle of the joint; delayed
  schedule) — PROOFS A4; LEAN/INVARIANCE A2.
- Prop 5 (growth, not level) — PROOFS A5; Spearman 0.75–0.91 in three domains.
- Thm 6 (joint minimiser = minimal automaton under a dense primary loss; dilution counterexample) —
  PROOFS A6; Nerode metric kernel and no-collapse (EXACTNESS §8, to be proved).

## Experiments and the numbers that go in the tables
- Group word problem (INVARIANCE): base 3/6, term 5/6 (reduced partners), 3/3 to 1,024 (random partners);
  e ≤ 8 training: base chance by 256, term 3/3.
- Lean tier 1 (LEAN_S1, LEAN_H, LEAN_S): six seeds; R 0/6 at 256; R+I, R+NL, R+NL+I 6/6; at 1,024 R+NL+I
  6/6, R+NL 6/6, R+I 5/6; combination exact to 4,096 3/3, floor 0.00012; transformer grid never exact at
  training length under 2× FLOPs; data axis: NextLat 8/8, invariance loses exactness at 80k chains (1/3).
- Lean tier 2 (LEAN_H): term 0.47 → 0.90 at 256, no seed exact; [metric and combination pending].
- Code (EXEC_D): R 0.05–0.25 at 256; R+I 2/3 exact; control collapses; T 0.26.
- Prover proxy: 1 call per solved problem vs 64/442; E1: drifting tracker wrong on 27–47% of long
  prefixes, loses 10–19 points; exact tracker 9,000/9,000.
- Natural proofs (LEAN_N): pending. Dilution harness with the metric (METRIC T8.3′): pending.

## Related work (verified; POSITIONING.md, NOVELTY.md)
NextLat (2511.05963) as the nearest and as a baseline arm; bisimulation metrics and MDP homomorphisms;
path independence; state-regularised and minimal-automata RNNs; forward-invariant certificates (ICML
2026); SIRE; Corder/ContraCode; the 2025–26 state-tracking literature; JEPA for Lean (negative).

## Limitations to state
Tier-1 chains are a finite synthetic space; tier 2 not exact; natural proofs [pending]; the invariance
arm's loss of exactness at 80k chains is unexplained; transformer control not exact at training length
under 2× FLOPs; language form open (distinction half).

## Figures and tables
F1 exact match vs length (four arms, six seeds) with pair-distance growth; F2 the compute graph; F3 the
floor vs η_final and μ; F4 kernel calls per solved problem vs distance, exact vs drifting tracker; T1
registered clauses and verdicts; T2 scale and data axes; T3 two domains.

## Night-2 additions to the skeleton (23 Oct, ~06:00)
- Metric loss: exact alone on tier 1 (3/3); weakest clause incarnation on tier 2 (floor grows); corrected
  language test moves the state but to the first-owner shortcut (probe 0.45, paired 0.07): a Figure/Table
  on "distinction without labels exists; what it finds is the shortcut".
- Tier 2 = under-training (24k steps: combination exact 2/2). Data axis: term strength must scale with
  data per step (80k anomaly = drift; 4× partners or μ = 3 restores).
- Mechanism figure: 960 pure clusters; ~20-d affine image of the Polish string; rewrites act as the induced
  permutation's linear map; NextLat also minimal. Systematicity: 0.000 on fresh atoms; symbol-agnostic fix
  [pending].
- Natural proofs: negative with reason (content generation, not tracking); the tracker's niche in a prover
  is the determined steps; free-running 0.000 at this size.
- Title leaning: "Exact state tracking from certified invariance: three clauses of Nerode, where each pays,
  and where none does".
