# REDTEAM_C: prior art for M (error correction for programs) and P (log-depth certified execution)

Red team C, 28 Oct 2026. Every citation in §5 was checked live on **2026-10-28**, through the arXiv API
(export.arxiv.org), the Crossref API, ACL Anthology, or the venue or lab page. Items I could not confirm are in §6.
Items already in L1–L6, REDTEAM_A or REDTEAM_B are marked *(known)* and appear only for contrast.

Read depth: **[read]** means I read the method and results sections, from HTML or extracted PDF text. **[abs]** means
abstract and metadata only.

## Verdict table

| Idea | Verdict | Who got there first (closest, new to our map) | What is still ours, stated precisely |
|---|---|---|---|
| **M overall:** "digital error correction for programs inside the model" | **PARTLY DONE.** Each of the five parts has a precedent, and two are fully done. I found no paper that bundles them, or that runs the checks inside the same LLM. | **SemRegex** (Zhong et al., EMNLP 2018): exact minimal-DFA equivalence as the RL reward for NL→regex, plus distinguishing strings. **Mündler et al.** (PLDI 2025): type checking inside decoding, plus repair. **Co-rewarding** (ICLR 2026): agreement across rephrased questions as the training reward. **Nguena Timo et al.** (Mar 2026): GPT-4 (the code calls gpt-4o) writes DFSMs, which are repaired with distinguishing sequences. | (a) The checker, the equivalence test and the counterexample search are all run as the **same model's certified lookups**, with no interpreter. (b) **Exact automaton equivalence between programs compiled from different paraphrases, with no gold program,** used as a training signal. (c) The blindness theorem as the reason next-token training cannot fix compile errors that lie off its distribution. |
| M1. Type and well-formedness checker inside the model | **PARTLY DONE** (checkers in the loop are standard; inside the model as certified lookups: not found) | Synchromesh (ICLR 2022), monitor-guided decoding (NeurIPS 2023), **type-constrained decoding (PLDI 2025)**, SynCode (2024), typed holes (OOPSLA 2024), **TyFlow** (2025, learns typing derivations). Self-verification: Weng et al. 2023; GenRM (ICLR 2025). | A checker whose verdict is exact because each check is a certified forward pass of the same model. The check itself (alphabet, every cell has a row, header matches rows) is trivially decidable in 20 lines of Python. B4's "Python twin" objection applies in full. |
| M2. Snap to the nearest well-typed program | **DONE** (classical, and recent for LLMs) | Aho & Peterson 1972 (minimum-distance error-correcting parser); Seminal (PLDI 2007); Rite (PLDI 2020); **Alur et al. IJCAI 2013** (edit distance to the nearest correct DFA); Break-It-Fix-It (ICML 2021); Mündler 2025 (repair: +37% relative); **DCCD** (Feb 2026: draft, then a constrained projection). | Only the analogy (program-space closure ≙ state snap), and doing it with certified lookups. **Hazard:** snapping turns a detectable error into a silent one (§1.2). |
| M3. Decidable equivalence as a training signal ("Nerode training for compile") | **PARTLY DONE.** Done against a gold program; not found across paraphrases with exact equivalence. | **SemRegex 2018** (reward = 1 iff the minimal DFA equals the gold's; +12.6 points on KB13 over MLE). SoftRegex 2019 (a learned approximate equivalence). ReViSQL 2026 (bounded SQL equivalence in the RL reward). Agreement across paraphrases as a reward: **Co-rewarding-I** (ICLR 2026, answer equality), **PS-GRPO** (2025, BLEU), LoGIST (NeurIPS 2026). Equivalence voting at inference: Li et al. NeurIPS 2024; semantic triangulation 2025–26. | SemRegex's exact oracle combined with Co-rewarding's cross-paraphrase pseudo-labels: the minimal automata of two compiles of one question must agree, with no gold. A reviewer will describe it in exactly those words. The risk that agreement rewards consistent but wrong compiles is published (§1.3). |
| M4. Aimed adversarial paraphrases ("kicks" in language space) | **PARTLY DONE** | SCPN (NAACL 2018: adversarial paraphrases plus adversarial training); SEARs (ACL 2018); VAT (TPAMI 2018: worst-case direction in input space); text-to-SQL: Gan et al. ACL 2021 (adversarial training, explicitly *not* worst case), Pi et al. ACL 2022, Dr.Spider ICLR 2023; **Paul, Zhu & Bayley (Feb 2026)**: search for the minimal NL change that breaks the generated code (evaluation only). | Choosing the rewrite by the largest change in the compiled program's **equivalence class** (a decidable target, not BLEU or pass@1), and training invariance to it against an exact target. |
| M5. Shortest distinguishing inputs as exact counterexamples for repair | **DONE** | **SemRegex 2018** (distinguishing strings from R ∧ ¬R̂ during RL); **Nguena Timo et al. 2026** (distinguishing sequences fed back to the model to repair the DFSMs it wrote); D'Antoni et al. TOCHI 2015 (short counterexamples as feedback on DFA constructions); Orvalho et al. AAAI 2025 (CEGIS repair for LLMs); Liu, Sala, Reps & Murali 2026 *(known, REDTEAM_B)*. | Nothing beyond running the counterexample inside the model. |
| **P. Log-depth parallel certified execution** | **PARTLY DONE (the algorithm and the in-network version); CLEAR for the exact claim** | Algorithm: Kogge–Stone 1973, Ladner–Fischer 1980, Hillis–Steele 1986, Blelloch 1990/93, **Mytkowicz, Musuvathi & Schulte (ASPLOS 2014: enumerate every start state per chunk, compose by table gather)**. In-network: Liu et al. 2023 *(known)*, Rizvi et al. AISTATS 2024, Brandoit 2026 *(known)*, MLP-LDRU 2026, Log-Depth RLM 2026, DEER/ELK. LLM calls: flat or recursive merging only (D&C noise, ICLR 2026; RLM 2025; Multiverse 2025; LLM×MapReduce *(known)*). Exact long runs with LLM calls are all sequential (MAKER *(known)*; the MD5 run over 196 calls, Aug 2026). | No paper found executes **an LLM's own per-step forward passes as an associative scan** (log₂T rounds of batched lookups), with **each composition itself a certified forward pass**. Two engineering obstacles (§2.3) decide whether that is a theorem or a slogan: composing needs functions rather than states, and the certificate must hold under batching. |

**Ranked by kill strength:** M5 (done twice, including an LLM-on-DFSM paper from March 2026) > M2 (fifty years old) >
M3 (SemRegex took exact-DFA-equivalence training in 2018; only the no-gold cross-paraphrase version is left) >
M4 > M1 > P (the algorithm is textbook, but no one runs an LLM's own certified steps through it).

**New blind-spot items that matter beyond M and P** (none appear in L1–L6, REDTEAM_A or REDTEAM_B):
- **SemRegex (EMNLP 2018).** The earliest place where "minimal-DFA equivalence is the right training signal for a
  program-writing model" is stated and measured. Any v2 sentence about "Nerode training" or "certified equivalence as
  a loss" must cite it.
- **Nguena Timo, Rodriguez & Avellaneda (arXiv 2603.29140, Mar 2026).** GPT-4 (gpt-4o in their code) writes deterministic, input-complete
  FSMs as CSV transition tables, which are checked against an oracle through a distinguishing automaton and repaired.
  It is the nearest published neighbour of Savant's compile step.
- **Mytkowicz et al. (ASPLOS 2014).** "Compose transition tables by gather" is their primitive. It is what P's
  "certified lookups compose associatively" reduces to.
- **Thinking Machines, "Defeating Nondeterminism in LLM Inference" (Sep 2025 blog).** Batch-variant kernels mean
  that a batched forward is not the certified forward. This bears on P and on Theorem P's "same code path"
  hypothesis (§2.3).

---

## 1. M: error correction for programs

### 1.1 M1. A type and well-formedness checker inside the model

**External checkers in the loop (standard since 2022):**
- **Poesia et al., Synchromesh** (ICLR 2022; arXiv 2201.11227) [abs]. Constrained semantic decoding uses a completion
  engine that enforces scoping and type rules on partial programs (SQL, Vega-Lite, SMCalFlow).
- **Agrawal et al., monitor-guided decoding** (NeurIPS 2023; arXiv 2306.10763) [abs]. A static analysis runs as a
  monitor during decoding.
- **Mündler, He, Wang, Sen et al., type-constrained code generation** (PACMPL/PLDI 2025; arXiv 2504.09246;
  DOI 10.1145/3729274) [read: intro, §2–3 from the PDF text].
  - A *prefix automaton* tracks the type environment Γ (declared identifiers and their types).
  - A search over inhabitable types decides whether a partial expression can still reach the required type. Only
    tokens with that property survive.
  - The prefix property guarantees that every reachable state can still be completed into an accepted program, so
    the procedure is sound.
  - About 94% of compile errors in LLM-written TypeScript are type errors and 6% are syntax errors.
  - Results: compile errors fall by more than half. Functional correctness rises by 3.5–5.5% relative, and
    "functionally correct repair of non-compiling code" by 37% relative.
  - The checker is symbolic and external. It masks logits.
- **Ugare et al., SynCode** (arXiv 2403.01632) [abs]. **Blinn et al., typed holes** (OOPSLA 2024; arXiv 2409.00921)
  [abs]. **Park et al., grammar-aligned decoding** (NeurIPS 2024; arXiv 2405.21047) [abs].
- **Huang et al., TyFlow** (arXiv 2510.10216, Oct 2025) [abs]. This is the closest to "inside the model".
  - Typing rules are mapped one-to-one onto synthesis rules.
  - The model is trained on decision sequences derived from type derivations, so it "internalizes" type reasoning
    rather than being masked.
  - It is a learned, uncertified internal checker.

**Self-verification by the same model (uncertified):** Weng et al. 2023 (EMNLP Findings; arXiv 2212.09561) [abs];
Zhang et al., GenRM (ICLR 2025; arXiv 2408.15240) [abs].

**Compiler feedback in training (known in part):**
- RLEF *(known, REDTEAM_B)*.
- CodeRL (arXiv 2207.01780), PPOCoder (TMLR; arXiv 2301.13816) and StepCoder (arXiv 2402.01391) [abs].
- Self-Debugging (arXiv 2304.05128), Reflexion (arXiv 2303.11366), LEVER (ICML 2023; arXiv 2302.08468) and CodeT
  (arXiv 2207.10397) [abs].

**Verdict and what is left.** "Lint before execute" is standard. What I did not find is a checker whose every step is a
lookup by the *same* LLM, certified per row, so that its verdict is exact by Theorem P rather than a learned
judgment.

The weakness to say out loud: the checks named in M1 are a finite syntactic test that a script does exactly. The only
reason to put them inside the model is the "no interpreter" thesis. A reviewer will ask what the inside version buys
over `assert set(rows) == Q × Σ`. The honest answer is uniformity: one mechanism, one certificate. It is not
capability.

### 1.2 M2. Snap the program to the nearest well-typed program: DONE

- **Aho & Peterson. "A Minimum Distance Error-Correcting Parser for Context-Free Languages."** SIAM J. Comput. 1(4),
  1972. DOI 10.1137/0201022 (Crossref). This is the original "snap to the nearest string in the language".
- **Lerner, Flower, Grossman & Chambers, Seminal.** PLDI 2007. DOI 10.1145/1250734.1250783. The type checker is an
  oracle inside a search for nearby programs that do type-check.
- **Sakkas, Endres, Cosman, Weimer & Jhala, Rite.** PLDI 2020. DOI 10.1145/3385412.3386005. A learned repair template
  is followed by synthesis of the closest type-correct fix.
- **Alur, D'Antoni, Gulwani, Kini & Viswanathan. "Automated Grading of DFA Constructions."** IJCAI 2013,
  https://www.ijcai.org/Abstract/13/292 [abs].
  - "How many states and transitions of A we need to modify" to obtain a correct DFA: that is the nearest correct
    automaton under edit distance.
  - They found that edit distance alone is not enough. They add a semantic distance and a "misread the problem"
    distance (MOSEL).
- **Yasunaga & Liang, Break-It-Fix-It.** ICML 2021; arXiv 2106.06600 [abs]. A learned fixer maps broken programs to
  good ones, with a critic (the compiler) deciding what counts as fixed. DrRepair (ICML 2020; arXiv 2005.10636) is its
  predecessor.
- **Mündler et al. 2025** (above): the repair task is done by constrained regeneration.
- **Reddy, Walker, Ide & Bedi. "The Hidden Cost of Structured Generation in LLMs: Draft-Conditioned Constrained
  Decoding" (DCCD).** arXiv 2603.03305, Feb 2026 [read: method and results].
  - An unconstrained draft is followed by constrained decoding conditioned on the draft.
  - They state standard constrained decoding as a per-step reverse-KL projection onto the valid set. The "projection
    tax" is the sum of log(1/feasible mass).
  - GSM8K strict accuracy goes from 15.2% to 39.0% at 1B, and from 49.4% to 73.9% at 1.5B.
  - Training-free. This is "snap the draft into the well-formed set" in current LLM form.

**Red-team point that matters more than priority.**
- Snapping a wrong table to the nearest well-formed table makes the error **silent**.
  - M1 exists to *detect* errors, and the snap then *erases the evidence*.
  - DCCD warns that hard masking yields "valid but semantically wrong" outputs. Alur et al. needed semantic distance
    because syntactic nearness is the wrong metric.
- In v1 the snap works because a *code* separates the cells (the margin). A program space has no such margin: a
  one-cell edit moves to a different, equally well-formed program.
- So the state analogy fails exactly where it would matter. Snap only when the edit is forced: for example a missing
  row with a single declared default, or a header typo with a unique match. Otherwise reject and recompile.

### 1.3 M3. Decidable semantic equivalence as a training signal

**Done against a gold program:**
- **Zhong, Guo, Yang, Peng, Xie, Lou, Liu & Zhang. "SemRegex."** EMNLP 2018, https://aclanthology.org/D18-1189/
  **[read: §2–4, Table 2]**
  - Regex → minimal DFA. Reward r(R) = 1 iff R's minimal DFA equals the gold's, else 0. Trained by policy gradient
    from an MLE-pretrained seq2seq model.
  - The motivation is "program aliasing": MLE penalises equivalent programs that differ in syntax.
  - DFA-equivalence accuracy:
    - KB13: 65.6% (MLE) → 78.2%;
    - NL-RX-Synth: 88.7% → 91.6%;
    - NL-RX-Turk: 58.2% → 62.3%.
  - No paraphrases and no agreement between two outputs: the equivalence is always to the gold.
- **Park et al. "SoftRegex."** EMNLP 2019, https://aclanthology.org/D19-1677/ [abs]. Exact equivalence is
  PSPACE-complete for regexes, so they replace it with a learned equivalence probability. This is the
  "it is too slow" objection. It does not apply to explicit transition tables: DFA minimisation and equivalence are
  near-linear.
- **Zhu, Jin, Choi & Kang. "Human-Level Text-to-SQL via RL on Verified Data" (ReViSQL).** arXiv 2603.20004, Mar 2026
  [abs + search summary].
  - A bounded SQL equivalence checker (VeriEQL) flags 32.8% of execution-match rewards as false positives.
  - The reward is down-weighted when equivalence is refuted.

**Agreement across paraphrases as a training reward (answers, not programs):**
- **Zhang et al. "Co-rewarding."** ICLR 2026; arXiv 2508.00410 **[read: method and Table 1]**
  - Co-rewarding-I rephrases each question (Qwen3-32B, "keeps the semantical equivalence", no check). It samples G = 8
    rollouts for each version.
  - The majority answer of one version is the pseudo-label that rewards the other version's rollouts, and vice
    versa. The reward is 1[ans(y) = pseudo-label].
  - It is label-free. It still collapses on DAPO-14k.
- **Hamman et al. "Paraphrased Set GRPO" (PS-GRPO).** arXiv 2510.04392, NeurIPS 2025 workshop **[read: method and
  results]**
  - The reward is the BLEU similarity of a rollout to rollouts for *other* paraphrases.
  - TriviaQA consistency: 53.0 → 87.3 (lexical).
- **Liu et al. "LoGIST: logic-invariant LLMs."** NeurIPS 2026; arXiv 2610.25402 [abs]. Consistency across logically
  equivalent inputs, through a decision-diagram embedding.

**Equivalence among samples, at inference only:**
- **Li et al. "Autoformalize Mathematical Statements by Symbolic Equivalence and Semantic Consistency."** NeurIPS 2024;
  arXiv 2410.20936 [abs]. ATP-checked equivalence clusters choose among k formalisations.
- **Poiroux, Weiss, Kunčak & Bosselut.** EMNLP 2025; arXiv 2406.07222 [abs]. Type-check filtering plus self-consistency
  gives up to +18.4% on ProofNet; Lean equivalence tooling is released.
- **Dai, Liang, Xu, Xie & Mechtaev. "Semantic Triangulation."** arXiv 2511.12288 (v4 Sep 2026) [abs + search summary].
  - It transforms the problem into a semantically different one that has an exact mapping between solutions (inverse,
    decomposition, enumeration).
  - It accepts a program only when solutions agree across the transformation. Some proofs are in Lean.
  - Selection and abstention only.

**Not found.** I found nothing that takes two programs compiled from **different paraphrases of one question**,
compares them by **exact minimal-automaton equivalence**, and uses agreement as a **training** signal with no gold
program. That is the narrow residue of M3.

**Risks the literature already names:**
- Agreement rewards consistent but wrong compiles: Co-rewarding's collapse on DAPO-14k; Knight & Leveson's correlated
  N-version failures *(known, L6 §3.3 and E10)*.
- INSIGHTS §2.7: 64–88 of 1,280 gate answers were certified with a wrong table. Equivalence-as-agreement does not
  touch errors that both paraphrases share, such as a misread default rule.

**Name.** Vafa et al. (NeurIPS 2024) *(known, REDTEAM_A)* already use Myhill–Nerode as an *evaluation* metric for world
models. "Nerode training" as the name for an equivalence reward will draw that comparison and SemRegex's priority.

### 1.4 M4. Aimed adversarial paraphrases

- **Iyyer, Wieting, Gimpel & Zettlemoyer. SCPN.** NAACL 2018; arXiv 1804.06059 [abs]. Syntactically controlled
  paraphrases serve as adversarial examples, and adversarial training on them improves robustness. This is the
  original "kick in paraphrase space".
- **Ribeiro, Singh & Guestrin. SEARs.** ACL 2018, https://aclanthology.org/P18-1079/ [abs]. Semantically equivalent
  adversarial rules.
- **Miyato et al. Virtual Adversarial Training.** arXiv 1704.03976 [abs]. The worst-case local direction, the
  continuous ancestor of "aim the kick".
- **Gan, Chen, Huang et al. Spider-Syn.** ACL 2021; arXiv 2106.01065 [abs]. Synonym substitution plus adversarial
  training for text-to-SQL. The abstract says the substitutions are "not adversarially selected to conduct worst-case
  attacks".
- **Pi et al. ADVETA.** ACL 2022; arXiv 2212.09994 [abs]. Adversarial table perturbation and augmentation as the
  defence.
- **Chang et al. Dr.Spider.** ICLR 2023; arXiv 2301.08881 [abs]. 17 perturbations. The most robust model still drops
  14.0% overall and 50.7% on the hardest perturbation.
- **Wang et al. ReCode.** arXiv 2212.10264 [abs]. Robustness of code generation to docstring and name perturbations.
- **Saparina & Lapata.** EACL 2024; arXiv 2402.08666 [abs]. LLM-generated question reformulations as augmentation
  improve Dr.Spider robustness.
- **Ghosh Paul, Zhu & Bayley. "Operational Robustness of LLMs on Code Generation."** arXiv 2602.18800, Feb 2026 [abs].
  - They search for "the expected minimal change in the natural language descriptions" that makes the generated code
    wrong.
  - The paraphrases are word-replacement mutants. Functional equivalence is checked against the code generated from
    the original task.
  - Evaluation only. It is the closest to an aimed kick.

**What is left.** The aim is defined by a *decidable* change in the compiled program's equivalence class, rather than by
pass@1, BLEU or embedding loss. Invariance is then trained against an exact equivalence target. The theoretical reason
(blindness) is also left.

The component that is new is the target, not the adversarial loop. Note also that Dr.Spider found only 270 of 500
human paraphrases to be meaning-preserving. Automatic "paraphrases" that change the compiled automaton will often be
**real meaning changes**. An aimed search will find those first, so you need a semantic-preservation check that is
independent of the compiler, or the method trains the model to ignore real differences.

### 1.5 M5. Shortest distinguishing inputs as counterexamples: DONE

- **SemRegex 2018** (above). Algorithm 2 builds distinguishing strings from R ∧ ¬R̂ and ¬R ∧ R̂ against beam samples of
  the pretrained model, and uses them as the test-case reward. KB13 77.5% (distinguishing) vs 66.5% (random tests).
- **Nguena Timo, Rodriguez & Avellaneda. "Designing FSMs Specifications from Requirements with GPT 4.0."** arXiv
  2603.29140, 31 Mar 2026 **[read: §2–5, Tables 1–5]**
  - GPT-4 (Listing 1 calls gpt-4o) writes deterministic, input-complete FSMs as CSV rows (State, Input, Output, Next_State).
  - Each is compared with an oracle machine through a distinguishing automaton (equivalent iff its language is empty).
  - Repair uses four sources: syntactic diffs, distinguishing sequences (random accepting paths, not shortest),
    checking sequences answered by an expert, and SAT-based mining over mutation machines.
  - Distinguishing-sequence repair: 100% at 5 states, 0% at 10 states. Fault-model repair: 100% at 10 states.
  - No training.
- **D'Antoni, Kini, Alur & Gulwani. "How Can Automatic Feedback Help Students Construct Automata?"** ACM TOCHI 2015.
  DOI 10.1145/2723163 (Crossref). Short counterexample strings as feedback; a study with 377 students.
- **Orvalho, Janota & Manquinho.** AAAI 2025; arXiv 2502.07786 [abs]. CEGIS-style LLM program repair with
  counterexamples and MaxSAT fault localisation.
- Liu, Sala, Reps & Murali 2026 *(known, REDTEAM_B)*: exact DFA-equivalence counterexamples returned to an LLM.

**Verdict:** DONE. Nothing remains except "the counterexample search runs inside the model". That claim depends on M1's
justification.

### 1.6 The theory claim ("blindness of next-token loss to off-distribution program errors")

- SemRegex's "program aliasing" is the nearest published *argument*: MLE is a syntax-based objective that penalises
  correct alternatives. Blindness is the dual: MLE cannot see wrong programs off the data. That is distinct, but a
  reviewer will put the two side by side.
- Exposure-bias and compounding-error theory is covered in L4 *(known)*. Applying the blindness theorem to the compile
  step looks like ours. Its value depends on a measured consequence: for example, compile errors on held-out
  paraphrases that next-token loss on gold programs does not reduce, and that an equivalence reward does.

---

## 2. P: log-depth parallel certified execution

### 2.1 The algorithm is textbook

- **Kogge & Stone. "A Parallel Algorithm for the Efficient Solution of a General Class of Recurrence Equations."**
  IEEE Trans. Comput. 1973. DOI 10.1109/TC.1973.5009159 (Crossref). Carry-lookahead as a parallel prefix over the
  {kill, propagate, generate} monoid.
- **Ladner & Fischer. "Parallel Prefix Computation."** J. ACM 27(4), 1980. DOI 10.1145/322217.322232 (Crossref). FSM
  runs as a prefix over Boolean transition matrices, per Mytkowicz §2.2.
- **Hillis & Steele. "Data Parallel Algorithms."** CACM 1986. DOI 10.1145/7902.7903 (Crossref). Function composition
  as the scan operator. Mytkowicz credits them with the transition-function formulation.
- **Blelloch. "Prefix Sums and Their Applications."** CMU, 1990/93. https://www.cs.cmu.edu/~guyb/papers/Ble93.pdf
  [read §1.1, §1.4]. A work-efficient scan (O(n) work, 2 log n depth) and recurrences.
- **Mytkowicz, Musuvathi & Schulte. "Data-Parallel Finite-State Machines."** ASPLOS 2014.
  DOI 10.1145/2541940.2541988 (Crossref) **[read: §1–3]**
  - Each chunk is run from **every** start state (the "enumerative computation").
  - The resulting transition-function tables are composed by **gather**, S ⊗ T [i] = T[S[i]], which is associative.
    That is a table lookup.
  - The overhead is ×n work for n states, recovered by "convergence": active states collapse to 16 or fewer.
  - 3× faster on one core and 21× on 8 cores, on regex, Huffman and HTML tokenisation.
  - Follow-up: Qiu et al., ASPLOS 2021, DOI 10.1145/3445814.3446705.
- **Barrington.** JCSS 1989. DOI 10.1016/0022-0000(89)90037-8. Width-5 branching programs = NC¹. The S5 word problem
  is NC¹-complete, so log-depth composition is optimal in depth for general automata unless TC⁰ = NC¹.
  - **Use this.** With each call a constant-depth forward pass (Merrill & Sabharwal *(known, L2)*), no O(1)-round
    scheme exists for S5, so log T rounds is the right target.

### 2.2 The neural and LLM versions

**In-network log-depth composition (constructions and architectures):**
- Liu et al. ICLR 2023 *(known)*.
- **Rizvi, Lizaire, Lacroce & Rabusseau.** AISTATS 2024 (PMLR v238); arXiv 2403.09728 [abs]. Transformers simulate
  weighted automata at depth log T by a recursive parallel scan.
- **Engelmayer, Georgiev & Veličković. "Parallel Algorithms Align with Neural Execution."** LoG 2023 (PMLR 231); arXiv
  2307.04049 [abs]. Parallel algorithms train better than sequential ones on CLRS.
- **Pert, Alrajeh & Russo. MLP-LDRU.** arXiv 2605.26035, May 2026 [abs]. A log-depth recurrent unit by parallel
  reduction: 100% OOD on 18 of 21 regular-language tasks and ≥99.9% on the other 3.
- **Wang, Cingillioglu & Pert. "Log-Depth Recurrent Language Modeling."** arXiv 2609.28212, Sep 2026 [abs]. Adds a
  Blelloch down-sweep for autoregressive LM. Outputs are tree-invariant only if the operator is associative.
- **Gaudreault & Mao. "Parallel Recursive LSTM."** arXiv 2605.17108 [abs].
- **Shaj et al. "Kalman Linear Attention."** ICML 2026; arXiv 2602.10743 [abs].
- **Yau et al. "Prefix Scannable Models."** arXiv 2506.10918 *(known, L2 B23)*.
- **Lim et al. DEER** (arXiv 2309.12252) and **Gonzalez et al. ELK** (NeurIPS 2024; arXiv 2407.19115) [abs]. Newton
  iterations, each a parallel scan, evaluate *nonlinear* RNNs in parallel over the sequence. This is the continuous
  analogue of "run a sequential model in log rounds".
- Brandoit et al. 2026 *(known)*: NFSM tables composed under a scan, certified by margin. **This is the closest
  in-network twin of P: certified tables composed associatively.**
- Li, Guo & Andreas 2025 *(known)*: fine-tuned LMs learn an associative scan internally, and it breaks beyond a
  cutoff.

**Parallelism over LLM calls (none associative, none exact):**
- **Xu et al. "When Does Divide and Conquer Work for Long Context LLM?"** ICLR 2026; arXiv 2506.16411 **[read:
  framework, Tables 2–3]**
  - A single LLM manager merges flat; hierarchy appears only as a proof assumption.
  - The "aggregator noise" term is exactly what associativity plus certification would remove.
- **Zhang, Kraska & Khattab. Recursive Language Models.** arXiv 2512.24601 [abs]. Recursive sub-calls over pieces of
  the prompt from a REPL.
- **Yang et al. Multiverse.** arXiv 2506.09991 [abs]. MapReduce-style native parallel generation.
- **Pan et al. APR.** COLM 2025; arXiv 2504.15466 [abs].
- **Rodionov et al. Hogwild! Inference.** NeurIPS 2025; arXiv 2504.06261 [abs].
- **Ning et al. Skeleton-of-Thought.** ICLR 2024; arXiv 2307.15337 [abs].
- **Jin et al. PASTA.** arXiv 2502.11517 [abs].
- **Fu et al. Lookahead Reasoning.** arXiv 2506.19830 [abs]. Step-level speculation verified in a batch.
- LLMCompiler and LLM×MapReduce *(known)*.
- **Anari et al. "Parallel Sampling via Autospeculation."** arXiv 2511.07869 [abs]. Õ(√n)-round sampling from
  autoregressive oracles. A different problem (sampling, not deterministic execution), but the nearest
  "fewer rounds than steps" result for LMs.

**Exact long runs with LLM calls are sequential:**
- MAKER, Schuurmans, Lewandowski and Percepta *(known)*.
- **Mohandas Pai & Xian.** arXiv 2609.00012, Aug 2026 [abs]. MD5 through 196 dependent tool calls; state is carried in
  context, with voting. Strictly sequential.
- **Sinha et al. "The Illusion of Diminishing Returns."** arXiv 2509.09677 [abs].

**Not found.** I found no paper or blog in which an LLM's *own* step lookups are executed as a parallel prefix: a
log₂T-round schedule of batched forward passes in which each composition is itself a model forward checked against a
certificate. P is **CLEAR** at that resolution.

### 2.3 What decides whether P is a theorem or a slogan

1. **Composition needs functions, not states.** Under the pin, a lookup is (s, e) ↦ s′. A scan needs chunk functions
   Q → Q. There are two routes, and both have a cost the claim must state.
   - **Enumerative (Mytkowicz).**
     - Run each chunk from all |Q| start states: |Q|·T certified lookups, which is |Q| times the sequential work.
     - Then compose by gather, T[S[i]]. These are lookups into tables **written at run time**, not into the certified
       program. Each needs its own per-row certificate (|Q| forwards per table per round) or must happen outside the
       model, which breaks "every lookup is a certified forward pass".
     - Convergence (Mytkowicz §3) is the known mitigation.
   - **Monoid table.**
     - Write and certify, once, the multiplication table of the program's transition monoid. Then every scan node is
       a certified lookup in a fixed table.
     - For the adder this is the 3-element {K, P, G} monoid: 9 rows, plus 100 rows mapping digit pairs to K/P/G. That
       is excellent and fully certifiable.
     - For S5 it is 120 × 120 = 14,400 rows. INSIGHTS S reports about 1 row in 1,000 lost at 2,048–4,096 rows, so the
       name pool needs screening.
     - In general the monoid has up to |Q|^|Q| elements, which is Liu et al.'s Krohn–Rhodes point. **Claim P for
       small transition monoids, and say so.**
2. **Batching breaks "the same code path".**
   - Theorem P's hypothesis is that the deployed forward is the certified forward. INSIGHTS P-M already records a
     non-bitwise 1-token forward (86% of ticks), and BRIDGE recorded an HF/vLLM disagreement.
   - P runs thousands of rows per batch. Batch-variant kernels (Thinking Machines, Sep 2025) make a row's logits depend
     on batch size and composition.
   - Either certify under the exact batched path, or use batch-invariant kernels, or state a margin-based version
     (RC: `robust_cell` with τ covering the batch-induced drift).
3. **Work against depth.**
   - Kogge–Stone does n log n work. Brent–Kung/Blelloch do O(n) work in 2 log n depth.
   - For 8,000-digit addition: about 26 scan rounds plus 2 rounds of digit lookups, against 8,000 ticks, with 2–3 times
     the total forwards.
   - In a browser on WebGPU, wall-clock gains depend on batch width. Measure tokens per second, not rounds.
4. **Parallel sentence reads are not new.** Parallel Context Windows (ACL 2023), APE (ICLR 2025) and Block-Attention
   *(known, L3)* already restart positions per block.
   - The event quote is the measured failure locus (INSIGHTS §2.3). Parallel reads do not help it.
   - P speeds up the part that already works.

**What P can claim, precisely.**
- The model's own certified lookups, organised as a Blelloch scan over a **certified monoid table**, give the exact
  result in O(log T) rounds.
- Theorem P extends to the scan when the monoid table is certified on the deployed batched path. The Lean statement
  would be a scan-tree version of `compose_exact`.
- Barrington shows log T rounds cannot be beaten for S5.
- Everything except "the lookup is a certified LLM forward pass" is 1973–2014.

---

## 3. Closest papers, read beyond the abstract

| Paper | Read | Why it is closest |
|---|---|---|
| Zhong et al., SemRegex, EMNLP 2018 | §2–4, Alg. 1–2, Table 2 (PDF text) | Exact minimal-DFA equivalence as the RL reward, plus distinguishing strings: M3 (gold) and M5 |
| Nguena Timo, Rodriguez & Avellaneda, arXiv 2603.29140 | §2–5, Tables 1–5 (HTML) | An LLM writes FSM transition tables; equivalence via a distinguishing automaton; counterexample repair: M5 and Savant's compile step |
| Yang et al., "Fine-Tuning Language Models Using Formal Methods Feedback", arXiv 2310.18239 | method, experiments (HTML) | An LLM's steps become an FSA controller, model-checked with NuSMV against 15 LTL specs. DPO on "satisfies more specs". Spec satisfaction goes from 60% to 90% (Llama-2-7B, LoRA). Formal verification of LLM-written automata *driving training*, but by spec count, not by equivalence, and not well-formedness |
| Zhang et al., Co-rewarding, ICLR 2026 | method, Table 1 (HTML, first half) | Cross-paraphrase agreement as the training reward: M3 without exact program equivalence |
| Hamman et al., PS-GRPO, arXiv 2510.04392 | method, results (HTML) | Paraphrase-set consistency reward |
| Reddy et al., DCCD, arXiv 2603.03305 | method, results (HTML) | A draft snapped into the well-formed set: M2 in current LLM form |
| Mündler et al., PLDI 2025 | intro, §2–3 (PDF text) | Type checker inside decoding, with repair: M1 and M2 |
| Mytkowicz et al., ASPLOS 2014 | §1–3 (PDF text) | Enumerate start states per chunk and compose tables by gather: P's primitive |
| Xu et al., D&C for long context, ICLR 2026 | framework, Tables 2–3 (HTML) | LLM chunk-and-merge with an "aggregator noise" term: the LLM-call baseline P must beat |

---

## 4. Queries and venues searched

**Venues and sources:**
- arXiv (API and abstract pages), ACL Anthology, ICLR, NeurIPS and ICML virtual pages, PMLR, ACM DL via Crossref,
  IEEE via Crossref, IJCAI, mlanthology.
- Microsoft Research publication pages, Berkeley BAIR blog, Thinking Machines blog, Cognizant AI Lab page,
  percepta.ai, EPFL Infoscience.
- Web search in extended mode for every query marked (ext).

**For M:**
1. type-constrained code generation language models 2025 type system decoding (ext)
2. semantic equivalence reward reinforcement learning paraphrase consistency text-to-SQL program equivalence training signal (ext)
3. natural language to regular expression DFA equivalence reward training SemRegex SoftRegex (ext)
4. paraphrase invariance semantic parsing consistency training equivalent logical forms across paraphrases (ext)
5. adversarial paraphrase semantic parsing robustness training text-to-SQL Dr.Spider perturbation (ext)
6. LLM code generation consistency across paraphrased prompts semantically equivalent prompts training invariance 2025 (ext)
7. "semantic triangulation" LLM code generation problem transformations equivalence
8. consistency regularization code language model paraphrased problem statements RL reward agreement between programs (ext)
9. Co-rewarding self-supervised RL rephrased questions cross-agreement pseudo-label
10. LLM synthesizes automaton or state machine from NL specification, equivalence checking minimised DFA, fine-tuning 2025 2026 (ext)
11. aimed adversarial paraphrase maximize change in generated program, robustness training code LLM, worst-case rewrite (ext)
12. TyFlow type system language model code generation internalize typing derivations
13. language model trained to perform type checking itself well-formedness check before execution (ext)
14. minimum distance error-correcting parser nearest well-typed program repair type error search Seminal Rite
15. automated grading DFA constructions edit distance nearest correct automaton counterexample feedback
16. unsupervised semantic parsing paraphrase agreement learning signal; Fader paraphrase-driven learning
17. LLM generates FSM from NL requirements, completeness, determinism, well-formedness, repair loop (ext)
18. NL to LTL self-consistency semantic equivalence classes Büchi automata Spot voting paraphrases (ext)
19. can LLMs act as type checkers or compilers
20. autoformalization symbolic equivalence, type-check filter, self-consistency, training with equivalence (ext)
21. text-to-SQL consistency between SQL for paraphrased questions, equivalence-based self-training or reward (ext)
22. GRPO reward invariance across paraphrased prompts consistency reward (ext)
23. adversarial training semantic parsing worst-case paraphrase search; ADVETA
24. "error-correcting" code generation LLM nearest valid program projection constrained decoding
25. regex generation LLM RL DFA equivalence reward 2024–2026 GRPO (ext)
26. Synchromesh; monitor-guided decoding
27. NL to temporal logic LLM fine-tuning RL semantic equivalence reward automata (ext)
28. counterexample-guided repair LLM generated automaton shortest distinguishing string fine-tuning
29. LLM writes DFA or transition table, samples compared by automaton equivalence, consistency or self-training (ext)
30. "Nerode" language model training loss equivalence classes LLM compile programs
31. Vafa et al., Myhill–Nerode metrics; DFA equivalence as a training objective

**For P:**
32. LLM parallel scan associative composition state tracking log depth language model calls prefix sum (ext)
33. "parallel prefix" OR "associative scan" LLM reasoning steps compose transition functions logarithmic depth (ext)
34. divide and conquer LLM state tracking chunks compose partial functions 2025 2026 (ext)
35. data-parallel finite-state machines enumerative speculation Mytkowicz
36. LLM agent sequential task parallelized by composing chunk summaries as state-to-state functions, reduction tree (ext)
37. MAKER follow-up, parallel speedup, log-depth decomposition (ext)
38. LLM addition carry-lookahead parallel prefix chain-of-thought log depth (ext)
39. Multiverse; APR; Hogwild; divide-and-conquer parallel reasoning
40. DEER, ELK: parallelizing nonlinear sequential models, Newton, parallel scan
41. prompting an LLM to compose permutations pairwise in a binary tree (ext)
42. "recursive doubling" OR "pointer jumping" OR "Blelloch" LM inference executing program steps in parallel (ext)
43. Percepta log-time execution, parallel
44. LLM as a monoid combine operator, associativity, tree reduction (ext)
45. neural FSM execution log depth, composition of transition matrices (ext)
46. Lewandowski / Schuurmans universal machine with step-by-step calls
47. LM simulates an FSM on each chunk from every start state, then composes (ext)
48. speculative step-level parallel reasoning; speculative actions
49. "Length Generalization with Log-Depth Recurrent Units"
50. "Parallel Algorithms Align with Neural Execution"
51. LLM function composition by repeated squaring or binary lifting
52. Recursive Language Models
53. LLM tool-free computation parallelized across calls in logarithmic rounds (ext)
54. "scan" OR "prefix sum" LM "each step" "forward pass" parallel execution of a program trace (ext)
55. LLM composes state transformations from chunks, associative merge, entity tracking (ext)
56. Barrington S5 NC¹; Ladner–Fischer; Hillis–Steele
57. blog "associative scan" LLM agents OR "parallel prefix" "LLM calls" (ext)

---

## 5. Verified citations (all accessed 2026-10-28)

**arXiv API (export.arxiv.org): the id returned the intended title.**

| id | short reference |
|---|---|
| 2504.09246 | Mündler et al., Type-Constrained Code Generation (also DOI 10.1145/3729274) |
| 2510.10216 | Huang et al., TyFlow |
| 2511.12288 | Dai et al., Semantic Triangulation |
| 2508.00410 | Zhang et al., Co-rewarding (ICLR 2026) |
| 2510.04392 | Hamman et al., PS-GRPO |
| 2310.18239 | Yang et al., Formal Methods Feedback |
| 2603.03305 | Reddy et al., DCCD |
| 2605.30054 | Chen et al., Projectional Decoding (FSE 2026 IVR) |
| 2603.20004 | Zhu et al., ReViSQL |
| 2602.18800 | Ghosh Paul et al., Operational Robustness |
| 2406.07222 | Poiroux et al. (EMNLP 2025) |
| 2410.20936 | Li et al. (NeurIPS 2024) |
| 2201.11227 | Synchromesh |
| 2306.10763 | Monitor-guided decoding |
| 2304.05128 | Self-Debug |
| 2303.11366 | Reflexion |
| 2302.08468 | LEVER |
| 2207.10397 | CodeT |
| 2410.02089 | RLEF |
| 2603.29140 | Nguena Timo et al. |
| 2610.25402 | LoGIST |
| 2212.09994 | ADVETA |
| 2301.08881 | Dr.Spider |
| 2402.08666 | Saparina & Lapata |
| 2301.13816 | PPOCoder |
| 2207.01780 | CodeRL |
| 2402.01391 | StepCoder |
| 2409.00921 | Typed holes |
| 2403.01632 | SynCode |
| 2405.21047 | Grammar-aligned decoding |
| 2106.06600 | Break-It-Fix-It |
| 2005.10636 | DrRepair |
| 2007.04973 | ContraCode |
| 2212.10264 | ReCode |
| 2106.01065 | Spider-Syn |
| 1804.06059 | SCPN |
| 2212.09561 | Self-verification |
| 2408.15240 | GenRM |
| 2005.13485 | Cao et al., dual paraphrasing |
| 2502.07786 | Orvalho et al. |
| 1704.03976 | VAT |
| 2605.26035 | MLP-LDRU |
| 2609.28212 | Log-Depth RLM |
| 2307.04049 | Engelmayer et al. |
| 2506.16411 | D&C noise (ICLR 2026) |
| 2512.24601 | RLM |
| 2504.15466 | APR |
| 2504.06261 | Hogwild! |
| 2506.19830 | Lookahead Reasoning |
| 2502.11517 | PASTA |
| 2609.00012 | MD5 tool calls |
| 2407.19115 | ELK |
| 2309.12252 | DEER |
| 2307.15337 | Skeleton-of-Thought |
| 2602.10743 | Kalman Linear Attention |
| 2605.17108 | Parallel Recursive LSTM |
| 2506.09991 | Multiverse |
| 2403.09728 | Rizvi et al. |
| 2511.07869 | Autospeculation |
| 2506.10918 | Prefix Scannable Models |
| 2509.09677 | Illusion of Diminishing Returns |

Known items re-checked through the same API: 2511.09030 (MAKER), 2210.10749, 2503.02854, 2410.09342, 2609.32447.

**Crossref API (DOI resolved to the intended title, authors and venue):**
- 10.1145/322217.322232 (Ladner & Fischer 1980)
- 10.1145/7902.7903 (Hillis & Steele 1986)
- 10.1145/2541940.2541988 (Mytkowicz et al. 2014)
- 10.1109/TC.1973.5009159 (Kogge & Stone 1973)
- 10.1137/0201022 (Aho & Peterson 1972)
- 10.1145/1250734.1250783 (Seminal 2007)
- 10.1145/3385412.3386005 (Rite 2020)
- 10.1145/2723163 (D'Antoni et al. 2015)
- 10.1016/0022-0000(89)90037-8 (Barrington 1989)
- 10.1145/3445814.3446705 (Qiu et al. 2021)

**Venue and lab pages (HTTP 200 and title matched):**
- https://aclanthology.org/D18-1189/ (SemRegex)
- https://aclanthology.org/D19-1677/ (SoftRegex)
- https://aclanthology.org/P13-1158/ (Fader, Zettlemoyer & Etzioni, Paraphrase-Driven Learning)
- https://aclanthology.org/P18-1079/ (SEARs)
- https://www.ijcai.org/Abstract/13/292 (Alur et al. 2013)
- https://iclr.cc/virtual/2026/poster/10008259 (Co-rewarding)
- https://www.cs.cmu.edu/~guyb/papers/Ble93.pdf (Blelloch, text read)
- https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/ (title matched; "batch-invariant" present)
- https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/asplos302-mytkowicz.pdf (text read)

## 6. Unverified (do not cite without a check)

- **"On Repairing Ill-Typed Expressions"**, EPFL Infoscience record 190024. The search summary says it is a complete
  algorithm that returns the type-correct expressions closest to an ill-typed one. The record page returned HTTP 202
  with no content, so the authors, year and venue are unconfirmed (probably Kuncak's group).
- **Yang et al. 2310.18239 as MLSys 2024.** A proceedings.mlsys.org PDF with this title appeared in search results;
  I did not open it. Only the arXiv id is verified.
- **SpecFix** (arXiv 2505.07270), **LLM-FSM** (arXiv 2602.07032), **SmartFSM** (IJCAI 2025 proceedings PDF 0653),
  **RESTL** (2511.08555), **ReasonSTL** (2605.06483), **SCP-NL2TL** (2608.05439), **NeuroNL2LTL** (2605.22874) and
  **CodeThinker** (2605.17958): seen only in search results, ids not checked. None changes a verdict.
- **Moore (1956)** "Gedanken-experiments on sequential machines" and **Hopcroft & Karp (1971)** DFA equivalence: the
  classical sources for distinguishing experiments and shortest counterexamples. Not fetched.
- **Fader et al. 2013:** the page is verified, but whether its paraphrase clusters act as a *consistency* signal for
  the parser (and not only for lexicon learning) is not checked.
