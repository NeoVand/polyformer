# AUDIT: an independent check of the master table (24 Oct 2026)

The auditor is a Claude session that wrote none of the experiment code. It followed `research/AUDIT_BRIEF.md`.
Everything was read-only on the audited worktrees: nothing was edited, committed or stashed there. Scripts, outputs
and rerun records are in `research/audit/`. The reruns were registered, with their tolerances, in
`research/audit/RERUNS.md` before any was launched.

**Approval and spend.** AUDIT_BRIEF.md says "needs Neo's go". The free checks (1–4) and the two free S5 reruns
(local CPU) ran first. Neo then gave the go-ahead directly to this session. The ten registered Modal reruns were
spawned at 11:47:58 EDT on 24 Oct and collected at 12:52 CDT. Modal's billing report puts the `polyformer-audit` app
at **$2.38** for 24 Oct (CPU $1.23, L4 $0.51, H100 $0.45, memory $0.18), against the $15 cap.

**What was audited**

| Item | Location | Commit |
|---|---|---|
| code, add, count | `exec-d-0e1910` | records at `dcd126c`; HEAD moved to `78cf2cf` during the audit (section 18 only; records unchanged, re-verified) |
| lean | `lean-s-2b865a` | `189485a` |
| s5 | `invariance-3e22f3` | `4fd9c75` |
| stories | `lean-n-data-34a2d2` | `d5640d0` |
| master table | `notes-2026-10-22/research/master/build_master.py` | `a001d03`; then `4b4f973` (11:33), which fixed counting FULL+N during the audit |

## Verdicts

| Check | code | lean | s5 | add | count | stories |
|---|---|---|---|---|---|---|
| 1. Provenance: master number → raw record | pass | pass | **fail** (D5, D6) | pass | pass at `4b4f973`; **fail** at `a001d03` (D3) | pass |
| 1. Provenance: record → code and config | pass (manifest hashes) | pass (manifest hashes) | pass (manifest hashes) | pass (manifest hashes; D13) | pass (manifest hashes; D13) | partial: config in record, commit from git history only (D13) |
| 2. Selection after every term is on, never on test lengths | pass | pass (no selection) | pass (no selection) | pass | **fail** (D3, D2) | pass (no selection) |
| 2. Test sets disjoint from training (hashed) | pass | pass | pass | pass | pass | pass |
| 2. Config differs from O only in intended flags | pass | pass | pass | pass | pass (D2: the FULL+N seeds have no same-seed O) | pass |
| 2. Same exact-metric definition | pass (D9) | pass, mislabelled (D7, D9) | pass (D9) | pass (D9) | pass (D9) | pass (D9) |
| 3. Leakage, by reading code | pass | pass (D12) | pass | pass | pass | pass for the table's arms; soft arm not simulator-free (D10) |
| 4. Shallow floor at chance at the long length | **fail**: 0.424 (D8) | **fail**: 0.27 (D8) | pass | **fail**: 1.000 (D1) | pass (D8) | pass (D8) |
| 5. Rerun O, one seed | **pass** (identical) | **fail on the value band**; not exact holds (D16) | **pass** | **pass** (same value) | **pass** (identical) | **pass** (identical) |
| 5. Rerun FULL+N, one seed | **pass** (identical) | **pass** | **fail by one sequence** (D4) | **pass** (identical) | **pass** (identical, step 750) | **pass** (identical) |

## What changes for the paper

*Status after the fixes (EXEC_LM §19, `build_master.py` at `2854f81`): see "Status of the findings after the fixes"
below. Resolved: D1, D2, D3, D5, D6, D7 (table), D11. Partly resolved: D4, D8, D9, D13, D15. Open: D10, D12, D14,
D16. New: N1–N4.*


1. **Addition at 128× does not show long-range state** (D1). A rule that sees only the last 8 items is exact on the
   4,096-item test set. The column shows that the fixed norm prevents blow-up over 4,096 steps, not that the state
   carries information across them.
2. **The counting column cannot attribute exactness to the signal** (D2). Under the selection rule, the signal arms
   are read at step 750 and O+N and NS+N at step 250. The 3/3 vs 2/3 difference is also within binomial noise at
   n = 128.
