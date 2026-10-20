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
- 2026-10-20 12:50 UTC — Read the brief and began independent prior-art, diagnostic, and language-harness
  audits. Working only in this worktree; no paid jobs launched. Baseline commit `99084c7`. Modal authentication
  and the existing tokenized FineWeb-Edu volume are available. Local test environment is
  `/tmp/beyond-venv` (JAX 0.12.0, optax 0.2.8).
- 2026-10-20 12:55 UTC — Designs frozen below before implementation/training. Rejected positive-only
  exponential tilting as a general linear-precision mechanism: a convex combination cannot extrapolate
  beyond the keys' convex hull. Existing diagnostic retrieval controls were near chance; existing noncausal
  group Match-3 cannot be silently reused in a causal language layer. These are design-stage findings,
  not post-result gate changes. Spend to date: $0.
- 2026-10-20 13:02 UTC — Stage-0 implementation and task checks pass. Before any paid experiment,
  moved sector mixing before the shared matrix readout, reducing its three projections to one. Tightened
  the recurrent control to the reference implementation's rectangular state (key width 0.75D,
  value width 1.5D), learned exponential/softplus decay with published timescale initialization,
  causal convolution and output gate. Timescales are excluded from weight decay. Independent audits
  caught and corrected a triangular-versus-dense attention FLOP mismatch before any comparison.
  Existing LOCAL.md tests still pass. No paid jobs launched.
- 2026-10-20 13:05 UTC — Pilot manifests committed at `faf69bd` (implementation/predictions `6d117b9`);
  both Modal apps launched, with four jobs each and eight total active slots. Diagnostic app
  `ap-Inpw8DO8kXIjSkhydLg9iq`; timing app `ap-vIIocj6JAVowdQC2DuEMqv`. Local launch logs:
  `/tmp/beyond-pilot-diag.log`, `/tmp/beyond-pilot-lm.log`. Durable worker logs/results are on
  `polyformer-beyond-runs`; local ledger `results/beyond_budget.json`. All 31 jobs have an aggregate
  maximum resource reservation of $8.634; results are pending.
- 2026-10-20 13:12 UTC — All seven language timing runs completed with finite losses; 50-to-100-update
  times are S 0.082 s, P 0.098 s, A 0.152 s, B/C 0.114 s, GDN1 0.626 s (DP4 to be tabulated).
  This motivates one common confirmation FLOP budget rather than repeated nearly identical recurrent
  controls; any final amendment will be committed before quality sweeps. Diagnostic pilots are ongoing.
  At 1,000 updates, small MQAR scores are S 10.07%, P 9.96%, A/B/C 9.72/9.58/9.56%,
  GDN1 99.69%, prefix 0.54%. The attention controls have not learned binding yet; the recurrent control
  has a causal convolution. Before freezing the screen, register a control-learnability extension below.
- 2026-10-20 13:20 UTC — The 24 diagnostic timing pilots are complete. All one-layer class-word arms
  remain near chance at 1,000 updates; this includes the new prefix control, so there is no demonstrated
  state-learning positive control in the common backbone yet. Softmax's 6,000-update MQAR tests give
  10.07% / 10.62% at rates .004 / .008; induction at .004 gives 100% (the .008 job is pending).
  The exact validation-set key-blind value-histogram oracle is 10.376%, loss 2.69364 nats; the two
  softmax training losses are 2.70145 / 2.69968. This supports a binding plateau, not successful retrieval.
  DP4's language time is 1.442 seconds/update. Conservative settled-plus-reserved estimate is $4.88.
  Register narrow positive-control and runtime tests below before launching them. Added explicit common
  FLOP targets to avoid inheriting an arm's recurrent microstep count when pricing its peers; fixed a
  floating-point rounding issue that gave the unmatched prefix pilots 999 rather than 1,000 steps.
  Added final checkpoint persistence and same-sample final component ablations for later language runs.
- 2026-10-20 13:22 UTC — The remaining induction control also reaches 100%. All 35 initial jobs are
  complete with finite outputs; conservative settled estimate $4.726 (screen $2.400, language $2.326).
- 2026-10-20 13:24 UTC — Word controls and recurrent runtime tests launched from immutable manifests
  committed at `75dc81a`, predictions/implementation `cf2b32f`. Launch logs are
  `/tmp/beyond-word-learn.log` and `/tmp/beyond-runtime.log`. Their uploaded sources remain fixed.
  Added an optional common QKV convolution after the raw-MQAR binding failure; register its narrow
  control pilot below. This is an explicit architecture refinement, not a replacement retrieval task.
- 2026-10-20 13:27 UTC — The random-initialized prefix reader reaches A5 second-half balanced
  validation accuracy 95.19%, 98.83%, 99.72%, 100%, 100%, 100% at successive 1,000-update marks;
  final independent-test accuracy is 100%. Paired initialization and the historical control are
  still pending. This supports testing the random initialization in all three candidates, before
  freezing the main screen. The shared-convolution implementation passes causal, reduction, gradient,
  shared-initialization and exact-cost checks; the legacy LOCAL.md test suite still passes.
- 2026-10-20 13:34 UTC — Matched A5 controls complete: paired initialization scores 1.54% at update
  1,000, 99.11% at 2,000, then 100% by 4,000; random starts at 95.19% at 1,000 and also reaches
  100%. Both final independent tests are 100%. Thus random initialization speeds early learning here;
  paired identity is not incapable of learning. Historical holonomy reproduces 100%, also at length 64.
  All six recurrent runtime tests complete: GDN1 unroll 1/4/16 is .626/.439/.477 s/update;
  DP4 is 1.439/1.060/1.249. Unroll 4 wins for both, but DP4 remains too slow for an affordable
  full-budget comparison. An exact chunked-recurrence prototype is being checked offline, with its
  additional arithmetic counted explicitly before any benchmark. Development settled estimate $3.035.
  Convolution and combined-layer pilots launched from `45f8895` (predictions `5c706af`); logs
  `/tmp/beyond-conv-learn.log` and `/tmp/beyond-combined-learn.log`. Current conservative total,
  including outstanding reservations: $9.059.
- 2026-10-20 13:44 UTC — Combined one-layer pilots complete: A/B/C all score 100% A5 test;
  S5 scores are A 2.91%, B 100%, C 100%, standalone prefix 99.95%. Both convolved two-layer
  softmax MQAR controls (.004/.008) score 100% validation and test, resolving the observed binding
  plateau in this common backbone. The remaining one-layer/induction convolution controls are pending.
  L4 capacity queues explain their elapsed launch delay; subprocess runtimes remain about two minutes.
  The independently calibrated position-only causal Match-3 baseline scores 74.85% balanced test
  accuracy; report this alongside model scores rather than equating any above-chance result with
  learned composition.
- 2026-10-20 13:44 UTC — GPU chunk proof passes all 20 cases: worst output/final-state absolute
  errors 8.01e-5 / 1.03e-4; worst input-VJP absolute error .00470 and relative L2 1.45e-5, within
  preregistered tolerances. Timing selects chunk 32 for both variants: GDN1 .153 s/update, DP4 .361,
  versus best unrolled .439 / 1.060. Chunk-16 times are .169 / .439. All four timing runs are finite.
  This now makes full three-seed language comparisons against **both** modern recurrent variants
  affordable, removing the need to select only one from short runs. The final language registration
  will freeze that stronger comparison before quality sweeps. Development settled estimate $4.759.


- 2026-10-20 13:48 UTC — All 61 development jobs are complete. Every convolved softmax retrieval
  pilot scores 100% validation/test, including one-layer MQAR at both rates and two-layer induction.
  Settled conservative estimates: screen $3.737, language $2.326, development $4.759, total $10.821.
  Freeze the main diagnostic registration below and its deterministic planner: 46 primary jobs,
  validation-triggered alternate rates, independent seeds 1/2/3, and 48 descriptive cells.
  Planner self-tests cover 18 invariants; all 96 arm/task/depth compute counts were independently
  checked. JSON reporting now preserves diagnostic component parameters and the full language config;
  these additions do not change training. No main diagnostic result has been observed.


- 2026-10-20 13:54 UTC — Main diagnostic primary grid launched from manifest commit `62fd24d`,
  registration/source commit `c65001b`, app `ap-OSAE6blVW7QHUfKKdJntWb`, eight concurrent L4 jobs;
  launch log `/tmp/beyond-stage1-initial.log`. First completed results show schedule sensitivity:
  A now reaches 100% one-layer S5 validation under its matched-compute schedule, while C reaches
  64.70% and the longer-budget prefix control 9.73%. These trigger only the registered decisions;
  no architecture changes follow. All six cells and needed alternate rates remain required.
  Language registration below is written before any quality sweep: independent seeds 1/2/3,
  three fresh rates for every arm, both raw/convolved softmax and both modern RNN controls.


