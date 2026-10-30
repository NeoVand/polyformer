The recorded arithmetic mostly matches. The strongest problems are **unequal gates, self-loop probes that do not establish table use, and pin success selected by the gate itself**. No files changed.

I used an independent Python script: load `runs.json` and the step files; count `prediction != true`; identify first occurrences of each held `(state,event)`; group recorded margins by arm and τ; take medians; sum corruption outcomes and pin bits. This recomputes statistics from records, not logits from model weights. Raw summaries are minified on [runs.json:1](/Users/neo/repos/polyformer-wt/predict/research/predict/results/p2v2-savant-r3/runs.json:1).

**Independent recount**

| Headline | Recomputed result | Verdict |
|---|---|---|
| Competence | Trained **16/16 gate passes**; bare **0/16**. But trained gates contain **16 events**, bare gates **25**. | **BUG** in the “16-event” description; unequal tests. |
| Teacher-forced first-use medians | τ=16: **15.0625**; 256: **12.8125**; 2,048: **13.625**; 8,192: **11.0625**, each n=4. | **OK**, matches. |
| Approximately 10k, teacher-forced | `[10.375,13.0,10.75]` → **10.75**, n=3. Exact τ=10,190: **13.0**, n=1; τ=10,196: **10.5625**, n=2. | **OK**, pooled maximum differs from an exact-τ estimate. |
| Free-run medians | **15.0625, 12.875, 13.5625, 11.0625** at the four fixed τ; maximum `[12.0,10.375,10.75]` → **10.75**, n=3. | **OK**, matches. |
| Corruption | Copies **0/16**; table-destination predictions **16/16**; controls correct **16/16**. | **OK** as observed outcomes. |
| Pins | **3 error observations**, **0 pin errors**; two observations repeat the same draw/step across TF/free arms. | **OK** as counts, not three independent failures. |

Exact report excerpts matching the recount are “`(256, 12.8125, 4), (2048, 13.625, 4)`” at [PREDICT.md:338](/Users/neo/repos/polyformer-wt/predict/research/predict/PREDICT.md:338), the free-run list at [PREDICT.md:339](/Users/neo/repos/polyformer-wt/predict/research/predict/PREDICT.md:339), and “`follow_h` 0 of 16, `follow_t` 16 of 16” at [PREDICT.md:366](/Users/neo/repos/polyformer-wt/predict/research/predict/PREDICT.md:366).

The three raw error rows are:

- `[8196,32913,11051,3331,198,11051,-0.125,1]` — [trained-d0-tf-t8192.json:1](/Users/neo/repos/polyformer-wt/predict/research/predict/results/p2v2-savant-r3/steps/trained-d0-tf-t8192.json:1).
- `[10186,40936,7270,3331,7728,7270,-1.375,1]` — [trained-d2-tf-t10190.json:1](/Users/neo/repos/polyformer-wt/predict/research/predict/results/p2v2-savant-r3/steps/trained-d2-tf-t10190.json:1).
- `[10186,40936,7270,3331,7728,7270,-1.0,1]` — [trained-d2-free-t10190.json:1](/Users/neo/repos/polyformer-wt/predict/research/predict/results/p2v2-savant-r3/steps/trained-d2-free-t10190.json:1).

**BUG — “margin falls by 5–7 logits” is not valid across all probes.** From the corruption records:

| Distance | Control median | Corrupted median | Difference | Median paired decrease |
|---|---:|---:|---:|---:|
| 65 | 15.0625 | 8.1875 | 6.875 | 7.3125 |
| 513 | 13.625 | 8.6875 | 4.9375 | 5.875 |
| 4,097 | 12.9375 | 8.125 | 4.8125 | 5.5625 |
| Per-draw maximum | 10.75 | 6.9375 | 3.8125 | 4.125 |

Individual decreases range **2.875–10.125**. Exact supporting records include `"control_margin": 12.0, "corrupt_margin": 9.125` at [PREDICT.md:350](/Users/neo/repos/polyformer-wt/predict/research/predict/PREDICT.md:350) and `"control_margin": 13.875, "corrupt_margin": 3.75` at [PREDICT.md:356](/Users/neo/repos/polyformer-wt/predict/research/predict/PREDICT.md:356). Fix the wording and specify the statistic; outcome counts remain unchanged.

**Checklist findings**

