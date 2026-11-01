# Wild card / editor's eye: 12 headlines, 8 killed, 4 developed

## Twelve headlines
1. **A grammar rule found by a machine.** An LLM used as an informant (a speaker you question) proposes an English constraint that no grammar book records, and preregistered human judgments confirm it.
2. **A memory census of communication.** Counting Nerode classes (sets of histories that every future treats the same way) as depth grows shows which of speech, birdsong, whale codas and music need unbounded memory.
3. **Impossible languages, settled.** Humans and LMs learn the same possible and "impossible" mini-languages, with complexity matched between them.
4. **How much published mathematics is false?** A lower bound in which every counted error is a counterexample certified in Lean.
5. An LLM deciphers Linear A.
6. The Voynich manuscript is, or is not, a language.
7. An LLM trained only on pre-1905 text rediscovers relativity.
8. A higher-order-attention network that "sees" SET finds record cap sets.
9. Centaur-2: a fine-tuned LLM predicts experiments nobody has run yet.
10. A child-scale LM settles the poverty-of-the-stimulus argument.
11. Sperm-whale codas translated.
12. An LM's built-in learning biases (its "inductive bias") explain Greenberg's word-order universals.

## Killed (8)
- **5 Linear A.** Luo, Cao & Barzilay (2019, ACL; arXiv:1906.06718) deciphered Ugaritic and Linear B by aligning them with a *known* related language. Linear A has no known relative, so any reading cannot be checked. The headline cannot be both true and verifiable.
- **6 Voynich.** There is no ground truth. Bowern & Lindemann (2021, *Annu. Rev. Linguist.* 7:285–308) already reviewed the statistical evidence that it is language-like. Reviewers would see the topic as crank-adjacent.
- **7 Time-locked LLM.** Hla's Machina Mirabilis / GPT-1900 (Mar 2026, GitHub, not peer-reviewed) trained on pre-1900 text plus pre-1905 physics and got only "glimpses" of quanta. Talkie is similar (details unverified). Post-training leaks modern knowledge, and our scale is too small.
- **8 Cap sets.** A cap set is a set of points in Z₃ⁿ with no three on a line, which is exactly a SET-free deck.
  - Romera-Paredes et al. (2024, *Nature*, FunSearch) found the size-512 cap set in dimension 8.
  - Novikov et al. (2025, arXiv:2506.13131, AlphaEvolve) extended LLM-driven evolutionary search to many problems.
  - Charton, Ellenberg, Wagner & Williamson (2024, arXiv:2411.00566, PatternBoost) mixed transformers with local search to build constructions.
  - My guess is under 5% odds of a record against DeepMind's compute. Our characters law explains, it does not search.
- **9 Centaur-2.** Binz et al. (2025, *Nature*) fine-tuned an LLM on Psych-101 (160 experiments) to predict human choices. Hewitt, Ashokkumar, Ghezae & Willer (2024 preprint; whether it reached *Nature* is unverified) predicted 70 survey-experiment effects with GPT-4 at r≈0.85. A follow-up would be incremental, and critiques are already in print.
- **10 Poverty of the stimulus.** The field is crowded and has no decisive design left for one person.
  - Yedetore, Linzen, Frank & McCoy (2023, ACL): networks trained on child-directed speech chose linear, not hierarchical, rules.
  - Vong, Wang, Orhan & Lake (2024, *Science*): learned words from one child's headcam.
  - McCoy & Griffiths (2025, *Nat. Commun.*): distilled Bayesian priors into networks.
- **11 Whale translation.** Sharma et al. (2024, *Nat. Commun.*) found a combinatorial coda "phonetic alphabet". Paradise et al. (2025, NeurIPS; arXiv:2512.02206, WhAM) built a generative coda model. Project CETI owns the field data, and meaning cannot be checked. (Public codas still feed idea 2.)
- **12 Word order.** This is already done.
  - Hahn, Jurafsky & Futrell (2020, *PNAS*): efficiency-optimised grammars reproduce Greenberg's correlations.
  - Kuribayashi et al. (2024, ACL; arXiv:2402.12363): got them from cognitively motivated LMs.

## Survivor A: "Impossible languages: one preregistered test of humans and machines"
- **The debate.** Kallini et al. (2024, ACL; arXiv:2401.06416) found GPT-2 learns English-derived "impossible" languages less well. Bowers & Mitchell (2025, arXiv:2511.11389, BBS commentary) argue LMs learn many impossible languages equally well, and that the hard ones are "simply more complex". Kallini & Potts (2025, arXiv:2512.09394) set out LMs as testbeds for the question. Janarthan, Haley & Goldwater (2026, arXiv:2606.30815) find gradual grammaticality loss but sharp generation failures.
- **Decisive experiment.**
  - Build 8 mini-languages in 4 matched pairs (possible vs impossible). The impossible members use counting-based agreement and a non-conservative determiner. "Conservativity" is a proposed universal: no language has a word like "every" that checks things outside its noun.
  - Match each pair exactly on minimal-automaton size and description length, certified mechanically. This removes the complexity objection.
  - Teach the same stimuli to about 600 online participants and to LMs (scratch-trained and Qwen-ICL).
  - If the gap survives matching in humans but not in LMs, Bowers wins. If it survives in both, the LM-as-model camp wins. Both outcomes settle the question.