- 2026-10-20 14:01 UTC — All three candidates reach 100% seed-0 two-layer MQAR validation;
  GDN1/DP4 reach 99.976%/99.927%. One-layer word reversals were audited against the pilot:
  candidate paths, optimizer, initialization and generators are unchanged; compute matching changes
  A's schedule substantially and C's slightly, and even B's identical schedule shows some run variation.
  The evidence establishes optimization/run sensitivity, not an isolated causal effect of the schedule.
  The fixed descriptive manifest is committed at `dc6029a`; it remains queued behind primary selection
  and B/reference confirmations. A strict artifact-integrity and final-test confirmation evaluator is
  saved under `analysis/`, outside the immutable worker sources.
- 2026-10-20 14:01 UTC — The language reporting-only patch and portable CPU proof are saved under
  `results/beyond_reporting_patch/` and `analysis/test_beyond_lm_reporting.py`. Reconstructed old/new
  CLI runs give bitwise-identical final GPT/B parameters and unchanged legacy rounded metrics;
  direct GPT/B/C forward/gradient/update checks also agree. New raw scalar versus legacy reduction
  differences are at most 9.91e-8, and raw scalar versus sequence-mean differences at most 3.47e-7.
  The patch is **not applied** to the frozen diagnostic worker sources; apply and record its source
  bridge only after Stage 1 finishes. No language quality sweep has begun.


- 2026-10-20 14:08 UTC — All 46 primary jobs complete with no execution errors; integrity checks
  pass. A scores 100% validation in all six cells. B scores 100% except two-layer S5 (0.807%);
  C scores 100% except one-/two-layer S5 (64.70%/3.531%). Thirteen word-cell alternates at .002
  are mechanically required; no retrieval alternate is triggered. Screen settled estimate is $8.319
  including pilots; total settled estimate $15.403. The first-rate results do not establish confirmation.
- 2026-10-20 14:08 UTC — Audit found a written-rule/executable discrepancy, missed in the earlier
  review: section 4 requires the **candidate** to reach 90%/95% and be within 3 points below its
  selected reference. The frozen selector additionally requires the **reference** to reach 90%/95%,
  yielding `no_positive_control` otherwise. This extra restriction exists in preregistered code but
  not in the written gate or original brief. The absolute candidate threshold already prevents a
  chance-level match from passing. Finish every prescribed alternate unchanged before deciding
  whether this discrepancy is material. Preserve the original executable outcome. Any reconciliation
  must be explicit, uniform across A/B/C and all cells, committed before untouched confirmation
  seeds, and reported alongside the original-code outcome; it cannot retroactively make that code's
  gate pass. No missing/nonfinite reference may become an easy win, and reference selection, rates,
  candidate thresholds, margins, budgets and confirmation seeds must remain unchanged.


- 2026-10-20 14:12 UTC — Thirteen prescribed alternates launched from manifest commit `7d7977a`
  (prior log/registration `1a275f8`), app `ap-5dAW0tONr50SFioZAgQGVQ`, eight L4 slots,
  local launch log `/tmp/beyond-stage1-alternate.log`. Architecture/training sources remain frozen.
  Portable Stage-2 planning tools and budget/provenance documentation are now saved in `analysis/`
  and `results/beyond_language_planning/`; all 20 tests and four path-portability checks pass.
  These are offline preparation only: no language quality job has been launched.


- 2026-10-20 14:15 UTC — All 13 alternates complete without errors; the integrity audit accepts all
  59 main tuning runs. Lower rate .002 brings C's one-/two-layer S5, B's two-layer S5, and both S5
  prefix controls to 100% validation. Every candidate and selected reference now scores 100% in
  every primary cell. `results/beyond_stage1_selection_strict.json` preserves the original executable
  selection. Register section 4.1 before **any** confirmation call: reconcile the extra reference-floor
  condition with the written rule and report both policies. No seed-0 decision, rate or reference
  changes, and no confirmation outcome has been observed. The matrix RNN word failures remain in
  the record; they do not imply an expressivity impossibility.


- 2026-10-20 14:18 UTC — The reconciled selection is sealed at commit `79e7aad`; its strict and
  written-rule seed-0 survivors are identically B, C, A. Independent shared-reference and B runs
  (36 jobs) launched from manifest commit `a4bf178`, app `ap-B2mThiC800wdEqxhimaAYg`, log
  `/tmp/beyond-stage1-references-b.log`, eight concurrent L4 slots. No additional tuning is allowed.
  C/A's 36 confirmation configurations are also frozen, to run after the descriptive grid in the
  registered order. The dual-policy evaluator passes 17 checks; the report builder passes seven
  and preserves unrounded decisions, validation/test separation and original-code outcomes.
  Before these confirmations, conservative settled totals were screen $9.528, language $2.326,
  development $4.759, total $16.613. Root worker sources remain unchanged.


- 2026-10-20 14:26 UTC — Saved the working report in `BEYOND_REPORT.md`, with all pending outcomes
  explicitly marked. The language planner now verifies the registered gate reconciliation and pins
  its adapter; 24 CPU tests plus four portability checks pass. A fresh source-level FLOP sensitivity
  audit finds approximately 3.0–3.2% more candidate arithmetic than RNN arithmetic at the nominal
  matched budget, and approximately 0.25–0.45% less than softmax: dense score products and combined
  corrected-weight value products differ from the legacy analytic convention. Exact GPU arithmetic
  has not been measured. The audit is in `results/beyond_language_planning/proof.json`; no counters,
  worker sources, training schedules or quality jobs changed. Resolve this before freezing language.


- 2026-10-20 14:33 UTC — Ten of 36 reference/B confirmations are complete. One-layer S5 prefix
  reference seed 1 scores 6.624% second-half balanced test accuracy at its frozen .002 rate;
  seeds 2/3 score 100%. Thus the original executable reference-floor restriction is material in
  confirmation, and must be reported beside the prospectively reconciled written rule. No candidate
  is yet confirmed, no rates change, and the failed reference is retained. Several early Modal
  container starts logged broken pipes, but API call graphs showed pending allocation, not failed
  model executions; the original calls continue without duplicate dispatch or changed hardware.


- 2026-10-20 14:40 UTC — Prospectively registered the language control allowance in Section 5,
  policy `3a340829e3fa07d6808280c240992af63283088ac92a3d68d7935cb7822d0991`.
  Candidate schedules and all sweeps stay fixed. Each of five comparators receives the minimum
  whole updates needed to cover every included candidate under four declared arithmetic models:
  nominal, nominal plus block recomputation, source-dense upper (no A sharing credit), and that
  source estimate plus recomputation. Independent audits verify all seven survivor subsets,
  240 dominance inequalities and 35 minimal ceilings; planner tests pass. Forecasts are $77.09
  with B/C or $94.26 with A/B/C, within the unchanged $100 cap subject to rolling settlements.
  This is not measured GPU-FLOP equality; report all four estimates, tokens and runtime. No language
  quality results have been observed. The final language reporter passes 26 tests, preserves both
  Stage-1 policies, and distinguishes training-seed variation from conditional sequence uncertainty.


- 2026-10-20 14:41 UTC — All 36 shared-reference/B confirmations complete without execution
  errors. B scores **100% final test in all 18 primary cells** and passes the prospectively reconciled
  written rule. Its original-code outcome is **unconfirmed**, because the prefix reference scores
  6.624% on S5 L1 seed 1 and 1.523% on S5 L2 seed 3; all other references score 100%.
  Both outcomes are sealed in `results/beyond_stage1_b_confirmation.json`. No rates or recipes
  change. These confirmations cost $3.449 conservatively; settled screen total is $12.978.
  The 48 descriptive runs launched from the previously frozen `dc6029a` manifest, app
  `ap-trSobOtETv1B8a00KYVTME`, log `/tmp/beyond-stage1-descriptive.log`, eight L4 slots.
  C/A confirmations remain queued afterward. Language accounting amendment is committed at
  `cfcd1bb`; all top-level diagnostic worker sources remain unchanged.


