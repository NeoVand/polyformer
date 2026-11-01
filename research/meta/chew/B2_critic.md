# Hostile review of round A: six directions, two hybrids

**Bottom line.** None of the six survives as written. Two survive once rescoped, and only when merged. Verdicts: SURVIVES-IF (rescoped), DOWNGRADE (a real paper, not Nature), KILL.

**Killed without full review.** The Lean audit of false mathematics (A4-C) only covers finite-certificate claims, so it counts slips in small tables, not errors in "published mathematics". The world-model detour (A3-3) is an engineering claim that a negative-eigenvalue DeltaNet baseline probably answers (Grazzi et al. 2025, ICLR, arXiv:2411.12537, as cited in A3; I did not re-verify it). Repair-algorithm and brain-selection (A2-3/4) both need a lab. Self-training counterexamples (A1-3) is a footnote to model collapse.

## 1. A grammar rule found by a machine (A1-1, A4-D, A3-2)
**Referee.** "English syntax is the most-mined dataset in linguistics. Sprouse, Schütze & Almeida (2013, *Lingua* 134) replicated about 95% of randomly sampled *Linguistic Inquiry* judgments with naive speakers. A 'new' contrast will be a rediscovery, a plausibility gradient or a lexical quirk. Hu, Wilcox, Song, Mahowald & Levy (2026, *TACL* 14) show that LM minimal-pair differences already track human ones, so 'humans confirm the LM' is expected, not a discovery. Testing ten candidates leaves many forking paths. The monoid version is ill-posed: a finite two-sided congruence makes the language regular."

**Fix.** Make the headline a measured **discovery yield**: the share of LM-proposed constraints that are new (checked blind against CGEL, the reference grammar of English) and that replicate. Compare it with linguist-proposed contrasts and with random contrasts of matched LM difference. Each candidate must be a compact rule that predicts judgments on nonce words. Submit as a **Registered Report**: methods are peer-reviewed before data collection, with acceptance in principle regardless of outcome. Drop the monoid framing.

**Verdict.** DOWNGRADE (NHB). Nature only if the yield surprises.

## 2. Impossible languages with matched complexity, humans vs LMs (A4-A)
**Referee.** "You matched complexity under your own encoding, not the learner's. Bowers & Mitchell (2025, arXiv:2511.11389; LMs learn many impossible languages as well as attested ones) will call any human gap unmatched complexity. Hunter (2025, *Computational Linguistics*) showed that Kallini et al. (2024, ACL) changed two variables at once, and your counting-vs-hierarchy pair risks the same. An hour of online learning invites puzzle-solving. Musso et al. (2003, *Nature Neuroscience*) found that adults *do* learn 'unreal' rules, using different brain regions. An underpowered null settles nothing."

**Fix.** Preregister equivalence tests, which can affirm "no difference", with power to match. Match complexity on two independent metrics, and add a rare-but-attested control of equal complexity to separate rarity from impossibility. Test generalisation under a concurrent memory load to suppress explicit strategies. Compare three learners: a transformer, an LSTM and a Bayesian grammar learner.

**Verdict.** SURVIVES-IF; it goes into Hybrid 1.

## 3. Universals as transmission failures (A2-1)
**Referee.** "Iterated learning (each learner trains on the previous learner's output) owns this field. Kirby, Cornish & Smith (2008, *PNAS*) evolved structure in human chains. Griffiths & Kalish (2007, *Cognitive Science*) proved that chains of Bayesian samplers converge to the learners' prior. Ren, Guo, Qiu, Wang & Sutherland (2024, NeurIPS) showed the same bias amplification in LLMs. Truncating an LM's context is not human working memory."

**Fix.** Use the theorem as the instrument. One generation of learning measures prior plus data, while the chain's endpoint measures the prior alone; the gap between them is the finding. Manipulate human memory with a standard dual task. Predict out-of-sample frequencies in Grambank (a typological database of world languages), controlling for language family.

**Verdict.** DOWNGRADE alone; essential inside Hybrid 1.

## 4. Indirect evidence supplies the missing grammar (A2-2)
**Referee.** "Patil, Jumelet, Chiu et al. (2024, *TACL*, 'FiCT') removed constructions from training data and found generalisation from indirect evidence. Yang, Bisazza, Schneider & Wilcox (2026, arXiv:2602.09992) did so at child scale. A teaching set found by ablation is specific to one corpus, and adult tests say nothing about children."

**Fix.** It needs longitudinal child data and a collaborator.

**Verdict.** KILL for a solo bid on a timescale of weeks.

