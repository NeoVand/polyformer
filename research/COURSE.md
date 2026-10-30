# COURSE: what went wrong, and the corrected course

23 October 2026, afternoon. Written after the natural-proof block failed a third readout. One file; the briefs
that follow point here and nowhere else.

## 1. Where we stand, in three facts

1. **Exact state on certified synthetic domains is finished.** Rewrite chains (tier 1 and 2), code execution,
   group words: the tracker with the invariance term, or with next-latent prediction, or both, is exact at
   128–512× its training length on every seed; the plain tracker drifts; the transformer collapses. The mechanism
   is the minimal automaton in a ~20-dimensional affine code (`MECHANISM.md`). The theory (`EXACTNESS.md`,
   `PROOFS.md`) explains every anomaly we met. This is a solid method-plus-theory paper on state tracking. It
   is not the jewel.
2. **On natural proofs, three readouts failed at the same place.** Whole state (§7–9 of `LEAN_N.md`), the change
   readout (§10) and the copy head (§11, chain gate 0.44) all learn *what kind of step* a tactic is (0.90–0.94
   in distribution; closures stay exact at 0.93–1.00 on longer proofs) and never produce the *new terms* a step
   introduces (rewritten target 0.00–0.02, added hypothesis types 0.06). Free-running string match: 0.000.
3. **Our term's margin over next-latent prediction is thin on chains** (3/3 vs 2/3 at 4,096; 6/6 vs 6/6 at 256).
   The paper's strength is the theorem, the certification and the metric, not that delta.

## 2. Diagnosis

**(a) We scored strings, not futures.** Our own thesis (`LEAN_PLAN.md` §0) says the kernel is the Nerode
oracle and the state is the class of histories with the same future. Then for natural proofs we defined
success as reproducing Lean's pretty-printed state. That is *generation* of new content, a neural elaborator,
which a 128-wide slot cannot do and which large language models already do passably. Three heads later we were
still bending the architecture around the wrong target. The parts of the readout that are *decisions* (kind,
closures) worked on the first try and extrapolate.

**(b) We predicted dilution and then ignored it.** Proposition B says the term selects exactness only where the
primary loss is dense in the state and its strength scales with observations per step. A rewrite chain gives a
full observation at every step. A natural proof gives one: the gold tactic's result. We never added observations.

**(c) The end use never needed the strings.** A prover gets the state text from the kernel for one call. What
it cannot get cheaply is what the kernel will say about tactic sequences it has *not* run yet. The valuable
product is the kernel's verdict k steps ahead. `PROVER_PROXY.md` already measured this on chains: one kernel
call per solved problem against 64–442.

**(d) Process.** About $75 of the night went into hardening what already worked (blocks H, S, D, metric,
mechanism). The leap step was funded last and judged by the wrong metric.

## 3. The correction: read out decisions, not strings

**Stage two becomes a kernel oracle.** Input: the initial proof state, seen once; then tactics one at a time,
with no intermediate state. Output at each step: what the kernel would say to this tactic at this point:
accepted or rejected; goals remaining; proof complete; error class. "Imagination depth k" means the slot has
carried k−1 steps without a kernel. The latent keeps whatever content the verdicts require; nothing is decoded.

This is the theory applied literally. Observations o(u) are kernel verdicts; two histories are Nerode-equivalent
when no tactic future distinguishes their verdicts; the metric of `EXACTNESS.md` §8 is defined on exactly these.
Density comes from **several probe tactics per state**: the gold tactic (accepted) and perturbed tactics
(verdict from the REPL), so the loss is dense in the state as Proposition B requires. A wrong latent now shows
first-order in a wrong verdict, which is the signal the term and next-latent prediction shape.

**Why a prover cares.** A k-step look-ahead filter that spares kernel calls at equal proofs found. The guard,
from the ICML 2026 "candidate exposure" result (ranking filters hide tactics Lean would have accepted): recall on
accepted tactics is registered, not just accuracy.

**Novelty** (searched 23 Oct). No published model predicts Lean's verdicts several steps ahead without the
kernel. Nearest: effect-grounded tactic embeddings (Samoylov & Vosoughi, MathNLP 2025; Dartmouth thesis 2026),
which embed a tactic by the edit it makes and do no imagination; LeanProgress (arXiv 2502.17925), which
predicts steps remaining and gains 3.8 points on Mathlib4 with ReProver; VERITAS (arXiv 2606.19399), a critic
with the kernel in the loop. Verifier-in-the-loop methods run Lean at every step. None carries a state without
the kernel; none claims exactness or length extrapolation.

## 4. Pilot D1, registered before spend (≤ $25 in two sessions)

### 4.1 Data (session lean-n-data; cap $6)