- 2026-10-20 14:49 UTC — Fingerprinted both existing language token binaries through Modal's
  local control-plane read API, without a Modal Function or GPU slot. Full SHA-256 evidence,
  exact byte/token counts, stable before/after metadata and explicit provenance gaps are saved in
  `results/beyond_language_planning/dataset.json`. The corpus is 744.583M training / 7.515M
  validation tokens. Bind this committed evidence into the language plan and rehash after the
  study. No dataset contents, worker source or training recipe changed; the original unpinned
  download revision and tokenizer build cannot be recovered retrospectively.


- 2026-10-20 14:58 UTC — Clarified language failure handling prospectively, before any quality
  trial. If only a candidate has no valid result across its three registered rates, keep every failure
  and mark it tuning-invalid/unconfirmed while continuing every viable candidate. All five controls
  remain mandatory; any control without a valid rate, or no viable candidate, stops the final grid.
  Original compute allocations and control allowances remain fixed even if the failed candidate
  set the budget. Identity/accounting contradictions stop for investigation rather than being
  classified as numerical failure. This policy changes no architecture, rate, gate or paid job.


- 2026-10-20 14:58 UTC — All 48 descriptive jobs completed without numerical/execution failures;
  all pass manifest/configuration/step/FLOP audits. Screen settled total is $17.691. C/A's 36
  frozen confirmations launched in app `ap-pNvJTjpGROnx7nXNNJyBOb`, log
  `/tmp/beyond-stage1-confirm-ca.log`, eight L4 slots. Match-3 scores span 73.863–74.418% balanced
  accuracy: no arm improves on the matched-test-seed position-only accuracy rule (74.4178%);
  the separately calibrated balanced-accuracy rule scores 74.7824% on that same seed. The earlier
  74.8455% value pools four test seeds and must not be confused with either matched-seed rule.
  Two-layer affine MSE is S .004219, P .001722, A/B/C .003109/.002787/.002596, GDN1 .002154,
  DP4 .008264, prefix .019530; the mean-value baseline is 12.212769. These are descriptive
  single-training-seed results, with per-example uncertainty retained, not additional gate choices.

- 2026-10-20 15:09 UTC — Committed candidate-local tuning failure handling and the completed
  descriptive results in `2e076e6`, before any language quality trial. C/A's first eight calls remain
  queued with no worker task IDs after approximately eleven minutes; no retry or replacement was
  dispatched. A read-only scientific review tightened the working report: 18 confirmation cells
  are six conditions across three seeds, final/tuning text windows are not token- or document-disjoint,
  and PaTH's proposed value-update direction is explicitly credited. No experimental rule changed.

- 2026-10-20 15:15 UTC — C's independent two-layer S5 confirmation failed the 95% threshold at
  seeds 1 and 2: balanced second-half test accuracy 3.252958465% and 6.776395185%, respectively
  (`7a10082a429e045e884c451b`, `1a94b1fef75adf22aa7c7992`). Both are completed, finite,
  identity/accounting-audited results, not numerical or infrastructure failures. C cannot advance
  under the registered all-cells rule. All remaining C/A jobs continue unchanged; complete
  confirmation classification will be sealed after the entire grid closes. B remains eligible.

- 2026-10-20 15:16 UTC — C's third two-layer S5 confirmation also failed: 1.590191013%
  balanced second-half test accuracy (`f42e9787dd8636906c637cb5`), again finite and integrity-valid.
  All three independent seeds fail this cell despite selected seed-0 validation reaching 100%.
  This establishes a reproducibility/learnability failure for the frozen recipe, not an expressivity
  impossibility or an isolated causal effect of attention conditioning.

- 2026-10-20 15:17 UTC — A also fails independent confirmation: one-layer S5 seeds 1 and 3
  score 5.458905638% and 13.43755079% balanced second-half test accuracy
  (`3baa01c6c5822fee57550bd8`, `971507305f6e63432d17232d`). These are finite, completed and
  identity/accounting-audited runs. C is now complete: its only below-floor cells are the three
  two-layer S5 seeds. B is the sole candidate that can advance; the remaining A jobs still run to
  preserve the complete registered record. No language job has launched and no recipe changed.

- 2026-10-20 15:23 UTC — All mandatory Stage-1 calls are closed and all 72 confirmation/reference
  results are integrity-audited. Final artifact `results/beyond_stage1_confirmation.json`, seal
  `7bf813f4960062be47dce620a45a417a85848e986406bec3e732ebe7c2fcb8be`: active written rule
  B passes 18/18 cells, A is rejected with 14/18, C rejected with 15/18. A additionally fails S5
  L2 seeds 2/3 at 1.656640750%/90.72641994%. There are no reference-gap-only failures.
  Under the original strict code A/C are rejected and B is unconfirmed because of the two reference
  floors. Screen settled cost is $21.414724. The optional, already-committed LLA regression pair
  fits even at its full $0.519542 reservation and launched in `ap-rybRGDHPKwzydAjW8NVdBt`.
  All worker sources remain frozen until that pair closes. B alone will enter language.

- 2026-10-20 15:28 UTC — All Stage-1 calls, including optional LLA, are closed; global active
  reservations are zero. The final integrity artifact audits all 181 main/confirmation/descriptive/
  optional results with no execution or numerical errors. Final screen settled estimate is
  $21.597644. LLA's one-/two-layer affine test MSE is .000663872/.001887549 (example SE
  .000078596/.000216912); these remain single-seed descriptive controls. Applied the previously
  committed, tested reporting-only `lm.py` patch after source freeze release. Its exact SHA is
  `d9cfad64cb8e4697b61549fdbea50efdaecc0f984f94baa0429cc7112a9aebff`; only reporting/evaluation
  paths changed, with unchanged training established by the saved Stage-0 proof. No language
  quality jobs have launched.

- 2026-10-20 15:30 UTC — Committed complete Stage-1 evidence and reporting patch in `c55c3bd`;
  committed source bridge `a8fcc9df1d7981dddcb7df9c048f2556a841ba85d0420d221fda743ce2070b39`
  in `e8eab2b`. The production verifier accepts the actual closure and exact reporting-only diff.
  Froze `results/beyond_language_plan.json`, seal
  `1c3aa0819d081dd233d289a0241e94b1141f4fae31ac8eff8cd2c8f046d3126e`, with survivor B and
  controls rawS/convS/convP/GDN1/DP4. The 18 rate trials each use 3,051 updates; final B uses
  12,207 updates (399,998,976 tokens). Control updates are 13,540/13,531/12,533/13,105/10,277.
  Nominal B target is 1.2139564225136e17 training FLOPs; all four work conventions are recorded.
  Language forecast is $66.657532 including pilots, aggregate timeout maximum $86.258104.
  All source, data, policy and evaluation identities are frozen before any quality launch.

- 2026-10-20 15:30 UTC — Committed the language plan in `d9a40cc` and all 18 tuning jobs in
  `294d42f` before launch. Started bounded app `ap-cdFQjRkHyLG01MwzArzPgZ` from
  `manifests/beyond_language_tuning.json`, log `/tmp/beyond-language-tuning.log`, at most eight
  H100 jobs globally. Root owns the launcher; the harness auditor monitors provenance and will
  create the immutable rate selection only after all 18 trials are terminal. No intermediate
  checkpoint or held-out result selects rates. Worker sources, planner and Section 5 remain frozen.

- 2026-10-20 15:34 UTC — Saved posthoc S5 learning-dynamics analysis at
  `results/beyond_stage1_learning_dynamics.json` (seal
  `e2f514c708b5caed8a8804182ced9640f43c777e987b41444a2716a2b6cf23d5`), using only existing
  curves from 24 runs. None of the seven failing A/C runs reached 95% at a recorded evaluation;
  six peaks are at most 13.5703%, while A L2 seed 3 improves to 90.4546% at the final update.
  Final validation/test late accuracies differ by at most .271869 percentage points. No observed
  success-then-collapse is established, and no formal train/validation gap can be calculated from
  the saved unequal metrics. This is descriptive interpretation, not checkpoint/rate selection or
  evidence that coupling alone caused failure. Language first-wave jobs are training without errors.

- 2026-10-20 15:37 UTC — Language tuning is 8/18 complete: all rawS/convS rates plus convP
  .002/.004. Every completed result passes the production source/configuration/accounting audit;
  no failures or rate selections. All completed curves have the exact eight scheduled evaluations,
  including final update 3,051. Eight calls are active and two remain undispatched. Settled costs
  plus active reservations total $43.261027 across all stages; this is a conservative estimate,
  not an invoice. Committing the completed-result snapshot while the unchanged grid continues.

