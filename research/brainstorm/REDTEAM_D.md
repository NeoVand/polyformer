# Red team D: "a model that learns what to keep, proved exact" (28 Oct 2026)

**Scope.** I tested three claims against our verified map (L1 §1.1, §1.4, §1.5; L2 §1.2 and K4; L4 §1.2, §1.5) and against
new searches. Every arXiv identifier below was checked today, 2026-10-28, with the arXiv API
(`export.arxiv.org/api/query?id_list=…`) for title, authors, date and comment field. DOIs were checked with Crossref, and
PMLR pages were fetched directly. "Read" means I read the method or theorem text (HTML, or PDF converted with pdftotext),
not only the abstract.

---

## 1. Verdict table

| Claim | Verdict | Closest work (verification) | Sentence we can safely use |
|---|---|---|---|
| **C1.** "A model that learns what to keep, with the result proved exact, doesn't exist yet." | **FALSE** | **Learned state, certified at every length, small networks trained from scratch:**<br>- Brandoit et al., arXiv 2609.32447 (2026); in our map, L4 §1.2.<br>- Bugaud 2026a/b, ICML 2026 workshops; in our map, L4 §1.5.<br>- **New:** Nerem, Chen, Dasgupta & Wang, "Graph neural networks extrapolate out-of-distribution for shortest paths", COLT 2026 (PMLR v336), arXiv 2503.19173. Theorem read; PMLR page fetched.<br><br>**Certified, but the kept state is chosen by the designer:**<br>- Rodionov & Prokhorenkova, "Discrete Neural Algorithmic Reasoning", ICML 2025 (PMLR v267), arXiv 2402.11628. Read.<br>- Cai, Shin & Song, ICLR 2017; in our map.<br><br>**A non-neural learner whose abstraction is certified exact:**<br>- Abate, Giacobbe & Schnitzer, "Bisimulation Learning", CAV 2024, LNCS 14683:161–183, doi 10.1007/978-3-031-65633-0_8. Crossref checked; method read. | "States learned by small networks trained from scratch have already been certified exact at every length (Brandoit et al. 2026; Bugaud 2026; Nerem et al. 2026). What we add is a *pretrained language model* that chooses what it carries." |
| **C2.** "No prior work has a *pretrained LM* choose what to carry into a bounded or isolated context, with a proof or certificate that the computation inside is exact at unbounded length." | **TRUE as far as we searched**, but **Savant itself satisfies it**. C2 is therefore a novelty claim for Savant, not evidence that the problem is open. | **Pretrained model and a certificate, but the harness, not the model, fixes what is carried:**<br>- Lewandowski, Machado & Schuurmans, arXiv 2601.08061; in our map, L1 §1.1.<br><br>**The model chooses what it carries, but there is no proof:**<br>- Lee & Kim, Recursion of Thought, ACL 2023 Findings, arXiv 2306.06891. They fine-tune GPT-3. PDF read.<br>- Aghajohari et al., The Markovian Thinker / Delethink, arXiv 2510.06557. Read.<br>- Sun et al., Context-Folding, arXiv 2510.11967. PDF checked.<br>- Zhang, Kraska & Khattab, Recursive Language Models, arXiv 2512.24601. Read.<br>- MemAgent (ICLR 2026), MEM1, InftyThink (ICLR 2026) and THREAD: abstracts read and PDFs checked.<br><br>**Learned erasure with only an expressivity theorem:**<br>- PENCIL, ICML 2025; in our map, K4 and L1 §1.5. | "To our knowledge, Savant is the first pretrained language model that chooses what to carry into an isolated context and whose computation there is certified exact at every length. The certificate holds relative to the table and notes it wrote." |
| **C3.** "No prior work proves, or certifies with a finite check, that a model's *own chosen abstraction* is sufficient for the task." | **PARTLY.** FALSE when the task is given formally. TRUE (nothing found) for a pretrained LM reading natural language. | **Formal task:**<br>- Moore (1956), Chow, IEEE TSE SE-4:178–187 (1978), and Vasilevskii, Cybernetics 9:653–665 (1973; Crossref dates the translation 1975). A state bound plus a finite test suite certifies equivalence. Crossref checked.<br>- Angluin, Inf. Comput. 75:87–106 (1987). Crossref checked.<br>- Abate et al., CAV 2024: a learned partition is SMT-certified to be an exact bisimulation.<br>- Zhong et al., SemRegex, EMNLP 2018, doi 10.18653/v1/D18-1189. The model writes a regex from natural language, and it is checked by exact DFA equivalence against a human-written reference. Crossref checked.<br>- Delgrange, Nowé & Pérez, ICLR 2023, arXiv 2303.12558: bounds on the bisimulation distance of a learned latent MDP, PAC-estimated. Bounds read in the PDF.<br><br>**Language models (no sufficiency certificate):**<br>- L\*LM, arXiv 2402.07051.<br>- LWM-Planner, AISTATS 2026, arXiv 2506.09171.<br>- WorldCoder, arXiv 2402.12275.<br>- Context Compaction Theory, arXiv 2608.01326. | "No work we found certifies that the state a pretrained language model chose to keep from a natural-language question is sufficient for that question. Finite certificates of sufficiency exist only when the task is given formally: as a model of the system, as an oracle with a bound on its number of states, or as a reference specification." |

