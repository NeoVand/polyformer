# Audit reruns: registration (written before any rerun was launched, 24 Oct 2026)

Independent auditor: a session that wrote none of the experiment code. One seed of O and one of FULL+N per domain,
from a clean export of the commit that produced the records (`git archive`, never the audited worktrees), with a
`--tag` so no original record is overwritten. Runs are not bitwise reproducible across containers (each domain's
auditor found float non-determinism), so each comparison is a registered tolerance, not equality.

| domain | arm, seed | commit exported | expected (record) | registered pass criterion | where | est. cost |
|---|---|---|---|---|---|---|
| code | O, s0 | exec-d `d5fc861` (exec_lm_run.py 812c2867) | exact_64x 0.0293 (15/512); floor_acc_last[1024] 0.423828125 | exact_64x < 0.10, and floor_acc_last[1024] = 0.423828125 exactly with n = 512 (data fingerprint) | Modal `exec_lm_modal.py` | ~$0.60 |
| code | FULL+N (RNLIr), s0 | same | 1.000 (512/512) | ≥ 0.99 (≥ 507/512), same data fingerprint | Modal | ~$1.40 |
| add | O (R), s0 | exec-d `dcd126c` | 0.000 at 4,096 | < 0.99 (expected ≈ 0) | Modal | ~$0.21 |
| add | FULL+N (RNLIr), s0 | same | 1.000 at 4,096 | ≥ 127/128 | Modal | ~$0.38 |
| count | O (R), s0 | same | 0.094 at 4,096 | between 7 and 20 of 128 (chance band) | Modal | ~$0.18 |
| count | FULL+N (RNLIr), s3, `--select_after 600` | same | 1.000 at 4,096, step 750 | ≥ 127/128, selected step ≥ 600 | Modal | ~$0.40 |
| lean | O, s0 | lean-s `189485a` | 0.430 at 1,024 (another identical-config run gave 0.469) | not exact (< 0.99); value in 0.35–0.55 | Modal H100 | ~$0.24 |
| lean | FULL+N, s0 | same | 1.000 at 1,024 and 4,096 | ≥ 0.99 at 1,024 | Modal H100 | ~$0.34 |
| s5 | O, s0 | invariance `4fd9c75` | 0.533 at 1,024; step-1 CE 5.19 | not exact (< 0.99); step-1 CE 5.19 | local CPU (free) | $0 |
| s5 | FULL+N, mu 0.1, s0 | same | 1.000 at 1,024; step-1 loss 5.3014 | ≥ 0.99 (≥ 507/512); step-1 loss 5.3014 to 4 decimals | local CPU (free) | $0 |
| stories | O, s10 | lean-n-data `d5640d0` | 0.000 (0/128) | ≤ 0.02 | Modal L4 | ~$0.34 |
| stories | FULL+N, s10 | same | 1.000 (128/128) | ≥ 127/128 | Modal L4 | ~$0.34 |

Estimated Modal total about $4.5, under the $15 cap. **The Modal rows wait for Neo's explicit go-ahead to this
session** (AUDIT_BRIEF.md: "needs Neo's go"); the S5 rows run on a local CPU at no cost.

A rerun that misses its criterion is reported as a discrepancy with the full record; nothing is rerun to get a pass.

## Results (appended after the runs; the registration above is unchanged)

