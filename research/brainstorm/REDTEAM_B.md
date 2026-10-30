# REDTEAM_B: prior-art hunt for I2, I3, I4, I5, I8, I9, I10

Red team B, 28 Oct 2026. Every citation below was checked live on **2026-10-28**, through the arXiv API
(export.arxiv.org), Crossref, the GitHub API or the venue page. Anything I could not confirm is listed in §9.
Nothing here repeats the L1–L6 map. Where an item is already in L1–L6 it is marked *(known, Lx)* and used only for
contrast.

Read depth: **[read]** means I read the method and results sections, not just the abstract. **[abs]** means I
read the abstract and metadata only.

## Verdict table

| Idea | Verdict | Closest prior art (new to our map) | What is still ours, stated precisely |
|---|---|---|---|
| **I2** certified identification of machines and rules by an LLM learner | **PARTLY DONE** | Liu, Sala, Reps & Murali 2026: an LLM proposes, exact DFA-equivalence counterexamples come back. Chen, Trivedi & Velasquez: pMAT 2024, CAPAL (ICLR 2026), CEDAR 2026. OPINE-World 2026 and Rodionov 2026 (LLM-written world models checked on every recorded transition, ARC-AGI-3). SmartLabel (OOPSLA 2025): neural mispredictions make active learning return the wrong program. | (a) The hypothesis is run by the learner's own network, and Theorem P makes counterexamples sound. Others get soundness by running Python outside the model, or only probabilistically by conformal evaluation (SmartLabel). (b) The learner prints an m-complete stopping statement ("certain for any machine with ≤ m states"). No LLM learner I found has a conformance-testing stopping rule; all of them stop at replay consistency. (c) An LLM that chooses its own queries against a black-box Mealy machine, with query counts compared to L\*/L#: not found. |
| **I3** self-predicted failure sets, plus self-repair | **PARTLY DONE** | Mayr, Yovine & Visca (MAKE 2021): Bounded-L\* learns a DFA that *PAC-approximates the set of inputs a black-box RNN gets wrong*, an "interpretable error characterization". Khmelnitsky et al. (ATVA 2021): surrogate DFA plus model checking, with pumped "faulty flows". | An **exact** (not PAC) description of the network's infinite error set at all lengths. It is derived white-box from the model's own per-row checks and verified in both directions by a bounty. The model's own renaming as the repair lever is also new. The failure set itself is a product automaton once Theorem P holds, so a reviewer will credit the novelty to Theorem P, which we already claim. |
| **I4** the ∀ badge: a per-answer Lean theorem that the network is right for all inputs | **PARTLY DONE** | Amit, Goldwasser, Paradise & Rothblum (NeurIPS 2025): per-input proofs of *output* correctness. Gross et al. (NeurIPS 2024) and Wu et al. (ICLR 2025): proofs about *trained weights* on finite domains. teal-sea/lean-checked-network (GitHub, Oct 2026): a Lean-kernel theorem that a trained transformer adds mod 113 on all 12,769 inputs. Floyd 1967 already is the "Nerode certificate" (meanings per state, checked per transition). | A kernel-checked theorem whose subject is **the network's own execution on a code path, for all inputs of all lengths**, emitted per answer. Nothing I found makes an all-lengths claim about trained LLM weights. The meaning certificate is **not** new: cite it as Floyd's inductive assertions on a finite-state program, and claim only its composition with Theorem P. |
| **I5** the certified self-improvement ratchet | **PARTLY DONE** | Schmidhuber's Gödel machine (2003): rewrite only on a proof of usefulness. **CNPI (Xiao, Liao & Yuan, ICLR 2018)**: a verified, frozen core keeps every learned program correct as new ones are added, and the paper notes Cai et al.'s RNPI loses guarantees on old tasks after retraining. CCL (Pham & Sun, ISSTA 2024), Provably Safe Model Updates (SaTML 2026) and SafeAdapt (2026) preserve certified properties across updates. GRASP (EMNLP 2026) gates skill libraries on a regression budget. | The gate uses a regression suite that is **complete by theorem** (per-row certificate ⇔ exact at all lengths). It applies to **weight updates of an LLM**, not a frozen core, and an update is rejected unless the whole library recertifies. No found paper gates LLM weight updates on complete recertification. CCL repairs or drops certificates instead of rejecting updates. CNPI avoids the problem by freezing. |
| **I8** certify the model, not the program (N\*) | **PARTLY DONE** (the claim's shape) / **CLEAR** for LLMs | **CNPI (ICLR 2018), Theorem 1**: train and verify a core and 4 combinators once, then *every* combinatorizable program runs "with perfect generalization (i.e. with any input complexity)". Verification is needed "once". Sälzer, Alsmann & Lange (ICLR 2025): verifying transformer encoders over unbounded length is undecidable, and decidable when quantised or bounded. | The certificate is about **pretrained LLM weights**: one lookup head plus row-local attention gives every table up to N rows over a screened vocabulary, exactly, at any length. CNPI is the precedent to cite for the shape "verify a finite core once, all programs follow". Its proof is on paper, for a small LSTM NPI with a combinator architecture. |
| **I9** row-level or process-exact rewards for program-synthesis RL | **PARTLY DONE** | EGCA (ICLR 2026 SPOT workshop): finds the earliest execution divergence from a reference trace and puts the GRPO advantage on that span. RLTF (TMLR): penalises the error line. PSGPO (Dai et al. 2024): binary-searches for the first wrong line to get line-level PRM labels. Ghedamsi & Bochmann 1992/93: locate the faulty *transition* of an FSM from failed tests. | **Exactness** of the credit. Under certified execution a wrong answer is never execution noise, and with a reference table the wrong row is the first product-run divergence, found with no LLM debugger. Without a reference table, finding the row is the classical FSM diagnosis problem, which may need extra tests and may have no unique answer. The bet must say which of the two cases it is in. |
| **I10** exact state over long documents | **PARTLY DONE** | New to our map: NeSyA (IJCAI 2025), neural predicates plus an exact symbolic automaton. CEDAR 2026: LLM semantic judgments plus DFAs over event traces. Compiled AI 2026: the LLM compiles code, then runs with zero LLM calls. Chain of Agents (NeurIPS 2024) and LLM×MapReduce: chunk-local judgments with a carried, inexact state. Known: CFSM, TemporalGuard, SpecGuard, LLM+ASP, StateMem, BABILong. | The control loop runs **inside the same LLM under the certificate**, with no interpreter. That makes "end-to-end error = snap error" and "cost per row, not per step" theorems. Each row of the compiled semantic table is checked. The external-code version of the architecture is now commonplace, so B4's "Python twin" objection applies in full. |

**No idea is fully DONE.** Every one has a published version without the in-network certificate, so our
contribution in each case comes down to Theorem P plus "inside the network".

### The six most dangerous new finds (none is in L1–L6)

1. **Xiao, Liao & Yuan, "Improving the Universality and Learnability of Neural Programmer-Interpreters with
   Combinator Abstraction" (CNPI), ICLR 2018.** It pre-empts the *shape* of I8 and the motivation of I5 (§5, §6).
2. **Mayr, Yovine & Visca, MAKE 2021.** "A DFA of the inputs the network gets wrong" is already a published
   artefact, PAC and black-box (§3).
3. **Liu, Sala, Reps & Murali 2026 (CEGML)**, plus the **Chen–Trivedi–Velasquez trilogy (pMAT, CAPAL, CEDAR)**.
   These groups are working right next to I2. CAPAL and CEDAR came out in 2026, so the scoop risk is real (§2).
4. **SmartLabel (Barnaby et al., OOPSLA 2025).** It already argues and measures B3's "sound counterexamples" point:
   neural mispredictions make active learning return the wrong program. Their fix is conformal, ours is a theorem (§2).
5. **Amit, Goldwasser, Paradise & Rothblum, Self-Proving Models.** B3 asked us to verify it; it is real, and it
   covers per-input proofs of outputs (§4).
6. **EGCA (Kumar, Kumar & Gupta 2026).** Exact divergence-span credit from execution traces is published; ours is
   the table-row special case (§7).

---

## 2. I2: certified identification by an LLM learner. PARTLY DONE

### Evidence

**A. The LLM proposes and an exact teacher returns counterexamples (closest in shape)**
- **Liu, Sala, Reps, Murali. "Counterexample Guided Learning in the Large using Reasoning Agents."** arXiv
  2606.11521, Jun 2026. https://arxiv.org/abs/2606.11521 **[read]**
  - What they do:
    - an LLM proposes regexes;
    - the teacher computes exact language equivalence through minimal DFAs (pyformlang) and returns "clustered"
      symbolic counterexamples;
    - reflection and repair loops come on top.
  - Results: on Simple Regex at star-depth 4, success rises from 3.2% to 38.1%; on Extended Regex at depth 2, from
    38.9% to 74.1%.
  - What they don't do:
    - no identification, termination or query bound is claimed;
    - the hypothesis runs in external code, not in the LLM;
    - no Mealy machines, transducers, W-method or state bounds;
    - the LLM never chooses membership queries.
  - Distance to I2: the same loop with the guarantee removed. This is the paper a reviewer will put beside I2.
- **Alsadat, Gaglione, Neider, Topcu, Xu. "Using LLMs to Automate and Expedite RL with Reward Machine."** arXiv
  2402.07069, 2024. https://arxiv.org/abs/2402.07069 **[abs]**
  - The LLM writes automata (reward machines) and rewrites them when environment counterexamples appear.
  - It gives no guarantee that the automaton is correct, as the pMAT paper points out.

**B. The LLM as the (noisy) teacher in L\***
- **Vazquez-Chanlatte, Elmaaroufi, Witwicki, Zaharia, Seshia. "L\*LM."** arXiv 2402.07051, 2024.
  https://arxiv.org/abs/2402.07051 **[abs]**
  - The LLM answers membership queries for DFA learning from demonstrations.
- **Chen, Trivedi, Velasquez. "LLMs as Probabilistic Minimally Adequate Teachers for DFA Learning" (pMAT).** arXiv
  2408.02999, 2024. https://arxiv.org/abs/2408.02999 **[read]**
  - The LLM answers membership queries with persistent errors; equivalence queries are assumed exact.
  - Its related-work section names the prior "LLM outputs automata directly" line (Alsadat et al.).
- **Chen, Trivedi, Velasquez. "Towards Persistent Noise-Tolerant Active Learning of Regular Languages with Class
  Query" (CAPAL).** ICLR 2026. https://iclr.cc/virtual/2026/poster/10011821 (OpenReview id 1XMUe2dGRr) **[abs, venue
  page]**
  - Convergence is proved under persistent membership noise, given a perfect equivalence oracle.
