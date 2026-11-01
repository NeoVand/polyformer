**Verdict: PARTIAL; the integrated programme remains OPEN.** Live-web cutoff: **1 November 2026**. “OPEN” means no verified precedent found, not proven absence.

**1. LLM oracle: OWNED broadly; Clark-specific implementation OPEN.**

- [Goertzel, Suárez-Madrigal & Yu (2020, arXiv:2005.12533)](https://arxiv.org/abs/2005.12533) use BERT probabilities for categories, senses, and symbolic link-grammar rule evaluation.
- [Vazquez-Chanlatte et al. (2024, arXiv:2402.07051)](https://arxiv.org/abs/2402.07051), *L*LM*, use LLM membership answers plus demonstrations to learn DFAs.
- [Clark & Eyraud (2007, JMLR)](https://www.jmlr.org/papers/volume8/clark07a/clark07a.pdf) learn substitutable CFGs from positive data alone—not membership queries.
- [Clark (2010, ICGI)](https://www.its.caltech.edu/~matilde/ClarkSyntacticConceptLattice.pdf) learns CFGs using concept lattices, positive data, and membership queries.
- [Clark (2015, Journal of Logic and Computation)](https://doi.org/10.1093/logcom/ext037) develops syntactic concept lattice algebra; its concepts are not simply congruence classes.
- [Yoshinaka (2011, Theoretical Computer Science)](https://doi.org/10.1016/j.tcs.2010.12.058) extends substitutability learning to subclasses of MCFGs.

**2. Explicit grammar plus fidelity to pretrained LLM judgments: PARTIAL.**

- [Li et al. (2024, Findings NAACL)](https://aclanthology.org/2024.findings-naacl.70/) induce compound PCFGs using LLM embeddings; evaluation targets parsing, not oracle fidelity.
- [Bhattamishra, Hahn & Kanade (2026, ICLR)](https://proceedings.iclr.cc/paper_files/paper/2026/file/c541db4fb9e391c377c44e1cebeebe56-Paper-Conference.pdf) extract DFAs approximating truncated LM support, including pretrained BLT models prompted on restricted formal languages.

English CFG/PCFG/MCFG extraction with systematic held-out judgment coverage remains unverified.

**3. Mechanistic substitutability: PARTIAL; causal span-congruence abstraction OPEN.**

- [Jian & Reddy (2023, EMNLP)](https://aclanthology.org/2023.emnlp-main.144/) aggregate attention across syntactic substitutions to induce dependencies.
- [Hewitt & Manning (2019, NAACL)](https://aclanthology.org/N19-1419/) recover tree distances/depths through supervised linear probes.
- [Manning et al. (2020, PNAS)](https://pubmed.ncbi.nlm.nih.gov/32493748/) demonstrate emergent hierarchy, dependency, and coreference information.
- [Murty et al. (2023, ICLR)](https://arxiv.org/abs/2211.01288) project transformer computations onto approximating binary trees without supervised probes.
- [Kryvosheieva et al. (2026, ACL)](https://aclanthology.org/2026.acl-long.7/) causally localize shared units across agreement phenomena.

None establishes that English spans implement two-sided Myhill classes under composition.

**4. Algebraic characterization through LLMs: PARTIAL.**

- [Carrasco, Mayr & Yovine (2024, arXiv:2412.09760)](https://arxiv.org/abs/2412.09760) define probabilistic congruences and actively learn regular LM quotients.
- [Yang, Chiang & Angluin (2024, NeurIPS)](https://arxiv.org/abs/2310.13897) prove star-free expressivity for strictly masked hard-attention transformers without positional embeddings.
- [Strobl et al. (2024, TACL)](https://aclanthology.org/2024.tacl-1.30/) reconcile transformer expressivity results under differing assumptions.
- [Musso et al. (2003, Nature Neuroscience)](https://pubmed.ncbi.nlm.nih.gov/12819784/) find different Broca-area learning responses for “real” versus constructed “unreal” rules.
- [Moro, Greco & Cappa (2023, Cortex)](https://doi.org/10.1016/j.cortex.2023.07.003) argue impossible-language constraints distinguish brains from LLMs.
- [Kallini et al. (2024, ACL)](https://aclanthology.org/2024.acl-long.787/) find GPT-2 learns manipulated “impossible” languages less efficiently than English.
- [Hunter (2025, Computational Linguistics)](https://aclanthology.org/2025.cl-2.7/) identifies a confound in their constituency comparison.

These neither identify English’s syntactic monoid nor establish human/LLM equivalence. Star-free/aperiodic theorems do not transfer wholesale to Qwen.

**5. New human-confirmed linguistic discoveries: PARTIAL; strong version unverified. Debate remains unsettled.**

- [Yu et al. (2026, arXiv:2604.07189)](https://arxiv.org/abs/2604.07189) automate corpus investigations, report intensifier patterns, and replicate published findings; independent confirmation of a previously unknown generalization is unverified.
- [Beguš, Dąbkowski & Rhodes (2025, IEEE TAI)](https://arxiv.org/abs/2305.00948) demonstrate prompted syntactic/phonological analyses, not that discovery-and-confirmation sequence.
- [Piantadosi (2023 preprint; 2024, Language Science Press)](https://lingbuzz.net/lingbuzz/007180) argues LLM success undermines strong generativist claims.
- [Chomsky, Roberts & Watumull (2023, NYT essay)](https://www.nytimes.com/2023/03/08/opinion/noam-chomsky-chatgpt-ai.html) argue prediction lacks human explanatory constraints.
- [Kodner, Payne & Heinz (2023, arXiv:2308.03228)](https://arxiv.org/abs/2308.03228) challenge acquisition realism and prediction-as-explanation.
- [Futrell & Mahowald (2025 online; 2026, BBS)](https://doi.org/10.1017/S0140525X2510112X) advocate LMs as scientific model systems without replacing linguistic theory.
- [Lan, Chemla & Katzir (2024, Linguistic Inquiry)](https://doi.org/10.1162/ling_a_00533) challenge island-learning conclusions using additional generalization tests.
- [Ziv, Lan, Chemla & Katzir (2026, Journal of Language Modelling)](https://jlm.ipipan.waw.pl/index.php/JLM/article/view/457) delimit LLMs’ usefulness as proxies for cognitive theories.

**Necessary corrections.** A finite exact two-sided quotient implies regularity; nonregular syntax requires infinitely many classes or another finite representation. Finite-context clustering establishes only observational equivalence. Lattice concepts permit overlapping categories. Acceptance alone cannot identify semantic interpretations. [Chomsky (1957, *Syntactic Structures*, Mouton)](https://danielwharris.com/teaching/364/readings/ChomskySyntactic.pdf) rejects requiring discovery procedures; he does not prove their impossibility.

**(a) Remarkable result.** An automatically extracted, compact grammar that predicts a previously unknown human constructional restriction, survives independent preregistered human testing, and corresponds to causally interchangeable model computations. No verified precedent found for that combination.

**(b) Closest attempt.** Goertzel et al.: essentially the proposed oracle-to-symbolic-grammar architecture. Their grammar-rule demonstration used six words; it rejected all six injected bad rules but also three valid rules. Broad coverage and causal validation were absent.

**(c) Most dangerous paper.** [Hu, Wilcox, Song, Mahowald & Levy (2026, TACL)](https://aclanthology.org/2026.tacl-1.7/) analyze and test 280,000 English/Chinese pairs: probability conflates grammaticality with message probability. This undermines raw-probability membership thresholds. Meaning-controlled contrasts and calibrated, explicitly approximate oracles remain viable.

**(d) Two-week pilot.** Use [Qwen3.5-0.8B-Base and 4B-Base](https://huggingface.co/collections/Qwen/qwen35) on agreement and NP substitution. Days 1–3: calibrate and freeze acceptability scoring against 300 human judgments. Days 4–9: query 200 spans ×100 two-sided contexts; infer classes and a CFG capped at 50 nonterminals/200 rules. Hold out lexemes, contexts, and embedding depths; compare n-gram and ordinary PCFG baselines. Days 10–14: measure balanced oracle fidelity and matched within-/between-class activation swaps.

Preregister a kill criterion: **held-out fidelity below 80%**, despite oracle–human agreement above 90%, kills this compact extraction pilot. It does not falsify every Harris-style learner.