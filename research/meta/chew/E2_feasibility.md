**Recommendation: fund direction 1’s 48-hour test first, then direction 2. Run one programme at a time.** D3 contains only a work note; direction 5 reconstructs the grammar proposal from the memo.

Common preparation: repair the extra-token contamination and normalization in `research/polybench.py`; preserve `research/lm.py`’s ordinary-attention controls; recover the Nerode metric code at `ed271371`. **Nerode equivalence** groups histories whose answers agree under every permitted continuation; here it supplies exact controls for finite tasks. Replace initial-owner-only training pairs with histories sharing their initial owner but differing in current ownership.

Reuse Sketchpad’s renderer, exhaustive checker and experiment records; new tasks require new certificates. Keep Newton/cubic experiments in small models: these operators are not drop-in Qwen layers. Use Qwen3.5-0.8B/4B for scoring and small trainable adapters. The existing 0.8B workflow is established; verify the 4B checkpoint/cache before budgeting throughput.

**Compute basis:** [Modal list prices](https://modal.com/pricing) give H100 $3.9492/hour and L4 $0.7992/hour. Including CPU/RAM, use **H=$4.394/hour** (H100, four cores, 32 GiB), **L=$1.021/hour** (L4, two cores, 16 GiB), **C=$0.633/hour** (CPU only, eight cores, 32 GiB). Budgets include 25% contingency and exclude labour/recruitment. These are workload allocations, not measured runtimes; benchmark each workload for 30 minutes first.

| Direction | Total H/L/C hours | Compute budget | First 48-hour pilot |
|---|---:|---:|---:|
| 1 | 24/16/20 | $170 | $20 |
| 2 | 18/30/10 | $150 | $17 |
| 3 | 4/80/40 | $160 | $17 |
| 4 | 36/16/100 | $300 | $10 |
| 5 | 40/20/20 | $265 | $25 |

1. **What grammatical memory preserves — four weeks.**

   Computational psycholinguistics already compares memory and word-prediction explanations. [Hahn, Futrell, Levy & Gibson (2022, *PNAS* 119:e2122602119)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9618130/) explained recursive-sentence difficulty through optimized word retention: a mandatory competitor.

   **Data:** StructuralCost, 475 readers/40,800 observations; [download](https://doi.org/10.34847/nkl.7c467lyv) access and licence **unverified**. [Nusbaumer, de-Dios-Flores, Bel, Pallier, Wisniewski & Crabbé (2026, *Findings EMNLP*:28874–28888)](https://aclanthology.org/2026.findings-emnlp.1360.pdf) released it and identified structural costs missing from model predictions. Fallback: [Natural Stories](https://github.com/languageMIT/naturalstories), 10,245 words/181 readers, CC-BY-NC-SA-4.0. [Futrell et al. (2021, *Language Resources and Evaluation* 55:63–77)](https://sites.socsci.uci.edu/~rfutrell/papers/futrell2021natural.pdf) supplied reading times for unusual constructions. Pin the repository’s May-2025 alignment correction.

   **First 48 hours:** enumerate memory distinctions in miniature grammars; compare predictions with recency, retained-word and Qwen probability accounts. Include StructuralCost’s double-embedding speedup: “more states means harder” could fail immediately. Stop if predictions duplicate existing accounts.

   **W1:** reproduce reading-time contrasts; freeze reader/item splits. **W2:** train three equally sized memory learners, three seeds, targeted continuations and longer-training controls. **W3:** erase/restore pending grammatical distinctions, comparing equally disruptive irrelevant erasure. **W4:** test untouched constructions and Natural Stories, controlling frequency, length and word probability.

   **Assumption:** finite grammar distinctions explain human processing. Require construction-specific effects; reader-capacity predictions additionally require StructuralCost access.

2. **Representation changes explain relational errors — four weeks.**

   **Arity** counts inputs combined in one relation; changing their representation can change the apparent arity. Compare interaction order against sequential rules and similarity-based categorization.

   **Data:** [Psych-101 training release](https://huggingface.co/datasets/marcelbinz/Psych-101), 859 MB/~60,100 participant records, Apache-2.0; extract category-learning studies and reserve entire studies. [Binz et al. (2025, *Nature* 644:1002–1009)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12390832/) trained Centaur on this behavioural collection. [REL-Algebra](https://huggingface.co/datasets/mims-harvard/rel): 1,000 questions, MIT. [Fesser, Ektefaie, Fang, Kakade & Zitnik (2026, arXiv:2604.12176)](https://arxiv.org/html/2604.12176) already demonstrated increasing-arity failures.

   **First 48 hours:** reconstruct archived stimuli; identify cases where shortest-rule length, similarity and interaction order predict different errors. Fit simple competitors first. Stop if archived trials cannot distinguish them.

   **W1:** repair Newton controls and enumerate stimulus statistics. **W2:** compare cubic/Newton, repeated ordinary attention, joint-feature readouts and Abstractors under equal measured compute, three seeds. [Altabaa, Webb, Cohen & Lafferty (2024, ICLR; arXiv:2304.00195)](https://arxiv.org/html/2304.00195) already solved SET using relational representations. **W3:** predict held-out human learning transitions; test selective rescue inside Qwen using Sketchpad-rendered intermediate relations. **W4:** replicate across studies and unseen symbols.

   **Assumption:** trajectories constrain representation changes; model interventions cannot establish human causality. [Feldman (2006, *Journal of Mathematical Psychology* 50:339–368)](https://www.researchwithrutgers.org/en/publications/an-algebra-of-human-concept-learning/) already decomposed concepts by feature degree—abstract verified; full text **unverified**.

3. **Which reward-learning memories can observations distinguish? — four weeks.**

   **Identifiability** asks whether observations distinguish competing mechanisms; it prevents declaring a fitted description the true algorithm. Standard alternatives include running reward averages, remembered events and recurrent networks. [Eckstein, Summerfield, Daw & Miller (2026, *Nature Human Behaviour* 10:972–987)](https://pmc.ncbi.nlm.nih.gov/articles/PMC13212159/) found flexible memory outperformed scalar reward estimates. [Ji-An, Benna & Mattar (2025, *Nature* 644:993–1001)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12390849/) extracted strategies from tiny recurrent networks.

   **Data:** Eckstein’s [archive](https://osf.io/8xz3w/), 862 included participants/617,871 trials; access/licence **unverified**. Its [software repository](https://github.com/google-deepmind/hybrid_rnns_reward_learning) separates Apache-2.0 code from CC-BY-4.0 other materials; that does not establish the OSF licence. Psych-101 reward tasks provide the licensed fallback.

   **First 48 hours:** fit three simple mechanisms; find held-out histories with ≥0.1 disagreement in choice probability. Simulate whether available observations distinguish them. Stop if diagnostic histories are too scarce.

   **W1:** reproduce baselines and participant splits. **W2:** fit tiny recurrent models and a Qwen adapter; apply targeted-future training. **W3:** use Nerode enumeration to find separating continuations for finite competitors, then locate corresponding archived trials. **W4:** replicate across another reward task; report interchangeable explanations.

   **Assumption:** informative histories occur naturally. Exact certificates cover specified finite models, not human cognition.

4. **Memory predicts compensation among grammatical cues — five weeks.**

   Linguistic typology compares grammatical systems. [Verkerk et al. (2026, *Nature Human Behaviour* 10:126–136; online 2025)](https://sfb1102.uni-saarland.de/sfbunisb/uploads/2025/11/s41562-025-02325-z.pdf) tested 191 universals with ancestry/geography controls. [Li & Liu (2025, *Entropy* 27:1128)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12651683/) already analysed morphology, order and directionality across 55 languages.

   **Data:** [Grambank v1.0.3](https://zenodo.org/records/7844558), 9.1 MB, 2,467 varieties/195 features, CC-BY-4.0; [Finnish-TDT, UD2.18](https://universaldependencies.org/treebanks/fi_tdt/index.html), 15,136 sentences, CC-BY-SA-4.0, for annotation validation.

   **First 48 hours:** enumerate eight miniature grammars crossing case marking, order freedom and nesting. Compare exact memory costs with ambiguity costs. Stop if predictions coincide or real feature combinations lack coverage.

   **W1:** audit feature definitions/missingness; reserve language families. **W2:** derive predictions before fitting language data. **W3:** train `lm.py` models and Qwen adapters on identical messages rendered under alternative grammars; include models initialized randomly. **W4:** compare memory, communication and pairwise-feature explanations with ancestry/geography controls. **W5:** test unseen families and investigate exceptions.

   **Assumption:** fragment-level memory costs transfer across languages. Another three-way correlation alone is insufficient.

5. **Discover one new grammatical restriction — eight active weeks; conditional.**

   Corpus linguistics uses searches and controlled sentence comparisons. [Yu, Yu, Xiao & Xing (2026, arXiv:2604.07189)](https://arxiv.org/html/2604.07189v1) already automated investigations and replicated findings. [Hu, Wilcox, Song, Mahowald & Levy (2026, *TACL* 14:124–146)](https://aclanthology.org/2026.tacl-1.7.pdf) showed sentence probability confounds grammar with meaning.

   **Data:** [BLiMP](https://huggingface.co/datasets/nyu-mll/blimp), 67,000 sentence pairs, CC-BY-4.0. [Warstadt et al. (2020, *TACL* 8:377–392)](https://aclanthology.org/2020.tacl-1.25.pdf) supplied controlled grammatical contrasts; use them for calibration.

   **First 48 hours:** test Qwen4B proposals and 0.8B scoring against ten hidden synthetic restrictions and 200 meaning-matched contrasts. Proposed gate: recover eight restrictions across unseen words and beat simple substitution search.

   **W1:** calibrate the model informant. **W2:** generate 30 candidates and counterexamples. **W3:** linguist screens novelty. **W4:** register at most three predictions. **W5:** human confirmation. **W6:** independent replication. **W7:** challenge meaning/frequency explanations. **W8:** release surviving rule and discovery trace. Stop at W3 if none survives.

   **Assumption:** a linguist and participant approval are available. Add $2,000–4,000 for participants; collaborator pay and approval delays remain unbudgeted.

These are publication programmes, deferring autonomous internal programming and the investor demo. Task-specific adapters relax condition 1; external Sketchpad assistance relaxes condition 2; all exceed condition 12’s one-week pace. They buy controlled scientific comparisons. Novelty and flagship acceptance remain unverified.