- **Chen, Velasquez, Trivedi. "CEDAR: Automata as Verifiable Interfaces for Language-Guided Embodied Action."** arXiv
  2608.27797, Aug 2026. https://arxiv.org/abs/2608.27797 **[read]**
  - The LLM gives semantic membership judgments; CAPAL learns the skill and spec DFAs; execution stands in for the
    equivalence query; composition is by product.
  - The paper says this is "not a certificate" that the DFAs capture the instruction.
- **Fica, Otop. "Active Automata Learning with Advice."** ECAI 2025; arXiv 2508.10535.
  https://arxiv.org/abs/2508.10535 **[abs]**
  - Prior knowledge (string-rewriting "advice") cuts query complexity.
  - This is the formal slot an LLM's semantic prior would occupy. Cite it for "priors cut queries".

**C. LLM-written world models checked against all observations (the law lives in Python)**
- **Courtis, Li, Sanner. "OPINE-World."** arXiv 2607.01531, Jul 2026 (under review, ICLR 2027).
  https://arxiv.org/abs/2607.01531 **[read, first half]**
  - Method:
    - a Python world model is revised by counterexample-guided synthesis;
    - a replay-consistency condition requires every recorded transition to be reproduced;
    - experiments are chosen by unexplained entropy.
  - Results: 20 of 25 ARC-AGI-3 games, RHAE 78.4.
  - The paper says: "Replay consistency also provides no guarantees for entirely unvisited objects." No state bounds,
    no conformance testing.
- **Rodionov. "Executable World Models for ARC-AGI-3 in the Era of Coding Agents."** AGI-2026; arXiv 2605.05138.
  https://arxiv.org/abs/2605.05138 **[abs]**
