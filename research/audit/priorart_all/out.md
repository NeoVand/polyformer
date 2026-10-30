I found substantial prior art for the cores of results 1, 3–6, and for several components of result 7. The strongest additional challenges are **Whitney’s extension theorem for result 1**, **Chung et al.’s drift-horizon corollary for result 2**, and **Abbe et al.’s explicit history removal and position reindexing for result 5**. I did not find your two exact drift formulas or the complete self-authoring, certifying, neural-execution system.

This is a search-based assessment through **29 October 2026**, not an exhaustive clearance. I searched the requested topic families across arXiv, indexed OpenReview submissions and proceedings, PMLR/COLT, and ACL Anthology. OpenReview and Google Scholar access limitations materially weaken coverage of the newest submissions.

Dates below mean **first arXiv submission where available**; journal receipt dates or publication dates are identified separately. They should not be confused with conference submission dates. Citations first posted after 1 July 2026 are **bold**; later versions of older papers are marked separately. **IMPLIES** denotes my mathematical inference, rather than wording explicitly used by the cited author.

**1. Blindness: the objective-level formulation has a serious classical antecedent, although I did not locate its complete tracker-specific statement.**

- Hassler Whitney. *Analytic Extensions of Differentiable Functions Defined in Closed Sets*. Transactions of the American Mathematical Society 36(1):63–89, 1934. Received **29 March 1933**, revised 2 May 1933. Theorem I, p. 65, includes the prescribed-derivative condition:
  
  > “\(D_kF(x)=f_k(x)\) in \(A\)”
  
  **Verdict: IMPLIES the finite-view mathematical core of result 1.** At finitely many distinct Euclidean points, prescribed values and first derivatives satisfy the extension compatibility conditions. Applying the theorem componentwise gives smooth maps agreeing on every observed value while having arbitrarily prescribed Jacobians there. Any objective depending exclusively on those values is consequently identical. That last sentence is my deduction, not Whitney’s terminology. The paper does not discuss training objectives or closed trackers. [Primary paper](https://www.math.ucdavis.edu/~saito/data/high-dimensions/whitney1.pdf)

- Max Simchowitz, Daniel Pfrommer, and Ali Jadbabaie. *The Pitfalls of Imitation Learning when Actions are Continuous*. COLT 2025, PMLR 291:5248–5351; arXiv:2503.09722. Submitted **12 March 2025**. Theorem 1 establishes exponentially amplified execution error under its learning and dynamics assumptions. The authors explicitly qualify the mechanism:
  
  > “our negative results necessarily leverage that the learner has uncertainty over the true dynamics”
  
  **Verdict: PARTIAL—results 1 and 2.** This is a learning lower bound involving uncertainty about dynamics and restrictions on imitator policies. It does not state the unrestricted, objective-level arbitrary-Jacobian equivalence you describe. [Theorem and discussion](https://arxiv.org/html/2503.09722v1), [COLT citation](https://proceedings.mlr.press/v291/simchowitz25a.html)

- Riku Green, Zahraa S. Abdallah, and Telmo M. Silva Filho. *Exposure Bias as Epistemic Underidentification in Recursive Forecasting*. arXiv:2606.12990. Submitted **11 June 2026**. Theorem 1:
  
  > “Then the one-step Bayes objective identifies the predictor only on \(M\), not on rollout-induced states outside \(M\).”
  
  **Verdict: PARTIAL—an explicit objective-level underidentification theorem.** Identical one-step Bayes risk can coexist with different recursive forecasts. Appendix A.2 constructs disagreement outside the observed support; A.3 discusses Jacobian amplification. It treats squared-loss Bayes prediction and off-support disagreement, not arbitrary Jacobians at the observed views or every value-only objective. This is closer to your objective-level language than Simchowitz et al. [Theorem 1 and appendices](https://arxiv.org/html/2606.12990v1)

- **Gunner Levi Howe. *The Automaton Underneath: The Additive Input Pathway Is a Parasitic Attractor for State Tracking in Householder Linear RNN*. arXiv:2609.18966. Submitted 16 July 2026, according to the arXiv record.** The paper says:
  
  > “The additive pathway is parasitic: a norm-inflation channel that cross-entropy feeds”
  
  **Verdict: PARTIAL—empirical evidence related to result 1.** Removing an additive pathway reveals better state tracking in trained recurrent models. There is no arbitrary-Jacobian indistinguishability theorem. The intervention concerns purpose-trained RNNs, not pretrained chat-model table lookup. [Paper](https://arxiv.org/html/2609.18966), [date record](https://arxiv.org/abs/2609.18966)

- **Arian Eamaz and Mojtaba Soltanalian. *Behavioral Capacity Certificates for Quantized Language Models*. arXiv:2609.37887. Submitted 29 September 2026.** In the proof surrounding Theorem 2.4:
  
  > “Layerwise transition equality on the reference reached states makes the training computations equal inductively”
  
  **Verdict: PARTIAL—reached-state equivalence, but not Jacobian blindness.** Theorem 2.4 distinguishes equal empirical-loss cells from population behavior and requires independent transfer evidence. Appendix A.4 also discusses complete reachable-state cuts, including KV-cache paths. It does not establish arbitrary off-trajectory derivatives or an all-length execution certificate. [Theorem 2.4; Appendices A.3–A.4](https://arxiv.org/html/2609.37887v1)

The important qualification is that **“arbitrary prescribed Jacobians at reached views” requires assumptions on the reached set**. It is straightforward for finitely many distinct views. It is false without qualification when values are fixed on an open set, and arbitrary prescriptions can violate compatibility on accumulating sets. Fixed neural architectures or derivative bounds can also remove the required freedom. Thus “class-free” should describe the objective’s dependence, while stating the richness and geometry assumptions on the competing trackers.

**2. Sharp drift time: I found the margin-over-drift structure, but neither exact formula.**

- Stéphane Ross and J. Andrew Bagnell. *Efficient Reductions for Imitation Learning*. AISTATS 2010, PMLR 9:661–668. Submission date not disclosed in the accessed record; published **May 2010**. Theorem 2.1:
  
  > “\(J(\hat\pi)\leq J(\pi^*)+T^2\epsilon\).”
  
  **Verdict: PARTIAL—compounding-error dependence.** The accompanying discussion states tightness in its imitation-learning setting. This is cumulative task cost under classification error, not a deterministic first margin-crossing time for a non-expansive smooth tracker. [Theorem 2.1](https://proceedings.mlr.press/v9/ross10a/ross10a.pdf)

- Jiwan Chung, Heechan Choi, and Seon Joo Kim. *Rethinking State Tracking in Recurrent Models Through Error Control Dynamics*. arXiv:2605.07755. Submitted **8 May 2026**. Corollary 1 gives:
  
  > “\(T_{\mathrm{cross}}\approx\frac{\tau M}{\|W_{\mathrm{out}}\bar{\eta}\|}\).”
  
  **Verdict: PARTIAL—a substantially closer antecedent.** Theorem 1 establishes neutrality of exact affine return maps on the state-separating subspace. Corollary 1 and Appendix D.3 derive additive residual accumulation and a separation-over-readout-drift crossing scale under coherent residual drift and approximately stable separation. The displayed relation is approximate; it does not establish your exact \(\sqrt2K\) constant or the loss-resolution expression. [Theorem 1, Corollary 1, Appendix D.3](https://arxiv.org/html/2605.07755v1)

I found no matching statement of
\[
N=\frac{m}{\sqrt2K\epsilon}
\qquad\text{or}\qquad
\frac{mL}{\log(1+\rho/\bar s)}.
\]
However, the first formula’s underlying mechanism is already present in Chung et al. A novelty claim should distinguish **sharp constants and the loss-to-horizon conversion** from the established separation/drift principle.

Also, “fails exactly beyond” must mean a sharp worst-case construction or threshold under additional assumptions. Non-expansiveness and a per-step error bound alone do not force every tracker to fail: errors can cancel or be corrected. Your brief does not define enough of \(m,K,L,\bar s\) to check constant-level equivalence.

**3. Finite reads: the oracle obstruction is classical; the smooth-derivative tracker packaging was not located.**

- Hassan Ashtiani, Vinayak Pathak, and Ruth Urner. *Black-box Certification and Learning under Adversarial Perturbations*. ICML 2020, PMLR 119:388–398; arXiv:2006.16520. Submitted **30 June 2020**. Observation 21’s proof says:
  
  > “no matter what queries the certifier chooses, we can always set \(p\) to be a point that was not queried”
  
  **Verdict: PARTIAL—finite-query robust-certification impossibility.** Observation 17 gives a non-certifiability example for halfspaces; Observation 21 supplies a particularly simple unqueried-point construction. The oracle returns classifier labels, rather than values and arbitrary derivatives of smooth closed trackers. [Observations 17 and 21](https://proceedings.mlr.press/v119/ashtiani20a/ashtiani20a.pdf)

- Edward F. Moore. *Gedanken-Experiments on Sequential Machines*. In Claude E. Shannon and John McCarthy, editors, *Automata Studies*, Annals of Mathematics Studies 34, Princeton University Press, 1956, pp. 129–153. Submission date unavailable; published **1956**. Theorem 2:
  
  > “there exist other machines experimentally distinguishable from \(S\) for which the original experiment would have had the same outcome.”
  
  **Verdict: IMPLIES the unrestricted finite-testing obstruction; PARTIAL for your smooth formulation.** Its proof constructs machines indistinguishable for the completed experiment but distinguishable later. It does not provide a smooth derivative-oracle theorem. The absence of a known machine-size bound matters; Moore also studies positive identification results under boundedness assumptions. [Theorem 2 and proof](https://www.cs.cmu.edu/~cdm/resources/Moore1956-gedanken-experiments.pdf)

My inference for your smooth setting is direct: after a finite adaptive transcript, put a smooth bump in an unqueried open subset of the positive-radius region being certified. The perturbation vanishes near every queried point, preserving **all** derivatives there. The identical answers preserve the adaptive query sequence inductively. If the tracker class permits that bump to violate the target condition, certification is impossible.

That supplies a strong classical-obviousness challenge. The remaining work is establishing that the required perturbation stays inside your particular closed-tracker class and breaks your precise robust-exactness predicate.

**4. Robust Myhill–Nerode: the invariant-cell core is already explicitly stated, including in September 2026.**

- **Julien Brandoit, Arthur Fyon, Thomas Braipson, Tom Clara, Florent De Geeter, Pierre Sacré, Damien Ernst, and Guillaume Drion. *Length-Independent State Tracking Under a Parallel Scan*. arXiv:2609.32447. Submitted 26 September 2026.** Theorem 3.2, “Cell partition,” requires:
  
  > “\(\Phi_x(U_q)\oplus\bar B_\eta\subseteq U_{\delta_x(q)}\)”
  
  **Verdict: STATES the robust invariant-cell/all-length core; PARTIAL for the full block-and-prefix formulation.** The theorem is an iff characterization with bounded Euclidean cells. Definition 2.1 quantifies over every perturbation trajectory, so history-dependent perturbations are already covered. Appendix F supplies the induction proof. Its contraction statement concerns cell-image diameter; it should not automatically be identified with a Lipschitz contraction hypothesis. [Definition 2.1, Theorems 3.1–3.3, Appendix F](https://arxiv.org/html/2609.32447v1)

- Michael O. Rabin. *Probabilistic Automata*. Information and Control 6:230–245, **1963**. Submission date not established. The paper states:
  
  > “every p.a. with isolated cut-point is equivalent to a suitable deterministic automaton.”
  
  **Verdict: PARTIAL—robust separation leading to finite-state recognition.** Theorem 3 establishes the isolated-cutpoint result. It does not state your smooth-view, contractive-block certificate. [Primary paper, Theorem 3](https://perso.ens-lyon.fr/denis.kuperberg/CR18/probas.pdf)

- Mike Casey. *The Dynamics of Discrete-Time Computation, with Application to Recurrent Neural Networks and Finite State Machine Extraction*. Neural Computation 8(6):1135–1178, **15 August 1996**. Submission date not established. The accessible abstract says the system:
  
  > “must organize its state space to mimic the states in the minimal deterministic finite state machine”
  
  **Verdict: PARTIAL, based on the abstract only.** This establishes relevant historical positioning, but I could not inspect the complete theorem statements and therefore do not use Casey to resolve your exact refinements. [Primary bibliographic record and abstract](https://pubmed.ncbi.nlm.nih.gov/8768390/)

For ordinary total Euclidean automata, grouping \(k\) events into a macro-symbol and initializing after a fixed prefix are natural reductions to invariant-set induction. Correct readout at intermediate positions still requires your within-block conditions. The **partial-automaton and pseudometric formulation** is the part I did not find stated in the inspected sources; a pseudometric quotient also requires compatible transitions and readouts.

Bugaud remains an important unresolved candidate, detailed below.

**5. Theorem P: finite local verification implying arbitrary-length execution is established; history removal and position reset are also established.**

- Jonathon Cai, Richard Shin, and Dawn Song. *Making Neural Programming Architectures Generalize via Recursion*. ICLR 2017; arXiv:1704.06611. ArXiv submission **21 April 2017**; earlier OpenReview submission date could not be checked. Section 3.3:
  
  > “we only need to test a finite number of inputs to show that the model will work correctly on inputs of unbounded complexity.”
  
  **Verdict: STATES the finite-local-verification ⇒ unbounded-correctness principle; PARTIAL for Theorem P.** They explicitly verify valid local input sequences and use recursion to make verification finite. This is a neural program interpreter, not pinned transformer KV decoding. They also report addition experiments reaching 5,000 digits. [Verification procedure](https://arxiv.org/pdf/1704.06611)

- Dale Schuurmans, Hanjun Dai, and Francesco Zanini. *Autoregressive Large Language Models are Computationally Universal*. arXiv:2410.03170. Submitted **4 October 2024**. Their reported verification checks that Gemini:
  
  > “correctly apply each of the \(2027\) production rules”
  
  **Verdict: STATES the exhaustive-rule-checking basis for exact universal neural execution; PARTIAL for results 5 and 7.** The Lag-system construction and extended decoding connect a finite rule table to universal computation. The program is supplied by the researchers; the result is not the complete self-written-program pipeline. [Construction and Section 8](https://arxiv.org/html/2410.03170v1)

- Alex Lewandowski, Marlos C. Machado, and Dale Schuurmans. *Universal computation is intrinsic to language model decoding*. arXiv:2601.08061. Submitted **12 January 2026**; inspected revision **10 February 2026**. Appendix C, Theorem 1, concludes that decoding:
  
  > “exactly simulates the execution of \(L(U_{15,2})\)”
  
  **Verdict: STATES the central sufficiency result in a very close setting.** The hypotheses require every production rule to be generated correctly from a fixed system prompt plus the encoded local symbol pair. The conclusion holds for arbitrary input strings. Appendix F proves it; Corollary 2 reports the condition for Llama-4-17B-128E-Instruct using 1,857 contexts. This is direct prior art for an LLM serving as a certified neural executor. It does not explicitly present your pinned-KV iff, margin, Mealy-block, or Lean formulation. [Theorem 1, Corollary 2, Appendix F](https://arxiv.org/html/2601.08061v2)

- Emmanuel Abbe, Samy Bengio, Aryo Lotfi, Colin Sandon, and Omid Saremi. *How Far Can Transformers Reason? The Globality Barrier and Inductive Scratchpad*. NeurIPS 2024; arXiv:2406.06467. Submitted **10 June 2024**; inspected v3, **1 November 2024**. Section 3.2.2 explicitly proposes:
  
  > “attention masking and reindex positions”
  
  and
  
  > “simply remove the previous states at each time”
  
  **Verdict: STATES the key context-management semantics; PARTIAL for Theorem P.** The model generates each next state as if given only the persistent question and current state. Appendix C.2 retains the question as permanent memory. This substantially anticipates persistent program context, history eviction, and position reset, although not your exact KV implementation or certificate theorem. [Section 3.2.2 and Appendix C.2](https://arxiv.org/html/2406.06467v3)

- Chenxiao Yang, Nathan Srebro, David McAllester, and Zhiyuan Li. *PENCIL: Long Thoughts with Short Memory*. ICML 2025; arXiv:2503.14337. Submitted **18 March 2025**. Theorem 5.1 states:
  
  > “PENCIL with this transformer computes the same output with \(O(T)\) generated tokens”
  
  **Verdict: PARTIAL—exact transformer computation with deliberate context reduction.** Theorem G.1 formalizes simulation with context \(O(S)\), and the reduction rules erase intermediate computation. This is an existence/construction result, not certification of an arbitrary pretrained model’s self-written table. [Theorem 5.1 and Appendix G](https://arxiv.org/pdf/2503.14337)

The necessity direction of your iff is immediate **if every certified row can be exposed by an allowed initial tape/local configuration**: an incorrect row then gives a one-step counterexample. If some rows are unreachable, necessity must be restricted accordingly. Thus the most defensible distinction is the precise cache semantics, reachability conditions, robustness margins, block interface, and formalization—not the bare local-to-global equivalence.

**6. No finite test suite: classical in unrestricted machines, but the strict-margin decoder construction was not found.**

Moore’s Theorem 2 above is the decisive historical antecedent. Two recent transformer results are relevant but do **not** establish exactly the same impossibility:

- Artur Back de Luca and Kimon Fountoulakis. *Certification from Examples is Hard for Circuits and Transformers under Minimal Overparametrization*. arXiv:2605.22964. Submitted **21 May 2026**. Theorem 4.2 says:
  
  > “every target computed by the original architecture is hard to certify in the enlarged one”
  
  **Verdict: PARTIAL—large certification-set lower bounds.** Its transformer construction yields exponential certification requirements on a fixed finite input domain after a small architecture enlargement. Exhaustive finite certification still exists on that domain. It does not establish absence of every finite suite, nor your simultaneous per-row and strict-margin constraints. [Theorem 4.2](https://arxiv.org/html/2605.22964v1)

- Andy Yang, Pascal Bergsträßer, Georg Zetzsche, David Chiang, and Anthony W. Lin. *Length Generalization Bounds for Transformers*. ICML 2026, PMLR 306:144227–144248; arXiv:2603.02238. The arXiv record gives first submission **13 February 2026**; inspected revision **31 May 2026**. Corollary 3.6:
  
  > “The length complexity of C-RASP is not computably bounded.”
  
  **Verdict: PARTIAL—uncomputable generalization bounds, not your exact finite-test statement.** The paper separates negative results for more expressive models from positive bounds under precision restrictions. “No computable uniform bound” must not be substituted for “no finite distinguishing suite for this target/class.” [Corollary 3.6 and surrounding results](https://arxiv.org/html/2603.02238v2), [submission record](https://arxiv.org/abs/2603.02238)

I did not locate a paper explicitly combining **retained history, passing every local row certificate, passing an arbitrary finite suite with strict margins, and later exact-arithmetic failure**. That conjunction requires a decoder-class realization argument beyond Moore’s abstract machine construction.

**7. System claim: important components are known; I found no complete match.**

The Schuurmans and Lewandowski papers already establish certified execution **by language-model decoding itself**. Cai et al. already establish finite verification and very long neural-program execution. The following candidates address the remaining components.

- Ruize Xu, Chenxiao Yang, Yanhong Li, and David McAllester. *Training Transformers as a Universal Computer*. arXiv:2604.25166, submitted **28 April 2026**. A later version is **[*Towards Training Transformers as a Universal Computer*, Findings of EMNLP 2026, pp. 48933–48954, October 2026](https://aclanthology.org/2026.findings-emnlp.2284/)**. The inspected arXiv paper reports:
  
  > “with per-program traces reaching 7,552 lines.”
  
  Its table caption specifies:
  
  > “Accuracy is the token-level success rate.”
  
  **Verdict: PARTIAL—a strong multi-thousand-step neural execution precedent.** A 59.5M transformer predicts MicroPy execution steps, with reported 100% accuracy on the tested tasks, including multiplication traces of 7,552 lines and SAT-solving traces of 5,020 lines. Evaluation uses stepwise prompt/completion pairs. I therefore do not count this as verified evidence of an uninterrupted free-running rollout. It is neither a pretrained 4B chat model nor exhaustive certification of self-authored programs. [Methods, Tables 1–2, Section 3.3](https://arxiv.org/html/2604.25166)

- Kevin Meng, David Bau, Alex Andonian, and Yonatan Belinkov. *Locating and Editing Factual Associations in GPT*. NeurIPS 2022; arXiv:2202.05262. Submitted **10 February 2022**. The paper describes:
  
  > “we modify feed-forward weights to update specific factual associations using Rank-One Model Editing (ROME).”
  
  **Verdict: PARTIAL—rank-one intervention in pretrained associative memory.** Section 3.1 derives the constrained associative-memory update. It changes particular factual associations; it does not expose a general exact prompt-table lookup primitive or certify arbitrary execution. [Section 3.1 and Appendix A](https://arxiv.org/html/2202.05262)

- Eric Todd, Millicent L. Li, Arnab Sen Sharma, Aaron Mueller, Byron C. Wallace, and David Bau. *Function Vectors in Large Language Models*. ICLR 2024; arXiv:2310.15213. Submitted **23 October 2023**. The introduction says:
  
  > “An FV does not directly perform a task, but rather it triggers the execution of a specific procedure by the language model”
  
  **Verdict: PARTIAL—eliciting latent computational behavior.** This uses activation interventions to induce tasks across contexts. It does not establish exact table lookup exposed by a rank-one weight edit, much less the ten-family result. [Methods and experiments](https://arxiv.org/html/2310.15213)

- Luke J. O’Connor. *Self-Programmed Execution for Language Model Agents*. arXiv:2605.06898. Submitted **7 May 2026**; inspected **revision 15 October 2026**. The abstract states:
  
  > “the model completion is itself the orchestrator program, and the harness evaluates this program”
  
  **Verdict: PARTIAL—self-authored programs; UNRELATED to neural execution certification.** The model writes the orchestration program, but an external Spell runtime evaluates it. This does not make the transformer’s forward passes the certified interpreter. [Architecture and execution definition](https://arxiv.org/html/2605.06898v2)

- **Hanchao Zhou and Jialei Li. *SCOPE: Certified Theorem Proving with a Language Model as the Policy Planner*. arXiv:2610.08319. Submitted 6 October 2026.** Its abstract states:
  
  > “a symbolic engine executes the numerics”
  
  **Verdict: UNRELATED to the defining neural-executor claim.** The model plans, a symbolic engine computes, and a compiler produces the proof. The word “certified” does not make this a precedent for certified computation inside the LLM. [Paper](https://arxiv.org/html/2610.08319v1)

- **Sietse Schelpe. *Smarter and Cheaper at Once: Byte-Exact KV-State Grafting Turns a Frozen Small Model into a Verified-Knowledge Flywheel*. arXiv:2607.14431v1. Submitted 15 July 2026.** The paper reports:
  
  > “the grafted logit vector is byte-for-byte identical to a fresh computation”
  
  **Verdict: UNRELATED to program correctness; related cache engineering only.** It reports restoring cached computation under a deterministic configuration. Equality to fresh logits is not equality to a program specification and does not give an all-length executor theorem. [Inspected v1](https://arxiv.org/html/2607.14431v1)

For your three specific system-search questions:

| Question | Finding |
|---|---|
| An LLM certifiably executes programs it writes itself | **No complete match found.** Program authorship and certified neural execution appear separately in the inspected literature. |
| Exact multi-thousand-step execution inside neural forward passes | **The arbitrary-length guarantee is already present** in the Lag-system papers. Xu et al. provide a close empirical precedent, but their reported evaluation is stepwise. |
| Pretrained table lookup exposed by a low-rank edit | **No exact match found.** ROME and function vectors are related mechanisms, not demonstrations of the claimed general lookup primitive. |

I found no inspected source matching the combined **4B chat model, light fine-tuning, self-written table, exhaustive row certification, pinned-cache execution, million-digit addition, 30,000 Lag steps, browser deployment, and rank-one exposure across ten model families**.

The following limits remain material:

- **Bugaud:** Zacharie Bugaud, *Which Regular Languages Admit Provably Correct RNN Implementations? A Lattice-Theoretic Characterisation via Forward-Invariant Sets*, associated with the **11 July 2026 ICML AI for Math workshop**. The [OpenReview record](https://openreview.net/forum?id=L4kh17ZuSa) and [linked PDF](https://openreview.net/pdf/1d89b741e0f9e5f8879d942fa64bd77eb423b0d7.pdf) were inaccessible. I could not verify the submission date, quote a theorem, or establish whether this is exactly your “Bugaud 2026a.” I do not assign a substantive verdict from an autogenerated secondary summary.
- **Casey 1996:** bibliographic record and abstract accessible; full theorem text not accessed.
- **OpenReview:** browser-verification barriers affected individual papers; the ICLR 2027 venue page did not expose a usable submission inventory. Coverage of ICLR 2027, NeurIPS 2026, and ICML workshops therefore relied partly on indexed records and accessible arXiv versions.
- **Google Scholar:** direct search was inaccessible.
- **Xu et al.’s October ACL version:** the primary metadata and abstract were accessible, but the proceedings PDF was not. The detailed numerical assessment above uses the arXiv text.
- **Whitney:** the theorem was available through indexed extraction of the primary PDF; the direct PDF text renderer did not expose the document normally.
- I did not enumerate every submission in the six requested arXiv categories. Negative findings reflect topic-, phrase-, citation-, and venue-targeted searching.
- Your Lean files and full theorem hypotheses were not supplied for comparison. Formalization can be a contribution even where the underlying mathematical implication is known.

| Result | Overall verdict | Decisive citation(s) | What remains unmatched |
|---|---|---|---|
| **1. Blindness** | **PARTIALLY KNOWN** | [Whitney 1934](https://www.math.ucdavis.edu/~saito/data/high-dimensions/whitney1.pdf); [Green et al. 2026](https://arxiv.org/html/2606.12990v1) | Exact closed-tracker/objective formulation. The finite-view arbitrary-Jacobian core follows from classical extension theory. |
| **2. Sharp drift time** | **PARTIALLY KNOWN** | [Chung et al. 2026, Cor. 1](https://arxiv.org/html/2605.07755v1) | Both exact formulas, sharp constants, and loss-resolution conversion are **NEW as far as searched**. |
| **3. Finite reads** | **PARTIALLY KNOWN** | [Ashtiani et al. 2020](https://proceedings.mlr.press/v119/ashtiani20a/ashtiani20a.pdf); [Moore 1956](https://www.cs.cmu.edu/~cdm/resources/Moore1956-gedanken-experiments.pdf) | Exact smooth closed-tracker predicate and adaptive derivative-oracle statement; classical bump constructions strongly anticipate it. |
| **4. Robust Myhill–Nerode** | **PARTIALLY KNOWN** | **[Brandoit et al., 26 September 2026, Thm. 3.2](https://arxiv.org/html/2609.32447v1)** | Full partial-automaton/pseudometric/block-prefix package. Robust invariant-cell induction and history-dependent perturbations are already covered. |
| **5. Pinned-cache Theorem P** | **PARTIALLY KNOWN** | [Lewandowski et al. 2026, Thm. 1](https://arxiv.org/html/2601.08061v2); [Abbe et al. 2024](https://arxiv.org/html/2406.06467v3) | Exact KV-policy iff, reachability qualifications, margins, Mealy blocks, Lean proof. Core sufficiency and reset semantics are known. |
| **6. No finite history-retaining test suite** | **PARTIALLY KNOWN** | [Moore 1956, Thm. 2](https://www.cs.cmu.edu/~cdm/resources/Moore1956-gedanken-experiments.pdf) | Explicit decoder realization preserving row certificates and strict margins while failing later. |
| **7. Complete system** | **PARTIALLY KNOWN** | [Lewandowski et al. 2026](https://arxiv.org/html/2601.08061v2); [Xu et al. 2026](https://arxiv.org/html/2604.25166); [Meng et al. 2022](https://arxiv.org/html/2202.05262) | The complete pipeline and specific scale/browser demonstrations, plus general latent lookup exposed by rank one across ten families, are **NEW as far as searched**. |