**What stays open in C3, stated exactly.**

1. **Faithfulness to the natural-language question itself cannot be proved by anyone.**
   - Natural language has no formal semantics. This is the same gap as faithfulness in autoformalization.
   - Clover says outright that it "assume[s] that a precise natural language description … is available".
   - Astrogator has the user confirm a formal query.
   - BEq and FormalAlign compare one formal statement with another, or score alignment with a learned model.
   - Do not claim this form.
2. **Sufficiency against an executable reference, with a state bound, is decidable by a finite test.** Moore, Chow and Vasilevskii give such a test. The theory is classical; what is new is only the application. No LLM paper does it:
   - L\*LM only guarantees a DFA "consistent with the input examples".
   - The pMAT/CAPAL line assumes the equivalence oracle.
   - WorldCoder checks consistency with observed data, and its Theorem 2.4 assumes the true model lies in the model class.
   - LWM-Planner says it does not claim "formal guarantees".
   - Context Compaction Theory lists compaction that an LLM can compute as open.

   **The open, well-posed form for LLMs is this.** A pretrained LM reads a natural-language question and chooses its carried state and table. That choice is certified *sufficient* against an executable reference by a finite conformance test with a justified state bound. No per-question human-written reference is used. Exact execution is then certified at every length (Savant's existing half).
3. **Sufficiency relative to the model's own full-context behaviour.** This is my inference and has not been checked: our own `no_finite_test_suite` theorem suggests no finite test can certify it in general, because the reference would itself be decoding with history in context.

**Correction for THESIS_CHECK.md line 28.** This file is not edited; only this output was written. The line says: "Learned, certified abstraction … is open. Everyone else hand-designs what is kept." **Both halves are false as written.**
- Brandoit, Bugaud and Nerem learn what is kept and certify it.
- MemAgent, MEM1, Delethink, InftyThink, Context-Folding and RLM let a pretrained LLM choose what is kept, without a certificate.

Narrow the line to C3's open form in item 2 above.

---

## 2. Close papers: what each does, what it proves, and the gap

### C1: learned states certified exact

- **Brandoit et al. 2026** (arXiv 2609.32447; map L4 §1.2).
  - Neural FSMs, trained from scratch.
  - An iff cell condition for independence of length.
  - Tables are read off the logits and checked exactly; with a margin, every length is exact.
  - **Gap to us:** no language model and no choice of what to carry from a question. Already in the map.
- **Bugaud 2026a/b** (ICML 2026 workshops; map L4 §1.5).
  - Certificates of Elman RNNs from the weights alone; 100% at L = 10⁶.
  - Only absorbing-state languages can be certified.
  - **Gap to us:** small RNN, formal languages, no LLM. Only the abstracts were read; see §3.
- **Nerem, Chen, Dasgupta & Wang, COLT 2026** (PMLR v336; arXiv 2503.19173 v2). Theorem 2.3 read.
  - **What it does.** A MinAgg GNN is trained with only output supervision (the K-step Bellman–Ford answer) plus a sparsity penalty, on a finite set 𝒢_K. The network chooses what each node stores.
  - **What it proves.** Suppose the loss on the finite set is within ε of its global minimum, which can be checked after training. Then on *every* graph of any size, (1−Mε)·x_v ≤ h_v ≤ (1+Mε)·x_v.
  - **Gap.** The bound is multiplicative and approximate, not exact. K is fixed, and longer runs are argued only by recurrence. The theorem covers the ℓ₀-regularised loss, not the L1 proxy used in the experiments. The model is a GNN, not an LM.
  - This is the strongest *new* counterexample to C1.
- **Rodionov & Prokhorenkova, ICML 2025** (arXiv 2402.11628 v3). §§4–5 read.
  - **What it does.** A discrete-state, hard-attention GNN processor.
  - **What it proves.** All discrete transitions and attention cases are enumerated, "check[ing] all states change to the correct ones", which guarantees correct execution "for any test data".
  - **Gap.** The states are the benchmark's *hints*, so a designer chose them. The no-hint models, which choose their own states, were never verified and never reached perfect scores. The checks were made by hand.
- **Cai, Shin & Song, ICLR 2017** (map L1 §1.2).
  - A finite verification set proves a recursive NPI correct at any length.
  - **Gap.** The traces, and so what is kept, are supervised.
- **Abate, Giacobbe & Schnitzer, CAV 2024** (doi 10.1007/978-3-031-65633-0_8). Method read.
  - **What it does.** An SMT-based learner fits a decision-tree classifier with per-class ranking functions on sampled states. An SMT verifier then checks the whole infinite state space, and counterexamples go back to the learner.
  - **What it proves.** On acceptance, the partition is a valid stutter-insensitive bisimulation: an abstraction that is *sufficient* for every LTL property. The method is sound but not complete.
  - **Gap.** The system must be given formally, the learner is not neural, and there is no natural language.
  - It counts against C1 for non-neural learners and against C3 for formal tasks.

### C2: pretrained LMs choosing what to carry

- **Lewandowski, Machado & Schuurmans 2026** (map L1 §1.1).
  - Llama-4 executes all 1,857 Lag rules. Fresh-call harness plus per-rule checks gives exactness at unbounded length.
  - **Gap.** The harness fixes the window and the prompt fixes the rules, so the model chooses nothing.
- **Recursion of Thought, Lee & Kim, ACL 2023 Findings** (arXiv 2306.06891).
  - **What it does.** GPT-3 is fine-tuned (along with tiny models) to emit special tokens that open sub-contexts with sub-problems it writes itself. It gets near-perfect scores on arithmetic and algorithmic tasks with very long effective traces.
  - **What it proves.** No guarantee. The paper notes that "it is hard to guarantee high accuracy".
  - **Gap.** The decomposition is learned by imitating designed traces, and there is no certificate.
  - This is the closest earlier work to Savant on parts (a) and (b) of C2. Cite it.
- **The Markovian Thinker / Delethink** (arXiv 2510.06557 v3). Read.
  - **What it does.** R1-Distill-1.5B is RL-trained in 8K chunks. The KV cache is cleared at each boundary, and the query plus the last m = 4K tokens are carried over. The policy learns what to write into that tail.
  - **What it proves.** Nothing about correctness. The formal content concerns cost only ("linear compute with constant memory"), and the authors call their explanations "speculative".
  - **Gap.** No certificate. The carry-over slot is fixed in size, and only its content is learned.
- **Context-Folding** (arXiv 2510.11967).
  - **What it does.** The agent branches into sub-trajectories and folds each into a summary it writes itself, trained with FoldGRPO.
  - **What it proves.** Nothing: the PDF contains no theorem or guarantee.
  - **Gap.** No certificate, and the tasks are deep research and SWE.
- **Recursive Language Models** (arXiv 2512.24601 v3). Read.
  - **What it does.** The root LM writes REPL code that slices the prompt and decides what goes into each sub-call.
  - **What it proves.** Nothing. "Unbounded input tokens" is stated as a goal, the support is empirical, and guardrails are "highly under-explored".
  - **Gap.** No certificate.
- **MemAgent** (ICLR 2026 Oral; 2507.02259), **MEM1** (2506.15841), **InftyThink** (ICLR 2026; 2503.06692), **THREAD** (2405.17402).
  - **What they do.** Memory or summaries written by the LLM, overwritten or consolidated (MemAgent and MEM1 are RL-trained), or child threads it spawns.
  - **What they prove.** None states a theorem, proof or guarantee; I searched the PDF text for these terms. MemAgent's "retain exactly the information needed" is an empirical claim.
  - **Gap.** Choice without a certificate.
- **PENCIL** (map K4) and **Abbe et al. 2024** (map L2 §1.2).
  - PENCIL has a learned reduction rule with a theorem on Turing-machine expressivity. Abbe et al. pin the context by design.
  - **Gap.** Both are trained from scratch, with no certificate of the trained model.
- **Self-proving models, Amit, Goldwasser, Paradise & Rothblum, NeurIPS 2025** (arXiv 2405.15722 v4). Read.
  - **What it does.** A 6.3M-parameter GPT computes GCD and then proves its output to a hand-written verifier.
  - **What it proves.** Soundness for every input (Def. 3.2), with Bézout soundness error 0. Learning guarantees hold only under convexity assumptions.
  - **Gap.** A per-output proof against a formal function, not a pretrained LM. There is no bounded context and no claim about unbounded length; inputs go up to 10⁴.
- **MAKER** (map L1 §1.5).
  - Pretrained LM, with a designer-chosen per-step context.
  - **Gap.** Voting makes it probabilistic, and there is no proof.

**What Savant means for C2.** On the wording, Savant satisfies all three parts:
- a pretrained Qwen3-4B, fine-tuned;
- notes and a table that it writes itself, carried into an isolated KV context;
- a per-row certificate that holds at every length.

So C2 cannot support the sentence "learned, certified abstraction does not exist". Savant's certificate is conditional on the abstraction, which is exactly C3's gap.

### C3: certifying that the chosen abstraction is sufficient

- **Moore 1956; Vasilevskii 1973; Chow 1978** (Chow, doi 10.1109/TSE.1978.231496; Vasilevskii, doi 10.1007/BF01068590; Moore in map L4 §1.4).
  - **What they prove.** If the black box has at most m states, a finite W-method suite proves the hypothesis machine equivalent, so the kept state is sufficient.
  - **Gap.** This needs an oracle for the true task and a state bound. There is no learner and no language.
- **Angluin 1987** (doi 10.1016/0890-5401(87)90052-6) and **Gold 1978** (doi 10.1016/S0019-9958(78)90562-4).
  - Membership and equivalence queries yield the minimal DFA. Gold's characteristic samples identify it from data.
  - Sufficiency is certified only through the equivalence oracle.
- **Givan, Dean & Greig 2003** (AIJ 147:163–223, doi 10.1016/S0004-3702(02)00376-4).
  - Exact bisimulation minimisation of a *known* MDP.
  - The abstraction is computed, not chosen by a model.
- **Delgrange, Nowé & Pérez, ICLR 2023** (arXiv 2303.12558; also the AAAI 2022 version, 2112.09655). §2 read.
  - **What it does.** A neural encoder learns a discrete latent MDP: what is kept.
  - **What it proves.** Local losses bound the bisimulation distance, in expectation under the stationary distribution, and for states sharing a code with weight ξ⁻¹(s). The losses "can be efficiently PAC-estimated". Ergodicity is assumed.
  - **Gap.** The guarantee is statistical and approximate, not a finite exact certificate, and there is no language. This is the closest RL work.
- **Bonet, Francès & Geffner, AAAI 2019** (doi 10.1609/aaai.v33i01.33012703). Theorem 10 read.
  - **What it does.** Features (what is kept) and abstract actions are learned by Max-SAT from sampled transitions.
  - **What it proves.** Theorem 10: *if* the abstraction is sound, the plan solves all instances.
  - **Gap.** Soundness is checked only on the sample. This is the classical analogue of "exact given the abstraction, sufficiency unproved", the same structure as Savant.
- **SemRegex, Zhong et al., EMNLP 2018** (doi 10.18653/v1/D18-1189). Search summaries only; see §3.
  - **What it does.** A seq2seq model writes a regex from natural language.
  - **What it proves.** Minimal-DFA equivalence with a human-written reference regex, used as reward and metric. This is an exact sufficiency check for every string length.
  - **Gap.** It needs a human formal reference for each question, and the model is not a pretrained LLM.
- **L\*LM, Vazquez-Chanlatte et al. 2024** (arXiv 2402.07051). PDF checked.
  - **What it does.** The LLM answers membership queries, and a DFA, which "explicitly encode[s] memory", is identified by SAT.
  - **What it proves.** Only that the DFA is "consistent with the input examples".
  - **Gap.** No equivalence with, or sufficiency for, the natural-language task.
  - Chen, Trivedi & Velasquez (arXiv 2408.02999): the LLM is modelled as a noisy teacher, and correctness assumes an equivalence oracle. Search summary only.
- **LWM-Planner (Fact-Augmented Lookahead), Holt et al., AISTATS 2026** (arXiv 2506.09171). Abstract read.
  - The LLM extracts atomic facts as its abstraction, motivated by bisimulation through a proxy ε_sim.
  - The authors state "without claiming formal guarantees".
  - This is the most direct LLM instance of an abstraction the model chooses without a certificate.
- **WorldCoder, Tang, Key & Ellis 2024** (arXiv 2402.12275). Theorem 2.4 read.
  - The LLM writes world-model code and debugs it until it is consistent with all data.
  - The theorem bounds the actions needed to reach the goal, assuming the true MDP lies in the model class.
  - It gives no certificate that a particular program is sufficient.
- **Clover** (arXiv 2310.17807) and **Astrogator** (arXiv 2507.13290).
  - Formal checking from code to specification.
  - The step from natural language to specification is assumed precise (Clover) or confirmed by the user (Astrogator).
- **Context Compaction Theory, Tirmazi, Markelon, Bishop & Mitzenmacher 2026** (arXiv 2608.01326). Read.
  - The budget for generative compaction equals one-way communication complexity, and selection is strictly weaker.
  - It contains no certificate of an LLM's compaction.
  - It lists efficient compaction that an LLM can compute as open, and its Opus 4.8 case study fails at set membership.
- **DeMem, Zou et al. 2026** (arXiv 2605.10870). Theorem 1 read.
  - **Theorem 1.** Histories can share one memory state iff one action is ε-optimal for all of them. This is a decision-theoretic Nerode condition.
  - The certificates are statistical lower bounds that trigger splits.
  - **Gap.** It does not certify memory written by an LLM, and the sets are finite.
- **Alpay & Alakkad 2026** (arXiv 2606.07623). Abstract only.
  - Finite certificates that a context forces an answer, in families of linear tasks over finite fields.
  - Extracting a smallest forcing subcontext is NP-complete.
  - **Gap.** Formal task families, with no choice by an LLM.

---

## 3. Unverified or partly verified items

- **Bugaud 2026a/b.** Only the abstracts were read (from the map). OpenReview was behind a challenge.
- **SemRegex.** Crossref metadata is confirmed. The DFA-equivalence reward is taken from search summaries; I did not read the full text.
- **Chen, Trivedi & Velasquez.**
  - arXiv 2408.02999 is confirmed, but its method was not read.
  - The claim that its 2026 ICLR follow-up (CAPAL, "persistent noise-tolerant active learning") assumes a perfect equivalence oracle comes from a search summary. I did not open the page or confirm authorship.
- **DeMem venue.** The NeurIPS 2026 poster (neurips.cc/virtual/2026/poster/150643) appeared in search results; arXiv lists no venue.
- **Context-Folding, MEM1, InftyThink, THREAD and MemAgent.** I checked abstracts and searched the PDF text for theorem and guarantee terms; I did not read their method sections in full. Context-Folding's arXiv HTML returned 404.
- **Delgrange et al.** The PAC-estimation theorem itself (in the AAAI 2022 paper) was not read; only the ICLR 2023 §2 statement was.
- **Moore 1956.** Not re-verified (no DOI; in map L4 §1.4).
- **Characteristic samples (RPNI; Oncina & García 1992).** Not verified, so I do not cite them.
- **BEq.** ICLR 2025 proceedings page and FormalAlign (arXiv 2410.10135) came from a search listing; their methods were not read.
- **Venues not confirmed.** Delethink, RLM, Context-Folding, THREAD, MEM1, WorldCoder and Clover. Their arXiv comment fields list none.
- **C3 item 3** (that no finite test can certify sufficiency against the model's own full-context behaviour) is my inference from our `no_finite_test_suite` theorem. It is not checked in Lean.
- **Absence claims.** C2's "TRUE" and C3's "TRUE for LLMs" rest on about 12 searches (standard and extended) and the papers above. A paper from the last few weeks, or one under a workshop-only title, could be missed.