- **Tang, Key, Ellis. WorldCoder.** arXiv 2402.12275. https://arxiv.org/abs/2402.12275 **[abs]** *(B3 already names
  it.)*
- **Piriyakulkij, Liang, Tang, Weller, Kryven, Ellis. PoE-World.** arXiv 2505.10819.
  https://arxiv.org/abs/2505.10819 **[abs]**
- **Khan et al. "One Life to Learn."** ICLR 2026; arXiv 2510.12088. https://arxiv.org/abs/2510.12088 **[abs]**
- **Warrier et al. "Benchmarking World-Model Learning with Environment-Level Queries" (WorldTest / AutumnBench).**
  ICML 2026; arXiv 2510.19788. https://arxiv.org/abs/2510.19788 **[abs]**
  - Humans beat models; the paper attributes the gap to exploration and belief updating.
  - This is the natural public benchmark for I2's "alien device".

**D. Experiment choice, distinguishing inputs and the soundness problem**
- **Barnaby, Chen, Ramalingam, Bastani, Dillig. "Active Learning for Neurosymbolic Program Synthesis" (SmartLabel).**
  PACMPL OOPSLA2 2025; arXiv 2508.15750. https://arxiv.org/abs/2508.15750 **[read, first half]**
  - Symbolic active learners "can -- and, in practice, do -- return an unintended program due to mispredictions of
    neural components". A mis-detected object makes the true program disagree with the user's example, so it is
    discarded.
  - The fix is conformal prediction sets (probabilistic coverage under i.i.d.).
  - Results: 98% of 112 benchmarks recovered in 4.9 rounds, against at most 65% for prior learners.
  - **This is B3's mechanism point (uncertified slips pose as counterexamples), already published and measured.** Our
    delta is that the pin makes it a theorem with zero slips, not a coverage probability.
- **Barnaby, Ding, Bastani, Dillig. "Choose, Don't Label."** arXiv 2604.08792, 2026.
  https://arxiv.org/abs/2604.08792 **[abs]**
  - Multiple-choice disambiguation queries over clusters of candidate programs.
- **Jha, Gulwani, Seshia, Tiwari. "Oracle-guided component-based program synthesis."** ICSE 2010.
  https://doi.org/10.1145/1806799.1806833 (Crossref)
  - The classical "ask the input that splits the finalists" (distinguishing inputs). B2's demo step is this.
- **Piriyakulkij, Langenfeld, Le, Ellis. "Doing Experiments and Revising Rules with Natural Language and
  Probabilistic Reasoning."** NeurIPS 2024; arXiv 2402.06025. https://arxiv.org/abs/2402.06025 **[abs]**
  - LLM rule proposals, Bayesian updates and information-gain experiment design on Zendo.
- **Li, Tamkin, Goodman, Andreas. "Eliciting Human Preferences with Language Models" (GATE).** ICLR 2025; arXiv
  2310.11589. https://arxiv.org/abs/2310.11589 **[abs]**
- **Qiu et al. "Phenomenal Yet Puzzling."** ICLR 2024; arXiv 2310.08559. https://arxiv.org/abs/2310.08559 **[abs]**
- **Parab, Lu, Wu, Gulwani.** arXiv 2509.01016. https://arxiv.org/abs/2509.01016 **[abs]**
  - Both are hypothesis refinement for rule induction and its error sources.

**E. Baselines that show the gap**
- **Hua et al. "InductionBench."** ACL 2025; arXiv 2502.15823. https://arxiv.org/abs/2502.15823 **[abs]**
  - LLMs fail to induce even subregular string functions from examples, and get worse with more data.
  - This is the right external baseline for "three examples, one question".
- **Ozelim, Zenil.** arXiv 2608.01575. https://arxiv.org/abs/2608.01575 **[abs]**
  - In-context algorithmic reasoning measured against an exact Bayes-optimal reference.

**F. Classical anchors not yet in L1–L6**
- Rivest & Schapire 1993, https://doi.org/10.1006/inco.1993.1021. B3 relies on it for O(log ℓ) counterexample
  processing.
- Gold 1967, https://doi.org/10.1016/S0019-9958(67)91165-5.
- Angluin 1987 *(known, L6)*.

### What remains new for I2

1. **Soundness by theorem, inside the model.** Every published loop either runs the hypothesis outside the LLM
   (Liu et al.; OPINE-World; WorldCoder; CEDAR's DFAs) or tolerates a noisy oracle statistically (pMAT, CAPAL,
   SmartLabel). Our version has the network that wrote the table execute it, with Theorem P making each disagreement
   refute the hypothesis.
2. **A stopping certificate.** No LLM learner I found reports an m-complete (W-method or H-method) suite, or a
   statement of the form "certain for ≤ m states". OPINE-World says outright that it has no guarantee off the data.
3. **An LLM that chooses its own queries against a black-box Mealy machine**, scored against L\*/L# query counts: not
   found.

### What this means for the bet

- B4's skeptic test is now the decisive one. A frontier model writing Python, plus AALpy's W-method, gives the same
  guarantee. The only delta is that the law lives inside the network.
- Run that arm first. If it matches on queries and correctness, I2 is a demonstration of Theorem P, not a new
  capability.
- Name Chen, Trivedi & Velasquez and Liu, Sala, Reps & Murali in the first related-work paragraph.

---

## 3. I3: self-predicted failure sets and self-repair. PARTLY DONE

### Evidence

**The closest: a learned automaton of a network's error set**
- **Mayr, Yovine, Visca. "Property Checking with Interpretable Error Characterization for Recurrent Neural
  Networks."** *Mach. Learn. Knowl. Extr.* 3(1):205–227, 2021. https://doi.org/10.3390/make3010010 (Crossref).
  Earlier version at CD-MAKE 2020. **[read §1–4]**
  - Method: Bounded-L\* learns an (ε, δ)-approximation of Ψ(C), the set of sequences on which the black-box
    classifier violates the property.
    - A nonempty DFA is a certain violation, and comes with an "explicit and interpretable characterization of the
      error".
    - An empty DFA gives a PAC bound.
  - **This is I3's artefact (a finite automaton for the infinite error set), published five years ago.** Theirs is
    PAC and black-box; ours would be exact and white-box.
