# CHAT3: the gate (T5) and the chat fine-tune (T4)

CHAT stream of SKETCHPAD3 (brief `research/meta/sketchpad3/CHAT.md`, contract `CONTRACT.md` beside it), branch `chat`,
Modal app `polyformer-chat`, cap $25. Neo approved the work and its spend on 30 Oct 2026.

## Report

**Commits on `chat`:** ae54f59a (T5), 6699624c, 981eb016, 6095c0bf, and the final commit with this report.

**T5 passed.** `patch_onnx_lora.py` now builds the decoder with one more input, `lora_gate` (float16, shape `[1]`). It
was tested on ONNX Runtime 1.31.1 CPU with 100 chat prompts × 25 calls and all 1,795 E6 rows. Gate 0 is bit-identical
to stock Qwen3.5-0.8B and gate 1 is bit-identical to today's page graph, in logits, hidden states and every cached
state. The page's WebGPU provider was not tested.

**T4 failed its registration.** I trained four adapters (P1 to P4), and none passes every bar. All four keep every
table row and stay well inside the perplexity kill line, and none hits a kill line. So I declare no shipping E8: the
page should keep chat at gate 0, as it has since 441e3283. The two candidates are on the `polyformer-chat` volume:
- **P4**, `runs/train_p4/files/p4`. This was the last run. It is my pick if Neo wants gate-1 chat anyway, because its
  GSM8K and MMLU are nearest stock. It fails the word bar (0.817) and the IFEval bar (−4.4 points).
- **P2**, `runs/train_p2/files/p2`. It comes nearest the registration: only the word bar fails, by one item (0.894), and
  IFEval is −0.55. But it breaks multi-step word problems: GSM8K falls from 0.516 to 0.204, because it writes one
  confident wrong expression.

| measure (held-out templates; gate 1 zero-shot vs stock few-shot) | bar | stock | P2 | P4 (last run) |
|---|---|---|---|---|
| opening the sheet: precision / recall | ≥ 0.95 | 0.971 / 0.809 | **1.000 / 0.998** ✓ | **1.000 / 0.994** ✓ |
| word problems → correct sheet line | ≥ 0.90 | 0.789 | 0.894 ✗ (161/180) | 0.817 ✗ (147/180) |
| equations → correct `solve` line | ≥ 0.95 | 0.583 | **0.975** ✓ | **0.958** ✓ |
| expressions from mixed text (prose) | ≥ 0.95 | 0.667 | **1.000** ✓ | **0.992** ✓ |
| IFEval strict prompt-level, minus stock (0.536) | ≥ −2 | — | **−0.55** ✓ | −4.44 ✗ |
| kill: table rows (E7, 2,446) | all | — | 2,446 ✓ | 2,446 ✓ (min margin 5.37) |
| kill: PRIMER perplexity / stock | ≤ ×1.03 | 18.46 | ×1.004 ✓ | ×1.013 ✓ |
| kill: IFEval more than 5 points down | not hit | — | not hit | not hit (−4.44) |
| MMLU 500 (report) | — | 0.476 | 0.422 | 0.442 |
| GSM8K 250, Python stand-in for the sheet (report) | — | 0.516 | 0.204 | 0.452 |

**What failed, and why.**
- **The word bar.** It fails on two of the twelve held-out templates, which the model misreads every time. In
  "how many kg under the limit", it computes load − limit instead of limit − load (14/14 wrong in P2, P3 and P4).
  In "earns $h an hour, works n hours, pays fees", it drops or misplaces the hours (P4 15/15 wrong, P2 1/15). On the
  other ten templates, P2 and P4 are both 147/151 (0.974). This is a reading error by the 0.8B, not a format error. I
  did not train on these two structures, on purpose: that would have taught to the held-out set.