3. **The S5 FULL+N "3/3" sits on the threshold** (D4). A same-code, same-seed rerun gives 506/512 = 0.988, one sequence
   short of 0.99.
4. **Table fixes** (D5, D6, D7, D9): the S5 EQ+N cell uses the μ that validation rejected; S5 cells print 0/1 instead
   of fractions; the Lean column is 128×, not 64×; n differs by column (128 to 512).
5. **A wrong number in CONTRIBUTIONS.md** (D11): E7's "no signal 0.630" is a per-step mean placed among exact-at-end
   values. The exact-at-end value is 0.594.
6. **The reruns confirm the table where it was checked, with two exceptions.** 10 of 12 reruns pass their
   registered criteria; 7 of the 10 Modal reruns reproduce their records exactly (D14). The exceptions:
   - S5 FULL+N s0 lands one sequence under 0.99 (D4).
   - Lean O's value is noise at about ±0.2 (D16); its verdict, not exact, stands.

## Status of the findings after the fixes (24 Oct, 13:00 CDT)

Checked by this auditor (read-only) at exec-d `0cbbfb3` (EXEC_LM §19: registered at `cddf91f` 11:53, spawned 11:55,
results `df0b45f` and `0cbbfb3` 12:53–12:54), at `notes-2026-10-22` `2854f81` (`build_master.py`, `master_table.md`,
`CONTRIBUTIONS.md`), and on the unchanged Lean (`189485a`), S5 (`4fd9c75`) and stories (`d5640d0`) worktrees.

What was verified:
- **The table builder:** reproduces the committed `master_table.md` at `2854f81` exactly (`audit/rebuilt_master_2854f81.md`).
- **The §19 records** (`audit/arith/s19_check.py`):
  - all 30 store `select_after` 600, select at step 750–1,250, and test n = 512 at every length;
  - ABLATION_arith.json's 30 §19 rows equal the raw records, uniform and long-carry, with 0 mismatches;
  - the stored window floors equal the audit's own computation.
- **A new, registered check** of what the long-carry set shows (below, and D1 in the table).

| # | finding | status | evidence |
|---|---|---|---|
| D1 | addition floor 1.000 at 4,096 | **resolved** | See note D1 below. |
| D2 | counting confounded by training steps | **resolved** | See note D2 below. |
| D3 | counting FULL+N selected before onset | **resolved** | Fixed at `4b4f973`. Superseded at `2854f81` by the §19 rows, which all select after step 600. |
| D4 | S5 FULL+N rerun 506/512 | **partly resolved** | The table now prints S5 fractions (FULL+N 1.000 / 0.998 / 0.998). Still missing: intervals, larger n, and the Methods sentence on hardware. |
| D5 | S5 EQ+N cell used the rejected μ | **resolved** | `build_master.py` keeps only `chosen_on_validation` records. The EQ+N cell is 0.867 / 0.893 / 1.000, which is μ = 1 (`0e378cf`). |
| D6 | S5 printed 0/1 | **resolved** | Reads `acc_last_64x`: O 0.533 / 1.000 / 1.000; O+N 0.713 / 0.777 / 1.000. |
| D7 | Lean labelled 64× | **resolved in the table** | The header reads "Lean (8 to 1,024; 128x)", and every column states its length ratio. The record fields are still named `exact_64x`, which is cosmetic. |
| D8 | floors missing; code and Lean above chance | **partly resolved** | See note D8 below. |
| D9 | n differs by column | **partly resolved** | Arithmetic is n = 512 with Clopper–Pearson intervals in ABLATION_arith.json (§19). Lean (256), stories (128) and the arithmetic FULL rows (128) are unchanged. The table states no n. |
| D10 | stories soft arm not simulator-free | **open** | Stories worktree unchanged since the audit. |
| D11 | CONTRIBUTIONS E7 mixed metrics | **resolved** | E7 reads "no signal 0.594 / 0.312 / 0.672 (exact at the end)" (`0e378cf`). |
| D12 | Lean has no validation split | **open** | Disclosure only; Lean worktree unchanged. |
| D13 | records lack code, data and hardware identity | **partly resolved** | §19 records store `select_after` and `selected_step`, and save the selected parameters. No record stores a commit, hashes or hardware. The stories builder is still uncommitted. |
| D14 | reproducibility across hardware | **open** | Methods sentence not yet written. |
| D15 | text mismatches | **partly resolved** | EXEC_LM 16.3 is marked superseded for counting (line 1743). The other items were not re-checked. |
| D16 | Lean O spread about ±0.2 | **open** | The table prints Lean O as point values (0.430 / 0.000 / 0.891). Report it as "not exact" with the spread. |