- **Khmelnitsky, Neider, Roy, Xie, Barbot, Bollig, Finkel, Haddad, Leucker, Ye. "Property-Directed Verification and
  Robustness Certification of Recurrent Neural Networks."** ATVA 2021, LNCS 12971.
  https://doi.org/10.1007/978-3-030-88885-5_24 ; arXiv 2009.10610 **[read]**
  - Method: L\* builds a surrogate DFA, which is model-checked against a DFA specification.
  - Output: single counterexamples, generalised by pumping into "faulty flows" (81 of 109 counterexamples).
    RNN-vs-hypothesis inclusion is checked statistically, and termination is not guaranteed.
- **Tran et al. "Verification of Recurrent Neural Networks with Star Reachability."** HSCC 2023.
  https://doi.org/10.1145/3575870.3587128 (Crossref) **[abs]**
  - Builds a *complete* set of counterexamples, but only at fixed sequence lengths (T_max ≤ 20 in the experiments).
- **Zhang, Zhao, Chen, Song, Chen. "BDD4BNN."** CAV 2021. https://doi.org/10.1007/978-3-030-81685-8_8 ; arXiv
  2103.07224 **[abs]**
  - Exact BDD encoding of a binarised network's input–output relation, so misclassified inputs in a region can be
    counted (finite domain).

**Self-prediction of failure in LLMs (all statistical and per instance, never a set)**
- **Ghasemabadi, Niu. "Can LLMs Predict Their Own Failures?" (Gnosis).** arXiv 2512.20578.
  https://arxiv.org/abs/2512.20578 **[abs]**
- **Binder et al. "Looking Inward."** arXiv 2410.13787. https://arxiv.org/abs/2410.13787 **[abs]**
  - Self-prediction beats cross-prediction slightly, and only on short tasks.
- **Li et al. "Last Step Matters."** EMNLP 2026; arXiv 2608.29685. https://arxiv.org/abs/2608.29685 **[abs]**
  - At 50% of a trajectory, no uncertainty signal exceeds a mean AUROC of 0.60.
  - This is good contrast for B2's "my first mistake will be at step 41,307".
- Conformal and selective guarantees:
  - Quach et al., ICLR 2024, https://arxiv.org/abs/2306.10193;
  - Mohri & Hashimoto 2024, https://arxiv.org/abs/2402.10978;
  - 2026 abstention papers: https://arxiv.org/abs/2604.27914 and https://arxiv.org/abs/2607.04430.
  - All need calibration data and exchangeability. **[abs]**
- **Eyuboglu et al. "Domino."** ICLR 2022; arXiv 2203.14960. https://arxiv.org/abs/2203.14960 **[abs]**
  - Discovers and describes slices of systematic error. A statistical "describe where I fail".

**Repair with guarantees**
- **Sotoudeh, Thakur. "Provable Repair of Deep Neural Networks."** PLDI 2021; arXiv 2104.04413.
  https://arxiv.org/abs/2104.04413 **[abs]**
- CCL (see §5).

### What remains new for I3

- The failure set is **exact, of all lengths, and two-sided**: everything inside fails, everything outside is right.
  It comes from one forward pass per row, and a bounty can attack it.
- The repair lever is the model's **own renaming of symbols**. I found nothing on LLMs repairing themselves by
  renaming confusable identifiers.

### What this means for the bet

- Cite Mayr et al. as the origin of "a DFA of the network's errors" and claim exact instead of PAC.
- Once Theorem P holds, the failure set is a product construction. The paper must present I3 as a consequence that
  only the pin makes possible (`no_finite_test_suite`), not as a separate theorem.
- Keep B4's design rule: the specification must come from outside the model.

---

## 4. I4: the ∀ badge. PARTLY DONE

### Evidence

**Per-input proofs of outputs**
- **Amit, Goldwasser, Paradise, Rothblum. "Models That Prove Their Own Correctness."** NeurIPS 2025 (arXiv comment);
  ECCC TR24-098; arXiv 2405.15722. https://arxiv.org/abs/2405.15722 **[read]**
  - Setup:
    - the model proves its output to a fixed verifier V by an interactive proof;
    - soundness holds for every input;
    - "verifiability" holds on average over a distribution.
  - Experiment: a 6.3M GPT on GCD, with Bézout coefficients as the proof, and integers ≤ 10⁴. Annotated transcript
    learning reaches about 96% verifiability (v4, Table 2).
  - The proof certifies the **output**, not the network's computation; there is no claim about input length.
  - Delta: their proof is about the answer; ours is about the network on all inputs of all lengths.
- **Zhou et al. "Don't Trust: Verify."** ICLR 2024; arXiv 2403.18120. https://arxiv.org/abs/2403.18120 **[abs]**
  - Autoformalises each answer in Isabelle and rejects inconsistent ones: per-answer formal checks of outputs.

**Proofs about trained weights (finite domains)**
- **Gross, Agrawal, Kwa, Ong, Yip, Gibson, Noubir, Chan. "Compact Proofs of Model Performance via Mechanistic
  Interpretability."** NeurIPS 2024; arXiv 2406.11779. https://arxiv.org/abs/2406.11779 **[abs]**
  - Computer-assisted lower bounds on accuracy for Max-of-K, across 151 seeds and 102 proof strategies.
  - Shorter proofs need more mechanistic understanding.
- **Wu, Jaburi, Drori, Gross.** ICLR 2025; arXiv 2410.07476. https://arxiv.org/abs/2410.07476 **[abs]**
  - Compact proofs for group-operation networks. On S5, a ≥ 95% accuracy bound for 45% of models.
- **teal-sea/lean-checked-network.** GitHub, created 2026-10-15, last push 2026-10-27, 1 star.
  https://github.com/teal-sea/lean-checked-network (GitHub API)
  - It describes "Lean 4 kernel-checked results about trained neural networks: a transformer proved to add mod 113
    on all 12,769 inputs, and an alpha-beta-CROWN certificate for ACAS Xu … checked with standard axioms only".
  - Unreviewed, but it is the first Lean-kernel theorem about trained weights that I found. Finite domain, no length
    axis.