- **IFEval against GSM8K: a seesaw.** Every change that brought multi-step reasoning back cost instruction-following:
  - P2: −0.55 IFEval, 0.204 GSM8K.
  - P3 (human GSM8K solutions): −2.8 IFEval, 0.376 GSM8K.
  - P4 (stock's own solutions, ARC in its own batch): −4.4 IFEval, 0.452 GSM8K.

  The IFEval bar is also near the noise.
  - P4 against stock disagrees on 116 of the 541 prompts (stock passes 70 that P4 fails; P4 passes 46 that stock
    fails). Under a no-difference null, the net count would then vary by about ±11 prompts, which is ±2 points.
  - So the −2 bar is one standard deviation wide. P4's −4.4 is about 2.2 SD below stock, and P2's lead over P4 is
    also about 2.2 SD.
- **The sheet did not help on GSM8K.** P4 opens it on 221 of 250 problems, at 3.0 calls each. It is right on 100 of
  those 221 and on 13 of the 29 it does not open. That is below stock's 129/250 without a sheet. Its errors are in
  choosing operations, which the sheet does not check.

**Predictions against results for P4 (the last run).**

| measure | predicted | result |
|---|---|---|
| precision | 0.99 | 1.000 |
| recall | 0.99 | 0.994 |
| word | 0.89 | 0.817 |
| equations | 0.97 | 0.958 |
| prose | 0.99 | 0.992 |
| IFEval | −1.0 | −4.4 |
| MMLU | 0.45 | 0.442 |
| GSM8K | 0.50 | 0.452 |
| rows | all | all |
| perplexity | ×1.00–1.02 | ×1.013 |

I was wrong on IFEval, which I predicted would improve and which got worse, and on word.

**Spend:** $19.72 on Modal billing for app `polyformer-chat` on 30 Oct (22:54 UTC), against a $25 cap. I am not
launching another run: P4 was registered as the last.

**Options for Neo.** The problem belongs to continual learning (adding a skill without losing old ones). Its standard
fixes are replay, distillation (used here), parameter isolation (the gate is one) and routing. Options:
1. **Keep chat at gate 0.** This is the status quo: stock chat, and the sheet only on the page's own arithmetic path.
   It breaks nothing. It buys no model-initiated sheet.
2. **Switch the gate inside a reply.** Stock (gate 0) writes all prose. The page switches to gate 1 only between
   ```` ```sheet ```` and the closing ```` ``` ````, so P4 writes the work order. Prose is stock's by construction.
   - It breaks the zero-shot condition: stock needs the sheet system prompt to open the sheet at all. Measured
     few-shot, stock opens with recall 0.81 (bar 0.95) and precision 0.97.
   - A risk: at gate 1 the adapter would read a cache written at gate 0, which it never saw in training.
   - It costs one evaluation, about $1, and no training.
3. **One more run (P5), about $3.5, inside the cap.** It would use P2's recipe plus stock's own GSM8K solutions,
   without the ARC batch. It breaks the "P4 was the last run" registration. I would expect P4-like IFEval at best,
   given the seesaw above.

**Assumptions Neo did not ask for:**
- I scored sheet lines and GSM8K with a Python stand-in, not the certified sheet.
- I assume visitors to a calculator chat ask multi-step word problems at least as often as format-constrained prompts.
  That assumption is why I pick P4 over P2.
- The held-out templates test new phrasings, not new mathematics.

## T5: the gate

**What the page needs to wire.** The decoder graph built by `research/sketch/patch_onnx_lora.py` (default; `--no-gate`
builds the old graph) has one more input:

| name | dtype | shape | meaning |
|---|---|---|---|
| `lora_gate` | float16 | `[1]` | 0 = stock Qwen3.5-0.8B, 1 = the sheet machine (today's adapter graph) |

Every LoRA branch's output is multiplied by it before it is added back: y = x W + gate · scale · (x Aᵀ) Bᵀ, in all 150
patched matmuls (q, k, v, o in the 6 attention layers; in_proj_qkv, in_proj_z, out_proj in the 18 gated-delta-net
layers; gate, up, down in all 24 MLPs). Nothing else changes: the base
weights, the inside patch (`hidden_states` out, `steer` in) and `lens.bin` are the same files. The worker must feed
`lora_gate` on every decoder call, the way it feeds `steer` (transformers.js feeds only the inputs it knows): chat at 0
until T4 passes, sheet steps at 1. It is an input, not a constant, so one session serves both.

**Why it is exact.** At gate 0 each patched matmul computes x W + 0 (IEEE: adding a zero returns the other operand), at
gate 1 it computes x W + d · 1 = x W + d. Neither depends on fusions, as long as the runtime does not reorder these
elementwise ops into the matmul; the test checks that it does not on ONNX Runtime CPU.

**Rebuild check ($0, local graph surgery).** `patch_onnx_lora.py --no-gate` on the E6 seed 3 adapter, then
`patch_onnx_inside.py`, reproduces the page's `arithmetic/onnx/decoder_model_merged_fp16.onnx` byte for byte (sha256
`e906c473…`), so the gated graph differs from today's only by the gate.

**Identity test** (`research/sketch/chat/gate_identity.py`, Modal CPU, ONNX Runtime 1.31.1 CPUExecutionProvider, the page's
fp16 decoder files): three graphs, stock (base + inside patch), today (`arithmetic/` as deployed) and gated (E6 + gate +
inside patch). Pairs stock vs gate 0 and today vs gate 1; every call compares logits, `hidden_states` and every present
state bit for bit.
- 100 chat prompts (HuggingFaceH4/no_robots test split, first user turn, chat template, thinking off): one prefill with
  all logits, then 24 greedy decode steps through the cache;
- all 1,795 E6 table rows: inputs_embeds and 3-D positions captured from the Hugging Face forward (fp32 embeddings and
  vision tower, so not the page's q4/fp16 inputs; an identity test needs only the same inputs on both sides).

Smoke (1 prompt, 18 rows): 25/25 chat calls and 18/18 rows bit-identical on both pairs; today and gate 1 answer 18/18
rows right on these inputs, stock 0/18 (the inputs are real).

**Full run (8 CPU shards, 30 Oct, ~5 min each; summary `gate_identity_summary.json`): bit-identical everywhere.**

| pair | chat calls (100 prompts × 25) | table rows | logits, hidden_states, presents | max diff |
|---|---|---|---|---|
| stock vs gate 0 | 2,500 / 2,500 | 1,795 / 1,795 | all bit-identical | 0 |
| today vs gate 1 | 2,500 / 2,500 | 1,795 / 1,795 | all bit-identical | 0 |

Greedy continuations identical on 100/100 prompts for both pairs. On the captured row inputs, today's graph and gate 1
answer 1,795/1,795 rows right at every answer place; stock 12/1,795. So gate 0 is stock Qwen and gate 1 is today's graph
on ONNX Runtime CPU; the certificate is unchanged by construction. Not tested: the page's WebGPU execution provider (no
WebGPU on Modal). The argument above holds there unless that provider fuses the gate's Mul into the matmul; a cheap
on-device check is the page's own certificate at gate 1 (it must match today's margins exactly).