**D1.** Two pieces of evidence, together:
- **§19 long-carry set:** the window-8 floor that resets the carry to 0 scores 0/512. But the set is one-sided (N1),
  so that alone does not show the arms hold the carry.
- **The registered balanced check** (`audit/RERUNS.md`; `audit/arith/balanced_long_carry.py`, `.json`):
  - All 12 normed checkpoints (O+N, NS+N, EQ+N and FULL+N on seeds 6–8) reproduce their recorded long-carry score.
  - On the balanced set they are exact at 4,096. FULL+N scores 512/512 on 3 of 3 seeds, with both halves 256/256.
  - Both window-8 floors on that set are 0.500.

The arms hold a carry across chains of up to about 4,000 items. Remaining fix: report the balanced result next to
the long-carry column (N1).

**D2.** EXEC_LM §19.2 is the control the audit asked for:
- every counting arm (O, O+N, NS+N, EQ+N, FULL+N) on fresh seeds 6–8;
- one selection rule after step 600, so every arm is read at step 750;
- n = 512 at 4,096.

Results:

| arm | exact at 4,096 |
|---|---|
| NS+N | 3/3 (512/512 each) |
| EQ+N | 3/3 (512/512 each) |
| FULL+N | 3/3 (512/512 each) |
| O+N | 1/3 (507, 503, 465 of 512) |
| O | 0/3 (0.090–0.137, at chance) |

The earlier attribution of counting to the signal was the step confound: next-state prediction plus the norm is enough.

**D8.**
- **Arithmetic:** §19 stores window floors in every record (counting 0.098 at 4,096; addition 1.000 uniform, 0.000
  long-carry).
- **Lean, S5 and stories:** their records still have no floor, and LEAN_S1 still calls 0.008 "chance" (line 239).
- **The table:** prints no floor row.

### New findings in this pass

- **N1. The long-carry set is one-sided.** Every chain is started by a pair summing to at least 10, so the final carry
  is 1 in 512 of 512 programs. The window-8 floor that resets the carry to 0 is 0.000, as §19 reports, and the audit
  reproduces it. The same rule assuming a carry of 1 scores **1.000** at 1,024 and 4,096
  (`audit/arith/long_carry_floor.json`). So L1 shows the arms do not reset the carry, not that they hold it.
  The registered balanced check settles it for the models.
  - In half the programs the chain is started by a pair summing to at most 8, so it carries 0. Both window-8 floors
    then score 0.500.
  - Every normed arm still scores at least 0.990 at 4,096 on 3 of 3 seeds.
  - The closest is EQ+N s7: 507/512, with 251/256 on the carry-0 half.
  - The evaluation used the saved selected parameters; each reproduced its record's long-carry score at 1,024 first.
  - Fix: add the balanced set to the long-carry column, or note this check beside it.
- **N2. The arithmetic columns mix two sources.** O to FULL+N come from §19 (seeds 6–8, n = 512); FULL comes from the
  original runs (seeds 0–2, n = 128 at 4,096, also selected after step 600). Fix: footnote the FULL cells, or rerun FULL
  under §19.
- **N3. CONTRIBUTIONS E6 is stale.** It still reads "counting: ordinary at chance (0.1), recipe 0.984-1.000" and "one
  full seed pending", and it presents uniform addition without the long-carry result. Fix: restate E6 from §19.
- **N4. The builder reads the worktrees' working files, not pinned commits.** The table therefore changes whenever a
  worktree moves. Fix: read each ABLATION file with `git show <commit>:<path>` and print the commits under the table.

## Discrepancies, with evidence and fix

