**The arithmetic reproduces. The main weakness is that the mandatory identity check bypasses the committee kernel. “22/24 exact” is also strictly teacher-forced state accuracy.** The report explicitly says “the true trace is teacher-forced” ([HEADPIN.md:13](/Users/neo/repos/polyformer-wt/headpin/research/headpin/HEADPIN.md:13)). No files were edited.

1. **Recomputation — OK.**

I independently read all JSONL records and decoded the corresponding NPZ arrays using Python’s standard library, without importing the reporting functions. I compared argmax IDs with target IDs, located the first incorrect token, took each run’s minimum stored margin, then aggregated counts and medians.

All **432 unique runs**, with no missing or duplicate grid entries, agree with their NPZ arrays. Every displayed result-table cell matches, including rounding. Each cell below contains values for **1,024 / 4,096 / 8,192**, with 24 runs per length.

| Policy | State-exact | Read-exact | Median minimum state margin |
|---|---|---|---|
| pin-all | 24 / 24 / 24 | — | 14.75 / 14.75 / 14.75 |
| full | 24 / 24 / 22 | 24 / 19 / 0 | 10.75 / 8 / 6.25 |
| pin-committee | 12 / 0 / 0 | 0 / 0 / 0 | 0.0625 / −4.25 / −8.625 |
| pin-random | 9 / 9 / 10 | 8 / 4 / 0 | −1.0625 / −1.375 / −1.0625 |
| requote-256 | 0 / 0 / 0 | 0 / 0 / 0 | −5.625 / −7.125 / −8.375 |
| requote-1024 | 2 / 0 / 0 | 0 / 0 / 0 | −3.5 / −7.875 / −8.0625 |

Raw policy blocks start at `results/counted/runs.jsonl:1,73,145,217,289,361`; reported rows start at `HEADPIN.md:70,73,76,79,82,85`. For example, the two full-history state failures are exactly `"n_state_wrong": 1` in compass tapes 1 and 3 ([runs.jsonl:138](/Users/neo/repos/polyformer-wt/headpin/research/headpin/results/counted/runs.jsonl:138), [runs.jsonl:140](/Users/neo/repos/polyformer-wt/headpin/research/headpin/results/counted/runs.jsonl:140)).

For E0, I independently calculated  
`S = z_uu − z_uv − z_vu + z_vv`, and each target’s margin against the highest recorded non-target top-two logit. All **32 records** agree. Recomputed medians, displayed at the report’s precision:

| Delay | Distant: S / margin-u / margin-v | Relocated: S / margin-u / margin-v |
|---|---|---|
| 64 | 50.78 / 11.75 / 10.56 | 77.57 / 14.88 / 16 |
| 256 | 50.12 / 11.88 / 12.91 | 76.6 / 14.81 / 16.5 |
| 1,024 | 47.09 / 8.312 / 10.91 | 78.21 / 15.12 / 16.5 |
| 4,096 | 45.32 / 10.81 / 13.12 | 76.8 / 14.94 / 16.19 |

Sources: four table blocks at `results/counted/e0.jsonl:1,9,17,25`; report at [HEADPIN.md:93](/Users/neo/repos/polyformer-wt/headpin/research/headpin/HEADPIN.md:93). **Falling: false; restored: true.**

Ancillary numbers also agree: census **72**, maximum **33,892**, zero over cap; five ledger charges recompute to **$1.1447 total** using the recorded pricing formula. Sources: `"max_tokens": 33892` (`results/counted/census.json:5`), pricing at `hp_modal.py:35,36,200`, charges at `results/modal_ledger.json:32,57,82,107,132`. Smoke timings **1.05 / 1.207 seconds** match the saved measurements (`smoke.json:110,111`); they cannot be independently re-timed from records. Run margins are verified against saved margin arrays, not reconstructed from unavailable full logits (`hp_core.py:281`).

2. **Frozen predictions and verdicts — OK for this complete dataset; two BUGs.**

The four prediction paragraphs are unchanged from registration commit `28813e1a`. Code implements H1’s implication, H2’s `<=`, H3’s strict `>`, and H4’s conjunction of strict decline and restoration. Independent verdicts are **H1 false, H2 true, H3 false, H4 false**. Exact comparisons: `"rnd <= full"` (`hp_report.py:134`), `"r256 > full8"` (`:141`), `"seq[i] > seq[i + 1]"` (`:162`), `"falling and restored"` (`:166`); registrations at `HEADPIN.md:35,37,39,41`.

- **BUG: E0 destination differs from registration.** Report: “v is the next state in the list” (`HEADPIN.md:25`). Code: `v = next(x for x in table["states"] if x != u)` ([hp_e0.py:20](/Users/neo/repos/polyformer-wt/headpin/research/headpin/hp_e0.py:20)). This chooses the **first unequal state**. With `[a,b,c,d]` and `u=b`, it chooses `a`, not `c`. Implement the registered successor, with explicit wraparound. Existing E0 arithmetic remains correct for the executed protocol; corrected E0 values and H4 are unknown.
- **BUG: H1 does not reject missing paired runs.** It uses `both = [k for k in pin if k in com]` (`hp_report.py:123`), silently dropping missing committee results. Require the complete expected key set and uniqueness before any verdict. **Effect here: zero**, because the independently checked grid is complete.

3. **Attention intervention — implementation looks correct for counted forwards; validation BUG.**