## T4: the chat fine-tune

### Registration (30 Oct 2026, written before any T4 spend; predictions are mine, made before the baseline)

Measured on the held-out templates of `dialogues.py` (never trained), the model at gate 1 (stock + adapter) zero-shot,
against stock Qwen few-shot on the same items (system prompt describing the sheet plus four example exchanges). Every
sheet line is scored by running it through `sheet_ref.py`, the host stand-in for the sheet, never by string match.

| measure | threshold | my prediction |
|---|---|---|
| opening the sheet: precision | ≥ 0.95 | 0.97 |
| opening the sheet: recall | ≥ 0.95 | 0.96 |
| word problems → a correct sheet line (held-out templates) | ≥ 0.90 | 0.85 (fails) |
| equations copied into a correct `solve` line (also expand, factor, systems) | ≥ 0.95 | 0.93 (fails narrowly) |
| numeric expressions from mixed text (prose family) | ≥ 0.95 | 0.97 |
| IFEval strict prompt-level accuracy, gate 1 minus stock | ≥ −2 points | −1.5 |

Kill lines (any one stops the final adapter from shipping): any table row lost (all 1,795 E6 rows, or E7's rows when the
final run starts from E7, must keep margin > 0 in PyTorch); plain-text perplexity above ×1.03 of stock (prediction
×1.01); IFEval more than 5 points below stock (prediction: not hit).

Reported without a prediction: GSM8K (250 test problems, seed 0) stock versus gate 1 with the sheet (blocks run on the
Python stand-in, not the certified sheet), and MMLU (500 test questions, seed 0, zero-shot letter logits) stock versus
gate 1.

My guesses for the stock few-shot baseline, so the gap is honest: precision 0.6, recall 0.5, word 0.4, equation 0.3,
prose 0.5. Assumptions I am making that Neo did not ask for: the held-out templates are new phrasings and new scenarios,
not new kinds of mathematics, so they measure transfer within the format, not GSM8K-style reasoning; single-digit
+ − × with one operation is the only arithmetic the model should do without the sheet; the `= …` line formats follow the
PROGRAM stream's runtime as of 30 Oct and may drift (they are masked from the loss, so a drift costs little).

### Baselines (Modal H100, 30 Oct; `chat_eval.py`)