### D1. Addition: the shallow floor is 1.000 at 4,096 (check 4)
- **Evidence** (`audit/arith/floors.py`, `floors.json`):
  - The rule computes the answer from the last k items only, with the carry reset to 0 before the window. It is
    scored on the exact test programs of `exec_arith.py` (seed 4873, n = 128).
  - At 4,096 it scores 0.000 for k ≤ 3, 0.141 for k = 4, 0.820 for k = 5, 0.977 for k = 6, and **1.000 for k ≥ 8**.
    At 32 it is already 1.000 for k = 6.
  - The cause: digit pairs are uniform (`exec_arith.py:120`), so a carry crosses a run of pairs summing to 9 only with
    probability 0.1 per item. Runs of 8 almost never occur.
  - O fails at 4,096 (0.000) through state-norm blow-up, from about 4–6 to 1,662–1,967, not because the task needs
    long memory.
  - No floor is stored in any arithmetic record. The results dict at `exec_arith.py:378–382` has none, while
    `exec_lm_run.py:316–319` does.
- **Fix**, either of:
  - (a) Add a long-carry test set, where a carry is generated early and then propagates through a run of pairs
    summing to 9 for hundreds of items, so that every window rule with k ≪ L fails. Then report the floor next to the
    arms. If the selected checkpoints were saved, this is evaluation only; otherwise it needs the arms retrained.
  - (b) Present addition as a closure result (no blow-up at 128×) and print the floor 1.000 in the table.

### D2. Counting: the arm comparison is confounded by training steps (check 2)
- **Evidence:**
  - On counting, validation is 1.000 at every one of the 12 checkpoints for every arm (11 of 12 for O s1). The
    selected step is therefore set by the rule, not the data.
  - Rule-set steps: 250 for O, O+N and NS+N (`select_after` 0); 750 for EQ+N and the fresh FULL+N (`select_after`
    600). The `select_after` value is in the manifests only, not in the result records.
  - The reading "the signal closes the gap" (EXEC_LM 14.1, 16.2, 16.3: FULL+N 3/3 against NS+N 2/3 and O+N 1/3)
    cannot be separated from 500 extra training steps.
  - The splits are also within noise:
    - The misses are 126/128 (NS+N s1) and 127, 126, 124 of 128 (O+N).
    - A model with true accuracy 0.99 passes ≥ 127/128 only 63% of the time.
    - 128/128 has a one-sided 95% lower bound of 0.977.
  - The counting FULL+N row in `4b4f973` uses seeds 3–5. Every other counting row uses seeds 0–2, so the FULL+N row
    has no same-seed O, O+N or NS+N.
  - "Identical to NS+N" (EXEC_LM 14.1, 16.4, 17) is false for seed 2: training loss at step 100 is 0.64086 against
    0.60888 with the signal weight still 0.
- **Fix:**
  - Register and run count O, O+N and NS+N with `--select_after 600`, on the seeds of the FULL+N row (3–5), or all arms
    on 0–2. That is about $1.2–2.4.
  - Evaluate at 4,096 with n = 512.
  - Until then, the counting column supports "next-state + norm is near-exact; O is at chance", not an attribution to
    the signal.
  - Store `select_after` in every record.

### D3. Counting: registered FULL+N selected before onset (known; now fixed in the table)
- **Evidence:**
  - `ARITH_count_RNLIr_s{0,1,2}.json` were selected at step 250, with the equivalence weight at 0 (fully on from step
    600, `exec_arith.py:308–309`). `ABLATION_arith.json` at `dcd126c` flags them `selection_bug`.
  - The master table at `a001d03` used them (count FULL+N 2/3) and dropped the arm labelled
    "FULL+N (fresh seeds, uniform rule)".
  - At `4b4f973` the builder excludes the three, lists them in a note, and maps seeds 3–5 to FULL+N: 3/3, selected
    step 750 ≥ 600 on all three.
  - The builder reproduces the committed table exactly at both commits (`audit/rebuilt_master_a001d03.md`, `audit/rebuilt_master_4b4f973.md`).
  - The post hoc reselections `*_sel.json` (rule written after the results were seen) are marked
    `not_used_in_the_table`. Correct.
