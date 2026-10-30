# Live prior-art gate 3: registers in a delta-rule state, and computation as pictures (29 Oct 2026)

You are a skeptical prior-art auditor with live web search. Today is 29 Oct 2026. Open the pages; link and date every
claim; negative results mean "not located". Previous gate: ../leap2_gate/out.md (read its table first; do not repeat it).

## F. Fable's leap (research/meta/LEAP2.md, section 2)
A hybrid LM whose recurrent layers are delta-rule states (Gated DeltaNet in Qwen3.5 / Qwen3-Next / Kimi Linear, RWKV-7)
holds a register machine IN the state: registers are snapped key directions, a write is the rank-one delta update
S <- S(I - b k k^T) + b v k^T (erase then write), a read is S q. Control stays in attention over a pinned program prefix.
LoRA on the DeltaNet projections only. Certificate: enumerated local rows + a locality lemma (Gram matrix of snapped keys
bounds cross-register interference) + a basin condition F_a(B_q) in B_delta(q,a). Thesis: a decoder is finitely
certifiable iff its view of the past is a finite function of a history-independent state; full-attention transformers
need a host to satisfy this, delta-rule hybrids satisfy it by construction. Search at least: "Gated DeltaNet register
file", "linear attention associative memory interpreter", "Qwen3-Next / Qwen3.5 state tracking exact", "fast weight
programmers instruction set", "delta rule erase write locality bound", "hybrid linear attention program execution without
chain of thought", "certifiable decoder finite state history independence", Schlag 2021, Siems 2026 REPL traces,
Howe 2026, Grazzi 2024, DeltaProduct, Merrill "illusion of state".

## M. Multimodal ideas (Neo: "imagine programs as videos or images, think bold")
M1 The state is a picture. In Qwen3.5-0.8B each Gated DeltaNet head carries a 128x128 matrix state (18 layers x 16
heads). Show that working memory live as images while the model computes; let a user poke (edit) the state and the model
continues from the edited memory; registers appear as rank-one strokes. Prior art on visualising / editing linear-RNN or
fast-weight states as images, "memory editing" of recurrent state, interactive state intervention demos.
M2 Drawn machines. Computation as a video of one learned local rule on a 2D canvas (cellular automaton / Wireworld /
systolic array) inside a multimodal LM: programs are drawings (circuits, systolic multipliers), execution is a video,
certificate = enumerate the rule's finite neighbourhood table, exact for any canvas size and any number of steps. Prior
art: neural cellular automata (Mordvintsev 2020+), NCA for ARC (2025-26), CNNs learning Game of Life (Springer & Kenyon),
LLMs trained on elementary CA ("Intelligence at the edge of chaos"), learned systolic arrays, Wireworld computers,
any LM or VLM with an internal CA executor, certified CA rule learning.
M3 Watch, then run. Show the model a few frames of a process (CA, sorting animation, long division on paper, a cube
being turned); it induces the exact rule and continues it exactly for 10^6 steps, with a certificate once every
neighbourhood has been observed. Prior art: rule induction from video, "video models are zero-shot learners and
reasoners" (Veo 3, 2025), visual planning / thinking with images, ARC video variants, physics rule discovery.
M4 Program as an image input. A program (flowchart, circuit, handwritten algorithm, a register-machine listing as a
picture) is given as an image; the multimodal LM compiles it into its own state and executes it without chain of thought.
Prior art: VLMs reading flowcharts/code screenshots and executing them, visual programming benchmarks.

## Output (write to out.md in this folder)
Top table: one row per item (F, M1-M4): verdict KILLED / NARROW / OPEN, closest work (link, date), what remains open.
Then evidence per item. Then: is anything known about the actual numerics of Qwen3.5's Gated DeltaNet decay (alpha
range, state precision in HF/FLA/transformers.js kernels) that would kill long-horizon register storage? Under 2,000 words.
Be blunt.
