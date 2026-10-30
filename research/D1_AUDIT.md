# D1 audit: is the negative natural-pilot result sound?

Scope: LEAN_N.md sections 12.1–12.8, `research/lean_n_d1.py`, `lean_n_run.py`, `lean_n_prep.py`, `lean_n_data.py`,
the records `research/results/lean_n/runs/d1b_*_natural_*.json`, `d1_summary.md`, and `d1_verdicts.json` (worktree
`lean-n-train-a0a5e2`), plus the probe data `probes.npz` / `probes.jsonl.gz` / `items.jsonl.gz` (worktree
`lean-n-data-34a2d2`). Everything was read only. Recomputations used `python -I` on the npz and json files.
Hashes check out: `probes.npz` = `probes_src.npz` = c907209e…, and `lean_n_vprobes.npz` = a481eacd…, as in 12.1.
File:line references are to the train worktree's `research/` folder unless stated otherwise.

---

## 1. U's design — ISSUE: U is a from-scratch, 128-d, late-fusion critic whose probe names do not match its state names. It is not a ceiling.

**What U receives.**
- The true canonical state s_t at the probe's depth: `critic_state(tgt[row, t])` gives INIT followed by the state tokens,
  with EOS dropped (`lean_n_d1.py:104-110, 127-128, 380`).
- The index is right. `tgt[row, k]` is `items.states[k]` (`lean_n_prep.py:348, 370`). For every gold probe I checked
  that Lean's resulting canonical state equals `tgt[row, t+1]` (4,856/4,856 train, 973/973 test_mid) and never
  equals `tgt[row, t]`.
- The probe as `vp_tok_c`: the raw probe text renamed with the item's script map (`lean_n_prep.py:840`).

**Encoder and training.**
- U uses the same recurrence cell as R. It applies `rec_absorb` from the learned `w0`, with `pos0` positions, to the
  state event (`lean_n_d1.py:185, 354`): d = 128, 4 heads, 4 ticks, no event encoder.