1. **OK — imported harness format.** The executed builder calls `pb_lit.literal(ex, tok)` and `br_core.layout(tok, ex, lit)` at [pr_v2.py:330](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_v2.py:330) and [pr_v2.py:335](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_v2.py:335). The shared layout checks `"program layout does not match pb_lit.program_ids"` and uses `pb_lit.run_ids` at [br_core.py:104](/Users/neo/repos/polyformer-wt/predict/research/predict/br_core.py:104). This establishes the plain sequence format. It does **not** establish that the input rendering was trained: `fmt="lines"` is forced at [pr_v2.py:311](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_v2.py:311), while the family marks its last format held out at [pb_families.py:77](/Users/neo/repos/polyformer-wt/predict/research/promptbox/pb_families.py:77); cycle’s last format is `"lines"` at [pb_families.py:453](/Users/neo/repos/polyformer-wt/predict/research/promptbox/pb_families.py:453).

2. **OK — executed first use and scoring alignment.** Queries use `epos = rs + k * stride` and target `ids[epos + 1]` at [pr_v2.py:359](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_v2.py:359) and [pr_v2.py:366](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_v2.py:366). Free execution computes `true = dest_of.get((state_id, event))` and checks the actual held pair at [pr_v2.py:608](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_v2.py:608). All recorded exposures occur at τ; the divergent run correctly has none. Margins are target minus best other vocabulary logit: `"margin = top - float(torch.max(masked))"` / `"float(lg[target]) - top"` at [pr_job.py:391](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_job.py:391) and [pr_job.py:394](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_job.py:394).

3. **OK mechanically; DESIGN FLAW mechanistically — corruption.** The constructor requires `uses != [first, first + g]` to reject a tape at [pr_v2.py:169](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_v2.py:169). Replacement candidates exclude `true_out`, and exactly one assignment changes the input: `dirty[out_pos] = wrong` at [pr_v2.py:994](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_v2.py:994) and [pr_v2.py:999](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_v2.py:999). I reconstructed all 16 event trajectories and verified the two visits and recorded distances.

   However, held-row selection prioritizes self-loops: `transit(se[0], se[1]) != se[0]` sorts first when false at [pr_v2.py:239](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_v2.py:239). All four selected rows are hold/stay self-loops; the prompt explicitly says these commands “do nothing” at [pb_families.py:439](/Users/neo/repos/polyformer-wt/predict/research/promptbox/pb_families.py:439). Thus the correct answer is already the current state. Moreover, `follow_t = int(pd == reuse["true"])` measures agreement, **not evidence of table consultation** ([pr_v2.py:1014](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_v2.py:1014)).

4. **OK mechanically; DESIGN FLAW as independent evidence — pinned twin.** Errors call `pin.query(state_id, event, true)` at [pr_v2.py:620](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_v2.py:620); shared `tick` feeds exactly `[[s_id, e_id]]` at [pb_pin.py:245](/Users/neo/repos/polyformer-wt/predict/research/promptbox/pb_pin.py:245). But admission already requires `pin_wrong == 0` over every row ([pr_v2.py:781](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_v2.py:781), [pr_v2.py:801](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_v2.py:801)). The three corrections survive; independent evidence that pinning generally rescues failures does not.

5. **OK for causal target exclusion; DESIGN FLAW for broader leakage/generalization claims.** The supplied program contains every destination, and the prompt contains the whole event tape; this is an oracle-program execution test. `"ids = prompt + prog + opener + run + closer"` appears at [br_core.py:108](/Users/neo/repos/polyformer-wt/predict/research/predict/br_core.py:108). TF supplies prior correct states; free runs supply predictions ([pr_v2.py:633](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_v2.py:633)). No final-answer string is appended by this layout; although `literal` retains `"answer": ex["answer"]`, the program emits `answer_line`, the template ([pb_lit.py:214](/Users/neo/repos/polyformer-wt/predict/research/promptbox/pb_lit.py:214), [pb_lit.py:233](/Users/neo/repos/polyformer-wt/predict/research/promptbox/pb_lit.py:233)). Training-set overlap cannot be certified from this job’s evaluation-source manifest and adapter identity alone ([manifests/p2v2.json:7](/Users/neo/repos/polyformer-wt/predict/research/predict/manifests/p2v2.json:7), [PREDICT.md:275](/Users/neo/repos/polyformer-wt/predict/research/predict/PREDICT.md:275)).

