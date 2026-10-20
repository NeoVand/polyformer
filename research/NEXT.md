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

## Seed-0 Pilots and Preregistered Main-Grid Predictions (Frozen Before Main Runs)

### 1. Seed-0 Pilot Results (`next_pilot1` and `next_pilot2`)

All 12 pilot jobs (`next_pilot1`: 4 narrative jobs, 1,500 steps, batch 64, eval seed 1234, 128 pairs/split;
`next_pilot2`: 2 mixed ARC jobs, 1,500 steps, batch 32, 16 tasks/cell, TTT 16 steps at 1e-3, plus 6 single-primitive
control jobs at 500 steps, 2,048 train tasks, TTT off) completed on L4 with zero errors. Conservative settled spend:
**$0.371512** (Experiment 1) + **$0.554111** (Experiment 2) = **$0.925623** total.

#### Experiment 1 Seed-0 Pilot (`eval_seed=1234`, 128 pairs / 256 sequences per split)

Decision target share `p`: **0.01047** on `id` (mean 14.23 ops), **0.00963** on `paraphrase` (mean 13.79 ops),
**0.00530** on `length` (mean 27.91 ops), **0.00529** on `both` (mean 27.95 ops), **0.01700** on `short` (8 ops).
Initial-owner heuristic paired accuracy: **14.06%** (`id`), **11.72%** (`paraphrase`), **9.38%** (`length` / `both`),
**23.44%** (`short`).

| Arm | Objective | Split | Paired acc % | Single acc % | Token CE | Decision CE | Non-decision CE |
|---|---|---|---:|---:|---:|---:|---:|
| `softmax` (71,962 params) | `token` | `id` | 2.34 | 22.66 | 0.6470 | 1.3885 | 0.6391 |
| `softmax` | `token` | `paraphrase` | 0.00 | 22.27 | 4.9580 | 1.3916 | 4.9926 |
| `softmax` | `token` | `length` | 0.00 | 25.78 | 0.7284 | 1.3910 | 0.7249 |
| `softmax` | `token` | `both` | 0.00 | 25.00 | 5.1735 | 1.4131 | 5.1935 |
| `softmax` | `token` | `short` (8 ops) | 0.00 | 26.56 | 0.6311 | 1.3885 | 0.6180 |
| `hybrid` (78,330 params) | `token` | `id` | 1.56 | 23.44 | 0.6467 | 1.3889 | 0.6389 |
| `hybrid` | `token` | `id_no_composition` | 0.00 | 23.44 | 0.6467 | 1.3888 | 0.6388 |
| `hybrid` | `token` | `paraphrase` | 0.00 | 26.56 | 5.1175 | 1.3898 | 5.1538 |
| `hybrid` | `token` | `length` | 0.00 | 24.22 | 0.7418 | 1.3900 | 0.7384 |
| `hybrid` | `token` | `both` | 0.78 | 27.73 | 5.2893 | 1.3947 | 5.3100 |
| `hybrid` | `token` | `both_no_composition` | 0.00 | 27.34 | 5.2885 | 1.3944 | 5.3092 |
| `hybrid` | `token` | `short` (8 ops) | 0.78 | 28.12 | 0.6304 | 1.3886 | 0.6173 |
| `softmax` | `decision` | `id` | **13.28** | **33.59** | 8.1625 | **1.2724** | 8.2354 |
| `softmax` | `decision` | `paraphrase` | **10.16** | **37.11** | 8.1782 | **1.2766** | 8.2453 |
| `softmax` | `decision` | `length` | 0.78 | 22.27 | 9.1852 | 1.4022 | 9.2267 |
| `softmax` | `decision` | `both` | 3.12 | 26.17 | 9.0953 | 1.3881 | 9.1363 |
| `softmax` | `decision` | `short` (8 ops) | 27.34 | 51.56 | 7.0547 | **1.0497** | 7.1586 |
| `hybrid` | `decision` | `id` | 10.16 | 31.25 | 10.9642 | 1.3275 | 11.0663 |
| `hybrid` | `decision` | `id_no_composition` | 10.16 | 30.47 | 10.9612 | 1.3297 | 11.0631 |
| `hybrid` | `decision` | `paraphrase` | 8.59 | 28.52 | 11.0089 | 1.3564 | 11.1027 |
| `hybrid` | `decision` | `length` | 2.34 | 23.83 | 11.0044 | 1.3991 | 11.0555 |
| `hybrid` | `decision` | `both` | 3.12 | 26.17 | 11.0199 | 1.3935 | 11.0711 |
| `hybrid` | `decision` | `both_no_composition` | 3.91 | 25.78 | 11.0152 | 1.3933 | 11.0664 |
| `hybrid` | `decision` | `short` (8 ops) | **29.69** | **51.56** | 10.9218 | 1.1629 | 11.0906 |