- **Kill.** In a pilot with 60 participants, humans show no possible/impossible gap once complexity is matched.
- **Why *Nature*.** It settles a Chomsky-era argument with the first head-to-head that controls complexity.
- **Closest prior art.**
  - Galke, Ram & Raviv (2024, *Nat. Commun.*): humans and networks both benefit from compositional mini-languages.
  - Hunter & Lidz (2013, *J. Semantics*): children failed to learn a non-conservative determiner.
  - Spenader & de Villiers (2019; venue unverified): failed to replicate that.

## Survivor B: "Does only human language need unbounded memory? A Nerode census of speech, song and sea"
- **The debate.** Hauser, Chomsky & Fitch (2002, *Science*) proposed recursion as uniquely human. Fitch & Hauser (2004, *Science*) found tamarins failed AⁿBⁿ (a pattern needing a counter). Gentner et al. (2006, *Nature*) claimed starlings succeed.
- **Decisive experiment.**
  - Fit one LM per corpus, then use it as an oracle to estimate N(d), the number of distinguishable Nerode classes at depth d.
  - Corpora: child-directed speech, Bengalese finch and canary song, sperm-whale codas, Bach chorales.
  - Calibrate first on synthetic regular, context-free and mildly context-sensitive grammars at each real corpus's size and alphabet.
  - Headline: whether N(d) saturates (finite-state) or keeps growing.
- **Kill.** On the calibration grammars, at real corpus sizes, the estimator separates regular from context-free less than 90% of the time.
- **Why *Nature*.** It replaces 20 years of operant-training debate with one quantitative measure applied across species. It reuses our Nerode machinery.
- **Closest prior art.**
  - Sainburg, Theilman, Thielk & Gentner (2019, *Nat. Commun.*): mutual information decays exponentially then as a power law in both birdsong and speech.
  - Kershenbaum et al. (2014, *Proc. R. Soc. B*): animal sequences are not Markov chains.
  - Morita, Koda, Okanoya & Tachibana (2021, *PLoS Comput. Biol.*): measured context length in song with neural LMs.
  - Zuidema et al. (2019, arXiv:1901.05180): review of the Chomsky hierarchy across language, music and animal song.
  - I found no precedent for estimating Nerode-class growth this way.

## Survivor C: "A Lean-certified lower bound on false statements in published mathematics"
- **Gap.** Rivin (2025, arXiv:2511.10543) had LLM referees read about 37,000 arXiv papers and report 6.5–9.6% error rates, with no certification. Bastounis, Circelli & Hansen (2026, arXiv:2610.08144) show that Lean-verified autoformalisations can misstate the original claim. Ammanamanchi et al. (2026, arXiv:2606.29493) certified hundreds of defects in Lean benchmarks.
- **Decisive experiment.**
  - Take a stratified sample of 500 math.CO/NT papers from 2010–2024.
  - Extract only claims that have finite certificates: small-case tables, explicit constructions, "for all n ≤ N".
  - Search for counterexamples with SAT/brute force, check each in the Lean kernel with `decide`, and have two humans confirm it against the PDF.
  - Report a certified lower bound. Misformalisation cannot inflate it, because each counted error is checked against the paper.
- **Kill.** Fewer than 5 confirmed false claims, or most hits are typos.
- **Why *Nature*.** It is reproducibility for mathematics, where the numbers so far are uncertified.
- **Closest prior art.** Jenne, Brown, He & Kvinge (2026, arXiv:2610.40382) evaluate LMs on randomly sampled conjectures. Unverified web reports of lab-scale audits suggest this window is closing.

## Survivor D: "The first syntactic generalisation discovered by a machine and confirmed in humans"
- **Decisive experiment.**
  - Run a Harris discovery procedure with Qwen as informant. Harris's procedure groups words and phrases by the contexts they share.
  - Use meaning-controlled minimal pairs; this answers Hu, Wilcox, Song, Mahowald & Levy (2026, TACL), who show raw probability conflates grammaticality with how likely the message is.
  - A linguist checks candidates blind against CGEL and the literature.
  - Preregister the top 10 and test them with 300 participants.
- **Kill.** None of the 10 is confirmed, or every confirmed one turns out to be already known.
- **Why *Nature*.** It makes the young-Chomsky dream real, on the riskiest odds of the four.
- **Closest prior art.**
  - Yu et al. (2026, arXiv:2604.07189): agent-driven corpus linguistics that replicates known findings.
  - Misra & Mahowald (2024, EMNLP): LMs learn the rare AANN construction ("a beautiful five days") from more common phenomena.
  - Beguš, Dąbkowski & Rhodes (2025, IEEE TAI): LLMs' metalinguistic analyses.

**Assumptions Neo did not ask for:**
- All four drop the "exact computation" dream conditions.
- A, B and D need human-subject approval (IRB) and online participant budgets.
- Odds are my guesses: A highest, D lowest.

**Glossary:** this brief was read-only, so I did not append to `GLOSSARY.md`. These terms need adding: Nerode class, conservativity, cap set, impossible language, informant.
