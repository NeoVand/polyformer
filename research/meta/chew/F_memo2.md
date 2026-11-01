# MEMO v2 — 1 November 2026

## 1. Three bets, ranked

**Start with relational reasoning; switch to sentence memory if human-study approval cannot arrive by week two.** I rank expected scientific value, including a strong specialist paper, rather than headline size. Assumptions: one full-time researcher; existing hardware; salary and publication charges excluded; ten weeks to a manuscript. No direction promises the complete architecture. Abstracts below describe hoped-for results, exactly 120 words each. Odds are subjective eventual-acceptance estimates from launch, including project failure—not measured probabilities.

### 1. “When extra time and intermediate relations rescue human reasoning”

**Arity** counts inputs combined in one relation; it distinguishes joint processing from simply remembering more objects. This is cognitive psychology: compare mechanisms through controlled tasks and interventions.

**Hoped-for abstract**

Why do people fail to combine relationships they understand separately? We test whether time pressure limits the interactions available to a decision, rather than imposing a fixed ceiling on the number of objects represented. Controlled tasks keep objects, answers and simpler statistical relationships constant while changing which combinations determine the answer. Competing models predict specific choice patterns before human testing. Additional time and an intermediate relation selectively restore the missing pattern, whereas reducing visual similarity repairs a different class of errors. Predictions transfer across unfamiliar symbols and two task families in independent participants. The results identify when relational reasoning fails and how representations rescue it, while distinguishing effective computational limits from claims about the elementary operations performed by biological neurons.

**Decisive test / kill.** Predict complete choice patterns under deadlines, extra time and supplied intermediate relations; independently vary visual similarity. Freeze predictions across two task families. Compare repeated two-input processing, joint three-input processing, rule learning, similarity and mixtures of strategies at matched measured computation. Require selective rescue and independent replication. Kill before recruitment if competitors agree, simulated evidence needs more participants than the budget permits, or approval misses week two. Kill the headline if only overall accuracy improves.

**First 48 hours:** enumerate small cue-controlled tasks. Let Pij be the probability of choosing pair (i,j) among all four pairs. A fixed, single-stage sum of the three pair scores predicts P11P22/(P12P21) stays constant across cues; test this restriction and rescue by repeated processing. Fix scaling that suppressed larger interactions and remove the unintended extra input token. No participants; cap $75.