Pilot diagnosis:
1. Under `token` weighting, final-decision tokens represent only $p \approx 0.53\%\text{--}1.05\%$ of tokens; both
   arms fit narrative syntax (`other_ce` $\approx 0.639$ on `id`) while leaving `decision_ce` stuck at the 4-label
   uniform ceiling $\ln 4 = 1.3863$ (`1.3885` / `1.3889`) and paired accuracy near zero (`2.34%` / `1.56%`).
2. Under `decision` weighting, removing the $100\times$ dilution drops `decision_ce` to `1.2724` (`softmax`) and
   `1.3275` (`hybrid`) on `id` (`1.0497` and `1.1629` on `short`), lifting paired accuracy to `13.28%` (`softmax`) and
   `10.16%` (`hybrid`) on `id` (`27.34%` and `29.69%` on `short`). However, this matches the shallow initial-owner
   heuristic (`14.06%` on `id`, `23.44%` on `short`) rather than multi-step alias + transposition tracking, and
   zeroing `hybrid`'s composition branch (`id_no_composition`) leaves its paired accuracy unchanged (`10.16%`).

#### Experiment 2 Seed-0 Pilot (`eval_tasks=16` per cell)

Single-primitive controls (500 steps, `train_tasks=2048`, `ttt_steps=0`):
- `identity`: `softmax` **100.0%** exact (16/16), `hybrid` **100.0%** exact (16/16).
- `colour` (operator-heldout random colour bijection): `softmax` **100.0%** exact (16/16), `hybrid` **100.0%** exact (16/16).
- `rotation` (fixed 90° D4 rotation): `softmax` **100.0%** exact (16/16, loss 0.0092), `hybrid` **0.0%** exact (0/16,
  cell 19.6%, loss 2.1071 — the 1D raster Householder prefix branch slows 2D spatial attention routing).

Mixed ARC pilot (1,500 steps, `train_tasks=8192`, `ttt_steps=16` at `1e-3`):

| Tier & Depth | Softmax no-TTT exact (cell) % | Softmax TTT exact (cell) % | Hybrid no-TTT exact (cell) % | Hybrid TTT exact (cell) % | Copy-input exact % | Privileged solver exact (ident.) % | Shorter canonical % |
|---|---:|---:|---:|---:|---:|---:|---:|
| `invertible_depth1` | **31.25** (40.5) | **31.25** (38.5) | 0.00 (25.7) | 25.00 (38.7) | 0.00 | 100.0 (100.0) | 0.0 |
| `invertible_depth2` | **37.50** (43.9) | **37.50** (43.2) | 0.00 (32.8) | **37.50** (43.4) | 12.50 | 100.0 (100.0) | 68.8 |
| `invertible_depth3` | **6.25** (20.3) | **6.25** (17.7) | 0.00 (17.4) | **6.25** (18.9) | 0.00 | 100.0 (100.0) | 56.2 |
| `invertible_depth4` | **6.25** (17.5) | **6.25** (16.1) | 0.00 (13.9) | **6.25** (20.1) | 6.25 | 100.0 (100.0) | 100.0 |
| `irreversible_depth1` | 6.25 (82.6) | 6.25 (81.1) | 0.00 (77.4) | **18.75** (80.2) | 25.00 | — | — |
| `irreversible_depth2` | **12.50** (84.9) | **12.50** (83.7) | 0.00 (83.7) | **12.50** (79.5) | 0.00 | — | — |
| `irreversible_depth3` | 0.00 (77.3) | 0.00 (78.0) | 0.00 (77.4) | 0.00 (76.9) | 0.00 | — | — |
| `irreversible_depth4` | 0.00 (81.8) | 0.00 (75.9) | 0.00 (82.5) | 0.00 (81.2) | 0.00 | — | — |

