# L5 prior art: tools, program-aided reasoning, neurosymbolic programs with LLM primitives, latent reasoning

Literature agent L5, 28 October 2026. Scope: claims C6 (Savant), C9 (reasoning with calls), C10 (planned: semantic-event
programs, a universal register interpreter, a certified standard library) and the framing "this is not a tool call".

**How every entry was verified.** Each arXiv entry was fetched live from the arXiv API on 2026-10-28 with
`L5_verify_arxiv.py` (an `id_list` query plus a check that the returned title matches the expected one); 185 records
matched. The raw records (title, full author list, first-version date, arXiv comment and journal_ref, abstract) are in
`L5_verified_records.json`, together with Semantic Scholar venue hints and DBLP keys. Venues below come from the arXiv
comment or journal_ref, from a DBLP conference key, or are marked "(S2 venue)" when only Semantic Scholar gives them.
DOIs were checked on Crossref; the two vendor sources were read from the vendor's own page or PDF. Every URL below was
accessed on 2026-10-28. For the closest papers (marked **[read]**) I read the method and results sections, not just the
abstract; the summaries are mine. Items I could not verify are listed at the end and are not used in the argument.

**Closeness scale.** 0 background; 1 related, cite if space; 2 overlaps a sub-claim, must cite and position; 3
pre-empts part of a claim as worded, must reword.

---

## 0. Verdict in one screen

- **C6.** I found no prior work in which a pretrained chat LLM writes a transition table, certifies every row with its
  own forward passes, and runs it under a KV-cache policy exactly at 4,096-digit addition and 10,000 events while keeping
  its language. But each ingredient has a named precedent, and three of them are close enough to force rewording:
  - **The certificate theorem.** Cai, Shin and Song (ICLR 2017) proved "provably perfect generalization" for a neural
    program executor by checking it on a finite verification set that covers every base case and reduction. Recursion
    bounds each call, and the paper says outright that an executor carrying hidden state across unboundedly many calls
    cannot be verified this way. That is Theorem P and the theorem pair in an older form.
  - **Exact long execution by an LLM's own steps.** MAKER (2025) finished a 1,048,575-step Towers of Hanoi run with zero
    errors. Each step was one LLM call that saw only the strategy and the current state, with voting.
  - **Step-wise execution with a state-only context.** CAEF (2024) fine-tuned LLaMA-3.1-8B to run arithmetic as a Turing
    machine, one generate call per transition. It reaches 98.6% at 100-digit addition, against 43.0% for GPT-4o.
- **C9.** The format is not new. "Reason in words, call code mid-thought, read the result, keep reasoning, several
  calls" ships in OpenAI's o-series (system card, April 2025: "The models use tools in their chains of thought") and in
  Claude's interleaved thinking. It is also a large academic line (ToRA, START, ReTool, CoRT, rStar2-Agent). Citing
  results by placeholder is Chain-of-Abstraction (y1, y2) and ReWOO. What is new is the callee: the same model's decoding,
  certified. The mandatory baseline is the same Qwen3-4B with a real Python interpreter (PAL/ToRA style) on the same
  composites, plus frontier models with their code tool switched on. On pure arithmetic both will also be exact.
- **C10.** The pattern "LLM judgments snapped to symbols, exact symbolic control on top" is established, always with
  the control run in code: Chain of Code's LMulator, Binder, COGEX, Codified Finite-State Machines (ICLR 2026), the
  TemporalGuard and SpecGuard monitors (2026), LOTUS semantic operators, Vieira, LLM-Symbolic Programs, and LLM plus ASP
  on bAbI, StepGame and CLUTRR. A universal interpreter inside a transformer exists in two forms: constructed (Looped
  Transformers as Programmable Computers, ICML 2023) and trained from scratch (Xu, Yang, Li and McAllester, April 2026:
  a 59.5M-parameter MicroPy interpreter, 100% on held-out programs whose traces run to 7,552 lines). "Certified once"
  is Cai et al.'s phrase almost word for word. What remains ours: control executed by the LLM's own pinned decoding,
  with a machine-checked necessary-and-sufficient per-row certificate.
- **Latent reasoning.** No latent or "system 2 without tokens" method claims exactness at length. The strongest
  length claims are modest extrapolations on parity and variable assignment (Thinking States, 2026) and on RASP-L tasks
  (looped transformers). None offers a certificate. These are context, not threats.

---

## 1. The five most dangerous papers

### 1. Cai, Shin and Song, "Making Neural Programming Architectures Generalize via Recursion" (ICLR 2017) **[read]**
URL: https://arxiv.org/abs/1704.06611 (arXiv comment "Published in ICLR 2017"; a secondary source reports it was one
of three ICLR 2017 best papers, not confirmed on iclr.cc).

- **What they did.** They added recursion to the Neural Programmer-Interpreter (NPI), so every call runs for a fixed
  number of steps however long the input is. They then built a verification set covering every base case and reduction
  rule (20,181 problems for grade-school addition) and ran the trained model on it once. Passing it is a proof of
  "provably perfect generalization": correct behaviour on all valid inputs of any length (section 4, appendix A.6).
  They state the converse intuition explicitly: the non-recursive NPI keeps an LSTM hidden state across a number of
  calls that grows with input length, so no finite test settles what it does on longer inputs.
- **Overlap.**
  - Theorem P (certify every reachable row, and the run equals the table's run at any length) is the same argument,
    with the bounded call made by a KV-cache policy instead of recursion.
  - The theorem pair (unpinned decoding has no finite certifying test suite; pinned decoding has one) restates their
    recursive versus non-recursive contrast as a theorem.
  - C10's "universal interpreter certified once" matches their "this verification phase only needs to be performed once
    after training".
- **Reword.**
  - Present Theorem P as "the pretrained-LLM, KV-cache form of the verification argument of Cai et al. (2017)".
  - The new parts are: the converse (necessity) and the impossibility half, both proved in Lean; certification per
    program on an off-the-shelf LLM rather than per model on a purpose-built executor; and the bitwise tick-to-row
    equality measured on real hardware.
  - Never write that finite verification implying correctness at any length is new.
- **Comparison it suggests.** None experimental. Cite it in the statement of Theorem P and in the "why the clock"
  paragraph: their recursion and our pinning do the same job, bounding what one step can see.

### 2. Meyerson et al., "Solving a Million-Step LLM Task with Zero Errors" (MAKER, arXiv Nov 2025) **[read]**
URL: https://arxiv.org/abs/2511.09030. Companion: Lai et al., CAEF (https://arxiv.org/abs/2410.07896) **[read]**.

- **What MAKER did.**
  - It split 20-disk Towers of Hanoi into 1,048,575 single-move LLM calls. Each call saw only the given strategy, the
    current disk configuration and the previous move, and returned the move and the next state.
  - A "first-to-ahead-by-k" vote plus red-flagging (discarding over-long or malformed replies) gave zero errors over the
    whole run with gpt-4.1-mini, whose per-step error was about 0.0022, so k = 3.
  - The cost is Θ(s ln s) in the number of steps s; the authors estimate about $3.5K for the full run at a 0.95 success
    target. The strategy is given to the model, not discovered.
- **What CAEF did.**
  - It fine-tuned LLaMA-3.1-8B with LoRA "executors" that each perform one Turing-machine transition per generate call,
    on a text state (heads, carry, output tape). An "aligner" maps the question to the initial state.
  - Results: 98.6% at 100-digit addition, against 43.0% for GPT-4o; 97–100% across seven operators. Testing stops at
    100 digits, inside the training length range. No exactness claim.
- **Overlap.**
  - Both run a model-executed state machine one step at a time, with a context that holds only the current state.
    That is the essence of the clock.
  - MAKER pre-empts the headline "exact at very long lengths from an LLM's own steps": 1M steps with zero errors,
    against our 10,000 events.
  - CAEF pre-empts "fine-tune an LLM to run arithmetic step by step in its own decoding".
- **Reword.**
  - Say "certified" where MAKER says "voted", and quantify the difference. MAKER's guarantee is statistical, needs
    several samples per step and grows as s ln s. Ours is deterministic for certified rows, costs one forward pass per
    distinct row, and adds nothing per step.
  - Avoid "exact at any length" without "for certified programs, deterministic decoding, on the tested host".
  - Do not imply ours is the longest exact LLM-executed run: MAKER's is longer.
- **Comparisons they suggest.**
  1. A MAKER-style arm. Measure the per-step error ε of the uncertified base Qwen3-4B under the same clock. Report the
     k_min and the sample cost MAKER's formula needs to reach our exactness at 4,096 digits and 10,000 events, against
     the one-off certification cost.
  2. CAEF's 5/10/50/100-digit addition grid as a direct comparison row; we exceed it in length and exactness.

### 3. Gao et al., "PAL: Program-aided Language Models" (ICML 2023, S2 venue), and its interleaved descendants **[read]**
URLs:
- PAL: https://arxiv.org/abs/2211.10435
- OpenAI o3 and o4-mini System Card (16 April 2025): https://cdn.openai.com/pdf/2221c875-02dc-4789-800b-e7758f3722c1/o3-and-o4-mini-system-card.pdf
- Anthropic interleaved thinking: https://platform.claude.com/docs/en/build-with-claude/extended-thinking
- START: https://arxiv.org/abs/2503.04625 **[read]**
- ReTool: https://arxiv.org/abs/2504.11536

- **What they did.**
  - PAL has the LLM write a Python program and hands execution to the interpreter. It introduced **GSM-HARD**: GSM8K
    with one number per question replaced by an integer of up to 7 digits.
  - On GSM-HARD, CoT falls from 65.6% to 20.1% while PAL stays at 61.5%. In 16 of 25 inspected cases CoT wrote nearly
    the same reasoning for the small and large versions, so arithmetic, not reasoning, was the failure.
  - The interleaved descendants move the call inside long reasoning. The o3 system card says the models use Python
    "during their thought process". Claude's interleaved thinking "lets Claude think between tool calls ... reasoning
    about each tool result before determining what to do next" (beta header `interleaved-thinking-2025-05-14`).
  - START (QwQ-32B) inserts Python calls mid-CoT, raising AIME24 from 50.0 to 66.7. ReTool and ToRL learn when to call
    by RL.
- **Overlap.** C9's format and its theorem C (the execution term is zero) are PAL's informal argument: "any complex
  computation can be performed accurately given the correctly generated program". A reviewer will say C9 is
  tool-integrated reasoning with the tool replaced.
- **Reword.**
  - Drop any implication that reasoning-with-calls, multiple calls or citing results is new.
  - State the novelty as the callee: "the call's executor is the model's own decoding under a pinned context, with a
    per-row certificate; no interpreter, sandbox or second model exists at inference".
  - Say plainly that a Python tool is also exact on these computations.
- **Baselines this forces.**
  1. The same Qwen3-4B base with a Python interpreter (PAL/ToRA prompt, or a short TIR fine-tune) on the same composite
     templates.
  2. Frontier models with their code tool on, as well as off.
  3. GSM-HARD itself, plus a "GSM-Huge" variant with 100–4,096-digit numbers.

  If Savant matches (1) on accuracy, the paper's argument is architectural (self-contained, certified, runs in a
  browser with no runtime), not an accuracy win. Say so before a reviewer does.