## 5. Working memory requires erasure (A3-1)
**Referee.** "Sinha, Arun, Goel, Staab & Geiping (2025, arXiv:2509.09677) showed that models make more errors when their context holds their own past errors. Aghajohari, Chitsaz, Kazemnejad, Chandar, Sordoni, Courville & Reddy (2025, arXiv:2510.06557, 'Delethink') reset context to a short carry-over state and got linear-cost reasoning. In Altmann, Trafton & Hambrick (2014, *JEP: General* 143), interruptions of 2.8 s doubled human sequence errors, but an LLM is never interrupted. Calling pointer errors 'placekeeping' proves no shared mechanism. The dilution bound is unproved."

**Fix.** Prove the dilution bound in Lean. Then turn the dissociation (49,084 of 49,087 post-error steps still follow the rule) into a human prediction: vary the similarity between steps in Altmann's placekeeping task and preregister that sequence errors, but not rule errors, follow the similarity law fitted on the LLMs.

**Verdict.** DOWNGRADE (NMI/ICLR); the human half is a lottery ticket.

## 6. Nerode census of speech, song and sea (A4-B)
**Referee.** "Every finite corpus has a finite automaton, so class growth confounds memory with sample size, and the oracle model's architecture sets the count. Causal states (Crutchfield) are Nerode classes for stochastic processes. Hahn & Futrell (2019, *Entropy*) estimated predictive rate–distortion for language and argued it beats counting causal states. Lin & Tegmark (2017, *Entropy*) and Sainburg et al. (2019, *Nat. Commun.*) already separated exponential from power-law information decay in song and speech. Van Heijningen, de Visser, Zuidema & ten Cate (2009, *PNAS*) showed that simple rules explain the songbird 'recursion' results."

**Fix.** Report the memory–surprisal curve (Hahn, Degen & Futrell 2021, *Psychological Review*), not a Chomsky-hierarchy verdict.

**Verdict.** KILL: the rescue is a Hahn–Futrell extension in which we have no edge.

## Hybrid 1: Which impossible grammars die in the learner, and which in the chain?
- **Builds on:** 2 (machine-certified complexity matching, using our automaton tooling) and 3 (transmission theory).
- **Materials:** six to eight pairs (possible vs impossible), plus rare-but-attested controls.
- **Arm A:** one generation of learning, in about 600 online humans and in transformer, LSTM and Bayesian learners.
- **Arm B:** five-generation chains for each learner type.
- **Theory:** by Griffiths–Kalish, Arm B reveals each learner's prior. Patterns that are hard in A are learner constraints; patterns hard only in B are transmission filters. Which machine matches humans in each arm settles the model comparison.
- **External test:** correlation with Grambank frequencies on held-out patterns.
- **Kill:** pilot humans (n=60 per arm) show neither gap.
- **Venue and cost:** NHB Registered Report, Nature if the split holds across families; about $8k for participants.

## Hybrid 2: A spectral law of concept difficulty in humans and machines
- **Builds on:** A1-4, the characters law and the coupling barrier.
- **Old question:** what makes a concept hard? Feldman (2000, *Nature* 407) said the length of its shortest logical formula. Kurtz, Levering, Stanton, Romero & Morris (2013, *JEP: LMC*) showed that the classic ordering of Shepard, Hovland & Jenkins (1961), with the XOR-like Type II easier than the linearly separable Type IV, flips with procedure.
- **Theory:** Abbe, Boix-Adserà & Misiakiewicz (2023, COLT, arXiv:2304.03752) show gradient learners pay by the **leap**, the Fourier degree they must jump. Leap predicts Type IV easier; formula length predicts Type II easier. The characters law extends the prediction to SET-like decks over Z₃ⁿ, where learning order should follow which group characters are acquired.
- **Decisive experiment:** humans learn Match-k categories whose pairwise statistics are identical, under rule-seeking or concurrent-load instructions. Preregister that loaded (implicit) learners follow the leap ordering and rule-seekers follow formula length. Softmax and cubic attention should each match one mode, and both must beat ALCOVE (Kruschke 1992, *Psychological Review*), the standard attention-based exemplar model.
- **Kill:** neither ordering predicts held-out human learning curves.
- **Why:** cheap data, a theorem behind the prediction, and a Nature precedent to challenge. I found no prior test of leap on humans; absence is unverified.

**Assumptions check.** Both hybrids defer conditions 2–7 and 10, and need ethics approval (IRB) plus participant budgets beyond condition 12. Leap theory concerns SGD, which humans do not run, so it gives predictions, not derivations.

**Glossary terms to add** (this brief was read-only): Registered Report, equivalence test, iterated learning, leap, predictive rate–distortion, SHJ types, ALCOVE.
