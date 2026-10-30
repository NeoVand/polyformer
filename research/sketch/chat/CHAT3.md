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

(pending)

## Spend

| job | what | cost |
|---|---|---|

## Glossary candidates

- Gate (hard LoRA gate): a 0/1 graph input multiplying every adapter branch; ours (SKETCHPAD3 T5, 30 Oct 2026); gate 0
  is the base model exactly, so the language half is untouched whenever the sheet is off.
