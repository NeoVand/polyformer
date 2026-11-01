**Pilot direction 2 first: identify the experiences that produce grammatical generalization. Direction 1 has the broadest headline; direction 3 offers a plausible Nature Human Behaviour route.** The strongest opportunity is a new explanation of human language, tested through interventions.

The frontier, verified through **1 November 2026**:

- **Acquisition.** *Poverty of the stimulus* means that children’s experience allegedly cannot explain their grammatical knowledge; the decisive issue is which information suffices. [Vong, Wang, Orhan & Lake (2024, Science)](https://pubmed.ncbi.nlm.nih.gov/38300999/) learned word–referent mappings from 61 hours of one child’s recordings. [Charpentier et al. (2025, BabyLM Workshop)](https://aclanthology.org/2025.babylm-main.28/) extended training on child-scale word budgets to interaction and human-likeness evaluations. [Yang, Bisazza, Schneider & Wilcox (2026, arXiv:2602.09992)](https://arxiv.org/abs/2602.09992) found generalization without direct examples at 10M words, but weaker learning efficiency than children.

- **Universals and impossible languages.** *Typology* compares languages; *universals* are proposed shared constraints or tendencies. Their explanation could distinguish biological restrictions from learning and cultural pressures. [Kallini, Papadimitriou, Futrell, Mahowald & Potts (2024, ACL)](https://aclanthology.org/2024.acl-long.787/) found slower learning of manipulated “impossible” English. [Xu, Kuribayashi, Oseki, Cotterell & Warstadt (2026, TACL)](https://aclanthology.org/2026.tacl-1.27/) extended preferences to subtle English/Japanese word-order manipulations. [Ziv, Lan & Chemla (2026, EACL)](https://aclanthology.org/2026.eacl-long.249/) found no systematic possible/impossible separation across a wider sample. Unattested does not establish unlearnable.

- **Emergent syntax.** [Yao, Boguraev, Pimentel & Mahowald (2026, EMNLP)](https://aclanthology.org/2026.emnlp-main.732/) found agreement mechanisms reorganizing after behavior stabilized. [Boguraev, Nakai, Mahowald & Steuer (2026, arXiv:2608.28924)](https://arxiv.org/abs/2608.28924) transferred grammatical mechanisms across languages, with stronger transfer between similar languages. Finding another grammatical circuit is insufficient novelty.

- **LLM informants.** An *informant* supplies judgments used to infer grammar; reliability determines whether discoveries concern people or model artifacts. [Hu, Wilcox, Song, Mahowald & Levy (2026, TACL)](https://aclanthology.org/2026.tacl-1.7/) explained why meaning-matched sentence contrasts outperform absolute probabilities. [Winston & Kolter (2026, ICML)](https://proceedings.mlr.press/v306/winston26a.html) trained tiny models on grammatical nonsense, separating syntactic competence from world knowledge. Meaning control is now an experimental variable.

- **Psycholinguistics.** *Surprisal* measures how unexpected a word is; it connects model probabilities to reading difficulty. [Oh, Zhu & Schuler (2025, Findings ACL)](https://aclanthology.org/2025.findings-acl.91/) showed that larger models’ poorer reading-time predictions persist without substantial training/test overlap. [Timkey, Huang, Oh, Prasad, Arehalli, Linzen & Dillon (2026, PNAS)](https://pmc.ncbi.nlm.nih.gov/articles/PMC13462876/) separated early prediction-related costs from additional rereading costs in 368 participants. “Prediction is insufficient” is already published.

- **Neuroscience.** *Brain–LM alignment* means predicting brain activity from model representations; it does not establish identical computations. [AlKhamissi et al. (2025, EMNLP; arXiv:2503.01830)](https://arxiv.org/abs/2503.01830) found alignment tracking grammatical competence more closely than reasoning. [Cai, Kfir, Jamali et al. (2026, Nature)](https://www.nature.com/articles/s41586-026-10691-5) mapped linguistic information in individual neurons during speech production. Crucially, [Hadidi, Feghhi, Song, Blank & Kao (2026, Nature Communications)](https://doi.org/10.1038/s41467-026-72253-7) showed that data splitting, word rate and positional signals can produce misleading alignment.

These are **cognitive-science experiments** using controlled learning, behavioral testing and model-guided brain experiments. **Assumption:** publication takes priority over immediately satisfying conditions 5/10/11—certification, a new architecture and a browser demo. Existing architectures isolate explanatory variables; inventing an architecture could satisfy condition 10 but adds confounds. Full human studies relax condition 12’s week/$2k limit. Costs below are planning estimates, excluding salary.

1. **“Language universals emerge from failures of cultural transmission.”**

   **Question:** Are absent grammars unlearnable, or learnable but unstable when passed between speakers?

   **Decisive experiment:** Train fresh, open GPT-2-style models on matched miniature languages; require equal initial comprehension. Cross short/long dependencies with generous/restricted production memory, then transmit generated utterances through five learner generations. Use exact grammar checks. Predict which rules disappear, then test human transmission chains. A reversal caused by memory support would distinguish a production constraint from categorical unlearnability.

   **Most dangerous prior:** [Janarthan, Haley & Goldwater (2026, CoNLL)](https://aclanthology.org/2026.conll-main.24/) already found relatively preserved grammatical judgments but poor long-sentence generation in impossible languages. Novelty requires actual transmission and human intervention.

   **Kill:** disappearance follows initial learning differences, or humans show no predicted memory-dependent reversal.

   **Cost/assumption:** $500–1,500, two-week model pilot; $3–6k and 6–10 weeks for adults. Adult miniature-language learning tests this mechanism, not childhood acquisition. **NHB plausible; Nature possible with convergence across several grammatical families.**

2. **“Indirect experience supplies the missing evidence for grammar.”**

   **Question:** Which ordinary constructions teach a rule never directly demonstrated?

   **Decisive experiment:** Retrain open 30–125M-parameter models on 10M words with direct question-formation evidence removed. Remove candidate sources of indirect evidence, then restore them with controls matched for vocabulary, length and frequency. Freeze the predicted teaching set; test unseen words and constructions, followed by randomized miniature-language learning in people.

   **Most dangerous prior:** Yang et al. (2026), above, already filter direct evidence. [Yao, Misra, Weissweiler & Mahowald (2025, arXiv:2503.20850)](https://arxiv.org/abs/2503.20850) manipulated input to identify direct and indirect sources of grammatical preferences. The advance must be a specific explanatory teaching set with prospective human confirmation.

   **Kill:** restoration fails across five seeds and two architectures, unrelated examples work equally well, or human transfer fails.

   **Cost/assumption:** $500–1,500 and two weeks for models; child validation needs a collaborator, months and roughly $5–15k. **NHB plausible; Nature only with broad developmental confirmation.** Success could refute a specific necessity claim, not all innate contributions.

3. **“A shared repair algorithm explains human and machine sentence comprehension.”**

   **Question:** What computation causes extra difficulty when a sentence forces reinterpretation?

   **Decisive experiment:** Use open Pythia/GPT-2 models to identify representations of competing interpretations. Replace those representations experimentally and derive a compact repair model. Compare it with prediction-only and memory-retrieval accounts. Select new sentences where the accounts disagree; independently match human next-word expectations. Preregister predictions for reading delays and persistent wrong interpretations, then test new participants. Neo’s experience with explicit computational states could make the proposed repair operations inspectable.

   **Most dangerous prior:** Timkey et al. (2026, PNAS), above, already establish the behavioral dissociation. [Barenholtz (2026, arXiv:2606.05346)](https://arxiv.org/abs/2606.05346) predicts additional reading costs from hidden-state trajectories. Another correlation adds little.

   **Kill:** the repair model fails held-out constructions or offers no prospective advantage over either alternative.

   **Cost/assumption:** $300–800 compute plus $2–4k participants, four–eight weeks. Assumes model interventions yield transferable behavioral predictions. **NHB plausible; Nature unlikely without a broader principle.**

4. **“Human language cortex selects among equally predictive algorithms.”**

   **Question:** Does brain alignment identify grammatical computation or merely shared predictive information?

   **Decisive experiment:** Construct open small models with different experimentally verified grammatical mechanisms, matched on trial-level word probabilities. Fit equally constrained brain-prediction models to public recordings; freeze competing predictions for novel, meaning-controlled sentences. Test these prospectively with a neuroscience collaborator. Model interventions establish causality inside the model; human measurements test correspondence.

   **Most dangerous prior:** [Tuckute et al. (2024, Nature Human Behaviour)](https://doi.org/10.1038/s41562-023-01783-7) already selected sentences that successfully drove or suppressed language-network activity. Novelty requires discriminating mechanisms despite matched predictive performance.

   **Kill:** probability matching fails, differences disappear under confound controls, or prospective brain responses fail to discriminate.

   **Cost/assumption:** $300–1,000 public-data pilot; roughly $10–25k and months for new scanning. Requires a collaborating laboratory. **NHB plausible; Nature a stretch.**

The publication precedents are real but not solo: [Lake & Baroni (2023, Nature)](https://www.nature.com/articles/s41586-023-06668-3) matched human generalization and errors using specially trained networks; [Binz et al. (2025, Nature)](https://www.nature.com/articles/s41586-025-09215-4) built Centaur from a large behavioral dataset and tested broad transfer. Both support ambitious scientific claims through unusually strong human comparisons.