S5, run 24 Oct 11:26–11:33 on a local CPU (Apple M4; jax 0.12.0, optax 0.2.8, numpy 2.5.4, the Modal image's pins)
from `git archive 4fd9c75`. The sources the training path uses (`invariance.py`, `validation_models.py`,
`validation_run.py`, `validation_tasks.py`, `groups.py`, `events_data.py`) hash identically to the record manifest
`inv_r3.json` (commit 669b3d3). `invariance_run.py` differs only by the added ablation summary (`ABL_ARMS`,
`ablation()`) and the `ORDER` list, with no change on the training or evaluation path. The original records ran on
Modal CPU containers (x86, 2–4 cores). Records and logs: `s5/rerun/`.

| run | record at 1,024 | rerun at 1,024 | step-1 loss, record / rerun | curves identical through | criterion | verdict |
|---|---|---|---|---|---|---|
| O, s0 | 0.533 (273/512) | 0.486 (249/512) | ce 5.19 / 5.19 | step 400 (first difference at 500: 2.9343 vs 2.9026) | not exact; step-1 CE 5.19 | **pass** |
| FULL+N, mu 0.1, s0 | 1.000 (512/512) | **0.988 (506/512)** | 5.3014 / 5.3014 (ce 5.1913, inv 0.5679, ns_kl 0.0268, ns_sl1 0.0266 in both) | step 100 (first difference at 200: 4.1448 vs 4.1447) | ≥ 507/512; step-1 loss 5.3014 | **fail by one sequence** |

FULL+N rerun at the other lengths: 1.000 at 16 and 64, 0.994 (509/512) at 256, 0.988 at 1,024. The mean over events
at 1,024 is 0.990 (record 1.000). Per the registration it was not rerun.

The Modal rows (code, add, count, lean, stories) were not launched. They wait for Neo's go-ahead.

## Launch protocol and where this stopped (24 Oct, about 11:50)

Not launched: Neo had not answered the go-ahead question when the laptop was due to close. Nothing is running on
Modal for this audit, and no call ids exist.

When Neo approves, launch so the runs survive the laptop sleeping:
1. Make a clean export of each domain's commit (`git archive`), never the audited worktrees.
2. `modal deploy` the app.
3. Call `.spawn()` from a script that exits. Do not use `modal run --detach` with a live client: one was cancelled
   when the laptop slept on the morning of 24 Oct.
4. Write results to a separate audit volume (for example `polyformer-audit`).
5. Commit the spawned call ids to this file before the laptop closes.
6. Collect later, and score each run against the registered criterion above.

## Launched (24 Oct 11:47:58, on Neo's go-ahead to this session)

The ten Modal reruns were spawned on the deployed app `polyformer-audit` (`audit/modal/audit_modal.py`, deployed 11:47).
`audit/modal/launch.py` spawned them, recorded the call ids in `audit/modal/calls.json`, and exited. No live client
holds them. Results and full logs go to the Modal volume `polyformer-audit` under `/<job id>/`.

Exports baked into the image:
| domain | export | key code hash | data file |
|---|---|---|---|
| code | `d5fc861` | `exec_lm_run.py` 812c2867 | `feats_mid.npz` 90af782d |
| add, count | `dcd126c` | `exec_arith.py` ec07ac85 | `arith_feats.npz` 2ba3d5ef (committed) |
| lean | `189485a` | `lean_run.py` 8eab3f7c | `a4x.npz` 26a08608 |
| stories | `d5640d0` | — | — |

Images use the original pins.

Hardware: code and arithmetic on 8–16 CPUs; lean on H100; stories on L4 with 2 CPUs.

Collect a run with `modal.FunctionCall.from_id(<call id>).get()`, or read the volume
(`modal volume get polyformer-audit <job id>`). Then score each run against its registered criterion above.

### Results as they arrive

| run | record | rerun | step-1 loss, record / rerun | curves identical through | criterion | verdict |
|---|---|---|---|---|---|---|
| lean O, s0 (H100, 82.6 s) | 0.430 at 1,024; an identical-config run gave 0.469 | **0.766** at 1,024 (1.000 / 0.986 / 0.898 / 0.766 / 0.609 at 8 / 64 / 256 / 1,024 / 4,096) | 3.6619 / 3.6619 | step 100 (first difference at 200: 0.9910 vs 0.9909) | not exact, and in 0.35–0.55 | **fail on the band**; "not exact" holds |
| lean FULL+N, s0 (H100, 157.9 s) | 1.000 at 1,024 and 4,096 | 1.000 at 8, 64, 256, 1,024 and 4,096 | 3.9089 / 3.9089 (ce 3.6886, inv 0.1913, nl_h 0.1107, nl_kl 0.1096: all as expected) | step 1 (first difference at 100: 1.3025 vs 1.3023) | ≥ 0.99 at 1,024 | **pass** |
| code O, s0 (8–16 CPU, 2,000 s) | 0.0293 (15/512) | 0.0293 (15/512); floor_acc_last[1024] 0.423828125, n 512 | 1.04076 / 1.04076 | every logged step (identical) | < 0.10 and fingerprint | **pass** |
| code FULL+N, s0 (5,009 s) | 1.000 (512/512) | 1.000 (512/512); same fingerprint | 1.08094 / 1.08094 | every logged step (identical) | ≥ 507/512 and fingerprint | **pass** |
| add O, s0 (427 s) | 0.000 at 4,096 | 0.000; selected step 500 in both | 2.85156 / 2.85156 | step 1 (first difference at 100) | < 0.99 | **pass** |
| add FULL+N, s0 (1,258 s) | 1.000 | 1.000 (128/128); selected step 1,000 in both | 2.89553 / 2.89553 | every logged step (identical) | ≥ 127/128 | **pass** |
| count O, s0 (572 s) | 0.094 (12/128) | 0.094 (12/128); selected step 250 | 2.66546 / 2.66546 | every logged step (identical) | 7–20 of 128 | **pass** |
| count FULL+N, s3, `--select_after 600` (1,180 s) | 1.000 | 1.000 (128/128); selected step 750 | 2.8501 / 2.8501 | every logged step (identical) | ≥ 127/128, step ≥ 600 | **pass** |
| stories O, s10 (L4, 966 s) | 0.000 (0/128) | 0.000; every length and per-step mean identical | step-0 CE 1.87252 / 1.87252 | every logged step (identical) | ≤ 0.02 | **pass** |
| stories FULL+N, s10 (1,153 s) | 1.000 (128/128) | 1.000; every length identical; 4,000 steps done | step-0 CE 1.87277 / 1.87277 | every logged step (identical) | ≥ 127/128 | **pass** |

Lean O config differs from both earlier records only in bookkeeping (`outdir`, `tag`, `seeds`, `pair_mult` no-op,
`fixed_norm` None vs False). So O's value at 1,024 moves between 0.43 and 0.77 under float-level differences alone.
The registered band assumed ±0.05 and was too narrow. Record: `audit/modal/results/lean_O_s0.json`.

Collected 24 Oct 12:52 CDT (the laptop moved from EDT to CDT; container logs give the spawn as 15:47:58 UTC). All
ten returned code 0. Scoring: `audit/modal/score.py` → `audit/modal/score.json`. Spend: Modal's billing report for
24 Oct gives $2.38 for the app `polyformer-audit` (CPU $1.23, L4 $0.51, H100 $0.45, memory $0.18).

## Balanced long-carry check (registered before evaluation, 24 Oct 12:57 CDT, commit ced74c2; free, local CPU)

**Why.** EXEC_LM section 19 (A) answers D1 with a long-carry set. In that set every chain is started by a pair
summing to at least 10, so the final carry is 1 in 512 of 512 programs. The audit recomputed two floors on the exact
sets (`audit/arith/long_carry_floor.py`, `long_carry_floor.json`):
- a window-8 rule that resets the carry to 0 scores 0.000 at 1,024 and 4,096, matching the stored floor;
- the same rule assuming a carry of 1 into the window scores **1.000** at both lengths.

So the set shows the arms do not reset the carry. It cannot show that they hold it rather than assume it.

**Check.** Evaluation only, on the selected parameters section 19 saved (`polyformer-exec-lm-results/ctl_add_<arm>_s<seed>/`),
for the normed arms O+N, NS+N, EQ+N and FULL+N on seeds 6–8. No training.
- **Fidelity first:** each checkpoint must reproduce its record's `long_carry_1024` answer_exact exactly. If it does
  not, the check is void for that checkpoint.
- **Balanced set:** `sample_long_carry`'s construction, seed 7777 + length, n = 512 at 1,024 and 4,096. In half the
  programs (alternating) the item before the chain sums to at most 8, which kills any carry, so that chain carries 0.
  The other half is unchanged and carries 1.
- **Floors** reported on the balanced set: window-8 with the carry reset to 0, and with it reset to 1. Both are
  expected near 0.5.

**Registered criterion.** An arm holds the carry if answer_exact ≥ 0.99 at 4,096 on the balanced set, with both halves
≥ 0.98. An arm that assumes a carry scores about 0.5: the carry-0 half fails. D1 is resolved if FULL+N holds the carry
on 3 of 3 seeds. The other arms are reported without a prediction.

**Result** (evaluated 12:58–13:10 CDT on a local CPU; `audit/arith/balanced_long_carry.json`).

Floors on the balanced set: the final carry is 1 in half the programs (0.500). Window-8 scores 0.500 with the carry
reset to 0 and 0.500 with it reset to 1.

Every checkpoint passed the fidelity check: each reproduced its record's long-carry answer at 1,024 (1.000 = 1.000).

| arm | seed 6, at 4,096 (carry-1 / carry-0 half) | seed 7 | seed 8 |
|---|---|---|---|
| O+N | 1.000 (1.000 / 1.000) | 1.000 (1.000 / 1.000) | 1.000 (1.000 / 1.000) |
| NS+N | 1.000 (1.000 / 1.000) | 1.000 (1.000 / 1.000) | 1.000 (1.000 / 1.000) |
| EQ+N | 1.000 (1.000 / 1.000) | 0.990 (1.000 / 0.980) | 1.000 (1.000 / 1.000) |
| FULL+N | 1.000 (1.000 / 1.000) | 1.000 (1.000 / 1.000) | 1.000 (1.000 / 1.000) |

At 1,024 every cell is 1.000 except EQ+N s7 (0.998).

**Registered criterion met:** FULL+N holds the carry on 3 of 3 seeds (512/512, both halves 256/256), so D1 is
resolved. Every other normed arm also meets the criterion. The closest is EQ+N s7: 507/512 overall, 251/256 on the
carry-0 half.