- It has 875,050 parameters, identical to R and B (records' `params`).
- It is initialised from `PRNGKey(seed)`. Nothing in `lean_n_d1.py` or `lean_n_run.py` loads weights.
- It trains on the same 2,565 items (`n_train_items` = 2565) for 8,000 steps, 64 items × 8 probes per batch. Its training
  verdict accuracy is 1.000.

**Late fusion.** Under amendment B, p(accept) is `applicability(LN(pre), e)` (`lean_n_d1.py:225-239`):
- `pre` is the slot after reading the state alone;
- `e` is a 128-d pooled encoding of the probe alone.

So the state is squeezed into one 128-d vector before the probe is known, and acceptance is a bilinear form of two
pooled vectors. No probe token ever attends to a state token. For "does this rewrite pattern / lemma / hypothesis fit
this goal" over an open mathlib vocabulary, this is the weakest possible reader of a state, not an upper bound.

**Names do not match.**
- The canonical state names every hypothesis by its position in that goal, `v1, v2, …` (`lean_n_data.py:199-214`,
  line 207).
- The script map gives `v_j` only to hypotheses of the *initial* state and `h1, h2, …` to every other hypothesis name
  (`lean_n_data.py:327-343`).

So any hypothesis introduced after s_0 is `h_k` in U's probe and a positional `v_m` in U's state, and `h_k` never occurs
in any state. Counts from `items.jsonl.gz` and `probes.jsonl.gz`:

| registered test misplaced gold | probes | name a hypothesis that is h_k for U |
|---|---|---|
| depth ≥ 1 | 736 | 322 (0.44) |
| depth 1 | 82 | 39 (0.48) |

- At depth 1, 12 of the 13 unknown-identifier rejections are among those 39. Those are exactly the probes where U's
  "true state" should have helped most.
- In training only 841 of 4,848 misplaced-gold probes (0.17) carry such names, so the mismatch also shifts the
  distribution.
- Of the 210 test probes that name an initial `v_j`, 74 see that `v_j`'s type differ between s_0 and s_t. This is a
  proxy for a position shift or a rewritten hypothesis.

R, T and B do not have this problem. Their inputs are the source-named s_0 (`init_check_failed` = 0 in
`lean_n_train.json`), raw tactics, and the raw probe.

**Plainly:** U is trained from scratch, not pretrained. It has the same width and cell as R and is fused only at the
end, and it is partly blind to names. It is an upper bound in information content only, and not even fully that.

## 2. Misplaced-gold names — OK on the mechanics. The name-based component is small. A different shallow component dominates (see 7).

**Names are not resolved against s_t.**
- A misplaced-gold probe is the verbatim raw tactic of step t′ ≠ t, with the names of its original step. All 5,939
  same-item misplaced-gold texts equal `tactics_raw[t′]` exactly.
- It is run at s_t, so Lean resolves the names there. That is the intended semantics, and R, T and B see names
  consistent with their inputs.

**Why rejected misplaced-gold probes fail** (`err_class`, with the "other" class split by its first REPL message):

| rejection reason | all splits (5,827 rejected) | registered test, depths 1–12 (539) | band {1} (65) |
|---|---|---|---|
| rewrite failed | 0.268 | 0.267 | 0.246 |
| type mismatch | 0.180 | 0.208 | 0.262 |
| **unknown identifier** | **0.127** | **0.106** | **0.200** |
| simp / norm_num / linarith made no progress | 0.150 | 0.119 | 0.077 |
| elaboration (application type mismatch, function expected, synthesis) | 0.064 | 0.109 | 0.108 |
| intro / cases / induction on the wrong goal shape | 0.083 | 0.100 | 0.062 |
| other / unclassified | about 0.13 | about 0.09 | about 0.05 |

Name errors are 11–20% of rejections, so the task is not mainly a name lookup. It does have a shallow component, though:
the tactic's head word (check 7).

## 3. Leakage — OK. Theorem-disjoint, test-only probes, no later states.

**Splits.**
- No `(file_path, full_name)` overlaps between train and test_mid, train and val, train and test_long, or val and
  test_mid.
- `tree.npz` holds only theorem items (kind 0) in every split.
- No registered item's initial canonical state equals any training item's.
- Only 82 of the 900 registered-item states occur among training states: the 82 final `no goals` states.
- Test items have `novel_premise` = 1 by construction.

**Probes.**
- Training probes come only from the batch's rows of the post-hold-out `nat/train` (`lean_n_d1.py:61-79, 113-129, 330`).
- Test numbers use only `nat/test_mid` probes on the 82 registered rows (`select`, `lean_n_d1.py:486-489`).

**No later state is visible.**
- R, R+NL+I and T read `ev0` (the source-named s_0) and `evt`. Each `evt` event is two block markers plus the raw
  tactic tokens (`lean_n_prep.py:347`).
- `tgt` is never read by R, R+NL+I, T or B. Only U's `critic_state` reads it.
- The recurrence state `hs[:, t]` depends only on events up to t, and T is causal. The test at
  `test_lean_n_d1.py:69-100` checks both.
- The block markers come from the goal structure up to s_t only, and every arm gets the same markers.

**Minor text overlap, harmless.**
- 169 training misplaced-gold probes and 742 training corpus-random probes reuse tactic strings from test_mid items.
  They are cross-theorem probes run on training states, so they carry no test label.
- 54% of registered test misplaced-gold texts occur verbatim among the training probes, mostly generic tactics.
- Recall of accepted probes is higher on seen texts, so the overlap does not inflate anything.

## 4. Band {1} recomputation — OK.

Every natural record stores per-probe p(accept) for test_mid, val, held-out and test_long.

**Recomputed from the stored predictions** (82 probes, 17 accepted, one probe per registered item):
- R+NL+I seed 0, band {1} = **0.7095**. The report says 0.710.
- B (16k, the judged record) seed 0 = **0.6443**. The report says 0.644.
- All four bands of all nine records I recomputed (R, T, B 8k at seed 0; R+NL+I, B 16k, U at seeds 0 and 1) match `d1_summary.md` to 4 decimals.
- The bootstrap 95% interval [0.580, 0.831] reproduces, and so does the paired R+NL+I − B difference,
  +0.0652 [−0.030, 0.174].

**The code path is correct:**
- balanced accuracy is the mean of the two per-class recalls from pooled counts (`lean_n_d1.py:454-469`);
- the bootstrap resamples items, 2,000 times with seed 0 (`lean_n_d1.py:472-483`);
- the paired interval uses the same item resamples for both arms, with identical item order from `np.unique` on the
  same selection (`lean_n_d1.py:687-693`).

## 5. Reset on reject, and teacher forcing — OK.

**A probe is a branch** (`lean_n_d1.py:177-190`):
- `pre = hs[:, t]`, and `post = rec_absorb(pre, probe)`;
- `hs` comes from `forward(ev0, evt)` over gold events only (`lean_n_d1.py:299, 361`);
- `post` is never fed back.

So the carried slot is never overwritten, not just restored after a rejection. Accepted probes don't replace it either,
as 12.1 says.

**Teacher forcing covers tactic tokens only.** `evt` is markers plus tactic tokens, and states are never an input.

**Checks:**
- My recomputation: gold probe tokens equal `evt[row, t]` on 1.000 of gold probes in all four splits.
- Repo tests at `test_lean_n_d1.py:69-100`: probe = event t+1, and the gold states do not depend on the probes.

## 6. Arms differ only as intended — OK.

**Architecture** (records' `params` and `cfg`):

| arm | parameters | what differs |
|---|---|---|
| R | 875,050 | the base model |
| B | 875,050 | the same architecture as R |
| U | 875,050 | the same architecture as R |
| R+NL+I | 1,039,402 | adds the NextLat dynamics model |
| T | 1,535,914 | 4 causal layers; FLOPs per event 1.008 of R's |

- R, R+NL+I and U read their first event with the same `rec_absorb(w0, ·, pos0)`.
- T pools s_0 with one learned query and then runs causal blocks, as registered.

**Training is the same for every arm.**
- AdamW at 1e-3, weight decay 0.01, gradient clip 1.0, warm-up then cosine (`lean_n_run.py:905-913`).
- 8,000 steps; B is judged at 16,000 under the extension rule.
- 64 items × 8 probes per batch, with the same item-sampling and probe-sampling seeds.
- The jit checks pass (`loss_rel` ≤ 3e-5).

**B truly sees no state.**
- `pre` = the learned `w0` (`lean_n_d1.py:182-183, 353`), and `hs` is None. `ev0`, `evt` and `tgt` are never read.
- So B's acceptance is a linear function of the probe encoding.
- The only context B gets is step t's two block markers and the `focus` wrapper, which every arm also gets.

## 7. Shortcut features — ISSUE: a one-word lookup equals B and out-ranks every arm, U included.

**What predicts acceptance.**
- By probe kind (all splits): gold 100%, misplaced gold 22%, premise swap 10%, argument permutation 45%, corpus random
  6%. Kind is not an input, and within the misplaced-gold metric it is constant.
- Probe length alone: AUC 0.42–0.60 per band.
- Whether the probe names a hypothesis: AUC 0.43–0.57.
- The `focus` wrapper: AUC 0.42–0.53.
- None of those three explains B.
- **The tactic's head word does.**
  - Training misplaced gold, accepted share: `rw` 0.075 (n 1,095), `exact` 0.018 (628), `simpa` 0.031, `rfl` 0.051,
    `simp` 0.19, `rcases` / `cases` 0.39, `have` 0.76.
  - Registered test misplaced gold: `exact` 0/97, `rw` 0.10 (n 182), `have` 0.73 (74), `congr` 14/14.

**A logistic regression on the head word alone, fit to the 18,375 training probes of all kinds (as B is trained),
scored on registered test misplaced gold:**

| band | {1} | {2–3} | {4–6} | {7–12} |
|---|---|---|---|---|
| head word: BA at 0.5 | 0.615 | 0.593 | 0.655 | 0.651 |
| B seed 0 / seed 1: BA at 0.5 | 0.644 / 0.658 | 0.577 / 0.611 | 0.622 / 0.609 | 0.632 / 0.642 |
| head word: AUC | 0.778 | 0.828 | 0.804 | 0.830 |
| arms' AUC range (R, R+NL+I, T, B, U, both seeds) | 0.62–0.78 | 0.56–0.68 | 0.64–0.72 | 0.64–0.73 |

The same regression fit to training misplaced gold only reaches BA 0.74 / 0.71 / 0.74 / 0.78 and AUC 0.80–0.88.

**Paired item bootstrap, AUC(head word) − AUC(arm):**
- It is positive, with the 95% interval excluding 0, on bands {2–3}, {4–6} and {7–12} for every arm tested: R seed 0,
  R+NL+I seeds 0 and 1, B seed 0, U seeds 0 and 1.
- Example, U seed 0: +0.145 [+0.03, +0.26], +0.101 [+0.03, +0.18], +0.136 [+0.06, +0.23].
- Band {1} is level, with intervals spanning 0.

So B's 0.64 is explained by the head-word prior. Every arm, including the true-state U, ranks misplaced-gold probes
worse than a one-word table on 3 of 4 bands.

**The R+NL+I schedule is as configured** (curves in `d1b_RNLI_natural_s{0,1}.json`; `lean_n_run.py:792, 897`;
`lean_n_d1.py:276`):
- The invariance weight mu_t is 0 through step 1,600 (20% of 8,000), 0.125 at 1,700, 0.5 at 2,000, and 1.0 from 2,400
  (a 10% ramp).
- NextLat (smooth-L1 + KL, weight 1 each) is **not delayed**. It is active from step 1 (nl_h 0.059, nl_kl 0.032 at
  step 1; `lean_n_d1.py:316, 323`). This matches 12.1, which gives a delay only for the invariance term.
- The distance is centred cosine (`lean_n_run.py:627-636`) on `readout_view` = LN_f(slot) (`lean_n_run.py:323`). That
  is the same view the bilinear head reads, and NextLat's smooth-L1 uses it too.
- NextLat's KL goes through the frozen applicability form at the batch's probes, for t ≥ 1 (`lean_n_d1.py:261-270`).

## 8. Other defects — ISSUE (protocol, not code): every arm is over-trained to memorisation with no model selection. No label, index, mask or depth bug.

**Ruled out:**
- labels: `vp_acc` and `vp_t` equal `probes.npz` row by row;
- probe-to-state mapping: gold result state = `tgt[t+1]` on 1.000;
- depth: every probe has t ≤ n_ev − 2;
- masks: recomputed bands match (check 4).

**Over-training.**
- Each training probe is drawn about 220 times (8,000 × 64 × 8 / 18,375).
- Training-batch accuracy is 0.95 by step 1,600–2,000 and 1.000 by step 4,000 for R, T and U.
- `val_every` = 0 (`lean_n_d1.py:585`), so the judged model is the last step, never the best one on validation.
- The final models put p(accept) < 1e-4 on 38–49% of test misplaced-gold probes. P3 fails for the same reason: 24–30%
  of accepted probes sit at p < 5e-6.
- Failing to beat a head-word lookup (check 7) is the signature of memorisation, not of an absent signal.

**Distribution shift that adds to it.**
- 1,547 of 2,850 training items have one step. Their "misplaced gold" is another theorem's tactic: 1,372 of 4,350
  training misplaced-gold probes, 14% accepted against 23% for same-item probes.
- 58% of training misplaced-gold probes are at depth 0, while the judged bands start at depth 1 in proofs of 8–15 steps.

**The fixed 0.5 threshold.** The models are trained on a 37%-accepted mixture and scored on a set about 23% accepted,
which compresses balanced accuracy. AUC is the cleaner diagnostic.

---

## Overall verdict

The registered measurement stands. P1, P2 and P3 fail as computed: the numbers reproduce from the stored per-probe
predictions, and I found no leakage, label, index, mask or depth error. The interpretation does not stand:
- U is not a ceiling. It is trained from scratch, fuses a 128-d state vector with a 128-d probe vector only at the end,
  and sees a different name for every later-introduced hypothesis in 44–48% of the judged probes.
- Every arm, U included, is out-ranked on 3 of 4 bands by a logistic regression on the tactic's first word, fit to the
  same 2,565 items.

So the evidence shows that the training protocol failed to generalise even a shallow learnable feature: memorisation to
1.000, about 220 passes per probe, no validation-based model selection. It does not show that "the verdict function is
not learnable from 2,565 theorems". "This pilot cannot test state tracking" is still true, but because no arm
generalises, not because the function is unlearnable.

One rerun would settle it: retrain U and B on the same 2,565 items, two seeds, with these changes.
- U′ reads a name-consistent state and probe: the state re-rendered with source names, or the probe renamed with
  s_t's own positional map.
- U′'s probe tokens cross-attend over the state tokens.
- Both pick their checkpoint on validation misplaced-gold AUC.
- The head-word regression is reported as the floor.

If U′ beats both B′ and the floor by ≥ 0.10 balanced accuracy on bands {1} and {4–6}, the verdict is learnable from the
state at this scale, and the tracking arms should be rerun under the same model selection. If U′ stays at the head-word
floor, the "not learnable from scratch at 2,565 theorems" reading is confirmed.