Pilot diagnosis:
1. Both models solve operator-heldout colour permutations in-context via content-addressed colour lookup (`5/16 = 31.25%`
   at depth 1; `6/16 = 37.50%` at depth 2 where 2 tasks reduce to identity and 4 reduce to pure colour permutations;
   `1/16 = 6.25%` at depths 3 and 4), and neither model infers held-out 2D spatial transformations (`d4`, `translate`)
   from 3 demos in-context.
2. Without TTT, `hybrid`'s 1D prefix branch disrupts zero-shot colour lookup (`0.00%` across all depths); 16 steps of
   demo TTT restore `hybrid` to parity with `softmax` (`25.00%, 37.50%, 6.25%, 6.25%`), not superiority.
3. The privileged family solver (`structural_solver`) achieves **100.0%** exact accuracy and **100.0%** identifiability
   at all depths 1–4, proving the demonstrations uniquely determine the operator while $100\%$ of depth-4 invertible
   compositions collapse to $\le 3$ canonical factors.

---

### 2. Frozen Main-Grid Protocol and Preregistered Predictions (Seeds 1, 2, 3)

We freeze the main grids using the exact committed source code (`dilution.py` and `algebraic_arc.py` defaults, zero
code edits since pilot commit `c6957aa`):
- **Experiment 1 (`next_main1`, manifest `research/manifests/next_main1.json`, job spec `research/next_jobs/main1.json`):**
  12 jobs on L4 — `arm in {softmax, hybrid}` $\times$ `objective in {token, decision}` $\times$ `seed in {1, 2, 3}`,
  `--steps 1500 --batch 64 --eval-pairs 256 --eval-seed 73517`, `max_seconds=900`. Max reservation $4.360836
  (cumulative Experiment 1 max reservation $4.732348 $\le$ $15.00 cap).
- **Experiment 2 (`next_main2`, manifest `research/manifests/next_main2.json`, job spec `research/next_jobs/main2.json`):**
  24 jobs on L4 — 6 mixed ARC jobs (`arm in {softmax, hybrid}` $\times$ `seed in {1, 2, 3}`, `--steps 2500 --batch 32
  --eval-tasks 64 --train-tasks 8192 --ttt-steps 16 --ttt-lr 0.001`, `max_seconds=900`) plus 18 single-primitive
  control jobs (`arm in {softmax, hybrid}` $\times$ `control in {identity, rotation, colour}` $\times$ `seed in {1, 2, 3}`,
  `--steps 500 --batch 32 --eval-tasks 64 --train-tasks 2048 --ttt-steps 0`, `max_seconds=600`). Max reservation
  $6.856296 (cumulative Experiment 2 max reservation $7.410407 $\le$ $20.00 cap; cumulative total $\le$ $35.00 cap).

#### Registered Predictions and Numeric Pass/Fail Thresholds