- **Searched everywhere for the same failure** (selection at or before a term's onset). None outside these three
  records:

  | domain | term fully on | earliest selected step in a delayed-term arm |
  |---|---|---|
  | code | 1,200 | 12,500 |
  | add | 600 | 750 |
  | count, other arms | 600 | 750 |
  | lean | 3,600 | no selection; read at 12,000 |
  | s5 | step 1 | no selection; read at 4,000 |
  | stories | 1,200 | no selection; read at 4,000 |

- **Fix:** done in the table. The cell or its footnote should still say "seeds 3–5" (see D2).

### D4. S5 FULL+N rerun: 506/512, one short of the criterion (check 5)
- **Evidence** (`audit/RERUNS.md`, results; records in `audit/s5/rerun/`):
  - Run from `git archive 4fd9c75` on a local Apple M4 CPU, with the image's pins.
  - Training-path sources hash identically to the record's manifest (`inv_r3.json`, commit 669b3d3).
    `invariance_run.py` differs only by the added ablation summary.
  - Step-1 loss is 5.3014 in both, with every component equal. The curves are identical through step 100 and first
    differ at step 200 (4.1448 vs 4.1447).
  - Result: 1.000 at 16 and 64, 0.994 at 256, **0.988 (506/512) at 1,024**, against the record's 1.000 (512/512).
  - The O rerun passes: 0.486 against 0.533, not exact, step-1 CE 5.19.
  - The original ran on Modal x86 CPU containers (2–4 cores). Float accumulation differs by hardware, and here that
    moved 6 of 512 sequences.
  - The other S5 seeds already sit at 511/512 (FULL+N s1, s2), and NS+N s0 at 509/512.
- **Fix:**
  - Report S5 (and every domain) as fractions with Clopper–Pearson intervals, not only as k/3 counts.
  - Evaluate the long length on more sequences (4,096 is cheap on CPU for S5) so that 0.99 and 1.0 can be told apart.
  - State in Methods that runs are not bitwise reproducible across hardware (see D14).
  - Optional: a separately registered Modal-CPU rerun of the same job (about $0.06) would separate hardware from run
    noise. Its result would be reported either way; it would not replace this one.

### D5. S5: the master's EQ+N cell uses the μ validation rejected (check 1)
- **Evidence:**
  - `build_master.py` keeps only μ = 0.1 for S5, with the comment "validation-chosen mu = 0.1".
  - `ABLATION_S5.json` marks μ = 1.0 as `chosen_on_validation` for EQ+N: mean last-event accuracy at e = 256 is 0.99609
    vs 0.96484 (`invariance_run.py:555–563`; reproduced exactly).
  - Shown: 0.615 / 0.783 / 0.998. Chosen: 0.867 / 0.893 / 1.000. Both are 1/3.
  - FULL+N and FULL did choose 0.1.
- **Fix:** in `build_master.py`, `if dom == "s5" and not r.get("chosen_on_validation", True): continue` in place of the
  μ = 0.1 filter.

### D6. S5: the master prints 0/1 instead of the fraction (check 1)
- **Evidence:**
  - S5's `exact_64x` is a boolean, and the builder converts it to 1.0 or 0.0.
  - O s0 shows 0.000 (actual 0.533); O+N s0 and s1 show 0.000 (0.713, 0.777).
  - The k/3 counts are unaffected.
- **Fix:** read `acc_last_64x` for S5.

### D7. Lean: "64×" is 128× and "256×" is 512× (check 2)
- **Evidence:**
  - Training chains have 8 rewrites. `exact_64x` is read at 1,024 and `exact_256x` at 4,096 (`lean_s_ablation.py:16`).
  - No verdict flips: O is already not exact at 256 on 3/3, and FULL+N is 1.000 at 256, 1,024 and 4,096.
- **Fix:** a column footnote ("Lean: 1,024 = 128×; 4,096 = 512×"), or rename the fields.

### D8. Floors are missing from four domains, and two are well above chance (check 4)
Floors computed by the audit at the long length, on the exact test sets:

| domain | shallow floor | chance | best arm | recorded in the records? |
|---|---|---|---|---|
| code | 0.424 (last write per variable) | 1/16 = 0.0625 (4 active bits); best constant 0.295 | 1.000 | yes, `floor_acc_last` |
| lean | 0.273 (start + last event); 0.324 at 4,096 | uniform in the start's class 0.058; uniform 1/960 = 0.001 | 1.000 | no |
| s5 | ≤ 0.020 (parity only; others ≤ 0.010) | 1/120 = 0.008 | 1.000 | no |
| add | **1.000** (last 8 items) | — | 1.000 | no (D1) |
| count | 0.070–0.109 (constant, last word, last-k counts) | 0.1; 95% band 7–20 of 128 | 1.000 | no |
| stories | 0.000 (last event only); 0.102 for a partial tracker | 6.4e-5 | 1.000 | no |

- **Code:** the floor is far below the 0.99 bar, so no exact cell is explained by it. But O+N s2 (0.484) is only
  +0.061 above it, under EXEC_LM's own "tracks" margin of +0.10. O (0.021–0.029) is below the best constant: it is
  confidently wrong, not at chance.
- **Lean:**
  - LEAN_S1 calls 0.008 "chance". A chain stays inside its start's class (52 classes of size 8, 24 or 120), so a
    history-free rule scores 0.27–0.32 at long lengths.
  - O s0 (0.430) is only +0.16 above that floor.
- **Fix:**
  - Store a floor in every domain's records (the scripts in `audit/*/floors.py` compute them).
  - Print the floor under each column of the master table.
  - Correct "chance" in LEAN_S1.

### D9. The exact metric has the same definition everywhere but not the same resolution (check 2)
- **The definition is the same in every domain:** the fraction of test sequences whose whole final state is right,
  exact at ≥ 0.99, on the final or selected checkpoint.
- **What differs:**

  | domain | training → long length | multiple | n at the long length | errors allowed at 0.99 |
  |---|---|---|---|---|
  | code | 16 → 1,024 | 64× | 512 | 5 |
  | lean | 8 → 1,024 | 128× | 256 | 2 |
  | s5 | 16 → 1,024 | 64× | 512 | 5 |
  | add | 32 → 4,096 | 128× | 128 | 1 |
  | count | 32 → 4,096 | 128× | 128 | 1 |
  | stories | 16 → 1,024 | 64× | 128 | 1 |

- **Fix:** state the length and n per column. Report intervals. Raise n to 512 where it is cheap: arithmetic and
  stories.

### D10. Stories: the soft arm is not simulator-free (check 3; not in the master table)
- **Evidence:**
  - The cross-entropy targets for both stories of every accepted pair, including the 125 wrong pairs, are simulator
    states (`stories_track.py:201–205`).
  - The proposal pool is 80% certified-equal by construction (`stories_soft.py:106–129`).
  - The bge-m3 threshold of 0.998 was chosen using simulator labels on 3,000 pairs (`stories_soft.py:84–96`).
  - `label_for_measurement_only` is only counted, never used in the loss.
- **Fix:** describe the soft arm as "soft pair selection under simulator state supervision", or remove simulator
  states from its pairs' targets and from the threshold choice, before claiming a soft checker suffices (CONTRIBUTIONS
  E8).