For every step t of every item in `tree.npz` (about 8,400 natural steps, all splits), build probes at state s_t:

| probe kind | construction | expected verdict |
|---|---|---|
| gold | the item's tactic at t | accept |
| misplaced gold | the item's tactic from another step t' ≠ t, applied at s_t | mostly reject; valid text, wrong state (the hard class) |
| premise swap | the tactic with its premise replaced by another premise used in the same file | mostly reject |
| argument permutation | arguments reordered, or one dropped | mixed |
| corpus random | a tactic from a different item | mostly reject |

The REPL (as in `LEAN_N_DATA.md` §2, same mathlib commit) runs each probe at s_t and records: accepted (no error
and goals re-canonicalise), goals remaining, proof complete, error class (unknown identifier; rewrite failed;
type mismatch; unsolved goals; timeout; other), and for accepted perturbed probes the resulting canonical state.
Four perturbed probes per step; about 42k REPL calls; the data step cost $0.67 for about 10k, so about $3; cap $6.
Output `research/results/lean_n/data/probes.npz` with per-probe fields and an index into `tree.npz`; a README
with verdict shares per kind and split; the test probe sets per depth k ∈ {1, 2, 3, 4, 6, 8, 12}, balanced
accepted/rejected within the misplaced-gold class, drawn from the registered test items and all 138 test items.
Chain probes for the gate: at a chain state, a lemma instance at a position where it applies (accept) or does
not (reject); 2 per step, 16k steps; certified syntactically by the rewrite engine (Lean is not needed: the
engine is already the certified source for chains).

### 4.2 Training (session lean-n-train, after its §11 gate report; cap $18)

Model: stage one's tracker (d = 128, 4 ticks, no event encoder), the one exact at 256 on chains under a linear
head. A probe tactic goes through the same transition as a gold step; the **verdict head** is linear in
LN(slot′): accepted (2-way), goals remaining (softmax to 16), complete (2-way), error class (6-way). On a
rejected probe the slot is reset to its pre-probe value (the kernel rejects, the state is unchanged); the
trajectory continues with the gold tactic. Next-latent prediction targets the slot after the gold step;
invariance partners are the three kinds already built (alpha, reorder, equal states).

Arms: **R**, **R+NL+I**, **T** (causal transformer over initial-state tokens plus the tactics so far, per-event
FLOPs matched), **B** (state-blind: verdict from the probe tactic's tokens alone), **U** (one-step critic that
is *given* the true state text at step k−1; uses the kernel, upper bound). Two seeds. Natural items only, 8k
steps, the §10.3 schedule. Gate C0 first on chains ($1): R+NL+I verdict exactness 1.000 at 256 on both seeds.

Metrics at each depth k: verdict accuracy on misplaced-gold probes; on all probes; recall of accepted probes at
a fixed threshold; goals-remaining exactness; pair-distance growth (the drift diagnostic).

**Predictions, committed now.**
- **P1, tracking exists.** At depth 1, R+NL+I's misplaced-gold accuracy is at least 10 points above B on both
  seeds. *Kill the direction if not*: then the slot does not carry the state at all.
- **P2, exactness carries.** From depth 1 to depth 8 on misplaced-gold probes, R+NL+I loses at most half the
  points R loses, and is at least 5 points above T at every depth ≥ 4, on both seeds.
- **P3, the prover guard.** At the threshold where R+NL+I keeps 90% of accepted probes at depth 4, it rejects at
  least 50% of the rejected ones. (Translates into kernel calls spared.)
- Reported, not registered: U's accuracy (how far below the kernel-fed critic we are), growth versus accuracy
  (Spearman), per error class.

### 4.3 If P1 and P2 hold

Stage three: replay ReProver's search trees on the novel-premise test with the oracle as a k-step filter; the
number is kernel calls spared at equal theorems proved, with recall of accepted tactics beside it. After that,
the jewel path: the three clauses (verdict cross-entropy, next-latent, certified invariance) as auxiliary losses
on a 1.5B prover's hidden state, judged by compile rate against proof length.

## 5. What stops

- The content route (§11 copy head) stops after its gate report. Producing new terms is the generator's job.
- No more hardening runs on synthetic domains. String exact match stays the metric there, and only there.
- The $80 cap of §11 is released; D1 spends at most $25 of it.

## 6. Odds, honestly

Pilot positive: about one in two. Given that, the search-tree number positive: about one in two. A paper exists
on either branch (theorem, certification, metric, synthetic exactness, mechanism, the oracle result positive or
negative with its reason). The jewel needs both branches.

### 4.4 Amendment to the evaluation, registered before the natural pilot ran (23 Oct)

