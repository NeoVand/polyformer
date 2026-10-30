You are the prior-art kill gate for one proposed claim. Use live web search (arXiv, OpenReview, Google Scholar, GitHub, company blogs) and report dates. Be hostile: the person paying for this asked "isn't this already known?" and will lose trust if a "new" claim turns out to exist.

THE CLAIM (to test, as worded):
"A pretrained chat model (Qwen3-4B), fine-tuned with a small LoRA adapter and run under one fixed KV-cache policy (keep the program's cache, keep one (state, event) block, evict the rest, restart positions), writes a short register-machine program (program counter, flag, digit-string registers, ~18 opcodes) for a plain-language question and executes it with its own forward passes, exactly at every length, with a machine-checked necessary-and-sufficient per-row certificate (each reachable (state, input) row's argmax margin), whose arithmetic half is the model's own inherited single-digit arithmetic (digit add-with-carry, digit multiply, compare, AND/OR from few-shot micro-prompts) certified exhaustively on the device, while remaining a normal chat model (GSM8K, MMLU, perplexity kept)."

Supporting sub-claims to test separately:
S1. Exhaustive certification of a pretrained LLM's inherited single-digit arithmetic (all 200 add-with-carry cases etc.), used as the instruction set of an exact computer.
S2. An LLM fine-tuned to execute its own self-written register/assembly programs step by step inside its forward passes (not by calling a Python tool), exact at length.
S3. A KV-cache eviction policy that turns a decoder into an exact recurrent executor with a finite certificate (compare StreamingLLM, H2O, TOVA, Delethink/Markovian thinking, RMT/Memformer).
S4. "Judge with the LLM, then aggregate exactly with the same LLM's certified arithmetic."
S5. The whole system as a combination: is the combination itself already published or announced?

Run at least these searches (and any others you need):
1. "register machine" language model "KV cache" exact execution 2026
2. fine-tuned LLM executes its own program "every step" exact certificate attention sink
3. "certified" OR "verified" "instruction set" transformer arithmetic exhaustive margin pretrained
4. pretrained language model digit addition exhaustive certification inherited arithmetic
5. Percepta transformer computer LLM integration 2026; Tzamos transformer interpreter fine-tune
6. CAEF exact arithmetic LoRA LLaMA length generalization 2025 2026
7. Markovian thinking / Delethink chunked reasoning exact state tracking theorem
8. recurrent memory transformer discrete memory tokens exact state certificate (RMT, Memformer, Titans, Infini-attention)
9. "program counter" attention learned exact length generalization interpreter fine-tune LLM 2025 2026
10. language model writes a program and executes it without tools in-context interpreter exact 2026
11. Codified finite-state machines LLM ICLR 2026 and follow-ups
12. neural ALU pretrained LLM lookup table digits certified browser WebGPU 2026
Also check: Lewandowski, Machado, Schuurmans 2026 (universal computation with LLM fresh calls); Schuurmans 2024 "Memory augmented LLMs are computationally universal"; Cai, Shin, Song 2017 (recursion, finite verification); Giannou et al. 2023 looped transformers; Xu et al. 2026 MicroPy; Certified Grokking 2026; LOTUS; Palimpzest; Chain of Code; "learning to execute"; neural program executors on LLMs (e.g. "LLMs as interpreters", "CodeI/O", "execution-trace fine-tuning", "SemCoder", "NExT").

For each sub-claim and the whole: citation with link and date, a short verbatim quote, and a grade: STATES (kills), IMPLIES/PARTIAL (forces rewording; give the surviving wording), CONTEXT (cite only). Then a final verdict on THE CLAIM: KILL / NARROW (give the exact surviving sentence) / PASS, and a separate one-paragraph answer to the plain question "is this already known?" as a skeptical ML researcher would answer it. Write everything to your output; do not edit any files.
