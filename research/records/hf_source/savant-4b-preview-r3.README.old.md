---
license: other
license_name: savant-proprietary
license_link: LICENSE
base_model: Qwen/Qwen3-4B
base_model_relation: finetune
library_name: transformers.js
pipeline_tag: text-generation
tags:
  - onnx
  - webgpu
  - transformers.js
  - qwen3
---

# Savant-4B preview r3

Savant-4B preview r3 is an experimental research preview made for the Polyformer demo page. It runs in the browser
with WebGPU through transformers.js. This is not a general-purpose assistant, and it is not meant for any use outside
that page.

## What changed in r3

- **Certified addition.** For explicit additions of two whole numbers ("What is 4096 plus 77?", "X + Y"), the model
  now writes the adder as a 200-row table, and the clock runs it with a certificate (see below). r3 continues
  r2's adapter for 500 steps of training on this format (ARITH, seed 1).
- **Kept from r2.** The six event families still use literal tables, certificates and pinned ticks. Word problems,
  other operations and ordinary questions are answered in words.
- **Same pipeline as r2.** The merge is done as the gates were scored. The ONNX export uses q4f16: 4-bit, with the
  v and down projections at 8 bits.

## What it does

When you ask a plain question about a sequence of events, for example a shell game, a parity check, a robot's walk,
a compass or a short story, the model writes a small program before it answers:

- a literal transition table for each quantity it has to track, `register X: start s` followed by rows `s e t`,
  in which every name is a single token;
- the place in the question where the events are, as two quoted anchors;
- `<exec/>`.

A small clock on the page then runs the table, and the model does the running:

1. **Certificate.** Every table row is checked with one forward pass. The model sees the table and a two-token
   block (the current state, then the event) and must put its largest logit, over the whole vocabulary, on the
   row's written destination, with a positive margin.
2. **Run.** The clock feeds one such block per event and takes the argmax. Each tick is the same computation as
   the row it repeats, so it can be compared with the certified row bit for bit.

At the end the clock appends `<final> X=v </final>`, and the model states the answer in words.

**Certified addition.** For "What is X plus Y?" the model writes a different program:

- the adder as a literal table of 200 rows `c a b c' s`, one per carry c and digit pair (a, b), each meaning
  c + a + b = 10·c' + s;
- where each of the two numbers is in the question, as quoted anchors;
- `<exec/>`.

The clock reads the two numbers and pairs their digits from the right. A missing digit is read as 0, and one more
0 0 pair is added. It then runs one tick per pair. A tick is two forward passes over the cached table:

1. The block `[c][a][b]` gives the new carry c'.
2. The block `[c][a][b][c']` gives the sum digit s.

Every one of the 200 rows is certified first through the same two forwards. The sum is the sum digits read
backwards, so it is exact for numbers of any length once the table is certified.

## How it was made

- **Base model:** [Qwen/Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B), revision `1cfa9a72`.
- **Fine-tuning:** one LoRA adapter (rank 64, alpha 128, on the attention and MLP projections of every layer),
  trained on the base model. It started as PROMPTBOX's final adapter (`rlg-ours/adapter_iter60`: literal-table
  programs and the pinned executor, a language repair, then reinforcement learning). It was then continued for 500
  steps on certified addition (`arith-s1r2/adapter_step500`, branch `arith`), with rehearsal of the families,
  general chat and the base model's own replies.
- **Merge:** the adapter was merged into the bfloat16 base weights.
- **Export:** the merged model was exported to ONNX with the onnxruntime-genai model builder (0.9.0, fp16, the
  WebGPU graph layout: GroupQueryAttention, separate RotaryEmbedding, fp16 KV cache).
  - The LM head is tied to the embedding through a Transpose.
  - The logits are cast to float32.
  - A `num_logits_to_keep` input is added.
- **Quantisation (`q4f16`):** MatMulNBits with block size 32, symmetric. The v and down projections (72
  matrices) are 8-bit, and the q, k, o, gate and up projections (180) are 4-bit. Activations, the embedding and the
  LM head stay in float16. The file keeps the `q4f16` name, so transformers.js loads it with `dtype: 'q4f16'`.