The data session's depth-balanced test sets hold 34–70 probes per depth for depths 1–8 and 2 at depth 12 (misplaced
gold is accepted on 21.9% of probes, so balancing by subsampling discards most of them). At that size a 10-point
margin sits inside the sampling error. Therefore, with gate C0 still running and no natural number seen:

- The misplaced-gold metric is **balanced accuracy over all misplaced-gold probes at a depth** (mean of the
  per-class recalls, no subsampling), with a bootstrap 95% interval over items.
- Depths are pooled into bands **{1}, {2–3}, {4–6}, {7–12}**. P1 is judged on band {1}; P2's "loses at most half"
  compares band {1} with band {4–6}; "≥ T + 5 at every depth ≥ 4" becomes "≥ T + 5 on bands {4–6} and {7–12}".
- The same curves are also computed on the validation split (332 items) and the held-out training items (285),
  which are larger, as supporting evidence; the registered verdict stays on the test items.
- P3 is judged on band {4–6}.

Probe verdict shares, for the record: gold 100% accepted; misplaced gold 21.9%; premise swap 10.3%; argument
permutation 44.8%; corpus random 5.7%. The 32,000 chain probes passed a 200/200 Lean spot check each way. Data
spend $0.058 of $6.

### 4.5 Gate C0 contingency, registered after seed 0 (0.576 at 256) and before seed 1 reported

A verdict on a chain is one bit per probe, two probes per step, against about ten bits of state. The primary loss
is therefore sparse in the state, the regime of Proposition A, and drift is the predicted outcome. Two readings are
possible and the in-distribution number separates them:

- **Drift** (verdict exactness ≥ 0.98 at 8–16 steps, falling by 256): density is the remedy. Amendment A: chain
  probes 2 → 8 per step, and next-latent prediction computed **in the latent** (centred cosine on LN(slot), stop-
  gradient target, as the invariance distance is), not through the verdict head, so that the dense self-supervised
  clause does not inherit the readout's sparsity. If A still drifts, amendment A′ adds the Nerode metric loss of
  `EXACTNESS.md` §8 with the verdict distribution as the observation, which is the theory's instrument for
  propagating sparse distinctions backward through the recursion (branch `claude/metric-0160e1`).
- **Cannot compute applicability** (in-distribution exactness < 0.98): the transition was built to produce the next
  state, not to compare a probe's pattern with a subtree. Amendment B: the verdict head becomes probe-conditioned,
  linear in LN(slot) for each probe (a bilinear form of the pre-probe slot and the probe encoding); the transition
  still produces the slot after an accepted probe. The invariance distance stays on LN(slot).

Gate rule unchanged: the natural pilot runs only after R+NL+I is exact at 256 on both seeds under the amended
configuration. Cap unchanged ($18 for the training session; about $2 per gate attempt).

**Gate C0 under B, decision on a split result (23 Oct).** Seed 0 exact (0.99999 at 256); seed 1 0.99146 with
training accuracy 0.992 and errors flat with depth: under-fit, not drift. Decision: both seeds rerun at 24k steps
under the same configuration (about $3); the gate counts only as 2/2 under one configuration. For the natural
pilot: the 8k schedule stands, but any arm whose training verdict accuracy ends below 0.99 is extended to 16k
before a test number is read, and both are reported.

## 7. Pilot D1 verdict (23 Oct, evening): negative, and uninformative about tracking

`LEAN_N.md` §12.6–12.8, commit 7d0852a on `claude/lean-n-train-a0a5e2`. Gate C0 passed at 24k steps (1.00000 at 256
on both seeds). On natural proofs P1, P2 and P3 all fail. Misplaced-gold balanced accuracy on the registered test
items sits at 0.57–0.78 for every arm in every depth band, with overlapping intervals; training accuracy is 1.000
for every arm that sees a state; the state-blind baseline cannot fit the training verdicts (0.80) and tests at 0.64.

**The decisive line is U.** The critic that is *given the kernel's true state* reads 0.64–0.69, inside the intervals
of the trackers and of the state-blind baseline. So from 2,565 theorems, a model trained from scratch cannot learn
whether a mathlib tactic applies to a mathlib goal even with the goal in hand. The pilot therefore cannot separate
"the slot does not carry the state" from "nothing at this scale reads a verdict off a state". The kill rule fires
as registered; its premise (that U is learnable) was false.

**What held.** On chains the same machinery, same head, same term, is exact at 256 steps. The invariance term and
next-latent prediction again collapsed the natural-proof state space (unrelated distance 0.03) once the primary
loss was memorised, which is the predicted trivial minimum when the primary loss stops supplying distinction.

**Boundary, stated for the paper.** The exact-state mechanism works where the per-step content function is
learnable from the data; on natural mathlib proofs at this scale it is not, and that limit sits upstream of state
tracking. Crossing it needs a pretrained encoder of goals and tactics and the full LeanDojo corpus, with U as the
ceiling to beat first.

