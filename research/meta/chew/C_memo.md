# CHEW_MEMO

## 1. The three best directions, ranked

**Rank by value of the next experiment: relational learning first, grammar discovery second, transmission third.** These are cognitive-science projects: experiments explaining how people learn. Their standard tools are controlled training, competing explanations and independent human tests.

All abstracts below describe **hoped-for results, not findings**. Live checks are current to 1 November 2026; uniqueness remains **unverified**.

### 1. “A shared interaction bottleneck predicts human and machine learning”

An interaction depends jointly on several inputs. Pairwise statistics summarize two inputs at a time; controlling these helps isolate relationships involving more inputs. This ranks first because it offers the cheapest decisive use of our surviving mathematical mechanism.

**Prospective abstract — 120 words**

Why are some concepts easy to learn and others stubbornly difficult? We test whether difficulty depends on which combinations of information a learner can use, beyond the length of the rule describing the answer. Carefully constructed visual tasks hold individual features and pairwise statistics constant while changing the relationships that determine category membership. Neural models generate predictions for learning speed, errors and transfer before human testing. Instructions and an additional memory task then change which strategies participants can employ. We show that one quantitative account predicts these changes across unfamiliar task families and visual formats. The results connect a controllable computational mechanism to human learning, explaining when compact rules remain difficult and when changes in representation make those rules accessible.

**Decisive experiment and kill:** Compare our mechanism for jointly scoring triples with ordinary networks, rule learners and models recalling similar examples. Exhaustively check the stimulus statistics; match training and computation budgets. Freeze predictions before testing people, reserving two entire task families. Kill before recruitment if predictions do not separate; kill the scientific claim if it cannot outperform alternatives on both reserved families and predict the intervention’s effect.

