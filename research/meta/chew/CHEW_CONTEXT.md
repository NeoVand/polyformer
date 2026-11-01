# Chew: where is the most fruitful direction, with Nature-level publication potential? (1–2 Nov 2026)

**Neo's words (1 Nov):**
- "Let's sleep on this. I think it is worth thinking more and doing more web search. Let's stop one shot direction
  setting. Let's chew on it. Where is the most fruitful direction with great publication potential? A flashy headline
  that can buy us clout and draw attention and Nature would like to publish it."
- Earlier the same day: "Imagine you are the young Chomsky and you have access to LLMs! And you can dissect them and
  try to make a better theory of syntax and semantics ... I'm sure there is crazy prior art to this but none of it has
  been ground breaking."
- "I think there is something interesting about our work on higher order attention and nerode that we haven't found
  yet. Our Feynman and Newton stuff might have legs and are innovative. They might have mistakes in them tho."
- "I'm interested in making models that could not just statistically learn language but also reveal its structure."

**Who Neo is and what he needs.** He is one researcher at the MIT Media Lab, who wants "a few great publications
soon", a startup foundation, and to be credible to the major AI labs. His strengths include LLM fine-tuning (LoRA,
GRPO, on-policy distillation, gating), formal methods (Lean), in-browser ML (WebGPU) and visual design. His standing
judgment criteria are in `research/meta/NEO_CONDITIONS.md` (read it).

**Resources.** Modal GPUs (H100s; hundreds to low thousands of dollars if there is conviction), an Apple M4 with
32 GB, open models (Qwen3.5 0.8B–4B and larger via Modal), API access to frontier models, and weeks, not years. Teams
of one have published in Nature recently: check them (for example Lake & Baroni, Nature 2023, on systematic
generalisation; Binz et al., Nature 2025, "Centaur", a fine-tuned LLM of human cognition). Verify these exist and what
made them publishable.

## What we have (assets and results; details in the files)

- **Sketchpad** (`/Users/neo/repos/sketchpad/paper/paper.md`).
  - Qwen3.5-0.8B with a LoRA computes exactly on a rendered sheet. Each step reads a 3-cell view, so all 2,446 views
    are certified on the device.
  - Lean proofs: exactness on the views implies exactness at all lengths, and no finite test suffices for chain of
    thought.
  - 220/220 pre-registered problems; algebra; a gated chat model.
  - Prior art owns the principle: Lewandowski 2026 and DNAR 2025. Journal odds were judged low (NMI ~5%, Nature
    Communications ~17%).
- **Higher-order attention (October).**
  - Cubic attention solves SET (100% against softmax 57%).
  - The coupling barrier and order-k blindness.
  - Newton attention, exact on Match-k, with the "characters law" (exact iff all 40 characters of Z_3^4).
  - The free-field (Feynman-diagram) formalism: softmax is one particle and subset attention a generating function.
  - Feynman attention (DS-PA): pointer chase with 62k params against softmax's 154k.
  - No gain on language modelling, possibly because of a precision bug; an audit is running
    (`research/meta/survive/AUDIT.md` when done).
- **Nerode work.**
  - The exact state of a trained recurrence is the minimal automaton (960/960 classes) in a ~20-dim affine code.
  - A Nerode metric loss makes recurrences exact.
  - It fails under dilution, probably because it averages over futures instead of quantifying over them.
  - Round 8 (`research/meta/rounds/r8_status.md`): "bind classes, not tokens"; no surviving HIT after the gate.
- **Language-structure direction**: Harris's discovery procedure, executed with an LLM informant. Gate in
  `research/meta/survive/chomsky_gate_report.md`: PARTIAL, the integrated programme OPEN, the most dangerous paper Hu,
  Wilcox, Song, Mahowald & Levy (TACL 2026).
- **Twelve days of history** (`research/meta/META_REPORT.md`): 1,913 commits, more than 25 programmes, about $3k
  spent.
  - At least 15 theorem statements refuted.
  - Many results were "partially known" after the fact: we did too little literature review early.
- **Dead framings** (do not propose a variant without a change of level):
  - long arithmetic for its own sake;
  - GSM8K gains at 0.8B;
  - a universal interpreter;
  - certified CLRS algorithms;
  - higher-order heads as a perplexity gain;
  - matrix-state recurrences against DeltaNet;
  - revisable memory and mixture-of-depths routing;
  - self-predictive state;
  - latent recurrence inside a pretrained model;
  - certified retrieval;
  - the tutor pivot;
  - ARC by scaffolding.

## The bar

A Nature (or Nature Human Behaviour / Nature MI flagship) paper:
- a result of broad scientific interest;
- usually settles a long-standing question, or makes a discovery in a science, or shows a capability with big
  consequences;
- survives hostile review;
- its headline is true.

"Flashy" must still be true and robust. A headline that collapses under review costs more clout than it buys.
