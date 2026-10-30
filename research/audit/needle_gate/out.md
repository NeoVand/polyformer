**I would narrow C1, C2, and C7; kill C3–C6 and C8 as currently stated. C7 has the strongest surviving research question.** Several proposed theorems are standard consequences of finite-state simulation, concentration, perturbation theory, or associative reduction. Two claims also have substantive correctness problems: C5’s unrestricted “iff” and C6’s finite bicyclic-monoid certificate.

I searched live sources through **29 October 2026**, emphasizing 2025–2026, using arXiv, OpenReview, ACL Anthology, PMLR, and original papers. Google Scholar was not reliably accessible. Recent arXiv results below are preprints unless a venue is specified. This is an adversarial novelty screen, not an exhaustive priority determination.

In the tables, **STATES** means the cited work explicitly states the identified component; **IMPLIES** means a short deduction gives it; **PARTIAL** means material overlap with an important missing ingredient. None of these labels alone means a paper contains your entire proposal.

One shared qualification: an “iff” certificate needs **exact transition-trace correctness**, a complete description of the executor’s effective state, and correct initialization and termination. Positive logit margin is sufficient, but not necessary for deterministic exactness when ties are resolved correctly. Robustness to arbitrary logit perturbations bounded by \(\eta\) requires a gap exceeding \(2\eta\).

---

**C1. Certified pushdown execution via a KV stack policy**

**Prior art**