- **Active in counted forwards: OK.** The counted path sets `pin.spec = spec` and explicitly uses `use_cache=False` ([hp_core.py:232](/Users/neo/repos/polyformer-wt/headpin/research/headpin/hp_core.py:232), `:235`). Thus the nonempty-cache bypass does not disable these measurements.
- **Qwen3 ordering/GQA/head targeting: OK by inspection.** `q_norm(q_proj(...))` and `k_norm(k_proj(...))` precede RoPE (`hp_attn.py:58,59,137,189,191`). Contiguous KV repetition at `:51`, followed by indexing at `:193,194`, implements **KV head = query head // group**. Recorded geometry is **32 query / 8 KV heads**, hence group 4 (`smoke.json:92,93`). Selection uses `module.layer_idx` (`hp_attn.py:265`), and scattering writes the selected head indices (`:201,202`).
- **SDPA versus eager: OK for the recorded setup.** The loader explicitly requests `attn_implementation="sdpa"` (`../bridge/br_core.py:164`); the custom path directly imports SDPA (`hp_attn.py:29`). This does not establish eager-backend equivalence.
- **BUG: identity validation bypasses the intervention.** For all heads, `H.forward` sets **`pin.spec = None`** and invokes a separate sliced-layer implementation ([hp_core.py:228](/Users/neo/repos/polyformer-wt/headpin/research/headpin/hp_core.py:228)). No-heads returns `orig` (`hp_attn.py:266,282`). The additional diagnostic exercises only ordinary reconstructed attention at layer 0 (`:267,268`). **No identity check exercises the subset pin kernel** at `:176` or its other-position handling at `:205`. The record confirms `"all_heads_path": "sliced_layer"` (`smoke.json:105`). This fails the brief’s requirement to validate “pin-committee with all heads chosen” (`HEADPIN_BRIEF.md:50`).
- **BUG if used with cached generation:** `if spec is None or _past_len(past_key_values) > 0: return orig(...)` ([hp_attn.py:260](/Users/neo/repos/polyformer-wt/headpin/research/headpin/hp_attn.py:260)). Cached decoding silently loses the pin. Reject unsupported cache usage or implement it correctly. **Effect on current counted numbers: zero.**

4. **Leakage and comparison fairness — OK for conditional comparisons; DESIGN FLAWS for broader claims.**

**Teacher forcing:** every full-history table uses the true trace. The shared helper constructs state labels via `run_program(...)` (`../promptbox/pb_lit.py:207`), inserts them into `run_ids` (`:247,249`), and builds `ids = prompt + prog + opener + run + closer` (`../bridge/br_core.py:108`). Scoring predicts the state after the event (`hp_core.py:342,352`). Previous correct states are therefore supplied even after hypothetical errors. The final answer field is not appended by this layout. This supports conditional next-state accuracy, **not free-running reliability**; all 24 full-history runs at 8,192 have read errors (`HEADPIN.md:75`).

**Committee selection:** independently regenerated exactly from CIRCUITS’ `mrow > 0.5` and destination-slot argmax rules (`…/anatomy/circuits/ac_mkspec.py:14,16`). No HEADPIN-outcome selection is evident. However, CIRCUITS explicitly used **Savant r2** (`…/circuits/CIRCUITS.md:3,4`), while HEADPIN loads **r3** (`HEADPIN.md:29`). Thus this tests transfer of that particular committee, not every possible untrained pin.

**Training/fairness:** all arms share one frozen, merged model: `m.eval()` and `p.requires_grad_(False)` (`../bridge/br_core.py:168,170`), then iterate the same tapes (`hp_run.py:383,384`). There is no arm-specific rank, learning rate, training-step count, loss schedule, or checkpoint selection. Upstream checkpoint-training contamination is **not established absent** by these evaluation records. Programs explicitly use `split="train"` (`hp_core.py:174`); E0 uses `pool["train"]` (`:416`). These are not unseen-program/name generalization tests.

**Requote:** inserts only row tokens `[s,e,t,newline]` (`hp_core.py:80,139`) every W **original tokens after Π**, including intervening program text (`hp_seq.py:23,32,33`). Scoring correctly uses the position immediately before each original target (`hp_core.py:376,377`). It changes sequence length and format, so it does not isolate lag at equal token/compute budget. Likewise, random control matches head count, not layer distribution (`hp_heads.py:19,29`). These are limits on mechanism claims, not recount errors.

5. **Figures/captions — OK for supplied tables; curves missing.**

There are no figures in the report to validate. Table aggregation matches the captions: “median across tapes of each tape’s minimum state-token margin” (`HEADPIN.md:66`; implemented at `hp_report.py:186`). E0 medians also match. The brief requested “E0’s curves” (`HEADPIN_BRIEF.md:61`), but the delivered report contains a numerical table (`HEADPIN.md:91`).

**BUGs by severity:** high—identity gate bypasses the committee kernel; medium—E0 destination protocol mismatch; medium but dormant—cached decoding bypass; low and dormant—incomplete-grid H1 acceptance. Only the E0 correction necessarily requires new numerical measurements; the committee correction’s numerical effect is unknown until its actual kernel is validated.

**Headline claims that survive:**

- **Full history 22/24 at 8,192:** survives as teacher-forced state-exactness only.
- **Requote-256 does not beat full:** survives for this exact insertion protocol: 0/24 versus 22/24.
- **Committee pin does not beat full:** recorded counts survive; attribution to a correctly validated intervention remains provisional.
- **No untrained head pin can help:** unsupported; only one transferred committee and one random set were tested.
- **H4 fails:** survives for the executed E0 destination rule, pending correction to the registered rule.

**Minimal reruns:** validate the actual subset kernel against an independent attention reference, including selected/unselected heads and cache rejection; rerun the 144 committee/random cases only if that exposes a correction. For E0, regenerate changed `v` conditions—four delays × two placements per affected table—and recompute medians. Existing full/requote records need no rerun for their narrow teacher-forced claims. Free-running claims require a separately registered evaluation.