# CHAT brief: the gate and the chat fine-tune (T5, T4)

Read first: `research/meta/sketchpad3/CONTRACT.md` (rules, seam 3, your files), then `research/meta/SKETCHPAD3.md` §1
(the compile baseline), §4 and §6 items 5–6. Worktree: `/Users/neo/repos/polyformer-wt/chat`, branch `chat`. Log:
`research/sketch/chat/CHAT3.md`. Your own Modal app `polyformer-chat` (copy the pattern of `research/sketch/modal/`; you
may mount the `polyformer-sketch` volume read-only for adapters and write to your own volume). Modal spend cap: **$25**.

## Background in four lines

Qwen3.5-0.8B plus one LoRA (r16, alpha 32, language layers) does certified arithmetic on a rendered sheet (E6 seed 3,
on the `polyformer-sketch` volume; the CALC stream is training E7 with subtraction and division tables). Measured on
30 Oct (`research/sketch/compile_baseline.py`, 60 problems per task): the adapter wrecks instruction-following (word
problem → expression 44/60 stock, 1/60 with E6), though plain-text perplexity moved only ×1.007. The page's chat runs
on those weights today. Goal: one model that chats like stock Qwen and opens its sheet by itself when a problem needs it.

## T5 first: the gate ($0–2, a day at most)

- `research/sketch/patch_onnx_lora.py` injects the LoRA branches into the base fp16 decoder graph. Add one graph input,
  `lora_gate` (float16, shape [1]), that multiplies every LoRA branch's output before it is added back.
- Verify on Modal (ONNX Runtime, the same graph files the page uses; build them with `patch_onnx_lora.py` and
  `patch_onnx_inside.py` as `research/sketch/build_program.sh` does): gate 0 against the stock graph (the base decoder
  with the same inside patch, no LoRA) on 100 chat prompts: logits bit-identical, or if ONNX Runtime's fusions break bit
  identity, report the largest difference and require identical greedy outputs; gate 1 against today's graph: the same
  logits, so the certificate is unchanged.
- Commit the patch and the test, and write in `CHAT3.md` the exact input name, dtype and shape, so the orchestrator can
  wire the page (the worker feeds the gate; chat at 0 until T4 passes; sheet steps at 1). You do not edit `src/`.

## T4: the chat fine-tune ($5–10 for the final run; pilots ≤ $5 in all)

**Data (synthetic, about 3,000 dialogues).** The work-order format is CONTRACT seam 3: a ```` ```sheet ```` block, then
the runtime's `= …` line (masked from the loss), then the model goes on using that value. Mix:
- problems that need the sheet: arithmetic with multi-digit numbers, decimals, percent and money, division to k places,
  √, gcd; equations (`solve`), expansions, factoring, 2×2 systems; problems inside prose and word problems;
- about 30% distractors that must not open it: chit-chat, facts, writing, code, and single-digit mental arithmetic;
- held-out templates for every family (never trained), which the evaluation uses.
Answers inside a sheet line must be the translation only; the value always comes from the `= …` line. Keep a flag for
the older format (one binary operation per line, `t1 = a op b`, CONTRACT seam 3) without training on it.

**Loss.** Cross-entropy on the model's turns; replay of every sheet table row (all must stay certified); and
self-distillation (Learning without Forgetting): a KL term toward stock Qwen's own token distribution on instruction
prompts (teacher = the same model with the adapter disabled). Prompts: public instruction sets on the Hugging Face hub
(for example `HuggingFaceH4/no_robots`, the `google/IFEval` prompts held out for evaluation only). Start from E6 for
pilots; the final run starts from CALC's E7 when it exists on the `polyformer-sketch` volume (`research/sketch/CALC3.md`
names it); if E7 is not ready when your pipeline is, ask the orchestrator rather than waiting silently.

**Registered (write these into `CHAT3.md` before the final run, with your own predictions next to them).** Against stock
few-shot on the same held-out templates (measure that baseline first, it is cheap):
- opening the sheet: precision and recall each ≥ 0.95;
- word problems → a correct sheet line on held-out templates ≥ 0.9 (stock: 0.73 on the old format);
- equations copied into a correct `solve` line ≥ 0.95; numeric expressions from mixed text ≥ 0.95;
- instruction-following (IFEval-style, strict prompt-level accuracy) within 2 points of stock.
Kill: any table row lost, plain-text perplexity above ×1.03 of stock, or instruction-following more than 5 points below
stock. Report also, without a prediction: GSM8K (a 250-problem subset) stock versus the model with the sheet (run the
blocks with a Python stand-in for the exact sheet, said as such), and MMLU (a 500-question subset) stock versus gate 1.

## Done

The gate patch with its identity test; the E8 adapter on your volume (path in `CHAT3.md`) with its evaluation table
against the registration; committed on `chat`; and the final report (what passed, what failed, numbers, spend). The
orchestrator builds the program folder and wires the page.
