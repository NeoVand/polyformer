# Beyond softmax and matrix-state RNNs — working report

**Experiments are running. This is not the final result.** Evidence snapshot: 20 October 2026,
16:04 UTC. B passes the prospectively reconciled written Stage-1 rule with **100% final test
accuracy in all 18 held-out confirmation cells**—six task/depth conditions across three training
seeds. Its original-code outcome is **unconfirmed** because two
standalone reference runs failed that code's additional accuracy floor. C fails the written rule:
two-layer S5 seeds 1/2/3 score **3.25%, 6.78% and 1.59%**, below the 95% threshold. These are valid
completed measurements. A also fails: one-layer S5 seeds 1 and 3 score **5.46% and 13.44%**.
C's complete record has no other below-floor cells. A also fails two-layer S5 at seeds 2 and 3.
All mandatory confirmations are complete and audited. **B is the sole candidate eligible for language.**
All three candidates reached 100% selected seed-0 validation in the
six primary cells. The descriptive grid is complete. B's language plan is frozen, and its
18-trial language rate sweep is complete. All arms select .008, and B trails both softmax controls
and both recurrent controls at that short tuning budget. No final-seed language result is yet available.
These results establish successful synthetic-task learning in this regime, not a language advantage.

The question is whether one affordable layer can combine content selection, improved local
estimation and order-sensitive composition, then beat both softmax and modern matrix-state RNNs
under a common candidate compute budget, with controls given at least each candidate's modeled work
under four declared arithmetic conventions. Earlier project studies motivated these capabilities separately;
their limits remain relevant. [LOCAL.md](LOCAL.md) found modest language benefits from local
linear estimation, while [GROUPS.md](GROUPS.md) and [THEORY.md](THEORY.md) distinguished
noncommuting composition from order-blind alternatives. None establishes that combining the
components improves language. The present experiment tests that additional proposition.