### 4. Li et al., "Chain of Code: Reasoning with a Language Model-Augmented Code Emulator" (ICML 2024 oral) **[read]**
URL: https://arxiv.org/abs/2312.04474.

- **What they did.**
  - The LM writes code or pseudocode. Python runs each line; when a line fails (for example an undefined
    `is_sarcastic(...)` or `is_fruit(...)`), the "LMulator" is given the program, the line and the state history, and
    writes the next program state back into the interpreter.
  - On BIG-Bench Hard (text-davinci-003) it scores 84, against 72 for CoT, 48 for Python only and 57 for LM-only
    emulation. On algorithmic tasks it gets 95 against 71 for CoT; on NLP tasks it ties CoT at 74.
  - Multi-Step Arithmetic gets 100 with Python and 1 with LM-only emulation.
- **Overlap.**
  - C10's semantic events are CoC's LMulated lines: the LLM's judgment enters a program as a value, and exact control
    runs on it.
  - C9's "the model writes a program mid-thought and the result returns to context" is CoC's interleave.
  - CoC's LM-only ablation is exactly the uncertified "LLM executes its own program" baseline, and it fails on
    algorithmic tasks. This is the failure our clock removes.
- **Reword.** For C10, say "as in Chain of Code, semantic sub-steps are judged by the LM. Unlike Chain of Code, the
  exact steps are also run by the LM, under a certified pinned context, rather than by Python."
- **Comparison it suggests.** Run Chain of Code's three-way ablation on our composites and semantic-event tasks:
  - interleave (Python plus LM);
  - LM-only;
  - Savant (LM judgments plus in-model certified control).

  Then report each of theorem C's error terms. Expect Savant ≈ interleave on accuracy and ≫ LM-only.

### 5. Peng, Hou, Zhou and Shang, "Codified Finite-State Machines for Role-playing" (arXiv Feb 2026; ICLR 2026 per the OpenReview PDF header seen in search, not opened) **[read]**
URL: https://arxiv.org/abs/2602.05905. Companions:
- TemporalGuard: Cohen, Havelund, Omer and Peled, LNCS *AI Verification* 2026, https://doi.org/10.1007/978-3-032-32357-6_7
- SpecGuard: https://arxiv.org/abs/2610.36258 **[read]**

- **What CFSM did.**
  - An LLM (claude-4.0-sonnet) reads a character profile, extracts a finite state set, and writes a transition function
    `get_next_state(state, scene, action)` as code.
  - Each condition in that code is a semantic yes/no predicate, `binary_question(text, question)`, answered by an LLM or
    a distilled classifier. A probabilistic variant (CPFSM) weights transitions by the classifier's log-probabilities.
  - On three synthetic FSMs (Mario power-ups and others) with path lengths 1–10, CFSM is 100% accurate while gpt-4.1 and
    gpt-4.1-mini, prompted directly, degrade with length. CoT helps but costs about 25× CFSM's forward time.
- **What the monitors did.**
  - TemporalGuard grounds each conversation message into atomic propositions (embedding, NLI, or zero- and few-shot LLM
    classification, per the LLMrv repository) and monitors past-time LTL over them.
  - SpecGuard compiles LTLf specifications into symbolic DFAs over a fixed 15-proposition contract. It states that its
    guarantees "do not assume error-free natural-language AP activation".
- **Overlap.**
  - C10's "programs whose events are the LLM's own semantic judgments; each sentence snapped to a symbol; certified
    control tracks the exact state" is CFSM's and TemporalGuard's design, except that their control runs in code.
  - CFSM also pre-empts C6's "writes a transition table from a plain-language description".
  - SpecGuard draws our own distinction between "certified" and "right": the guarantee covers the automaton, not the
    grounding.
- **Reword.**
  - Present C10's novelty as moving the control into the model's own certified decoding, plus the error decomposition
    (snap error versus zero control error).
  - Cite CFSM for "LLM writes the FSM, LLM judges the guards".
  - Cite SpecGuard and TemporalGuard for "guarantees are conditional on grounding".
- **Comparisons they suggest.**
  - Use CFSM's synthetic FSM benchmark at path lengths 10 → 10,000 as a C10 benchmark, with CFSM (Python control, same
    Qwen3-4B as predicate) as the baseline.
  - Expect equal accuracy wherever the snaps are equal; that equality is itself the evidence that control error is zero.

**Runners-up, in order:**
- Xu et al. 2026, *Training Transformers as a Universal Computer* (C10 interpreter).
- Yang et al., PENCIL, ICML 2025 (the clock as a context-reduction policy).
- Back de Luca and Fountoulakis 2026, *Certification from Examples is Hard* (the theorem pair).
- Guo, Wu and Yiu 2026, *The Deterministic Horizon* (C9 framing: "tool delegation becomes necessary").
- Weir et al., COGEX, NeurIPS 2024, and Chae et al., Think-and-Execute, EMNLP 2024 (LM-emulated programs).
- Gao et al. 2024, Chain-of-Abstraction (C9 citing by placeholder).

---

## 2. Annotated list

Format: citation; URL (accessed 2026-10-28); what it does; **closeness** and the claim it touches; **for us**.

### A. Program-aided reasoning and tool-integrated reasoning (TIR)

**A1.** Gao, Madaan, Zhou, Alon, Liu, Yang, Callan, Neubig. *PAL: Program-aided Language Models.* ICML 2023 (S2
venue). https://arxiv.org/abs/2211.10435 **[read: GSM-HARD sections]**. The LLM writes Python and the interpreter
executes it. It introduced GSM-HARD, where CoT collapses (65.6 → 20.1%) and PAL holds (61.5%). **3, C9.** **For us:**
the root of the C9 format and the obligatory baseline. GSM-HARD, scaled up, is the cleanest composite benchmark for C9.

**A2.** Chen, Ma, Wang, Cohen. *Program of Thoughts Prompting: Disentangling Computation from Reasoning for Numerical
Reasoning Tasks.* TMLR 2023 (arXiv comment). https://arxiv.org/abs/2211.12588. It separates reasoning (written as a
program) from computation (an external interpreter) and gains about 12% over CoT across eight numerical datasets.
**2, C9.** **For us:** cite with PAL. Our "computation by the model itself, certified" is the other side of their
disentangling.

**A3.** Schick et al. *Toolformer: Language Models Can Teach Themselves to Use Tools.* NeurIPS 2023 (S2 venue).
https://arxiv.org/abs/2302.04761. A self-supervised model learns which APIs to call, including a calculator, and how to
use their results. **1, C9.** **For us:** the precedent for "the model decides when to compute". REASON's
`<program>`-opening probability is the same decision.

**A4.** Parisi, Zhao, Fiedel. *TALM: Tool Augmented Language Models.* arXiv 2022. https://arxiv.org/abs/2205.12255.
Text-only tool interfaces bootstrapped by self-play. **1, C9.** **For us:** background.

**A5.** Patil, Zhang, Wang, Gonzalez. *Gorilla: Large Language Model Connected with Massive APIs.* NeurIPS 2024 (S2
venue). https://arxiv.org/abs/2305.15334. API-call generation with retrieval. **0, C9.** **For us:** background only.

**A6.** Karpas et al. *MRKL Systems.* arXiv 2022. https://arxiv.org/abs/2205.00445. A neuro-symbolic architecture that
routes queries from an LLM to discrete reasoning modules such as a calculator. **1, C9 framing.** **For us:** the
"modular, neuro-symbolic" framing that our "not a tool call" argument opposes.

**A7.** Yao et al. *ReAct: Synergizing Reasoning and Acting in Language Models.* ICLR 2023 (DBLP).
https://arxiv.org/abs/2210.03629. Interleaves reasoning traces with actions. **1, C9.** **For us:** the generic
interleaving template; cite once.

**A8.** Gou et al. *ToRA: A Tool-Integrated Reasoning Agent for Mathematical Problem Solving.* ICLR 2024 (arXiv
comment). https://arxiv.org/abs/2309.17452. Trains models on interleaved natural-language reasoning and tool-call
trajectories. **2, C9.** **For us:** the closest trained open-model form of reasoning with calls; a TIR baseline recipe.

**A9.** Zhou et al. *Solving Challenging Math Word Problems Using GPT-4 Code Interpreter with Code-based
Self-Verification.* ICLR 2024 (DBLP). https://arxiv.org/abs/2308.07921. Attributes GPT-4 Code Interpreter's gains to
generating and running code, then checking the outputs; adds code-based self-verification. **1, C9.** **For us:**
frontier tool use was already understood in 2023 as "compute, then check".

**A10.** Wang et al. *Executable Code Actions Elicit Better LLM Agents* (CodeAct). ICML 2024 (arXiv comment).
https://arxiv.org/abs/2402.01030. Python code as the action space of an agent, with multi-turn execution. **1, C9.**
**For us:** background.

**A11.** Qin et al. *ToolLLM.* ICLR 2024 (S2 venue). https://arxiv.org/abs/2307.16789. Large-scale API tool use.
**0.** **For us:** background.

**A12.** Cai, Wang, Ma, Chen, Zhou. *Large Language Models as Tool Makers.* ICLR 2024 (S2 venue).
https://arxiv.org/abs/2305.17126. A strong model writes reusable Python tools that a weaker model then calls. **1,
C10 library.** **For us:** prior art for "a library of programs the model writes once and reuses".

