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

# Savant-4B Loom (preview)

Savant-4B Loom (preview) is an experimental research preview made for the Polyformer demo page, beside Savant r3. It
runs in the browser with WebGPU through transformers.js. This is not a general-purpose assistant, and it is not meant
for any use outside that page. These files have not been uploaded.

## What this preview adds

- **Certified addition and subtraction.** For two whole numbers, the model writes a 200-row table and the clock runs
  it with a certificate. Addition is the r3 adder. Subtraction is the same shape: each row is a borrow b, a digit a
  and a digit c, with d − 10·b' = a − c − b.
- **Several calls in one answer.** A question can take more than one `<exec/>`. The clock runs each call, appends
  `<final>…</final>`, and the model continues. Up to eight calls are executed.
- **Lineage.** The adapter is `reason-s1/adapter_step500`, a rank-64 LoRA continued for 500 steps from ARITH's
  `arith-s1r2/adapter_step500` (the adapter in Savant r3).
- **Same pipeline as r3.** The merge is done as the REASON gates were scored. The ONNX export is q4f16: 4-bit, with
  the v and down projections at 8 bits.

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

At the end the clock appends `<final> X=v </final>`, and the model states the answer in words. It may then write
another program. Calls 9–11 are not executed (`too many calls`). A twelfth `<exec/>` appends nothing.

**Certified addition.** For "What is X plus Y?" the model writes:

- the adder as a literal table of 200 rows `c a b c' s`, one per carry c and digit pair (a, b), each meaning
  c + a + b = 10·c' + s;
- where each of the two numbers is in the question, as quoted anchors;
- `<exec/>`.

The clock reads the two numbers and pairs their digits from the right. A missing digit is read as 0, and one more
0 0 pair is added. It then runs one tick per pair. A tick is two forward passes over the cached table:

1. The block `[c][a][b]` gives the new carry c'.
2. The block `[c][a][b][c']` gives the sum digit s.

**Certified subtraction** uses the same two forwards. The row order is borrow, then the two digits, and the second
forward's argmax is the difference digit.

Every one of the 200 rows is certified first through the same two forwards.

## How it was made

- **Base model:** [Qwen/Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B), revision `1cfa9a72`.
- **Fine-tuning:** one LoRA adapter (rank 64, alpha 128, on the attention and MLP projections of every layer),
  trained on the base model. It started as PROMPTBOX's final adapter (`rlg-ours/adapter_iter60`). It was continued
  for 500 steps on certified addition (`arith-s1r2/adapter_step500`, branch `arith`), then for 500 steps on
  multi-call reasoning (`reason-s1/adapter_step500`, branch `reason`, commit `a56b8861`). The reason run's manifest
  initialises from `/arithvol/arith-s1r2/adapter_step500`.
- **Merge:** the adapter was merged into the bfloat16 base weights on the CPU, the way the REASON gates scored it.
  A GPU merge of the same adapter matches all 399 tensors.
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
  `config.json`. The three ONNX files are the same sizes as Savant r3 (59,786,005, 1,999,831,040 and 1,268,776,960
  bytes). The weights differ.

`SOURCE.json` lists every file with its sha256, along with the commands, the versions and the machines used.

## Use

```js
import { AutoModelForCausalLM, AutoTokenizer } from '@huggingface/transformers'; // 4.3.1

// Local folder. Nothing in this directory has been uploaded.
const id = 'savant-4b-loom-preview';
const tokenizer = await AutoTokenizer.from_pretrained(id);
const model = await AutoModelForCausalLM.from_pretrained(id, { dtype: 'q4f16', device: 'webgpu' });
```

- **Decoding.** Decode greedily (`do_sample: false`). `generation_config.json` sets greedy decoding as the default.
- **Prompt format.** The model was trained on prompts of the form
  `<|im_start|>user\n{question}<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n`.
- **The clock.** It is part of the Polyformer page, not of this repository.

## Validation

Numbers are copied from the records named in `research/webexport/REASON_EXPORT.md`. The bfloat16 column is the merged
model on an H100. The q4f16 column is this ONNX file on onnxruntime CUDA, on an H100. The WebGPU column is this file
in transformers.js 4.3.1 on an Apple M4.