- **Somani 2026** *(known, L5 F15)*: solver-checked circuit claims over a hash-pinned 1,280-prompt domain.

**Proofs about programs the model writes (run outside the model)**
- **Sun, Sheng, Padon, Barrett. Clover.** arXiv 2310.17807. https://arxiv.org/abs/2310.17807 **[abs]**
- **Aggarwal, Parno, Welleck. AlphaVerus.** arXiv 2412.06176. https://arxiv.org/abs/2412.06176 **[abs]**
- **Yang et al. AutoVerus.** PACMPL 2025. https://doi.org/10.1145/3763174 **[abs]**
- **VERINA.** arXiv 2505.23135. https://arxiv.org/abs/2505.23135 **[abs]**
- **Vericoding benchmark.** arXiv 2509.22908. https://arxiv.org/abs/2509.22908 **[abs]**
- **Koomullil. "Proof-Carrying Certificates for LLM Pipelines."** arXiv 2605.16407.
  https://arxiv.org/abs/2605.16407 **[abs]**
  - Lean 4 certificates for the deterministic computation *around* the LLM, "rather than the model itself".

**Why the pin is needed (theory)**
- **Sälzer, Alsmann, Lange. "Transformer Encoder Satisfiability."** ICLR 2025; arXiv 2405.18548.
  https://arxiv.org/abs/2405.18548 **[abs]**
  - Satisfiability is undecidable for unbounded inputs.
  - It becomes decidable (NEXPTIME) with fixed-width arithmetic or a length bound.
  - Cite it beside `no_finite_test_suite`.
- **Jiang, Hague, Rümmer, Lin. "Synthesis and Verification of Transformer Programs."** arXiv 2602.16473.
  https://arxiv.org/abs/2602.16473 **[abs]**
  - Verifies C-RASP *programs* with Lustre/Kind2, not trained weights.

**Integrity, not correctness**
- **Sun, Li, Zhang. zkLLM.** ACM CCS 2024; arXiv 2404.16109. https://arxiv.org/abs/2404.16109 **[abs]**
  - Proves that specific weights produced an output. The cryptographic counterpart of "this code path".

**The certificate's own lineage**
- **Floyd. "Assigning meanings to programs."** Proc. Symp. Appl. Math. 19, 1967.
  https://doi.org/10.1090/psapm/019/0235771 (Crossref)
  - B3's Nerode certificate (a meaning per state, an initial condition, each row preserving meaning, outputs right
    under the meaning) is Floyd's inductive-assertion method applied to a finite-state program.
  - The completeness direction (label each state by its Nerode class) is textbook Myhill–Nerode.
- Framing papers that call for exactly this kind of artefact:
  - Dalrymple et al., "Towards Guaranteed Safe AI", arXiv 2405.06624, https://arxiv.org/abs/2405.06624 **[abs]**;
  - Tegmark & Omohundro, arXiv 2309.01933, https://arxiv.org/abs/2309.01933 **[abs]**.

### What remains new for I4

- A per-answer, kernel-checked theorem in which **the network's execution is the subject** (via Theorem P and the
  code-path hypothesis), quantified over all inputs of all lengths.
- Nothing found makes a ∀-length statement about a trained LLM. The nearest are finite-domain (Gross; Wu; teal-sea)
  or about outputs (Amit et al.).
- Do **not** claim the meaning certificate as new. Claim only the chain spec ⇐ table ⇐ network-under-clock.

---

## 5. I5: the certified ratchet. PARTLY DONE

### Evidence

**The idea's archetype**
- **Schmidhuber. "Gödel Machines: Self-Referential Universal Problem Solvers Making Provably Optimal
  Self-Improvements."** arXiv cs/0309048 (2003). https://arxiv.org/abs/cs/0309048 **[abs]**
  - The system rewrites itself only once it has proved the rewrite useful.
- **Zhang, Hu, Lu, Lange, Clune. "Darwin Gödel Machine."** arXiv 2505.22954. https://arxiv.org/abs/2505.22954
  **[abs]**
  - Drops the proof and accepts changes on empirical benchmark evidence (SWE-bench 20.0% → 50.0%).

**A verified core whose old programs stay correct (dangerous)**
- **Xiao, Liao, Yuan. "Improving the Universality and Learnability of Neural Programmer-Interpreters with Combinator
  Abstraction" (CNPI).** ICLR 2018; arXiv 1802.02696. https://arxiv.org/abs/1802.02696 **[read: §4, Theorem 1,
  Table 1, §5.1, App. C outline]**
  - Theorem 1: if the core and combinators "are trained and verified before being fixed", CNPI can "maintain correct
    interpretation of already learned programs" while new programs are added.
  - The paper states the regression problem itself: after Cai et al.'s RNPI trains on a new task, "the property of
    perfect generalization on old tasks may not hold any more".
  - Their answer is to freeze the core. Ours is to let the weights move and reject any update that fails
    recertification.

