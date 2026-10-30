**The headline counts reproduce. The claims “forgetting is necessary” and “only pin is learnable at rank 1” do not follow.** The main problems are experimental design; I found two reporting bugs with no effect on the headline counts.

Read-only audit; no files edited. Paths below are relative to `research/remember`. Round 2’s report is `REMEMBER2.md`.

1. **Headline recount — OK**

   I ran a separate, in-memory Python script using only JSON/CSV readers. It selected jobs from each plan, required complete records, reconstructed exactness as `first_error is None or first_error >= length`, checked every JSON/CSV cell, sorted failing runs’ 1-based error steps, and selected index `(n−1)//2`. Pin counters were summed once per complete tape, excluding duplicate prefix rows.

   | Claim | Independent result | Match |
   |---|---:|---|
   | R1 pin exact at 2048 | **80/80** | Yes: `REMEMBER.md:8`, “80 of 80” |
   | R1 bitwise pin ticks | **163,840/163,840** = 80 × 2048 | Yes: `REMEMBER.md:7` |
   | R1 remember models with zero exact runs | **7/10** | Yes: `REMEMBER.md:5` |
   | R1 remember lower median first error | **3**, over **76 failures**, excluding **4 survivors** | Yes: `REMEMBER.md:6` |
   | R1 window exact at 1024 | **0/80**, zero in **10/10 models** | Yes: `REMEMBER.md:9` |
   | OLMo 5B / 84B / base, pin at 1024 | **0/4, 4/4, 4/4** | Yes: `REMEMBER.md:10` |
   | Same OLMo checkpoints, remember | **0/4, 1/4, 0/4** | Yes: `REMEMBER.md:10` |
   | R2 E-hist/remember exact at 256 | **4/16** | Yes: `REMEMBER2.md:5` |
   | R2 E-hist/remember median at 4096 | **26**, 16 failures, zero excluded | Yes: `REMEMBER2.md:6` |
   | R2 E-hist/pin exact at 4096 | **7/16** | Yes: `REMEMBER2.md:7` |
   | R2 E-pin/pin exact; E-pin/remember median | **16/16; 3** | Yes: `REMEMBER2.md:9` |
   | R2 E-pin bitwise ticks | **65,536/65,536** | Yes: `REMEMBER2.md:236` |

   “Full-history arms fail” requires qualification. The four R1 survivors are directly recorded by the substring `remember,2048,2048,1` at `results/r-qwen3-0.6b/runs.csv:41`, `:47`, `results/r-qwen3-1.7b/runs.csv:35`, and `results/r-qwen3-14b/runs.csv:29`.

   I also checked all displayed exactness cells, first-error anatomy, and margin summaries; they reproduce under the report’s **lower-median** convention. However, JSON and CSV are two serializations of the same measurements: `rem_job.py:324` explicitly says “written from the same payload as the json.” The recount validates arithmetic, not the original `torch.equal` measurements; those are performed at `rem_job.py:279`.

2. **Frozen predictions and verdicts — OK arithmetic; BUG in one guard; DESIGN FLAW in interpretation**

   The prediction sections match their registration commits (`9807f8d1` and `e9699430`). The shortened horizons are disclosed: `REMEMBER.md:108` says “Read the measured claims at 2048”; `REMEMBER2.md:76` records one tape and lengths `[256, 1024, 4096]`.

   The observations do **not** satisfy several registered predictions:

   - R1 predicted zero remember survivors in **each** model (`REMEMBER.md:65`); only 7/10 meet that condition. OLMo-84B also contradicts the zero-survivor prediction (`REMEMBER.md:71`; raw survivor at `results/r-olmo2-7b-84B/runs.csv:7`).
   - R2 predicted at least half the history runs exact at 256 in **at least three models** (`REMEMBER2.md:53`). Counts are **0/4, 1/4, 2/4, 1/4**: only Llama qualifies (`REMEMBER2.md:179`, `:183`, `:187`, `:191`).
   - R2 predicted a history median **above 32** and all E-hist/pin runs exact (`REMEMBER2.md:55`, `:57`); observed values are **26** and **7/16**. The decline from 4/16 at 256 to 0/16 at 4096 supports decline at the measured horizon, not the unmeasured 8192 prediction.

   **BUG:** R1’s registered certification guard requires “the edit file’s sha256 is in the job record” (`REMEMBER.md:127`). The actual predicate at `rem_report.py:244–246` checks certification, bitwise counts, and exactness but never checks edit metadata. Removing `edits` from an in-memory summary still returns `ruled_out=True`. Require hash presence for every counted model; compare registered hashes if claiming identity. **Current numerical effect: none**—the records contain hashes.

   **DESIGN FLAW:** Neither report implements a test of impossibility or exclusive learnability. The exactness rule is merely `return first_error is None or first_error >= length` (`rem_models.py:108`). Failure of one training recipe cannot establish that no rank-1 history solution is learnable.