**A13.** Kadlčík et al. *Calc-X and Calcformers.* EMNLP 2023 (arXiv comment). https://arxiv.org/abs/2305.15017.
Arithmetic chain-of-thought datasets with calculator calls inside the chain. **1, C9.** **For us:** the "calculator
inside the chain" data format.

**A14.** Gao et al. *Efficient Tool Use with Chain-of-Abstraction Reasoning.* COLING 2025 (DBLP).
https://arxiv.org/abs/2401.17464. Models write reasoning with abstract placeholders ("[20 + 35 = y1]") that tools fill
in afterwards. **2, C9 ("results can be cited by number").** **For us:** citing a call's result by a symbol is CoA's
device; cite it there.

**A15.** Xu et al. *ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models.* arXiv 2023.
https://arxiv.org/abs/2305.18323. Plans with placeholders for tool evidence, then executes. **1, C9.** **For us:** cite
with CoA.

**A16.** Kim et al. *An LLM Compiler for Parallel Function Calling.* ICML 2024 (arXiv comment).
https://arxiv.org/abs/2312.04511. Plans a dependency graph of function calls and executes them in parallel. **1, C9.**
**For us:** background for multiple dependent calls.

**A17.** Li et al. *START: Self-taught Reasoner with Tools.* EMNLP 2025 (DBLP). https://arxiv.org/abs/2503.04625
**[read]**. Hints such as "Wait, maybe using Python here is a good idea" insert Python calls into QwQ-32B's long CoT,
followed by rejection fine-tuning. AIME24 rises from 50.0 to 66.7. **2, C9.** **For us:** the "call mid-thought" format
on an open reasoning model. Gains come from the tool, not the data: QwQ-RFT without tools stays near QwQ.

**A18.** Feng et al. *ReTool: Reinforcement Learning for Strategic Tool Use in LLMs.* arXiv 2025.
https://arxiv.org/abs/2504.11536. RL teaches when to interleave real-time code execution into long reasoning. **2,
C9.** **For us:** an RL counterpart to REASON's learned decision to compute.

**A19.** Li, Zou, Liu. *ToRL: Scaling Tool-Integrated RL.* arXiv 2025. https://arxiv.org/abs/2503.23383. RL from base
models discovers tool use (43.3% AIME24 at 7B). **1, C9.**

**A20.** Li et al. *CoRT: Code-integrated Reasoning within Thinking.* arXiv 2025. https://arxiv.org/abs/2506.09820.
Hint-engineered data for code calls inside thinking, from 1.5B to 32B. **2, C9.** **For us:** the closest data recipe to
Savant's "program inside thinking".

**A21.** Shang et al. *rStar2-Agent: Agentic Reasoning Technical Report.* arXiv 2025. https://arxiv.org/abs/2508.20722.
A 14B model trained by agentic RL to think before Python calls and reflect on their feedback. **1, C9.**

**A22.** Xue et al. *SimpleTIR.* arXiv 2025. https://arxiv.org/abs/2509.02479. Stabilises multi-turn TIR RL. **1.**

**A23.** Mai et al. *Agent RL Scaling Law* (ZeroTIR). arXiv 2025. https://arxiv.org/abs/2505.07773. Spontaneous code
execution emerges under outcome RL. **1.**

**A24.** Lin, Xu. *Understanding Tool-Integrated Reasoning.* arXiv 2025. https://arxiv.org/abs/2508.19201. Gives a
formal argument that tools strictly expand a model's empirical and feasible support beyond pure text. **2, C9 framing.**
**For us:** a theoretical opponent. Our clock expands what pure decoding can do without any external tool, so state how
this sits with their result: the pinned context is an inference-time policy, not a tool.

**A25.** Chen et al. *RL for Tool-Integrated Interleaved Thinking towards Cross-Domain Generalization.* arXiv 2025.
https://arxiv.org/abs/2510.11184. **1.**

**A26.** Fatahi Bayat, Pezeshkpour, Hruschka. *From Proof to Program: Characterizing Tool-Induced Reasoning
Hallucinations in LLMs.* ACL (S2 venue). https://arxiv.org/abs/2511.10899. With a code interpreter, models treat tool
outputs as substitutes for reasoning ("Tool-Induced Myopia"). Final answers improve while justification degrades.
**2, C9.** **For us:** theorem C's third term (the reasoning glue) is exactly where this failure lives. Measure and
report it separately; it pre-empts any claim that certified calls make the whole answer trustworthy.

**A27.** Wu et al. *Agentic Reasoning.* ACL 2025 (arXiv comment). https://arxiv.org/abs/2502.04644. Agents with web
search, code and memory tools. **1.**

**A28.** OpenAI. *OpenAI o3 and o4-mini System Card.* 16 April 2025.
https://cdn.openai.com/pdf/2221c875-02dc-4789-800b-e7758f3722c1/o3-and-o4-mini-system-card.pdf. "The models use tools
in their chains of thought ... using Python to analyze data during their thought process." **3, C9.** **For us:** the
C9 format is a frontier product feature. The frontier comparison must include tools-on.

**A29.** Anthropic. *Extended thinking: interleaved thinking with tool use* (Claude Platform docs).
https://platform.claude.com/docs/en/build-with-claude/extended-thinking. Interleaved thinking lets Claude reason between
tool calls within one turn (Claude 4 models; beta header `interleaved-thinking-2025-05-14`; automatic under adaptive
thinking). **3, C9.** **For us:** as A28.

**A30.** Chen et al. *Steering Large Language Models between Code Execution and Textual Reasoning.* ICLR 2025 (journal
ref). https://arxiv.org/abs/2410.03524. No single method decides well when to code and when to reason in text; forcing
code does not reliably beat text. **2, C9.** **For us:** the "when to compute" decision is a known open problem; it
supports REASON's measurement of when `<program>` opens.

**A31.** Chen et al. *CodeSteer.* ICML 2025 (journal ref). https://arxiv.org/abs/2502.04350. A small model steers a
larger one between code and text. **1, C9.**

**A32.** Guo, Wu, Yiu. *The Deterministic Horizon: When Extended Reasoning Fails and Tool Delegation Becomes
Necessary.* arXiv 2026 (v2 Aug 2026). https://arxiv.org/abs/2606.00376 **[read]**. Already in `refs.bib`.
- Twelve models, including o3, o3-mini, Claude Sonnet and Opus 4.5, DeepSeek-R1 and Gemini, on eight deterministic
  state-tracking domains.
- Unaided CoT crosses 50% at a depth d* between 19 and 31.
- With an exact BFS-solver tool, models reach 76–94% against 17–42% for CoT on PermutationProbe at depth > 20; the
  residual tool errors are formatting and transcription.
- Fine-tuning Llama-3.1-8B on optimal traces gains only +0.9 pp.

**2–3, C9 framing.** **For us:** their conclusion, "delegate deterministic sub-problems to verified solvers", is our
claim with the solver moved inside the model. Their 6–24% interface error is the "quote" term of our theorem C. Use
their task families as a C9 benchmark.

**A33.** Yu. *Evaluating Prompting and Execution-Based Methods for Deterministic Computation in LLMs.* arXiv 2026.
https://arxiv.org/abs/2605.03227. Program-of-thought reaches perfect accuracy on binary counting and arithmetic
evaluation where CoT and Least-to-Most fail. **1, C9.** **For us:** more evidence that the Python-tool baseline is
exact on our tasks.

**A34.** Tang et al. *Empirical Computation: Prompting versus Programming.* ASE 2026 NIER (arXiv comment).
https://arxiv.org/abs/2503.10954. A position paper framing LLM-solved computation as "empirical computation". **0.**

**A35.** Sun et al. *Executing as You Generate: Hiding Execution Latency in LLM Code Interpreters.* arXiv 2026.
https://arxiv.org/abs/2604.00491. Overlaps interpreter execution with generation. **0.**

**A36.** Xu et al. *TInR: Exploring Tool-Internalized Reasoning in Large Language Models.* ACL 2026 (arXiv comment).
https://arxiv.org/abs/2604.10788 **[read]**. It internalises tool *knowledge* (documentation, call formats) into special
tokens. The tools still run externally; no computation is internalised. **1, C9 (a name collision).** **For us:** if we
say "internalised execution", distinguish it from TInR in one clause.

**A37.** O'Connor. *Self-Programmed Execution for Language-Model Agents.* NeurIPS 2026 (arXiv comment).
https://arxiv.org/abs/2605.06898. The model's completion is itself the orchestrator program (in a Lisp, "Spell") whose
primitives include model calls; an external harness evaluates it. **1–2, C9/C10.** **For us:** "the model writes the
program that drives its own calls" with an external evaluator; ours inverts this (no evaluator, the model evaluates).

### B. LLMs as emulators and executors of code

**B1.** Zaremba, Sutskever. *Learning to Execute.* arXiv 2014. https://arxiv.org/abs/1410.4615. LSTMs trained to output
the results of short programs. **1.** **For us:** lineage.

**B2.** Nye et al. *Show Your Work: Scratchpads for Intermediate Computation with Language Models.* arXiv 2021.
https://arxiv.org/abs/2112.00114. Emitting intermediate steps lets transformers do long addition and execute programs.
**2, C6.** **For us:** the token-based baseline for "LLM executes a program". Our pinned clock is a scratchpad whose
past is evicted.

**B3.** Zhou et al. *Teaching Algorithmic Reasoning via In-context Learning.* arXiv 2022.
https://arxiv.org/abs/2211.09066. Algorithmic prompting improves long parity, addition and multiplication. **1, C6.**

**B4.** Liu et al. *Code Execution with Pre-trained Language Models.* Findings of ACL 2023 (arXiv comment).
https://arxiv.org/abs/2305.05383. **1.**

**B5.** Gu et al. *CRUXEval: A Benchmark for Code Reasoning, Understanding and Execution.* ICML 2024 (DBLP).
https://arxiv.org/abs/2401.03065. On 3–13-line Python functions, GPT-4 with CoT reaches 81% on output prediction.
**1, C6.** **For us:** uncertified LLM execution is unreliable even on short code; a contrast row.

**B6.** La Malfa et al. *Code Simulation Challenges for Large Language Models.* arXiv 2024.
https://arxiv.org/abs/2401.09074. Simulation fidelity falls with a routine's computational complexity and relies on
pattern recognition and memorisation. **1–2, C6.** **For us:** motivation; cite in the "plain decoding drifts"
paragraph.