**Certified properties preserved across updates**
- **Pham, Sun. "Certified Continual Learning for Neural Network Regression" (CCL).** ISSTA 2024.
  https://doi.org/10.1145/3650212.3680322 ; arXiv 2407.06697 **[read]**
  - Certificates are DeepPoly-style intervals for each property.
  - Retraining uses synthetic data from certificate preconditions, regularisation and bias clipping.
  - It **does not reject updates**: certificates it cannot restore are dropped ("All the remaining certificates after
    the model clipping are valid").
  - Scale: small and medium networks (ACAS Xu, MNIST, CIFAR-10, Census).
- **Elmecker-Plakolm, Fasterling, Sosnin, Tsay, Wicker. "Provably Safe Model Updates."** SaTML 2026; arXiv
  2512.01899. https://arxiv.org/abs/2512.01899 **[abs]**
  - Finds the largest region of parameter space certified to keep a performance specification, and confines updates
    to it.
- **Anisimov, Belardinelli, Wicker. "SafeAdapt."** arXiv 2604.09452. https://arxiv.org/abs/2604.09452 **[abs]**
  - Projects RL updates onto a certified "Rashomon set".

**Gated skill libraries for LLM agents**
- **Moll et al. "GRASP: Gated Regression-Aware Skill Proposer."** EMNLP 2026; arXiv 2605.29668.
  https://arxiv.org/abs/2605.29668 **[abs]**
  - Admits an edit only if it improves a held-out probe within a hard regression budget.
  - The ablation says the gate, not the skill writing, drives the gain.
- **Jiang et al. "SoK: Agentic Skills."** arXiv 2602.20867. https://arxiv.org/abs/2602.20867 **[abs]**
  - Names "verification at the point of admission" as the open obstacle.
- **Metere. "Methods for Formal Verification of Agent Skills."** arXiv 2605.23951. https://arxiv.org/abs/2605.23951
  **[abs]**
  - Proof-carrying skill artefacts that prove containment, not correctness.
- **Lin. "Self-Improvement Can Self-Regress."** arXiv 2606.21090. https://arxiv.org/abs/2606.21090 **[abs]**
  - The rise-and-collapse failure of REINFORCE self-training on code: the motivation for a ratchet.

**Self-training on verified data (the STaR half is DONE many times over)**
- STaR, https://arxiv.org/abs/2203.14465;
- ReST-EM, https://arxiv.org/abs/2312.06585;
- expert iteration in Lean (Polu et al.), https://arxiv.org/abs/2202.01344;
- LEGO-Prover's growing library of verified lemmas, https://arxiv.org/abs/2310.00656;
- STP, https://arxiv.org/abs/2502.00212;
- LeanAgent, lifelong learning with Lean-verified proofs and forgetting metrics, https://arxiv.org/abs/2410.06209;
- Absolute Zero, executor-verified self-play, https://arxiv.org/abs/2505.03335;
- AlphaVerus (§4).

All **[abs]**.

### What remains new for I5

- The acceptance gate is a **complete** regression suite for the skill library: per-row recertification ⇔ every skill
  exact at every length (Theorems P and C). It is applied to **LLM weight updates**, and failing updates are rejected.
- No published system combines a completeness theorem, weight updates and a reject-on-fail gate.
- The weaker forms are all published:
  - preserve or repair certificates (CCL);
  - freeze the verified core (CNPI);
  - confine updates to a certified region (Wicker et al.);
  - gate on held-out probes (GRASP).
- Cite CNPI's sentence about RNPI as the earliest statement of the problem.

---

## 6. I8: certify the model, not the program. PARTLY DONE in shape, CLEAR for LLMs

### Evidence
- **CNPI (above), Theorem 1 and Table 1** **[read]**
  - Verify the core and five combinators once ("# verifications of programs/combinators: once"). Then every
    combinatorizable program, with verified detectors, is interpreted "correctly with perfect generalization (i.e.
    with any input complexity)".
  - **That is "certify the interpreter once, every program follows", for a small neural interpreter, in 2018.**
  - Limits:
    - the proof is on paper (Appendix C, by induction over appliers);
    - the core is verified on a finite trace set, Cai-style;
    - each task's condition detectors still need verifying;
    - LSTM core, no language.
- *(known, L1/L5)* Giannou et al.; Fixed Universal Transformers; Percepta.
  - These are hand-built or compiled universality, with no certificate of learned weights.
- **Friedman, Wettig, Chen. "Learning Transformer Programs."** NeurIPS 2023; arXiv 2306.01128.
  https://arxiv.org/abs/2306.01128 **[abs]**
  - Trains transformers constrained to decompile into readable programs: the "by construction" route to N\*.
- **Shaw et al. "ALTA."** TMLR 2025; arXiv 2410.18077. https://arxiv.org/abs/2410.18077 **[abs]**
  - A compiler (with loops) plus analysis of whether training data suffice for a program to be learned.
- **Sälzer et al. (ICLR 2025, §4)**
  - Over unbounded lengths, verifying a transformer encoder is undecidable; quantisation makes it decidable but hard.
  - This is the theory reason N\* needs the pin and a screened, finite vocabulary.
- **Gross et al.; Wu et al.; teal-sea (§4)**
  - Weights-level proofs, but on finite domains.

### What remains new for I8

- A certificate on **pretrained LLM weights** that quantifies over *all* tables up to N rows and all lengths. I found
  no such certificate for any learned transformer.
- CNPI must be cited as the precedent for the *form* of the claim.

---

## 7. I9: row-level credit for program-writing RL. PARTLY DONE

### Evidence
- **Kumar, Kumar, Gupta. "Execution-Grounded Credit Assignment for GRPO in Code Generation" (EGCA).** ICLR 2026
  SPOT workshop; arXiv 2603.16158. https://arxiv.org/abs/2603.16158 **[read]**
  - Method:
    - the candidate and a reference solution run under the same instrumentation;
    - the earliest divergence among "boundary blocks" (token span plus state snapshot, about 12.4 per sample) gets
      the whole GRPO advantage, and downstream tokens are masked;
    - compiler locations are used for syntax errors;
    - a debugging LLM aligns the traces.
  - It needs a reference solution.
  - Results: HumanEval 82.1 vs 79.0 for GRPO; MBPP 68.9 vs 67.4.
  - **This is I9's mechanism for Python code.**
- **Liu et al. "RLTF."** TMLR; arXiv 2307.04349. https://arxiv.org/abs/2307.04349 **[abs plus summary]**
  - Fine-grained feedback puts a −0.3 penalty on the line the compiler or runtime error points to.
- **Dou et al. "StepCoder."** arXiv 2402.01391. https://arxiv.org/abs/2402.01391 **[abs]**
  - Fine-grained optimisation that masks unexecuted code.
- **Dai et al. "Process Supervision-Guided Policy Optimization for Code Generation."** arXiv 2410.17621.
  https://arxiv.org/abs/2410.17621 **[abs]**
  - A line-level PRM, with labels from a binary search for the first erroneous line.
