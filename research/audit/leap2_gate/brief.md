# Live prior-art gate: five candidate "new kind of model" directions (29 Oct 2026)

You are a skeptical prior-art auditor with live web search. Today is 29 Oct 2026. Search arXiv, OpenReview, Hugging Face,
GitHub, company blogs (2023 to Oct 2026). For every claim give a link and a date. Do not trust memory; open the pages.

## Context
We have: (1) learned recurrent states that "snap" (contract) onto a finite code set, which makes them exact at long
horizons (S5 / Lean rewrite tracking, 4,096+ steps); (2) a theory that a pinned/contractive learned transition is
history-independent, so enumerating its finite domain once certifies every input of every length (induction);
(3) a learned register-ISA executor run by an external host clock (13 programs, bitwise exact, zero-shot on new
programs); (4) a certified native digit ALU inside base Qwen3-4B. Previous gate (same folder, ../savant_r_gate/out.md)
found "LLM runs its own programs exactly" mostly known: Meridian (Apr 2026, hand-compiled WASM coprocessor + nanochat),
Percepta (transformer computer, Python interpreter), Schuurmans 2023/2024, nCPU, Naughton "Certified Grokking" (Jul 2026).
Already found today: retrofitted recurrence (McLeish et al. arXiv 2511.07384; Shapiro arXiv 2608.11233, rank-16 LoRA loop on
Qwen2.5-0.5B), Relaxed Recursive Transformers (2410.20672), Ouro/LoopLM (2510.25741), "Training-free looped transformers",
"Looped LMs improve compositional tool calling" (2608.18171), Fan et al. looped length generalization (2409.15647),
"Specifying exact circuit algorithms in universal transformers" (NeurIPS 2025). Go beyond these.

## Candidates (judge each)
C1 Crystallized loop. A learned (not hand-constructed) latent loop inside a pretrained LM (native looped base such as
Ouro, or a retrofitted LoRA loop on Qwen) trained so its latent iterations ARE one exact universal executor (small register
ISA or stack VM). Loss: (a) every training step covers the executor's whole finite transition domain with a margin hinge,
(b) a snap/pin term keeps the loop state within delta of a finite codebook (so it is history-independent), (c) KL to the
base on ordinary text. After merging, one finite enumeration certifies exactness for all programs and all lengths. The LM
writes the program into latent registers from a plain prompt (SFT on a generator, then RL); no chain-of-thought tokens,
no host clock. Claim to test: "first learned latent loop in a language model with a finite certificate of exactness for
unbounded inputs".
C2 Programs as weights. The LM emits a low-rank weight delta (composed from a finite certified codebook of instruction
deltas) into its own looped core; executing the program = iterating the rewired core. Neighbours to check: fast-weight
programmers, hypernetworks, Text-to-LoRA, Drag-and-Drop LLMs, TTT layers, Titans, any "LLM writes its own LoRA to compute".
C3 Homomorphism loss. Train state encodings so enc(xy) = enc(x) o enc(y) for a learned associative o, with states snapped
to a finite monoid, so exact state over N steps is computed by parallel prefix in O(log N) depth, certified by checking
generators. Neighbours: Liu et al. 2023 shortcuts to automata, DeltaProduct, negative-eigenvalue linear RNNs, RWKV-7,
bisimulation-metric representation learning, any associativity/homomorphism regulariser.
C4 Compile then dissolve. Compile an exact interpreter into a looped block (ALTA / Tracr style), distil its hidden-state
trajectory into the LM's own looped core through a learned linear map (state alignment, interchange intervention
training), discard the compiled block, certify by enumeration. Neighbours: ALTA trace supervision, Geiger et al. IIT/DAS,
Tracr, Meridian, compiled-weights initialisation or distillation.
C5 Base-model choice. Which open base models (<=4B, browser-feasible) give native affordances for C1 to C4: looped
(Ouro 1.4B/2.6B, Huginn-0125 3.5B, retrofitted checkpoints), matrix-state hybrids (RWKV-7, Gated DeltaNet hybrids,
anything with proven state-tracking). Give HF ids, licence, loop counts usable at test time, known extrapolation behaviour,
and any report of exact multi-digit arithmetic or state tracking inside the latent loop without CoT.

## Specific questions
Q1 Has anyone trained a looped or retrofitted LM to execute programs exactly within latent iterations (no CoT), with
exactness over hundreds or thousands of steps? Best reported numbers.
Q2 Has anyone certified or proven unbounded-length correctness of a TRAINED recurrent/looped network via a finite check
(automata extraction with exactness guarantees, RNN verification, Naughton 2026, others)? What exactly do they prove?
Q3 Is there any "new loss" in 2025-2026 that makes a network's latent loop a finite exact machine (quantised latent
reasoning, discrete latent thoughts, VQ thought tokens, codebook-snapped recurrence)?
Q4 Strongest 2026 demos of latent (no-CoT) reasoning that shocked researchers (HRM, TRM, successors): what do they do,
what are their limits, does any keep a language model intact?

## Output (write to out.md)
Top: a table, one row per candidate: verdict KILLED / NARROW / OPEN, closest work (link, date), what remains open in one
line. Then evidence per candidate, then Q1-Q5 answers, then base-model table. Be blunt. Under 2,500 words.
