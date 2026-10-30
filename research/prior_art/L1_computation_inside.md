# L1. Computation and program execution inside neural networks and LLMs

Prior-art map for claims C1–C10, area L1. Compiled 28 October 2026.

**How entries were verified.**
- **arXiv.** 146 arXiv records came from the arXiv API (`export.arxiv.org/api/query`, run on 2026-10-28). That gives the title, the full author list, the first-version date, the latest version, the author comment and the journal reference. The raw records are in `research/prior_art/L1_verified_records.json`.
- **Venues.** These come from the arXiv comment, the journal reference, or a Semantic Scholar batch lookup run on the same day. Where only Semantic Scholar names the venue, the entry says so.
- **Non-arXiv sources** were fetched directly on the same day:
  - Percepta's three posts, read from the site's JavaScript bundles because the pages render client-side;
  - Papailiopoulos's Substack post;
  - the TMLR BibTeX page and the ICML 2025 workshop page for ET-CoT;
  - Crossref for the DNC;
  - the Hugging Face model API for `percepta-ai/spotlight-vm` and `NJUDeepEngine/CAEF_llama3.1_8b`.
- **Deep reads.** For these 13 sources, methods and results were read beyond the abstract:
  - Lewandowski et al. 2026; Cai et al. 2017; CAEF; all three Percepta posts; MAKER; PENCIL;
  - Qiu et al.; Neural Comprehension; TAIL; Fixed Universal Transformers; the FSM-execution benchmark;
  - ALTA's learnability section; Papailiopoulos's SUBLEQ post.

  Everything else rests on the abstract as fetched.

**Closeness scale.**
- 0: background only.
- 1: same area, different question.
- 2: overlaps a component of a claim.
- 3: pre-empts part of a claim as currently worded.

Already-known items (Schuurmans 2023 and 2024; Percepta, March 2026) are not re-reported. **Section 2.0 updates both**: each has a 2026 follow-up that matters more than the original.

---

## 1. The five most dangerous papers

### 1.1 Lewandowski, Machado & Schuurmans, "Universal computation is intrinsic to language model decoding" (arXiv 2601.08061, January 2026)

This is the 2026 sequel to Schuurmans, Dai & Zanini 2024.

**What they did.**
- They simulate the universal Turing machine U(15,2) as a Lag system with 1,857 production rules over 249 symbols.
- A system prompt for Llama-4-17B-128E-Instruct was found by automated trial-and-error search, with feedback on the rules that failed.
- Under greedy decoding the model then executes all 1,857 rules correctly.
- The correctness argument is an induction:
  - every step is a fresh call made of the system prompt plus the current two-symbol window of the operational string;
  - so the 1,857 single-rule checks cover every input the harness can ever produce;
  - so the run is exact for unbounded computation.
- The earlier Gemini result is now unverifiable because that model was deprecated.
- They also show that frozen, randomly initialised networks are universal once an encoder and decoder (a codebook) are learned.
- The paper does not discuss positional encoding, the KV cache, or what happens if history stays in context.

**What overlaps.**
- **C5, the sufficiency half of Theorem P, almost exactly.** A finite per-rule check, plus a harness that bounds what the model sees at each step, gives exactness at any length. Their fresh-call harness is a pinned clock in our sense.
- **C10(b): a universal machine certified once inside an LLM.** This is done: rule by rule, on an open-weights model.
- **C6's framing that the LLM itself is the computer, with no tool.**

**What does not overlap.**
1. The **necessity** direction of Theorem P.
2. The **negative theorem** that no finite test certifies unpinned decoding. They never test history-in-context, and their argument silently depends on its absence.
3. **The clock as a KV-cache policy inside one decoding run**: a chunk-aligned attention sink, Π cached, blocks evicted, positions restarted. Their harness is an external loop of separate calls.
4. **The model writing its own program** from a plain question (C6).
5. **Practical speed.** One U(15,2) step costs many Lag rewrites. A table program costs one block per event.
6. **Fine-tuning and mechanism** (C4, C7).
7. **Lean.**

**Rewording.**
- **C5:** "Theorem P gives the necessary and sufficient condition under which a per-row check certifies decoding at every length. The rule-by-rule argument of Schuurmans et al. (2024; Lewandowski et al. 2026) is its sufficiency direction for a fresh-call harness. We show the harness can be a cache policy inside one run, and prove (in Lean) that without pinning no finite test certifies."
- **C10(b):** "certified once" is not new in principle. Claim instead a *register-machine* interpreter at useful speed, inside a fine-tuned chat LLM, running programs the model writes, and certified under the pinned clock.

**Tests it suggests (cheap, local, $0 of Modal).**
- (a) Port their U(15,2) Lag rules into our harness. Certify all 1,857 rows on Savant under the pinned clock.
- (b) Run the same rules with history kept in context, unpinned. If it fails at length while every rule passes in isolation, that demonstrates `no_finite_test_suite` on their own construction. That is the cleanest possible figure for the theorem pair.
- (c) Report steps per useful operation for Lag-U(15,2) against our table programs, for example 4,096-digit addition.

### 1.2 Cai, Shin & Song, "Making Neural Programming Architectures Generalize via Recursion" (ICLR 2017; arXiv 1704.06611)

**What they did.**
- They train a recursive Neural Programmer-Interpreter (NPI) on recursive execution traces for grade-school addition, bubble sort, topological sort and quicksort.
- They then prove "perfect generalization" (correct on inputs of any length) by verification. The theorem is ∀i∈V, M(i)⇓P(i), where V is the set of step-input sequences within one call, built from the reference program's observation-to-observation map.
- Recursion makes V finite: each call runs a fixed number of steps however long the input.
- They argue explicitly that the non-recursive version, whose LSTM state persists across arbitrarily many sub-calls, cannot be certified without evaluating it at that length.
- All four learned programs passed their verification sets.
- **Limitations they state:** strong recursive-trace supervision, and infeasibility for huge input domains.

**What overlaps.**
- **C5's whole logical skeleton.** Bound what the network sees per step, and a finite check covering every reachable step input certifies every length. Leave the state unbounded, and no finite check suffices. Their recursion boundary plays the role of our block eviction and position restart. Their remark about the non-recursive LSTM is the informal ancestor of `no_finite_test_suite`.

**What does not overlap.**
- They use an NPI with environment observations, not a transformer LLM. There is no KV cache, attention or positions.
- The non-recursive impossibility is a remark, not a theorem.
- There is no necessity theorem, no proof assistant, and the programs are not written by the model.

**Rewording.**
- Cite as the origin of verification-based perfect generalization for neural programs.
- Describe Theorem P as the transformer, KV-cache analogue with both directions proved.
- **Never write "first certificate of exactness at any length for a neural executor".**

**Test.** This is a framing change, not a test. Map our row set to their V explicitly in the Methods: one block is one "call", and position restart is what keeps V finite.

### 1.3 Lai, Xu, Yang, Huang, Cao & Xu, "Executing Arithmetic: Fine-Tuning Large Language Models as Turing Machines" (CAEF; arXiv 2410.07896, 2024)

**What they did.**
- LLaMA-3.1-8B (base) with LoRA adapters (r = 8) learns one-step Turing-machine transitions: input ⟨state, command⟩, output the next ⟨state, command⟩, in a textual tape format with right-to-left digits.
- Each step's input is only the current representation. The executor is Markovian, and the whole tape is re-emitted every step.
- An "aligner" adapter translates expressions in and out. "Executor composers" call other executors: multiplication calls addition and less-than.
- **Exactness of a whole run:**
  - addition executor 100.0/100.0/99.9/99.6% at 5/10/50/100 digits;
  - end-to-end addition 98.6% at 100 digits (GPT-4o 43.0%);
  - multiplication and division 99.3% on 1–10 digits.
- **Stated limitations:**
  - errors on repeated-digit patterns ("999…", "456456…");
  - slowness, because "the KV cache from the previous step cannot be effectively reused" when the input shifts. They wish for a RAM-like cache;
  - the per-operator Turing machines are hand-designed.
- Checkpoint public: `NJUDeepEngine/CAEF_llama3.1_8b` on Hugging Face.

**What overlaps.**
- **C6:** an LLM that runs state-machine programs for arithmetic step by step in its own forward passes, with no tool.
- **C5:** a per-step Markov context, the pinned clock without the name.
- **C10:** composition by calls.

**What does not overlap.**
- The Turing machines are written by humans, with one adapter per operator.
- It is not exact: 98–99.6% at 100 digits against Savant's exact 4,096 digits.
- There is no certificate.
- The whole tape is re-emitted each step. Ours keeps Π cached and evicts only the (state, event) block, which is exactly the "RAM-like KV cache" they ask for.
- No language-retention test, and the model does not write programs from plain questions.

**Rewording.**
- C6 must not say or imply "first LLM that executes arithmetic as a state machine in its own forward passes".
- The distinctive claim is the conjunction: one fine-tune that (i) writes the table program from a plain question, (ii) certifies every row, and (iii) runs it under a cache policy that makes the certificate sufficient. Exact to 4,096 digits, language kept.

**Baseline and test.**
- Run the CAEF checkpoint against our addition sweep (100 → 4,096 digits) and on adversarial repeated-digit inputs.
- Run Savant on the same repeated-digit inputs: their failure mode is a natural stress test of C8.
- Try certifying CAEF's executor rows under our harness, to show that the certificate, not the format, is the difference.

### 1.4 Percepta (Tzamos et al.), three posts: "Can LLMs Be Computers?" (11 March 2026), "Constructing an LLM-Computer" (25 March 2026), "Can LLMs Grow Their Own Capabilities?" / "Spotlight Memory" (2 October 2026)

Pages: https://www.percepta.ai/blog/can-llms-be-computers ; https://www.percepta.ai/blog (index) ; model https://huggingface.co/percepta-ai/spotlight-vm (created 2026-09-29, Apache-2.0).