- **Li et al. "CodePRM."** Findings of ACL 2025. https://aclanthology.org/2025.findings-acl.428 **[abs]**
- **Yu et al. "ORPS."** ICML 2025; arXiv 2412.15118. https://arxiv.org/abs/2412.15118 **[abs]**
- **Cui et al. "PRIME."** arXiv 2502.01456. https://arxiv.org/abs/2502.01456 **[abs]**
- **Gehring et al. "RLEF."** arXiv 2410.02089. https://arxiv.org/abs/2410.02089 **[abs]**
- **Le et al. "CodeRL."** arXiv 2207.01780. https://arxiv.org/abs/2207.01780 **[abs]**
- **Ghedamsi & Bochmann 1992, "Test result analysis and diagnostics for finite state machines"; Ghedamsi, Bochmann &
  Dssouli 1993, "Diagnosing multiple faults in finite state machines".**
  https://www.site.uottawa.ca/~bochmann/Curriculum/Pub/ (PDF fetched, HTTP 200) **[abs from search summary]**
  - Localise the faulty transition of an FSM from a failed test.
  - Ambiguity is resolved with extra diagnostic tests.
  - The general algorithm blows up combinatorially (Hierons).

### What remains new for I9

- **Credit with zero execution noise**: a certified executor never slips, so every wrong answer indicts a row.
- **No debugger model**: given a reference table, the wrong row is the first divergence of the product run, and is
  exact.
- If only final answers are known, the "exact wrong row" claim is false in general. Finding the row is FSM fault
  diagnosis, which may need extra queries and may not give a unique row.
- The orchestrator's bet B must say whether it assumes per-step labels or a reference table.

---

## 8. I10: exact state over long documents. PARTLY DONE

### Already known (not re-reported)
CFSM, TemporalGuard, SpecGuard, LLM+ASP (Yang, Ishay & Lee), StateFlow, StateMem/StateMemBench, BABILong, ProPara,
the MD5 chain over 196 dependent tool calls, LongProc and Michelangelo (L2/L5).

### New evidence
- **Manginas, Paliouras, De Raedt. "NeSyA: Neurosymbolic Automata."** IJCAI 2025; arXiv 2412.07331.
  https://arxiv.org/abs/2412.07331 **[abs]**
  - Neural predicates feed a symbolic automaton, so local judgments get exact automaton control over the sequence.
  - It beats LSTMs on event recognition.
- **CEDAR (§2)** **[read]**
  - LLM semantic judgments over event traces, with DFAs for skills and constraints, composed by product.
- **Trooskens et al. "Compiled AI."** arXiv 2604.05150. https://arxiv.org/abs/2604.05150 **[abs]**
  - The LLM compiles code once, then the workflow runs with no LLM calls.
- **Zhang et al. "Chain of Agents."** NeurIPS 2024; arXiv 2406.02818. https://arxiv.org/abs/2406.02818 **[abs]**
- **Zhou et al. "LLM×MapReduce."** arXiv 2410.09342. https://arxiv.org/abs/2410.09342 **[abs]**
  - Both read chunks locally and carry state, as a natural-language summary or a structured protocol; neither is
    exact.
- **Yoneda et al. "Statler."** ICRA 2024; arXiv 2306.17840. https://arxiv.org/abs/2306.17840 **[abs]**
- **Wang, Wei, Choi, Ren. "Symbolic Working Memory."** EMNLP 2024; arXiv 2408.13654.
  https://arxiv.org/abs/2408.13654 **[abs]**
- **Saito. "NRR-Phi."** arXiv 2601.19933. https://arxiv.org/abs/2601.19933 **[abs]**
  - Explicit, typed text-to-state update contracts.
- **Wu et al. "LLM-FSM."** arXiv 2602.07032. https://arxiv.org/abs/2602.07032 **[abs]**
  - LLM accuracy at recovering FSM behaviour drops sharply with FSM complexity: a negative baseline.

### What remains new for I10

- The control skeleton runs **inside the LLM under the certificate**, so "end-to-end error equals snap error" and
  "cost per row" are theorems rather than properties of external code.
- The compiled semantic table is **checked row by row**.
- Everything else (local LLM judgments plus an exact automaton) is published, in Python, several times.
- The only defence against "use Python" is the in-network argument, which is weakest here, because documents never
  require it.

---

## 9. Items not verified, or verified only in part

- **"DREAMTEAM" (ARC-AGI-3 multi-agent world models).** A search snippet gave it arXiv 2605.09650, but that ID is
  "Workspace Optimization: How to Train Your Agent" (Sarafian et al.). Not cited.
- **"Extracting Robust Register Automata from Neural Networks over Data Sequences."** A search gave arXiv 2511.19100,
  which resolves to "Synthesis and Verification of Register Automata over Data Sequences" (Hong et al.). Not cited.
- **ExecVerify** (white-box RL with verifiable stepwise rewards for code execution reasoning). OpenReview
  forum DDZw4Y5gHY is behind a bot check, so I could not open it. Possibly close to I9.
- **PRL-Coder (Ye et al. 2025).** Seen only inside a survey (arXiv 2601.19100); not opened.
- **REASSURE (Fu & Li, ICLR 2022).** Seen only in search summaries; authorship and venue not confirmed.
- **"Skill Gen: Verified Inference-Time Agent Skill Synthesis."** Title only, from a Hugging Face listing. Possibly
  close to I5; worth a follow-up.
- **LogSynthFSM (KDD 2026)**, **StateAct**, **Neural Reward Machines**, **Aura-State (HN post)**: search mentions
  only.
- **Mayr et al.'s experiments section** (MAKE 2021): read §1–4 only.
- **CAPAL** has no arXiv version that I found. Verified via the ICLR 2026 virtual page; the OpenReview API returned
  nothing without authentication.
- **teal-sea/lean-checked-network**: existence and description verified via the GitHub API; the proofs themselves
  were not checked.
- **Ghedamsi & Bochmann 1992/93**: PDF host verified (HTTP 200); content taken from the search summary, not read.

---

## 10. Search log

**Engines and sources:**
- web search (standard and extended modes);
- arXiv API (export.arxiv.org) for every arXiv ID;
- Crossref API for DOIs;
- GitHub API;
- venue pages: ICLR 2026 virtual site, NeurIPS proceedings, ACL Anthology, MDPI, ar5iv, uOttawa;
- OpenReview, which was blocked by its bot check.

### I2
1. active automata learning large language models L\* Mealy machine LLM hypothesis (ext)
2. LLM-guided automata learning regular language inference language model proposes DFA counterexample (ext)
3. "Counterexample Guided Learning in the Large using Reasoning Agents"
4. LLM agent identifies hidden finite state machine black box experiments world model exact equivalence 2025 2026
   (ext)