- 2026-10-20 15:47 UTC — Language tuning is 15/18 complete, all valid: only the three DP4
  rates remain active. GDN1 wall times are approximately 559–561 seconds; all rates preserve the
  exact registered configuration and eight evaluation marks. No rates selected yet. The working
  report now explicitly evaluates the previously registered descriptive affine target: B reduces
  MSE relative to softmax by 3.6251% at one layer and 33.9387% at two, missing/clearing the
  informative 10% target respectively. This was never an advancement gate and changes no decision.

- 2026-10-20 16:04 UTC — All 18 language tuning trials completed and passed source, runtime,
  configuration, evaluation-mark and compute-accounting checks. The bounded launcher exited
  successfully; global active calls are zero. Production selection
  `results/beyond_language_selection.json` has seal
  `47689eb6ec2154b644fd106b3766499c943eaf43d3ff10579bb4d31065203541`.
  Every arm selects .008 from final raw validation loss: rawS 3.916597597,
  convS 3.897960927, convP 3.871201463, B 3.922843644, GDN1 3.855246149,
  DP4 3.840065871 nats/token. All rates lie at the registered grid edge; no extension is allowed.
  These short tuning runs do not satisfy or reject the final three-seed gate. All six arms remain
  required for fresh final seeds 1/2/3, using the frozen allocations and timeouts. Settled
  language estimate is $17.302019 including timing pilots; total across all stages $43.658243.
  The report now distinguishes total/non-embedding parameters and all four modeled-work totals.

- 2026-10-20 16:05 UTC — Committed rates and all tuning evidence in `4746245`, then exported and
  committed the complete six-arm seed-1 final block in `a2f7df6`. Launched app
  `ap-hPs6cmYAdk6j72xPal4Jta`, manifest `manifests/beyond_language_seed1.json`, local log
  `/tmp/beyond-language-seed1.log`. All six calls are active; no original arm is omitted.
  The harness auditor checks final artifacts, while a separate read-only audit will download
  checkpoints and fingerprint their bytes without deserialization. Later seed blocks remain
  conditional only on terminal completion of this block and the fixed budget checks, not its losses.
  Current settled-plus-reserved estimate is $64.542413 total, including $38.186189 language.

- 2026-10-20 16:12 UTC — Before any final language result, specified an additional descriptive
  visualization of existing periodic evaluations: raw validation loss against tokens and nominal
  cumulative training FLOPs for all six arms and three final seeds, with across-seed means/SD at
  each arm's own scheduled marks. This reads only completed, audited final runs; it adds no jobs,
  checkpoints, tuning decisions or gate changes. Periodic validation uses seed 1234, whereas
  final headline evaluation uses seed 5678. The plots will not interpolate an equal-compute
  headline or replace the frozen final-result comparison. Interpretation notes now explicitly
  distinguish whole-branch activity/removal from isolated noncommuting-prefix utility.

- 2026-10-20 16:19 UTC — Offline learning-curve reporter
  `analysis/beyond_language_dynamics.py` is ready, with deterministic synthetic mean/SD and
  missing-seed checks plus visual inspection of both plot types. Source SHA
  `e9a681912dc3dc73e0ebd2013b28aece499621d9a05a76412004533c4925cb45`.
  It requires all 18 audited final runs and verifies their exact 16 evaluation marks and
  provenance before creating real-data plots. No experimental curves were inspected during
  development. B and both softmax controls have passed halfway; all six seed-1 jobs remain healthy.

- 2026-10-20 16:25 UTC — First final seed-1 results audited: rawS loss
  3.6615567803382874 nats/token at 13,540 updates; convS 3.6126492470502853 at 13,531.
  Both have exactly 16 scheduled evaluations, correct configuration/source/accounting, and
  1,024 final raw sequence losses from sample seed 5678 agreeing with the reported scalar.
  Worker wall times are 1,167.623s / 1,174.493s; settled estimates $1.610521 / $1.618905.
  Both saved checkpoints have been independently downloaded and byte-fingerprinted without
  deserialization. B and the other three arms remain active; no final candidate decision yet.

## 1. Design registration (before training)