**B7.** Ni et al. *NExT: Teaching Large Language Models to Reason about Code Execution.* ICML 2024 (S2 venue).
https://arxiv.org/abs/2404.14662. **1.**

**B8.** Ding et al. *SemCoder.* NeurIPS 2024 (arXiv comment). https://arxiv.org/abs/2406.01006. **1.**

**B9.** Zheng et al. *Executing Natural Language-Described Algorithms with Large Language Models: An Investigation.*
LREC-COLING 2024 (arXiv comment). https://arxiv.org/abs/2403.00795. GPT-4 executes 30 textbook algorithms described in
natural language, "as long as no heavy numeric computation is involved". **1–2, C10.** **For us:** "LLM as interpreter
of natural-language programs" is established; its failure is numerics at length, which is what certification fixes.

**B10.** Chae et al. *Language Models as Compilers: Simulating Pseudocode Execution Improves Algorithmic Reasoning in
Language Models* (Think-and-Execute). EMNLP 2024 (S2 venue). https://arxiv.org/abs/2404.02575. The LM first writes
task-level pseudocode once ("Think"), then simulates its execution on each instance ("Execute"). **2, C9/C10.** **For
us:** "write a task-level program once, run it per instance inside the LM" pre-dates us, uncertified. It is also the
closest precedent for a "standard library" reused across instances.

**B11.** Weir, Khalifa, Qiu, Weller, Clark. *Learning to Reason via Program Generation, Emulation, and Search* (COGEX).
NeurIPS 2024 (arXiv comment). https://arxiv.org/abs/2405.16337 **[read]**. Models write Python with *undefined* leaf
functions (for example `identify_ending()`). No interpreter runs; the LM emulates the whole execution, including the
leaves. The authors note that the emulated outputs can be inconsistent with the code, and say an interpreter is
preferable for precise algorithmic tasks. **2, C9/C10.** **For us:** the uncertified, all-in-model ancestor of C10.
Their caveat about inconsistent emulation is precisely what the certificate addresses.

**B12.** Li et al. *Chain of Code.* ICML 2024 oral. https://arxiv.org/abs/2312.04474 **[read]**. See section 1, item
4. **3, C9/C10.**

**B13.** Zhang et al. *Natural Language Embedded Programs for Hybrid Language Symbolic Reasoning.* NAACL 2024 (arXiv
comment). https://arxiv.org/abs/2309.10814. Python programs over natural-language data structures, run by an
interpreter. **1–2, C10.**

**B14.** Li et al. *CodeI/O: Condensing Reasoning Patterns via Code Input-Output Prediction.* ICML 2025 (arXiv
comment). https://arxiv.org/abs/2502.07316. Training to predict code inputs and outputs in natural-language CoT
improves general reasoning. **1.**

**B15.** Chen et al. *Chain of Execution Supervision Promotes General Reasoning in Large Language Models* (TracePile).
NeurIPS 2025 (journal ref). https://arxiv.org/abs/2510.23629. Turns 2.6M code executions into step-by-step
rationales. **1.**

**B16.** FAIR CodeGen team. *CWM: An Open-Weights LLM for Research on Code Generation with World Models.* arXiv 2025.
https://arxiv.org/abs/2510.02387. A 32B model mid-trained on Python interpreter and Docker trajectories, so that it
predicts execution state. **1–2, C6.** **For us:** the large-scale "LLM learns to execute" effort. It has no exactness
at length and no certificate.

**B17.** Rahmani. *Debugging code world models.* arXiv 2026. https://arxiv.org/abs/2602.07672. In a permutation-tracking
benchmark, long-horizon failures of a code world model come mostly from wrong action generation. Given ground-truth
actions, a transformer propagates state accurately over long horizons. **2, C6.** **For us:** independent support for
our decomposition, in which the transition is the easy part and the program or quote is the risk (theorem C).

**B18.** Maimon et al. *Self-Execution Simulation Improves Coding Models.* arXiv 2026.
https://arxiv.org/abs/2604.03253. SFT on natural-language execution traces plus RLVR, used for self-verification of
candidate solutions. **1.**

**B19.** Bayer et al. *Teaching LLMs Program Semantics via Symbolic Execution Traces.* arXiv 2026.
https://arxiv.org/abs/2605.06184. Violation detection degrades sharply with program length. **1.**

**B20.** Hasanov et al. *The Path Not Taken: Duality in Reasoning about Program Execution.* ACL 2026 (DBLP).
https://arxiv.org/abs/2604.20917. **0.**

**B21.** Lai et al. *Executing Arithmetic: Fine-Tuning Large Language Models as Turing Machines* (CAEF). arXiv 2024.
https://arxiv.org/abs/2410.07896 **[read]**. See section 1, item 2. They note that each step needs a fresh
`generate` call and that the KV cache cannot be reused across steps. Their stated failure mode is repeated digit
patterns ("999…"). **3, C6.** **For us:** the closest "fine-tuned LLM runs arithmetic as a state machine". Compare
directly; also test our tables on their failure inputs (long runs of 9s and repeated blocks).

**B22.** Weng et al. *Mastering Symbolic Operations: Augmenting Language Models with Compiled Neural Networks* (Neural
Comprehension). ICLR 2024 (arXiv comment). https://arxiv.org/abs/2304.01665 **[read]**. Gates compiled (Tracr-style)
networks into the LM's generation, token by token, for parity, reverse, addition and subtraction. It claims no length
degradation and "no additional tools". **2, C6 ("not a tool call").** **For us:** a precedent for exact symbolic
operations *inside* the network. Theirs are hand-compiled side modules (their AutoCoNN failed on addition, 0/20);
ours use the LLM's own weights. Cite for the framing.

**B23.** Dietz, Klakow. *IGC: Integrating a Gated Calculator into an LLM to Solve Arithmetic Tasks Reliably and
Efficiently.* arXiv 2025. https://arxiv.org/abs/2501.00684. An exact calculator module, emulated with GPU tensor
operations inside the forward pass, with no intermediate tokens and "no external tools". It is state of the art on
BIG-bench Arithmetic. **2, C6 framing.** **For us:** shows that "inside the forward pass" does not by itself mean "the
model computes". Our distinction ("the clock computes nothing about the state; every transition is the LLM's own
lookup") must be stated sharply against IGC.

**B24.** Xu, Li, Mei, Zhang. *AIOS Compiler: LLM as Interpreter for Natural Language Programming and Flow Programming
of AI Agents* (CoRE). arXiv 2024. https://arxiv.org/abs/2405.06907. An LLM interprets structured natural-language
programs step by step, with external memory and tools. **1–2, C10.** **For us:** "LLM as interpreter" as a phrase is
taken; use "certified executor".

**B25.** Gandhi et al. *Natural Language Commanding via Program Synthesis* ("Semantic Interpreter"). arXiv 2023.
https://arxiv.org/abs/2306.03460. Synthesises Office DSL programs. **0 (a name collision only).**

**B26.** Cohen, Cohen. *Watch Your Steps: Observable and Modular Chains of Thought* (Program Trace Prompting). arXiv
2024. https://arxiv.org/abs/2409.15359. Wraps CoT steps in Python-like named steps so they can be checked. **1, C9.**

**B27.** Holzer et al. *TempoBench.* arXiv 2025. https://arxiv.org/abs/2510.27544. Formally verifiable problems built
from synthesised Mealy machines; LLMs fall back on brute-force forward simulation. **1, C6.** **For us:** a source of
Mealy-machine instances with certificates.

### C. Bounded-context execution, neural interpreters, universal computation in transformers

**C1.** Graves, Wayne, Danihelka. *Neural Turing Machines.* arXiv 2014. https://arxiv.org/abs/1410.5401. **1.**

**C2.** Reed, de Freitas. *Neural Programmer-Interpreters.* ICLR 2016 (S2 venue). https://arxiv.org/abs/1511.06279. A
recurrent core with a program memory learns to compose and execute programs. **2, C10 (universal interpreter).**
**For us:** the original "one learned executor, many programs" model; cite with Cai et al.

**C3.** Cai, Shin, Song. *Making Neural Programming Architectures Generalize via Recursion.* ICLR 2017.
https://arxiv.org/abs/1704.06611 **[read]**. See section 1, item 1. **3, C6 (Theorem P, theorem pair), C10 ("certified
once").**

**C4.** Weiss, Goldberg, Yahav. *Thinking Like Transformers* (RASP). ICML 2021. https://arxiv.org/abs/2106.06981. **1.**

**C5.** Lindner et al. *Tracr: Compiled Transformers as a Laboratory for Interpretability.* NeurIPS 2023 (arXiv
comment). https://arxiv.org/abs/2301.05062. Compiles RASP programs into transformer weights. **1–2, C10 ("built-in
N\*").** **For us:** if the next model builds a table head in by construction (INSIGHTS N\*), Tracr is the method to
cite.

**C6.** Friedman, Wettig, Chen. *Learning Transformer Programs.* NeurIPS 2023 oral (arXiv comment).
https://arxiv.org/abs/2306.01128. **1.**

**C7.** Giannou et al. *Looped Transformers as Programmable Computers.* ICML 2023 (PMLR 202).
https://arxiv.org/abs/2301.13196. A fixed 13-layer transformer, looped, emulates a small instruction-set computer whose
program sits in the input. **2, C10 (a universal register interpreter).** **For us:** a universal interpreter in a
transformer exists by construction. Ours would be learned inside a pretrained LLM and certified.

**C8.** Fan et al. *Looped Transformers for Length Generalization.* ICLR 2025 (arXiv comment).
https://arxiv.org/abs/2409.15647. Looping a RASP-L step with adaptive depth gives strong length generalisation from
scratch. **1–2, C6.**

**C9.** Yang, Srebro, McAllester, Li. *PENCIL: Long Thoughts with Short Memory.* ICML 2025 (arXiv comment).
https://arxiv.org/abs/2503.14337 **[read]**.
- A reduction rule `C [CALL] T [SEP] A [RETURN] ⇒ C A` erases finished sub-computations, so context scales with space,
  not time.
- Theorem: a fixed transformer simulates any T-step, S-space Turing machine in O(T) tokens with O(S) context.
- On SAT at n = 10, CoT falls to 50% while PENCIL stays at 100%; on the 5×5 Einstein puzzle, PENCIL reaches 97% against
  25% for CoT.
- After a reduction the KV cache must be recomputed.

