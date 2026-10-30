# Live prior-art gate 4: a visuospatial sketchpad for a language model (29 Oct 2026)

Skeptical auditor with live web search; today is 29 Oct 2026. Open pages; link and date everything; "not located" is
not "absent". Earlier gates in ../leap2_gate and ../leap3_gate (read their tables; do not repeat them).

## Thesis to audit
Neo: "my brain thinks in pictures and uses some kind of visuospatial sketchpad when I do calculations or think about
algebra." Proposed direction ("grown, not built"): a pretrained vision-language model (target Qwen3.5-0.8B/2B, native
image+video, runs in the browser) is trained to keep its working memory as a 2D canvas that it OVERWRITES each step
(constant-size Markov state, not an appended chain of images or text) and re-reads with its own vision encoder, or keeps
as a latent grid snapped to a glyph codebook. Claims to test:
S1 Rendering is restoration: writing the canvas as discrete glyphs/cells each step is the nonaffine "snap" that
   finite-precision exact state tracking needs (Brandoit et al. 2609.32447); exactness then reduces to a finite check of
   the reader on cell patterns.
S2 Locality gives size generalisation: a local, translation-equivariant canvas update learned once (column addition,
   long multiplication grid, mental abacus) is correct on any canvas size and any number of steps, certified by
   enumerating the finite neighbourhood table.
S3 Optical compression (DeepSeek-OCR, Glyph): vision tokens are a denser working memory than text tokens; there is a
   measurable capacity trade-off between tokens per cell and exact-decode margin.
S4 Physics link: the same canvas machinery is a world model; integer lattice-gas style rules give EXACT conservation
   laws; one next-canvas objective trains arithmetic, algorithms and physics.
S5 Demos: mental abacus / long multiplication drawn live; a ball or fluid "imagined" frame by frame with exact
   conservation; poke the sketchpad mid-computation; photo of a handwritten sum -> sketchpad -> exact answer.

## Search at least
Visual Sketchpad (Hu et al. 2024); Multimodal Visualization-of-Thought MVoT (2025); Latent Sketchpad (2025); Mirage /
machine mental imagery (2025); Visual planning "think only with images" (2025); Thinking with generated images (2025);
"thinking with images" surveys 2025-26; DeepSeek-OCR (Oct 2025) and any DeepSeek-OCR 2 / follow-ups; Glyph (Zhipu 2025);
"text as pixels" / PIXEL / pixel language models; vision-centric token compression; Neural GPU (Kaiser & Sutskever 2016),
Extended Neural GPU; neural cellular automata for arithmetic; VLM arithmetic on rendered digits / "visual arithmetic";
mental abacus in AI and cognitive science (Frank & Barner 2012); 2D/abacus positional embeddings for arithmetic length
generalisation; video world models as reasoners (Veo 3 zero-shot reasoners, Genie 3, V-JEPA 2, Cosmos); learned
simulators with exact conservation (lattice gas, conservative neural PDE solvers); any 2026 "visual working memory" or
"canvas" architecture for LLMs; any certified/exact visual reasoning.

## Questions
Q1 For S1-S5, verdict KILLED / NARROW / OPEN with the closest work (link, date) and what remains open.
Q2 What exactly does DeepSeek-OCR (and successors) report: compression ratios vs precision, tokens per page, the
   "optical forgetting" idea; any use of optical context as working memory for reasoning rather than for documents?
Q3 Strongest 2025-26 results where a model reasons by drawing or imagining images: tasks, accuracy, model size, whether
   the image is overwritten (Markov) or appended, whether anything is exact or length-generalising.
Q4 Has anyone combined a pretrained VLM with an internal 2D canvas for exact arithmetic at hundreds of digits, or with
   certified local rules? Has anyone shown a learned world model with exact conservation laws?
Q5 Which open small VLMs (<=4B) run in the browser (transformers.js / WebGPU / ONNX) with image input, and at what
   per-image token cost and latency, as of Oct 2026?

## Output
Write out.md: top table (S1-S5 verdicts), then Q1-Q5 evidence. Under 2,500 words. Blunt.