All three designs retain softmax content weights and use the same Parallax correction:
`w_ij = p_ij [1 − rho_i · (k_j − mean_p(k)_i)]`, followed by `z_i = sum_j w_ij v_j`.
The corrected weights sum to one and can be negative. The learned probe `rho` supplies a covariance
correction; it does **not** guarantee exact affine reproduction after training. The exact
inverse-covariance special case is tested separately. Positive-only exponential tilting was rejected
during design because convex weights cannot extrapolate outside the keys' convex hull.
The estimation component follows [Parallax](https://arxiv.org/abs/2605.29157).

Composition uses small, dimension-five orthogonal matrices. Four learned Householder factors form
each token transition `U_t`. Prefix products `P_t = U_t ... U_0` can distinguish order when the
learned transitions do not commute. The branch exposes the full prefix matrix and short ordered features of arity
one and two, mixed before a shared readout. The main experiments use independent-random factor
initialization and an initial branch scale of 0.1.

| Candidate | How the components interact | Registered concern |
|---|---|---|
| A: transported Parallax | Compose first; transport selected value blocks through `P_i P_j^T`, alongside ordinary Parallax and a direct matrix readout. | Extra value operations and interference with retrieval. |
| B: parallel Parallax and matrix state | Add an independently computed prefix/short-product branch to ordinary Parallax. | The inexpensive composition branch may contribute nothing useful to language. |
| C: attention-conditioned matrix state | Compute Parallax first, then generate transitions from the token plus a gated attention summary. | Coupling may make the state representation harder to learn. |

B was favored before the main results for simplicity and cost. These are bounded combination
claims: [PaTH](https://arxiv.org/abs/2505.16381) already uses accumulated input-dependent
Householder transformations in attention. Its
[KV-cache discussion](https://arxiv.org/html/2505.16381v2#S3) also proposes extending the update
mechanism to value vectors; A explores that direction together with Parallax correction and an
explicit matrix readout. This is a proposed PaTH direction, not an evaluated extension in that paper.
[Lie-Algebra Attention](https://arxiv.org/abs/2606.20547) and
[Non-Commutative Words](https://arxiv.org/abs/2608.29314) also preclude broad claims to invent
group-valued tokens or ordered matrix representations. Our contribution, if supported, is the
measured behavior of these particular combinations.

Relative to convolved Parallax, B adds 1,113,552 parameters: 2.393% of total parameters or 5.427%
of non-embedding parameters. Its nominal arithmetic per token increases by 2.317%. It is a small
addition to that baseline, but neither free nor guaranteed to learn a useful computation.

The recurrent controls are canonical one-update Gated DeltaNet, with update strength in `(0,1)`,
and a four-update gated DeltaProduct extension with strength in `(0,2)`. Both include short
convolution, learned decay, normalized queries/keys and an output gate. They implement the
mechanisms of [Gated DeltaNet](https://arxiv.org/abs/2412.06464) and
[DeltaProduct](https://arxiv.org/abs/2502.10297) inside the common project backbone and optimizer;
they do not reproduce the papers' complete training recipes. A separate full-matrix prefix reader
provides a strong word-tracking control when query-read recurrent models fail to learn that task.

The development failures mattered. After 1,000 updates, raw softmax, Parallax and all three
candidates remained near 10% on separated-key/value MQAR, while Gated DeltaNet reached 99.69%.
Extending raw softmax to 6,000 updates at two rates produced only 10.07% and 10.62%, close to the
key-blind value-histogram oracle's 10.376%. Matching that control would not demonstrate retrieval.
A prospectively registered, common width-three causal QKV convolution resolved this observed
binding plateau: the convolved softmax pilots reached 100%. This known modification follows the
short-convolution precedent in [Primer](https://arxiv.org/abs/2109.08668). It is shared by
softmax, Parallax and A/B/C in both the main diagnostics and language comparison. Raw softmax
remains an additional language control.

The first word pilots also failed, including the new prefix control. A registered initialization
comparison found that random factors reached 95.19% A5 validation accuracy at 1,000 updates;
paired-identity factors reached only 1.54% then, but also reached 100% by 4,000 updates.
Both final tests were 100%. Near identity, first-order prefix perturbations add, while
order-sensitive commutators enter at second order. That motivates the initialization hypothesis;
the experiment supports faster early learning, not impossibility under paired initialization.

Optimization remains fragile. The combined-layer S5 pilot gave A only 2.91% final-test accuracy,
while B/C reached 100%. In the subsequent matched-compute screen, A reached 100%, whereas C's
first-rate one-layer validation score fell to 64.70%. Audits found unchanged candidate equations,
initialization, optimizer and data generators. Complete schedules changed with compute matching,
and even an unchanged B schedule showed run variation. These reversals demonstrate sensitivity;
they do not isolate a causal explanation.

Stage 0 checked causality, literal matrix products and transported paths, reductions to the simpler
layers, finite gradients, and the exact affine-reproduction special case. The main diagnostic
configuration is width 128, batch 64 and Muon, with task-specific one- or two-layer models.
Each task/depth receives B's nominal compute at 6,000 updates; other arms receive proportionate
updates and complete schedules. Final validation uses 1,024 sequences and final test 2,048.

The six primary cells are two-layer MQAR and induction, plus A5/S5 word tracking at both depths.
Word inputs contain a BOS token and 16 uniform group elements; the target at each position is
the running product, classified among 60 or 120 group elements. The gate averages class recall
over positions 9–16, avoiding the easier short prefixes.
The registered tuning rule starts at rate .004 and allows one alternate only below 97% final
validation: .002 for words, .008 for retrieval. All 46 first-rate runs and 13 triggered alternates
completed. Every candidate and selected reference reached 100% validation in every cell.
C needed .002 on both S5 depths; B needed .002 on two-layer S5. References selected by validation
are convolved softmax for retrieval and the full-matrix prefix reader for all word cells.
These are selected seed-0 results, not independent confirmation.

| Candidate | Selected seed-0 validation | Independent seeds 1/2/3: written rule | Independent seeds 1/2/3: original code | Language eligibility |
|---|---|---|---|---|
| A | 100% in all six cells | Rejected: 14/18 cells pass | Rejected; candidate failures and reference-floor failures | Not eligible |
| B | 100% in all six cells | Passed: 100% in all 18 cells | Unconfirmed: reference floor | Eligible under written rule |
| C | 100% in all six cells | Rejected: 15/18 cells pass | Rejected; candidate failures and reference-floor failures | Not eligible |

The failed cells are all S5. The following are final second-half balanced test accuracies (%),
with a 95% absolute floor plus the registered reference margin:

| Candidate | Depth | Seed 1 | Seed 2 | Seed 3 |
|---|---:|---:|---:|---:|
| A | 1 | 5.459 | 100 | 13.438 |
| A | 2 | 100 | 1.657 | 90.726 |
| B | 1 | 100 | 100 | 100 |
| B | 2 | 100 | 100 | 100 |
| C | 1 | 100 | 99.634 | 100 |
| C | 2 | 3.253 | 6.776 | 1.590 |

All other candidate confirmation cells pass. No failure is due solely to the relative margin.
The [complete confirmation artifact](results/beyond_stage1_confirmation.json) audits every candidate
and reference result. These are learnability and reproducibility failures of the frozen recipes,
not proofs of insufficient expressivity or isolated causal effects of the coupling choices.

The [saved-curve analysis](results/beyond_stage1_learning_dynamics.json) finds no recorded
95%-accurate checkpoint in any of the seven failed runs. Six peak at no more than 13.57% late
validation accuracy. A two-layer seed 3 instead improves from 9.75% to 74.26% to 90.45% over
its last three evaluations. Final validation and test late accuracies agree within 0.272 percentage
points. These trajectories support a learning-dynamics explanation rather than an observed collapse
after success. Training accuracy and validation cross-entropy were not saved, so a formal
train–validation generalization gap cannot be measured. The
[word-confirmation figure](results/beyond_stage1_report/confirmation_test_words.png) also separates
easier all-position accuracy from the registered second-half measure.

A disclosed protocol discrepancy requires reporting both columns. The written gate required
candidate accuracy of at least 90% on retrieval or 95% on second-half word positions, and no more
than three percentage points below its reference. The preregistered executable selector additionally
required the reference itself to meet that absolute floor. This was discovered after first-rate
results. All prescribed alternates finished unchanged; both rules then selected exactly the same
candidates, rates and references.

Before any confirmation launch, commit `445048e487906265c99a135e08ccedea39a03230` registered
[Section 4.1](BEYOND.md#41-written-rule-reconciliation-before-independent-confirmation):
use the written rule prospectively and preserve the original executable outcome alongside it.
Missing, failed or nonfinite references cannot establish a pass. Independent confirmation made
this distinction material: the one-layer S5 prefix reference scored 6.624% at seed 1 and the
two-layer S5 reference scored 1.523% at seed 3; all other reference scores were 100%. B scored
100% in those cells and all its others. The [B confirmation artifact](results/beyond_stage1_b_confirmation.json)
records both outcomes. The
[strict selection](results/beyond_stage1_selection_strict.json) remains immutable; the
[adapter](analysis/beyond_gate_reconciliation.py) checks the registration, original seal and
unchanged selection identities. Any future result passing only the reconciled rule must be labeled
accordingly. All 18 candidate confirmation cells must pass before language.

The completed descriptive map separates word tracking from more general composition. On causal
ordered Match-3, all arms at one or two layers score 73.86–74.42% balanced accuracy. On the same
test seed, the independently calibrated position-only rule optimized for balanced accuracy scores
74.78%; the rule optimized for ordinary accuracy scores 74.42%, matching the prefix control's
aggregate score at both depths ([baseline artifact](results/beyond_match3_position_baseline.json)).
No model improves on these controls. The previously reported 74.85% baseline pools four seeds.
Aggregate agreement is compatible with a position shortcut, but does not establish identical predictions.

This target asks whether any earlier ordered pair completes an identity relation with the current
element. The shared short-product branch exposes the current matrix times an average of individual
past matrices; its full prefix multiplies every intervening token. Neither explicitly exposes the
histogram of arbitrary earlier ordered-pair products that would support direct identity lookup. A transports
along contiguous paths, while C and deeper layers can learn contextual interactions. This structural
distinction motivates a learnability hypothesis; it does not prove an expressivity impossibility.
Even an explicit sum of triple products would need a readout that distinguishes identity matches
from the other summed terms. BOS and causal boundaries also reveal position despite `pos=0`.

All arms learn the affine regression problem far better than predicting the mean context value
(MSE 12.21277). At the registered compute budget, the combined layers do not lead this probe:

| Arm | One-layer test MSE | Two-layer test MSE |
|---|---:|---:|
| Convolved softmax | 0.020527 | 0.004219 |
| Convolved Parallax | 0.017094 | 0.001722 |
| A | 0.016037 | 0.003109 |
| B | 0.019783 | 0.002787 |
| C | 0.017419 | 0.002596 |
| Prefix | 0.066160 | 0.019530 |
| Gated DeltaNet | 0.004653 | 0.002154 |
| Gated DeltaProduct | 0.014731 | 0.008264 |
| LLA, optional explicit local-linear control | 0.000664 | 0.001888 |

B's mean MSE is 3.63% below softmax at one layer and 33.94% below it at two layers. It therefore
misses the registered descriptive 10% improvement target at one layer and clears it at two.
That target was informative, not an advancement gate.

These are descriptive seed-0 means over 2,048 test examples. The raw results retain standard errors
of squared error; those measure conditional test uncertainty, not training-seed variation. The
ranking alone establishes neither statistical superiority nor an isolated effect of composition.
The one-layer LLA result also shows why a learnable precision correction must not be described as
guaranteed recovery of an affine function after training. The
[affine-probe figure](results/beyond_stage1_report/descriptive_test_regression.png) displays the
reported conditional uncertainty.

The frozen [language plan](results/beyond_language_plan.json) tests B against five controls using
a single FineWeb-Edu shard, GPT-2 tokens, six layers of width
512, context 512, batch 64, BF16 and Muon. The fixed binaries contain 744.58M training tokens and
7.51M held-out tokens. Their full [fingerprints](results/beyond_language_planning/dataset.json) were
recorded before quality runs. Current preparation code specifies a document-level 99:1 split;
the original dataset revision and tokenizer build were not recorded. Every included arm receives three fresh approximately 100M-token
rate trials at {.002, .004, .008}. Only final unrounded validation loss selects the rate.
A candidate with no valid trial remains unconfirmed while other viable candidates continue;
all five controls are mandatory. Such failures never reduce the frozen compute allowances.
Fresh seeds 1/2/3 use candidate schedules set by the most expensive Stage-1-qualified candidate's
approximately 400M-token nominal budget when the plan is frozen, even if that candidate later has
no valid tuning trial. Before any language quality results, a conservative
allowance gives each control enough complete updates to cover every candidate under four declared
arithmetic conventions, including dense attention and whole-block recomputation estimates. These
intentional additions are reported separately from whole-update rounding. Final evaluation uses a
fresh fixed draw of 1,024 windows (seed 5678), while rate selection uses seed 1234. Both sample the
same validation file; windows may overlap within and between draws. This is neither token-disjoint
nor document-disjoint evaluation. Sequence-level uncertainty is conditional on the trained model
and may understate uncertainty when windows overlap.

All 18 tuning trials completed without numerical or execution failures. Final raw validation
losses in nats/token are shown below; bold entries select rates. These are approximately
100M-token runs at equal tokens, not the final compute-matched comparison.

| Arm | Rate .002 | Rate .004 | Rate .008 |
|---|---:|---:|---:|
| Raw softmax | 3.964051 | 3.926675 | **3.916598** |
| Convolved softmax | 3.941346 | 3.905269 | **3.897961** |
| Convolved Parallax | 3.908794 | 3.875718 | **3.871201** |
| B | 3.960137 | 3.922886 | **3.922844** |
| Gated DeltaNet, one update | 3.914880 | 3.868362 | **3.855246** |
| Gated DeltaProduct, four updates | 3.917680 | 3.860795 | **3.840066** |

Every selected rate is at the upper grid boundary. The preregistered policy prohibits extension,
so these results establish neither a global learning-rate optimum nor the final loss ordering.
B's .008 advantage over .004 is only 0.000043 nats/token; the deterministic selector uses the
unrounded means without treating this as a significant difference. The
[sealed selection](results/beyond_language_selection.json) retains every trial and its provenance.

The allocation is fixed before language results. Parameter counts include tied token embeddings;
the non-embedding count excludes both token and positional embeddings. Historical references to
the project's “19M” baseline mean non-embedding parameters. Parameter counts are not matched.
Planned tokens below are per final seed and will be checked against completed-run counters.

| Arm | Total parameters | Non-embedding parameters | Final updates | Planned tokens |
|---|---:|---:|---:|---:|
| Raw softmax | 44,933,120 | 18,915,328 | 13,540 | 443,678,720 |
| Convolved softmax | 44,960,768 | 18,942,976 | 13,531 | 443,383,808 |
| Convolved Parallax | 46,536,704 | 20,518,912 | 12,533 | 410,681,344 |
| B | 47,650,256 | 21,632,464 | 12,207 | 399,998,976 |
| Gated DeltaNet, one update | 48,157,280 | 22,139,488 | 13,105 | 429,424,640 |
| Gated DeltaProduct, four updates | 58,930,784 | 32,912,992 | 10,277 | 336,756,736 |

The four planned modeled-work totals, in units of `10^17` operations per final run, are:

| Arm | Nominal | Nominal + recomputation | Source upper | Source upper + recomputation |
|---|---:|---:|---:|---:|
| Raw softmax | 1.230855 | 1.412596 | 1.273460 | 1.469403 |
| Convolved softmax | 1.230773 | 1.412637 | 1.273349 | 1.469407 |
| Convolved Parallax | 1.218153 | 1.412657 | 1.257967 | 1.465742 |
| B | 1.213956 | 1.412564 | 1.252735 | 1.464269 |
| Gated DeltaNet, one update | 1.264354 | 1.464277 | 1.264354 | 1.464277 |
| Gated DeltaProduct, four updates | 1.252841 | 1.495962 | 1.252841 | 1.495962 |

These are analytic sensitivity conventions, not measured hardware operations. Their definitions
and exact, unrounded counts are in the frozen plan. All controls meet or exceed B in every column.

| Arm | Final loss, seed 1 | Seed 2 | Seed 3 |
|---|---|---|---|
| Raw softmax | Pending | Pending | Pending |
| Convolved softmax | Pending | Pending | Pending |
| Convolved Parallax | Pending | Pending | Pending |
| Gated DeltaNet, one update | Pending | Pending | Pending |
| Gated DeltaProduct, four updates | Pending | Pending | Pending |
| B | Pending | Pending | Pending |

For each seed, the headline requires candidate loss at most 99% of the better raw/convolved
softmax loss, and no higher than the better Gated DeltaNet/DeltaProduct loss. All three seeds and
the diagnostic gates are required. Convolved Parallax tests whether composition adds value beyond
the estimation component. Component-removal evaluations use identical final samples; they measure
sensitivity in a trained model, not the causal effect of retraining without that component.
Three successful seeds alone are not conventional statistical significance.

For B, composition ablation removes all three matrix sectors together, including their readout
bias. It does not isolate full-prefix memory or noncommutativity. The reported
`composition_over_content` and `matrix_over_content` are identical ratios of whole-branch RMS
to projected content RMS; `precision_over_content` measures the projected correction's RMS
relative to the corrected content output. They are activation measurements, not importance scores
or estimation accuracy. The separate convP `cor` statistic uses a different normalization and is
not directly comparable. Transition and adjacent-commutator statistics are unnormalized Frobenius
norms; random initialization already gives nonidentity, noncommuting transitions. Activity uses
only four validation sequences, with no uncertainty estimate. Learned sector coefficients are
signed and unconstrained; their magnitudes are affected by readout rescaling and cancellation.

Equal nominal FLOPs are not equal runtime. The analytic convention counts added projections,
scans, convolutions and transport, but excludes optimizer and rematerialization work. Attention
is charged under an ideal causal triangular
convention even though the JAX implementation materializes dense scores; the registered Parallax
count includes two value passes although corrected weights can combine them. Thus the headline
budget is an algorithmic convention, not a measurement of executed GPU arithmetic. The prospective
[control allowance](BEYOND.md#5-main-language-registration-before-quality-sweeps) covers each candidate's
modeled work under nominal, nominal-plus-recomputation, source-dense upper and source-dense-plus-
recomputation conventions. It charges A without compiler-sharing credit and adds updates to all
controls as needed. A positive result would therefore beat controls given at least its modeled
work under all four conventions. A negative result would not prove inferiority at an exact equal-
compute point. Additional control updates also increase data exposure. Recurrent
chunking preserves the mathematical recurrence, within tested floating-point tolerances, and its
extra Gram matrices, triangular solves and backward work are charged. Runtime-only tests selected
chunk 32: GDN1/DP4 took .153/.361 seconds per update versus .439/1.060 for their best unrolled
versions. These engineering measurements are not language-quality results.

The hard caps are **$25 diagnostic screen, $100 language, $25 development, $150 total**, including
pilots, failures and reservations. The completed screen cost estimate is $21.597644; language timing
pilots are $2.326004 and development is $4.758580, totaling $28.682228 before language quality runs.
The frozen B-only language comparison forecasts $66.657532 including its timing pilots; its summed
timeout maximum is $86.258104. These are resource estimates, not invoice totals.
The [ledger](results/beyond_budget.json), immutable manifests and [registration log](BEYOND.md)
remain authoritative. Budget exhaustion leaves missing runs explicitly unconfirmed.

The final report must replace the pending entries with verified results, both gate policies,
per-seed losses and uncertainty, compute/runtime accounting, and component ablations. A negative
answer remains informative: the components may coexist and solve synthetic tasks yet fail to
improve language at this scale. Neither success nor failure here would establish a universal winner.