| | bfloat16 (H100) | q4f16, onnxruntime CUDA (H100) | q4f16, transformers.js WebGPU (Apple M4) |
|---|---|---|---|
| adder rows certified, both forwards | 200/200 | 200/200 | 200/200 |
| adder smallest margin / 1st percentile | 11.875 / 13.375 | 11.2969 / 12.2031 | 11.3438 / 12.7031 |
| adder repeated ticks bitwise equal | 200/200 | 200/200 | 200/200 |
| subtracter rows certified, both forwards | 200/200 | 200/200 | 200/200 |
| subtracter smallest margin / 1st percentile | 11.875 / 12.75 | 7.625 / 12.0781 | 8.2813 / 12.0938 |
| subtracter repeated ticks bitwise equal | 200/200 | 200/200 | 200/200 |
| four recorded additions: carries and sum digits | 4/4 (224 ticks) | 4/4 (224 ticks) | — |
| the same four questions end to end: sum and words | 4/4 | 4/4 | — |
| time per adder tick (two forwards, 1,200-token table) | 63.63 ms | 16.79 ms | 313.4 ms |

On bfloat16, one of the four addition programs (`test|L10`) is not token-identical to the fixture. Its digit pairs,
final (`s=9119587345`) and words match. On q4f16 all four programs are token-identical.

**Families and language.** r3's counts are in parentheses, from `validate_torch_r3.json` and
`validate_ort_q4mixed_cuda_r3.json`.

| | bfloat16 | q4f16 |
|---|---|---|
| ten family questions: answers right | 9/10 (r3 9/10) | 8/10 (r3 9/10) |
| ticks bitwise equal to their certified rows | 6,272 of 6,272 | 5,760 of 5,760 |
| twelve more family questions | 8/12 (r3 9/12) | 8/12 (r3 10/12) |
| G1 sample, seed 777, first 64 held-out tables | — | 64/64 accepted, 5,694/5,694 rows, smallest per-table margin 3.9375 |
| GSM8K (40): right, programs written | 37, 0 (r3 36, 0) | 35, 0 (r3 37, 0) |
| ordinary questions: right in words, programs written | 7/7, 0 | 7/7, 0 |

Clock fails on both, as it did on r3. q4f16 also fails elevator: the table matches and the tape anchors do not, so
the clock does not run. Both fail `compass-heldout-128` (r3 passed it) and `prose-heldout-128` (r3's q4f16 passed
it). `parity-heldout-128` is certified and bitwise, and the answer is wrong, as on r3. The G1 sample is the same 64
tables as the prefix of r3's 128, with the same row counts. r3's smallest per-table margin on those 64 is 3.9531.
Every table is still accepted.

**Replay and generation.** Fed the four fixture transcripts, q4f16 and bfloat16 both reproduce all 8 calls (spans,
finals, values, errors) and locate 6/6. End-to-end generation on the 24 first-of-cell R1 problems is in the export
report. q4f16 agrees with the recorded correct/wrong verdict on 19/24. bfloat16 finished 14/24 and agrees on 13/14.

## Known limits

- **Experimental preview.** It is not safety-tuned beyond its base model and not evaluated as a chat assistant.
  Outside the question types it was trained on, its answers can be wrong.
- **What the certificate covers.** It shows that the model executes the table it wrote. It does not show that the
  table fits the question, or that the quoted span is the right part of the question.
- **Held-out families.** On question families held out of training, the model can write a wrong table or quote
  anchors that are not in the question. The page then stops before the run. This preview loses `compass-heldout-128`
  relative to r3, and q4f16 also loses elevator and `prose-heldout-128`.
- **Bitwise equality is per device.** A tick and its certified row are equal bit for bit only on the same device,
  backend and code path. Results can differ between GPUs and browsers, and 4-bit quantisation shifts margins
  slightly from the bfloat16 model.
- **Two whole numbers.** Certified arithmetic covers adding or subtracting two non-negative whole numbers.
  Multiplication, decimals, negative numbers and sums of three or more numbers are answered in words, without a
  certificate, unless the model breaks them into certified calls.
- **How many calls.** Eight calls are executed. Calls 9–11 receive `too many calls` and are not run.
- **Speed of long sums.** On an Apple M4, a real addition tick takes about 0.3 s in transformers.js. After the first
  few ticks, the page can read certified rows instead of running them (lookup mode); for sums of thousands of
  digits it has to.
- **Long inputs.** A question of a few thousand tokens needs a few GB of GPU memory for its KV cache and attention.
  Pass `num_logits_to_keep: 1` on prefill.
- **Greedy decoding differs across stacks.** The recorded REASON transcripts are vLLM greedy on bfloat16. This
  export's end-to-end runs are Hugging Face greedy. q4f16 also moves some programs. The export report lists every
  disagreement.

## License

Proprietary. See `LICENSE`. The model is a modified derivative of Qwen3-4B (Apache License 2.0); see `NOTICE` and
`LICENSE-Qwen3`.