**2–3, C6 (the clock).** **For us:** the closest precedent for "the clock is a context policy that evicts finished work,
which makes long exact computation possible". Cite it as the family the clock belongs to. Our differences are a fixed,
model-independent eviction of each block, with Π as a sink and positions restarted (no learned reduction tokens); a
pretrained LLM; and the certificate.

**C10.** Xu, Yang, Li, McAllester. *Training Transformers as a Universal Computer.* arXiv April 2026.
https://arxiv.org/abs/2604.25166 **[read]**.
- A 59.5M-parameter decoder trained from scratch, by next-token prediction on random MicroPy traces rewritten with PENCIL
  reductions, interprets a Turing-complete language.
- On six held-out, human-written tasks (copy and flip bits, binary addition and multiplication, SAT verification and
  solving) it is 100% correct. Traces run to 7,552 lines against a 128-line training cap.
- No formal verification.

**3, C10 (universal interpreter); 2, C6.** **For us:** the most direct pre-emption of "a universal interpreter inside a
transformer, exact far beyond training length". Our version must be distinguished by being inside a pretrained chat LLM
that keeps its language, and by a certificate rather than a test-set score. Read the full paper before writing C10.

**C11.** Liu, Andoni, Hsu. *Fixed Universal Transformers.* NeurIPS 2026 (arXiv comment).
https://arxiv.org/abs/2605.31423. Fixed weights simulate any transformer in a class when given a suitable input
embedding (the "program"); random transformers are universal almost surely. **1–2, C10.** **For us:** theory for
"the program lives in the input, the weights stay fixed", which is Π in the context.

**C12.** Aghajohari et al. *The Markovian Thinker* (Delethink). ICLR 2026 (per search; arXiv has no comment).
https://arxiv.org/abs/2510.06557. Already in LITERATURE.md (#51). RL-trained reasoning in fixed chunks with a textual
carryover. **2, C6 (the clock).** **For us:** cite with PENCIL as bounded-context reasoning.

**C13.** Ge et al. *Register Tokens for Bounded-State Reasoning in Diffusion Language Models.* arXiv 2026.
https://arxiv.org/abs/2609.16372. A continuous carried state across cleared chunks. **1.**

**C14.** Meyerson et al. *Solving a Million-Step LLM Task with Zero Errors* (MAKER). arXiv 2025.
https://arxiv.org/abs/2511.09030 **[read]**. See section 1, item 2. **3, C6.**

**C15.** Pai, Xian. *Long-Horizon State Tracking in LLMs: Executing MD5 through a Deep Sequence of Dependent Tool
Calls.* arXiv 2026. https://arxiv.org/abs/2609.00012. gpt-oss-120b carries four 32-bit words across 196 dependent tool
calls and returns the correct digest in a majority of completed runs. In the hardest setting every primitive tool is a
second LLM, with voting. **2, C6.** **For us:** a contemporary "exact state carried by LLM calls" result. Its two
ingredients (keep reasoning in context; vote) contrast with ours (evict; certify). MD5 is also a stretch benchmark.

**C16.** Yoneda et al. *Statler: State-Maintaining Language Models for Embodied Reasoning.* ICRA 2024 (arXiv
comment). https://arxiv.org/abs/2306.17840. An LLM keeps an explicit world-state text that a writer model updates. **1,
C10.**

**C17.** Hu et al. *ChatDB: Augmenting LLMs with Databases as Their Symbolic Memory.* arXiv 2023.
https://arxiv.org/abs/2306.03901. **1.**

**C18.** Bounsi et al. *Transformers meet Neural Algorithmic Reasoners* (TransNAR). arXiv 2024.
https://arxiv.org/abs/2406.09308. An LM cross-attends to a GNN algorithmic reasoner on CLRS-Text. **1.**

**C19.** Pan et al. *Can Transformers Reason Logically? A Study in SAT Solving.* arXiv 2024.
https://arxiv.org/abs/2410.07432. Decoder transformers decide 3-SAT by construction with backtracking CoT; trained ones
generalise within the training sizes but have limited length generalisation. **1.**

### D. Neurosymbolic programs with LLM (or neural) primitives

**D1.** Andreas et al. *Neural Module Networks.* CVPR 2016 (DBLP). https://arxiv.org/abs/1511.02799. **1, C10.**

**D2.** Gupta et al. *Neural Module Networks for Reasoning over Text.* ICLR 2020 (arXiv comment).
https://arxiv.org/abs/1912.04971. **1, C10.**

**D3.** Yi et al. *Neural-Symbolic VQA.* NeurIPS 2018 (arXiv comment). https://arxiv.org/abs/1810.02338. Neural
perception turns pixels into symbols; a symbolic executor runs the program. **1–2, C10.** **For us:** the classic
"snap perception to symbols, execute exactly" split.

**D4.** Manhaeve et al. *DeepProbLog: Neural Probabilistic Logic Programming.* NeurIPS 2018 (arXiv comment).
https://arxiv.org/abs/1805.10872. Neural predicates inside an exact probabilistic logic program. **1–2, C10.**

**D5.** Dohan et al. *Language Model Cascades.* ICML 2022 workshop (arXiv comment). https://arxiv.org/abs/2207.10342.
Programs that compose LM calls as probabilistic primitives. **1, C10.**

**D6.** Beurer-Kellner, Fischer, Vechev. *Prompting Is Programming: A Query Language for Large Language Models*
(LMQL). PLDI 2023 (arXiv comment). https://arxiv.org/abs/2212.06094. **1, C10.**

**D7.** Khattab et al. *Demonstrate-Search-Predict.* arXiv 2022. https://arxiv.org/abs/2212.14024. **0.**

**D8.** Khattab et al. *DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines.* arXiv 2023.
https://arxiv.org/abs/2310.03714. **1, C10.** **For us:** the dominant "programs with LM modules" framework; cite once.

**D9.** Cheng et al. *Binding Language Models in Symbolic Languages* (Binder). ICLR 2023 (arXiv comment).
https://arxiv.org/abs/2210.02875. LM-function calls bound inside SQL or Python and executed by Codex where the base
language cannot answer. **2, C10.** **For us:** "LLM judgments as primitives inside an exact program" in 2022.

**D10.** Surís, Menon, Vondrick. *ViperGPT: Visual Inference via Python Execution for Reasoning.* ICCV 2023 (S2
venue). https://arxiv.org/abs/2303.08128. **1, C10.**

**D11.** Gupta, Kembhavi. *Visual Programming* (VisProg). CVPR 2023 (S2 venue). https://arxiv.org/abs/2211.11559.
**1.**

**D12.** Liang et al. *Code as Policies: Language Model Programs for Embodied Control.* ICRA 2023 (S2 venue).
https://arxiv.org/abs/2209.07753. **1.**

**D13.** Schlag et al. *Large Language Model Programs.* arXiv 2023. https://arxiv.org/abs/2305.05364. Embeds an LLM
inside an algorithm (evidence-supported QA, +6.4% over CoT). **1–2, C10.** **For us:** the source of the phrase
"language model programs".

**D14.** Zelikman et al. *Parsel.* NeurIPS 2023 (DBLP). https://arxiv.org/abs/2212.10561. **1.**

**D15.** Zheng et al. *SGLang.* NeurIPS 2024 (DBLP). https://arxiv.org/abs/2312.07104. **0–1.** **For us:** KV-cache
reuse for structured LM programs; cite if we discuss cache policies.

**D16.** Willard, Louf. *Efficient Guided Generation for Large Language Models* (Outlines). arXiv 2023.
https://arxiv.org/abs/2307.09702. Compiles regular expressions and grammars into an FSM that masks the vocabulary
during decoding. **1–2, C10.** **For us:** the standard way to "snap a judgment to a symbol"; use or cite it for the
snap step.

**D17.** Patel et al. *Semantic Operators: A Declarative Model for Rich, AI-based Data Processing* (LOTUS). arXiv 2024.
https://arxiv.org/abs/2407.11418. Filter, join, sort and aggregate with natural-language criteria judged by LLMs.
**2, C10.** **For us:** semantic predicates as primitives of an exact algebra.

**D18.** Li et al. *Relational Programming with Foundation Models* (Vieira). AAAI 2024 (S2 venue).
https://arxiv.org/abs/2412.14515. Foundation models as foreign predicates inside Scallop/Datalog programs. **2, C10.**

**D19.** Wang et al. *Large Language Models are Interpretable Learners* (LLM-Symbolic Programs). ICLR 2025 (S2 venue).
https://arxiv.org/abs/2406.17224. Decision-rule programs whose nodes are LLM-judged natural-language concepts. **2,
C10.**

**D20.** Dinu et al. *SymbolicAI.* CoLLAs 2024 (S2 venue). https://arxiv.org/abs/2402.00854. **1.**

**D21.** Wu et al. *StateFlow: Enhancing LLM Task-Solving through State-Driven Workflows.* arXiv 2024.
https://arxiv.org/abs/2403.11322. Models LLM task solving as a state machine whose transitions come from rules or LLM
decisions. **1–2, C10.**

**D22.** Peng et al. *Codified Finite-State Machines for Role-playing.* arXiv 2026 (ICLR 2026, unconfirmed).
https://arxiv.org/abs/2602.05905 **[read]**. See section 1, item 5. **3, C10; 2, C6.**

**D23.** Li, Chen, Li, Zhong. *SpecGuard: Detecting Multi-Turn LLM Jailbreaks via Specification-Based Runtime
Monitoring.* arXiv, 26 Oct 2026. https://arxiv.org/abs/2610.36258 **[read]**. 52 deterministic text matchers feed 15
atomic propositions; ten LTLf specifications are compiled into symbolic DFAs. The exactness theorem covers the automaton
only, "not error-free natural-language AP activation". **2, C10.** **For us:** a two-day-old paper that already frames
the guarantee the way we must: exact control, uncertified grounding.

**D24.** Cohen, Havelund, Omer, Peled. *Temporal Guardrails for LLM Conversations: A Runtime Verification Framework.*
LNCS (AI Verification), 2026. https://doi.org/10.1007/978-3-032-32357-6_7. Crossref verified the record; the method
comes from the LLMrv repository, https://github.com/moraneus/LLMrv, whose owner handle matches co-author Moran Omer, but
the README does not cite the paper. Messages are grounded into propositions by embedding kNN, NLI or LLM zero- and
few-shot classification, and a past-time LTL monitor runs with constant-size state. **2–3, C10.** **For us:** an LLM
judgment per event, a symbol, and an exact automaton over 10,000-event conversations is a published design. Our addition
is that the automaton runs inside the same LLM, certified.

