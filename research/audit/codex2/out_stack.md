**The recorded accuracy totals survive. Two claims need correction: literal “bitwise” equality was not tested, and the registered L4 timing workload was not completed.** No files were edited.

Paths below are relative to `research/stack`.

1. **Independent recomputation — OK.** My read-only script counted certificate rows satisfying `argmax == ids[q2]` and positive margin; summed individual run counters; recomputed correctness from recorded outputs and targets; and calculated timing as `1000 × sum(seconds) / sum(n_steps)`, without calling `stack_report.py`.

| Headline | Independent result | Matches? |
|---|---:|---|
| Certificates | 50/50 + 144/144 + 294/294 = **488/488** | Yes |
| Minimum certificate margins | **7.875, 8.125, 5.0** | Yes |
| Canonical steps, Dyck-2 / Dyck-4 / Boolean | **45,159 / 45,159 / 44,760** | Yes |
| Total recorded logit and frame equality checks passing | **135,078/135,078**, each | Yes, numerical equality |
| Counted cells / random instances / malformed cases | **15/15 / 72/72 / 9/9** | Yes |
| BBH | **250/250**, **2,793** steps, maximum depth **7** | Yes |
| H100 | **24.024045 ms**, **90,459** steps | Yes |
| L4 | **63.965127 ms**, **5,870** steps | Yes, nine-cell subset |

Exact record anchors: `"rows": [` in `results/stack-counted-dyck2-h100/cert.json:88`, `results/stack-counted-dyck4-h100/cert.json:110`, and `results/stack-counted-bool-h100/cert.json:142`; `"cells": [` at each machine’s `cells.json:4`; `"instances": [` at `instances.json:14`. BBH records contain `"canonical_value"`, `"target"`, and separate equality counters at `results/stack-counted-bool-h100/bbh.json:20–33`. L4 stores `"n_steps": 24` and `"seconds": 1.545911450999995` for its first cell at `results/stack-l4/l4.json:51–54`.

Additional recomputations also match:

- Naive **B/A errors**: Dyck-2 **19/3090, 227/3090**; Dyck-4 **294/3090, 67/3090**; Boolean **132/2270, 77/2270**. Nonbottom equality matches: **0/6104, 0/6098, 0/4472**. Every control prediction was correct. Raw buckets explicitly store `"naive_ok"`, `"control_ok"` and `"n"` (`results/stack-counted-dyck2-h100/naive.json:20–28`, corresponding files for the other machines); these reproduce `STACK.md:359–362`.
- History d8/d64/d512: **8/8,8/8,7/8**; **8/8,8/8,8/8**; **8/8,8/8,8/8**. Thinking: **5/8,0/8,0/8**; **4/8,3/8,4/8**; **8/8,2/8,6/8**. These reproduce `STACK.md:324–336`; thinking records start at `"rows": [` (`results/stack-think-h100/think.json:13`).
- Historical BBH: **248/250 = 99.2%**, **244/250 = 97.6%**, **55/250 = 22.0%**. I filtered individual records by `"bbh|boolean_expressions|official"` in `../promptbox/results/base-think-bbh/base-think-bbh_bbh_official.rescored.json:29810`, `../promptbox/results/base-answer-3/base-answer-3_bbh_official.json:28053`, and `../closeout/results/co-r2-s1/co-r2-s1_bbh_official.json:54233`.
- Spend sums to **$11.760997**, matching **$11.7610**; the ledger calls this an `"upper-rate estimate … not an invoice"` (`results/modal_ledger.json:11`; report total `STACK.md:387`).

2. **Canonical history independence and closed cover — OK.** The actual call is:

> `forward(model, cache, [top_id, q_id, a_id], [P, P + 1, P + 2], P)`  
> `stack_forward.py:112`

The preceding line clones Π. I located and read the shared helper: it clones every layer’s `"keys"` and `"values"` (`../promptbox/pb_pin.py:217–235`). No stack depth or previous-step cache enters this call.

The closure check considers every parent exposed by popping, asserts BOT preservation and successor membership, then requires exact equality with the witnessed row set (`stack_validate.py:33–47`: `"assert expected == set(found[\"rows\"])"`). Independently enumerating those transitions reproduced **110 / 576 / 2,009** closure cases. Certificate rows include bottom, malformed, halt-entry and absorbing-halt transitions; classification is explicit at `stack_machine.py:300–314`. The arbitrary-depth conclusion remains conditional on deterministic inference, as the report states at `STACK.md:375`.

3. **Correct tensors — OK; literal bitwise claim — BUG, low severity.** Logits come from the event’s full vocabulary (`stack_forward.py:102`: `"return out.logits[0, -1]"`), indexed against the actual `(top,q,a)` certificate row (`:206–210`). Frame extraction includes K and V at slot P across every layer (`:60`).

However, the checks are:

> `if torch.equal(lg, ref):`  
> `if torch.equal(fr, frames[top]):`  
> `stack_forward.py:210,214`

