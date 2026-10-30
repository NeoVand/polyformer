**Verdict: NARROW. Do not present the claim as a new discovery that pretrained LLMs can be exact computers.** That proposition, finite local verification, learned machine execution, bounded-context recurrence, and internal execution alongside language generation all have substantial prior art. I did **not** find a source establishing the entire specified combination: Qwen3-4B + small LoRA + this cache protocol + inherited digit arithmetic + a complete execution certificate + measured capability retention.

Search cutoff: **29 October 2026**. I ran the twelve requested search families and the named antecedent checks, using primary papers, OpenReview material, repositories, and company announcements. Google Scholar’s direct search endpoint was inaccessible; some OpenReview pages challenged access, although indexed PDFs were available. Repository and company claims below are treated as **public disclosures**, not independently reproduced results. No files were edited.

“STATES” below kills the **explicitly identified component**. It does not mean that a paper containing one component anticipates the entire conjunction.

| Claim | Overall prior-art grade | Gate result |
|---|---|---|
| S1: inherited arithmetic, exhaustively certified as primitives | **IMPLIES/PARTIAL** | Possible narrow contribution; exhaustive neural arithmetic certification itself is known. |
| S2: self-written programs executed internally, exact at length | **IMPLIES/PARTIAL** | Learned execution and internal generation/execution are known; their certified realization in the specified pretrained model remains distinguishable. |
| S3: cache policy yielding recurrence and finite certification | **IMPLIES/PARTIAL** | Eviction, position reuse, recurrence, and finite local verification are known separately. The particular closure theorem could matter. |
| S4: semantic judgment followed by same-model certified arithmetic | **IMPLIES/PARTIAL** | Judgment plus exact aggregation is known; using inherited certified arithmetic in the same model is the remaining distinction. |
| S5: complete combination | **IMPLIES/PARTIAL** | No exact antecedent located; substantial combination-level overlap prevents PASS. |

**S1. Exhaustively certify inherited digit arithmetic and use it as an instruction set**

The strongest predecessors are these:

