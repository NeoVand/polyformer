# Beyond softmax and matrix-state RNNs — working report

**Experiments are running. This is not the final result.** Evidence snapshot: 20 October 2026,
15:01 UTC. B passes the prospectively reconciled written Stage-1 rule with **100% final test
accuracy in all 18 independent cells**. Its original-code outcome is **unconfirmed** because two
standalone reference runs failed that code's additional accuracy floor. A and C's independent
confirmations are pending; all three candidates reached 100% selected seed-0 validation in the
six primary cells. The descriptive grid is complete, and no language quality sweep has begun.
These results establish successful synthetic-task learning in this regime, not a language advantage.

The question is whether one affordable layer can combine content selection, improved local
estimation and order-sensitive composition, then beat both softmax and modern matrix-state RNNs
at equal nominal training compute. Earlier project studies motivated these capabilities separately;
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
each token transition `U_t`; prefix products `P_t = U_t ... U_0` retain order because the factors
need not commute. The branch exposes the full prefix matrix and short ordered features of arity
one and two, mixed before a shared readout. The main experiments use independent-random factor
initialization and an initial branch scale of 0.1.

| Candidate | How the components interact | Registered concern |
|---|---|---|
| A: transported Parallax | Compose first; transport selected value blocks through `P_i P_j^T`, alongside ordinary Parallax and a direct matrix readout. | Extra value operations and interference with retrieval. |
| B: parallel Parallax and matrix state | Add an independently computed prefix/short-product branch to ordinary Parallax. | The inexpensive composition branch may contribute nothing useful to language. |
| C: attention-conditioned matrix state | Compute Parallax first, then generate transitions from the token plus a gated attention summary. | Coupling may make the state representation harder to learn. |

B was favored before the main results for simplicity and cost. These are bounded combination
claims: [PaTH](https://arxiv.org/abs/2505.16381) already uses accumulated input-dependent
Householder transformations in attention;
[Lie-Algebra Attention](https://arxiv.org/abs/2606.20547) and
[Non-Commutative Words](https://arxiv.org/abs/2608.29314) also preclude broad claims to invent
group-valued tokens or ordered matrix representations. Our contribution, if supported, is the
measured behavior of these particular combinations.

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
The registered tuning rule starts at rate .004 and allows one alternate only below 97% final
validation: .002 for words, .008 for retrieval. All 46 first-rate runs and 13 triggered alternates
completed. Every candidate and selected reference reached 100% validation in every cell.
C needed .002 on both S5 depths; B needed .002 on two-layer S5. References selected by validation
are convolved softmax for retrieval and the full-matrix prefix reader for all word cells.
These are selected seed-0 results, not independent confirmation.

| Candidate | Selected seed-0 validation | Independent seeds 1/2/3: written rule | Independent seeds 1/2/3: original code | Language eligibility |
|---|---|---|---|---|
| A | 100% in all six cells | Pending | Unconfirmed: reference floor | Pending |
| B | 100% in all six cells | Passed: 100% in all 18 cells | Unconfirmed: reference floor | Eligible under written rule |
| C | 100% in all six cells | Pending | Unconfirmed: reference floor | Pending |

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
accordingly. All 18 independent candidate cells must pass before language.

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

These are descriptive seed-0 means over 2,048 test examples. The raw results retain standard errors
of squared error; those measure conditional test uncertainty, not training-seed variation. The
ranking alone establishes neither statistical superiority nor an isolated effect of composition.

Language, if candidates qualify, uses a single FineWeb-Edu shard, GPT-2 tokens, six layers of width
512, context 512, batch 64, BF16 and Muon. The fixed binaries contain 744.58M training tokens and
7.51M held-out tokens. Their full [fingerprints](results/beyond_language_planning/dataset.json) were
recorded before quality runs. Current preparation code specifies a document-level 99:1 split;
the original dataset revision and tokenizer build were not recorded. Every included arm receives three fresh approximately 100M-token
rate trials at {.002, .004, .008}. Only final unrounded validation loss selects the rate.
A candidate with no valid trial remains unconfirmed while other viable candidates continue;
all five controls are mandatory. Such failures never reduce the frozen compute allowances.
Fresh seeds 1/2/3 use candidate schedules set by the most expensive surviving candidate's
approximately 400M-token nominal budget. Before any language quality results, a conservative
allowance gives each control enough complete updates to cover every candidate under four declared
arithmetic conventions, including dense attention and whole-block recomputation estimates. These
intentional additions are reported separately from whole-update rounding. Final evaluation uses 1,024 fixed held-out sequences,
separate from tuning samples but drawn from the same validation corpus.

| Arm | Final loss, seed 1 | Seed 2 | Seed 3 | Parameters, tokens, runtime and cost |
|---|---|---|---|---|
| Raw softmax | Pending | Pending | Pending | Pending |
| Convolved softmax | Pending | Pending | Pending | Pending |
| Convolved Parallax | Pending | Pending | Pending | Pending |
| Gated DeltaNet, one update | Pending | Pending | Pending | Pending |
| Gated DeltaProduct, four updates | Pending | Pending | Pending | Pending |
| A / B / C, only if confirmed | Pending | Pending | Pending | Pending |

For each seed, the headline requires candidate loss at most 99% of the better raw/convolved
softmax loss, and no higher than the better Gated DeltaNet/DeltaProduct loss. All three seeds and
the diagnostic gates are required. Convolved Parallax tests whether composition adds value beyond
the estimation component. Component-removal evaluations use identical final samples; they measure
sensitivity in a trained model, not the causal effect of retraining without that component.
Three successful seeds alone are not conventional statistical significance.

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
pilots, failures and reservations. Before confirmation launches, conservative settled estimates were
$9.528/$2.326/$4.759 respectively, totaling $16.613; these are estimates, not invoice totals.
The [ledger](results/beyond_budget.json), immutable manifests and [registration log](BEYOND.md)
remain authoritative. Budget exhaustion leaves missing runs explicitly unconfirmed.

The final report must replace the pending entries with verified results, both gate policies,
per-seed losses and uncertainty, compute/runtime accounting, and component ablations. A negative
answer remains informative: the components may coexist and solve synthetic tasks yet fail to
improve language at this scale. Neither success nor failure here would establish a universal winner.