### D11. CONTRIBUTIONS.md E7 mixes two metrics
- **Evidence:**
  - "no signal 0.630 / 0.312 / 0.672": 0.630 is seed 10's per-step mean at 1,024 (`exact_per_step_mean` 0.6296; STORIES
    line 64).
  - 0.312 and 0.672 are exact at the end. Seed 10's exact-at-end value is 0.594, as the master table shows.
- **Fix:** "no signal 0.594 / 0.312 / 0.672".

### D12. Lean: no validation split (check 3)
- **Evidence:**
  - The LEAN_S1 pilots read the eval arrays at 8, 64, 256 and 1,024 to choose the position-wise head (RIp_a4 1.000 at
    256 against 0.004 for the decoder head).
  - That choice is shared by all arms, so it is not label leakage. The 4,096 split was never seen by the pilots.
- **Fix:** disclose it in Methods, and name 4,096 as the untouched length.

### D13. Records do not identify their own code or data
- **Evidence:**
  - No raw record stores a commit or a source hash.
  - Manifests do, for code, arithmetic, lean and S5. The exec-lm worker refuses to run on a hash mismatch.
  - Stories has neither. Its code version (4d5b335; reused O+N and EQ+N runs from 622be12 and 7bb9baf) was inferred
    from git history and diffs.
  - `host` defaults to "modal" whatever the host (`exec_lm_run.py:435`).
  - Data files are gitignored: `feats_mid.npz` (sha256 `90af782d…`), `arith_feats.npz` (`2ba3d5ef…`), `a4x.npz`
    (`26a08608…`).
  - The Hugging Face revisions are unpinned (`lm.revision` null; stories built three images).
  - `select_after` lives only in manifests, and `ABLATION_code.json` lacks `selected_step`.
  - No committed script builds `ABLATION_stories.json`. The audit re-derived all 18 values from the raw records.