| Source and date | Short verbatim quote | Grade and consequence |
|---|---|---|
| Schuurmans, [*Memory Augmented Large Language Models are Computationally Universal*](https://arxiv.org/html/2301.04589v1), **10 January 2023** | “checking a finite set of prompt-result behaviours” | **STATES** finite verification of a pretrained LLM used as a computer. **PARTIAL** for S1: the system supplies external associative memory, and its host code performs integer increment/decrement. It does not establish inherited decimal arithmetic as the certified ALU. |
| Schuurmans, Dai, Zanini, [*Autoregressive Large Language Models are Computationally Universal*](https://arxiv.org/abs/2410.03170), **4 October 2024** | “correctly apply each of the 2027 production rules” | **STATES** exhaustive rule checking for a pretrained model under extended greedy decoding. Kills novelty for “verify a finite instruction/rule set, then obtain universal computation.” |
| Lewandowski, Machado, Schuurmans, [*Universal computation is intrinsic to language model decoding*](https://arxiv.org/html/2601.08061v2), **12 January 2026; revised 10 February** | “The proof consists of an enumeration of the 1857 cases” | **STATES** the local-enumeration-to-unbounded-execution proof strategy for a pretrained model. **PARTIAL** for inherited arithmetic: the system prompt supplies a universal production-rule table. |
| Price, [*nCPU* manuscript, pinned repository version](https://github.com/robertcprice/nCPU/blob/bd56284c0b978cdd3dbd675023d6b1a486627f62/paper/ncpu_paper.md), **March 2026; present in a 7 March commit** | “finite, fully enumerable input spaces that can be exhaustively verified” | **STATES** exhaustive verification of neural ALU primitives: full adder, carry combination, logical operations, and byte multiplication. **PARTIAL** for S1: purpose-trained components, not inherited chat-model arithmetic. Its composition checks are less strong than its primitive checks. |
| Naughton, [*Certified Grokking*](https://github.com/brian-naughton/certified-grokking), **M1 release commit: 2 July 2026** | “target argmax on all 12,769 inputs” | **STATES** full-domain arithmetic-transformer certification with independently checkable interval bounds. **PARTIAL**: modular addition in a small task-trained transformer, not decimal micro-prompts in a pretrained chat model. |
| Naughton, [*Certified Inference*](https://github.com/brian-naughton/certified-inference), **4 July 2026** | “unique full-vocabulary exact-real next-token argmax” | **STATES** rigorous next-token certification for pretrained language models. **PARTIAL**: certifies model predictions, not an arithmetic specification or a universal executor. |

Two corrections matter. The memory-augmented Schuurmans paper is **2023**, not 2024. Also, *Certified Grokking* explicitly distinguishes its **exact-real network certificate** from empirical agreement with floating-point execution. “Certified on the device” is a different guarantee, not automatically a stronger one.

**Surviving S1 wording:** “We exhaustively validate a pinned pretrained chat model’s pre-existing decimal and Boolean micro-prompt behavior and use those validated behaviors as execution primitives.”

That wording still requires evidence that the operations worked **before** executor fine-tuning. Testing only the adapted model does not establish inheritance. Exhaustive checking of 200 addition-with-carry inputs establishes that particular interface, not arithmetic competence under arbitrary prompts or cached contexts.

**S2. Fine-tune an LLM to execute its own programs internally, exactly at length**

| Source and date | Short verbatim quote | Grade and consequence |
|---|---|---|
| Cai, Shin, Song, [*Making Neural Programming Architectures Generalize via Recursion*](https://people.eecs.berkeley.edu/~dawnsong/papers/iclr_2017_recursion.pdf), **ICLR 2017; arXiv 21 April 2017** | “provably perfect generalization” | **STATES** learned neural execution with finite verification sufficient for unrestricted task-size generalization. Their addition verification set contains 20,181 problems under stated input assumptions. **PARTIAL**: recursive NPI, not a pretrained chat transformer. |
| Giannou et al., [*Looped Transformers as Programmable Computers*](https://arxiv.org/abs/2301.13196), **30 January 2023; ICML 2023** | “function calls, program counters, and conditional branches” | **STATES** transformer execution of an instruction-set computer. Program counters, registers, branches, and looping are not differentiators. **PARTIAL**: constructed weights rather than LoRA learning in a chat model. |
| Lai et al., [CAEF: *Executing Arithmetic*](https://arxiv.org/html/2410.07896v1), **10 October 2024** | “All the executors and the aligner are executed by the LLM.” | **STATES** LoRA-based LLaMA execution of arithmetic machines and composition of learned operators. **PARTIAL**: separate adapters, prescribed operators, and empirical near-perfect performance up to 100 digits—not an all-length certificate. |
| Xu et al., [*Training Transformers as a Universal Computer* / MicroPy](https://arxiv.org/html/2604.25166v1), **28 April 2026** | “perfect accuracy on each task within the tested context lengths” | **STATES** a trained transformer predicting small-step execution of novel programs using bounded-context PENCIL scaffolding. **PARTIAL**: a 59.5M specialized model; tested-context accuracy, not certified correctness for every length. |
| Tong et al., [*Is Code Better Than Language for Algorithmic Reasoning?*](https://arxiv.org/abs/2606.15589), **14 June 2026; ICML 2026** | “the language model simulates that code in context” | **STATES** the self-generated-code/internal-simulation workflow. **PARTIAL**: no exactness guarantee; their experiments find little benefit from changing representation without reliable execution. |

CAEF is particularly damaging to a loosely written novelty claim: it already combines a **pretrained LLaMA, LoRA, machine-state transitions, arithmetic, and operator composition**. Its explicit limitation—“Prone to errors with repeated digit patterns”—is a useful distinction your certificate would have to eliminate, not merely outperform on sampled tests. [CAEF, §6](https://arxiv.org/html/2410.07896v1)

The other requested execution-training checks do not kill the certified formulation, but they must not be omitted from related work:

| Source/date | Verbatim quote | Grade |
|---|---|---|
| Zaremba–Sutskever, [*Learning to Execute*](https://arxiv.org/abs/1410.4615), **17 October 2014** | “training them to evaluate short computer programs” | **CONTEXT:** learned execution predates LLMs. |
| Liu et al., [*Code Execution with Pre-trained Language Models*](https://arxiv.org/abs/2305.05383), **8 May 2023** | “code execution pre-training and curriculum learning” | **IMPLIES/PARTIAL:** execution-trace training of pretrained transformers is established. |
| Ni et al., [*NExT*](https://arxiv.org/abs/2404.14662), **23 April 2024** | “inspect the execution traces of programs” | **CONTEXT:** execution-aware reasoning training, not certified interpretation. |
| Ding et al., [*SemCoder*](https://arxiv.org/abs/2406.01006), **3 June 2024** | “linking static code text with dynamic execution states” | **IMPLIES/PARTIAL:** one model learns generation and execution reasoning. |
| Li et al., [*CodeI/O*](https://arxiv.org/abs/2502.07316), **11 February 2025** | “predict inputs/outputs given code and test cases” | **CONTEXT:** input/output reasoning training; external ground truth checks predictions. |
| [*PLSemanticsBench*](https://arxiv.org/abs/2510.03415), **3 October 2025** | “execution trace prediction” | **CONTEXT:** explicit evaluation of LLMs as formal-semantics interpreters. |
| [*Self-Programmed Execution for Language-Model Agents*](https://arxiv.org/abs/2605.06898), **7 May 2026** | “the same data is both model context and executable program” | **CONTEXT:** self-orchestration through Spell; not evidence of certified neural arithmetic execution. |

**Surviving S2 wording:** “A LoRA-adapted pretrained chat model generates candidate register programs and executes accepted programs through neural transitions whose correctness is established for every execution covered by a finite-state reduction.”

“Candidate” and “accepted” matter: an exact executor can execute an incorrect program perfectly.

**S3. KV eviction turns a decoder into a recurrent executor with a finite certificate**

| Source and date | Short verbatim quote | Grade and consequence |
|---|---|---|
| Xiao et al., [*StreamingLLM*](https://arxiv.org/html/2309.17453v1), **29 September 2023; ICLR 2024** | “positions within the cache rather than those in the original text” | **STATES** persistent initial KVs + rolling recent KVs + cache-relative positional treatment. **PARTIAL** for S3: stability/perplexity, not exact machine execution. |
| Zhang et al., [*H₂O*](https://arxiv.org/abs/2306.14048), **24 June 2023; NeurIPS 2023** | “dynamically retains a balance of recent and H₂ tokens” | **CONTEXT:** cache eviction with a theoretical optimization guarantee. That guarantee is not a semantic execution certificate. |
| Oren et al., [*Transformers are Multi-State RNNs* / TOVA](https://arxiv.org/abs/2401.06104), **11 January 2024; EMNLP 2024** | “converted into bounded multi-state RNNs” | **STATES** the decoder-to-recurrent-system interpretation through bounded KV storage. **PARTIAL**: no finite symbolic transition certificate. |
| Aghajohari et al., [*The Markovian Thinker* / Delethink](https://arxiv.org/abs/2510.06557), **8 October 2025; ICLR 2026** | “resets the context and reinitializes the prompt with a short carryover” | **STATES** bounded textual state and context resets for extended reasoning. **PARTIAL**: resource scaling and empirical reasoning results, not exact state tracking for every input. |
| Bulatov et al., [*Recurrent Memory Transformer*](https://arxiv.org/abs/2207.06881), **14 July 2022** | “adding special memory tokens to the input or output sequence” | **CONTEXT:** recurrent memory vectors, not a certified finite alphabet of symbolic states. |
| Wu et al., [*Memformer*](https://arxiv.org/abs/2010.06891), **14 October 2020** | “linear time complexity and constant memory space complexity” | **CONTEXT:** bounded recurrent memory, no exact interpreter certificate. |
| Munkhdalai et al., [*Infini-attention*](https://arxiv.org/abs/2404.07143), **10 April 2024** | “incorporates a compressive memory into the vanilla attention mechanism” | **CONTEXT:** compression and long-context processing, not exact discrete execution. |
| Behrouz et al., [*Titans*](https://arxiv.org/abs/2501.00663), **31 December 2024 submission; 2025 paper** | “learns to memorize historical context” | **CONTEXT:** adaptive neural memory, not exhaustive symbolic-state certification. |

The strongest combination objection is **StreamingLLM/TOVA/Delethink plus Cai/Schuurmans**. These already supply the recurrence/reset machinery and the finite-local-correctness proof strategy. Merely putting those concepts together is weak novelty.

The 2026 Lewandowski paper is especially close: its actual protocol forms each query from a fixed system prompt and the current local window, appends the generated symbols to an operational string, then advances the window. Its proof concerns those reconstructed local queries. It does **not** establish equivalence to retaining history-conditioned KVs across steps. [Protocol and proof](https://arxiv.org/html/2601.08061v2)

**Surviving S3 wording:** “For this precise cache implementation, we prove that all execution histories represented by the same certified local state induce the same transition behavior, reducing arbitrary-duration execution to a finite check.”

That history-independence statement—not eviction itself—is the potentially substantive contribution.

**S4. Judge semantically, then aggregate exactly using the same model’s certified arithmetic**

| Source and date | Short verbatim quote | Grade and consequence |
|---|---|---|
| Li et al., [*Chain of Code*](https://arxiv.org/abs/2312.04474), **7 December 2023; ICML 2024** | “counts the number of times it detects sarcasm in an essay” | **STATES** the motivating pattern: semantic judgments combined with precise programmatic computation. **PARTIAL**: ordinary code uses an external interpreter; the LM handles semantic operations. |
| Patel et al., [*LOTUS / Semantic Operators*](https://arxiv.org/html/2407.11418v1), **16 July 2024** | “sorting or aggregating records using natural language criteria” | **IMPLIES/PARTIAL:** composable semantic analytics is established. Its semantic aggregation is not synonymous with certified arithmetic. |
| Liu et al., [*Palimpzest*](https://arxiv.org/html/2405.14696v1), **23 May 2024** | “orchestrate large numbers of models, prompts, and data operations” | **IMPLIES/PARTIAL:** model judgments embedded in conventional analytical processing are established. No same-model arithmetic certificate. |
| Peng et al., [*Codified Finite-state Machines for Role-playing*](https://openreview.net/pdf?id=xSuDJTQ3Ew), **arXiv 5 February 2026; ICLR 2026; earlier OpenReview submission** | “executable transition function” | **IMPLIES/PARTIAL:** generated state-transition code invokes semantic binary-question helpers. It does not establish that transformer forward passes implement the transition logic exactly. |

I found no verified CFSM follow-up establishing the proposed certified neural executor. CFSM is relevant to semantic predicates plus structured state transitions; it is not a direct all-length execution result.

**Surviving S4 wording:** “Given the model’s semantic judgments as inputs, the same checkpoint computes their aggregation through exhaustively validated arithmetic primitives.”

The guarantee is **conditional on the judgments**. Exact counting cannot repair incorrect classifications, missing records, mistaken extraction, or a wrongly generated aggregation program.

**S5. Has the combination already been published or announced?**

**Not the full specified combination that I could verify. But the surrounding integration claim has already been announced.**

The most important additional sources are:

| Source and date | Short verbatim quote | Grade and consequence |
|---|---|---|
| Saldyt–Kambhampati, [*Algorithmic Language Models with Neurally Compiled Libraries*](https://arxiv.org/abs/2407.04899), **6 July 2024** | “memory, registers, basic operations, and adaptive recurrence” | **IMPLIES/PARTIAL:** explicitly combines an LLaMA-based architecture with an internal differentiable computer and compiled algorithm library. Arithmetic is supplied, not inherited and exhaustively certified. |
| Percepta/Tzamos, [*Can LLMs Be Computers?*](https://www.percepta.ai/blog/can-llms-be-computers), **11 March 2026**, followed by [*Constructing an LLM-Computer*](https://www.percepta.ai/blog/constructing-llm-computer), **25 March**, and the [official implementation](https://github.com/Percepta-Core/transformer-vm) | “weights are computed analytically” | **STATES** program execution inside transformer weights; **PARTIAL** for the whole. The released VM is constructed, not an inherited-arithmetic chat model fine-tuned with LoRA. Its hull-based attention mechanism differs from the proposed eviction policy. |
| [*Meridian*, public manuscript commit](https://huggingface.co/eastlondoner/nanochat-wasm-coprocessor/commit/956b2fe155cbe8dd53349a4714be81d87ec97d30), **11 April 2026** | “generates WASM bytecode as tokens and executes them within the model’s own forward pass” | **STATES**, as a public claim, model-generated code plus internal execution in a language-generating model. **PARTIAL**: a separately hand-compiled frozen coprocessor and trained bridges, not inherited arithmetic or a LoRA-only modification. |
| Percepta, [*Can LLMs Grow Their Own Capabilities?*](https://www.percepta.ai/blog/can-llms-grow-their-own-capabilities), **2 October 2026** | “we hand-constructed a Python interpreter inside Spotlight” | **STATES** an announced extension to internal Python execution and writable memory. **PARTIAL**: changed architecture and constructed interpreter; no evidence of this Qwen/LoRA/certificate combination. |

Meridian is easy to miss and materially changes the answer. Its manuscript describes internal bytecode generation, deterministic execution, and conversational responses. It also reports **95% arithmetic accuracy on its small evaluation**, with remaining errors attributed to program generation. That is precisely why executor correctness and question-answer correctness must be separated. I verified a public manuscript artifact, not peer-review acceptance or an independent reproduction. [Meridian manuscript](https://huggingface.co/eastlondoner/nanochat-wasm-coprocessor/commit/956b2fe155cbe8dd53349a4714be81d87ec97d30)

Percepta’s October language-modeling experiments and its constructed interpreter should likewise not be silently combined into evidence that one pretrained chat model already possesses both properties. Its [Spotlight report](https://www.percepta.ai/blog/spotlight-memory) presents separate architecture-training experiments.

The defensible combination distinction is therefore **the particular integration and proof boundary**: inherited primitives, a learned executor, a pinned cache implementation, and a valid finite certificate in one pretrained checkpoint. Qwen3-4B, approximately 18 opcodes, browser deployment, or a small adapter are implementation choices; none independently supplies a strong scientific novelty claim.

**The wording also contains correctness claims that cannot pass merely because no identical paper was found.**

These are my technical objections to the proposed statement:

1. **Eviction is not necessarily a reset.** Retained state-token KVs can contain information obtained from now-evicted tokens. Restarting position indices does not erase that information. A certificate indexed only by textual `(state, input)` is incomplete unless all reachable KV realizations are covered or their transition equivalence is proved.

2. **Unbounded digit-string registers make the state space unbounded.** You need a proved reduction to finite local digit/control observations. Checking 200 additions does not certify digit routing, copying, carry scheduling, instruction fetch, branching, termination, or serialization.

3. **Positive margins are not unconditionally necessary.** For target token \(y\),
   \[
   m=z_y-\max_{j\ne y}z_j>0
   \]
   is equivalent to a **unique** correct argmax. A deterministic tie-breaker can return \(y\) at \(m=0\). Moreover, a conservative certified lower bound can fail to be positive even when the true margin is positive. State precisely which predicate is necessary and sufficient.

4. **The certificate must match execution.** Fix the checkpoint, adapter status, tokenizer, prompts, decoding rule, positions, cache construction, precision, and runtime semantics. Fresh-prompt arithmetic checks do not automatically transfer into program-conditioned cached execution. Multi-token outputs require checking every decoding prefix, including termination.

5. **Exact execution is not exact natural-language problem solving.** Program synthesis, semantic judgments, and preservation of GSM8K/MMLU/perplexity are separate empirical obligations. Benchmark retention supports a bounded capability-preservation claim; it does not certify “remaining a normal chat model.”

**Final verdict: NARROW.** The following is the exact surviving sentence I would allow as a *candidate contribution claim*, contingent on the implementation and proof actually establishing it:

> “For a pinned Qwen3-4B checkpoint with a small LoRA adapter, we combine model-generated register programs, exhaustively validated pre-existing digit-arithmetic primitives, and a learned executor under a specified cache/reset protocol, proving that finite local-transition checks suffice for exact execution of accepted programs at arbitrary run lengths under stated memory assumptions, while evaluating program-synthesis accuracy and chat-capability retention separately.”

I would withhold “necessary-and-sufficient” until the tie semantics, reachable-state coverage, numerical certificate, and KV-history equivalence are explicit.

**Is this already known?** Mostly yes. A skeptical ML researcher should recognize the central story as a combination of established ideas: learned neural interpreters, finite verification yielding unrestricted execution, pretrained LLMs implementing universal rule systems, bounded-context recurrence, and semantic judgments combined with exact computation. There are even public systems claiming language generation alongside internally executed model-generated programs. What I did not find is your exact inherited-arithmetic, LoRA, cache-policy, and certification package. That could support a useful systems-and-verification contribution if the proof closes the actual deployment semantics. It does not support selling “an LLM becomes an exact computer and still chats” as the discovery.