- **H1 (Experiment 1 Headline Pass Criterion, from Plan):** On the held-out `id` split (`eval_seed=73517`, 256 pairs),
  decision weighting raises `hybrid`'s paired exact-accuracy advantage over `softmax` by $\ge 15.0$ percentage points
  in the 3-seed mean:
  $$\bigl(\text{PA}_{\text{hybrid,dec}} - \text{PA}_{\text{softmax,dec}}\bigr) - \bigl(\text{PA}_{\text{hybrid,tok}} - \text{PA}_{\text{softmax,tok}}\bigr) \ge 15.0\text{ pp}$$
  AND $\text{PA}_{\text{hybrid,dec}} \ge 90.0\%$ in the 3-seed mean.
  - *Pilot-informed prediction:* **H1 will FAIL** (predicted interaction $\in [-5.0, +5.0]$ pp and
    $\text{PA}_{\text{hybrid,dec}} \in [5.0\%, 20.0\%]$).
- **P1.1 (Dilution Factor $p$ and Token-Weighted Plateau):** Across seeds 1–3 on `eval_seed=73517`, final-decision token
  share satisfies $0.0095 \le p \le 0.0115$ on `id`/`paraphrase`, $0.0048 \le p \le 0.0058$ on `length`/`both`, and
  $0.0160 \le p \le 0.0180$ on `short`. Under `token` objective, both `softmax` and `hybrid` achieve `other_ce <= 0.66`
  nats on `id` on 3/3 seeds while `decision_ce` remains near $\ln 4 = 1.3863$ (`1.37 <= decision_ce <= 1.42` nats on
  `id`) and paired accuracy remains $\le 5.0\%$ on `id`, `paraphrase`, `length`, and `both` on 3/3 seeds.
- **P1.2 (Decision-Weighting Effect on Both Arms):** Under `decision` objective, both `softmax` and `hybrid` improve
  over `token` objective on `id` by $\ge 5.0$ percentage points in 3-seed mean paired accuracy (`decision_ce <= 1.36`
  nats on `id` on 3/3 seeds) and reach $\ge 20.0\%$ 3-seed mean paired accuracy on `short` (8 operations), while
  unweighted narrative tokens diverge to `other_ce >= 6.0` nats on `id` on 3/3 seeds. However, neither arm exceeds
  $25.0\%$ 3-seed mean paired accuracy on `id` or $10.0\%$ on `length`/`both`.
- **P1.3 (Composition Branch Ablation in Experiment 1):** Under both `token` and `decision` objectives, the 3-seed mean
  paired accuracy gap `PA(hybrid) - PA(softmax)` on `id` and `both` stays $< 5.0$ percentage points, and zeroing the
  composition branch (`id_no_composition`, `both_no_composition`) alters `hybrid`'s 3-seed mean paired accuracy by at
  most $\pm 3.0$ percentage points.
- **H2 (Experiment 2 Headline Pass Criterion, from Plan):** On the `invertible` tier at depths $\ge 3$ (`invertible_depth3`
  and `invertible_depth4`), the best `hybrid` variant (`max(without_ttt, with_ttt)`) beats the best `softmax` variant
  (`max(without_ttt, with_ttt)`) by $\ge 15.0$ percentage points in 3-seed mean exact-match accuracy, with the
  advantage strictly increasing with depth from depth 1 to depth 4.
  - *Pilot-informed prediction:* **H2 will FAIL** (predicted 3-seed mean gap at depths 3 and 4 within $[-5.0, +5.0]$ pp,
    with both arms $\le 20.0\%$ exact accuracy at depths 3–4).
- **P2.1 (Privileged In-Context Solver and Algebraic Collapse):** Across seeds 1–3 (64 tasks/cell), `privileged_family_solver`
  achieves $\ge 98.0\%$ 3-seed mean exact accuracy and $\ge 95.0\%$ identifiability at all invertible depths 1–4, while
  `shorter_canonical_description_fraction` is $0.0\%$ at depth 1, $\ge 40.0\%$ at depths 2–3, and $100.0\%$ at depth 4.