5. language model program synthesis distinguishing input ask user disambiguate candidate programs active learning 2024
   (ext)
6. LLM writes program world model active exploration experiments revise rules Ellis WorldCoder PoE-World AutumnBench
   (ext)
7. language models W-method conformance testing equivalence oracle automata learning LLM learner sound counterexamples
   (ext)
8. in-context learning of finite automata LLMs induce transducer from few examples benchmark 2025 (ext)
9. "automata learning" "large language models" survey/position 2025 Mealy (ext)
10. LLM as learner in Angluin's MAT framework proposes hypothesis membership equivalence GPT-4 (ext)
11. "Doing Experiments and Revising Rules with Natural Language and Probabilistic Reasoning"
12. LLM-enhanced active model learning protocol state machine L# LLM prior reduce queries (ext)
13. ARC-AGI-3 agent learns game rules world model program synthesis 2026
14. "Active Learning for Neurosymbolic Program Synthesis" 2508.15750
15. AALpy GPT/LLM active automata learning Mealy 2025 2026 (ext)
16. "Active Automata Learning with Advice" Fica Otop
17. LLM identifies hidden automaton exact identification state bound scientific discovery agent Mealy benchmark (ext)
18. GATE eliciting human preferences; LLM most informative query rule learning
19. "three examples" rule induction LLM guarantee arbitrarily long inputs
20. can LLMs act as active learners asking membership queries (ext)
21. LLM system identification black-box device buttons hidden rules exact long prediction (ext)
22. LLM infers state machine from logs/traces passive learning equivalence 2025 2026 (ext)
23. Alsadat Gaglione Neider Topcu Xu LLM reward machine
24. CAPAL persistent noise-tolerant active DFA learning

### I3
1. NN verification exact set of failing inputs regular language RNN counterexample automaton PDV (ext)
2. LM predicts its own failures, which inputs it will get wrong, self-prediction introspection 2025 (ext)
3. provable repair of neural networks REASSURE Sotoudeh Thakur
4. BDD4BNN exact set misclassified; #DNN-verification counting unsafe inputs
5. "Property-Directed Verification" RNN Khmelnitsky … ATVA 2021
6. LLM self-repair renames identifiers near-duplicate names
7. predict in advance which step an LM will first err, long-horizon (ext)
8. exact characterisation of inputs on which a network errs, regular set of failing sequences, unbounded length (ext)
9. "Property Checking with Interpretable Error Characterization for Recurrent Neural Networks"
10. self-certifying LM certified abstention formal guarantee 2026 (ext)

### I4
1. self-proving models Amit Goldwasser Paradise Rothblum
2. compact proofs mechanistic interpretability Gross Max-of-K
3. formally verified trained transformer correct for all input lengths Lean Coq inductive invariant (ext)
4. proof-carrying answers LM machine-checked proof per answer 2025 2026 (ext)
5. Clover; AlphaVerus
6. certify network for all sequence lengths, proof assistant, verified automaton extraction (ext)
7. "Unifying and Verifying Mechanistic Interpretations"
8. Lean 4 proof about specific trained network weights kernel-checked (ext)
9. LLM writes automaton with per-state inductive invariant, Dafny/Lean (ext)
10. "Don't Trust: Verify"
11. "Towards Verifiable Transformers" Somani
12. zkLLM proofs of inference
13. transformer encoder verification arbitrary length undecidable Sälzer Lange

### I5
1. certified continual learning preserve verified properties after update (ext)
2. self-improving LLM accept update only if verified skill library passes, no-regression formal gate 2025 2026 (ext)
3. Darwin Gödel Machine; Gödel machine Schmidhuber
4. "SafeAdapt"
5. "Provably Safe Model Updates" 2512.01899
6. LEGO-Prover; STP; expert iteration Lean
7. formally verified skill library LLM agents, admission gating, monotone growth (ext)

### I8
1. weights-level certificate trained transformer in-context lookup any length margin head (ext)
2. verifying compiled transformer Tracr/RASP all inputs (ext)
3. formal guarantee from weights, all context lengths, induction head certificate (ext)
4. certify attention head retrieves correct key for every context up to length N (ext)
5. "for all programs" certificate neural interpreter verified universal executor trained weights (ext); plus I4 #3,
   #8 and #13

### I9
1. StepCoder RLTF fine-grained line-level reward
2. process reward from execution traces, credit to faulty line, fault localisation reward 2025 (ext)
3. "Execution-Grounded Credit Assignment for GRPO in Code Generation"
4. RL LLM generates FSM transition table, reward per transition (ext)
5. FSM fault diagnosis, faulty transition, Ghedamsi Bochmann
6. CodePRM execution-feedback PRM

### I10
1. LLM per-sentence state updates, deterministic program, BABILong neurosymbolic 100% (ext)
2. chunk-wise LLM structured state table, symbolic aggregation, exact entity tracking 2025 2026 (ext)
3. LLM semantic parser to automaton runtime monitor, ProPara, guarantees modulo grounding (ext)
4. BABILong neurosymbolic ASP/Prolog/Python (ext)
5. Chain of Agents; LLM×MapReduce
6. "Can Agent Memory Systems Track Evolving State"
7. NeSyA neurosymbolic automata; neural reward machines
8. LLM labels each event, automaton tracks state, long narrative (ext)
9. LLM sentence-to-operation plus deterministic executor, exact, length-independent (ext)
10. LLM compiles procedure or story to FSM verified per transition (ext)
11. symbolic working memory, external state table, BABILong/bAbI/ProPara (ext)

### Groups to watch (scoop risk)
- **Chen, Trivedi & Velasquez** (pMAT → CAPAL → CEDAR, 2024–2026): I2 and I10.
- **Reps & Murali, with Sala** (CEGML 2026): I2.
- **Barnaby & Dillig** (SmartLabel, Socrates): I2.
- **The Ellis group** (WorldCoder, PoE-World, AutumnBench): I2.
- **Gross and co-authors** (compact proofs): I4 and I8.
- **Wicker** (provably safe updates): I5.
- **Sanner** (OPINE-World): I2.