## 8. Options now

- **A. Lean oracle at scale.** All LeanDojo steps, REPL verdicts for 4 probes each (the data step cost $0.06 for
  42k, so a few dollars), a pretrained encoder (ReProver's or a small code model) for U first; tracking test only if
  U clears 0.85. $40–80. Odds of a clean exactness result: low; one-step acceptance is known to be hard (ICML 2026
  candidate-exposure result) and a 0.8 ceiling leaves no room for an exactness claim.
- **B. Write the paper we have.** Theorem, certification, Nerode metric, three certified domains exact at 128–512×,
  mechanism, prover proxy, and the two negatives with their reasons (language: no distinction for free; natural
  proofs: content function not learnable at this scale). Costs tokens, not dollars.
- **C. Latent execution without chain of thought (the regime the theory names).** Code execution is the domain where
  the content function is learnable (EXEC_D), certification is free (the interpreter), equivalences are certified
  (renaming, reordering, equal states) and the long-horizon failure of language models is well known. Test: a
  pretrained small language model as the statement encoder, the recurrent slot with the linear per-position readout
  (the recipe that holds), against the same model writing the state after every statement (chain of thought) and
  against it predicting the final state directly. Metric: exact state at 64 / 256 / 1,024 statements after training
  at ≤ 16, and tokens per step. Registered predictions: slot + term exact at 256 on 3/3; no chain of thought collapses
  by 64; chain of thought decays with length at 10–50× the tokens. ≤ $60. Odds of a positive: about 55%.

**Recommendation.** C and B together; A closed unless Neo wants the $10 ceiling check for the paper's boundary
statement. The paper page gets the D1 result at the next publish.

## 9. Audit of D1 (23 Oct, night): the measurement stands, the interpretation does not

A fresh reviewer (`D1_AUDIT.md`) reproduced every number from the stored per-probe predictions and found no leakage,
label, index, mask or depth error. Three findings overturn the reading of §7:

1. **U was not a ceiling.** It was trained from scratch, 128-d, the same cell as R; it fused a pooled state vector
   with a pooled probe vector only at the end (no probe token ever attended to a state token); and 44–48% of the judged
   probes named a hypothesis under a different name than U's state used, so it was partly blind by construction.
2. **A one-word table beats every arm.** A logistic regression on the tactic's head word, fit to the same training
   probes, out-ranks every arm including U on three of four depth bands (AUC 0.78–0.83 against 0.56–0.78), with paired
   intervals excluding zero. The state-blind baseline's 0.64 is that prior.
3. **The protocol memorised.** About 220 passes per training probe; training accuracy 1.000 by step 4,000; no
   validation-based checkpoint selection (the last step was judged); final models put p(accept) < 1e-4 on 38–49% of
   test probes. Failing to beat a one-word table is the signature of memorisation, not of an unlearnable function.

So "the verdict function is not learnable from 2,565 theorems" is **not shown**. What is shown: this training
protocol failed to generalise even a shallow feature. The direction is not dead; the pilot was run badly.

### 9.1 Rerun D1′, registered before launch (cap $6)

- **U′**: state and probe with consistent names (probe renamed with s_t's own positional map, or the state rendered
  with source names); probe tokens cross-attend over the state tokens; d = 128; same 2,565 items.
- **B′**: the state-blind arm, same training.
- **Floor**: the head-word logistic regression, reported on every band.
- **Model selection**: both arms pick their checkpoint on validation misplaced-gold AUC, evaluated every 250 steps;
  2 seeds; steps 8k; dropout 0.1 on the probe and state encodings.
- **Metrics**: balanced accuracy at the validation-chosen threshold, and AUC, on bands {1}, {2–3}, {4–6}, {7–12}.
- **Gate G′**: U′ beats both B′ and the floor by ≥ 0.10 balanced accuracy on bands {1} and {4–6} on both seeds. If G′
  holds, the trackers (R, R+NL+I, T) are rerun under the same model selection and the P1–P3 verdicts are re-read, with
  the floor as the baseline for P1 instead of B. If G′ fails, §7's reading stands as "not learnable at this scale
  under this protocol", and the pretrained-encoder question remains open.

### 9.2 D1′ result (23 Oct, night): gate G′ fails; the natural-proof reading now stands honestly

`LEAN_N.md` §13, commit 7acfbe5; $1.71. With consistent names, cross-attention from probe tokens to state tokens,
dropout and validation-chosen checkpoints, the critic given the true state reads 0.69–0.75 balanced accuracy on
bands {1} and {4–6}, the blind arm 0.68–0.76, the head-word floor 0.705 and 0.755. Margins over the blind arm −0.03
to +0.07, over the floor −0.06 to +0.03; the gate needed +0.10 over both. The state carries a little rank signal
(AUC +0.05 to +0.08 over the blind arm on band {4–6}, intervals excluding zero) but no more than the one-word table.
Early stopping worked on three of four runs. **Conclusion:** whether a mathlib tactic applies to a mathlib goal is not
learnable from 2,565 theorems by a small encoder trained from scratch, beyond the head-word prior. Trackers not
rerun. Open: a pretrained encoder of goals and tactics (cost $10–15 for the ceiling check). The exact-state line on
natural proofs waits on that; the paper states the boundary as measured, with the floor and the protocol.

## 10. Night 3 (23 Oct): the theorems, the execution pilot, and six cheap predictions

**PROOFS2.md** (branch `claude/gracious-panini-dde55f`, commit e58b194, 8,814 words), reviewed in the parent session:
T1 (readout criterion: a sole linear readout keeps differently labelled histories apart by (m_u+m_v)²/4K²; a second path
admits a collapse at cost I(Y;S|C) ≤ H(S)/n per token, which is 0.06 bits for the decoder head; an interpolating head
admits an exact collapse), T4 (observations per step, Fano bound; thresholds 15 / 21 / 362 probes on chains) and T5
(factoring through the minimal automaton ⇔ trivial holonomy on certified loops; drift ≤ curvature) are proved in full.
T2 (next-latent prediction is a right congruence refining Nerode, margin-free first-order, blind to coherent drift; the
combination theorem 2.4 under a closure assumption) and T3 (contraction corrects errors below (1−λ)·min(r, m/√2K); without
contraction σ√N; the term is the only margin-free force toward contraction, under a linear transverse model) are proved
with one part each under an extra assumption. T6 is conditional on TC⁰ ≠ NC¹. Verdict: sound; the paper's spine.

**EXEC_LM pilot** (`EXEC_LM.md` §2–3, $6.69): Qwen2.5-Coder-0.5B frozen middle-layer features + slot + linear bit head,
16k steps: exact at 256 on three pilot seeds (1.000 / 0.992 / 1.000), 0.90 and 0.98 at 1,024 on two; chain of thought
fine-tune 1.000 at 16, 0.703 at 64, 0.172 at 256 (below the shallow floor 0.45); direct arm at the floor. Registered
main batch of 12 jobs running (P1 R+NL+I ≥ 0.99 at 256 on 3/3; P2 direct < 0.5 at 64; P3 chain of thought decays, 8
tokens per statement; P4 R drifts; floor rule ≥ floor + 0.10).

**Six predictions dispatched** (all under the $10 rule, total ≤ $8): T3 perturbation recovery and T5 curvature predictor
and T6(ii) monoid computation to the mechanism session ($0, saved checkpoints); T4 probes per step, T1 bounded
sensitivity and T6(i) transformer horizon to the lean-h session (cap $5); T2 next-latent on ortho8 to the energy
session (cap $1). Reports: MECHANISM.md §7, LEAN_H.md §6, ENERGY.md §4.

### 10.1 The six predictions: outcomes (23 Oct, night; MECHANISM §7, LEAN_H §6, ENERGY_E0E2 §4.6; $4.07 in all)

| prediction | registered verdict | what the data says |
|---|---|---|
| T3 contraction | P3a, P3b pass; P3c, P3d fail | R+NL+I perturbations decay at λ 0.50–0.70 per event; full recovery to 0.3 rad, none past 1.2 rad. But the one-event Jacobian at the centres is > 1 (max 3–4, median 1.6–1.9); products over 2 events are ≤ 1 and over 10 events 0.003–0.3. Contraction is multi-step, not per event. R also corrects small perturbations (λ 0.83–0.87). |
| T5 curvature predicts drift | P5a fail (Spearman 0.69 vs 0.8), P5b pass | Loop curvature at training length separates the arms by two to three orders of magnitude (R 0.07, R+NL 0.002, R+I 0.0004, R+NL+I 0.0002), in the order of their drift, but does not rank R's seeds (0.43); growth at 256 does (0.94). Bound (23) holds on 100% of pairs, loose by 70–800× because the transport contracts. |
| T6(ii) monoid | decided: solvable | The 960-tree monoid's maximal subgroups are all solvable (largest S4). The depth-bound impossibility does not apply to tier-1 chains; the transformer's collapse there is explained by the absence of a carried state (T6(b)), not by complexity. |
| T6(i) transformer horizon | T6a fail, T6b fail | The transformer's exact horizon is 8, 10 and 7 rewrites when trained at 8, 16 and 32: flat, not proportional to L; trained at 32 it is not exact at 16. R+NL+I exact to 4,096 at L = 8 and 16; at L = 32 it failed to train (loss spike when the term ramped in), an optimisation failure, not drift. |
| T4 probes per step | T4a pass, T4b fail, T4c pass | Below q = 32 the probe-trained tracker is not exact even in distribution in 12k steps; at q = 32 one seed of two is exact to 256. The information thresholds (15, 21) are far below the optimisation threshold; sparse readouts fail harder than predicted. |
| T1 bounded sensitivity | T1a, T1b pass; T1c fail | The Lipschitz-bounded MLP head is exact at 256 on 2/2 with every unrelated pair above the bound; the unconstrained head shrinks the unrelated distance 9–13× at a lower training loss and drifts (0.47 / 0.57 at 256), short of the registered 10×-of-floor level. |
| T2 next-latent blind to coherent drift | T2a fail (one falsifier seed), T2b pass | Two of three two-copy next-latent seeds keep the periodic copy-mixing drift; one stays exact to 1,024. With the term, 6/6 exact to 1,024. **Post hoc law:** on every drifting two-copy run the first failure length obeys L* · √d16 ≈ 15, with d16 the pair distance at training length; it predicts the term's seeds fail at 1,700–5,600, so the term may slow coherent drift by 10–40× rather than remove it. Rerun to 4,096 partly reproduced (containers differ in floating point); the periodic seed's predicted return and second failure both landed in their windows. |

**Reading.** Every direction the theorems predict holds; four thresholds missed, each in a way that sharpens the
theory: contraction is multi-step; the chain task has no non-solvable group, so the transformer's failure is about
carried state, not circuit depth; the transformer's horizon is flat at 8–10 rewrites whatever its training length;
the probe threshold is set by optimisation, not information; and coherent drift obeys a quantitative onset law from
the pair distance at training length, which is the drift predictor T5 was looking for (it works on ortho8, not across
R's chain seeds). Amendments requested from the proofs session.

## 11. The headline lands (23 Oct, night): latent execution without chain of thought

`EXEC_LM.md` §4–6, branch `claude/exec-d-0e1910`, commit 206e13a; $21.33 of $60. Registered batch, 12 jobs, seeds 0–2,
every prediction passes:

| arm | 16 | 64 | 256 | 1,024 | tokens generated per statement |
|---|---|---|---|---|---|
| slot on frozen Qwen2.5-Coder-0.5B features, with the term and next-latent prediction | 1.000 ×3 | 1.000 ×3 | **1.000 / 1.000 / 1.000** | 0.965 / 0.844 / 0.729 | 0 |
| same slot, no objective | 1.000 / 1.000 / 0.957 | 0.88 / 0.83 / 0.69 | 0.07 / 0.05 / 0.14 | 0.03 | 0 |
| same LM fine-tuned to write the state after every statement | 1.000 ×3 | 0.50 / 0.81 / 0.90 | 0.06 / 0.32 / 0.37 | 0.06 / 0.28 / 0.25 | 8 |
| same LM writing only the final state | 0.36–0.54 | 0.34 | 0.19–0.32 | 0.03–0.14 | 8/n |
| shallow floor | 0.51 | 0.45 | 0.45–0.47 | 0.42–0.45 | |

P1 (exact at 256 on 3/3) passes; P2 (direct < 0.5 at 64) passes; P3 (chain of thought decays; 8 tokens per statement)
passes; P4 (plain slot drifts) passes; the kill rule does not fire; the floor rule is met by the full arm at every
length. Never wrong along the way on 100% / 100% / 99.8% of 256-statement programs; at 1,024 the median program is never
wrong. No collapse (unrelated distance 0.09–0.22). Drift diagnostic: canonical-partner growth predicts drift at Spearman
+0.88. The 1,024 tail is the clock returning slowly (state norm 1.2–1.35×).

**Caveats for the paper (from §6 of the report):** the state lives in the slot, not in the LM's residual stream (the LM
is frozen and per statement); the domain is 4 named bit variables with `set` and `op`; training length 4–16; the
chain-of-thought and direct arms had 2,000 full fine-tuning steps and smaller test sets at 256 and 1,024.

**Next cells** (registered before spend, under the remaining cap): the 1,024-tail levers of EXEC_D §7 (about $5); a
richer domain rung, 4-bit integer variables with +, −, × mod 16 and conditionals, then 8-bit, with the same four arms
(pilot under $10 first); a LoRA-tuned encoder; chain of thought trained at longer lengths as the fairness check.

### 11.1 Rung A pilot (23 Oct, late): the slot's transition is too shallow for 4-bit arithmetic; chain of thought computes it and still fails at length

`EXEC_LM.md` §7.2, $7.31. Eight variables over 0..15 with +, −, × mod 16 and one-line conditionals. The slot (d = 128
or 256, two-hidden-layer transition, frozen middle-layer features) reaches 0.375 exact at the training length (0.83
per variable) after 10k steps, gaining 0.05 per 2k steps; chain of thought reaches 0.986 at 16 (0.997 per variable),
then 0.28 at 64 and 0.000 at 256 (first error at statement 46). Stopped at the pilot as briefed. Two limits, both
seen: the slot's per-statement function is too shallow for arithmetic over named 4-bit values (EXEC_INVARIANCE 1.1
found the same), and the language model's in-context state does not extrapolate. The page is live with section 51
(commit 51383ab).