| Paper and date | Short decisive quotation | Assessment |
|---|---|---|
| Cai, Shin & Song, [*Making Neural Programming Architectures Generalize via Recursion*](https://people.eecs.berkeley.edu/~dawnsong/papers/iclr_2017_recursion.pdf), ICLR 2017 | “we only need to test a finite number of inputs” | **STATES** the central bounded-view recursive-verification principle. Does not implement your pretrained KV-stack policy. |
| Yang et al., [*PENCIL*](https://proceedings.mlr.press/v267/yang25ac.html), ICML, July 2025 | “recursively clean up intermediate thoughts based on patterns learned from training.” | **PARTIAL**: recursive context cleanup and general computation; not this finite certificate for an existing chat model. |
| Murty et al., [*Pushdown Layers*](https://aclanthology.org/2023.emnlp-main.195/), December 2023; preprint October 2023 | “models recursive state via a stack tape” | **PARTIAL**: explicit recursive state in transformers, but a different architecture and no matching certificate. |
| DuSell & Chiang, [*Stack Attention*](https://arxiv.org/abs/2310.01749), October 2023; ICLR 2024 | “allows transformers to recognize arbitrary CFLs.” | **PARTIAL**: stack-augmented transformer expressivity already covers context-free recognition. |
| Zhang et al., [*StackTrans: From Large Language Model to Large Pushdown Automata Model*](https://arxiv.org/abs/2507.15343), 21 July 2025 | “StackTrans explicitly incorporates hidden state stacks between Transformer layers.” | **PARTIAL**, and a particularly close architectural comparator. Hidden-state stacks in pretrained LMs are already proposed. |
| Grefenstette et al., [*Learning to Transduce with Unbounded Memory*](https://arxiv.org/abs/1506.02516), 8 June 2015; NeurIPS 2015 | “continuously differentiable analogues of traditional data structures such as Stacks, Queues, and DeQues.” | **PARTIAL**: neural control of unbounded external stacks is established. |
| Joulin & Mikolov, [*Inferring Algorithmic Patterns with Stack-Augmented Recurrent Nets*](https://arxiv.org/abs/1503.01007), 3 March 2015; NeurIPS 2015 | “a recurrent network associated with a trainable memory.” | **PARTIAL**: learned stack computation, without your verification scheme. |
| Schroeder et al., [*THREAD*](https://aclanthology.org/2025.naacl-long.427/), preprint May 2024; NAACL April 2025 | “child threads, which only return tokens needed for the parent thread to do its work.” | **PARTIAL**: bounded parent/child interfaces and recursive LLM execution; no all-input certificate. |
| Zhang, Kraska & Khattab, [*Recursive Language Models*](https://arxiv.org/abs/2512.24601), 31 December 2025 | “recursively call itself over snippets of the prompt.” | **PARTIAL**: recursive orchestration, not certified pushdown execution. |
| Alur & Madhusudan, [*Visibly Pushdown Languages*](https://www.cis.upenn.edu/~alur/Stoc04.pdf), STOC 2004 | “the input symbol determines when the pushdown automaton can push or pop” | **IMPLIES** the appropriate classical transition system and stack invariant. |

**Hostile referee assessment.** The abstract theorem is a standard **pushdown simulation invariant**, with Cai et al. already supplying the neural-program bounded-view verification argument. Once every concrete step implements the corresponding abstract transition, induction gives every finite execution length and depth.

The substantial issue is whether your concrete executor actually has finitely many views.

**Keeping only the top frame visible does not establish that its KV is determined by \((q,\gamma,a)\).** Its cached vectors may encode ancestors or previous operations from when that frame was created. Restarting positions does not erase information already embedded in those vectors. Consequently, checking one representative per symbolic row need not cover all realizable caches.

You need either:

- Canonical, history-independent frame construction, such as recomputation or certified templates; or
- A proof that every realizable KV frame belongs to an equivalence class on which the transition is uniformly correct.

The certificate must also cover bottom-of-stack behavior, malformed inputs, halting, and return-value transfer. Restoring the parent’s old state without incorporating the child’s result is not recursive evaluation.

The advertised check count assumes a **finite stack alphabet and atomic transition outputs**. Unrestricted integer arithmetic does not automatically fit a finite frame alphabet: specify bounded arithmetic or a digit-level algorithm with separately certified operations. Multi-token transition outputs likewise require more than one next-token check per row.

**What would make it a contribution?** A pretrained 4B executor whose *actual cache implementation* has a proved canonical-frame invariant, passes complete local certification, and supports recursive tasks with measured memory and latency advantages over fresh calls and existing stack architectures. Depth 500 is a useful demonstration; the invariant supplies the unbounded-depth argument.

**Verdict: NARROW.** Surviving claim: **a practical, certified canonical-KV implementation of a visibly pushdown interpreter on a pretrained LLM**. Do not sell finite recursive verification itself as new.

---

**C2. A predictive horizon law: collisions, not decay**

**Prior art**

| Paper and date | Short decisive quotation | Assessment |
|---|---|---|
| Jelassi et al., [*Repeat After Me: Transformers are Better than State Space Models at Copying*](https://arxiv.org/html/2402.01032v2), 1 February 2024; ICML 2024 | “the error of the algorithm depends on the probability of repeated n-grams” | **STATES** the collision mechanism. Its \(L^2D^{-n}\) bound already **IMPLIES** birthday-scale dependence. |
| Guo et al., [*Copying Under Repetition: From Prefix Matching to Position Hashing*](https://arxiv.org/abs/2610.26722), 19 October 2026; revised 21 October | “matching local content no longer reliably identifies where copying should continue or when it should stop.” | **STATES** content-address ambiguity under repetition. A very close, recent priority obstacle. |
| Giorlandino & Goldt, [*Two failure modes of deep transformers and how to avoid them*](https://arxiv.org/abs/2505.24333), 30 May 2025; revised February 2026, ICLR 2026 | “a formal parallel with the Random Energy Model from statistical physics.” | **STATES** the attention–REM connection; **PARTIAL** for a trained-model failure horizon. |
| Barbero et al., [*Transformers need glasses! Information over-squashing in language tasks*](https://arxiv.org/abs/2406.04267), 6 June 2024 | “certain distinct sequences of inputs to the Transformer can yield arbitrarily close representations in the final token.” | **PARTIAL**: another established mechanism for loss of distinguishability. |
| Xiang, [*A Conditional No-Hair Theorem for Transformers*](https://arxiv.org/abs/2610.24133), 16 October 2026 | “the prompt’s direct influence is diluted as the context grows” | **PARTIAL**: a conditional dilution theorem, not a universal prediction of rollout error. |
| Chowdhury, [*Lost in the Middle at Birth*](https://arxiv.org/abs/2603.10123), 10 March 2026 | “the U-shape is already present at initialization, before any training or positional encoding takes effect.” | **PARTIAL**: positional bias under its analyzed model, not your collision hazard. |
| Hong, Troynikov & Huber, [*Context Rot*](https://www.trychroma.com/research/context-rot), 14 July 2025, technical report | “their performance grows increasingly unreliable as input length grows.” | **PARTIAL**: empirical context degradation, without this predictive law. |
| Modarressi et al., [*NoLiMa*](https://proceedings.mlr.press/v267/modarressi25a.html), February 2025; ICML July 2025 | “questions and needles have minimal lexical overlap” | **PARTIAL**: exposes the limits of literal matching as an explanation of retrieval performance. |

**Hostile referee assessment: address form.** The product formula is exact only after assuming the conditional error hazard is precisely
\[
\Pr(\text{failure at }t\mid\text{survival},\text{input})=qC_t,
\]
where \(C_t\) is your conflict indicator. That is a model assumption, not a consequence of content-addressed attention.

Under an approximately independent, uniform-address model with alphabet size \(a\), a matching suffix has a *different continuation* with probability approximately \(1-1/a\). The rare-collision approximation therefore gives
\[
\Pr(\text{survive to }T)
\approx
\exp\!\left[
-\frac{q(1-1/a)T(T-1)}{2a^k}
\right],
\]
and hence
\[
T_{50}\approx
a^{k/2}
\sqrt{\frac{2\log2}{q(1-1/a)}}.
\]

Your expression omits the conflicting-continuation factor unless it is absorbed into a redefined \(q\). Overlapping suffixes, nonuniform inputs, and repeated collision clusters require additional analysis. The classical tools are the **birthday problem and Poisson/Chen–Stein approximation**. Jelassi et al. already establish the important scaling ingredient.

**Hostile referee assessment: key form.** Your lognormal variant follows immediately from the **Gaussian moment-generating function and a concentration assumption**. If background scores satisfy \(S_i\sim N(\mu,\sigma^2)\) and the target score is \(\mu+\Delta\), then
\[
\sum_{i=1}^{t}e^{S_i}\approx t e^{\mu+\sigma^2/2},
\qquad
\alpha_*\approx
\frac{1}{1+t e^{\sigma^2/2-\Delta}}.
\]
Thus \(t_0=e^{\Delta-\sigma^2/2}\) is an approximate **half-attention point**, not automatically an accuracy horizon.

Three distinctions matter:

1. Attention log-odds decline by \(\log2\) per doubling—one bit—not necessarily one unit of an output logit.
2. The target-to-one-competitor attention ratio is \(e^{s_*-s_j}\), independent of the common softmax denominator.
3. Output correctness depends on values, residual pathways, normalization, and subsequent layers. Attention dilution need not change the argmax in exact arithmetic.

If you subtract a background “bath,” its natural mean is
\[
\frac{\mathbb E[e^S V]}{\mathbb E[e^S]},
\]
not generally the unweighted mean value.

Collisions are neither universally necessary nor sufficient for failure: identical keys with identical useful values can be harmless; diffuse incorrect value mass can hurt without a near-duplicate. Positional information can also resolve repeated content, as Guo et al. demonstrate.

**What would make it a contribution?** Independently estimate effective address length, conflict sensitivity, or score/value statistics on short contexts, then predict held-out first-error distributions across lengths and tasks. Crucially, intervene separately on collision count and context length. A fitted birthday curve after observing failures is weak evidence.

**Verdict: NARROW.** Surviving claim: **a quantitatively predictive, causally validated collision-hazard model for a specified class of trained executors**. Kill “collisions, not decay” as a universal explanation, and do not present the birthday or lognormal calculations as new theorems.

---

**C3. A symmetrised restoring organ**

**Prior art**

| Paper and date | Short decisive quotation | Assessment |
|---|---|---|
| Meyerson et al., [*Solving a Million-Step LLM Task with Zero Errors*—MAKER](https://arxiv.org/abs/2511.09030), 12 November 2025 | “error correction to be applied at each step through an efficient multi-agent voting scheme.” | **STATES** bounded-step LLM voting for long reliable execution. |
| Levine & Feizi, [*Deep Partition Aggregation*](https://arxiv.org/html/2006.14768), June 2020; ICLR 2021 | “return the plurality classification” | **IMPLIES** the relevant half-vote-gap robustness certificate; its theorem explicitly uses the winner–competitor count gap. |
| Cohen, Rosenfeld & Kolter, [*Certified Adversarial Robustness via Randomized Smoothing*](https://proceedings.mlr.press/v97/cohen19c.html), ICML June 2019 | “a new classifier that is certifiably robust to adversarial perturbations under the L2 norm.” | **PARTIAL**: certification through randomized aggregation, with a different perturbation model. |
| Ye, Gong & Liu, [*SAFER*](https://aclanthology.org/2020.acl-main.317/), ACL July 2020 | “constructs a stochastic ensemble by applying random word substitutions on the input sentences” | **PARTIAL**: randomized input transformations and certified text classification. |
| Wang et al., [*Self-Consistency Improves Chain of Thought Reasoning in Language Models*](https://arxiv.org/abs/2203.11171), March 2022; ICLR 2023 | “find the most consistent answer in the final answer set.” | **PARTIAL**: answer aggregation, without your finite executor certificate. |
| Li & Li, [*From Discovery to Decision: Finite-Budget Recoverability in LLM Voting*](https://arxiv.org/abs/2610.01014), 1 October 2026 | “input permutation improves raw-plurality accuracy by 21.1 points with essentially unchanged single-call correctness.” | **PARTIAL**, directly relevant to encoding diversity. Its locking certificate certifies a voting outcome, not its correctness. |

**Hostile referee assessment.** Both mathematical claims are immediate.

A vote substitution can decrease the correct-versus-competitor gap by at most two. Therefore a gap of at least \(2m+1\) withstands \(m\) arbitrary corrupted votes. Combining this with your existing local-to-global theorem adds no new verification principle.

For competitor \(j\), let
\[
X_i=\mathbf1\{\text{copy }i\text{ votes correctly}\}
-\mathbf1\{\text{copy }i\text{ votes }j\}.
\]
Then \(X_i\in[-1,1]\). With independent encoding draws and
\[
\mu_c=p_c(\text{correct})-\max_{j\ne\text{correct}}p_c(j)>0,
\]
**Hoeffding’s inequality plus a union bound** gives exactly
\[
\Pr(\text{class }c\text{ fails})
\le (|S|-1)e^{-k\mu_c^2/2}.
\]

For \(N\) certified classes, the simultaneous bound is
\[
N(|S|-1)e^{-k\mu_{\min}^2/2}.
\]
Pointwise positive bias over an unbounded family does not provide a uniform finite pool.

Shared model weights do **not** invalidate this calculation when the encodings themselves are sampled independently for a fixed class. The real missing premise is positive bias: systematic semantic errors may survive every renaming.

The historical framing is already **von Neumann’s restoring organs**, **N-version programming**, and certified ensemble voting. Dependence among software failures is a longstanding issue; Knight and Leveson explicitly warn that reliability analysis must include dependent errors. [Knight & Leveson, January 1986](https://people.cs.rutgers.edu/~uli/cs673/papers/EvaluationMultiVersionProgramming86.pdf).

Two implementation qualifications matter:

- Every copy must consume the same voted state. Independently evolving copies require a certificate over their joint state.
- Load-time certification validates the measured execution configuration. It does not automatically cover later nondeterminism, changed batching, kernels, or common-mode faults.

**What would make it a contribution?** Evidence that semantics-preserving re-encoding creates a uniformly positive bias on difficult executor classes, together with a practical method that constructs a small certified pool. This would be an ensemble-design and deployment contribution; the stated threshold theorem is elementary.

**Verdict: KILL** as a theorem-led hypothesis. Keep the technique as a component of C1 or C8’s implementation.

---

**C4. Pinned stochastic execution with a time-uniform bound**

**Prior art**

| Paper and date | Short decisive quotation | Assessment |
|---|---|---|
| Mitrophanov, [*Sensitivity and convergence of uniformly ergodic Markov chains*](https://doi.org/10.1239/jap/1134587812), December 2005 | “perturbation bounds which relate the sensitivity of the chain under perturbation to its rate of convergence to stationarity.” | **STATES** the proposed mathematical result; see Corollary 3.1. |
| Zekri et al., [*Large Language Models as Markov Chains*](https://arxiv.org/abs/2410.02724), 3 October 2024; revised February 2025 | “equivalence between autoregressive transformer-based language models and Markov chains defined on a finite state space.” | **STATES** the finite-chain representation in a broader LM setting. Pinning makes the representation smaller. |

**Hostile referee assessment.** This is a direct application of **uniformly ergodic Markov-chain perturbation theory**.

A clean formulation uses the Dobrushin coefficient
\[
\delta(P^j)=\sup_{x,y}\operatorname{TV}(P^j(x,\cdot),P^j(y,\cdot)).
\]
For equal initial distributions and rowwise kernel error at most \(\varepsilon\),
\[
\sup_t\operatorname{TV}(\nu Q^t,\nu P^t)
\le \varepsilon\sum_{j\ge0}\delta(P^j).
\]
If \(\delta(P^j)\le C\rho^j\), splitting the sum yields your expression.

Be careful with normalization: if your assumption instead means
\[
\sup_x\operatorname{TV}(P^j(x,\cdot),\pi)\le C\rho^j,
\]
the immediate pairwise bound has \(2C\). Mitrophanov’s norm convention must be translated consistently.

The claimed kernel construction also needs restrictions:

- Arbitrary external events produce a controlled or time-inhomogeneous process, not necessarily one homogeneous chain.
- One forward pass provides a next-token distribution. A multi-token parsed transition generally needs additional computation.
- Parsing failures and other possible outputs must belong to the state model.

Most importantly, this bounds **time-marginal distributions**, not the probability that an entire sampled execution remains exact. The latter can deteriorate with length even when every marginal stays close.

The proposed converse is false without qualifications. A history-keeping decoder with a fixed finite context window has finitely many token contexts; a decoder may also simply ignore history. For an unrestricted, unbounded-context black box, finite observations cannot constrain behavior on every unobserved context—but that is an elementary **indistinguishability/no-free-lunch argument**, not a distinctive converse to pinning.

**What would make it a contribution?** New, useful bounds for controlled executors, computable tight mixing constants, or a rigorously specified separation between certificate classes. Merely substituting an LLM-derived kernel into Mitrophanov is insufficient.

**Verdict: KILL.**

---

**C5. Faults heal iff the program has a synchronising word**

**Prior art**

| Paper and date | Short decisive quotation | Assessment |
|---|---|---|
| Dauber, [*An analysis of errors in finite automata*](https://www.sciencedirect.com/science/article/pii/S0019995865902238), June 1965 | “An error is defined as a pair of states” | **STATES** the classical pair-state framework for analyzing error correction. |
| Gusev, [*Synchronizing automata with random inputs*](https://arxiv.org/abs/1404.6731), 27 April 2014 | “the expected number of steps until synchronization is exponential in the number of states.” | **STATES** analysis of synchronization time under random driving inputs. |
| Alves et al., [*Secure Recovery Procedure for Manufacturing Systems Using Synchronizing Automata and Supervisory Control Theory*](https://ieeexplore.ieee.org/abstract/document/9291471/), online December 2020; journal 2022 | “brings the system and supervisor back to a known state.” | **STATES** synchronization as recovery from state uncertainty. |
| Maass & Orponen, [*On the effect of analog noise in discrete-time analog computations*](https://igi-web.tugraz.at/people/Abstracts/MaassOrponen%3A97j/), 1998 | “reduces the power of analog computational models to that of finite automata” | **PARTIAL**: noisy computation, but not your synchronization equivalence. |
| Maass & Sontag, [*Analog Neural Nets with Gaussian or Other Common Noise Distributions Cannot Recognize Arbitrary Regular Languages*](https://www.sontaglab.org/FTPDIR/maass_sontag_analog_neural_networks_gaussian_neural_computation1999.pdf), 1999 | “Rabin referred to these languages as definite languages.” | **PARTIAL**: the stronger “noise implies definite” connection depends on the specified noise assumptions. |

**Hostile referee assessment.** A constant map in the transition monoid is precisely the existence of a reset word. The proposed consequence is governed by **synchronizing automata, coupling, and renewal/recovery-time arguments**. As stated, the iff is false.

**A synchronizing word need not occur.** Take two states, an identity symbol \(a\), and a reset symbol \(b\). Feed only \(a^\infty\). If faults flip the state independently with probability \(p\), starting from the correct state,
\[
\Pr(\text{wrong at }T)=\frac{1-(1-2p)^T}{2}\longrightarrow\frac12.
\]
The automaton has a synchronizing word, but the actual input never uses it. A synchronization waiting time under that input is infinite.

**Global synchronization is not necessary for recovery from the actual faults.** Let \(a\) send \(0,1\mapsto0\) and \(2\mapsto2\). There is no constant transformation on all three states. Nevertheless, starting at \(0\), faults restricted to \(0\to1\) heal on the next fault-free \(a\). The resulting error is \(O(p)\).

Further, “bounded away from zero” must specify the limit. For fixed \(p>0\), synchronizing systems can also have positive stationary error. The meaningful distinction is often behavior **as \(p\to0\)**.

A defensible repaired statement assumes a specified input process, a specified fault kernel, and finite expected coupling time from every fault-reachable pair. Under suitable conditions, a union-bound or renewal argument gives a bound of order
\[
p\,\mathbb E[\tau_{\mathrm{recovery}}].
\]
Existence of a limit requires additional stationarity/ergodicity assumptions; a limsup bound is a different claim.

The direct computational object is the **pair automaton**. If \(R\) is its transient off-diagonal transition matrix, expected recovery times satisfy
\[
h=(I-R)^{-1}\mathbf1.
\]
This can be more informative than a worst-case global synchronizing word.

**What would make it a contribution?** A new quantitative result for a carefully specified fault/input class, or a useful learned-executor recovery predictor that substantially improves existing pair-automaton analysis. The current reset-word criterion does neither.

Also, do not attribute the unrestricted “noise implies definite” slogan jointly to Casey and Maass–Orponen: the noise model matters, and Maass–Sontag is the closer cited result.

**Verdict: KILL.**

---

**C6. Tree-parallel certified execution via the bicyclic monoid**

**Prior art**

| Paper and date | Short decisive quotation | Assessment |
|---|---|---|
| Blelloch, [*Prefix Sums and Their Applications*](https://www.cs.cmu.edu/~scandal/papers/CMU-CS-90-190.html), November 1990 | “a computation that seems inherently sequential, but for which there is an efficient parallel algorithm.” | **IMPLIES** logarithmic-depth associative reduction and scan. |
| Mytkowicz, Musuvathi & Schulte, [*Data-Parallel Finite-State Machines*](https://www.microsoft.com/en-us/research/publication/data-parallel-finite-state-machines/), ASPLOS March 2014 | “enumerating transitions from all possible states on each input symbol.” | **PARTIAL**: established parallelization of finite-state execution through transition summaries. |
| Levien, [*Fast GPU bounding boxes on tree-structured scenes*](https://arxiv.org/pdf/2205.11659), 23 May 2022 | “The theoretical derivation of the algorithm relies heavily on the bicyclic semigroup, actually a monoid” | **STATES** the bicyclic-monoid connection to parallel tree/parenthesis processing. |
| Barrington, [*Bounded-width polynomial-size branching programs recognize exactly those languages in NC1*](https://people.cs.umass.edu/~barring/publications/bwbp.pdf), February 1989 | “can be recognized by a width-5 polynomial-size branching program.” | **PARTIAL**: classical algebraic Boolean computation, but not your direct bicyclic evaluation claim. |

**Hostile referee assessment.** For a **finite** monoid \(M\), checking its multiplication implementation on all \(|M|^2\) pairs certifies every reduction tree by induction. A balanced tree gives \(\lceil\log_2T\rceil\) rounds and \(O(T)\) multiplication work. This is a direct **associative reduction/scan** consequence.

But **the bicyclic monoid is infinite**. Its parenthesis summaries contain unbounded unmatched-close and unmatched-open counts. Thus \(|M|^2\) is not a finite certificate for unbounded Dyck execution.

This is structural: a language recognized by a homomorphism into a fixed finite monoid is regular. Unbounded Dyck-1 is not regular, by **Myhill–Nerode**.

There are further scope problems:

- For Dyck-\(k\), counts alone do not retain bracket types. They cannot distinguish valid nesting from strings such as `([)]`.
- Boolean evaluation needs summaries of operators and values, or a tree-contraction algorithm. Balancing parentheses with the bicyclic monoid does not itself evaluate the expression.
- A block-diagonal mask specifies independent pair computation; the reduction schedule, padding, summaries, and intermediate representations still need verification.

A bounded-depth restriction can yield a finite automaton and finite transition monoid. Alternatively, one can verify an arithmetic implementation of the infinite monoid. Either repair changes the claimed certificate.

**What would make it a contribution?** A new compact symbolic certificate for unbounded summaries, or an efficient certified implementation with a demonstrated systems advantage. A finite multiplication-table certificate plus a parallel scan is not enough.

**Verdict: KILL** as stated: classical parallelism combined with an invalid finite-cardinality premise.

---

**C7. Semantically neutral words that restore continuous state**

**Prior art**

| Paper and date | Short decisive quotation | Assessment |
|---|---|---|
| Omlin & Giles, [*Constructing Deterministic Finite-State Automata in Recurrent Neural Networks*](https://clgiles.ist.psu.edu/papers/JACM-1996-stable-encoding-rnn-automata.pdf), JACM November 1996 | “the constructed network correctly classifies strings of arbitrary length.” | **STATES** stable recurrent realizations of finite automata. **PARTIAL** for learning a restoring identity word in a pretrained model. |
| Casey, [*The dynamics of discrete-time computation, with application to recurrent neural networks and finite state machine extraction*](https://pubmed.ncbi.nlm.nih.gov/8768390/), August 1996 | “a precise description of the attractor structure of such systems is given.” | **PARTIAL**: established dynamical-systems treatment of recurrent finite-state computation. |
| Goyal et al., [*Think before you speak: Training Language Models With Pause Tokens*](https://arxiv.org/abs/2310.02226), 3 October 2023; ICLR 2024 | “allowing the model to process extra computation before committing to an answer.” | **PARTIAL**: neutral extra computation, without a semantic identity or contraction certificate. |
| Brandoit et al., [*Length-Independent State Tracking Under a Parallel Scan*](https://arxiv.org/abs/2609.32447), 26 September 2026 | “contraction to suppress numerical perturbations and separation to keep distinct states apart.” | **STATES** the central stability principle. A major obstacle to claiming novelty for restoration alone. |
| Wang et al., [*PAR: Progress-Aligned Recurrence for Length Generalization in State Tracking*](https://arxiv.org/abs/2610.27628), 20 October 2026 | “rescales recurrent states to their first-iteration norms.” | **PARTIAL**, and very close empirically: small Qwen, \(S_5\) state tracking, and explicit stabilization of recurrent state. |

**Hostile referee assessment.** The identity
\[
(s_i s_{i+1})^3=e
\]
is a standard **Coxeter relation**. Stability once a restoring map contracts is a standard **contraction/Lyapunov argument**. Neither is new.

The potentially new part is quite specific: **a learned semantic identity word induces useful off-manifold dissipation in the same continuous executor, without exposing intermediate symbolic states**.

That distinction is mathematically necessary. If the continuous maps constitute an exact group action throughout a neighborhood, then the identity word is the identity map there, with derivative \(I\); it cannot strictly contract. Your group semantics must hold on state centers or decoded equivalence classes while permitting dissipative behavior away from them.

Likewise, “ordinary generators expand slightly” needs a definition. If every generator expands every direction throughout the relevant regions, their composition cannot contract. Expansion of an operator norm, or average observed perturbations, does not imply that stronger condition.

A credible certificate needs neighborhoods, not just measurements at 120 centers. For every \(g\in S_5\), certify a basin around \(z_g\) with the correct readout and a restoring bound such as
\[
\|F_w(h)-z_g\|\le r\|h-z_g\|+\eta_w,
\qquad r<1.
\]
If ordinary operations are \(L\)-Lipschitz with per-step error \(\eta\), then after \(b\) useful operations followed by restoration,
\[
e_{\mathrm{next}}
\le
rL^b e+
r\eta\sum_{j=0}^{b-1}L^j+\eta_w.
\]
You need \(rL^b<1\), a steady-state radius inside the certified basins, and bounds on intermediate excursions. Jacobians only at the centers do not establish this.

The carrier must include all effective recurrent state. Hidden KV history, changing positions, or additional latent tokens cannot be omitted from the proof.

**What would make it a contribution?**

- The same learned identity word restores all 120 semantic states.
- A rigorous neighborhood certificate covers perturbations and numeric error.
- Rank-4 adaptation actually learns the mechanism without a hidden symbolic projection.
- It beats matched-compute pause/filler controls, simpler identity words such as \(s_i^2\), norm anchoring, and explicit attractor/projection baselines.

Brandoit already makes contraction-plus-separation central; PAR already stabilizes small-Qwen \(S_5\) computation and reports 95.5% full-state accuracy at 512 moves after training on at most 32. Your contribution must be the **certified semantic-word mechanism**, not merely better long-run stability. [Brandoit et al.](https://arxiv.org/abs/2609.32447), [Wang et al.](https://arxiv.org/abs/2610.27628).

**Verdict: NARROW.** This is the strongest survivor. I did not find the exact learned, uniformly certified identity-word construction. Its discovery and certification could be nontrivial; its stability corollary is classical.

---

**C8. One enumeration certifies the model for all programs**

**Prior art**

| Paper and date | Short decisive quotation | Assessment |
|---|---|---|
| Cai, Shin & Song, [*Making Neural Programming Architectures Generalize via Recursion*](https://people.eecs.berkeley.edu/~dawnsong/papers/iclr_2017_recursion.pdf), ICLR 2017 | “This verification phase only needs to be performed once after training.” | **STATES** once-after-training finite verification under bounded recursive views; narrower than arbitrary program-table coverage. |
| Giannou et al., [*Looped Transformers as Programmable Computers*](https://proceedings.mlr.press/v202/giannou23a.html), January 2023; ICML July 2023 | “a single frozen transformer, instructed by its input” | **PARTIAL**: a universal frozen interpreter with constructed weights. |
| Lewandowski, Machado & Schuurmans, [*Universal computation is intrinsic to language model decoding*](https://arxiv.org/abs/2601.08061), 12 January 2026 | “correctly execute each of the universal Lag system’s 1857 production rules” | **IMPLIES** once-for-all verification for programs represented through the fixed universal machine. Very close to the all-program quantifier. |
| Xu et al., [*Training Transformers as a Universal Computer*](https://arxiv.org/abs/2604.25166), 28 April 2026 | “generalizes to held-out human-written programs” | **PARTIAL**: trained interpreter generalization; not an exhaustive universal certificate. |
| Jacoby, Barrett & Katz, [*Verifying Recurrent Neural Networks using Invariant Inference*](https://arxiv.org/abs/2004.02462), April 2020; ATVA 2020 | “reduce the complex problem of verifying recurrent networks into simpler, non-recurrent problems.” | **PARTIAL**: compositional/invariant verification already converts unbounded recurrent behavior into local obligations. |
| Katz et al., [*Reluplex*](https://arxiv.org/abs/1702.01135), February 2017; CAV 2017 | “verifying properties of deep neural networks (or providing counter-examples).” | **PARTIAL**: weight-level property verification, distinct from enumerating concrete executor inputs. |

**Hostile referee assessment.** Suppose every concrete execution configuration \(x\) has a view \(V(x)\) in a finite set \(\mathcal V\), and you establish
\[
F(x)=f(V(x)).
\]
If every view’s transition is correct and the abstraction is closed under execution, then every assembled program is correct by induction.

That is **finite-domain exhaustive verification plus an interpreter simulation invariant**. The universal quantifier over assembled programs does not itself make the result new. A certified universal interpreter already executes programs never assembled during certification.

The real work is proving that \(\mathcal V\) is both **complete and small**.

A 512-token page and degree bound eight do not make enumeration practical. Token strings, names, targets, row orderings, and graph neighborhoods still produce enormous combinatorial spaces. “No gap” does not resolve that.

Nor does restricting attention at decoding prove locality. If page KV was produced while attending to other program text, the same visible page can carry different hidden information. This is C1’s cache-history problem again.

If you quotient by renaming, you must prove the executor respects that equivalence. A neural model is not automatically equivariant under arbitrary state names, separators, or row permutations. C3’s empirical symmetrization is not such a proof.

**What would make it a contribution?** A practical abstraction with:

1. A proved coverage theorem for every allowed program;
2. An explicit, tractable number of representative views;
3. A complete certificate for the frozen pretrained executor on those representatives;
4. A demonstrated deployment benefit over certifying each program separately.

That could be valuable verification engineering, especially if the quotient construction is new. The statement “enumerate every possible local input and compose” is not a new theorem.

**Verdict: KILL** as stated. Reconsider only after exhibiting a small, sound quotient whose construction—not merely its exhaustive checking—is the substantive result.

---

The ranking below is by **research value remaining after this audit**, not by ease of producing a demo.

| Rank | Hypothesis | Verdict | What remains worth pursuing |
|---:|---|---|---|
| **1** | **C7 — restoring identity words** | **NARROW** | Learn and uniformly certify a semantic identity word that contracts continuous-state error across all \(S_5\) states. |
| **2** | **C1 — certified KV stack** | **NARROW** | Prove canonical cache-frame semantics and deliver a practical pretrained pushdown executor. |
| **3** | **C2 — collision horizon** | **NARROW** | Predict held-out failure horizons from independently measured quantities; causally separate collisions from dilution. |
| **4** | **C8 — all-program enumeration** | **KILL** | A new tractable, complete quotient of program views could justify reopening it. |
| **5** | **C3 — symmetrized voting** | **KILL** | Useful implementation technique; vote robustness and concentration claims are standard. |
| **6** | **C4 — stochastic uniform bound** | **KILL** | Direct Mitrophanov application; unrestricted converse is false. |
| **7** | **C5 — synchronization iff healing** | **KILL** | Classical recovery analysis; stated equivalence omits decisive input and fault assumptions. |
| **8** | **C6 — finite bicyclic certificate** | **KILL** | Classical scan plus an infinite monoid; finite \(|M|^2\) certification does not cover unbounded Dyck. |