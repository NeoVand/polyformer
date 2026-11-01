**Build an instrument that proposes grammatical restrictions and tries to break them.** Its scientific product is a previously unrecognized rule that predicts withheld human evidence better than existing explanations. Acceptability judgments measure how natural sentences sound; grammar, meaning, and processing all influence them. Model agreement alone cannot establish a fact about human grammar.

This belongs to **grammar induction: inferring explicit rules from examples**. [Harris (1954, *WORD* 10:146–162)](https://gwern.net/doc/psychology/linguistics/1954-harris.pdf) developed distributional analysis—characterizing expressions through their environments. [Clark & Eyraud (2007, *JMLR* 8:1725–1745)](https://www.jmlr.org/papers/volume8/clark07a/clark07a.pdf) proved learning results for restricted grammars from positive examples. [Clark (2010, *ICGI*:38–51)](https://www.its.caltech.edu/~matilde/ClarkSyntacticConceptLattice.pdf) added membership queries—asking whether a string belongs—and overlapping categories defined through shared contexts. These provide designs, not guarantees for noisy LLM judgments or unrestricted natural language.

The procedure should have five stages:

1. **Specify the contrast.** Fix language variety, intended interpretation, and competing explanations. Represent each expression through its behaviour in sentence frames containing a slot. Allow overlapping categories: an expression can perform several functions.

2. **Measure meaning-matched differences.** A meaning-matched minimal pair changes one grammatical property while preserving the recoverable intended message. Compare sentence log probabilities within each pair, using the same discourse context. [Hu, Wilcox, Song, Mahowald & Levy (2026, *TACL* 14:124–146)](https://aclanthology.org/2026.tacl-1.7.pdf) tested 280,000 English/Chinese pairs, supporting these comparisons while explaining failures of absolute probability thresholds. Their paper supplies a justification for this design.

3. **Challenge the matching.** A native linguist must check interpretations; sentence similarity scores are insufficient. Cross the grammatical manipulation with plausible/unusual scenarios, several vocabularies, and alternative repairs. Reject effects driven by changed participants, meanings, or discourse suitability. Meaning matching reduces the confound; it does not automatically eliminate it.

4. **Search informative disagreements.** Build an expression-by-context table of scored contrasts. Group expressions with similar responses, then search short if–then rules, penalizing complexity. Request examples where competing rules predict different outcomes. This adapts Clark’s programme to contrasts rather than pretending to possess an infallible membership oracle. Deliberately distinguishing contexts also address the identification failure documented in `AUDIT.md`.

5. **Separate discovery from confirmation.** Preserve every candidate and failed prediction. Freeze rules before exposing withheld human ratings. Search scholarship in the target language; have experts assess novelty without knowing proposal source. “New” means new to scholarship, not merely absent from a benchmark. Unknown training data prevent proving the model never encountered the idea.

A concrete target is whether separating two verbs becomes unacceptable only under a particular combination of complement form and clause embedding, after matching distance and verb identity. Existing ordering restrictions are positive controls. A discovery must predict an additional contrast that competing accounts miss.

**Language choice should follow demonstrated grammatical competence, not a coverage list.** [Qwen’s official Qwen3.5 release](https://qwen.ai/blog?email_hash=23463b99b62a72f26ed677cc556c44e8&id=qwen3.5) lists **201 languages and dialects**, including Indonesian, Tamil, Turkish, Vietnamese, Cantonese, and multiple Arabic varieties. The [4B model card](https://huggingface.co/Qwen/Qwen3.5-4B) repeats the claim; it does not establish reliable judgments in every language.

| Target | Proposed opportunity and limitation |
|---|---|
| **Indonesian** | Interactions among verb voice, displaced objects, intervening clauses, and formal/colloquial usage. My preferred discovery prospect, conditional on native expertise and calibration. |
| **Tamil** | Interactions among noun case, verb agreement, and embedded clauses. Higher model-reliability risk. |
| **Mandarin** | Interactions among object placement, event completion, and discourse. Practical model coverage is attractive; obvious restrictions are extensively studied. |
| **Dutch** | Verb-complement ordering across clause and verb types. Best first archival experiment because detailed participant ratings exist. |

These are **proposed search regions, not verified gaps in description**. The realistic opening is an overlooked interaction within a studied language. Poorly documented varieties frequently lack both reliable model coverage and independent validation.

**Public evidence supports several different kinds of validation.**

| Resource and paper | What it supplies |
|---|---|
| [Sprouse, Schütze & Almeida (2013, *Lingua* 134:219–248)](https://www.jonsprouse.com/papers/Sprouse%20et%20al.%202013.pdf) | Tested **148 English contrasts with 936 participants**, using three judgment tasks; [data/materials are linked](https://www.jonsprouse.com/research.html). Strong calibration, after checking meaning matching. |
| [Warstadt, Parrish, Liu, Mohananey, Peng, Wang & Bowman (2020, *TACL*), BLiMP](https://aclanthology.org/2020.tacl-1.25.pdf); [Xiang, Yang, Li, Warstadt & Kann (2021, *EACL*), CLiMP](https://aclanthology.org/2021.eacl-main.242.pdf) | Generated **67,000 English / 16,000 Mandarin pairs**, with human validation samples. Most labels are constructed rather than participant measurements. CLiMP’s person/bicycle role reversal illustrates why “minimal” need not mean meaning-matched. |
| [Gauthier, Hu, Wilcox, Qian & Levy (2020, *ACL Demonstrations*), SyntaxGym](https://aclanthology.org/2020.acl-demos.10.pdf) | Standardized controlled model evaluations; not itself a comprehensive human-rating archive. |
| [Zhang, Liu, Huang, Mao, Wang & Hu (2024, *ACL*), MELA](https://aclanthology.org/2024.acl-long.146.pdf) | Combined **46,000 acceptability examples across ten languages**, largely published linguistic judgments rather than uniform participant experiments. |
| [Leong, Ngui, Susanto, Rengarajan, Sarveswaran & Tjhi (2023, arXiv:2309.06085), BHASA/LINDSEA](https://arxiv.org/pdf/2309.06085) | Public Indonesian/Tamil expert-written tests. Validation sometimes allowed grammatical-but-implausible rejected alternatives: filter these before using them here. |
| [Suijkerbuijk, Prins, de Heer Kloots, Zuidema & Frank (2025, *Computational Linguistics*), BLiMP-NL](https://aclanthology.org/2025.cl-4.6.pdf) | **8,400 Dutch pairs; 756 experimentally tested**, with approximately 20 ratings per grammatical sentence and ten per ungrammatical sentence, plus reading times. Best archival starting point. |
| [Skirgård et al. (2023, *Science Advances* 9:eadg6175), Grambank](https://hilario.bambooradical.com/downloadables/sciadv.adg6175.pdf); [Dryer & Haspelmath, eds. (2013, MPI-EVA), WALS Online](https://wals.info/) | Compiled structural properties across languages. Useful for typology—comparing language structures—and selecting contrasts; neither supplies sentence-level confirmation. |

A new generalisation can explain old judgments. An archive cannot validate newly generated sentences it never tested. Withheld public data may also have appeared in model training.

**Prior art makes the defensible claim narrower.**

- [Goertzel, Suárez-Madrigal & Yu (2020, arXiv:2005.12533)](https://arxiv.org/html/2005.12533v1) already guided symbolic grammar induction with transformer probabilities. Their six-word demonstration rejected six spurious rules **and three valid ones**.
- [Yu, Yu, Xiao & Xing (2026, arXiv:2604.07189)](https://arxiv.org/html/2604.07189v1) automated corpus investigations and replicated two published studies; they explicitly acknowledge discovery-versus-recall uncertainty.
- [Beguš, Dąbkowski & Rhodes (2025 revision, arXiv:2305.00948)](https://arxiv.org/pdf/2305.00948) tested prompted syntactic and phonological analyses.
- [Tikhonov, Shteiner, Bykova & Yamshchikov (2025, *Findings ACL*)](https://aclanthology.org/2025.findings-acl.934.pdf) built a Russenorsk discovery assistant; verification of additional novel hypotheses was outside scope.
- [Lian, Ku & Hsieh (2026, *Computing Conference*), CorPilot](https://link.springer.com/chapter/10.1007/978-3-032-24804-6_2) reports Mandarin corpus analysis and novel patterns. Abstract/appendices opened; full text unavailable, independent novelty and confirmation **unverified**. This is a direct competitor.

Claim a particular independently supported discovery and measured discovery yield. A “first automated linguist” claim would fail.

**Run a two-week Dutch pilot with a $300 compute ceiling.** Assume a native Dutch syntactician contributes 12–16 hours, priced separately.

- **Days 1–3:** Audit BLiMP-NL meanings and provenance. Allocate up to **252 rated pairs each** to calibration, discovery, and sealed confirmation, separating construction templates and main verbs; report actual post-filter counts. Use [Qwen3.5-4B-Base](https://huggingface.co/Qwen/Qwen3.5-4B-Base), before instruction tuning, and [Aya Expanse 8B](https://huggingface.co/CohereLabs/aya-expanse-8b) as a different-family check. Require **85% agreement** with calibration contrast directions while answering at least **80%** of eligible pairs.
- **Days 4–9:** Build **200 expressions × 100 contexts**. Spend **10,000 contrast queries** choosing informative disagreements and **10,000** randomly. Produce **30 candidates total**: ten from each search method and ten from direct prompting. Cap each rule at three conditions. Screen novelty blind.
- **Days 10–14:** Freeze at most **three rules**, rival predictions, and analysis choices. Require at least **24 eligible withheld pairs per rule**, spanning multiple verbs and constructions, with every critical comparison represented. Analyse human rating differences while accounting for speaker and item variation; correct for testing three claims. A survivor must predict a difference the existing account misses, with its corrected uncertainty interval excluding zero.

**Kill** if calibration fails, all 30 candidates are known or meaning-driven, or none survives withheld human evidence. Missing comparisons kill the archive-only confirmation route: generated examples then require new speaker judgments.

The collaborator needs interpretable rules, glossed examples, counterexamples, rival analyses, provenance, and the complete failure ledger. They must distinguish a grammatical restriction from a preference or processing difficulty.

This assumes direction 2 takes priority over Neo’s internal-computation, certification, architecture, and one-week conditions. Standard alternatives address the same evidence constraint differently: corpus analysis buys observed usage but weak evidence about impossibility; new participant experiments buy targeted contrasts at additional cost. A Nature-level result would require a consequential theoretical revision and independent replication.