6. **DESIGN FLAW — comparison fairness.** Same frozen adapter: the loader calls `model.eval()` and sets `requires_grad_(False)` ([pr_job.py:317](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_job.py:317)); arm-specific rank, optimizer steps, learning rate, and checkpoint/loss scheduling are therefore inapplicable here. But machines, names, row counts, prompts, and gate lengths differ. Trained uses cycle programs; bare uses the fixed 16-row machine ([PREDICT.md:250](/Users/neo/repos/polyformer-wt/predict/research/predict/PREDICT.md:250)). The report’s “passed the **16-event run**” is false for bare ([PREDICT.md:341](/Users/neo/repos/polyformer-wt/predict/research/predict/PREDICT.md:341)): `events_for_delay(16)` has `tau + 1 + 2 * reuses = 25` events ([pr_data.py:118](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_data.py:118)). Trained’s gate covers indices 0–15; actual τ=16 first-use results exist for **four**, not sixteen, draws. Relabeling preserves gate counts; equal-length counts require new scoring.

7. **OK for reported verdicts; BUG in automated reporting.** Frozen rules require strictly decreasing TF medians, copy rate exceeding control error at the shortest distance, and all pins correct ([PREDICT.md:262](/Users/neo/repos/polyformer-wt/predict/research/predict/PREDICT.md:262), [PREDICT.md:264](/Users/neo/repos/polyformer-wt/predict/research/predict/PREDICT.md:264)). Independent application gives **fall fails; copy fails/falsifier fires; pin holds**.

   The reporter overwrites the ladder with `taus = rec.get("ladder") or taus`, omitting draw 2’s τ=10,190 ([pr_v2.py:1123](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_v2.py:1123)). Fix by taking the union of exact τ values and separately reporting pooled maxima. The manually amended report already supplies both. Also, `if not any(r.get("follow_h") == 1 for r in corr)` never implements the shortest-distance copy-versus-control criterion ([pr_v2.py:1157](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_v2.py:1157)). Implement explicit verdicts and an empty-data guard; current verdicts stay unchanged.

8. **OK with a presentation limitation — figures.** Panel A plots recorded first-use margins; panels B/C plot outcome fractions and separate margin medians ([pr_fig.py:242](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_fig.py:242), [pr_fig.py:282](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_fig.py:282), [pr_fig.py:305](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_fig.py:305)). Their endpoints pool different per-draw maxima at median x coordinates: `xs_m.append(_med(tmax_xs))` and `rungs.append((_med(...), max_rows))` ([pr_fig.py:258](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_fig.py:258), [pr_fig.py:279](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_fig.py:279)). Label that pooling and sample sizes; the endpoint is not one common tested distance.

**BUGs by severity**

- **Medium:** unequal-gate/“16-event” reporting; overgeneralized 5–7-logit decrease; incomplete automated verdict/τ aggregation. Fixes and numerical effects are above.
- **Low, latent:** `except torch.OutOfMemoryError` precedes the function-local `import torch`, so an exception is masked by an unbound-local error ([pr_v2.py:1005](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_v2.py:1005)). Move the import before the `try`; no recorded corruption numbers change.

**Headline claims that survive**

- **Competence:** 16/16 trained versus 0/16 bare **gate passes**, not a matched delay-16 comparison.
- **First-use margins:** the stated medians and nonmonotonicity survive; the frozen fall prediction fails.
- **Corruption:** 0/16 copied and 16/16 agreed with the table destination; table reliance and a universal 5–7-logit decrease do not follow.
- **Pinned twin:** all three recorded errors were corrected, conditional on prior all-row pin certification.

**Minimal re-runs**

- None for the corrected descriptive statistics or frozen verdicts; regenerate the report.
- To complete the existing maximum-τ data, rerun only `trained|0|tf|10202`, recorded as `"error oom"` at [PREDICT.md:302](/Users/neo/repos/polyformer-wt/predict/research/predict/PREDICT.md:302), after scoring logits incrementally instead of retaining and concatenating all chunks ([pr_v2.py:503](/Users/neo/repos/polyformer-wt/predict/research/predict/pr_v2.py:503)).
- Stronger conclusions need a newly registered matched comparison: identical machines and gate lengths across formats, non-self-loop held rows with arbitrary mappings, and pin evaluation without selecting draws for pin perfection.