- **Fix:**
  - Write the commit, the code hashes, the data hashes, the model revision, `select_after` and `selected_step` into
    every record.
  - Commit the stories ablation builder.
  - Archive the three data files with the release.

### D14. Reproducibility holds on matched hardware but not across it (check 5)
- **Evidence:**
  - **Exact on Modal:** seven of the ten Modal reruns reproduce their records exactly, with every logged loss and every
    result equal: code O and FULL+N; add FULL+N; count O and FULL+N s3; stories O and FULL+N (L4, bf16 encoder).
  - **add O:** differs from step 100 but lands on the same value.
  - **Lean on H100:** O differs from step 200 and moves from 0.430 to 0.766 (D16). FULL+N stays exact.
  - **S5 on a local Apple CPU:** differs from step 200 (D4).
  - **Same-seed divergence across arms:** code EQ+N s0 vs O+N s0 at step 400 with the weight at 0 (0.06586 vs
    0.07014); count FULL+N s2 vs NS+N s2 at step 100.
- **Fix:**
  - A Methods sentence: results reproduce exactly on the original container types, and only to tolerance elsewhere.
  - Record the hardware in every record.
  - Ship the release's reproduction scripts with tolerances, as in `audit/RERUNS.md`.

### D15. Text that does not match the code or records (minor; no verdict changes)
- **EXEC_LM:**
  - `exec_lm_run.py:16` and §1 say 4,000 steps; the runs used 16,000.
  - §16.4 says "ties keep the earliest"; for code, equal accuracy is broken by lower validation CE.
  - §17 says "n = 512 items"; n counts programs.
  - `exec_ablation.py:77, 96` say "items of 1-32"; training uses 4–32.
- **Arithmetic:** fresh count s5 trained 1,446 s of its 1,500 s budget; the budget nearly binds.
- **Manifests:** those marked `uncommitted: true` (exec-lm main, arithmetic sections 14 and 16, lean O and FULL) match
  committed code hashes.
- **Lean:**
  - LEAN_S 3.8 says onset at step 2,400; it is 2,401.
  - O is LEAN_H's reused compiler-flag control; its configuration matches.
- **S5:**
  - The FULL+N μ grid was proposed after μ = 1 failed. This is disclosed in INVARIANCE 8, and validation and test agree
    in every arm.
  - Sections 5–7 also required mean ≥ 0.99; section 8 dropped it. Same result for all 27 records.
- **Stories:**
  - STORIES 8.1 "p (seed mean)": O+N stated 0.00071, but the per-seed mean is 0.000677 (0.000627 from the mean E).
    FULL stated 1.0, but the values are 0.668 and 0.00579.
  - The pilot seed-10 runs had `time_budget` 2,700, not 1,150 or 1,500.
  - The published `train.jsonl.gz` is read by no run.
  - NextLat arms draw their head weights before the main layers, so their main-weight initialisation differs from the
    non-NextLat arms at the same seed.

### D16. Lean O: run-to-run spread far wider than recorded (check 5)
- **Evidence:**
  - The O s0 rerun on H100 has the same config apart from bookkeeping, the same step-1 loss (3.6619), and identical
    curves through step 100.
  - It gives 0.766 at 1,024, against 0.430 and 0.469 in the two earlier runs. That is outside the registered
    0.35–0.55 band (`audit/RERUNS.md`).
  - O is still not exact, so no verdict changes.
  - But O's Lean values, and the "+0.16 over the floor" reading in D8, are not stable to better than about ±0.2.
- **Fix:** report Lean O as "not exact" with its seed spread, never as a point value; D3 in the Lean audit (±0.05)
  understated it.