**Prior art: partial. Most dangerous:** [Shang, Kreiman & Sompolinsky (2026, *Scientific Reports* 16:22146)](https://pmc.ncbi.nlm.nih.gov/articles/PMC13369344/) already connected model representations to human relational difficulty. [Halford, Wilson & Phillips (1998, *Behavioral and Brain Sciences*)](https://staff.aist.go.jp/steven.phillips/papers/relational_complexity.pdf) explained capacity through jointly processed relationships. [Feldman (2000, *Nature*)](https://pubmed.ncbi.nlm.nih.gov/11034211/) linked concept difficulty to shortest rule length. Our opening is a quantitative prediction of intervention effects across new families.

**Time/cost:** One-week model gate, $100–300; full study 6–8 weeks, $2–4k, including participants.

**What could go wrong / assumption:** People may use strategies absent from our models. The [local audit](/Users/neo/repos/polyformer/research/meta/survive/AUDIT.md) does not establish a universal accuracy law or unrestricted impossibility claims against ordinary networks. We assume an informative contrast survives those corrections.

**Why Nature would care:** A transferable explanation of learning difficulty, supported by successful interventions, could connect machine learning to a longstanding question about thought. Another accuracy correlation would not.

### 2. “Language models reveal an overlooked constraint on human grammar”

A language model predicts text from prior text. Here it supplies candidate discoveries; people determine whether those discoveries describe human language.

**Prospective abstract — 120 words**

Can a language model help discover a fact about human grammar that was previously unknown? We introduce a procedure that proposes compact restrictions by comparing expressions across carefully matched sentence contexts. Independent linguists assess novelty without knowing which method proposed each candidate. Before collecting confirmation data, we fix predictions for unfamiliar words, new constructions and competing explanations. Human judgments then confirm a restriction that existing accounts fail to predict, and a second sample reproduces the effect. Comparisons with simple search and expert proposals measure whether the procedure improves discovery rather than merely generating plausible examples. The resulting rule identifies a previously overlooked boundary in grammatical knowledge and establishes a reproducible method for turning statistical models into instruments of linguistic discovery.

**Decisive experiment and kill:** Generate 30 candidate rules; have a linguist independently screen novelty; fix at most ten confirmation tests with correction for testing multiple candidates. Compare against expert proposals and simple automated searches. Require one new rule to replicate in separate participants and unseen words, then survive competing explanations. Kill if every confirmed rule is known, meaning-dependent or confined to particular words.

**Prior art: partial. Most dangerous:** [Yu, Yu, Xiao & Xing (2026, arXiv:2604.07189)](https://arxiv.org/abs/2604.07189) automated corpus investigations and replicated published linguistic findings. [Hu, Wilcox, Song, Mahowald & Levy (2026, *TACL* 14:124–146)](https://aclanthology.org/2026.tacl-1.7/) showed why sentence probability confounds grammar with message plausibility. The remaining claim is an independently established new restriction, not automated linguistics itself.

**Time/cost:** Two-week discovery gate, $300–800; full study 8–10 weeks, $3–6k, plus a linguistics collaborator.

**What could go wrong / assumption:** English is heavily studied; apparent discoveries may be memorized scholarship or ordinary meaning effects. We assume a sufficiently consequential unknown rule exists. Finite sentence samples cannot establish an exact finite grammar for unrestricted English.

**Why Nature would care:** A machine-assisted discovery that changes a linguistic explanation would demonstrate scientific value beyond reproducing known judgments. This has the largest headline upside and least predictable yield.

### 3. “Memory limits determine which grammars survive transmission”

Transmission means learning from a previous learner’s productions. It lets us distinguish acquiring a rule from preserving it across people.

**Prospective abstract — 120 words**

Why do some learnable language patterns rarely survive in human communication? We separate learning a rule from reproducing it reliably for another learner. Participants and neural models first acquire matched miniature languages to comparable levels of understanding. Their productions become training material for successive learners, while a randomized memory aid changes production demands without supplying the correct grammatical answer. We show that particular rules disappear despite successful initial learning, and that memory support selectively preserves them. Predictions fixed using model experiments anticipate the direction and size of human changes across several rule families. These findings identify a causal pathway from individual production limits to collective language structure, while distinguishing transmission pressures from claims that the disappearing rules cannot be learned.

**Decisive experiment and kill:** Use three rule families, independent five-generation chains and randomized production-memory support. Match initial understanding within a prespecified tolerance; retain a communication task so losing expressive distinctions is costly. Freeze model predictions before human chains. Kill if initial learning differences explain disappearance, the memory aid teaches the rule, or selective rescue fails in adequately sized confirmation tests.

**Prior art: partial. Most dangerous:** [Janarthan, Haley & Goldwater (2026, *CoNLL*; arXiv:2606.30815)](https://aclanthology.org/2026.conll-main.24/) already found production failures and explicitly proposed transmission failure. [Cornish, Dale, Kirby & Christiansen (2017, *PLOS ONE* 12:e0168532)](https://pubmed.ncbi.nlm.nih.gov/28118370/) already showed memory-constrained human transmission producing language-like structure. Novelty requires selective rescue after equivalent learning.

**Time/cost:** Two-week model gate, $300–800; full study 8–12 weeks, $6–10k. Participant recruitment and study approval dominate.

**What could go wrong / assumption:** A memory aid may change attention or strategies; chains may simplify everything. Equal machine complexity does not establish equal psychological difficulty. We assume adult miniature-language experiments can reveal a mechanism; they cannot settle why all natural languages have their observed forms.

**Why Nature would care:** A causal explanation of why a learnable rule disappears could clarify how individual limitations shape collective language. Broad confirmation would be needed for the main journal.

## 2. Directions considered and rejected

- **Indirect evidence teaches missing grammar:** downgrade B1’s winner; [Dai, Zhou, Viswanathan & Frank (2026, arXiv:2610.22919)](https://arxiv.org/abs/2610.22919) already identified influential indirect evidence and tested removal across fifteen phenomena and five models.
- **Training-data changes alone:** [Leong & Linzen (2026, *Journal of Memory and Language* 149:104751)](https://tallinzen.net/media/papers/leong_linzen_2026_jml.pdf) already combined human judgments with removal, alteration and insertion of training sentences.
- **“Settle impossible languages”:** [Hunter (2025, *Computational Linguistics* 51:641–650)](https://aclanthology.org/2025.cl-2.7/) exposed a locality confound; matching formal size cannot eliminate every difference in human difficulty.
- **Memory erasure:** [Gong (2026, arXiv:2610.21176)](https://arxiv.org/abs/2610.21176) already separated retrieval from interference and improved decisions by suppressing distractors.
- **Sentence-repair mechanism:** [Ding (2026, arXiv:2610.36797)](https://arxiv.org/abs/2610.36797) already separated abandoned interpretations from adaptation through model interventions.
- **Cross-species memory census:** finite observations cannot prove unbounded memory; results depend on the fitted model and grouping tolerance.
- **Entity tracking and detours:** valuable engineering, but [Sarkar, Mukherjee & Sato (2026, arXiv:2610.34945)](https://arxiv.org/abs/2610.34945) already proposed entity-specific relational operators and tested composition.
- **Certified mathematics audit:** [She & Wang (2026, arXiv:2610.35596)](https://arxiv.org/abs/2610.35596) checked statistical papers with Lean and recovered errors; representative prevalence estimation needs substantial expert verification.
- **Standalone attention, exact calculators and recovered state machines:** retain useful components; the audit leaves no demonstrated broad language improvement from higher-order interactions.
- **Self-training counterexamples and Centaur-2:** insufficiently distinct from established programmes.
- **Brain-based model selection:** new measurements require a laboratory and a longer schedule.
- **Linear A, Voynich and whale translation:** insufficient independent evidence to check the intended headlines.
- **Cap-set records and historical rediscovery:** respectively weak competitive advantage and difficult contamination control.
- **Word-order universals:** too mature for a broad rediscovery claim; a specific new intervention would be required.

## 3. Decisions Neo must make

1. **Scientific publication or the complete model dream?** These options defer conditions 2–7’s internal execution and certification, condition 10’s new language-model architecture, and condition 12’s one-week budget. They buy independent scientific tests. If those conditions remain mandatory, choose an engineering paper and lower the Nature expectation.
2. **Stage spending:** My recommendation is a seven-day, $300 ceiling for direction 1’s discriminating experiment, with explicit stop rules. Do not launch all three programmes. Release participant funding only after the model gate survives.
3. **Accept collaboration and timing:** Recruit a cognitive scientist for 1 or 3, a linguist for 2. Costs exclude salary; approval delays and publication time are additional.
4. **Choose the publication threshold:** My subjective odds for eventual main-*Nature* acceptance are **below 5% for each direction**, not statistical estimates. *Nature Human Behaviour* is more plausible, still uncertain. A sound specialist paper should count as success.

The precedents justify ambition, not a solo shortcut: [Lake & Baroni (2023, *Nature*)](https://www.nature.com/articles/s41586-023-06668-3.pdf) reproduced human generalization with two authors; [Binz and colleagues (2025, *Nature*)](https://www.nature.com/articles/s41586-025-09215-4.pdf) trained Centaur on ten million choices across 160 experiments with forty authors. Their strength was consequential scientific evidence.