**D25.** Su et al. *Neuro-Symbolic Verification on Instruction Following of LLMs* (Nsvif). arXiv 2026.
https://arxiv.org/abs/2601.17789. An LLM classifies each constraint as logical or semantic; logical ones are checked by
generated code. **1.**

**D26.** Yang, Ishay, Lee. *Coupling Large Language Models with Logic Programming for Robust and General Reasoning from
Text.* Findings of ACL 2023 (arXiv comment). https://arxiv.org/abs/2307.07696. An LLM semantically parses stories into
atoms; reusable ASP modules reason exactly. State of the art on bAbI, StepGame, CLUTRR and gSCAN. **2, C10.** **For
us:** the benchmark set where "snap sentences to symbols, then exact control" is already strong. Use it as a C10
comparison.

**D27.** Kambhampati et al. *LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks.* ICML 2024 (journal
ref). https://arxiv.org/abs/2402.01817. Position: LLMs generate, external verifiers check. **1–2, C9/C10 framing.**
**For us:** our verifier is the certificate, and the checked executor is the LLM itself.

**D28.** Ganguly et al. *Proof of Thought.* NeurIPS 2024 System 2 Reasoning at Scale workshop (arXiv comment).
https://arxiv.org/abs/2409.17270. LLM to JSON DSL to first-order logic for Z3. **1.**

**D29.** Grand et al. *LILO: Learning Interpretable Libraries by Compressing and Documenting Code.* ICLR 2024 (arXiv
comment). https://arxiv.org/abs/2310.19791. **1–2, C10 (standard library).**

**D30.** Wang, Fried, Neubig. *TroVE: Inducing Verifiable and Efficient Toolboxes for Solving Programmatic Tasks.* ICML
2024 (S2 venue). https://arxiv.org/abs/2401.12869. Induces small verified function libraries from LM-written programs.
**2, C10 (a "certified standard library").** **For us:** "verifiable toolbox" is the nearest phrase; cite it.

**D31.** Wang et al. *Voyager: An Open-Ended Embodied Agent with Large Language Models.* TMLR 2024 (DBLP).
https://arxiv.org/abs/2305.16291. A growing library of executable code skills. **1, C10.**

### E. Logic by translation to solvers, and logic benchmarks

**E1.** Lyu et al. *Faithful Chain-of-Thought Reasoning.* IJCNLP-AACL 2023 (arXiv comment).
https://arxiv.org/abs/2301.13379. NL → symbolic chain (LM), then a deterministic solver, so the chain is faithful by
construction. **1–2, C9.** **For us:** "faithful because executed" is their argument; ours is "faithful because
certified". Cite with PAL.

**E2.** Pan et al. *Logic-LM.* Findings of EMNLP 2023 (arXiv comment). https://arxiv.org/abs/2305.12295. LLM
formalises, solver infers, solver errors drive self-refinement. **1–2, C9/C10.**

**E3.** Ye et al. *SatLM: Satisfiability-Aided Language Models Using Declarative Prompting.* NeurIPS 2023 (arXiv
comment). https://arxiv.org/abs/2305.09656. **1.**

**E4.** Olausson et al. *LINC: A Neurosymbolic Approach for Logical Reasoning by Combining Language Models with
First-Order Logic Provers.* EMNLP 2023, Outstanding Paper (arXiv comment). https://arxiv.org/abs/2310.15164. **1–2,
C10.** **For us:** the LLM is only a semantic parser and the prover reasons, the cleanest statement of the split we
keep inside the model.

**E5.** Xu et al. *Faithful Logical Reasoning via Symbolic Chain-of-Thought* (SymbCoT). ACL 2024 (arXiv comment).
https://arxiv.org/abs/2405.18357. The LLM itself carries out the symbolic reasoning, with no external solver, plus a
verifier step. **1–2, C10.** **For us:** "the LLM is its own solver", uncertified.

**E6.** Poesia, Gandhi, Zelikman, Goodman. *Certified Deductive Reasoning with Language Models* (LogicGuide). TMLR
2024 (DBLP). https://arxiv.org/abs/2306.04031. "Guides" constrain generation to statements a logic tool certifies as
valid; training on certified self-generated reasoning helps. **2, C6/C9 (terminology).** **For us:** "certified
reasoning with language models" is a taken title. Say what our certificate certifies (a run equals its table), and cite
LogicGuide to pre-empt confusion.

**E7.** Feng et al. *VeriCoT: Neuro-symbolic Chain-of-Thought Validation via Logical Consistency Checks.* arXiv 2025.
https://arxiv.org/abs/2511.04662. Each CoT step is formalised into first-order logic and checked by a solver. **1.**

**E8.** Ling et al. *Deductive Verification of Chain-of-Thought Reasoning* (Natural Program). NeurIPS 2023 (arXiv
comment). https://arxiv.org/abs/2306.03872. **1.**

**E9.** Xie et al. *On Memorization of Large Language Models in Logical Reasoning* (Knights and Knaves). arXiv 2024.
https://arxiv.org/abs/2410.23123. A dynamically generated K&K benchmark; fine-tuned models memorise yet also generalise.
**1, benchmark.**

**E10.** Xie et al. *Logic-RL.* arXiv 2025. https://arxiv.org/abs/2502.14768. Rule-based RL on K&K. **1.**

**E11.** Mondorf, Plank. *Liar, Liar, Logical Mire* (TruthQuest). EMNLP 2024 (arXiv comment).
https://arxiv.org/abs/2406.12546. Truth-teller/liar puzzles with 3–6 characters. **1, benchmark.**

**E12.** Suzgun et al. *Challenging BIG-Bench Tasks and Whether Chain-of-Thought Can Solve Them* (BBH). Findings of ACL
2023 (DBLP). https://arxiv.org/abs/2210.09261. Includes Web of Lies, Boolean Expressions, Tracking Shuffled Objects,
Navigate, Object Counting, Multistep Arithmetic and Dyck Languages. **1, benchmark.**

**E13.** Kazemi et al. *BIG-Bench Extra Hard.* ACL 2025 (S2 venue). https://arxiv.org/abs/2502.19187. Harder
replacements of every BBH task. The best general-purpose model scores 9.8% (harmonic mean) and the best reasoning model
44.8%. **1, benchmark.**

**E14.** Lin et al. *ZebraLogic: On the Scaling Limits of LLMs for Logical Reasoning.* ICML 2025 (arXiv comment).
https://arxiv.org/abs/2502.01100. Accuracy declines with search-space size, even for o1 and R1 (the "curse of
complexity"). **1, benchmark.**

**E15.** Saparov, He. *Language Models Are Greedy Reasoners* (PrOntoQA). ICLR 2023 (arXiv comment).
https://arxiv.org/abs/2210.01240. **1, benchmark.**

**E16.** Other benchmarks (each **0–1**; uses in section 4):
- bAbI, Weston et al. 2015, https://arxiv.org/abs/1502.05698
- ProPara, Dalvi et al., NAACL 2018, https://arxiv.org/abs/1805.06975
- CLUTRR, Sinha et al., EMNLP 2019, https://arxiv.org/abs/1908.06177
- BABILong, Kuratov et al., NeurIPS 2024 D&B, https://arxiv.org/abs/2406.10149: bAbI facts hidden in up to millions of
  tokens
- RULER, Hsieh et al., COLM 2024, https://arxiv.org/abs/2404.06654: includes variable tracking
- GSM-Infinite, Zhou et al. 2025, https://arxiv.org/abs/2502.05252
- CLRS-Text, Markeeva et al. 2024, https://arxiv.org/abs/2406.04229
- Reasoning Gym, Stojanovski et al., NeurIPS 2025 spotlight, https://arxiv.org/abs/2505.24760: procedurally generated
  RLVR environments with adjustable difficulty
- LongProc, Ye et al., COLM 2025, https://arxiv.org/abs/2501.05414

### F. Verification of LLM reasoning and certification theory

**F1.** Cobbe et al. *Training Verifiers to Solve Math Word Problems* (GSM8K). arXiv 2021.
https://arxiv.org/abs/2110.14168. **1.**

**F2.** Wang et al. *Self-Consistency.* ICLR 2023 (arXiv comment). https://arxiv.org/abs/2203.11171. **1.** **For us:**
majority voting is the statistical alternative to certification (as is MAKER's).

**F3.** Weng et al. *Large Language Models are Better Reasoners with Self-Verification.* Findings of EMNLP 2023 (arXiv
comment). https://arxiv.org/abs/2212.09561. **1.**

**F4.** Lightman et al. *Let's Verify Step by Step.* ICLR 2024 (DBLP). https://arxiv.org/abs/2305.20050. Process reward
models. **1, C6 terminology.** **For us:** a PRM verifies steps statistically; our certificate checks each step against
an exact table. Say this in one line.

**F5.** Wang et al. *Math-Shepherd.* ACL 2024 (S2 venue). https://arxiv.org/abs/2312.08935. **1.**

**F6.** Dhuliawala et al. *Chain-of-Verification Reduces Hallucination in Large Language Models.* ACL 2024 (S2 venue). https://arxiv.org/abs/2309.11495. **0–1.**

**F7.** Kirchner et al. *Prover-Verifier Games improve legibility of LLM outputs.* arXiv 2024.
https://arxiv.org/abs/2407.13692. **1.**

**F8.** Lambert et al. *Tülu 3* (names RLVR). arXiv 2024. https://arxiv.org/abs/2411.15124. **1.**

**F9.** Shao et al. *DeepSeekMath* (GRPO). arXiv 2024. https://arxiv.org/abs/2402.03300. **1.**

**F10.** DeepSeek-AI. *DeepSeek-R1.* Nature 645, 633–638 (2025) (journal ref). https://arxiv.org/abs/2501.12948. **1.**

**F11.** Yue et al. *Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?*
NeurIPS 2025 oral (journal ref). https://arxiv.org/abs/2504.13837. RLVR mostly reweights reasoning paths the base model
already has. **1–2, C6 ("the executor is latent and ~30 steps switch it on").** **For us:** the same "elicit, don't
create" story at a different level; cite where we say the lookup is latent.

**F12.** Necula. *Proof-carrying code.* POPL 1997. https://doi.org/10.1145/263699.263712. Pnueli, Siegel, Singerman.
*Translation validation.* TACAS 1998, LNCS. https://doi.org/10.1007/BFb0054170. (Both Crossref-verified; already named
in INSIGHTS.md.) **2, C6 framing.** **For us:** the certificate is translation validation of one program on one machine.

