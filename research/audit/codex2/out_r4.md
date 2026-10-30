The counted scores mostly reproduce. **Two RL implementation bugs prevent calling this the registered training procedure.** MMLU and WikiText also lack enough saved detail for a fully independent reconstruction.

Paths below are relative to `research/`. No files were edited.

I used read-only Python scripts that independently extracted answers, counted records, grouped cells, compared complete problem lists, and summed learning rates. For arithmetic scoring, I reproduced the documented extraction rules without importing the experiment’s scorer. For gates, I distinguish recounting saved flags from independently scoring outputs.

| Headline | Independent result, r4 versus reason-s1 | Verdict and exact evidence |
|---|---|---|
| Clock R1 | **175/384 versus 165/384**; difference **0.0260417** | **OK.** Rescoring gives 121+54 versus 90+75, with zero flag disagreements. Saved `"k"` values: `r4/results/r4-r1a/r4r1a_reason.json:14947`, `r4/results/r4-r1b/r4r1b_reason.json:14841`; `reason/results/r1a-clock/r1a_reason.json:20855`, `reason/results/r1b-clock/r1b_reason.json:24484`. |
| Targeted pool | **53/128 versus 24/128** | **OK, pooled only.** Coin contributes **43 versus 14**; four-total contributes **10 versus 10**. Raw records begin at `"records": [` in the same four files, respectively lines **593, 113, 573, 83**. Thus the entire pooled gain comes from coin. |
| Clock R2 | **117/160 versus 115/160** | **OK.** Independent rescore matches `"k": 117` and `"k": 115`: `r4/results/r4-r2/r4r2_reason.json:12197`; `reason/results/r2-clock/r2_reason.json:16938`. |
| No-clock R1 | **93/384 versus 128/384** | **OK numbers.** Rescore: 68+25 versus 82+46. `"k"` lines: `r4/results/r4-r1ap/r4r1ap_reason.json:4052`, `r4/results/r4-r1bp/r4r1bp_reason.json:3832`; `reason/results/r1a-plain/r1ap_reason.json:3878`, `reason/results/r1b-plain/r1bp_reason.json:3791`. |
| No-clock R2 | **71/160 versus 94/160** | **OK.** Matches `"k": 71` / `"k": 94`: `r4/results/r4-r2p/r4r2p_reason.json:3297`; `reason/results/r2-plain/r2p_reason.json:3190`. |
| GSM8K | **364/400 versus 369/400**, program rate **0** for both | **OK.** Re-extracted the last boxed answer from all saved responses and compared against `"gold"`. Raw items: `r4/results/lm-rl-c/lm_lm-rl-c_gsm8k_texts.json:2`; `reason/results/lm-s1/lm_reason-s1-500_gsm8k_texts.json:2`. |
| MMLU | Saved aggregates **781/1140 versus 740/1140** | **DESIGN FLAW: incomplete audit records.** These match `"k"` at `r4/results/lm-rl-c/lm_lm-rl-c.json:63` and `reason/results/lm-s1/lm_reason-s1-500.json:63`, but cannot be independently recounted from saved labels: `promptbox/pb_lmeval.py:105` saves only `mmlu_texts.append(o.outputs[0].text)`, and line **137** writes that text list without questions, IDs or gold labels. |
| WikiText perplexity | `exp(2.959034816830289)` = **19.2793547**; `exp(2.6258736738349513)` = **13.8166402** | **OK transformation; DESIGN FLAW for full reconstruction.** Inputs are `"nll_per_token"` at `r4/results/lm-rl-c/lm_lm-rl-c.json:74` and `reason/results/lm-s1/lm_reason-s1-500.json:74`. Per-token/window losses are discarded: `promptbox/pb_lmeval.py:73` saves only the aggregate. |
| Families pinned | **700/768 versus 733/768** | **OK flag recount.** Summed `"pinned_answer_correct"` over `"records"`: `r4/results/r4-fam/r4-fam_loop.json:30`; `reason/results/gate-fam/gate-fam_loop.json:30`. Full answer rescoring is not supported by these records: `promptbox/pb_loop.py:202` writes `"key": None`, and lines **315–317** remove `"_key"`. |
| G1 | **511/512** for both; **8/8** long runs exact | **OK record recount.** Both pass counts also equal the number of tables with zero wrong rows. `"tables"` begin at line **244** in `r4/results/r4-g1/r4-g1_g1.json` and `reason/results/g1-s1/g1-s1_g1.json`; the recorded fields include `"exact": true`, `"pass": true`, `"rows_wrong": 0` at lines **252, 260, 262**. |
| Compile held-out | **41/88** | **OK.** Independently scored saved regions against each saved answer key; zero flag disagreements. Records: `r4/results/r4-compile/r4-compile_reason.json:373`; aggregate `"k": 41`, `"n": 88` at **4774–4775**. |
| Addition | **148/160 versus 150/160** | **OK flag reconstruction.** Filtered out `"negative"` items and recomputed `outputs_exact AND words_exact`; both match. Records begin at line **1042** in `r4/results/r4-arith/r4-arith_arith.json` and `reason/results/gate-arith/gate_arith.json`. Definition: `arith/arith_loop.py:238`, `rec["exact"] = rec["outputs_exact"] and rec["words_exact"]`. Long answers are truncated when saved, preventing complete independent output rescoring: line **233**. |