3. **Context, feedback, and leakage — OK execution; DESIGN FLAW for broader claims**

   - **Exact pinned context:** tokenizer document prefix plus the **entire transition table**, followed by `[predicted current state, supplied event]`. Every table row contains its answer: `pb_pin.py:140` writes `[id_of[s], id_of[e], id_of[t], nl]`. `rem_job.py:394` prepends the document prefix; `../promptbox/pb_pin.py:243–246` uses positions `[P, P+1]` and `_clone(past)`. Thus every tick can look up its destination in Π. This is legitimate table execution, but not answer-free inference.
   - **No oracle state feedback during evaluation:** `rem_job.py:275` obtains `nxt` from the model; `:288` assigns `s = nxt`; `:290` feeds that state. `want` is used for comparison at `:282`. Round 2 does the same at `r2_eval.py:64`, `:71`, `:78–81`.
   - **Training teacher forcing is causal:** the true next state becomes the following block’s state (`r2_data.py:33–36`), while supervision is at the preceding event position (`:57`). Visibility is `idx[:, None] >= idx[None, :]` (`:82`), so that future state cannot be attended to. Training samples `pool["train"]` (`r2_train.py:155`); evaluation samples `pool["test"]` (`r2_eval.py:42`), with duplicate token IDs excluded by `../universal/uni_models.py:160`.
   - **Selection leakage/design bias:** evaluated tables were selected because E-pin already passed them: `rem_models.py:128`, `passed = [t for t in records if t["pass"]]`. Round 2 reuses that selection (`r2_models.py:88`, `return R.TABLES[name]`). This supports performance **conditional on E-pin certification**, not an unbiased comparison of the two edits’ generalization.
   - **“10 families” is inaccurate:** `rem_models.py:69–70` lists ten model checkpoints, five Qwen3 sizes. The machine generator has four shapes—`"random", "perm", "counter", "sticky"` (`../promptbox/pb_pin.py:109`)—and tables repeat across models (`rem_models.py:75–94`). These are not ten distinct machine families.
   - **A tick is one event transition**, not one bit or independent test: `rem_job.py:273–281` makes one prediction per event. Repeated visits to the same certified row contribute additional ticks.

4. **Fairness, rank, and checkpoint selection — DESIGN FLAW overall; implementation checks OK**

   **R1:** policies receive the same `pi`, tape, initial state, and weights (`rem_job.py:419–422`). Table encoding is identical; positions and execution format are not. PIN processes two tokens together at `[P,P+1]`; FULL processes individual tokens at `P+j` (`../bigidea/bi_stream.py:131`, `:140`, `:154–170`). Consequently, this comparison combines history retention, advancing positions, and forward-pass format. It does not isolate forgetting alone.

   **R2:** matching “budget” means matching supervised labels and optimizer updates. The report explicitly says “the number of tables in a step drops from 48 to 3” (`REMEMBER2.md:27`). Therefore, over 100 steps:

   - Both receive **76,800 supervised destinations**.
   - E-pin receives **4,800 table draws**; E-hist receives **300**, with correlated trajectory states.

   These are unequal data exposure and coverage, despite equal label counts. The implementations are `../universal/uni_job.py:343` for independent pinned examples and `r2_train.py:154–157` for history trajectories.

   **OK:** the actual compared recipes use 100 steps, five-step warmup, matching within-model learning rates and parameter counts. All four history records select run zero (`results2/train-*/train.json:3`, `"chosen": 0`). There is one CE loss from the first step (`r2_train.py:179–180`); checkpoint writes occur afterward (`:198–209`). There is no checkpoint selected before a delayed loss term activates. The optional retry selects by **pinned** validation (`:288–294`), which would favor pin performance, but it did not run here.

   **OK rank implementation, qualified terminology:** LoRA uses `r=1`, `lora_alpha=2`, q/k/v/o targets, and all layers (`r2_train.py:128–134`; saved config `results2/train-llama3.1-8b/edit/chosen/adapter_config.json:18`, `:20`, `:31`, `:34–38`). This is rank one **per adapted projection**, not one rank-one update for the whole network. Qwen uses an additive activation vector—`h = h + ... * add` (`../universal/uni_models.py:275`)—rather than LoRA. The report correctly distinguishes these classes at `REMEMBER2.md:21`.

5. **Figures — OK; trace-size promise — BUG**

   Both saved PNGs agree with the independently checked counts. R1 plots `exact / n` and lower-median first errors (`rem_fig.py:45`, `:55–57`). R2 plots `exact / n`, with the documented color/style mapping and E-hist/remember title counts (`r2_fig.py:30–34`, `:51`, `:57–58`), matching its caption at `REMEMBER2.md:172`.

   **BUG:** `REMEMBER2.md:35` promises “at most 96 points.” `r2_data.py:108–116` subsamples, then appends the endpoint and first-error point without enforcing the cap. Stored traces reach **97–98 points**; an example begins at `results2/eval-qwen3-1.7b/runs.json:95` and includes the appended endpoint at `:481`. Reserve slots for mandatory points before sampling. **Effect on headline numbers and these figures: none.**

**BUGs by severity**

- **Medium:** R1 certification verdict omits its required hash check; current counts unchanged.
- **Low:** R2 decimation exceeds its promised cap; current counts and figures unchanged.

**Headline claims that survive**

- **R1:** 80/80 selected, certified pin runs are recorded exact through 2048, with 163,840 matching tick logits.
- **R1 history:** 76/80 runs fail; universal failure and necessity of forgetting are unsupported.
- **R2:** this history-training recipe yields 4/16 exact at 256, 0/16 at 4096, and median first error 26.
- **R2 learnability:** “only pin is learnable at rank 1” does not survive the unequal data exposure, selected evaluation tables, and mixed edit classes.

**Minimal re-runs**

No GPU rerun is needed to retain the descriptive counts or fix the two reporting bugs. For a fair learnability comparison, retrain paired edits on identical tables, trajectories, supervised positions, steps, learning rates, and a common frozen selection rule; evaluate on fresh tables selected independently of either edit. To attribute the difference specifically to forgetting, additionally separate position reset and token-by-token versus two-token execution—the existing `TOK` and `ADV` controls already expose those distinctions (`../bigidea/bi_stream.py:156–165`).