`torch.equal` tests numerical equality, not byte identity; signed zeros can compare equal. **Fix:** describe the existing result as exact numerical equality, or compare contiguous byte views and retain tensor hashes. **Effect:** no demonstrated change to any answer, margin or numerical-equality count; the literal byte-equality count is unknown. Saved certificate records contain scalar summaries rather than the full tensors (`stack_forward.py:147–150,171–177`).

4. **Leakage and host/model division — DESIGN FLAW for interpreting this as independent reasoning; OK for supplied-table execution.** Every queried transition’s answer is deliberately present in Π:

> `pi += [ids[r["top"]], ids[r["q"]], ids[r["a"]], ids[r["q2"]], nl]`  
> `stack_forward.py:43`

Thus **488/488 certifies retrieval/execution of supplied answers**, not discovery of transition rules.

The host parses BBH syntax, emits the program **and separately computes its value** (`stack_machine.py:370–371`: `"return emit(tree), ast_value(tree)"`). That value and the official label do not enter the model call: inference precedes `"target = ex[\"target\"] == \"True\""` (`stack_job.py:195–202`).

The host also computes the reference transition and stack operation, checks the model output, and applies push/pop/rewrite/store operations (`stack_forward.py:222–236`; `stack_machine.py:40–54`). **The model’s contribution is only full-vocabulary next-control-state selection.** No erroneous state is silently repaired on the counted path: mismatch breaks execution at `stack_forward.py:224–230`.

No additional STACK training occurred: records say `"adapter2": null`, `"assign": 0` (`results/stack-counted-bool-h100/cert.json:2–3`). The unused fallback draws from `pool["train"]` (`stack_lora.py:43`), disjoint from test names by `../promptbox/pb_pin.py:73–94`. This does not establish absence of contamination in the pre-existing model.

5. **Frozen predictions and verdict rules — BUG for L4; otherwise consistent with these records.** The registered section is unchanged from commit `9aaeaf21`. Certificate acceptance implements `"arg == target and margin > 0"` (`stack_forward.py:145`); counted verdicts require exact execution and the correct final value (`stack_job.py:133,152,202`). Reported misses—Boolean zero-shot failure, B≤A on two machines, history degradation, and several thinking thresholds—are correctly retained (`STACK.md:357–366`).

The timing registration says:

> “mean over the counted cells’ steps” — `STACK.md:181`

But L4 executes:

> `for c in M.CELLS[:3]:` — `stack_job.py:228`

The report nevertheless marks its prediction as holding (`stack_report.py:400–402`). **Fix:** mark the full-workload L4 prediction untested, or run the missing six cells. **Effect:** **63.97 ms remains correct for its subset**; the registered 15-cell L4 mean is unknown.

6. **Comparator fairness and scoring — DESIGN FLAW for a controlled capability comparison; scoring OK.** Canonical/history use the same supplied table and model, but intentionally different cache/position policies. History stops on its first wrong state (`stack_forward.py:274–283`), so its score is correctly an exact-trace score.

Thinking instead uses the **base** model, natural-language inputs, stochastic sampling and a 32,768-token context (`stack_job.py:247–256,294–297`); canonical uses merged Savant r3 (`../scan/scan_forward.py:18–19,52–61`). Training, representation, compute budget and scoring are consequently unmatched. Rank, learning-rate and checkpoint-selection comparisons are inapplicable to the untrained STACK arms; the unused fallback has one loss from the outset and saves only after training (`stack_lora.py:138–150`).

Reparsing all **81** stored tails reproduced the scores; all **25** null answers were budget-exhausted responses. The parser explicitly requires `"</think>"` and an `"Answer:"` match (`stack_job.py:259–266`).

Naive A also changes query positions, so it does not isolate stored-KV effects alone (`stack_forward.py:324–326`). Its trajectory is reference-driven (`:360`: `"q = want_q2"`), and deep sampling uses only two instances, every fourth step (`stack_job.py:162–163`). These are sampled local errors, not autonomous-run failure rates.

7. **Figures/captions — OK for the tables present.** There are no plotted figures in this report. I independently reproduced the frame-depth and naive-table entries. The caption correctly says “Each row aggregates sampled steps” (`STACK.md:249`); code sums counts and takes maxima for delta columns (`stack_report.py:194–197`). Dyck-4’s imperfect depth-zero control is disclosed (`STACK.md:284`), preventing attribution of every nonzero difference solely to history.

**BUGs by severity:** medium—L4 prediction declared passed on an incomplete workload; low—numerical equality labeled literal bitwise equality. Neither changes recorded accuracy.

**Headline claims that survive:**

- **488/488:** survives as zero-additional-training certification of supplied-table execution.
- **135,078 steps:** survives as exact numerical equality; literal byte equality remains unverified.
- **BBH 250/250:** survives for the host-compiled, host-stack pipeline.
- **Naive failures:** survives for the sampled local comparisons, with positional and numerical-control qualifications.
- **24/64 ms:** survives for the respective measured workloads; full registered L4 timing remains open.

**Minimal reruns:** none for the narrowed accuracy claims; six missing L4 cells for the registered timing verdict; replay the counted canonical suite with byte-level checks only if retaining literal “bitwise” wording.