- **P2.2 (Single-Primitive Controls):** Across seeds 1–3 (`eval_tasks=64`, 500 steps, no TTT), both `softmax` and
  `hybrid` reach $\ge 95.0\%$ 3-seed mean exact accuracy on `identity` and on operator-heldout `colour` permutations,
  whereas on fixed `rotation` (`("d4", 1)`), `softmax` exceeds `hybrid` by $\ge 25.0$ percentage points in 3-seed mean
  exact accuracy (`softmax >= 90.0%` on at least 2/3 seeds).
- **P2.3 (Mixed Invertible Depth Trend and TTT Rescue of Hybrid):** On `invertible` depths 1–2, both `softmax` and
  `hybrid` (with TTT) achieve $15.0\%\text{--}45.0\%$ 3-seed mean exact accuracy (matching the fraction of tasks that
  reduce to pure colour permutations or identity) and drop to $\le 20.0\%$ at depths 3–4. For `hybrid`, `with_ttt`
  exceeds `without_ttt` by $\ge 10.0$ percentage points in 3-seed mean exact accuracy on `invertible_depth1` and
  `invertible_depth2` (`without_ttt <= 10.0%`).
- **P2.4 (Irreversible Tier):** On `irreversible` depths 1–4, both `softmax` and `hybrid` (with and without TTT) stay
  $\le 25.0\%$ 3-seed mean exact accuracy at depths 1–2 and $\le 10.0\%$ at depths 3–4, while achieving $\ge 70.0\%$
  3-seed mean cell accuracy due to background sparsity.

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
- 2026-10-20 19:28 UTC — Both generator/layer test suites are written first and observed failing on missing
  implementation modules. Experiment 1 avoids answer-conditioned rejection: reciprocal transfers preserve the
  initial owner's counterfactual difference. Decision weighting will mean equal weight per final answer and
  zero narrative-token weight, explicitly the strongest version of the requested reweighting. Experiment 2
  consumes only demonstration input/output grids and query input, with output masking and task-reset TTT tests.
  No paid calls yet. Main comparisons will use fresh seeds 1/2/3, keeping seed 0 for pilots only.
- 2026-10-20 19:30 UTC — Stage-0 passes: 7 narrative tests (including 4,000 brute-force trajectories), 7 ARC tests
  (D4 closure, inverse/compound transforms, no-label-leak and task-reset TTT), and 5 runner tests. Both local
  training/evaluation smoke runs succeed. Freeze seed-0 pilots: four narrative arms, 1,500 updates, batch64,
  eval seed1234 (reserved main eval73517 untouched); two mixed ARC arms, 1,500 updates, batch32, 16 tasks/cell,
  plus both architectures on identity/fixed-rotation/random-colour controls, 500 updates, TTT off for controls.
  Shared widths64/depth2; default rates narrative .002, ARC .001. Mixed ARC TTT16 at .001. Pilot timeouts900s
  (mixed/narrative) and600s (controls); no main runs yet. Main seeds remain1/2/3. In irreversible depth1 only,
  use input-heldout primitive controls because crop and gravity are singleton functions; depths2–4 retain
  program-hash separation. Fixed-canvas crop means crop-to-origin then zero-pad, not variable-size ARC crop.
- 2026-10-20: Astra hit her usage limit (resets 27 Oct) after the tests and seed-0 pilot launch. Argon (Gemini, agy CLI) takes over from this Log; brief in Claude's scratchpad argon-next.md.
- 2026-10-20 20:16 UTC — Argon (Gemini) resumed `next_pilot1` and `next_pilot2`, settled the 6 completed Modal calls and
  ran the remaining 6 seed-0 pilot calls to completion (all 12 pilot jobs complete, 0 errors; conservative settled
  spend $0.371512 Exp 1 + $0.554111 Exp 2 = $0.925623 total). Tabulated all seed-0 pilot outcomes and froze/committed
  main-grid protocols (`main1.json` 12 jobs, `main2.json` 24 jobs, seeds 1/2/3) and numeric pass/fail predictions (H1,
  P1.1–P1.3, H2, P2.1–P2.4) in `NEXT.md` before planning or launching any main run.