**F13.** Back de Luca, Fountoulakis. *Certification from Examples is Hard for Circuits and Transformers under Minimal
Overparametrization.* arXiv May 2026. https://arxiv.org/abs/2605.22964. "Exact certification" means the smallest set of
labelled examples certifying that a learned hypothesis equals the target. With minimal overparametrisation, certificate
size becomes exponential for depth ≥ 2 threshold circuits and for log-precision transformers. Trained transformers for
binary addition evade large sampled certificates. **2–3, C6 (the theorem pair).** **For us:** a contemporary, sharper
version of our "no finite test suite certifies unpinned decoding". Our positive half is the escape: pinning makes the
input domain of a step finite, so per-row certificates are complete. Cite it in the theorem pair and check that our
statement is consistent with theirs.

**F14.** Yang, Bergsträßer, Zetzsche, Chiang, Lin. *Length Generalization Bounds for Transformers.* arXiv 2026.
https://arxiv.org/abs/2603.02238. There are no computable length-generalisation bounds for C-RASP (two layers) and hence
for transformers; for positive C-RASP and fixed precision a bound exists but is exponential. **2, C6 (theorem pair).**
**For us:** another reason that certifying unpinned decoding from finite data is hopeless. Cite it beside F13.

**F15.** Somani. *Towards Verifiable Transformers: Solver-Checkable Circuit Explanations.* arXiv 2026.
https://arxiv.org/abs/2605.24033. Solver-checked circuit claims over a hash-pinned prompt domain; "we must build the
object we can verify". **1–2, C6 (no weights-level certificate, N\*).**

**F16.** Huang et al. *A Formal Framework for Understanding Length Generalization in Transformers.* ICLR 2025 (S2,
comment). https://arxiv.org/abs/2410.02140. Ahuja, Mansouri. *On Provable Length and Compositional Generalization.*
arXiv 2024. https://arxiv.org/abs/2402.04875. **1.**

### G. Latent reasoning and "system 2" without more tokens

**G1.** Graves. *Adaptive Computation Time.* arXiv 2016. https://arxiv.org/abs/1603.08983. Dehghani et al. *Universal
Transformers.* ICLR 2019 (DBLP). https://arxiv.org/abs/1807.03819. Banino et al. *PonderNet.* ICML 2021 workshop
(comment). https://arxiv.org/abs/2107.05407. **1.**

**G2.** Goyal et al. *Think before you speak: Training Language Models With Pause Tokens.* ICLR 2024 (arXiv comment).
https://arxiv.org/abs/2310.02226. Zelikman et al. *Quiet-STaR.* arXiv 2024. https://arxiv.org/abs/2403.09629. Pfau,
Merrill, Bowman. *Let's Think Dot by Dot.* arXiv 2024. https://arxiv.org/abs/2404.15758. **1 each.** None claims
exactness at length.

**G3.** Baherwani, Goldstein, Panda. *Not All LLM Reasoning is Visible in the Chain-of-Thought.* arXiv 2026.
https://arxiv.org/abs/2607.22925. Filler tokens give 13 frontier models up to +13 pp. **1.**

**G4.** Deng et al. *Implicit Chain of Thought Reasoning via Knowledge Distillation.* arXiv 2023.
https://arxiv.org/abs/2311.01460. Reasoning moved "vertically" across layers; multi-digit multiplication. **1.** (Its
2024 sequel and Coconut are in LITERATURE.md, #53 and #50.)

**G5.** Zhu et al. *Reasoning by Superposition: A Theoretical Perspective on Chain of Continuous Thought.* NeurIPS 2025
(arXiv comment). https://arxiv.org/abs/2505.12514. **1.**

**G6.** Shen et al. *CODI.* EMNLP 2025 (DBLP). https://arxiv.org/abs/2502.21074. Zhang et al. *Soft Thinking.* NeurIPS
2025 (S2 venue). https://arxiv.org/abs/2505.15778. **1 each.**

**G7.** Saunshi et al. *Reasoning with Latent Thoughts: On the Power of Looped Transformers.* ICLR 2025 (arXiv
comment). https://arxiv.org/abs/2502.17416. Zhu et al. *Scaling Latent Reasoning via Looped Language Models* (Ouro).
arXiv 2025. https://arxiv.org/abs/2510.25741. (Recurrent depth, Geiping et al., is LITERATURE.md #54.) **1 each.**

**G8.** Wang et al. *Hierarchical Reasoning Model.* arXiv 2025. https://arxiv.org/abs/2506.21734.
Jolicoeur-Martineau. *Less is More: Recursive Reasoning with Tiny Networks* (TRM). arXiv 2025.
https://arxiv.org/abs/2510.04871. Latent recursion on Sudoku, mazes and ARC with tiny models. **1.** **For us:** the
popular face of "reasoning without tokens"; fixed-size puzzles, no exactness at length.

**G9.** Amos et al. *Latent Reasoning with Supervised Thinking States.* arXiv 2026. https://arxiv.org/abs/2602.08332.
Thinking tokens produced while reading are fed back as embeddings, with stronger state tracking than CoT and
extrapolation beyond training lengths (the abstract gives no numbers). **2, C6 (state tracking).** **For us:** the
nearest latent method with a state-tracking length claim. Read its tables before claiming that latent methods fail at
length.

**G10.** Cheng, Zhang. *Not All Thinking is Created Equal: Latent Reasoning Discovers a Recurrent Search Algorithm for
Depth Generalization.* arXiv 2026. https://arxiv.org/abs/2609.35643. **1.**

**G11.** Zhu et al. *A Survey on Latent Reasoning.* arXiv 2025. https://arxiv.org/abs/2507.06203. **0** (an index).

**G12.** Bai et al. *Why Can't Transformers Learn Multiplication?* arXiv 2025. https://arxiv.org/abs/2510.00184.
**1.**

### H. Frontier and reasoning models on long exact tasks

**H1.** Shojaee et al. *The Illusion of Thinking.* NeurIPS 2025 (arXiv comment). https://arxiv.org/abs/2506.06941.
Reasoning models "face a complete accuracy collapse beyond certain complexities" on controllable puzzles and "fail to
use explicit algorithms". **2, C9 comparator.**

**H2.** Lawsen. *Comment on The Illusion of Thinking.* arXiv 2025. https://arxiv.org/abs/2506.09250. Attributes much of
the collapse to output-token limits and unsolvable instances. When asked to write a generating function instead of
listing moves, models show high accuracy on Tower of Hanoi. **2, C9.** **For us:** the strongest objection to any
"frontier models fail" panel. Our frontier arm must include "write a program" (and, separately, "write and run").

**H3.** Sinha, Arun, Goel, Staab, Geiping. *The Illusion of Diminishing Returns: Measuring Long Horizon Execution in
LLMs.* ICLR 2026 (arXiv comment). https://arxiv.org/abs/2509.09677 **[read]**. Already in `refs.bib`. In a dictionary
lookup and running-sum task with the plan given, the single-turn horizon at ≥ 80% accuracy is 2,176 steps for GPT-5,
432 for Claude 4 Sonnet, 384 for Grok 4 and 120 for Gemini 2.5 Pro. Self-conditioning on one's own errors drives
failure; Qwen3 thinking models resist it. No tool experiments. **2, C9.** **For us:** the only verified published Grok
number for long exact execution I found. Their task is an ideal Savant program (a lookup plus a counter).

**H4.** Motwani et al. *LongCoT: Benchmarking Long-Horizon Chain-of-Thought Reasoning.* arXiv 2026.
https://arxiv.org/abs/2604.14140. 2,500 problems needing tens to hundreds of thousands of reasoning tokens; GPT 5.2
scores 9.8% and Gemini 3 Pro 6.1%. **1–2, C9.**

**H5.** Malek et al. *Frontier LLMs Still Struggle with Simple Reasoning Tasks.* arXiv 2025.
https://arxiv.org/abs/2507.07313. Thinking models fail when parameters scale the computation (counting, logic,
planning) and on trivialised "unpuzzles". **1.**

**H6.** Panda et al. *When LLMs Stop Following Steps: A Diagnostic Study of Procedural Execution in Language Models.*
arXiv 2026. https://arxiv.org/abs/2605.00817. First-answer accuracy on given arithmetic procedures falls from 63% at 5
steps to 20% at 95 steps, across 15 models. **2, C9.** **For us:** a ready-made benchmark of "procedures written in
words", ideal for "write the table, run it".

**H7.** Patil et al. *Beyond Accuracy: Diagnosing Algebraic Reasoning Failures in LLMs Across Nine Complexity
Dimensions.* arXiv 2026. https://arxiv.org/abs/2604.06799. Every model collapses between 20 and 30 parallel branches.
**1.**

**H8.** Zhang, Cao, You. *Counting Ability of Large Language Models and Impact of Tokenization.* arXiv 2024.
https://arxiv.org/abs/2410.19730. Nikankin et al. *Arithmetic Without Algorithms: Language Models Solve Math With a Bag
of Heuristics.* ICLR 2025 (S2 venue). https://arxiv.org/abs/2410.21272. **1 each**, for the introduction.

**H9.** Tang et al. *Do Language Models Track Entities Across State Changes?* ICML 2026 (arXiv comment).
https://arxiv.org/abs/2605.30233. LMs do not track world state incrementally; they aggregate relevant information in
parallel at the final token. **1–2, C6/C10.** **For us:** a mechanistic reason that plain decoding cannot keep exact
state over long event streams; it supports the clock.

**H10.** Fan et al. *Can Agent Memory Systems Track Evolving State?* (StateMemBench). arXiv 2026.
https://arxiv.org/abs/2608.19652. Hamilton et al. *Too Long, Didn't Model.* LaTeCH-CLfL 2025 (S2 venue).
https://arxiv.org/abs/2505.14925. **1 each**; C10 benchmark candidates.