- **Layout:** the layout follows [onnx-community/Qwen3-4B-ONNX](https://huggingface.co/onnx-community/Qwen3-4B-ONNX).
  The graph is `onnx/model_q4f16.onnx`, and its weights are in two external-data chunks of at most 2 GB, listed in
  `config.json`.

`SOURCE.json` lists every file with its sha256, along with the commands, the versions and the machines used.

## Use

```js
import { AutoModelForCausalLM, AutoTokenizer } from '@huggingface/transformers'; // 4.3.1

const id = 'mohsenvand/savant-4b-preview'; // the repository these files are uploaded to
const tokenizer = await AutoTokenizer.from_pretrained(id);
const model = await AutoModelForCausalLM.from_pretrained(id, { dtype: 'q4f16', device: 'webgpu' });
```

- **Decoding.** Decode greedily (`do_sample: false`). `generation_config.json` sets greedy decoding as the default.
- **Prompt format.** The model was trained on prompts of the form
  `<|im_start|>user\n{question}<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n`.
- **The clock.** It is part of the Polyformer page, not of this repository.

## Validation

**Addition.** The table, both forwards and the replays were checked against the format's reference
implementation and fixtures (branch `arith`).

| | bfloat16 merged model (PyTorch, H100) | this model (onnxruntime CUDA, H100) | this model in transformers.js on WebGPU (Apple M4) |
|---|---|---|---|
| adder rows certified, both forwards | 200/200 | 200/200 | 200/200 |
| smallest margin / 1st percentile | 9.38 / 11.50 | 8.53 / 11.23 | 8.58 / 11.17 |
| repeated ticks bitwise equal | 200/200 | 200/200 | 200/200 |
| four recorded runs (10 and 100 digits): carries and sum digits equal | 4/4 (224 ticks) | 4/4 (224 ticks) | 4/4 (224 ticks) |
| the same four questions end to end: program, sum and words right | 4/4 | 4/4 | — |
| time per tick (two forwards over a 1,200-token table) | 67 ms | 17 ms | 310 ms |

**Families and language** (the same checks as r2):

| | bfloat16 | this model |
|---|---|---|
| ten family questions: answers right | 9/10 | 9/10, the same nine |
| ticks bitwise equal to their certified rows | 5,376 of 5,376 | 4,865 of 4,865 |
| twelve more family questions | 9/12 | 10/12 |
| 128 executor tables (PROMPTBOX gate G1 sample) | — | 128/128 accepted, smallest margin 3.70 |
| GSM8K (40): right, programs written | 36, 0 | 37, 0 |
| ordinary questions: right in words, programs written | 7/7, 0 | 7/7, 0 |

## Known limits

- **Experimental preview.** It is not safety-tuned beyond its base model and not evaluated as a chat assistant.
  Outside the question types it was trained on, its answers can be wrong.
- **What the certificate covers.** It shows that the model executes the table it wrote. It does not show that the
  table fits the question, or that the quoted span is the right part of the question.
- **Held-out families.** On question families held out of training, the model can write a wrong table or quote
  anchors that are not in the question. The page then stops before the run.
- **Bitwise equality is per device.** A tick and its certified row are equal bit for bit only on the same device,
  backend and code path. Results can differ between GPUs and browsers, and 4-bit quantisation shifts margins
  slightly from the bfloat16 model.
- **Addition only.** Certified arithmetic covers adding two non-negative whole numbers. Subtraction,
  multiplication, decimals, negative numbers and sums of three or more numbers are answered in words, without a
  certificate.
- **Speed of long sums.** On an Apple M4, a real addition tick takes about 0.3 s in transformers.js. After the first
  few ticks, the page can read certified rows instead of running them (lookup mode); for sums of thousands of
  digits it has to.
- **Long inputs.** A question of a few thousand tokens needs a few GB of GPU memory for its KV cache and attention.
  Pass `num_logits_to_keep: 1` on prefill.

## License

Proprietary. See `LICENSE`. The model is a modified derivative of Qwen3-4B (Apache License 2.0); see `NOTICE` and
`LICENSE-Qwen3`.