**Verified prior art.** [Halford, Wilson & Phillips (1998, *Behavioral and Brain Sciences* 21:803–831)](https://staff.aist.go.jp/steven.phillips/papers/relational_complexity.pdf) already proposed relational limits and decomposition: **most dangerous paper**. [Feldman (2006, *Journal of Mathematical Psychology* 50:339–368)](https://www.researchwithrutgers.org/en/publications/an-algebra-of-human-concept-learning/) decomposed concepts by how many features a regularity involves; abstract verified, full text **unverified**. [Altabaa, Webb, Cohen & Lafferty (2024, ICLR; arXiv:2304.00195)](https://arxiv.org/html/2304.00195) solved relational tasks using separated relational representations. [Shang, Kreiman & Sompolinsky (2026, *Scientific Reports* 16:22146)](https://pmc.ncbi.nlm.nih.gov/articles/PMC13369344/) linked human difficulty to distances among model representations. Another correlation is insufficient.

**Cost/odds/learning:** $3,500–4,500, including roughly 240 adults across discovery/replication, computation and contingency. Nature 1–3%; Nature Human Behaviour 5–12%; Cognitive Science 35–55%. Assumption: interventions distinguish mechanisms without teaching the answer. Failure still identifies whether our advantage comes from representation, repeated processing or joint operations; it cannot identify biological circuitry.

### 2. “Which grammatical distinctions must readers remember?”

**Nerode equivalence** groups histories giving the same answers under every permitted continuation. For grammars with fixed vocabulary and length limits, it identifies exactly what compression loses; relevance to human reading remains a hypothesis. Sentence-processing research normally compares word prediction, word retention and structural memory.

**Hoped-for abstract**

What information must readers preserve while a sentence unfolds? We compare memory for words with memory for distinctions that change how a sentence can legally continue. Within bounded grammars, these distinctions are calculated exactly, allowing controlled removal of information without changing other properties of the model. Under matched memory budgets, the resulting account predicts specific reading difficulties across withheld constructions and independent human datasets, beyond word predictability, distance and existing structural memory measures. It also predicts when greater nesting does not increase difficulty. Removing and restoring particular distinctions changes model predictions selectively. These findings explain which information a useful compressed representation must retain, while separating mathematical guarantees about finite models from empirical claims about the mechanisms that support human language.

**Decisive test / kill.** Match memory capacity by the number of distinguishable stored states. Remove/restore particular unfinished grammatical obligations inside models; predict reserved constructions and independent reading datasets beyond word probability, distance and existing memory measures. Require specific effects, including cases where deeper nesting speeds reading. Kill if predictions duplicate prior accounts, depend on privileged grammatical information absent from competitors, or yield only better average fit. Model interventions establish model causality; archived reading remains observational.

**First 48 hours:** reproduce one nesting contrast; enumerate a tiny grammar; find a prediction separating word-retention and obligation-retention accounts. Verify StructuralCost access and licence; otherwise use corrected Natural Stories and OneStop, verifying download access before continuing. Cap $75.

**Verified prior art.** [Hahn, Futrell, Levy & Gibson (2022, *PNAS* 119:e2122602119)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9618130/) explained recursive difficulty through optimized word retention. **Most dangerous:** [Yoshida, Isono, Kajikawa, Someya, Sugimoto & Oseki (2025, ACL:9795–9812)](https://aclanthology.org/2025.acl-long.483.pdf) already compared structural and word memory. [Kajikawa, Isono & Wilcox (2026, CoNLL:15–33)](https://arxiv.org/html/2602.18217) predicted reading costs from information retained for future words; [Isono & Kajikawa (2026, CoNLL:57–69)](https://arxiv.org/html/2604.27468) tested structurally guided maintenance. Novelty must concern **which distinctions disappear**, not “structure matters.”

**Data:** [Nusbaumer, de-Dios-Flores, Bel, Pallier, Wisniewski & Crabbé (2026, Findings EMNLP:28874–28888)](https://aclanthology.org/2026.findings-emnlp.1360.pdf) introduced StructuralCost; download/licence remain **unverified**. [Futrell, Gibson, Tily, Blank, Vishnevetsky, Piantadosi & Fedorenko (2021, *Language Resources and Evaluation* 55:63–77)](https://sites.socsci.uci.edu/~rfutrell/papers/futrell2021natural.pdf) released Natural Stories; use its [May-2025 alignment correction](https://github.com/languageMIT/naturalstories). [Berzak, Malmaud, Shubi, Meiri, Lion & Levy (2025, *Scientific Data* 12:1995)](https://www.nature.com/articles/s41597-025-06272-2.pdf) released OneStop reading measurements; download access remains **unverified**.

**Cost/odds/learning:** $700–1,500 with contingency. Nature <1%; Nature Human Behaviour 3–8%; TACL/Cognition 30–50%. Assumption: bounded grammar distinctions transfer to natural reading. Failure teaches whether formal memory sufficiency predicts human difficulty at all.

### 3. “When human choices distinguish reward memory from habit”

**Identifiability** means observations distinguish competing explanations; good prediction alone does not establish the internal mechanism. This is computational decision science. A **recurrent model** carries internal state between choices, letting us test what information prediction requires.

**Hoped-for abstract**

Which memories are actually required to explain human learning from rewards? Flexible models predict choices well, but different internal stories can support similar predictions. We compare accumulated reward estimates, recent event memories, repeated choice habits and small recurrent models across independent datasets. For specified finite models, we identify histories that produce identical future choices and calculate continuations that separate competing explanations. Tests on untouched participants show which memory distinctions observations require, which remain interchangeable and which cannot be judged from available trials. A targeted reanalysis changes a substantive conclusion about the information supporting adaptive choice without sacrificing predictive accuracy. The results separate behavioral evidence from interpretation and identify concrete experimental sequences that would resolve remaining disagreements about human learning mechanisms.

**Decisive test / kill.** Compare reward averaging, remembered events, repeated-choice habits and small networks with persistent internal state. Find sequences where predictions separate; test reserved participants and a different task. Require a changed substantive conclusion about memory or reward dependence. Exact guarantees cover specified finite models only. Kill if distinguishing histories are rare, simulated choices cannot identify their generating model, or the result merely repeats known ambiguity.

**First 48 hours:** reproduce one published contrast from Collins’s accessible [code/data](https://github.com/AnneCollins/WMH); fit simple alternatives; measure coverage of histories with at least 0.1 disagreement in choice probability. Cap $50. No large language model needed.

**Verified prior art. Most dangerous:** [Collins (2026 issue; online 2025, *Nature Human Behaviour* 10:357–369)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12932107/) already reanalysed seven datasets and favoured short-term memory plus habits over reward averaging. [Eckstein, Summerfield, Daw & Miller (2026, *Nature Human Behaviour* 10:972–987)](https://pmc.ncbi.nlm.nih.gov/articles/PMC13212159/) found flexible memory improved reward-learning models—and already checked recovery of the generating model from simulated choices. [Ji-An, Benna & Mattar (2025, *Nature* 644:993–1001)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12390849/) extracted strategies from tiny recurrent networks. [Shalizi & Crutchfield (2001, *Journal of Statistical Physics*; arXiv:cond-mat/9907176)](https://arxiv.org/pdf/cond-mat/9907176) established minimal summaries sufficient for predicting futures. The opening is a new boundary across tasks.

**Cost/odds/learning:** $300–1,000 with contingency. Nature <1%; Nature Human Behaviour 2–5%; Journal of Mathematical Psychology 25–40%. Assumption: archives contain separating evidence. Failure identifies useful experimental sequences and what existing evidence cannot decide.

## 2. What changed, and why

- **Keep #1, narrow its claim.** The [audit](/Users/neo/repos/polyformer/research/meta/survive/AUDIT.md) preserves restricted choice-score constraints, not a universal human limit or ordinary-network impossibility. Equal class means do not imply indistinguishable classes. Repetition and representation changes are mandatory controls.
- **Replace grammar discovery and transmission.** Novel grammar requires expert novelty adjudication and unpredictable discovery; the original transmission budget was $6–10k. Neither fits a dependable solo ten-week programme.
- **Promote archived human evidence, reduce novelty claims.** The newly checked sentence-memory papers and Collins substantially narrow D4/E2’s openings. Cheap computation does not imply a four-week flagship paper.
- **Use corrected memory training.** Averaging over every possible future can mark exactly the same histories equivalent as testing every future. Earlier training allowed remembering initial ownership instead of current ownership.
- **Evidence gaps:** D3 is an unfinished work note; E1 is empty. They supply no grammar review or referee endorsement.

## 3. Rejected directions

- New grammatical restriction: discovery and expert-validation risk; reserve for collaboration.
- Human transmission chains: exceeds this budget at credible replication scale.
- Universal four-relation limit: representation and sequential computation defeat the framing.
- Indirect grammar evidence, erasure and repair: extensions require a demonstrably new mechanism.
- Standalone attention, exact calculators and entity tracking: useful engineering reserve; no surviving broad language gain.
- Typological universals: ancestry, annotation and existing explanations overwhelm a short solo study.
- Brain alignment: archival data exist, but methodological and domain-learning costs are high.
- Formal-paper error census: expert verification dominates; selected errors cannot estimate prevalence.
- Cross-species unbounded memory, Linear A, Voynich and whale translation: inadequate independent evidence for the intended claim.
- Centaur successor, cap-set records and historical rediscovery: poor resource advantage or contamination control.

## 4. Citations and claims that were wrong

D1’s 48/48 finding covers C/B1/A1, not the entire folder.

- A3 gives Sanford the wrong identifier, **2306.02596**. Correct: [Sanford, Hsu & Telgarsky (2023, NeurIPS; arXiv:2306.02896)](https://arxiv.org/html/2306.02896), restricted shallow-attention limitations.
- A3/B2 give Abbe the wrong identifier, **2304.03752**. Correct: [Abbe, Boix-Adserà & Misiakiewicz (2023, COLT; arXiv:2302.11055)](https://proceedings.mlr.press/v195/abbe23a/abbe23a.pdf), a learning-complexity result under restricted assumptions. Its “leap”—the largest batch of new inputs introduced along the best ordering—does not mean the lowest nonzero degree.
- [Noy & Zhang (2023, *Science* 381:187–192)](https://shakkednoy.com/Noy%20Zhang%20NBER%20SI.pdf), randomized writing assistance: **40% less time**, not “40% faster.”
- [Ding (2026, arXiv:2610.36797)](https://arxiv.org/html/2610.36797v1), separated interpretation persistence from adaptation: 24 models overall, five for continuation interventions, nine for main internal interventions.
- [Dai, Zhou, Viswanathan & Frank (2026, arXiv:2610.22919)](https://arxiv.org/html/2610.22919v1), removed indirect grammatical evidence: five training runs, not five architectures.
- [Salvi, Horta Ribeiro, Gallotti & West (2026 correction, *Nature Human Behaviour* 10:2047)](https://www.nature.com/articles/s41562-026-02588-0) corrected personalization’s added advantage over ordinary GPT-4 to inconclusive, P=.0678.
- [Costello, Pennycook & Rand (2024, *Science* 385:eadq1814)](https://pubmed.ncbi.nlm.nih.gov/39264999/) reported lasting conspiracy-belief reductions; an omitted [2026 erratum, no authors listed, *Science* 394:eaem1178](https://pubmed.ncbi.nlm.nih.gov/42912168/) exists. Corrected estimates remain **unverified**.

## 5. Decisions for Neo

1. **Accept a scientific question as the deliverable?** These options defer conditions 2–7’s internal execution/certification, 9–10’s language-preserving architecture and 11’s investor demo. This buys tractable tests against human evidence. Your ten-week/$5k limit replaces condition 12.
2. **Human access or archives?** Choose #1 only with a credible approval route by week two; otherwise #2. Choose #3 for a theory-first, lower-cost reserve.
3. **One bet, staged spending.** Fund one 48-hour test; cap week-one spending at $300. Freeze predictions by week two; reserve weeks seven–eight for replication and nine–ten for writing.
4. **Does a strong specialist paper count as success?** It should. A Nature-only objective makes all three poor bets.