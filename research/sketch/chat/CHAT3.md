# CHAT3: the gate (T5) and the chat fine-tune (T4)

CHAT stream of SKETCHPAD3 (brief `research/meta/sketchpad3/CHAT.md`, contract `CONTRACT.md` beside it), branch `chat`,
Modal app `polyformer-chat`, cap $25. Neo approved the work and its spend on 30 Oct 2026.

## Report

(written at the end)

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