1. **Registered verdicts and selection — OK arithmetic; BUG training compliance.**

   Amendment A’s actual thresholds are unchanged from the SFT manifest’s frozen commit: `r4/manifests/r4-sft.json:5` names `50af96fc…`; that revision’s `R4.md:369–374` agrees with current `r4/R4.md:1624–1629`.

   Recomputed flags:

   | Registered test | Calculation | Verdict |
   |---|---:|---|
   | Validation improvement ≥0.04; RL gate ≥0.08 | `(28−20)/48 = 0.166667` | **OK: both true** |
   | R1 improvement ≥0.05 | `10/384 = 0.026042` | **OK: false** |
   | Target pool improvement ≥0.10 | `29/128 = 0.226563` | **OK: true** |
   | Other four decline ≤0.08 | `−19/256 = −0.074219` | **OK: true** |
   | R2 decline ≤0.05 | `2/160 = 0.0125` | **OK: true** |

   Validation rescoring gives **20, 27, 28 out of 48**, selecting step 400 under “highest accuracy…tie…later step” (`r4/R4.md:60`). Raw `"k"` values: `r4/results/val-s1/val-s1_reason.json:6274`, `r4/results/val-200/val-200_reason.json:4940`, `r4/results/val-400/val-400_reason.json:4728`. All three complete problem lists match.

   SFT, B and C pass the recorded language thresholds using their saved aggregates; this remains conditional on the unaudited MMLU totals. The rule is explicit at `r4/R4.md:287,294`: “MMLU rate at least … minus 0.015” and C runs only after B’s screen passes. B’s screen finished at `"2026-10-29T02:40:10.958298+00:00"` (`r4/results/lm-rl-b/lm_lm-rl-b.json:12`), before C’s manifest creation at **02:49:17** (`r4/manifests/rl-c.json:4`).

   **No evidence of r4 seed-777 checkpoint selection:** C finished at **04:16:51** (`r4/results/r4-rl-c/rl_record.json:32`), before counted-clock manifest creation at **04:21:35** (`r4/manifests/counted-clock.json:4`). However, the flags and selection are not implemented by `r4_report.py`: its `main` only recounts and checks equality of counts (`r4/r4_report.py:93–111`). They are correct report calculations, not an executable selection audit.

2. **Leakage — OK for inspected synthetic generation/prompt paths; DESIGN FLAW for language-test reuse.**

   Evaluation prompts contain only `R.chat_prompt(p["question"])` (`reason/reason_loop.py:201`). Reference calls are used for diagnostics after execution (`reason/reason_loop.py:285–288`), not appended as gold answers. RL similarly prompts from `p["question"]` (`reason/reason_rl.py:187`); gold answers and reference rows enter reward calculation afterward (**245–249**). Training sees reference targets intentionally; the prompt is masked with `[-100]` (`reason/reason_core.py:652–659`).

   Training samples `D.TRAIN_TEMPLATES` with `"train"` (`reason/reason_rl.py:47,55`), distinct from `TEST_TEMPLATES` (`reason/reason_data.py:49–51`). Compile training explicitly uses `"iid"` (`r4/r4_train.py:68,71`); its axes are `(False, False, False)` (`compile/compile_gen.py:79`). Ordinary RL questions use GSM8K/ARC `"train"` splits (`promptbox/pb_selfdistill.py:69,75`).

   **But language test scores influence progression/adoption.** The screen uses GSM8K/MMLU, and those exact evaluation datasets are loaded with `split="test"` (`promptbox/pb_lmeval.py:79,110`; gating at `r4/R4.md:284–294`). Consequently, these are reused selection screens, not untouched evidence of language preservation. External rehearsal files are loaded by path (`reason/reason_train.py:239–245`); their complete contents are not present in this record set, so exhaustive cross-dataset overlap is unverified.