**Next, under the standing rule (two pilots, each under $10):** rung A′, the state-space answer to the toy objection:
32 bit variables with the current operations plus conditionals on bits (the content function stays cheap, the state
space is 2^32, exactness there cannot be memorisation); and a deeper-transition pilot on rung A (4 ticks per statement
as the Lean tracker had, or a 3-hidden-layer transition) to see whether arithmetic comes within the slot's reach.
Main batches only after a pilot fits 16 at ≥ 0.98, registered first, inside the $60 cap; beyond it, Neo's word.

## 12. The trap, explained (23 Oct, late night): PROOFS3.md

`PROOFS3.md` (branch `claude/gracious-panini-dde55f`, 8d521f6, 4,448 words). Ranking of why the slot cannot learn
arithmetic over named values: **compositionality first** (the flat 128-wide slot has nothing that ties the computation at
one address triple to another; the true transition is equivariant under renaming the eight variables, so the natural
transition is eight registers with name-addressed reads and writes and one shared operation; chain of thought works
because attention is that shared read; and Proposition 3.3 proves the invariance term and next-latent prediction cannot
select the factorisation or the operation table, they select the frame condition only); **coverage second and
compounding** (zero-start programs make 83% of operation statements trivial, the effective number of local cells is 98 of
768, the flat learner has never seen 73% of its cells, and the operand distribution shifts at length, so even a fit slot
would extrapolate worse; random initial values raise the non-trivial share to 86%); **depth last** (one two-layer tick
cannot be exact, but deeper transitions learn at the same rate, so depth is necessary and not binding). The remedy for
content is the frozen model as a Markov step (4a): give it only the decoded state line and the current statement, no
history; Theorem 4.2 reduces exactness to a per-step error rate p with P(exact at N) ≥ Π(1 − p_t), turning the collapse at
statement 46 into a slow geometric decay; a frozen reader satisfies the bounded-sensitivity condition by fixity, so the
collapse theorem cannot bite through it.