**The March posts.**
- **The model.** A standard 7-layer PyTorch transformer, d_model 36, 18 heads of dimension 2, gated feed-forward, hard-max attention.
- **The interpreter.** Its weights are compiled analytically, not trained, into a WebAssembly interpreter. The pipeline is the CALM language, then a gate graph, then MILP scheduling, then weights. C programs compiled to WASM are fed as a prompt and executed as an append-only trace.
- **Speed.**
  - A convex-hull "HullKVCache" makes each lookup O(log t), giving more than 30k tokens/s on a CPU.
  - The hardest-known Sudoku (Arto Inkala's) is solved in under three minutes.
- **Guarantee.**
  - By construction, "the next execution token is always scored higher than everything else", that is, a margin.
  - If the compiled solver is correct, so is the run.
- **Mechanisms.**
  - The instruction pointer and stack depth are exact cumulative sums: uniform attention times position.
  - Programs can be partially evaluated into feed-forward weights.
- **Demo.** The construction runs in the browser.
- **Stated next steps:**
  - combine with an LLM and train it to invoke the execution path;
  - "Formally verifying the logic a transformer implements";
  - a formal write-up. **Not found** on arXiv or the web as of 2026-10-28.

**The October post.**
- A new architecture, Spotlight, with growing, sparsely addressed memory.
- A *hand-constructed* MicroPython v1.28.0 interpreter in that memory runs real Python, including packages, classes, generators and recursion 2,000 calls deep.
- It runs at 134k–144k tokens/s with constant work per step, on traces from 6.5M to 47.6M tokens.
- New packages can be written into memory at run time.

**What overlaps.**
- **C6's headline vocabulary** ("executes the program itself… within the same transformer", "no external tool", browser).
- **C10(b): a universal interpreter in weights.**
- **C10(c):** their instruction pointer *is* a certified-by-construction index increment.
- **C5's per-step margin guarantee**, by construction rather than by certificate.

**What does not overlap.**
- Nothing is learned.
- It is not a language model: no chat, no language retention.
- The model does not write its own programs.
- There is no certificate of a *trained* network and no Lean. Their "verification" is still future work.

**Race risk.**
- They have publicly stated LLM integration and formal verification as next steps.
- Their October model is public on Hugging Face as a text-generation model with custom code. The widget prompts there are Hugging Face defaults, not evidence of chat ability.

**Rewording.**
- Do not use "computer inside a transformer" or "runs programs in its own forward passes" as if new.
- Say: "inside a *pretrained chat LLM*, learned by fine-tuning, with a certificate of the *trained* weights".
- Cite Percepta's cumulative-sum pointer when C10(c) is built.
- Drop "runs in a browser" as a distinguishing point.

**Test.**
- Run 4,096-digit addition (and one Sudoku, if cheap) on `percepta-ai/spotlight-vm` and on Savant. Report exactness and the cost per step.
- Present Savant's per-row margin certificate as the *learned* counterpart of their *constructed* margin guarantee.

### 1.5 Meyerson et al., "Solving a Million-Step LLM Task with Zero Errors" (MAKER; arXiv 2511.09030, Nov 2025), with Yang, Srebro, McAllester & Li, "PENCIL" (ICML 2025; arXiv 2503.14337)

**MAKER.**
- **Task.** 20-disk Towers of Hanoi: 2²⁰−1 = 1,048,575 dependent moves, solved with zero errors by gpt-4.1-mini.
- **Context per step.** Each micro-agent sees only the current configuration and the previous move. The move strategy is given in the prompt.
- **Error correction.** First-to-ahead-by-k voting (k = 3), plus "red-flagging" that discards over-long or malformed replies.
- **Measured per-step error rates:**
  - gpt-4.1-mini, 0.22–0.40%;
  - Qwen-3, 23%;
  - Llama-3.2-3B, 100%.
- **Theory.** Assuming i.i.d. errors, the required k grows as ln s and the expected cost as s ln s.
- **Cost.** Projected run costs are about $3.5k–$4.9k on gpt-4.1-mini.

**PENCIL.**
- A learned reduction rule, C [CALL] T [SEP] A [RETURN] ⇒ C A, erases finished thoughts. The KV cache is recomputed after each reduction.
- A theorem gives Turing-machine simulation with O(T) tokens and O(S) context, for a fixed finite transformer with average-hard attention.
- **Empirical results.** 10–25M-parameter models trained from scratch:
  - 100% on SAT and QBF up to n = 10;
  - 97% on 5×5 Einstein puzzles.
- No pretrained LLM is involved, and nothing is certified.

**What overlaps.**
- **C5:** keep the context bounded and evict finished blocks, and long exact runs become possible. MAKER is the empirical twin of the pinned clock with a pretrained LLM and no fine-tuning.
- **C6's "exact at extreme length".**
- **C8:** MAKER measures the per-step error rate.
- The wider family is relevant too: InftyThink, the Markovian Thinker (already in LITERATURE.md), Markov chain of thought, and register tokens in diffusion LMs.

**What does not overlap.**
- MAKER's exactness is *probabilistic*: voting under an i.i.d. assumption, an external orchestrator, and thousands of dollars.
- Ours is *deterministic*: one pass per step, certified rows, and a theorem.
- PENCIL has no LLM and no certificate.

**Rewording.** For C5, the novelty is not "evict and restart". It is "under this eviction policy a finite certificate replaces voting: every step is provably right, and one sample per step suffices".

**Test (strong, cheap).**
- Run Hanoi-20 as a table program on Savant under the pinned clock: 1,048,575 steps, one greedy pass each, certificate shown.
- Report wall-clock and dollar cost against MAKER's.
- Optionally run unpinned decoding with MAKER-style voting as a baseline arm.

---

## 2. Annotated list

Format:
- **Citation.** URL (verified 2026-10-28).
- **What they did.**
- **Closeness** (0–3) → claim.
- **Implication for us.**

### 2.0 Updates to items already known

1. **Schuurmans, Dai & Zanini, "Autoregressive Large Language Models are Computationally Universal" (arXiv 2410.03170, 2024).** https://arxiv.org/abs/2410.03170 (still v1).
   - **Update.** The Gemini model it used is deprecated, so the result can no longer be reproduced (stated in the 2026 sequel).
   - **Sequel.** Lewandowski et al. 2026 (§1.1) re-establishes the result on Llama-4 with an explicit induction argument.
   - **Closeness.** 3 → C5 (sufficiency), C10(b). Cite the 2026 paper as the reproducible version.

2. **Percepta (Tzamos et al.), March 2026.**
   - **Updates:**
     - the 25 March post, "Constructing an LLM-Computer", documents the compiler and the margin guarantee;
     - the 2 October posts and `percepta-ai/spotlight-vm` move to a hand-built MicroPython interpreter in a growing-memory architecture;
     - a formal write-up was promised but not found.
   - **Closeness.** 3 → C6 vocabulary, C10(b,c). See §1.4.

3. **Lewandowski, Alex; Machado, Marlos C.; Schuurmans, Dale. "Universal computation is intrinsic to language model decoding." arXiv 2601.08061 (Jan 2026; v2).** https://arxiv.org/abs/2601.08061 — see §1.1.
   - **Closeness.** 3 → C5, C10(b).

### 2.1 Universality and expressivity of transformers and LLMs

4. **Pérez, Marinković, Barceló. "On the Turing Completeness of Modern Neural Network Architectures." ICLR 2019; arXiv 1901.03429.** https://arxiv.org/abs/1901.03429
   - **What they did.** Transformers and the Neural GPU are Turing complete under arbitrary precision and hard attention. Already in LITERATURE.md.
   - **Closeness.** 0 → C10.
   - **Implication.** Expressivity is not our claim. Cite once.

5. **Wei, Chen, Ma. "Statistically Meaningful Approximation: a Case Study on Approximating Turing Machines with Transformers." arXiv 2107.13163 (2021); NeurIPS per Semantic Scholar.** https://arxiv.org/abs/2107.13163
   - **What they did.** They require approximating networks to be *learnable* with sample complexity polynomial in machine size, and show transformers SM-approximate Turing machines with bounded computation time.
   - **Closeness.** 1 → C1, C6.
   - **Implication.** A theory precedent for "representable is not learned". It supports C1's motivation and does not touch the blindness mechanism.

6. **Giannou, Rajput, Sohn, Lee, Lee, Papailiopoulos. "Looped Transformers as Programmable Computers." arXiv 2301.13196; ICML 2023 per Semantic Scholar.** https://arxiv.org/abs/2301.13196
   - **What they did.** A hand-set looped transformer emulates a one-instruction (SUBLEQ) computer with program counters, branches and function calls. The input is a "punchcard".
   - **Closeness.** 2 → C10(b,c).
   - **Implication.** It is the canonical constructed program counter. C10(c)'s "certified index increment" should cite it and Percepta.

7. **Qiu, Xu, Bao, Tong. "Ask, and it shall be given: On the Turing completeness of prompting." ICLR 2025; arXiv 2411.01992.** https://arxiv.org/abs/2411.01992
   - **What they did.**
     - One fixed, hand-constructed transformer (hardmax, log precision) computes any computable function given a function-specific finite prompt.
     - The prompt encodes a two-tape Post–Turing machine (2-PTM); the run takes O(t log t) chain-of-thought steps.
     - No pretrained LLM, and no guidance on finding or checking prompts. (Deep-read.)
   - **Closeness.** 2 → C10(b).
   - **Implication.** "Fixed interpreter plus program-as-prompt" is a theorem already. Our C10(b) has to be about a *trained LLM*, *certified*, at useful speed.

8. **Li, Qian; Wang, Yuyi. "Constant Bit-size Transformers Are Turing Complete." NeurIPS 2025; arXiv 2506.12027.** https://arxiv.org/abs/2506.12027
   - **What they did.** Constant-precision transformers simulate any Turing machine given a long enough window, via Post (queue) machines. SPACE[s(n)] exactly characterises what a window of length s(n) computes.
   - **Closeness.** 1 → C5, C10.
   - **Implication.** Queue-based simulation mirrors the Lag-system harness. Useful theory for why bounded windows suffice when the *data structure* moves the pointer.

9. **Li, Qian; Wang, Yuyi. "Efficient Turing Machine Simulation with Transformers." arXiv 2512.00003 (v1 Sep 2025); ICLR 2026 per mlanthology.** https://arxiv.org/abs/2512.00003
   - **What they did.** Optimal O(s(n)) context with only O(s(n)^c) chain-of-thought steps per simulated step, using multi-queue machines and sparse geometric-offset attention.
   - **Closeness.** 1 → C10(c).
   - **Implication.** Theory for cheap pointer movement; cite if C10(c) claims efficiency.

10. **Merrill, Sabharwal. "The Expressive Power of Transformers with Chain of Thought." ICLR 2024 (arXiv comment); arXiv 2310.07923.** https://arxiv.org/abs/2310.07923
    - **What they did.** Chain of thought of linear length lifts transformers to recognise regular languages; polynomial length gives P. Already in refs.bib.
    - **Closeness.** 0 → C5.
    - **Implication.** Background.

11. **Li, Liu, Zhou, Ma. "Chain of Thought Empowers Transformers to Solve Inherently Serial Problems." ICLR 2024; arXiv 2402.12875.** https://arxiv.org/abs/2402.12875
    - **What they did.** Constant-precision transformers with T chain-of-thought steps compute size-T circuits.
    - **Closeness.** 0.
    - **Implication.** Background for "each block is one step".

12. **Feng, Zhang, Gu, Ye, He, Wang. "Towards Revealing the Mystery behind Chain of Thought: A Theoretical Perspective." NeurIPS 2023 (oral); arXiv 2305.15408.** https://arxiv.org/abs/2305.15408
    - **What they did.** Arithmetic and dynamic programming need chain of thought for bounded-depth transformers.
    - **Closeness.** 0.
    - **Implication.** Background.

13. **Malach. "Auto-Regressive Next-Token Predictors are Universal Learners." arXiv 2309.06979; ICML per Semantic Scholar.** https://arxiv.org/abs/2309.06979
    - **What they did.** Even linear next-token predictors trained on chain-of-thought data approximate any Turing-computable function. Introduces "length complexity".
    - **Closeness.** 1 → C1.
    - **Implication.** "Training on traces suffices in principle" is the optimistic view C1 qualifies (exactness at length).

14. **Wiedermann, van Leeuwen. "Large Language Models and the Extended Church-Turing Thesis." EPTCS 407 (NCMA 2024), 198–213; arXiv 2409.06978.** https://arxiv.org/abs/2409.06978
    - **What they did.** A fixed LLM is a (huge) finite-state transducer, and lineages of evolving LLMs are interactive Turing machines with advice.
    - **Closeness.** 1 → C5.
    - **Implication.** "A fixed LLM with bounded context is a finite-state transducer" is exactly why the pinned clock makes a finite certificate possible. Cite as framing.

15. **Saunshi, Dikkala, Li, Kumar, Reddi. "Reasoning with Latent Thoughts: On the Power of Looped Transformers." ICLR 2025; arXiv 2502.17416.** https://arxiv.org/abs/2502.17416
    - **What they did.** A k-layer block looped L times nearly matches a kL-layer model on reasoning. Looping simulates chain of thought.
    - **Closeness.** 1 → C9, C10.
    - **Implication.** An alternative to token-level steps; not a competitor on exactness.

16. **Back de Luca, Fountoulakis. "Simulation of Graph Algorithms with Looped Transformers." ICML 2024 (DBLP conf/icml/LucaF24); arXiv 2402.01107.** https://arxiv.org/abs/2402.01107
    - **What they did.** Constant-size looped transformers simulate Dijkstra, BFS, DFS and Kosaraju for any graph size, with a stated finite-precision limit.
    - **Closeness.** 1 → C10.
    - **Implication.** Constructed, not learned; its precision caveat is a counterpoint to our certified margins.

17. **Liang, Sha, Shi, Song, Zhou. "Looped ReLU MLPs May Be All You Need as Practical Programmable Computers." AISTATS 2025; arXiv 2410.09375.** https://arxiv.org/abs/2410.09375
    - **What they did.** A looped 23-layer ReLU MLP is a programmable computer.
    - **Closeness.** 0.
    - **Implication.** Background for C10.

18. **Liu, Andoni, Hsu. "Fixed Universal Transformers." NeurIPS 2026 (arXiv comment v2); arXiv 2605.31423.** https://arxiv.org/abs/2605.31423
    - **What they did.**
      - One frozen transformer emulates any transformer in a class (H heads, L layers) by changing only the input embedding, which encodes the target's weights.
      - Sparse {0,1} and random constructions; the embedding size grows like H^L.
      - Training only the embedding and unembedding of a frozen random or sparse model reaches 100% on Dyck-1 and k-hop induction.
      - (Deep-read.)
    - **Closeness.** 2 → C10(b), C4.
    - **Implication.**
      - Formal backing for "the program lives in the input representation". Our 2,560-number vector and 8-vector soft prompt that switch the executor on are an instance of this view.
      - Test: can a learned soft prompt encode a *whole table program*, not just switch the executor on?

19. **Huang, Yang, Bhattamishra, Sarrof, Krebs, Zhou, et al. "A Formal Framework for Understanding Length Generalization in Transformers." ICLR 2025; arXiv 2410.02140.** https://arxiv.org/abs/2410.02140
    - **What they did.** Functions expressible by "limit transformers" (C-RASP) are identifiable in the limit from long enough inputs, so they length-generalise under an idealised learner.
    - **Closeness.** 1 → C1.
    - **Implication.** The positive counterpart of C1. Their idealised learner (with regulariser) is not next-token likelihood on reached states. Cite next to the blindness theorem.

20. **Back de Luca, Giapitzakis, Yang, Veličković, Fountoulakis. "Positional Attention: Expressivity and Learnability of Algorithmic Computation." ICML 2025; arXiv 2410.01686.** https://arxiv.org/abs/2410.01686
    - **What they did.** Attention that depends only on positions keeps parallel-model expressivity, with a log-depth cost, and is learnable.
    - **Closeness.** 1 → C10(c), C7.
    - **Implication.** A design option for a certified index increment, where the pointer is purely positional.

### 2.2 Constructed and compiled transformers; neural computers

21. **Weiss, Goldberg, Yahav. "Thinking Like Transformers" (RASP). ICML 2021; arXiv 2106.06981.** https://arxiv.org/abs/2106.06981
    - **What they did.** A programming language whose primitives are attention and feed-forward operations.
    - **Closeness.** 0.
    - **Implication.** Background for any "program in weights" sentence.

22. **Lindner, Kramár, Farquhar, Rahtz, McGrath, Mikulik. "Tracr: Compiled Transformers as a Laboratory for Interpretability." NeurIPS 2023 (spotlight); arXiv 2301.05062.** https://arxiv.org/abs/2301.05062
    - **What they did.** Compiles RASP into decoder-only transformer weights, as ground truth for interpretability.
    - **Closeness.** 1 → C7.
    - **Implication.** Our mechanism analysis (C7) has no compiled ground truth. A reviewer may ask for a Tracr- or ALTA-compiled table executor to validate the head-map method.

23. **Friedman, Wettig, Chen. "Learning Transformer Programs." NeurIPS 2023 (oral); arXiv 2306.01128.** https://arxiv.org/abs/2306.01128
    - **What they did.** Constrained transformers are trained by gradient descent and then decompiled into discrete Python programs.
    - **Closeness.** 1 → C7.
    - **Implication.** An "interpretable by design" contrast to our post-hoc mechanism story.

24. **Shaw, Cohan, Eisenstein, Lee, Berant, Toutanova. "ALTA: Compiler-Based Analysis of Transformers." TMLR 2025; arXiv 2410.18077.** https://arxiv.org/abs/2410.18077
    - **What they did.**
      - A RASP-like language with loops compiles to Universal Transformers.
      - It constructs length-invariant parity and addition.
      - A "minimality" analysis: a non-minimal program's compiled parameters "can be freely changed without affecting any predictions on the training set", that is, they are under-specified.
      - Trace supervision recovers generalisation only when the minimal program generalises.
      - (Learnability section deep-read.)
    - **Closeness.** 2 → C1.
    - **Implication.**
      - The closest compiled-transformer statement of C1's idea: the training set leaves off-path behaviour free.
      - Cite in the blindness section. Our theorem is about likelihood pricing drift by the model's own error rate; theirs is about free parameters. Different, but a reviewer will connect them.

25. **Zhang, Bi, Zhang, Jin, Fu, Jin. "Weights to Code: Extracting Interpretable Algorithms from the Discrete Transformer." arXiv 2601.05770 (2026).** https://arxiv.org/abs/2601.05770
    - **What they did.** A "Discrete Transformer" with temperature-annealed discreteness, from which programs are extracted by hypothesis testing and symbolic regression.
    - **Closeness.** 1 → C7, C2.
    - **Implication.** Discreteness as a route to extractable algorithms is a cousin of closure (C2).

26. **Weng, Zhu, Xia, Li, He, Liu, et al. "Mastering Symbolic Operations: Augmenting Language Models with Compiled Neural Networks" (Neural Comprehension). ICLR 2024; arXiv 2304.01665.** https://arxiv.org/abs/2304.01665
    - **What they did.**
      - Tracr-compiled modules (parity, reverse, copy, addition, subtraction) are attached to pretrained LMs from T5 to GLM-130B. A gate decides token by token whether the LM or a module emits.
      - They report flawless symbolic execution.
      - Their AutoCoNN (LLM writes Tracr code) succeeds on parity and copy but on neither addition nor subtraction (0/20 for each).
      - (Deep-read.)
    - **Closeness.** 2 → C6, C10(b).
    - **Implication.**
      - The first "exact executors inside an LM" paper. Theirs are *separate compiled modules*; ours is *the LLM's own weights*, learned and certified.
      - Their AutoCoNN failure on addition is a nice contrast: Savant writes table programs that work.

27. **Saldyt, Kambhampati. "Algorithmic Language Models with Neurally Compiled Libraries." arXiv 2407.04899 (2024; v2 2025).** https://arxiv.org/abs/2407.04899
    - **What they did.** A preliminary study: memory, registers, basic operations and adaptive recurrence are added to a LLaMA-3-based transformer, with algorithms compiled into a differentiable library.
    - **Closeness.** 1 → C6, C10.
    - **Implication.** Architectural augmentation, against our unmodified-architecture fine-tune.

28. **Bunel, Desmaison, Kohli, Torr, Kumar. "Adaptive Neural Compilation." arXiv 1605.07969 (2016).** https://arxiv.org/abs/1605.07969
    - **What they did.** Programs are compiled into a differentiable machine (registers, memory, interpreter) and then optimised.
    - **Closeness.** 0.
    - **Implication.** Lineage for compile-then-train.

29. **Renda, Ding, Carbin. "Programming with Neural Surrogates of Programs." Onward! 2021; arXiv 2112.06148.** https://arxiv.org/abs/2112.06148
    - **What they did.** Neural networks trained to imitate programs, used for compilation, adaptation and optimisation.
    - **Closeness.** 0.
    - **Implication.** Background.

30. **Pan, Ganesh, Abernethy, Esposo, Lee. "Can Transformers Reason Logically? A Study in SAT Solving." arXiv 2410.07432; ICML 2025 (DBLP conf/icml/Pan0AEL25).** https://arxiv.org/abs/2410.07432
    - **What they did.** A constructed decoder-only transformer decides 3-SAT by DPLL-style chain of thought, implemented with their compiler PARAT. Trained models are compared.
    - **Closeness.** 1 → C10.
    - **Implication.** A second compiler lineage after Tracr.

31. **Turkcan. "Loom: A Scalable Analytical Neural Computer Architecture." arXiv 2604.08816 (Apr 2026).** https://arxiv.org/abs/2604.08816
    - **What they did.**
      - An analytically derived looped transformer, 22 opcodes in 8 layers, executes one instruction per forward pass.
      - The whole machine state is a fixed-size tensor; weights are program-independent; a 9×9 Sudoku runs in 284 instructions.
    - **Closeness.** 2 → C10(b).
    - **Implication.** A constructed universal executor with fixed cost per step. Our counter-position: learned and certified inside a chat LLM.

32. **Leon. "Modular Neural Computer." arXiv 2603.13323 (Mar 2026).** https://arxiv.org/abs/2603.13323
    - **What they did.** Analytically specified MLP modules with external memory and one-hot module gates for exact algorithms (min, sort, A*).
    - **Closeness.** 1 → C10.
    - **Implication.** Background.

33. **Lima de Jesus Silva. "A Symbolic Neural CPU for Quantization-Simulated Writeback and Interpretable Program Execution." arXiv 2607.10021 (Jul 2026).** https://arxiv.org/abs/2607.10021
    - **What they did.** A trace-supervised learned executor with an operation router over a fixed differentiable arithmetic-logic bank. It reproduces reference execution exactly (non-quantised) and keeps the symbolic path through 1,000-instruction programs at 8 bits.
    - **Closeness.** 1 → C6, C10.
    - **Implication.** A learned exact executor, but a bespoke architecture rather than an LLM. Its residual drift traced to a semantics mismatch is a nice parallel to our per-row margins.

34. **Zhuge, Zhao, Liu, Zhou, Liu, Wang, et al. (incl. Tian, Chandra, Schmidhuber; 19 authors). "Neural Computers." arXiv 2604.06425 (Apr 2026).** https://arxiv.org/abs/2604.06425
    - **What they did.**
      - Proposes the model *as* the running computer, aiming at a "Completely Neural Computer" with stable execution and reprogramming.
      - The first step trains video models on CLI and GUI I/O traces. Interface primitives and short-horizon control are learned; routine reuse and "symbolic stability remain challenging".
    - **Closeness.** 1 → C6, C10.
    - **Implication.** A high-profile agenda in which stable symbolic execution is the stated open problem. Our certified, exact execution is a direct answer: cite it in the introduction.

35. **Papailiopoulos. "Can You Train a Computer?" Substack post, 3 March 2026.** https://dimitrisp.substack.com/p/can-you-train-a-computer (code: github.com/anadim/subleq-transformer, not checked)
    - **What they did.**
      - A 4.9M-parameter encoder-only transformer (6 layers, d = 256), built with Claude Code, is *trained* only on single SUBLEQ transitions over a 32-cell, 8-bit machine and then looped.
      - 100% single-step accuracy on about 3.7k held-out states; more than 99.5% on about 800 unseen multi-step programs; the longest fully correct run is 61 steps.
      - Most errors are copy errors on unchanged cells. No certification.
    - **Closeness.** 2 → C2, C5, C10(b).
    - **Implication.**
      - The "trained computer" claim exists informally and is cited by Percepta.
      - Our differences: exactness at length, certification, inside an LLM.
      - Its copy-error failure is what our block eviction avoids, since the state is a short block and not a 32-cell tape.

### 2.3 Classical neural program executors

36. **Zaremba, Sutskever. "Learning to Execute." arXiv 1410.4615 (2014).** https://arxiv.org/abs/1410.4615
    - **What they did.** LSTMs read short Python-like programs character by character and predict their outputs, helped by curriculum learning.
    - **Closeness.** 1 → C6.
    - **Implication.** Origin of "neural networks executing programs". Cite in related work.

37. **Kaiser, Sutskever. "Neural GPUs Learn Algorithms." arXiv 1511.08228 (2015); ICLR 2016.** https://arxiv.org/abs/1511.08228
    - **What they did.** Trained on 20-bit binary arithmetic, the network generalises to much longer inputs. Already in LITERATURE.md.
    - **Closeness.** 2 → C6.
    - **Implication.** "Exact long arithmetic" is not new by itself; C6's novelty must be the LLM, the certificate and language.

38. **Graves, Wayne, Danihelka. "Neural Turing Machines." arXiv 1410.5401 (2014).** https://arxiv.org/abs/1410.5401
    - **What they did.** A differentiable controller with external memory learns copying and sorting.
    - **Closeness.** 0.
    - **Implication.** Background.

39. **Graves, Wayne, Reynolds, Harley, Danihelka, et al. "Hybrid computing using a neural network with dynamic external memory" (DNC). Nature 538, 471–476 (2016).** doi:10.1038/nature20101 (Crossref)
    - **What they did.** A differentiable neural computer with dynamic memory allocation.
    - **Closeness.** 0.
    - **Implication.** Background.

40. **Reed, de Freitas. "Neural Programmer-Interpreters." arXiv 1511.06279; ICLR 2016.** https://arxiv.org/abs/1511.06279
    - **What they did.** A recurrent core learns compositional programs from execution traces, with a program memory and subprogram calls.
    - **Closeness.** 1 → C10.
    - **Implication.** Ancestor of "executor plus programs"; NPI is also the substrate of Cai et al.

41. **Neelakantan, Le, Sutskever. "Neural Programmer: Inducing Latent Programs with Gradient Descent." arXiv 1511.04834; ICLR (the arXiv comment reads "ICLR 2015", Semantic Scholar the same; the year was not re-checked).** https://arxiv.org/abs/1511.04834
    - **What they did.** Induces latent programs over built-in operations.
    - **Closeness.** 0.
    - **Implication.** Background.

42. **Kurach, Andrychowicz, Sutskever. "Neural Random-Access Machines." arXiv 1511.06392 (2015).** https://arxiv.org/abs/1511.06392
    - **What they did.** A controller manipulates pointers over a random-access memory with fixed modules.
    - **Closeness.** 1 → C10(c).
    - **Implication.** Learned pointer manipulation; background for the index increment.

43. **Cai, Shin, Song (ICLR 2017)** — see §1.2.
    - **Closeness.** 3 → C5.

44. **Yan, Swersky, Koutra, Ranganathan, Hashemi. "Neural Execution Engines: Learning to Execute Subroutines." NeurIPS 2020; arXiv 2006.08084.** https://arxiv.org/abs/2006.08084
    - **What they did.** Transformers with learned conditional masking execute the subroutines of sorting, Dijkstra and MST with near-perfect generalisation to much larger sizes. They find transformers struggle to separate "what" to compute from "where".
    - **Closeness.** 1 → C8, C7.
    - **Implication.** The "where" (pointer) failure is the same axis as C8. Cite as precedent that pointer errors dominate.

45. **Bieber, Sutton, Larochelle, Tarlow. "Learning to Execute Programs with Instruction Pointer Attention Graph Neural Networks." NeurIPS 2020; arXiv 2010.12621.** https://arxiv.org/abs/2010.12621
    - **What they did.** A graph neural network over control-flow graphs with a soft instruction pointer, which becomes nearly one-hot. It improves systematic generalisation in program execution.
    - **Closeness.** 2 → C7, C10(c).
    - **Implication.** "A positional pointer that exists but is unused" (C7) should be contrasted with a model in which the pointer *is* the mechanism.

46. **Li, Gimeno, Kohli, Vinyals. "Strong Generalization and Efficiency in Neural Programs." arXiv 2007.03629 (2020).** https://arxiv.org/abs/2007.03629
    - **What they did.** Carefully designed I/O interfaces plus imitation give neural programs correct for arbitrary input sizes (sorting at any size tested); reinforcement learning then improves efficiency.
    - **Closeness.** 1 → C5, C6.
    - **Implication.** Strong generalisation by *interface design*. Our pinned clock is also an interface (what the model sees per step), so cite it there.

47. **Veličković, Ying, Padovano, Hadsell, Blundell. "Neural Execution of Graph Algorithms." ICLR 2020; arXiv 1910.10593.** https://arxiv.org/abs/1910.10593
    - **What they did.** Graph networks imitate step-wise algorithm execution under intermediate supervision.
    - **Closeness.** 0.
    - **Implication.** Background (neural algorithmic reasoning).

48. **Veličković, Badia, Budden, Pascanu, Banino, Dashevskiy, et al. "The CLRS Algorithmic Reasoning Benchmark." ICML 2022; arXiv 2205.15659.** https://arxiv.org/abs/2205.15659
    - **What they did.** Benchmark of 30 classical algorithms with trace hints.
    - **Closeness.** 0.
    - **Implication.** A possible extra domain, not needed.

49. **Rodionov, Prokhorenkova. "Discrete Neural Algorithmic Reasoning." ICML 2025; arXiv 2402.11628.** https://arxiv.org/abs/2402.11628
    - **What they did.** Forces neural reasoners into finite predefined discrete states, separating discrete and continuous flows. Perfect test scores, plus a proof of correctness "for any test data", because the discrete transitions can be checked exhaustively.
    - **Closeness.** 2 → C2, C3, C5.
    - **Implication.**
      - Same logic as our certificate: finite state plus exhaustive transition check gives any length.
      - Theirs is architectural (hard discretisation); ours is closure plus certification inside a continuous LLM.
      - Cite in the closure and Theorem P sections.

50. **Bounsi, Ibarz, Dudzik, Hamrick, Markeeva, Vitvitskyi, et al. "Transformers meet Neural Algorithmic Reasoners" (TransNAR). arXiv 2406.09308; CVPR 2024 MAR workshop.** https://arxiv.org/abs/2406.09308
    - **What they did.** An LM cross-attends to a pretrained graph-network algorithmic reasoner and gains out-of-distribution robustness on text CLRS.
    - **Closeness.** 1 → C6.
    - **Implication.** A hybrid alternative (an external neural executor) to "the LLM is the executor".

51. **Dehghani, Gouws, Vinyals, Uszkoreit, Kaiser. "Universal Transformers." ICLR 2019; arXiv 1807.03819.** https://arxiv.org/abs/1807.03819
    - **What they did.** Weight-shared recurrent depth with adaptive halting.
    - **Closeness.** 0.
    - **Implication.** Background.

### 2.4 LLMs that predict, emulate or are trained on execution

52. **Nye, Andreassen, Gur-Ari, Michalewski, Austin, Bieber, et al. (12 authors). "Show Your Work: Scratchpads for Intermediate Computation with Language Models." arXiv 2112.00114 (2021).** https://arxiv.org/abs/2112.00114
    - **What they did.** Transformers trained to write intermediate steps learn addition and *program execution traces* far better than direct prediction.
    - **Closeness.** 1 → C6, C9.
    - **Implication.** The origin of trace-as-chain-of-thought. Our blocks are a scratchpad with eviction and a certificate.

53. **Zhou, Nova, Larochelle, Courville, Neyshabur, Sedghi. "Teaching Algorithmic Reasoning via In-context Learning." arXiv 2211.09066 (2022).** https://arxiv.org/abs/2211.09066
    - **What they did.** "Algorithmic prompting" (fully explicit step rules) gives large out-of-distribution gains on addition and parity in prompted LLMs.
    - **Closeness.** 1 → C4.
    - **Implication.** Prompt-only execution of an explicit algorithm is the base-model baseline for C4.

54. **Liu, Lu, Chen, Jiang, Svyatkovskiy, Fu, et al. "Code Execution with Pre-trained Language Models" (CodeExecutor). Findings of ACL 2023; arXiv 2305.05383.** https://arxiv.org/abs/2305.05383
    - **What they did.** Pretraining on mutated Python execution traces to predict traces.
    - **Closeness.** 1 → C6.
    - **Implication.** Background.

55. **Ding, Steenhoek, Pei, Kaiser, Le, Ray. "TRACED: Execution-aware Pre-training for Source Code." ICSE 2024; arXiv 2306.07487.** https://arxiv.org/abs/2306.07487
    - **What they did.** Pretraining with execution-trace objectives.
    - **Closeness.** 0.
    - **Implication.** Background.

56. **Gu, Rozière, Leather, Solar-Lezama, Synnaeve, Wang. "CRUXEval: A Benchmark for Code Reasoning, Understanding and Execution." ICML 2024; arXiv 2401.03065.** https://arxiv.org/abs/2401.03065
    - **What they did.** 800 short Python functions with input and output prediction tasks.
    - **Closeness.** 1 → C6.
    - **Implication.** Reviewers may ask how Savant does on CRUXEval-O. Cheap and worth one row (language-kept evidence plus execution transfer).

57. **Liu, Chen, Jabbarvand. "CodeMind: Evaluating Large Language Models for Code Reasoning." arXiv 2402.09664 (2024).** https://arxiv.org/abs/2402.09664
    - **What they did.** A code-reasoning benchmark.
    - **Closeness.** 0.

58. **La Malfa, Weinhuber, Torre, Lin, Marro, Cohn, et al. "Code Simulation Challenges for Large Language Models." arXiv 2401.09074 (2024).** https://arxiv.org/abs/2401.09074
    - **What they did.** Frontier LLMs simulating straight-line code, critical paths, sorting and nested loops, without interpreters. Simulation is fragile and memorisation-driven; "Chain of Simulation" prompting helps.
    - **Closeness.** 1 → C4, C8.
    - **Implication.** Supports the premise that unaided LLM execution is fragile.

59. **Chen, Li, Wu, Liu, Su, Chang, et al. "Can Language Models Pretend Solvers? Logic Code Simulation with LLMs." arXiv 2403.16097 (2024).** https://arxiv.org/abs/2403.16097
    - **What they did.** LLMs simulate the outputs of logic-solver programs.
    - **Closeness.** 0.

60. **Ni, Allamanis, Cohan, Deng, Shi, Sutton, et al. "NExT: Teaching Large Language Models to Reason about Code Execution." arXiv 2404.14662; ICML 2024 per Semantic Scholar.** https://arxiv.org/abs/2404.14662
    - **What they did.** Self-training LLMs to reason over execution traces for program repair.
    - **Closeness.** 0.

61. **Ding, Peng, Min, Kaiser, Yang, Ray. "SemCoder: Training Code Language Models with Comprehensive Semantics Reasoning." NeurIPS 2024; arXiv 2406.01006.** https://arxiv.org/abs/2406.01006
    - **What they did.** "Monologue" reasoning about execution effects for a 6.7B code model.
    - **Closeness.** 0.

62. **Weir, Khalifa, Qiu, Weller, Clark. "Learning to Reason via Program Generation, Emulation, and Search" (CoGEX). NeurIPS 2024; arXiv 2405.16337.** https://arxiv.org/abs/2405.16337
    - **What they did.** LMs are fine-tuned to write Python *pseudo-programs*, with undefined leaf functions, and to *emulate* their execution, including intermediate call results. A single program is searched per task.
    - **Closeness.** 3 → C10(a); 2 → C6, C9.
    - **Implication.**
      - **Programs whose events are the LLM's own judgments already exist** (emulated leaf calls such as `detect_sarcasm`).
      - C10(a) must be reworded to the certified part: the deterministic skeleton certified row by row, with semantic events marked as uncertified oracle calls.
      - C6's "writes programs from plain questions and runs them itself" is shared at the level of pseudo-code. Ours is literal tables plus a certificate plus exactness.

63. **Li, Liang, Zeng, Chen, Hausman, Sadigh, et al. "Chain of Code: Reasoning with a Language Model-Augmented Code Emulator." ICML 2024 (oral); arXiv 2312.04474.** https://arxiv.org/abs/2312.04474
    - **What they did.** Writes code and runs what an interpreter can; the LM emulates the rest ("LMulator"). Also covered by another agent.
    - **Closeness.** 3 → C10(a); 2 → C9.
    - **Implication.** Same as CoGEX. For C9, "program calls mid-thought" with interpreter and emulation exists; ours are in-model and certified.

64. **Armengol-Estapé, Carbonneaux, Zhang, Markosyan, Seeker, Cummins, et al. "What I cannot execute, I do not understand: Training and Evaluating LLMs on Program Execution Traces" (E.T.). arXiv 2503.05703 (2025).** https://arxiv.org/abs/2503.05703
    - **What they did.** Execution tuning on line- and instruction-level traces of about 300k functions. About 80% output prediction on CRUXEval and MBPP; per its appendix, accuracy falls on long executions.
    - **Closeness.** 2 → C6.
    - **Implication.** Trace-trained LLM executors are not exact at length. This supports why C5's certificate matters.

65. **FAIR CodeGen team, Copet, Carbonneaux, Cohen, Gehring, Kahn, et al. (51 authors). "CWM: An Open-Weights LLM for Research on Code Generation with World Models." arXiv 2510.02387 (2025).** https://arxiv.org/abs/2510.02387
    - **What they did.** A 32B model mid-trained on Python interpreter traces and agentic Docker trajectories; it predicts line-by-line program state.
    - **Closeness.** 2 → C6.
    - **Implication.** The strongest *industrial* "LLM simulates execution" model. A baseline row for long table programs would show whether scale plus traces gives exactness at length (we expect not).

66. **Li, Guo, Yang, Xu, Wu, He. "CodeI/O: Condensing Reasoning Patterns via Code Input-Output Prediction." ICML 2025; arXiv 2502.07316.** https://arxiv.org/abs/2502.07316
    - **What they did.** Training on natural-language chain of thought for code input and output prediction improves general reasoning.
    - **Closeness.** 1 → C9.
    - **Implication.** Supports "execution training helps reasoning". Background for C9.

67. **Chen, Li, Bao, Lin, Liu. "Chain of Execution Supervision Promotes General Reasoning in Large Language Models" (TracePile). NeurIPS 2025 (arXiv journal-ref); arXiv 2510.23629.** https://arxiv.org/abs/2510.23629
    - **What they did.** 2.6M "chain of execution" rationales from code runs.
    - **Closeness.** 1 → C9.

68. **Eguchi, Oko, Yamauchi, Shing, Akiba. "Transforming Language Models into Program Interpreters via Execution Trace Chain of Thought" (ET-CoT). TMLR 2026.** https://openreview.net/forum?id=pOg7iub4Pz (existence verified via https://jmlr.org/tmlr/papers/bib/pOg7iub4Pz.bib; workshop version, Eguchi & Akiba, ICML 2025 PRAL workshop, https://icml.cc/virtual/2025/49856)
    - **What they did.** A tracing interpreter (PyTracify) generates systematic traces. LLMs fine-tuned to emit the trace as chain of thought execute Python "consistently" and beat same-size models on CRUXEval-O and LiveCodeBench.
    - **Closeness.** 2 → C6.
    - **Implication.** "Turn an LLM into an interpreter" is now a title. Our C6 differs by literal table programs, the certificate, eviction, and exactness at 4,096 digits. Full-text numbers unverified (§5).

69. **Bayer, Zetzsche, Bouissou, Delmas, Tautschnig, Kong. "Teaching LLMs Program Semantics via Symbolic Execution Traces." arXiv 2605.06184 (May 2026; ICML 2026 listing).** https://arxiv.org/abs/2605.06184
    - **What they did.** Symbolic-execution traces for continued pretraining of Qwen3-8B on C verification tasks. Detection degrades with program length.
    - **Closeness.** 1 → C6.

70. **Maimon, Yoran, Kreuk, Hassid, Cohen, Chambon, et al. "Self-Execution Simulation Improves Coding Models." arXiv 2604.03253 (Mar 2026).** https://arxiv.org/abs/2604.03253
    - **What they did.** SFT on natural-language execution traces plus RLVR. The model simulates its own code's execution to self-verify and self-fix in competitive programming.
    - **Closeness.** 2 → C9.
    - **Implication.** Mid-reasoning *self-simulated* execution is now trained at scale. C9's novelty must be "certified" calls, not "in-model" calls.

71. **Thakur, Saxena, Kulkarni, Singh, Selvam, Patel, et al. "Generating Verifiable Chain of Thoughts from Exection-Traces." arXiv 2512.00127 (2025).** https://arxiv.org/abs/2512.00127
    - **What they did.** Every chain-of-thought narration is cross-checked against the real trace; 54k verified rationales.
    - **Closeness.** 1 → C9.
    - **Implication.** "Verified" here means verified training data, not a certified executor. Cite to pre-empt word confusion.

72. **Zhang, Liao, Bao, Li, Wang, Ye, et al. (13 authors). "The Imitation Game: When LLMs Learn to Reason Like Programs via Code-Centric Reasoning Data Synthesis" (MIMIC). EMNLP 2026 (arXiv comment); arXiv 2609.16076.** https://arxiv.org/abs/2609.16076
    - **What they did.** Instrumented code produces dense execution-state rewards for reinforcement learning.
    - **Closeness.** 1 → C9.

73. **Lai, Xu, Yang, Huang, Cao, Xu (CAEF), 2024** — see §1.3.
    - **Closeness.** 3 → C6; 2 → C5, C10.

74. **Hua, Zhang, Lyu, Gu, Gao, Liu, et al. "The Imitation Game: Turing Machine Imitator is Length Generalizable Reasoner" (TAIL). arXiv 2507.13332 (2025); ICLR 2026 per a secondary listing.** https://arxiv.org/abs/2507.13332
    - **What they did.**
      - Qwen2.5-7B fine-tuned on synthetic chain of thought that imitates Turing-machine execution (linear transition, atomic states, memory fetcher) across 18 tasks.
      - Large-number addition trained at 10–30 digits reaches 86.5% at 41–50 digits.
      - The whole trace stays in context; general ability is not evaluated.
      - (Deep-read.)
    - **Closeness.** 2 → C6.
    - **Implication.** The strongest "LLM imitates a Turing machine" fine-tune. Not exact and no eviction. A good baseline table row (86.5% at under 2× length against our exact result at 64×+).

75. **Hou, Brandfonbrener, Kakade, Jelassi, Malach. "Universal Length Generalization with Turing Programs." arXiv 2407.03310 (2024); ICML 2025 per LITERATURE.md.** https://arxiv.org/abs/2407.03310
    - **What they did.** A Turing-machine-tape chain of thought (copy with small edits) gives robust length generalisation on addition, multiplication and in-context SGD. A RASP construction simulates any Turing machine.
    - **Closeness.** 2 → C6.
    - **Implication.** Already in LITERATURE.md. Pair it with TAIL in the C6 related work.

76. **Samiei, Mansouri, Soleymani Baghshah. "The Illusion of Procedural Reasoning: Measuring Long-Horizon FSM Execution in LLMs." arXiv 2511.14777 (Nov 2025).** https://arxiv.org/abs/2511.14777
    - **What they did.**
      - An explicit finite-state machine (states and actions as unrelated single-token words) is given in the system prompt; the model executes it turn by turn.
      - Qwen models up to Qwen3-235B reach about 50% task accuracy.
      - Gemini-2.5-flash reaches about 50% after 50 steps with 2 states × 40 actions, but about 100% with 40 states × 2 actions. Failures track rule-retrieval branching more than memory.
      - Negative self-conditioning appears; thinking mitigates it.
      - (Deep-read.)
    - **Closeness.** 2 → C4, C8.
    - **Implication.**
      - The nearest public benchmark to our table-in-prompt setting, with frontier and Qwen3 numbers.
      - **Run Savant and Qwen3-4B base (with and without the vector) on it** (§4). Their "branching beats memory" finding is a rival to C8's "pointer first": our analysis should separate row-retrieval errors from event-pointer errors.

77. **Wu, Han, Zhou, Huang, Zhang. "Computational Reasoning of Large Language Models" (TMBench). arXiv 2504.20771 (2025).** https://arxiv.org/abs/2504.20771
    - **What they did.** A Turing-machine benchmark: follow given transition rules and manage internal state for many steps.
    - **Closeness.** 1 → C4, C8.
    - **Implication.** An extra evaluation option.

78. **Panda, Kadasi, Upperwal, Singh. "When LLMs Stop Following Steps: A Diagnostic Study of Procedural Execution in Language Models." arXiv 2605.00817 (May 2026).** https://arxiv.org/abs/2605.00817
    - **What they did.** Step-wise arithmetic procedures: accuracy falls from 63% at 5 steps to 20% at 95 steps, with look-back dependencies as a key difficulty factor.
    - **Closeness.** 1 → C8.
    - **Implication.** Supports the "look-back/pointer" diagnosis.

79. **Sinha, Arun, Goel, Staab, Geiping. "The Illusion of Diminishing Returns: Measuring Long Horizon Execution in LLMs." ICLR 2026; arXiv 2509.09677.** https://arxiv.org/abs/2509.09677
    - **What they did.** Already in refs.bib. Execution with the plan given; self-conditioning on own errors.
    - **Closeness.** 2 → C8.
    - **Implication.** Already cited. C8 should state how "pointer first, then drift" relates to self-conditioning.

80. **Meyerson, Paolo, Dailey, Shahrzad, Francon, Hayes, et al. (MAKER), 2025** — see §1.5.
    - **Closeness.** 2 → C5, C6.

81. **Pai, Xian. "Long-Horizon State Tracking in LLMs: Executing MD5 through a Deep Sequence of Dependent Tool Calls." arXiv 2609.00012 (Aug 2026).** https://arxiv.org/abs/2609.00012
    - **What they did.** gpt-oss-120b carries exact MD5 state across 196 dependent tool calls.
    - **Closeness.** 1 → C6.
    - **Implication.** Tool-mediated contrast.

82. **Dugan, Jimenez Beneto, Loh, Chen, Dangovski, Soljačić. "OccamLLM: Fast and Exact Language Model Arithmetic in a Single Step." NeurIPS 2024; arXiv 2406.06576.** https://arxiv.org/abs/2406.06576
    - **What they did.** LLM hidden states control a symbolic module (OccamNet), giving 100% on single arithmetic operations.
    - **Closeness.** 1 → C6.
    - **Implication.** "Exact arithmetic in an LLM" via a bolted-on symbolic unit. Contrast with in-weights execution.

83. **Chen, Ma, Wang, Cohen. "Program of Thoughts Prompting." TMLR 2023; arXiv 2211.12588** and **Gao, Madaan, Zhou, Alon, Liu, Yang, et al. "PAL: Program-aided Language Models." arXiv 2211.10435.** https://arxiv.org/abs/2211.12588 ; https://arxiv.org/abs/2211.10435
    - **What they did.** The LLM writes code and an external interpreter runs it.
    - **Closeness.** 1 → C6, C9.
    - **Implication.** The tool-use baseline that Savant replaces. Cite once.

### 2.5 In-context automata and algorithm execution

84. **Akyürek, Wang, Kim, Andreas. "In-Context Language Learning: Architectures and Algorithms." arXiv 2401.12973 (2024).** https://arxiv.org/abs/2401.12973
    - **What they did.** Models learn regular languages from random DFAs in context. Transformers win, behaving like smoothed n-gram models via "n-gram heads".
    - **Closeness.** 1 → C4, C7.
    - **Implication.** In-context automaton *learning* from samples, not *execution* of a given table. Cite to separate the two.

85. **Gupta, Sanders, Solar-Lezama. "Randomly Sampled Language Reasoning Problems Elucidate Limitations of In-Context Learning." arXiv 2501.02825 (2025).** https://arxiv.org/abs/2501.02825
    - **What they did.** On randomly drawn simple languages, LLMs underperform n-gram models, with and without chain of thought.
    - **Closeness.** 1 → C4.

86. **Li, Raman, Wan, Samman, Lin. "Scaling Laws for State Dynamics in Large Language Models." arXiv 2505.14892 (2025).** https://arxiv.org/abs/2505.14892
    - **What they did.**
      - Prompted DFA next-state prediction with GPT-2 and Pythia. Pythia-1B stays under 50% with more than 10 states.
      - Activation patching finds state-propagating heads, but "action information is not reliably routed to the final token".
    - **Closeness.** 2 → C4, C7.
    - **Implication.**
      - Close in spirit to C4's "finds the row but does not read it out": heads carry the right information, and the readout fails.
      - Cite as the small-model precedent. Our contribution is the Qwen3-4B quantification (92% head against 35% rows) and the one-vector fix.

87. **Zhang, Du, Jin, Fu, Jin. "Finite State Automata Inside Transformers with Chain-of-Thought: A Mechanistic Study on State Tracking." ACL 2025 (per Semantic Scholar); arXiv 2502.20129.** https://arxiv.org/abs/2502.20129
    - **What they did.** Already in NOVELTY.md. Late-layer MLP neurons implement the automaton in chain-of-thought transformers.
    - **Closeness.** 1 → C7.

88. **Todd, Li, Sen Sharma, Mueller, Wallace, Bau. "Function Vectors in Large Language Models." ICLR 2024; arXiv 2310.15213.** https://arxiv.org/abs/2310.15213
    - **What they did.** A few heads carry a compact task vector. Adding it at one layer triggers the task zero-shot and in natural text.
    - **Closeness.** 2 → C4.
    - **Implication.** **Precedent for "a single vector added at one layer switches a capability on".** C4 must cite it and compare against it.
      - Test: build a mean-activation function vector from table-execution prompts and see whether it recovers the 99.8% of rows our trained 2,560-number vector gets.

89. **Hendel, Geva, Globerson. "In-Context Learning Creates Task Vectors." Findings of EMNLP 2023; arXiv 2310.15916.** https://arxiv.org/abs/2310.15916
    - **What they did.** In-context demonstrations compress into a single task vector that can be patched in.
    - **Closeness.** 2 → C4.
    - **Implication.** Same as function vectors.

### 2.6 Latent, recurrent and bounded-context computation

90. **Geiping, McLeish, Jain, Kirchenbauer, Singh, Bartoldson, et al. "Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach." NeurIPS 2025 (spotlight); arXiv 2502.05171.** https://arxiv.org/abs/2502.05171
    - **What they did.** Already in LITERATURE.md.
    - **Closeness.** 1 → C9.

91. **McLeish, Li, Kirchenbauer, Kalra, Bartoldson, Kailkhura, et al. "Teaching Pretrained Language Models to Think Deeper with Retrofitted Recurrence." arXiv 2511.07384 (2025).** https://arxiv.org/abs/2511.07384
    - **What they did.** Converts pretrained LMs into depth-recurrent models.
    - **Closeness.** 1 → C9.
    - **Implication.** Latent loops in a *pretrained* LM: the nearest latent alternative to token-level blocks.

92. **Hao, Sukhbaatar, Su, Li, Hu, Weston, et al. "Training Large Language Models to Reason in a Continuous Latent Space" (Coconut). COLM 2025; arXiv 2412.06769.** https://arxiv.org/abs/2412.06769
    - **What they did.** Already cited.
    - **Closeness.** 1.

93. **Goyal, Ji, Rawat, Menon, Kumar, Nagarajan. "Think before you speak: Training Language Models With Pause Tokens." ICLR 2024; arXiv 2310.02226.** https://arxiv.org/abs/2310.02226
    - **What they did.** Pause tokens add computation steps.
    - **Closeness.** 0.

94. **Zhu, Wang, Hua, Zhang, Li, Que, et al. (33 authors). "Scaling Latent Reasoning via Looped Language Models" (Ouro). arXiv 2510.25741 (2025; v6 2026).** https://arxiv.org/abs/2510.25741
    - **What they did.** Pretrained looped LMs at 1.4B and 2.6B, trained on 7.7T tokens.
    - **Closeness.** 0 → C9.

95. **Bae, Kim, Bayat, Kim, Ha, Schuster, et al. "Mixture-of-Recursions." arXiv 2507.10524 (2025).** https://arxiv.org/abs/2507.10524
    - **Closeness.** 0.

96. **Wang, Li, Sun, Chen, Liu, Wu, et al. "Hierarchical Reasoning Model." arXiv 2506.21734 (2025)** and **Jolicoeur-Martineau. "Less is More: Recursive Reasoning with Tiny Networks." arXiv 2510.04871 (2025).** https://arxiv.org/abs/2506.21734 ; https://arxiv.org/abs/2510.04871
    - **What they did.** Small recurrent reasoners on Sudoku, mazes and ARC.
    - **Closeness.** 0 → C2.
    - **Implication.** Background; a reviewer may name them as "small recurrent nets that reason".

97. **Fan, Du, Ramchandran, Lee. "Looped Transformers for Length Generalization." ICLR 2025; arXiv 2409.15647.** https://arxiv.org/abs/2409.15647
    - **What they did.** Looped transformers with an adaptive number of steps length-generalise on tasks with a known iterative solution built from RASP-L operations.
    - **Closeness.** 1 → C2.

98. **Yang, Srebro, McAllester, Li. "PENCIL: Long Thoughts with Short Memory." ICML 2025; arXiv 2503.14337** — see §1.5.
    - **Closeness.** 2 → C5.
    - **Implication.** Erasure with a recomputed KV cache. Our policy evicts without recomputation, because Π is a fixed prefix and positions restart.

99. **Yan, Shen, Liu, Jiang, Zhang, Shao, et al. "InftyThink: Breaking the Length Limits of Long-Context Reasoning in Large Language Models." ICLR 2026; arXiv 2503.06692.** https://arxiv.org/abs/2503.06692
    - **What they did.** Short reasoning segments alternate with summaries; earlier text is dropped.
    - **Closeness.** 1 → C5.
    - **Implication.** Bounded-context family; lossy summaries, no exactness.

100. **Yang, Liao, Fan. "Markov Chain of Thought for Efficient Mathematical Reasoning." NAACL 2025; arXiv 2410.17635.** https://arxiv.org/abs/2410.17635
     - **What they did.** Each reasoning step conditions only on a simplified current state.
     - **Closeness.** 1 → C5.

101. **Ge, Singh, Zhuang, Liu, Gao, Sala. "Register Tokens for Bounded-State Reasoning in Diffusion Language Models." arXiv 2609.16372 (Sep 2026).** https://arxiv.org/abs/2609.16372
     - **What they did.** Decode a chunk, clear it, and carry only register-token hidden states.
     - **Closeness.** 1 → C5.
     - **Implication.** "Clear the chunk, keep a fixed state" is now a 2026 pattern even in diffusion LMs. Our distinctive part is the certificate.

102. **Li, Li, Zhou. "Skip a Layer or Loop It? Learning Program-of-Layers in LLMs." ICML 2026; arXiv 2606.06574.** https://arxiv.org/abs/2606.06574
     - **What they did.** Per-input programs over pretrained layers (skip or loop).
     - **Closeness.** 0.
     - **Implication.** The word "program" is used differently; avoid confusion.

### 2.7 Mechanism and elicitation (adjacent; another agent likely covers interpretability)

103. **Prakash, Rott Shaham, Haklay, Belinkov, Bau. "Fine-Tuning Enhances Existing Mechanisms: A Case Study on Entity Tracking." ICLR 2024; arXiv 2402.14811.** https://arxiv.org/abs/2402.14811
     - **What they did.** Math fine-tuning improves entity tracking by *enhancing the same circuit* (positional pointers), not by building a new one.
     - **Closeness.** 2 → C4, C7.
     - **Implication.**
       - The direct precedent for "30 steps switch on a latent executor".
       - C4 should say "consistent with Prakash et al.: fine-tuning amplifies a circuit that is already there", and claim the new part: table-program execution, the head-against-readout gap, and certification.
       - Their cross-model activation patching is a method to borrow.

104. **Prakash, Shapira, Sen Sharma, Riedl, Belinkov, Rott Shaham, et al. "Language Models use Lookbacks to Track Beliefs." arXiv 2505.14685 (2025).** https://arxiv.org/abs/2505.14685
     - **What they did.** Lookback (pointer) mechanisms bind and retrieve states.
     - **Closeness.** 1 → C7, C8.

105. **Feng, Steinhardt. "How do Language Models Bind Entities in Context?" ICLR 2024 (DBLP conf/iclr/FengS24); arXiv 2310.17191.** https://arxiv.org/abs/2310.17191
     - **What they did.** Binding-ID vectors.
     - **Closeness.** 1 → C7.

106. **Wu, Geiger, Millière. "How Do Transformers Learn Variable Binding in Symbolic Programs?" ICML 2025 (arXiv comment); arXiv 2505.20896.** https://arxiv.org/abs/2505.20896
     - **What they did.** Trained transformers dereference assignment chains using the residual stream as addressable memory and routing heads, after a phase of shallow heuristics.
     - **Closeness.** 1 → C7.

107. **Wu, Wang, Xiao, Peng, Fu. "Retrieval Head Mechanistically Explains Long-Context Factuality." arXiv 2404.15574 (2024); ICLR per Semantic Scholar.** https://arxiv.org/abs/2404.15574
     - **What they did.** Fewer than 5% of heads do retrieval, and they exist already after short-context pretraining.
     - **Closeness.** 1 → C7.
     - **Implication.** Our ~30-head lookup committee should be compared with the retrieval-head set in Qwen3-4B. Do they coincide?

108. **Nikankin, Reusch, Mueller, Belinkov. "Arithmetic Without Algorithms: Language Models Solve Math With a Bag of Heuristics." arXiv 2410.21272; ICLR 2025 per Semantic Scholar** and **Kantamneni, Tegmark. "Language Models Use Trigonometry to Do Addition." arXiv 2502.00873 (2025).** https://arxiv.org/abs/2410.21272 ; https://arxiv.org/abs/2502.00873
     - **What they did.** How LLMs do arithmetic natively.
     - **Closeness.** 1 → C6, C7.
     - **Implication.** Contrast: Savant's arithmetic is table execution, not heuristics.

109. **Sinii, Gorbatovski, Cherepanov, Shaposhnikov, Balagansky, Gavrilov. "Steering LLM Reasoning Through Bias-Only Adaptation." EMNLP 2025; arXiv 2505.18706** and **Sinii, Balagansky, Gerasimov, Laptev, Aksenov, Kurochkin, et al. "Small Vectors, Big Effects." arXiv 2509.06608 (2025).** https://arxiv.org/abs/2505.18706 ; https://arxiv.org/abs/2509.06608
     - **What they did.** Trained per-layer steering vectors recover most of the reinforcement-learning reasoning gains.
     - **Closeness.** 2 → C4.
     - **Implication.** "One trained vector switches a capability on" is established for reasoning. Cite with function vectors.

110. **Venhoff, Arcuschin, Torr, Conmy, Nanda. "Base Models Know How to Reason, Thinking Models Learn When." ICML 2026 (spotlight; arXiv comment); arXiv 2510.07364.** https://arxiv.org/abs/2510.07364
     - **What they did.** Steering vectors induce reasoning mechanisms already present in base models.
     - **Closeness.** 2 → C4.
     - **Implication.** The same "latent in base" thesis as C4. Phrase C4 as an instance with a precise, testable mechanism.

111. **Wu, Arora, Wang, Geiger, Jurafsky, Manning, et al. "ReFT: Representation Finetuning for Language Models." arXiv 2404.03592 (2024).** https://arxiv.org/abs/2404.03592
     - **What they did.** Low-rank interventions on hidden representations.
     - **Closeness.** 1 → C4.
     - **Implication.** The rank-1 certification of 505/512 tables is a ReFT-style intervention. Cite as the method family.

---

## 3. Where the frontier is now (October 2026)

**Theory: universality is settled; the open questions are practical.**
- Transformers and LLMs are universal under almost any assumption: constant precision, a single fixed transformer with programs as prompts, frozen random networks with a learned codebook.
- Prompted LLMs have been certified, rule by rule, to run a universal Lag system. This was Gemini in 2024 and, reproducibly, Llama-4 in 2026, under a fresh-call harness.
- The open questions are programmability, efficiency, learnability, and above all **reliability at length**.

**Constructions.** Hand-built "computers inside transformers" now run real software fast:
- Percepta's compiled WebAssembly interpreter (millions of steps, O(log t) per step, a by-construction margin guarantee);
- their October 2026 MicroPython in Spotlight memory (tens of millions of steps at about 140k tokens/s);
- Loom and the Fixed Universal Transformer.

None of them is a language model or learned. Percepta has announced LLM integration and formal verification as its next steps.

**Learned executors.** On the learned side, LLMs fine-tuned on traces emulate execution well but not exactly:
- TAIL: 86.5% at under 2× training length;
- CAEF: 98–99.6% at 100 digits;
- E.T., CWM and ET-CoT: strong on CRUXEval, but they degrade with trace length.

Benchmarks of rule-following with given tables (FSM execution, TMBench, procedural arithmetic, Sinha et al.) show frontier models still collapse over tens to hundreds of steps.

**Long exact runs come from bounding the context.** PENCIL, InftyThink, the Markovian Thinker and register tokens all do this. The only million-step zero-error run (MAKER) bounds each step's context and then *votes*, at a cost of thousands of dollars.

**Verification of neural executors** is old: Cai et al. 2017 for recursive NPI, and discrete NAR in 2025.

**What nobody has shown:**
- a learned executor *inside a pretrained chat LLM*;
- that writes its own table programs;
- whose trained weights carry a per-row certificate;
- under a cache policy proven necessary and sufficient for exactness at every length;
- with the converse impossibility for unpinned decoding;
- with language kept.

That conjunction is our slot. Each component has a precursor that must be cited.

---

## 4. Ideas (experiments, comparisons, framings)

1. **Hanoi-20 against MAKER (C5, C6).**
   - 1,048,575 moves as a table program on Savant under the pinned clock: one greedy pass per move, rows certified.
   - Report exactness, wall-clock and dollar cost against MAKER's thousands of dollars on gpt-4.1-mini with voting.
   - Cheap (local 4B); a striking headline.

2. **Theorem pair on the Lag construction (C5, C10(b)).**
   - Certify the 1,857 U(15,2) Lag rules of Lewandowski et al. on Savant under the pinned clock.
   - Then run the same rules unpinned, with history kept, and show failure at length although every rule passes alone.
   - A live demonstration of `no_finite_test_suite` on the competitor's own object, and the best way to make the "they did sufficiency; we prove necessity and impossibility" point concrete.

3. **CAEF head-to-head (C6, C8).**
   - Run `NJUDeepEngine/CAEF_llama3.1_8b` on our addition sweep and on repeated-digit adversarial inputs ("999…", "456456…"); run Savant on the same.
   - Try certifying CAEF's executor rows under our harness, to separate format from certificate.

4. **FSM-execution benchmark (C4, C8).**
   - Evaluate Qwen3-4B base, base plus our 2,560-number vector, and Savant on Samiei et al.'s FSMs, including the 2 × 40 against 40 × 2 configurations.
   - If the vector transfers to their format, C4 generalises beyond our tables.
   - Break failures down into row-retrieval and event-pointer errors, to test C8 against their "branching factor" explanation.

5. **Function-vector baseline for C4.**
   - Build mean-activation function and task vectors (Todd; Hendel) for "execute the table" and compare them with our trained one-layer vector, in rows certified and in transfer across tables.
   - If a function vector already reaches about 99%, C4's vector claim becomes "the function vector of table execution". If not, that is a result.

6. **Lookup committee against retrieval heads (C7).**
   - Compute Wu et al.'s retrieval-head scores in Qwen3-4B and measure overlap with our ~30 lookup heads.
   - Also run Prakash et al.'s cross-model activation patching (base against Savant) to test "fine-tuning enhances the existing lookup circuit".

7. **Pointer as certified increment (C10(c)).**
   - Implement the instruction pointer as an exact cumulative sum, as in Percepta and Giannou: uniform attention times position, or positional attention (Back de Luca et al. 2025).
   - Certify it in Lean, then remove the clock.
   - Cite all three; claim the *learned and certified* version.

8. **C10(a), honestly.** Chain of Code and CoGEX already execute programs whose leaves are LM judgments. Frame ours as "certified skeleton, uncertified semantic oracle calls, with the oracle-call count reported per answer". The claim is the separation, not the idea.

9. **Soft prompt as program (C10(b), C4).**
   - Given Fixed Universal Transformers, test whether a trained soft prompt can carry a *specific* table program, not only the executor switch, and still certify.
   - A short experiment linking C4 and C10.

10. **Mechanism validation on a compiled executor (C7).** Compile a small table executor with Tracr or ALTA and run our head-map and logit-lens pipeline on it, where the ground truth is known. This pre-empts "is the head-map method valid?".

11. **Baseline rows to add to tables (C6):**
    - TAIL (Qwen2.5-7B) and CAEF (LLaMA-3.1-8B) as fine-tuned executor baselines;
    - CWM-32B as a scaled trace model;
    - Savant on CRUXEval-O, to show execution transfer and that language is kept.

12. **Framing sentences to adopt:**
    - "Theorem P is to pinned LLM decoding what Cai et al.'s verification theorem is to recursive neural programs, with both directions proved in Lean."
    - "Percepta constructs a computer in a transformer; we certify the one an LLM learns."
    - "MAKER makes a million steps exact by voting; certification makes each step exact once."

---

## 5. Unverified or partly verified

- **Percepta formal write-up** (promised 25 March 2026). Searched arXiv and the web for Tzamos, CALM, HullKVCache and Append-only Lookup Machine; nothing found.
- **"Spotlight Memory" companion post** (2 October 2026). Only its metadata and the capabilities post were read.
- **ET-CoT (TMLR 2026) full text.** OpenReview returned a browser check and its API returned nothing.
  - Existence, authors and venue were verified from the TMLR BibTeX at jmlr.org and the ICML 2025 workshop page.
  - No numbers verified.
- **Papailiopoulos, "Can You Train a Computer?"** A blog post with no paper. The GitHub repository `anadim/subleq-transformer` was not checked.
- **Venues taken only from Semantic Scholar or secondary pages:**
  - Wei et al. (NeurIPS; Semantic Scholar year inconsistent);
  - Giannou et al. (ICML 2023);
  - Malach (ICML);
  - NExT (ICML 2024);
  - Retrieval heads (ICLR);
  - Nikankin (ICLR 2025);
  - Zhang et al. FSA (ACL 2025);
  - TAIL (ICLR 2026, secondary page only);
  - Li & Wang 2512.00003 (ICLR 2026, mlanthology);
  - Hou et al. (ICML 2025, from LITERATURE.md).
- **Saldyt & Kambhampati venue.** A NeurIPS 2024 workshop page appeared in search results but was not fetched.
- **Gur-Arieh et al. 2025** (binding mechanisms, cited on a project page). Not looked up.
- **Neural Computers (Zhuge et al.).** Only the abstract and metadata read; no result numbers.
- **Out of scope and left to other agents:**
  - StreamingLLM and attention sinks (verified arXiv 2309.17453 only);
  - NextLat and state-tracking architectures;
  - tool-integrated reasoning.