| model | IFEval strict prompt | IFEval loose | IFEval instruction | MMLU (500) | GSM8K (250) | text ppl | table rows |
|---|---|---|---|---|---|---|---|
| stock Qwen3.5-0.8B (gate 0) | 0.536 | 0.577 | 0.640 | 0.476 | 0.516 | 18.46 | — |
| E6 (today's page, gate 1) | 0.372 | 0.409 | 0.508 | 0.400 | — | ×1.0065 | 1,795/1,795, MUL min margin 3.35 |

So today's chat at gate 1 is 16.4 IFEval points and 7.6 MMLU points below stock, while perplexity moved 0.65%: the
compile baseline's lesson again, now on a public benchmark. The row certificate in my evaluation reproduces E6's
documented one exactly (1,795, MUL 3.35), which checks the evaluation's table path. GSM8K: replies end with
`Answer: <n>`, else the last number counts; 36/250 stock replies hit the 640-token cap (scored as misses for every
model alike).

### Stock few-shot baseline on the held-out set (`eval_stock_fewshot`, 5.7 min)

Precision 0.971, recall 0.809 (437 of 540 sheet problems opened, 13 of 240 distractors); correct first sheet line:
calc 0.417, prose 0.667, word 0.789, equation 0.583; single-digit answers 50/50. Far stronger than my guesses (0.6,
0.5, 0.4, 0.3, 0.5): with the format spelled out and four examples, stock already writes good work orders; its losses
are recall (it answers in its head instead) and equations (it drops `solve`, or writes the equation as an expression).

### Pilot P1 (from E6, d1, 600 steps, ~$1.9)

Recipe: lr 1e-4 → 1e-5 cosine, 8 dialogues + 16 table rows (+6 replayed weak rows) + 4 KL prompts (reply positions
only, w 1) + PRIMER text KL (w 1) per step; 878 s for 600 steps on an H100.

| measure | stock few-shot | P1 (gate 1, zero-shot) | bar |
|---|---|---|---|
| open precision | 0.971 | 0.957 | ≥ 0.95 ✓ |
| open recall | 0.809 | 0.996 | ≥ 0.95 ✓ |
| word → correct line | 0.789 | 0.872 | ≥ 0.90 ✗ |
| equations → correct line | 0.583 | 0.967 | ≥ 0.95 ✓ |
| prose → correct line | 0.667 | 0.983 | ≥ 0.95 ✓ |
| calc → correct line (not registered) | 0.417 | 0.933 | — |
| IFEval strict prompt | 0.536 (stock) | 0.488 (−4.8) | ≥ −2 ✗ (kill at −5: not hit) |
| MMLU (500) | 0.476 (stock) | 0.410 | report |
| table rows | — | 1,795/1,795, min margin 6.59 (MUL) | all ✓ |
| PRIMER perplexity | 18.46 | ×0.988 | ≤ ×1.03 ✓ |

What the misses are: all 24 false opens are one held-out phrasing, `a − b = ?` (training taught `= ?` as a sheet
cue); 23 word misses come from two held-out structures, a discount then a fee (it drops `÷ 100`) and limit minus load
(it subtracts the wrong way round); the rest are copy slips (a decimal point, a bracket dropped) and a missing `solve`
on new phrasings. IFEval: P1 loses 73 prompts stock passes and wins 47, spread over every instruction type (no commas,
forbidden words, quotation, response language…): drift, not one broken behaviour. MMLU barely moved from E6 (0.400 →
0.410): reply-only KL on chat prompts does not restore knowledge.

### Run P2 = final candidate (from E7, d2): changes and predictions, registered before launch

E7 is ready (CALC3.md: 2,446/2,446 rows, min margin 3.96, perplexity ×1.0048,
`/sk/runs/e7_s3_4000_h4.0_stop3.0_fast/files/e7_adapter_s3_h4_v2_cont`), so this run starts from E7 and replays all
2,446 rows (strata add SUB 4, EST 6, DEC 1). Changes after P1:
- **Data d2.** Same held-out file as d1 (identical 780 items). Training sheet dialogues regenerated with more train
  phrasings (symbol single-digit forms `a + b = ?`, `a × b = ?`, `What is a − b?`, 150 of them with replies in stock's
  style `3 + 4 = 7`; more ways to ask for ÷ to k places, %, powers and `solve`) and three new train word scenarios with
  the structures P1 missed (a number minus a product; a discount then a fee). **Caveat:** I chose these after seeing
  P1's held-out misses, so the held-out word and false-open scores are no longer fully independent of my choices; the
  held-out templates themselves are still never trained.
- **Self-distillation stronger:** KL on every position of the instruction sequences (prompt and stock's reply), 8 per
  step, weight 2; plain-text KL moves from PRIMER.md to 2,000 chunks of 256 tokens from wikitext-2 (Wikipedia), 4 per
  step, so PRIMER perplexity becomes an untrained measure.
- 1,000 steps, otherwise P1's recipe.

Predictions for P2: precision 0.98, recall 0.99, word 0.93, equations 0.97, prose 0.98, IFEval −2.5 (still a narrow
fail of the 2-point bar; no kill), MMLU 0.44, every row certified, PRIMER perplexity ×1.00–1.02.

### P2 result (from E7, d2, 1,000 steps; 1,674 s training + 900 s evaluation, ~$3)

| measure | stock | P2 (gate 1) | bar | prediction |
|---|---|---|---|---|
| open precision | 0.971 (few-shot) | **1.000** (0 of 240 distractors) | ≥ 0.95 ✓ | 0.98 |
| open recall | 0.809 (few-shot) | **0.998** (539/540) | ≥ 0.95 ✓ | 0.99 |
| word → correct line | 0.789 (few-shot) | 0.894 (161/180) | ≥ 0.90 ✗ by one item | 0.93 |
| equations → correct line | 0.583 (few-shot) | **0.975** | ≥ 0.95 ✓ | 0.97 |
| prose → correct line | 0.667 (few-shot) | **1.000** | ≥ 0.95 ✓ | 0.98 |
| calc → correct line | 0.417 (few-shot) | 0.983 | — | — |
| IFEval strict prompt | 0.536 | **0.530 (−0.55)** | ≥ −2 ✓ | −2.5 |
| MMLU (500) | 0.476 | 0.422 (−5.4) | report | 0.44 |
| GSM8K (250, stand-in sheet) | 0.516 | **0.204** (sheet opened on 212) | report | — |
| table rows (E7) | — | 2,446/2,446, min margin 5.15 (EST) | all ✓ | ✓ |
| PRIMER perplexity (untrained now) | 18.46 | ×1.004 | ≤ ×1.03 ✓ | ×1.00–1.02 |

Stronger self-distillation fixed IFEval (−4.8 → −0.55) and the new train phrasings removed every false open. Two
failures remain. (1) Word problems miss the bar by one item: 14 of 19 misses are the held-out truck template ("how many
kg under the limit"), still written load − limit even after a train scenario of the same shape. (2) **GSM8K collapsed,
0.516 → 0.204**: the model learned "a word problem is one expression, written at once" and now skips the step-by-step
reasoning that stock does in words, writing a wrong one-liner and quoting it confidently (`52 − 8 ÷ 3.5` for a
three-runner problem; `2 × 30 ÷ 12` for sheets per month). Our synthetic word problems are all one-step translations,
so nothing taught it to reason before or between sheet calls. A model whose language half breaks on multi-step
problems is not "chats like stock", so P2 does not ship.

### Run P3 = final candidate (from E7, d3): changes and predictions, registered before launch

- **Multi-step data.** 1,200 GSM8K **training** problems (`gsm8k_dialogues.py`; the test split is never read) turned
  into replies that call the sheet once per step: GSM8K's own calculator annotations (`<<48/2=24>>`, Cobbe et al. 2021)
  become ```sheet blocks, each followed by the solution's sentence with the sheet's value; kept only when every
  annotation parses and the sheet prints exactly the annotated value (1,200 of the first 1,252). 3.2 blocks per reply.
  This is the ToRA / PAL pattern (reasoning in words, every calculation by the tool). d3 = d2's 3,150 + these 1,200.
- **MMLU guard.** 1,000 ARC (allenai/ai2_arc train) multiple-choice prompts, worded unlike my MMLU prompt, join the
  KL pool (prompt positions plus the letter distribution; no answers, no MMLU data).
- 1,200 steps, otherwise P2. GSM8K evaluation now allows 10 sheet blocks per reply (was 4).

Predictions for P3: precision 0.99, recall 0.99, word 0.91, equations 0.97, prose 0.99, IFEval −1.5, MMLU 0.45,
GSM8K 0.45–0.55 with the sheet (I expect it near stock, not above: the 0.8B's errors are in choosing operations, which
the sheet does not fix), every row certified, PRIMER perplexity ×1.00–1.02.

### P3 result (from E7, d3, 1,200 steps; 1,942 s training + 831 s evaluation, ~$3.3)

| measure | stock | P2 | P3 | bar | P3 prediction |
|---|---|---|---|---|---|
| open precision / recall | 0.971 / 0.809 (few-shot) | 1.000 / 0.998 | **1.000 / 0.994** | ≥ 0.95 ✓ | 0.99 / 0.99 |
| word → correct line | 0.789 (few-shot) | 0.894 | 0.856 | ≥ 0.90 ✗ | 0.91 |
| equations / prose | 0.583 / 0.667 | 0.975 / 1.000 | **0.975 / 0.992** | ≥ 0.95 ✓ | 0.97 / 0.99 |
| IFEval strict prompt | 0.536 | −0.55 | −2.8 (0.508) | ≥ −2 ✗ (kill −5 not hit) | −1.5 |
| MMLU (500) | 0.476 | 0.422 | 0.452 | report | 0.45 |
| GSM8K (250, stand-in sheet) | 0.516 | 0.204 | 0.376 (sheet on 250/250, 3.5 blocks each) | report | 0.45–0.55 |
| table rows (E7) | — | 2,446 ✓ | 2,446 ✓, min margin 5.78 | all | ✓ |
| PRIMER perplexity | 18.46 | ×1.004 | ×1.012 | ≤ ×1.03 ✓ | ✓ |

The ARC KL lifted MMLU (0.422 → 0.452) and the GSM8K-train replies lifted GSM8K (0.204 → 0.376), but IFEval slid
back (−0.55 → −2.8) and the word score fell. All word misses are single blocks (the score is not grading an
intermediate step): 14 truck ("under the limit": load − limit) and 11 worker-pay items (`152.25 + 26 × 152.25 − 227.75`
for pay minus fees), two of the twelve held-out templates; at about fifteen items each, one template the 0.8B misreads
costs eight points. GSM8K misses compute first and reason after (the human solutions' order: block, then the sentence),
e.g. adding the 52-mile total into the sum, or `20 ÷ 3 ÷ 4` for 20 ÷ (1 − 3/4). Two causes I can name for the IFEval
slide: 1,200 replies in GSM8K's terse human style (not stock's), and the ARC prompts taking 40% of the instruction KL's
slots (the KL pool was shared).

### Run P4 = last run within the cap (from E7, d4): changes and predictions, registered before launch

- **Multi-step data in stock's own words** (`gsm8k_stock.py`): stock solves GSM8K **training** problems step by step
  under a system prompt asking for each calculation on its own line (`8 × 3.5 = 28`); a solution is kept only if its
  answer is right and every calculation, run on the stand-in, prints exactly what stock wrote; each calculation line
  becomes a sheet block, so the reply reasons first (stock's words), then computes on the sheet, then goes on. The
  training dialogue has no system prompt. This replaces P3's human-written GSM8K replies (Toolformer's recipe: insert
  the tool into the model's own text, keep what checks out). At most 800 of them join d2's 3,150.
- **ARC in its own KL batch** (2 per step), so all 8 instruction-KL slots stay on instruction prompts.
- Everything else as P3 (1,200 steps, KL weight 2 on full sequences, wikitext text KL).

First try of `gsm8k_stock.py` (1,600 problems, 7 min, ~$0.5): only 9 kept (790 wrong answers, 764 with no
calculation on its own line: stock ignores that instruction and computes inline). Second try (2,000 problems): the
system prompt gains one worked example, and the converter also takes calculations written inside a sentence (`so she
serves 8 × 7 = 56 customers` → the words before it, the block, the sheet's value and the rest of the sentence); raw
replies are saved. Second try (10 min, ~$0.7): 547 kept of 2,000 (1,157 wrong answers, 173 with no calculation, 76
where stock's number format differs from the sheet's, 29 stock arithmetic slips, 18 unparsable steps), 2.6 sheet calls
per reply, in stock's own words: a plan sentence, the block, the value, the next step. d4 = d2's 3,150 + these 547.

Predictions for P4: precision 0.99, recall 0.99, word 0.89 (a narrow fail: I changed nothing aimed at the two
templates, on purpose), equations 0.97, prose 0.99, IFEval −1.0, MMLU 0.45, GSM8K 0.50, every row certified, PRIMER
perplexity ×1.00–1.02. Whatever P4 gives, it is the last run: the cap leaves room for no more.

### P4 result (from E7, d4, 1,200 steps; 2,709 s training + about 1,300 s evaluation, about $4.4)

| measure | stock | P2 | P3 | P4 | bar | P4 prediction |
|---|---|---|---|---|---|---|
| open precision / recall | 0.971 / 0.809 (few-shot) | 1.000 / 0.998 | 1.000 / 0.994 | **1.000 / 0.994** (537/540, 0 of 240 distractors) | ≥ 0.95 ✓ | 0.99 / 0.99 |
| word → correct line | 0.789 (few-shot) | 0.894 | 0.856 | 0.817 (147/180) | ≥ 0.90 ✗ | 0.89 |
| equations / prose | 0.583 / 0.667 | 0.975 / 1.000 | 0.975 / 0.992 | **0.958 / 0.992** | ≥ 0.95 ✓ | 0.97 / 0.99 |
| calc (not registered) | 0.417 | 0.983 | 0.967 | 0.950 (5 `÷ … to k places` slips) | — | — |
| IFEval strict prompt | 0.536 (290/541) | 0.530 (287) | 0.508 (275) | 0.492 (266), −4.44 | ≥ −2 ✗ (kill −5 not hit) | −1.0 |
| IFEval loose / instruction | 0.577 / 0.640 | 0.560 / 0.633 | 0.547 / 0.607 | 0.521 / 0.596 | — | — |
| MMLU (500) | 0.476 | 0.422 | 0.452 | 0.442 | report | 0.45 |
| GSM8K (250, stand-in sheet) | 0.516 (129) | 0.204 | 0.376 (94) | 0.452 (113; sheet on 221, 3.0 blocks each) | report | 0.50 |
| table rows (E7) | — | 2,446 ✓ | 2,446 ✓ | 2,446 ✓, min margin 5.37 (EST), SUB 5.41 | all | ✓ |
| PRIMER perplexity | 18.46 | ×1.004 | ×1.012 | ×1.013 | ≤ ×1.03 ✓ | ×1.00–1.02 |

The word misses are 33. Two held-out templates account for 29: truck "under the limit", 14/14, written load − limit;
and worker pay minus fees, 15/15, with the hours dropped or misplaced, e.g. `152.25 − 227.75`. The other four are two
crate problems left unopened, one snow item and one field item. On the other ten templates P4 scores 147/151, the same
as P2.

IFEval against stock: P4 loses 70 prompts and wins 46. Reply lengths match stock (median 1,053 characters against
1,056), and the sheet opened on 1 of 541 prompts. So this is spread-out drift, not one broken behaviour, as with P1.
P2 against P4: P2 alone passes 56 prompts and P4 alone passes 35. That is about 2.2 standard deviations of paired
noise, so the cost of the stock-style GSM8K data and the ARC batch is probably real. Of the three changes from P2
(the 547 stock-solution dialogues, the ARC batch and 200 more steps), I cannot tell which one cost it.

GSM8K against stock: P4 loses 45 and wins 29. It is right on 100 of the 221 problems where it opened the sheet and on
13 of the 29 where it did not. The replies now reason before each call, as stock does: a plan sentence, the block, the
value. The remaining errors are in choosing the operation.

### Option 2, the gate switched inside a reply: registered before launch (30 Oct, approved by the orchestrator)

This is an evaluation, not a training run: P2 and P4 stay as trained, and "P4 was the last run" stands.

**Setup** (`gate_switch.py`). Stock Qwen at gate 0 writes the reply under the sheet system prompt and the four example
exchanges, the same messages as the stock few-shot baseline. As soon as its text ends with ```` ```sheet ````, the
adapter (gate 1) writes the block, up to and including the closing ```` ``` ````. The runtime's `= …` lines and
everything after them are gate 0 again.

A forward runs at the gate of the token it predicts. So the adapter reads the keys, values and delta-net states that
stock wrote: the cache is shared across the switch, as it would be on the page.

The mechanism, in one Hugging Face `generate` per batch:
- Every LoRA layer's scale becomes a per-row tensor (0 or alpha/r = 2).
- A logits processor picks each row's greedy token, or the runtime's forced token, and sets the next forward's gate.

Both writers are scored, P4 and P2. Self-test before anything else:
- logits with every row at gate 0 must equal the disabled adapter bit for bit;
- mixed-gate rows must equal their single-gate rows;
- 16 IFEval replies at gate 0 must equal plain stock generation token for token.

**Cache-mismatch test.** For each held-out item where a block opened, I take the context up to the opener and let the
writer write the block again, this time from a context prefilled entirely at gate 1. I compare the identical-block rate
and the line accuracy from the gate-0 cache against the gate-1 cache. I do the same, by identity only, for the first
GSM8K block.

**Bars:** T4's, unchanged. Precision and recall ≥ 0.95; word ≥ 0.90; equations ≥ 0.95; prose ≥ 0.95; IFEval strict
within 2 points of stock zero-shot (0.536). Kill lines: rows and perplexity cannot move, because the adapters are
unchanged and gate 0 is stock (T5); IFEval more than 5 points down.

**Predictions** (P4 writer; P2 in brackets):

| measure | prediction | why |
|---|---|---|
| precision / recall | 0.97 / 0.81, recall fails | opening the sheet is stock few-shot's own decision (437/540 and 13/240 in that baseline) |
| word | 0.78 [0.80], fails | stock opened 176/180; the writer is right on about 0.8 of those after stock's prose |
| equations | 0.83 [0.85], fails | stock opened 111/120, so 0.925 is the ceiling |
| prose | 0.65 [0.65], fails | stock opened 80/120, so 0.667 is the ceiling |
| IFEval strict | 0.52 (−1.6), passes | — |

- **IFEval is not stock zero-shot's by construction.** The system prompt changes stock. What is stock's by construction
  is stock few-shot: the gate-switch replies should equal it on every prompt where no block opens. I predict a block
  opens on at most 3 of the 541 prompts.
- **IFEval paired flips against stock zero-shot:** 40 prompts only stock passes, 31 only the gate switch passes.
- **GSM8K** (Python stand-in): 0.47. **MMLU** (gate 0 with the sheet prompt): 0.47.
- **Cache:** identical first blocks on 80% of the opened held-out items, and line accuracy from the gate-0 cache within
  3 points below the gate-1 cache.
- **Spend:** about $2: an H100 for about 30 minutes, one full pass with P4 and the opened items again with P2.

So I predict the gate switch, as specified, fails four bars, because stock decides when to open the sheet. What it buys
is IFEval near stock's, and the first measurement of the cache risk.

### Data (`dialogues.py`, seed 0)

3,000 training dialogues: calc 504, prose 420, word 714, equation 462, distractors 900 (30%: no_robots train prompts
342, single-digit arithmetic 203, writing 81, chit-chat 75, facts 71, code 64, maths talk 64); 15% carry an earlier
exchange as context. Held-out set: 780 items (calc, prose, equation 120 each, word 180, distractors 240 from held-out
templates and no_robots test prompts 100 onward). A sheet reply is three segments, tokenized separately exactly as the
page will see them: the model's text up to and including the closing ```` ``` ```` (its own token), the runtime's
`\n= …\n` (masked), the model's continuation quoting the value verbatim, then `<|im_end|>`. `--format ops` writes the
older one-operation-per-line work order (not trained).

**Protocol for the page** (what the worker must do at gate 1): generate until the model emits the token ```` ``` ````
that closes a block opened by ```` ```sheet ````; run the block; append the tokens of `"\n" + result lines joined by
"\n" + "\n"`; continue generating.

## Spend

| job | what | cost |
|---|---|---|
| gate_1349_0, gate_1351_0…7 | T5 identity test, CPU | ≈ $0.5 |
| stock_1401 | stock replies (900 distractor turns, 209 earlier turns, 1,500 KL prompts), H100 13.5 min | ≈ $0.9 |
| eval_stock, eval_e6 | baselines, H100 ~16 min each | ≈ $2.2 |
| running total (Modal billing, app polyformer-chat, 30 Oct 14:22) | | $4.83 |
| eval_stock_fewshot | stock few-shot on the held-out set, H100 5.7 min | ≈ $0.4 |
| train_p1 | pilot P1 (train + eval) | ≈ $1.9 |
| train_p2 | P2 (train + full eval) | ≈ $3.0 |
| train_p3 (+ gsm8k annotations) | P3 (train + full eval) | ≈ $3.3 |
| gsm8k_stock ×2 | stock's own GSM8K-train solutions (1,600, then 2,000 problems) | ≈ $1.2 |
| train_p4 | P4 (train + full eval), plus one launch that failed at once (stale volume) | ≈ $4.4 |
| **total (Modal billing, app polyformer-chat, 30 Oct 22:54 UTC)** | image builds and idle containers included | **$19.72** of $25 |

## Glossary candidates

- Gate (hard LoRA gate): a 0/1 graph input multiplying every adapter branch; ours (SKETCHPAD3 T5, 30 Oct 2026); gate 0
  is the base model exactly, so the language half is untouched whenever the sheet is off.
- Self-distillation / Learning without Forgetting [zoo]: training a changed model to keep matching the old model's output
  distribution on old-task inputs (Li and Hoiem 2016); here the teacher is the same weights with the adapter off, and the
  match is a per-token KL on stock Qwen's own replies to instruction prompts, so chat stays stock-like at gate 1.
- KL divergence: a measure of how far one probability distribution is from another (zero when equal); the loss term that
  pulls the adapted model's next-token distribution toward stock's.
- IFEval (Zhou et al. 2023, Google): 541 prompts with checkable instructions ("no commas", "at least 300 words"); strict
  prompt-level accuracy counts a prompt only if every instruction is followed; our kill line for chat damage.
- MMLU (Hendrycks et al. 2021): multiple-choice questions over 57 subjects; a broad-knowledge check that the adapter did
  not erase what the base knew.
- GSM8K (Cobbe et al. 2021): grade-school maths word problems; here a check of whether opening the sheet helps on
  multi-step problems written by people, not by our templates.
- Precision and recall of opening the sheet: of the replies that opened it, the share that needed it (precision); of the
  problems that needed it, the share where it was opened (recall).
- Held-out templates: question phrasings and word-problem scenarios never seen in training, so the score measures
  transfer of the format, not memory of the templates.
- Stand-in (host sheet): `sheet_ref.py`, exact fractions on the CPU in place of the certified sheet, used only to write
  training data and to score; never presented as the sheet.
- Toolformer recipe [zoo] (Schick et al. 2023, Meta): let a model write its own text, insert tool calls where they would
  produce what it wrote, and keep only the examples that check out; here stock's GSM8K-train solutions with every
  calculation turned into a sheet call (P4), so the training replies are in stock's own words.
- PAL / ToRA (Gao et al. 2022; Gou et al. 2023): solving maths word problems by interleaving reasoning in words with
  program or tool calls for every calculation; the pattern of the multi-step data in P3 and P4.
- Rejection sampling (of training data): generate many candidates and keep only those that pass a check (here: right
  final answer, and every calculation reprinted exactly by the stand-in); 547 of 2,000 survived.
- Paired flip noise: when two models answer the same prompts, only the prompts where they disagree carry information;
  with D disagreements the net difference varies by about ±√D under no real difference (P4 vs stock: D = 116, ±11
  prompts, ±2 IFEval points), so a 2-point bar is one standard deviation.
- Continual learning / catastrophic forgetting: the field of adding a skill to a trained model without losing old ones;
  its standard tools are replay, distillation, parameter isolation (the gate) and routing; T4's IFEval/GSM8K seesaw is
  this problem.
- Gate switching inside a reply (option, untested): stock at gate 0 writes the prose and the adapter at gate 1 writes
  only the sheet block, so chat is stock by construction; costs zero-shot opening (needs a system prompt).