**Dispatched (standing rule, each under $10, inside the $60 cap):** test 1, the factorised slot (registers, attention
read by name, shared operation MLP, write by name; prediction ≥ 0.98 at 16, kill below 0.90); test 3, Markov chain of
thought (prediction: no collapse, ≥ 0.9 at 64, 0.5–0.8 at 256, per-step error predicts the decay within a factor 2);
test 5, depth in isolation on single statements ($0). Test 2 (random initial values, flat slot) is already running with
both registered readings written down (coverage: ≥ 0.98; compositionality: ≤ 0.45).

## 13. Night 3 closes (24 Oct, early): the tail is closed, the trap is diagnosed, the cap is reached

`EXEC_LM.md` §7.1–9 on `claude/exec-d-0e1910` (bcaf1a4); EXEC_LM total $55.77 of $60, nothing running.

**The 1,024 tail is closed (registered, 3/3).** The RMS-normalised slot (norm fixed at √d after every statement), with
the term and next-latent prediction, is exact at 1,024 statements on 3 of 3 seeds (1.000 / 1.000 / 1.000; 1.000 / 0.998 /
1.000 at 256), 64× the longest training program, every one of 512 programs, the median program never wrong, canonical
distance 0.0001–0.001. L1, L2, L3 pass; the kill does not fire. The canonical-partner lever fails (0.60 at 1,024, kill
fires). Caveat: levers ran on the local CPU, the registered arm on Modal; a Modal confirmation of the RMS arm (3 seeds,
about $5) belongs in the paper's table.