**H11.** Already in our files and relevant here (not re-annotated): Michelangelo Latent List (LITERATURE #82), Faith
and Fate (#76), LEAPS (`refs.bib`, arXiv 2610.25919, verified again today).

### I. Deployment

**I1.** Ruan et al. *WebLLM: A High-Performance In-Browser LLM Inference Engine.* arXiv 2024.
https://arxiv.org/abs/2412.15803. **1, C6 ("runs in a browser").** **For us:** in-browser LLM inference is standard;
claim only that the *certified executor* runs in the browser.

---

## 3. The frontier in 2026, in one paragraph

By late 2026 the default answer to "LLMs cannot do long exact computation" is delegation, and delegation lives inside
the reasoning trace. Frontier models call a Python interpreter mid-thought (the o-series since April 2025; Claude's
interleaved thinking), and an RL literature on tool-integrated reasoning (ReTool, ToRL, SimpleTIR, rStar2-Agent, CoRT)
trains open models to decide when to call. Without tools, frontier models still lose exactness quickly:
- 2,176 steps for GPT-5, 432 for Claude 4 Sonnet and 384 for Grok 4 on a lookup-and-add task;
- unaided depth d* ≈ 19–31 on deterministic state tracking;
- under 10% for GPT 5.2 and Gemini 3 Pro on LongCoT;
- 63% → 20% accuracy from 5 to 95 given arithmetic steps.

Exactness without an interpreter has been reached three ways:
- **Statistically**, by decomposing into single-step LLM calls and voting (MAKER: a million Hanoi moves with zero
  errors; MD5 over 196 dependent calls).
- **From scratch**, by training small transformers to execute under context-reduction scaffolds (PENCIL; a 59.5M MicroPy
  interpreter exact on traces 60× longer than training).
- **By fine-tuning** LLMs to run arithmetic step by step, nearly but not exactly (CAEF at 100 digits).

Semantic-event control, where an LLM labels each event and an exact automaton tracks the state, is spreading through
agent safety (TemporalGuard, SpecGuard) and role-play (CFSM), always with the automaton in code. On the theory side, 2026
results show that certifying an unconstrained transformer from finite examples is exponentially hard (Back de Luca and
Fountoulakis) and that length-generalisation bounds are not even computable in general (Yang et al.). Bounded-step
designs are the known route to finite certificates: recursion in Cai et al. 2017, reduction in PENCIL, and our pinned
clock. Latent reasoning (Coconut, looped and recurrent-depth models, HRM and TRM, Thinking States) is active but makes
no exactness-at-length claims and offers no certificates. **Gap that remains open:** an off-the-shelf LLM that is
itself the certified executor of programs it writes, with language intact, and with a necessary-and-sufficient
certificate. I found nothing that fills it.

---

## 4. Ideas

### 4.1 Rewording rules (apply across the paper)
1. Never say first for any of these:
   - LLM-as-executor (CAEF, COGEX, Chain of Code, Think-and-Execute);
   - finite verification ⇒ all lengths (Cai et al. 2017);
   - zero-error LLM execution over long horizons (MAKER);
   - LLM-judged guards over code-run FSMs (CFSM, TemporalGuard);
   - a universal interpreter in a transformer (Giannou et al. 2023; Xu et al. 2026);
   - reasoning with interleaved calls (o3, Claude, START, ReTool);
   - citing results by placeholder (Chain-of-Abstraction).
2. Defensible "first" sentence: "To our knowledge, no prior system makes an off-the-shelf language model the certified
   executor of programs it writes itself: each transition is the model's own decoding under a fixed KV-cache policy, and
   a per-row certificate is necessary and sufficient for exactness at every length."
3. Frame the clock as a member of the bounded-context family (PENCIL, Delethink, MAKER's per-step agents, CAEF's
   per-step calls) whose distinguishing property is that it makes finite certification complete.
4. Frame certification against the statistical alternatives: voting (MAKER, self-consistency), process reward models
   (Lightman et al.) and execution-trace RLVR. Say what each guarantees.

### 4.2 Baselines that the prior art makes mandatory for C9 (REASON)
| Arm | Why (prior art) | Expected outcome |
|---|---|---|
| Qwen3-4B base + Python (PAL or ToRA-style; optionally a short TIR fine-tune) | PAL, ToRA, START, ReTool | exact on the arithmetic parts; equal to Savant if programs are equal |
| Frontier, tools on (o-series or GPT-5 with Python; Claude with code execution) | o3 system card; interleaved thinking | near-exact; reviewers will ask |
| Frontier, tools off but "write a generating function" (no execution) | Lawsen 2025 | shows whether the failure is execution or planning |
| Frontier, tools off, plain | Illusion of Thinking, Sinha | the failure panel (already planned) |
| Base Qwen3-4B under the same clock, uncertified, with MAKER-style first-to-ahead-by-k voting | MAKER | the cost of exactness by voting against by certification |
| Chain of Code interleave and LM-only on semantic composites | Chain of Code | Savant ≈ interleave ≫ LM-only |
| Base thinking at 32k | (planned) | collapses with length |

Report theorem C's three terms separately: table wrong, quote wrong (cf. the Deterministic Horizon's interface errors)
and glue wrong (cf. Tool-Induced Myopia).

### 4.3 Benchmarks where reasoning with calls shows at its best
- **GSM-HARD (PAL) scaled up to "GSM-Huge".** Swap in 100–4,096-digit numbers. CoT collapses, Python and Savant stay
  flat. This is the cleanest picture of C9: the same reasoning text, only the computation grows.
- **Sinha's running-sum task.** A dictionary lookup plus a counter; GPT-5 tops out at 2,176 steps. It is a two-row-type
  table for Savant; run it to 10,000 and beyond.
- **The procedures of "When LLMs Stop Following Steps".** 5–95-step arithmetic procedures given in words; the model
  writes the table, the clock runs it.
- **The Deterministic Horizon families:** PermutationProbe, FSA-Sim, ArithChain, CodeProbe. They are published, have
  frontier numbers, and have a tool arm to compare against.
- **BBEH and BBH algorithmic tasks:** Multistep Arithmetic, Tracking Shuffled Objects, Boolean Expressions, Object
  Counting, Dyck, Web of Lies. BBEH's best reasoning-model score is 44.8%, so there is room above it.
- **GSM-Infinite** (controllable reasoning depth and noise) and **CLRS-Text** (algorithm execution traces) for breadth.
- A stretch target: **MD5 over 196 dependent calls** (2609.00012), the 32-bit modular-add table as a certified program.

### 4.4 Benchmarks for semantic-event programs (C10)
The design principle: events are sentences, the program is a small automaton, length is the number of events, and every
error is attributable to a snap (the classification of a sentence) because control error is zero.
- **Web of Lies at length n** (BBH/BBEH style). "A says B lies" is one event and the state is one bit. Scale n from 5 to
  10,000; frontier models degrade with n.
- **Tracking Shuffled Objects / Kim and Schuster's boxes in prose.** Swaps and moves described in varied natural
  language; the state is a permutation (S_k), linking C10 directly to the S5 results of v1.
- **bAbI 1–3, 6–8 and 14 at BABILong lengths.** Location and possession tracking with facts spread over up to millions
  of tokens. Yang, Ishay and Lee (LLM + ASP) are the external-control baseline.
- **ProPara and OpenPI.** Procedural text with entity state changes; a real-language C10 testbed where snaps are hard.
- **CLUTRR and StepGame.** Relation composition (kinship, spatial) where each sentence contributes a generator. This is
  group-like composition over semantic events and ties to the holonomy and groups thread.
- **CFSM's synthetic FSMs (Mario power-ups and others)** extended from 10 to 10,000 steps, with CFSM (Python control,
  same predicate model) as the baseline.
- **Conversation policy monitors** (TemporalGuard and SpecGuard style). An LTL or DFA policy over 10,000 dialogue turns,
  with propositions snapped by Savant itself. This shows C10 in a safety application and borrows their "guarantee
  modulo grounding" framing.
- **A new, cheap, certifiable domain: "Ledger stories".** Deposits, withdrawals and transfers described in free prose,
  with the state a vector of balances under a modulus or a counter automaton. Ground truth comes from the generator,
  the snap set is small and fixed, and the length axis is unbounded.

For every C10 benchmark, report:
- snap accuracy per event, measured alone with constrained decoding to the symbol set (Outlines-style);
- end-to-end accuracy against length;
- the check that end-to-end error equals the snap-error prediction exactly (theorem C), which is the empirical
  signature that control error is zero.

### 4.5 Things to read in full before writing C10
1. Xu et al. 2026 (Universal Computer): its MicroPy encoding, the PENCIL scaffold, and whether the 59.5M interpreter's
   "100%" is token-level or program-level.
2. Cai et al. 2017, sections 3–4: borrow their verification-set construction language for Theorem P's "reachable rows".
3. Back de Luca and Fountoulakis 2026: check that our "no finite test suite" statement matches their model class and
   cite the exact theorem.
4. CFSM appendix: the social-simulation results (96.13% correct interactions) and the dynamic-state extension.

---

## Unverified or excluded items (not used in the argument)
- **"Transforming Language Models into Program Interpreters via Execution Trace Chain of Thought"** (Eguchi, Akiba et
  al.; ICML 2025 workshop poster as "Making LLMs Program Interpreters via Execution Trace Chain of Thought"; a TMLR 2026
  bibliography entry). No arXiv id found; not verified. Potentially close to C6 (an LLM trained to emit execution
  traces); find it before submission.
- **"Dissecting Tool-Integrated Reasoning: An Empirical Study and Analysis".** A search result gave arXiv 2508.15754,
  but that id resolves to a different paper ("When Tools Hurt LLM Reasoning"). Unverified.
- **ICLR 2017 best paper status of Cai et al.** Seen only in a Medium post; iclr.cc's archive page does not list titles.
- **CFSM at ICLR 2026.** Seen in a search-result snippet of an OpenReview PDF; the PDF could not be fetched.
- **OpenAI's "Introducing o3 and o4-mini" blog** returned HTTP 403. The system card PDF of the same date was used
  instead.
- **Kimi K2 Thinking's interleaved tool use, a "WASM interpreter in a transformer" forum post, MAKER's appendix on
  multi-digit multiplication, and Thinking States' per-length numbers.** Mentioned only by secondary sources; not
  checked and not used.

Files: `L5_verified_records.json` (185 arXiv records with abstracts and S2/DBLP venue hints, plus 5 DOI or vendor
records); `L5_verify_arxiv.py` (the verification script).