3. **Fairness — OK paired evaluation; DESIGN FLAW for causal attribution.**

   All six R1/R2 saved problem lists are exactly equal across arms. Historical/current AST comparison also found identical `make_problems`, `last_number`, `answer_region` and `correct`; the shared seed is constructed as `f"{seed}|{t}|{split}|{L}"` (`reason/reason_loop.py:70`), and scoring is at **85–113**.

   Both use the same 12,000-token-per-round limit, greedy generation and context-budget logic (`reason/reason_loop.py:212–219,409`). Family/addition question lists also match exactly. Both adapters have `"r": 64`, `"lora_alpha": 128` in `r4/results/r4-rl-c/adapter_iter40/adapter_config.json:31,20` and `reason/results/reason-s1/adapter_step500/adapter_config.json:31,20`.

   **Training and tool interfaces are not matched.** R4 adds 400 SFT steps from reason-s1 (`r4/results/r4-sft/train_record.json:11,43`), changed data mix (**29**), then B and C; C starts from B (`r4/results/r4-rl-c/rl_record.json:5`). Summed logged learning rates are **0.009 + 0.012 = 0.021**, so C’s reported 20× is its incremental stage, not the cumulative RL dose. New `number k` and `use` syntax are explicitly introduced (`r4/R4.md:20–21`). These results compare complete systems; they do not isolate RL, data, grammar or additional compute.

   SFT checkpoint selection occurs after executor and KL terms are active: pinned/Mealy losses at `reason/reason_train.py:303–312`, KL at **328–333**, save at **354–356**. Last logged values reproduce `"mealy_acc": 1.0`, `"pinned_acc": 1.0`, `"step": 399` (`r4/results/r4-sft/train_record.json:2437,2447,2449`). These are training-batch accuracies, not held-out executor guarantees.

4. **Figures — OK, not applicable.** `R4.md` contains numerical JSON blocks rather than plotted figures/captions; the counted sections begin at `r4/R4.md:835,1071,1178`. No figure claim needs reconciliation.

**BUGs, by severity:**

- **High — numeric rows are missing from the registered RL reward.** Registration says “number-mode rows are the 5-token row” (`r4/R4.md:296`). But `reference_rows` reads only `spec["lit"]["registers"]` (`r4/r4_reward.py:74–78`); numeric specs instead contain `"kind": "numbers", "op": …` (`reason/reason_data.py:204`). A direct reproduction returns `[]` for a numeric reference. **Fix:** expand numeric references through `reason_core.table_rows(op)` (**89–90**). Pure numeric rollouts currently lose up to **0.25 reward**; mixed prompts have the wrong denominator. Corrected headline accuracies are unknown until retraining.
- **High — registered RL KL rehearsal is absent.** “KL rehearsal stay[s] on every update” (`r4/R4.md:293`), but RL rehearses saved response tokens through cross-entropy (`reason/reason_rl.py:130–132,286–295`), without the reference-distribution KL used in SFT (`reason/reason_train.py:329–333`). **Fix:** implement the frozen KL requirement or explicitly report a protocol deviation. Existing counts do not change retrospectively; the corrected training outcome is unknown.
- **Medium — report verifier crashes on no-clock results.** `clock = doc.get("clock") or doc` followed by `clock["summary"]` (`r4/r4_report.py:66–67`) ignores the `"plain"` wrapper. Running it on `r4r1ap_reason.json` produced `KeyError: 'summary'`. **Fix:** explicitly select the evaluated mode. **Numerical effect: none** on my independent recount; the claimed verification path is broken.

The headline claims that survive are:

- **Clock R1:** 175 versus 165 survives; the registered +0.05 prediction fails.
- **Targeted pool:** 53 versus 24 survives; improvement is entirely coin, not both templates.
- **Clock R2:** 117 versus 115 survives; the allowance flag passes.
- **No-clock:** both reported declines survive.
- **Language:** GSM8K survives; MMLU remains aggregate-only; WikiText’s recorded transformation survives and shows **39.54% worse perplexity**, not language preservation.
- **Families/G1/addition:** saved-record counts survive, with the rescoring limitations above.
- **Compile:** 41/88 survives independent answer-key rescoring.

Minimal re-runs: fix both RL bugs and rerun **B from SFT-400, then C only under the frozen gate**, followed by affected evaluations. No SFT rerun is required by these findings. Recover MMLU item IDs/golds to rescore existing responses; otherwise rerun MMLU with complete records. Rerun WikiText likelihood evaluation saving window/token losses. For causal claims, additionally evaluate reason-s1 under the new harness and use a matched continuation control; for language-preservation claims, use a fresh language holdout.