**The trap is diagnosed: routing by name.** Four tests, all registered:
- Random initial values (coverage): 0.000 exact at 16, worse than the zero start (no easy early phase). Coverage is not
  the trap.
- Depth in isolation (clean one-hot state, uniform operands): three hidden layers reach 0.90, not 0.99; the transition fits
  every function symmetric in its two operands (+, ×) and fails the ordered ones (−, <), worst when both operands are read
  by name (0.59–0.66). Depth is not the trap; which-operand-is-which is.
- The factorised slot (eight registers, attention read by name, one shared operation MLP, write by name): **0.998 exact
  at 16** (prediction ≥ 0.98 passes; the flat slot: 0.375), 0.93 at 64, 0.75 at 256, 0.81 at 1,024 with repair by
  overwrite; not exact at length (drift signature returns in the registers; one seed; the slot is told where operand
  names sit).
- Markov chain of thought (frozen model, only the previous state line and the statement): the collapse is gone (0.27 flat
  to 1,024 against 0 for whole-history chain of thought) but the per-step error rises six-fold with length because the
  state lines at length are out of the training distribution; errors are repaired by overwrites, so exactness settles at
  a level rather than decaying geometrically. Theorem 4.2's bound holds and is loose.

**Rung A′ (32 bit variables)** stopped at the pilot: the flat slot plateaus at 0.76 exact at 16 (0.99 per bit) at either
width; chain of thought exact at 16, 0.43 at 64, 0 at 256. The same routing-by-name limit at 32 names.