## Checked and consistent
- **Raw records:** all 126 records behind the table (code 18, add 18, count 21, lean 24, s5 27, stories 18) equal their
  raw sources under one field mapping per domain (`audit/provenance.py`). No source is missing or untracked, and none
  lacks a config.
- **Table builder:** reproduces the committed `master_table.md` exactly at `a001d03` and at `4b4f973`.
- **Disjointness:** test and training sets were regenerated and hashed in every domain, including prefixes, windows,
  validation sets and certified partners. There are 0 overlaps. In Lean, all 960 states occur in training by design;
  test chains do not.
- **Leakage:** no domain uses teacher forcing at test, and no true state or label reaches the input. No partner is
  built from a test example. Evaluated n equals reported n.
- **Fixed norm:** identical in all five codebases, w ← w·√d/max(‖w‖, 1e-6):
  - `exec_lm_run.py:97–98`
  - `exec_arith.py:230–231`
  - `lean_run.py:185–186`
  - `validation_models.py:309–310`
  - `exec_lm_slot.py:238–239`

  This settles the open cross-domain question from the Lean audit.

## Reruns: results

Registered in `audit/RERUNS.md` before launch; scored by `audit/modal/score.py` (`audit/modal/score.json`); records in
`audit/modal/results/` and `audit/s5/rerun/`.

| domain | arm, seed | record | rerun | curve vs record | verdict |
|---|---|---|---|---|---|
| code | O, s0 | 0.029 (15/512) | 0.029 (15/512); floor fingerprint 0.423828125 | identical | pass |
| code | FULL+N, s0 | 1.000 | 1.000 (512/512); same fingerprint | identical | pass |
| add | O, s0 | 0.000 at 4,096 | 0.000 | differs from step 100; same selection (step 500) | pass |
| add | FULL+N, s0 | 1.000 | 1.000 (128/128) | identical | pass |
| count | O, s0 | 0.094 (12/128) | 0.094 (12/128) | identical | pass |
| count | FULL+N, s3, `--select_after 600` | 1.000 | 1.000 (128/128), selected step 750 | identical | pass |
| lean | O, s0 | 0.430 (0.469 in a second run) | 0.766 | differs from step 200 | fail on the 0.35–0.55 band; not exact (D16) |
| lean | FULL+N, s0 | 1.000 at 1,024 and 4,096 | 1.000 at every length | differs from step 100 (H100) | pass |
| s5 | O, s0 | 0.533 | 0.486 | differs from step 500 (local M4 CPU) | pass |
| s5 | FULL+N, mu 0.1, s0 | 1.000 (512/512) | 0.988 (506/512) | differs from step 200 (local M4 CPU) | fail by one sequence (D4) |
| stories | O, s10 | 0.000 | 0.000 (every length identical) | identical logged CE | pass |
| stories | FULL+N, s10 | 1.000 | 1.000 (every length identical) | identical logged CE | pass |

"Identical" means every logged loss and every reported accuracy equal the record. The launcher, app and call ids
are in `audit/modal/`; the runs were spawned from clean exports with no live client. Not run: the counting
step-confound control (D2), which needs its own registration (about $1.2–2.4).

## Files
- `audit/RERUNS.md`: registration and results.
- `audit/provenance.py`, `provenance.json`, `rebuilt_master_a001d03.md`, `rebuilt_master_4b4f973.md`, `rebuilt_master_2854f81.md`: check 1 (each
  rebuild equals the committed `master_table.md` at that commit).
- `audit/code/`: data regeneration and overlap, floors.
- `audit/arith/`: disjointness and partners, floors; the §19 checks (`s19_check.py`), long-carry floors
  (`long_carry_floor.py`) and the balanced long-carry check (`balanced_long_carry.py`). Set `AUDIT_CODE` to a checkout of exec-d `dcd126c`/research.
- `audit/lean/`: recomputed ablation, overlap, floors.
- `audit/s5/`: record checks, regeneration with hashes and floors, `rerun/`.
- `audit/modal/`: the Modal app, launcher, call ids, status and scoring scripts, `score.json`, and the ten rerun
  records in `results/`.
- `audit/stories/`: record inspection, config diffs, disjointness, floors, soft-arm check. Pass the stories research
  directory as the first argument.