This is a test of combinations and how they learn, not a claim to have invented selection, covariance
correction, or matrix composition. [PaTH](https://arxiv.org/abs/2505.16381) already puts input-dependent
Householder path products in attention scores. Its value-refinement extension is particularly close to A.
[CoPE](https://arxiv.org/abs/2405.18719) and
[stick-breaking attention](https://arxiv.org/abs/2410.17980) provide related content-dependent scalar position
and survival mechanisms. Neither scalar product supplies noncommuting matrix composition.

[Parallax](https://arxiv.org/abs/2605.29157) supplies the estimation component, with precisely the
unnormalized learned-probe variant that won the LOCAL.md comparison. For causal weights p, keys k, values v:

    kbar_i = sum_j p_ij k_j
    w_ij = p_ij [1 - rho_i · (k_j - kbar_i)]
    z_i = sum_j w_ij v_j,    rho_i = W_r x_i, W_r initialized to zero.

The weights sum to one but may be negative. This is a **learned covariance correction**, not a guarantee
of exact affine reproduction: exact precision requires rho = Cov(k)^(-1)(kbar-q), when the covariance is
invertible. We will test that algebraic special case and separately test whether training learns useful
estimation. Positive tilting cannot satisfy the out-of-hull special case, so it is dropped.

All three candidates use small orthogonal matrix states, dimension 5 per head, with four exact
Householder factors per token. Four reflections can represent any SO(5) rotation. Factors begin in two
identical pairs, giving the identity transition while leaving the individual factors independently
trainable. Let U_t be their product and P_t = U_t ... U_0. The branch exposes the whole matrix P_t,
not just its product with a single query vector. Arity-1 and arity-2 ordered features provide a short-product
learning path; learned feature-side sector scales combine them before one matrix-to-vector projection.
The initial branch scale is 0.1.
Common QKV, output and MLP parameters use exactly the GPT initialization stream; the complete model is
not identical to GPT at initialization because of the small matrix branch.

| Candidate | Mechanism | Prediction and principal risk |
|---|---|---|
| A, transported Parallax | Compute P from x first. In small five-dimensional value blocks, read P_i sum_j w_ij P_j^T v_j; mix with ordinary z, plus direct matrix readout. | Can select a location and transport its content along the intervening word. May interfere with stable retrieval and adds value operations. |
| B, parallel Parallax + matrix state | Ordinary z plus the independently computed prefix/short-sector matrix branch. | Most likely to pass, simplest and cheapest; separation lets each mechanism learn its task. The branch may add no value on language. |
| C, attention-conditioned matrix state | Compute z first; generate transitions from x + tanh(context_mix) z; then compose and read matrices. | Selection can condition the subsequent state update. Coupling may make the group representation harder to learn. |

[DeltaProduct](https://arxiv.org/abs/2502.10297) and
[Gated DeltaNet](https://arxiv.org/abs/2412.06464) are the recurrent precedents and comparators. The new
language baseline will include a learned forgetting gate, causal short convolution, normalized queries/keys,
delta updates, head normalization and an output gate. We will distinguish the canonical one-update,
beta-in-(0,1) Gated DeltaNet configuration from the four-update, beta-in-(0,2) gated DeltaProduct extension.
This is an implementation in our common backbone, not a reproduction of their complete published
training recipe. A standalone full-matrix prefix reader is an additional strong diagnostic control:
matching a delta baseline that itself fails word tracking is insufficient.

Broad group-token novelty claims are also excluded by
[Lie-Algebra Attention](https://arxiv.org/abs/2606.20547) and
[All You Need Is Non-Commutative Words](https://arxiv.org/abs/2608.29314).
The experimental question is whether combining these capabilities improves the measured tradeoff.

## 2. Measurement decisions fixed before pilots

- **Stage 0:** compare matrix scans with literal products, value transport with literal pairwise paths,
  zero-gate/zero-probe ablations with softmax, identity transitions and prefix-only special cases,
  future-token perturbations, finite gradients, and affine reproduction with the exact covariance probe.
  Test the regression labels and causal ordered Match-3 labels independently.
- **Diagnostic tasks:** preserve the historical MQAR and induction tasks as descriptive checks. Primary
  retrieval uses MQAR with T=128, 16 pairs and vocabulary 256, and an induction task with T=128,
  vocabulary 128 and all eight query tokens guaranteed three earlier occurrences. Targets always refer to
  the latest prior occurrence. Word problems are A5 and S5 length 16, with learned token embeddings and
  no positional embeddings; report accuracy over every position and over the second half separately.
  Extrapolation to length 64 is descriptive. Causal ordered Match-3 asks whether the current element
  completes any earlier ordered pair to the identity, not the historical noncausal marked-position task.
  A separate affine-regression probe measures estimation on held-out functions and keys.
- **Development and confirmation split:** seed-0 pilots measure timing and learnability. Any architecture
  adjustment following a pilot is explicitly logged before the main grid. Main predictions, exact grids,
  rates, step budgets and numerical gates will be committed in a second registration before that grid.
  A tuning set may select rates; an independent final test set is evaluated only after training.
  Use final-epoch results, not best checkpoints.
- **Diagnostic advancement intent:** two-layer retrieval must learn (at least 90% accuracy) and be within
  3 percentage points of softmax, rather than merely matching chance. Word tracking must reach at least
  95% second-half accuracy and be within 3 points of the strong full-matrix reader at both tested depths.
  One-layer separated-key/value MQAR remains descriptive because binding itself typically requires a
  second attention layer. Ordered Match-3 and regression explain failures and are reported even if a
  candidate fails the retrieval/state gate.
- **Compute:** the headline uses the existing analytic forward-FLOP convention, training = 3x forward,
  with every added projection, scan, convolution, transport and readout counted. This convention excludes
  optimizer and rematerialization work; report measured runtime and cost alongside it. Keep width fixed
  and vary training steps/tokens to match total FLOPs within one step, using a complete cosine schedule
  for every run. Never interpolate an old baseline loss for the headline.
- **Language:** retain the original >=1% equal-FLOP loss reduction on 3/3 seeds versus softmax, and no
  loss increase versus the strongest tuned recurrent baseline. Use the same independent `val_big`
  sample as LOCAL.md for continuity. All new arms receive the same 3-rate 100M-token tuning opportunity;
  the main language registration will freeze rates/grid before runs. Existing softmax/Parallax numbers
  are reference points, with fresh exactly compute-matched softmax runs for the final gate.
- **Budget:** Stage 1 <=$25, Stage 2 <=$100, total <=$150 including pilots. Reserve jobs at their timeout
  and explicit GPU/CPU/RAM limits before launch; never launch a batch whose reservation exceeds the
  remaining stage cap. [Modal prices](https://modal.com/pricing), checked 20 October 2026:
  H100 $0.001097/s, L4 $0.000222/s, CPU $0.0000131/core/s, RAM $0.00000222/GiB/s.
  Estimates will be labeled as estimates, with startup allowance; actual invoice totals are not inferred
  from GPU time alone. Failed runs count against the budget.

## 3. Pilot registration (before pilot results)

The executable manifests are `research/manifests/beyond_pilot_diag.json` and
`research/manifests/beyond_pilot_lm.json`; their source hashes, arguments, resource reservations and
prediction commit are authoritative. These are development runs, not confirmatory evidence.

- **Diagnostic pilot:** eight configurations (S, Parallax, A, B, C, standalone prefix, Gated DeltaNet
  nh=1/beta_max=1, gated DeltaProduct nh=4/beta_max=2); each on small MQAR at 2 layers and A5/S5 words at
  1 layer. Width 128, four heads, Muon 0.004, seed 0, 1,000 updates, batch 64. Validation 256 sequences,
  test 512, five evaluations. Fixed updates here measure speed and obvious learnability problems;
  equal-compute and three-seed claims are reserved for the main grid. L4, 300-second subprocess timeout,
  maximum reservation about $3.75, charged to the $25 diagnostic cap.
- **Language timing pilot:** S, Parallax, A, B, C and the two recurrent configurations, each 100 updates
  at the exact S6 model/batch shape (6x512, context 512, batch 64, two microbatches, bf16, rematerialization),
  Muon 0.004, 10-update warmup. Only 32 validation sequences, no `val_big` selection. H100,
  420-second subprocess timeout; maximum reservation about $4.89, charged to the $100 language cap.
  This estimates feasibility and numerical stability; it is not a language-quality or rate-selection test.
- **Predictions:** B is the fastest candidate; A incurs extra value passes; C has near-B FLOPs but may
  learn state tracking more slowly. Prefix and all three candidates should show word-learning signals
  before softmax; the 1,000-update pilot is too short to demand the final 95% gate. Neither recurrent
  configuration is assumed to solve class-word tracking just because its transition algebra permits it.
  A candidate-specific numerical failure is investigated before freezing the main grid. We will not
  delete failed or timed-out results.

**Control-learnability extension, registered after the 1,000-update MQAR pilot, before the extension.**
Train softmax at 6,000 updates on small MQAR and small induction, separately at Muon rates 0.004 and 0.008,
seed 0; all other diagnostic settings remain as above (256 validation, 512 test). Four L4 jobs with
600-second timeout, maximum combined reservation $1.04, charged to the diagnostic cap. Prediction:
at least one rate reaches 90% on both tasks; if it does not, the screen must distinguish failure to learn
local key/value binding from failure of content selection. Do not call chance-level matching a pass.
These control results may guide a documented task or common-backbone amendment before the main screen;
they cannot support a confirmatory architectural claim.

**Word learnability extension, registered before these results.** Three seed-0 A5 length-16 jobs,
6,000 updates each: (1) the exact historical holonomy positive control, `polybench.py`, one layer,
residual width 64, matrix dimension 3, 85 heads, order 3, normalized sectors, causal prefix, no positions,
AdamW .002, weight decay .01, batch 128; (2–3) the current standalone prefix reader, one layer,
width 128, four dimension-5 heads, four Householders, order 2, no positions, Muon .004,
weight decay .1, batch 64, with paired-identity versus independent-random Householder initialization.
The new reader uses 256 validation / 512 final-test sequences; the historical control retains its
2,048-sequence evaluation and length-64 extrapolation. L4, 600-second timeout each, maximum $0.78,
charged to the screen cap. Prediction: the historical control exceeds 95% second-half accuracy;
random initialization gives the new reader a stronger learning signal than paired identity.
Identity initialization has nonzero parameter gradients but makes first-order prefix perturbations
additive; order-sensitive commutators appear only at second order. This is a learnability hypothesis,
not a proof of the pilot failure. If both new variants fail, vary head capacity or training recipe
one factor at a time before claiming a composition limitation. Do not relax the 95% gate.

**Runtime-only recurrent engineering extension.** The serial recurrent implementation is much slower
than attention despite similar nominal FLOPs. Test exact `lax.scan` unroll factors 1, 4 and 16,
for each of GDN1 and DP4 at the S6 shape, seed 0, 200 updates, Muon .004, warmup 20, 32 validation
sequences and no `val_big`. Six H100 jobs, 900-second timeout each, maximum $7.71,
charged to the development reserve (not language-quality selection). Choose the fastest finite
100-to-200-update interval independently for each recurrent configuration. Loss does not select the
implementation. The recurrence and FLOP count are unchanged; local forward and VJP equivalence tests
must pass before launch. Prediction: moderate unrolling reduces serial dispatch overhead, although
the largest factor may cost more compilation. Report failed/timed-out variants and the chosen factor.

**Local-binding refinement and control pilot.** [Primer](https://arxiv.org/abs/2109.08668) supplies the
established depthwise-QKV convolution; [Arora et al.](https://arxiv.org/abs/2505.15105) separately show
that short convolutions can implement the association step in retrieval. Add an optional causal
width-3 depthwise filter after Q/K/V projection, with no activation. Initialize each channel's taps
uniformly in [-1/sqrt(3), 1/sqrt(3)] from a separate seed stream shared by softmax, Parallax and A/B/C.
Every pre-existing parameter draw is preserved. It adds 9D parameters and 18D nominal forward FLOPs
per layer. A/B's token-to-matrix input stays unchanged; C is conditioned on the convolved attention
output. The recurrent controls retain their own native convolution. This component is prior art.

Before choosing it for the main grid, run five softmax control jobs at seed 0 and 6,000 updates:
MQAR at depths 1 and 2, each at Muon .004 and .008; induction at depth 2 and .004.
Other settings match the retrieval control extension (width 128, heads 4, batch 64, weight decay .1,
256 validation / 512 test, six evaluations). L4 timeout 600 seconds each, maximum $1.30,
charged to the screen cap. Prediction: at least one rate exceeds 90% MQAR at both depths, and
induction remains at least 90%. If adopted, use the same convolution in diagnostics **and language**
for S/P/A/B/C, compare against that equally equipped softmax, and retain raw softmax as an additional
language comparator. Raw-MQAR failures remain reported. Neither a bound-key/value task nor
chance matching can replace the registered retrieval gate.

**Combined-layer learnability pilot.** Following the random-prefix result, test A/B/C separately on
A5 and S5 length 16 at one layer, with independent-random matrix initialization, the shared width-3
QKV convolution, and their original branch scale .1. Add the random standalone prefix reader on S5.
Seven seed-0 jobs, 6,000 updates, Muon .004, width 128, four heads, batch 64, weight decay .1,
256 validation / 512 test sequences, six evaluations, no positions; L4 timeout 600 seconds,
maximum $1.82 charged to the screen cap. Prediction: B reaches the 95% late-position criterion on
both groups; A may pay for its value coupling and C may learn more slowly because its transitions
depend on attention. The standalone prefix separates combined-layer interference from a failure of
the shared state component. These remain development runs; the final screen will use explicitly
matched compute and independent confirmation seeds.

**Exact chunk runtime extension, registered before GPU results.** The unrolled four-update recurrence
still costs 1.060 seconds/update. Implement the established chunk/WY triangular-solve reformulation
of the same delta updates, with chunk sizes 16 and 32 **microsteps**, preserving once-per-token decay
and reading only after a token's final microstep. State products and solves remain float32 with
highest matmul precision. This changes scheduling and redundant arithmetic, not the model recurrence.
CPU forward/final-state/input-VJP checks pass, including near-collinear keys, beta near 2, severe decay,
BF16-quantized inputs, padding and full length-512 states. Whole-layer BF16 gradient differences from
rounding reach relative L2 3.1e-5; do not describe the implementation as bitwise identical.

Run one H100 numerical proof (300-second timeout, maximum $0.56) before any chunk training benchmark.
Its committed script fixes tolerances: output/final-state relative L2 <1e-4 and scaled absolute error
<5e-4; all input-VJP relative L2 <2e-4 and scaled absolute error <3e-3. Report absolute errors.
Only if it passes, run four 200-update S6 timing jobs, chunks 16/32 for GDN1/DP4, otherwise identical
to the unroll timing grid (900-second timeout each, maximum $5.14). Charge all to development.
Select by finite 100-to-200-update runtime only, including unroll-4 as a fallback. Prediction:
chunking cuts recurrent latency by at least 2x versus the best unrolled implementation.

Count dense Gram/query matrices, masked work, padding, triangular solves, state updates and scalar
work in forward FLOPs. Also count the triangular-solve backward excess over the usual 3x-forward
approximation. At S6, chunks 16/32 add forward FLOPs/token 222,141 / 619,198.5 for GDN1 and
861,060 / 1,778,826 for DP4; additional backward charges beyond 3x-forward are
117,504 / 228,096 and 470,016 / 912,384, respectively. `lm.training_flops_per_token` supplies
the total used for language matching and reporting; unchanged arms remain exactly 3x-forward.
Diagnostics retain the native/unrolled recurrence and reject chunk configuration explicitly.

## 4. Main diagnostic registration

The development pilots are not confirmation. They establish usable controls and motivate the two
explicit refinements: independent-random matrix initialization and a shared local-binding convolution.
Freeze the following protocol before the main diagnostic manifests. No further layer parameters or
backbone changes will be selected from these main results.

**Arms and common recipe.** S, P, A, B, C, standalone prefix, GDN1 and DP4, all width 128, four
attention heads, MLP 512, batch 64, Muon, weight decay .1, six evaluations, 1,024 validation and
2,048 disjoint final-test sequences. S/P/A/B/C use width-3 QKV convolution. A/B/C/prefix use four
dimension-5 matrix heads, four Householders, short order 2, random initialization; candidate branch
scale remains .1 and prefix scale 1. GDN1 uses one update/beta_max 1; DP4 uses four/beta_max 2;
both keep native width-4 convolution, key width .75D, value width 1.5D, and unroll 4 (no chunking).
Positions follow the task definition: enabled for retrieval, disabled for group words and regression.
Every arm uses the same data and evaluation seed streams.

**Equal compute.** Each task/depth gets the compute of B at 6,000 updates. Execute
`floor(6000 * B_forward_flops_per_token / own_forward_flops_per_token)` updates, each with its own
complete warmup/cosine schedule. All widths remain fixed; the mismatch is less than one update.
There is no reason to increase every arm's budget to that of the most expensive recurrent variant.
Exact common forward-FLOP targets (training is 3x-forward for these unchunked diagnostic arms):

| Task | One layer | Two layers |
|---|---:|---:|
| MQAR | 614929.6875 | 1164323.375 |
| Induction | 582161.6875 | 1131555.375 |
| A5 words | 506060.23529411765 | 996504.4705882353 |
| S5 words | 521420.23529411765 | 1011864.4705882353 |
| Causal ordered Match-3 | 506060.23529411765 | 996504.4705882353 |
| Affine regression | 491483.29411764705 | 981927.5294117647 |

**Saturation screen, seed 0, validation only.** The six primary cells are two-layer MQAR and induction,
and A5/S5 words at both depths. Start all arms at .004; omit prefix's two-layer retrieval cells.
On word cells S/P are fixed-rate descriptive controls. For every other primary arm/cell, run one
alternate rate only if final validation accuracy is below 97% (or the first run is invalid):
.002 for words, .008 for retrieval. Choose the highest finite final validation score among the
executed rates, ties going to the lower rate. This is an **at-most-two-rate saturation screen**,
not a complete rate sweep. Do not select checkpoints, rates or continuation from seed-0 test scores.

For retrieval, S is the reference. For each word cell, select the strongest final-validation result
among prefix/GDN1/DP4, ties preferring prefix, then GDN1, then DP4. A candidate is screen-positive
only if all six validation cells meet the original absolute thresholds (90% retrieval, 95% word
second-half balanced accuracy) and lie no more than 3 percentage points below their references.
Freeze selected rates, reference identities and all seed-0 decisions in a committed selection artifact.

**Independent confirmation.** Screen-positive candidates and their shared references run seeds 1, 2
and 3 on the six primary cells, at their frozen rates and exactly the same compute budgets.
A candidate advances only if every final-test gate holds on all three seeds. Report all individual
scores and sequence-cluster uncertainty, including the easier all-position word score separately.
Confirmation priority is B, then C, then A, fixed by simplicity and cost rather than language results.
References run once and are shared; missing confirmations are labeled unconfirmed, never passed.

**Descriptive mechanism map.** All eight arms also run one-layer MQAR/induction and one-/two-layer
causal ordered Match-3 and affine regression, seed 0, fixed .004, the same matched-compute rule.
These 48 cells are reported even for candidates rejected by the primary screen. Match-3 reports
balanced accuracy and positional results against an independently calibrated position-only classifier:
position alone reaches about 74.85% balanced test accuracy on this task. Regression reports MSE,
normalized MSE, sequence-level uncertainty and the mean-value baseline. A 10% MSE reduction versus S
is an informative estimation target, not an advancement gate or cross-seed reliability claim.
Two optional LLA regression controls may run only after the mandatory work fits the budget.

**Predictions.** B passes the six-cell screen and three-seed confirmation. C should also pass but may
show more seed variation from its conditioned transitions. A is at risk on S5: its one-layer pilot
scored only 2.91% late-position test accuracy while B/C were 100%; the formal matched-compute screen
still tests its alternate rate. S/P should preserve retrieval but fail class-word tracking. GDN1
should retrieve well; neither query-read recurrent variant is assumed to match the full-matrix word
reader. P and the candidates should improve one-layer affine estimation over S, while depth may
narrow that gap. No Match-3 success is inferred from word tracking: the branch exposes short sectors
only through arity 2, while the task asks about arbitrary ordered triples.

**Budget and ordering.** All jobs use L4 and a 600-second subprocess timeout; the existing ledger
enforces the $25 screen cap including every pilot/failure/reservation. Run primary first-rate cells,
triggered alternates, shared references and B confirmation, then the descriptive map and remaining
candidate confirmations in the fixed priority order; finish these before optional additions.
Expected mandatory cost with three saturating
candidates is approximately $18.7 plus pilots, but this is not a spending guarantee. If the cap binds,
report the exact missing cells and unconfirmed status; do not borrow from another stage or silently
reduce evaluation sizes, steps, seeds or thresholds.



## 4.1. Written-rule reconciliation before independent confirmation

This amendment is made after all 59 seed-0 primary/alternate results and before any confirmation
seed 1, 2 or 3 is launched. All three candidates and all six selected references score 100%
validation after the prescribed alternates. Thus the original executable rule and the written rule
select exactly the same candidates, rates and reference identities. The discrepancy identified in
the Log changes **no seed-0 decision**.

For independent confirmation, use the originally written candidate rule explicitly. In every cell
and each of the three seeds, require a completed finite candidate and reference result, candidate
accuracy at least 90% for retrieval or 95% for second-half balanced word accuracy, and candidate
accuracy no more than 3 percentage points below the frozen reference. The reference itself need
not exceed the candidate's absolute threshold. A missing, failed or nonfinite reference remains
unconfirmed; it never becomes an easy comparison. All candidate thresholds, margins, selected rates,
reference identities, compute budgets, evaluation samples, seed counts and execution priority remain
unchanged. This correction applies uniformly to A, B and C and every primary cell.

Preserve the original sealed selection and its executable outcomes. A separate sealed selection
records this registration commit, the original selection hash, the reconciliation policy, and the
unchanged strict-code seed-0 outcomes. Confirmation reports **both** policies: the active written-rule
candidate outcomes and the original executable outcomes, including its additional reference floor.
Only candidates passing the active written rule in all 18 independent cells may enter language.
If a candidate later passes only the reconciled rule, say so adjacent to its result; do not present
it as passing the original executable rule. This is a disclosed post-seed-0 code/text reconciliation,
prospectively fixed before independent confirmation, not a retroactive alteration of the original code.

The policy identifier is
`59e1b83139fbb148de0132005de781486a86aa79cd4a2c5d675ca21416863d46`.
No model/training source or seed-0 artifact is changed. The original frozen job generator continues
to produce the same registered confirmation configurations from the separately sealed selection.

## 5. Main language registration (before quality sweeps)

Only candidates passing every registered independent Stage-1 confirmation gate enter language.
The architecture stays as frozen in Stage 1. Carry both modern recurrent variants through the full
language comparison; the exact chunk-32 implementation is selected only by its numerical proof and
runtime experiment. A reporting-only amendment before language will preserve unrounded validation
and final losses plus per-sequence final losses. Audit and commit its diff as a source-hash bridge:
no model, optimizer, data, initialization or training-step behavior may change.

**Common recipe and arms.** FineWeb-Edu, existing GPT-2-tokenized volume, vocabulary 50,304,
context 512, six layers, width 512, eight attention heads, MLP 2,048, batch 64, two accumulated
microbatches, BF16, rematerialization, Muon and the existing S6 optimizer recipe. Use learned
positional embeddings. Every arm starts fresh from its initialization and shared seed/data streams.
Controls are raw softmax, width-3-convolved softmax, width-3-convolved Parallax, GDN1 and DP4.
A/B/C use the same width-3 convolution, dimension-5 matrix states, four Householders, short order 2,
independent-random initialization and branch scale .1 as the diagnostic screen, with eight matrix
heads. GDN1/DP4 retain their native width-4 convolution, key width .75D and value width 1.5D;
chunk size 32 counts microsteps. Historical LOCAL.md results are context, not substitutes for any
fresh comparator in the headline.

**Fixed token corpus.** Before any language quality run, fingerprint both existing token files on
`polyformer-data/fineweb_edu` and bind the committed `results/beyond_language_planning/dataset.json`
into the executable plan. The observed corpus has 744,582,584 training and 7,514,908 validation
uint16 tokens. Its SHA-256 values are `b5684af6fa868293bf2628c41b08e54ea2a0ef8894f515bab299d17e909cf10b`
(train) and `5afa5156b009815de51f8b244741fc7ff0bab45fb582ed99ccce5dd2ed0cf0b9` (validation).
Current preparation code describes one FineWeb-Edu shard, `sample/10BT/000_00000.parquet`, preserving
row order, assigning zero-based document indices divisible by 100 to validation and all others to
training. It uses GPT-2 tiktoken ordinary encoding plus EOT 50256 after each document. The original
Hugging Face revision and tokenizer build were not recorded; current source evidence does not prove
the historical preparation invocation. The binary hashes identify the actual benchmark from this
point onward. Sampling uses random contiguous 513-token windows for 512 targets. Repeat the full
fingerprint after the study and report agreement or changes; no retokenization or split changes.

**Rate tuning, then independent seeds.** Every included arm, including raw softmax, receives exactly
three fresh 3,051-update runs (99,975,168 tokens), seed 0, rates {.002, .004, .008}, warmup 305 updates,
eight evaluation marks, `vseqs=1024`, `vbig=0`. Select the smallest finite **final unrounded** validation
loss on the fixed seed-1234 validation sample; ties select the lower rate. Require all three jobs
terminal before selection. A failed/nonfinite run is reported and cannot win. The prospective
candidate-local failure policy below specifies progression if an arm has no valid rate; that arm
cannot establish a language headline. Do not extend the rate grid at its edges or select intermediate
checkpoints. Freeze selected rates and final-job eligibility in a committed artifact.

**Prospective candidate-local tuning failures.** This rule is registered before
any language quality trial. All three registered rate trials of every original
arm must be terminal before selecting rates. A candidate whose three trials
are invalid is retained in the plan, selection and final report as
`tuning_invalid` and unconfirmed; its invalid trials are not measured quality
losses. Every candidate with at least one valid trial proceeds at its selected
rate. All five controls—raw softmax, convolutional softmax, convolutional
Parallax, GDN1 and DP4—are mandatory. If any control has no valid trial, or no
candidate has a valid trial, the entire final grid stops and the report states
the reason.

The original plan, original Stage-1 survivor list, all candidate schedules and
all control allowances remain frozen. In particular, a candidate's tuning
failure does not reduce controls' work, even if that candidate set the largest
compute allowance. Final job eligibility is recorded separately in the
committed selection artifact. It cannot silently drop a candidate with a valid
rate or any comparator. No additional attempts, rate extensions, intermediate
checkpoints or final held-out results are used to recover an invalid arm.

The selection retains every original tuning row, all invalid-run reasons and
all valid-rate winners. It records `viable_candidates`,
`tuning_invalid_candidates`, `invalid_controls`, `final_arm_order` and
`stop_reasons`. A shared verifier recomputes these fields from the complete
terminal grid before final export or reporting. A partial candidate selection
may proceed; all headline gates remain per candidate and require all registered
comparators and all three independent final seeds.

Policy ID:
`5a2058cda5ad1d84b8bb9d8a6843514b641e81390dcee1c5a28fca4da4cb27e9`.

Source, configuration, job-identity or declared accounting contradictions are integrity errors,
not candidate-local training failures. Successful results require complete, finite, consistent token
and FLOP counts. Explicit worker failures may lack optional metrics but must retain intact provenance;
any present contradictory accounting also stops selection for investigation.

Final runs use new initialization/data-order seeds **1, 2 and 3**, a complete fresh schedule with
400 warmup updates and 16 evaluation marks. The independent final sample is LOCAL.md's fixed
seed-5678 sample of 1,024 held-out sequences. Evaluate it once per trained model; report the exact
mean in nats/token and retain the individual sequence losses. It comes from the same validation
corpus as the tuning sample, so this is sample separation, not a new-corpus generalization test.
Save final checkpoints before extra diagnostics. No main run continues a tuning checkpoint.

**One nominal candidate budget, with conservative comparator allowances.** Amend the literal
per-candidate 400M-token recipe to one nominal reference budget equal to the most expensive
surviving candidate trained for 12,207 updates (399,998,976 tokens). Other candidates use
`ceil(F_target / (32768 * training_flops_per_token))` updates, with less than one update of rounding
excess. This avoids repeated controls at nearly identical budgets. Include the chunk solve's extra
backward cost; do not silently use 3x-forward for chunked recurrence. The prospective allowance
below supersedes nominal-only control schedules and records intentional added work separately.

| Arm | Forward FLOPs/token | Training FLOPs/token |
|---|---:|---:|
| Raw softmax | 92,473,464 | 277,420,392 |
| Convolved softmax | 92,528,760 | 277,586,280 |
| Convolved Parallax | 98,872,512 | 296,617,536 |
| A | 107,581,758.1875 | 322,745,274.5625 |
| B | 101,163,294.1875 | 303,489,882.5625 |
| C | 101,172,510.1875 | 303,517,530.5625 |
| GDN1, chunk 32 | 98,067,262.5 | 294,429,883.5 |
| DP4, chunk 32 | 123,706,314 | 372,031,326 |

If B/C survive and A does not, the target is 1.214067014230487e17 training FLOPs/run.
For audit, nominal-only updates for raw S / convolved S / convolved P / B / C / GDN1 / DP4 would be
13,356 / 13,348 / 12,491 / 12,209 / 12,207 / 12,584 / 9,959. If A survives, the target becomes
1.2909777933383885e17; nominal-only updates including A would be
14,202 / 14,193 / 13,283 / A 12,207 / B 12,982 / C 12,981 / GDN1 13,381 / DP4 10,590.
The actual control schedules receive the additional allowance below. Other survivor subsets use
the same fixed rules. The immutable executable plan records the exact case.
Report parameter counts, tokens, measured runtime and estimated cost alongside nominal FLOPs;
optimizer and rematerialization arithmetic remain outside this analytic convention.

**Prospective conservative control allowance, fixed before language quality results.**
The original analytic worker counter uses ideal triangular causal attention and the historical
two-value-product Parallax convention; the JAX implementation materializes dense attention and
combines corrected weights before its value product. Chunked recurrence already counts its dense
masked work. Whole-block checkpointing introduces another implementation sensitivity. Address these
identified differences prospectively by giving every comparator a conservative compute allowance.
The original worker counters continue to report their registered nominal values.

Let `F_a` be an arm's original forward FLOPs/token and `N_a` its original training FLOPs/token,
including the chunk solve's extra backward cost. Let `H_vocab = 2 * 512 * 50304 = 51,511,296`,
the tied vocabulary projection outside the checkpointed transformer blocks. Define the source-upper
forward adjustment `delta_a` as follows:

| Arm | Forward adjustment |
|---|---:|
| Raw or convolved softmax | 3,200,904 |
| Convolved Parallax, B or C | 3,231,552 |
| A, without compiler-sharing credit | 6,371,040 |
| GDN1 or DP4 | 0 |

At `T=512, D=512, heads=8, L=6`, with `t_c=(T+1)/2` and A's padded value width `p=520`,
these adjustments are `L*(T-t_c)*(4D+5heads)` for softmax,
`L*((T-t_c)*(8D+8heads)-2TD)` for Parallax/B/C, and
`L*((T-t_c)*(8D+8heads+4p)-2Tp)` for A. Credit the explicitly combined corrected-weight
value products, but charge A's duplicate ordinary `W@V` call without relying on common-subexpression
elimination. Keep the already-counted dense recurrent chunk work and solve backward surcharge.

Use all four declared training-work estimates per token:

1. Nominal: `W_a,0 = N_a`.
2. Nominal plus one whole-block recomputation: `W_a,1 = N_a + F_a - H_vocab`.
3. Source upper: `W_a,2 = N_a + 3*delta_a`.
4. Source upper plus one whole-block recomputation: `W_a,3 = N_a + F_a - H_vocab + 4*delta_a`.

Candidate schedules retain the original nominal common-target ceiling rule. For every control
`j` in raw softmax, convolved softmax, convolved Parallax, GDN1 and DP4, set

    updates_j = ceil(max_{included candidates i, conventions k}
                     updates_i * W_i,k / W_j,k).

This gives every control at least each included candidate's total modeled training work under
every declared convention. Batch tokens cancel from the ratio. Compute the ratios exactly using
rational arithmetic, and record the binding candidate/convention and all nonnegative work margins.
The intentional allowance is separate from ceiling roundoff; only the latter is below one update.
All rate sweeps remain three fresh 3,051-update runs. Final runs retain seeds 1/2/3, fresh complete
schedules, 400 warmup updates, evaluation samples, selected-rate procedure and headline loss gates.
Timeouts below are fixed prospectively, before any language quality job.

| Control | B/C: original → final updates | B/C final timeout | A/B/C: original → final updates | A/B/C final timeout |
|---|---:|---:|---:|---:|
| Raw softmax | 13,356 → 13,542 | 1,600s | 14,202 → 14,902 | 1,800s |
| Convolved softmax | 13,348 → 13,533 | 1,900s | 14,193 → 14,892 | 2,000s |
| Convolved Parallax | 12,491 → 12,535 | 2,100s | 13,283 → 13,829 | 2,300s |
| GDN1 | 12,584 → 13,108 | 2,900s | 13,381 → 14,474 | 3,100s |
| DP4 | 9,959 → 10,278 | 5,100s | 10,590 → 11,217 | 5,500s |

Candidate updates remain B 12,209/C 12,207 in the B/C case and A 12,207/B 12,982/C 12,981
in the A/B/C case. Other survivor subsets use the same fixed formula. The executable plan retains
the original nominal reference budget, all four per-token and total modeled counts, original/final
updates, added tokens, binding requirements, exact ratio proofs, forecasts and reservations.

The B/C language forecast becomes **$77.09**, including earlier timing pilots; aggregate timeout
reservations are **$99.82**. The A/B/C forecast becomes **$94.26**, with aggregate timeout
reservations **$122.17**, so rolling settlement remains necessary. Added forecast/maximum reservation
costs are $0.853041/$1.464528 for B/C and $2.117802/$2.562924 for A/B/C. The $100 language
cap, $150 total cap and no-transfer rule remain in force; forecasts do not guarantee completion.

This is a conservative comparator allowance under four specified arithmetic conventions, **not
a measurement or guarantee of equal hardware-executed GPU FLOPs**. Scalar costs remain estimates,
compiler behavior and precision affect execution, and actual autodiff may avoid some whole-block
recomputation. Optimizer arithmetic remains excluded. Report nominal work, these sensitivity
estimates, tokens, parameters, measured runtime and estimated spend distinctly. A positive outcome
would satisfy the preregistered loss gates against controls given at least the candidate's modeled
work under every stated convention.

The allowance policy identifier is
`3a340829e3fa07d6808280c240992af63283088ac92a3d68d7935cb7822d0991`.
Independent rational audits cover all seven survivor subsets, 240 dominance inequalities and
35 minimal-ceiling checks; the original counter audit is retained alongside this amendment.

**Headline and interpretation.** For each seed s in {1,2,3}, an advancing candidate X must satisfy

    loss_X(s) <= 0.99 * min(loss_raw_softmax(s), loss_convolved_softmax(s))
    loss_X(s) <= min(loss_GDN1(s), loss_DP4(s)).

All six inequalities across the three seeds and the Stage-1 gates are required. Missing/invalid
comparators make the result unconfirmed, not passed. This is a preregistered observed gate; three
wins alone are not conventional statistical significance. Report seed-level differences and paired
sequence-level uncertainty conditional on each trained model. Sequence uncertainty does not replace
training-seed variation; overlapping text windows may also limit independence.

Convolved Parallax is a separate mechanism comparator. Report its per-seed difference from each
candidate. A candidate that beats softmax and the RNNs but does not beat convolved Parallax has not
shown a useful extra composition contribution. On each candidate checkpoint also score zeroed
composition and precision components, plus coupling for A/C, on the same final sequences.
These are inference interventions in the trained model, not retrained controls; they show sensitivity
to removing a component and do not prove that noncommutativity caused a gain. Report matrix-state
usage, probe correction, coupling gates and commutator statistics without equating nonzero activity
with useful computation.

**Predictions.** B remains the favored design on simplicity and nominal cost. It should preserve most
of Parallax's estimation benefit, but a full 1% advantage over convolved softmax is uncertain:
previous language evidence suggests that high-order composition contributes little at this scale.
C may match B or lose slightly through additional coupling; A, if it advances, has the largest
compute/learnability risk. Convolved softmax may improve substantially over the historical raw
baseline, making the gate harder. The recurrent comparison is open; no winner is assumed from
synthetic retrieval or group-word performance. No zeroed-component or final-test result will select
architectures, rates or additional confirmatory runs.

**Budget.** Stage 2 remains capped at $100 including the $2.326 language timing pilots. With B/C,
all fresh three-rate sweeps and all seven arms at three final seeds forecast $77.09, including a 15%
convolution runtime allowance and the conservative control updates; full timeout reservations sum
to $99.82. If A also advances, the forecast is $94.26 and aggregate timeout maximum $122.17,
so only rolling reservations
backed by actual settlement can fit; the ledger still refuses any over-cap launch. Tune all included
arms, then execute complete seed blocks in seed order, keeping paired comparisons together. If the
cap prevents completion, report the exact absent runs and no three-seed headline. No funds transfer
from another stage. Timeouts and all failures count. Final timeouts are recorded in the executable
plan and are not silently increased after a failed job.