**Reading for the paper.** Both sides of the recipe's reach are mapped. Where the per-step function is within the
transition (bits, four names): exact at 64× training length on every seed with no generated tokens, while the same
language model writing its state collapses. Where the step needs routing by name (eight or thirty-two names, arithmetic):
the flat slot cannot fit the training length; structure that routes by name restores the fit at once; length then
reopens as drift inside the registers. The objectives select exactness within what the transition can fit, and never
more (PROOFS3 Prop. 3.3, confirmed four ways).

**Proposed next spend (needs Neo's word; the $60 cap is reached), about $40:** (i) Modal confirmation of the RMS headline,
3 seeds ($5); (ii) the factorised slot with RMS registers on rung A′ (32 bits, the 2^32 state-space answer) and on rung A,
3 seeds each with the tail levers ($20); (iii) the Markov step trained on uniform states, PROOFS3 test 4 ($5); (iv) the
first-error diagnostic of the A′ plateau ($1.40).

## 14. The funded runs land (24 Oct): the headline replicates, and the arithmetic rung is solved by the Markov step

`EXEC_LM.md` §10 (1858193); $36.55; EXEC_LM $92.31 of $100, nothing running.

1. **RMS headline on Modal: passes.** Exact 1.000 at 16 / 64 / 256 / 1,024 on 3 of 3 seeds; canonical distance 1–3 × 10⁻⁴
   throughout. The 64× result is not a property of the laptop.
2. **Factorised slot, 3 seeds.** Rung A (8 × 4-bit, arithmetic, conditionals): exact at 16 on 3/3 (1.000 / 1.000 / 0.998);
   at length a plateau 0.72–0.77 from 256 to 1,024; the repair model's *form* holds (fed the late per-step error it
   predicts 0.71–0.74 against 0.72–0.73 observed, per-variable 0.89 vs 0.89), the registered version failed because it was
   fed the early error (states near the zero start). Rung A′ (32 bits): exact at 16 on 2/3 (seed 2 stuck at 0.676; the
   kill fires by one seed), and at length a collapse, not a plateau (per-step error climbs; registers rewritten only
   every ~37 statements lose their values between writes; soft write attention is the suspected channel). Chain of thought
   on A′ at 3 seeds: 0.98–0.99 at 16, 0.38–0.56 at 64, 0.000 at 256.
3. **The Markov step trained on uniform states: exact at 1,024 on 3 of 3.** The frozen 0.5B model fine-tuned on single
   (state line, statement) → next-state pairs with states uniform over values, then run with a fixed 74-token context
   (its own last state line plus the statement): 1.000 at 16 / 64 / 256 / 1,024 on every seed; per-step error 0.5–2 × 10⁻⁵,
   every error on a conditional and every one repaired. The same model with its whole history in context was 0 at 256; the
   Markov step trained on zero-start states plateaued at 0.27. Two changes made the language model exact at 64× on the
   arithmetic rung: cut the context to the carried state, and train the step on the states it will meet.
4. **A′ flat-slot plateau diagnosed:** 91% of first errors are wrong writes; conditionals that fire are the worst statement
   (0.185 per occurrence) and they are 3% of conditionals from the zero start: a coverage artefact again.

**What this does to the paper.** The title and headline stand (latent, token-free, certified equivalences). The reach
section gains its strongest line: where the step is arithmetic over named values, the latent route needs registers and
then plateaus, while the language model as a Markov step on a bounded state, trained where it will be used, is exact at
1,024 on every seed at a constant 8 tokens per statement. Chain of thought's failure at length is now explained with
evidence: a growing context and a training distribution of states that long programs leave; neither is arithmetic.
Prior art to check: "The Markovian Thinker" (bounded-state reasoning, 2025) and fixed-window scratchpads.
