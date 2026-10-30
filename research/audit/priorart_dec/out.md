**Results 1–3 have substantial prior-art overlap, but I did not find the complete position-specific, real-valued, fixed-margin package you describe. Result 4’s repair is already explicit in prior work; calling it an erratum to Chow is misleading because Chow uses output-sequence semantics.**

The most consequential additional find is **Xiang, October 2026**, which proves causal prefix forgetting at the same \((\log n)^{L-1}/n\) rate. The ALiBi rate already appears in **Wu et al., ICML 2025**, for attention rollout.

I searched the requested phrases and variants across arXiv, OpenReview, ACL Anthology, and conference proceedings, including targeted 2023–2026 searches. Google Scholar searches were attempted but inaccessible. Below, quotations are short verbatim excerpts or displayed equations; surrounding descriptions are paraphrases. Verdicts concern the specified component, not automatically the entire numbered result.

**A. Shuyang Xiang. 2026. [A Conditional No-Hair Theorem for Transformers: How Language Models Forget Their Prompt](https://arxiv.org/html/2610.24133). arXiv:2610.24133, submitted October 16.**

Theorem 1, equation (3):
> \[
> \delta_L(t)\le C_L\frac{P(L+\ln t)^{L-1}}{t},
> \qquad C_L\le K_3\sum_{m=0}^{L-1}(K_1+2K_2)^m.
> \]

Here \(P\) bounds **prompt length**, and \(t\) indexes a shared continuation. Assumption 1 imposes a uniform lower bound on normalization denominators. Appendix A handles changing, content-dependent attention weights; it does not freeze attention. Corollary 1 bounds next-token distribution differences. Proposition 1 establishes matching logarithmic order in a linear uniform-attention relay model.

**Verdict: PARTIAL for result 1; IMPLIES the fixed-prefix version of result 3.** This substantially anticipates causal dilution and its fixed-margin consequence. It does not state the arbitrary-position \(\ln(n/p)\) refinement, sparse-Hamming factor, or width-2 \(\epsilon>0\) witness. Appendix A.3 explicitly excludes ALiBi. Replacing denominator nondegeneracy with globally Lipschitz \(\epsilon>0\) normalization is a straightforward proof adaptation, not a wholly new mechanism.

**B. Xinyi Wu, Yifei Wang, Stefanie Jegelka, and Ali Jadbabaie. 2025. [On the Emergence of Position Bias in Transformers](https://proceedings.mlr.press/v267/wu25ad.html). ICML, PMLR 267:67756–67781.**

Theorem 4.5:
> \[
> \mathbb{P}_{\mathrm{decay}}^{(t)}(z_i=j\mid X^{(0)})
> =\Theta\!\left(\binom{t+i-j}{i-j}e^{-(i-j)m}\right).
> \]

The [proof in Appendix E](https://arxiv.org/html/2502.01951v3) counts causal paths through \(t+1\) attention layers. Setting \(L=t+1\), its binomial factor is \(\Theta((1+i-j)^{L-1})\) for fixed depth.

**Verdict: STATES the ALiBi rollout rate; PARTIAL for result 1.** The polynomial degree and exponential factor are already present, including matching bounds. However, rollout through attention matrices is not a perturbation bound between two inputs whose queries, keys, and attention weights all change. Their core analysis also omits your full pre-norm/MLP architecture. Extending the rate to that architecture remains a substantive distinction.

**C. Borun D. Chowdhury. 2026. [Lost in the Middle at Birth: An Exact Theory of Transformer Position Bias](https://arxiv.org/html/2603.10123v1). arXiv:2603.10123.**

Section 4.1, equation (5):
> \[
> \rho_H^{(\mathcal M)}(x)=\frac{1}{(H-1)!}\left(\ln\frac1x\right)^{H-1}.
> \]

Section 3.1 explicitly identifies uniform causal attention with the Cesàro matrix. Equations (1)–(2) give exact discrete matrix powers, including residual mixing; Appendices A–C derive the discrete and continuous kernels.

**Verdict: STATES the Cesàro/logarithmic kernel calculation; PARTIAL for result 1.** The underlying sharpness mechanism is prior art. The calculation concerns an idealized routing model; Appendix D’s linearization does not establish your uniform nonlinear perturbation theorem or an exact width-2 witness satisfying all your assumptions.

**D. Michael Hahn. 2020. [Theoretical Limitations of Self-Attention in Neural Sequence Models](https://aclanthology.org/2020.tacl-1.11/). TACL 8:156–171.**

Lemma 5, concerning a changed earlier input and the final activation:
> “is bounded as \(O(1/n)\) with constants depending on the parameter matrices.”

I checked the [proof](https://aclanthology.org/2020.tacl-1.11.pdf): its attention normalization uses the full length at each row. Theorem 6 develops next-symbol prediction consequences.

**Verdict: PARTIAL for results 1 and 3.** This is the foundational dilution argument and prediction obstruction, but the proof does not give the causal triangular harmonic accumulation. The paper’s use of “decoder” terminology should not be mistaken for a proof of your masked case.

**E. David Chiang and Peter Cholak. 2022. [Overcoming a Theoretical Limitation of Self-Attention](https://aclanthology.org/2022.acl-long.527/). ACL, pages 7654–7664.**

Section 4.2:
> “However, in practice, \(\epsilon\) is always set to a nonzero value, which makes layer normalization Lipschitz-continuous, so Hahn’s Lemma 5 still applies.”

**Verdict: PARTIAL for results 1–2.** The decisive distinction between positive-\(\epsilon\) normalization and singular normalization is explicit prior art. Their constructions evade limitations through different assumptions, including \(\epsilon=0\) or length-dependent attention scaling. They do not prove your causal classification.

**F. Michael Hahn and Mark Rofin. 2024. [Why are Sensitive Functions Hard for Transformers?](https://aclanthology.org/2024.acl-long.800/). ACL, pages 14973–15008; arXiv:2402.09963.**

Limitations:
> “It remains open if transformer decoders, with causal attention masking, face a different set of limitations”

Theorem 4 and Corollary 5 relate input sensitivity to normalization blowup; the later results concern parameter-space sensitivity and learnability.

**Verdict: PARTIAL background, not a statement of results 1–3.** Xiang subsequently addresses a substantial causal-forgetting subproblem. I did not find a paper establishing your full class theorem, nor a source establishing that all of Hahn–Rofin’s broader causal sensitivity/landscape questions are closed.

**G. Blanka Kövér, Alexandra Butoi, Anej Svete, Michael Hahn, and Ryan Cotterell. 2026. [Understanding the Parameter Space Geometry of Transformers Encoding Boolean Functions](https://arxiv.org/html/2606.08768v1). arXiv:2606.08768.**

The ICML proceedings version is titled [Understanding the Parameter Space Volume of Transformers Encoding Boolean Functions](https://proceedings.mlr.press/v306/kover26a.html), PMLR 306:60726–60757.

Immediately following Corollary 3.4:
> “Thus, for large enough \(N\), a transformer recognizer is a constant function.”

Corollary 3.3 establishes uniform \(O(1/N)\) influence at a fixed EOS position when \(\epsilon>0\); Corollary 3.4 converts this into fixed-margin impossibility for nonconstant Boolean functions.

**Verdict: STATES the encoder analogue; PARTIAL for result 2.** Its attention is bidirectional. The causal last-token classification is not literally stated. Nevertheless, the crucial argument—uniformly small single-coordinate changes plus a fixed margin forces constancy along Hamming edges—is already explicit.

**H. Federico Barbero, Andrea Banino, Steven Kapturowski, Dharshan Kumaran, João G. M. Araújo, Alex Vitvitskyi, Razvan Pascanu, and Petar Veličković. 2024. [Transformers need glasses! Information over-squashing in language tasks](https://arxiv.org/html/2406.04267). NeurIPS 37.**

The assumption used in the sensitivity analysis:
> “the attention weights are treated as independent of the input.”

Theorem 5.1 and Appendix B.5 bound sensitivity using products of attention-plus-residual propagation matrices.

**Verdict: PARTIAL for results 1 and 3.** This anticipates the path-product framework and information bottleneck interpretation. The frozen-attention assumption prevents treating it as your complete Lipschitz perturbation theorem. Its other convergence results also do not establish arbitrary same-length Hamming-edit bounds.

**I. Andy Yang, Michaël Cadilhac, and David Chiang. 2025. [Knee-Deep in C-RASP: A Transformer Depth Hierarchy](https://arxiv.org/html/2506.16055). NeurIPS 2025; arXiv:2506.16055.**

Appendix F.5, proof of Proposition F.9:
> “there is a finite window \([i-\Delta_a,i]\) which receives nonzero attention.”

Lemma F.8 proves this for positive ALiBi slope under fixed precision, with
\[
\Delta_a=(S-s_0)/a,\qquad s_0=\log 2^{-s-1}.
\]

**Verdict: STATES finite-precision ALiBi locality; PARTIAL for result 2.** With all slopes positive and fixed depth, a bounded suffix dependency follows directly. Their mechanism is numerical underflow, whereas yours is exact real arithmetic plus a fixed classification margin. Their framework also permits zero-slope heads, so its overall language class should not be identified with definite languages without that additional restriction.

**J. Jiaoda Li and Ryan Cotterell. 2026. [Characterizing the Expressivity of Local Attention in Transformers](https://arxiv.org/html/2605.00768v3). ACL 2026; arXiv:2605.00768.**

Introduction:
> “with purely local attention, the computation depends only on a fixed-length suffix of the input”

Theorem 4.2 characterizes \(k\)-local attention through \(\mathrm{LTL}[Y^{\leq k}]\). Combined with the preceding logical characterizations, it supplies the definite-language correspondence for the appropriate local-attention family.

**Verdict: PARTIAL for result 2; directly anticipates the ordinary definite-language converse.** Their theorem uses fixed precision and no positional embeddings. It does not provide your real-valued ALiBi necessity theorem or arbitrary length-dependent acceptance. Also, their \(k\)-local masks have specific semantics: the paper explicitly distinguishes one-local from larger windows, so its theorem should not be paraphrased as unrestricted equivalence for every window convention.

**K. Franz Nowak, Ryan Cotterell, and Reda Boumasmoud. 2026. [A Compositional Theory of Causally Masked Transformers](https://arxiv.org/html/2607.26988v1). arXiv:2607.26988.**

Theorem 29:
> “Any language accepted by a NoPE transformer with width-one sliding-window attention is definite.”

Corollary 34 establishes tightness under the paper’s free-wiring assumption.

**Verdict: STATES a window/definite characterization under its assumptions; PARTIAL for result 2.** The theory uses finite arithmetic and specified evaluation semantics. Its lower bounds permit arbitrary maps between the relevant finite sets. Neither the unrestricted real-valued fixed-margin classification nor the positional “modulo length” extension follows literally from the stated theorem.

**L. Andy Yang, David Chiang, and Dana Angluin. 2024. [Masked Hard-Attention Transformers Recognize Exactly the Star-Free Languages](https://arxiv.org/html/2310.13897). NeurIPS 2024; arXiv:2310.13897.**

Theorem 5:
> “Both B-RASP and transformers with only future-masked rightmost-hard attention recognize exactly the star-free languages.”

**Verdict: PARTIAL for result 2’s constructive background.** It establishes powerful causal hard-attention recognition and includes bounded-suffix languages. It does not establish bounded-score softmax locality: hard selection bypasses the dilution assumption. Its normalization constructions likewise cannot simply be substituted into your model without checking their hypotheses.

**M. Benjamin L. Edelman, Surbhi Goel, Sham Kakade, and Cyril Zhang. 2022. [Inductive Biases and Variable Creation in Self-Attention Mechanisms](https://proceedings.mlr.press/v162/edelman22a.html). ICML, PMLR 162:5793–5831.**

Section 5:
> “this can be circumvented by allowing \(d\) and the weight norms to scale as \(\log(T)\).”

Proposition 5.1 constructs representations of sparse input dependencies with resources depending on context length.

**Verdict: PARTIAL for the lookup/expressivity comparison in result 3.** This explains how length-specific constructions escape dilution. It does not contradict a theorem about one fixed model with uniformly bounded scores across all lengths, nor supply your eventual lookup impossibility.

**N. Guanyu Cui, Zhewei Wei, and Kun He. 2026. [Position: The Turing-Completeness of Autoregressive Transformers Relies Heavily on Context Management](https://arxiv.org/html/2605.19514). arXiv:2605.19514v2.**

Lemma 5.3 concludes:
> “greedy decoding outputs \(f(a,b)\).”

The lemma realizes any function \(f:\Sigma^2\to\Sigma\) with a fixed decoder on length-two contexts; Appendix B gives the construction. Proposition 5.1 bounds systems using their summarization-style context management by constant-space computation.

**Verdict: PARTIAL for result 3’s reset/context-management distinction.** The separation between a fixed local decoder and the computational role of context management is explicit. It does not state your table-at-the-start margin obstruction or a W-method/per-row verification theorem. Completeness of exhaustive checking on a genuinely finite reset-input domain is an elementary consequence of finiteness.

**O. Bálint Kocsis and Jurriaan Rot. 2024/2025. [Complete Test Suites for Automata in Monoidal Closed Categories](https://arxiv.org/html/2411.13412v1). arXiv:2411.13412; FoSSaCS 2025, pages 198–219, [DOI](https://doi.org/10.1007/978-3-031-90897-2_10).**

Definition 3(ii) in the arXiv HTML requires:
> “such that \(\varepsilon\in W\)”

Section 5.1 explicitly extends the construction to Moore machines. The Moore example in Appendix D.1 includes \(\varepsilon\) in both proposed characterization sets. Their completeness proof uses the empty-word inclusion to obtain output agreement.

**Verdict: STATES the required safeguard; PARTIAL for the literal “unless” claim in result 4.** This requirement was explicit by November 2024. It does not assert that every individual suite omitting \(\varepsilon\) is incomplete.

There is also a notation issue: their \(P\) is a **state cover**, giving \(P\Sigma^{\le m-n+1}W\). Your exponent \(m-n\) corresponds to using a **transition cover**.

**P. Tsun S. Chow. 1978. [Testing Software Design Modeled by Finite-State Machines](https://archiv.infsec.ethz.ch/intranet_secured/r/1/chow-testingFSMs.pdf). IEEE Transactions on Software Engineering SE-4(3):178–187. DOI:10.1109/TSE.1978.231496.**

Appendix, Definition 1:
> “yield identical output sequences as a response to each input sequence in \(V\).”

The appendix’s final theorem establishes equivalence from \(PZ\)-equivalence under that semantics. Definition 7 only requires that \(W\) distinguish states; it does not add your final-output-only convention.

**Verdict: UNRELATED to an alleged error in Chow’s stated theorem; PARTIAL as the theorem being adapted.** Observing an output sequence also observes outputs along prefixes. Observing only the final output discards that information. A counterexample to the latter adaptation is not a counterexample to Chow’s theorem.

The following additional candidates were screened because they could otherwise be mistaken for the requested results:

| Candidate and full citation | Verbatim excerpt and location | Verdict |
|---|---|---|
| Hanna Herasimchyk, Robin Labryga, Tomislav Prusina, and Sören Laue. 2026. [A Structural Theory of Position Bias in Transformers](https://arxiv.org/html/2602.16837), arXiv:2602.16837v3. Earlier title: *A Residual-Aware Theory of Position Bias in Transformers*. | §3: “while abstracting away token-wise components such as MLP blocks and layer normalization.” | **PARTIAL, result 1.** Propositions 4.2–4.4 analyze residual-aware rollout and positional drift. They do not supply the full nonlinear single-token bound. |
| Daniel Wolfson and Tal Wagner. 2026. [Positional LSH: Binary Block Matrix Approximation for Attention with Linear Biases](https://arxiv.org/html/2605.09472), arXiv:2605.09472. | Abstract: “reducing long-context ALiBi to a collection of randomized short-context regular (positionally unbiased) attention operations.” | **PARTIAL, results 1–2.** Theorems 2.1–2.2 approximate ALiBi through randomized local blocks. This is not a deterministic, length-independent suffix classification theorem. |
| Cheng Huan and Hongwei Yuan. 2026. [An Adjoint-Sensitivity Framework for Lost-in-the-Middle Phenomena in Causal Residual Transformers](https://arxiv.org/html/2607.17696), arXiv:2607.17696. | Theorem 2.7: \(\left\|\mathrm{Attn}_{\theta}^{\rm c}(X_L)_i-\mathrm{Attn}_{\theta}^{\rm c}(X)(p_i)\right\|\le C_{R,\eta}/L.\) | **UNRELATED to the claimed \(1/n\) perturbation theorem.** This is discrete-to-continuum approximation error for smooth position fields, not influence of changing one token. |
| Alexander Kozachinskiy, Tomasz Steifer, and Przemysław Andrzej Wałęga. 2026. [Parity, Sensitivity, and Transformers](https://arxiv.org/html/2602.05896), arXiv:2602.05896. | Theorem 8: “there is a 4-layer transformer for PARITY with a standard-form input embedding” | **PARTIAL, result 2’s scope.** The causal construction permits polynomially growing positional encodings. Polynomial boundedness is not uniform boundedness; this does not contradict your assumptions. |
| Anonymous authors. 2025 submission to ICLR 2026. [Language Models Are Injective and Hence Invertible](https://openreview.net/pdf/57a9aa51498f44a0f3027131a75c216167dadc76.pdf). | Theorem 2.2: \(\Pr[r(s;\theta)=r(s';\theta)]=0.\) | **UNRELATED to a uniform-margin contradiction.** The theorem fixes a finite context horizon. Injectivity, and positive separation on each finite domain, do not imply one positive separation bound over all lengths. |

Several qualifications affect the novelty claims themselves:

- **Result 1 needs \(p<n\).** As written, its flat bound includes \(p=n\), where it predicts \(O(1/n)\). The residual identity path permits an \(O(1)\) change. Exclude the readout position or add a diagonal term. For ALiBi, “bounded scores” must refer to the content scores before adding the unbounded distance penalty.
- **The main unlocated part of result 2 is the exact real-valued causal necessity theorem.** Its margin argument is directly analogous to Kövér et al.; the window converse has substantial prior art. The phrase “every language definite modulo length” also requires a precise allowance for length information. Arbitrary dependence on \(n\) cannot be promised for an arbitrary fixed positional-encoding scheme.
- **Result 3’s Hamming inequality follows directly by telescoping result 1.** For the table consequence, one needs two admissible contexts with different required destinations and only the specified table coordinates changed. A destination’s literal absence elsewhere does not alone rule out its being encoded elsewhere or memorized in parameters. Reset verification additionally requires that the reset remove all persistent computational state and leave a fixed finite input domain.
- **Result 4 should say “the general guarantee can fail without \(\varepsilon\),” not that every such suite fails.** For example, a unary two-state toggle with outputs \(0,1\), transition cover \(\{\varepsilon,a,aa\}\), and \(W=\{a\}\) has the complete two-state test suite \(\{a,aa,aaa\}\), despite omitting \(\varepsilon\).

The failure motivating the corrected result 4 is nevertheless real. Consider three states with outputs \(0,0,1\), initial state \(q_0\), and transitions
\[
a:(q_0,q_1,q_2)\mapsto(q_1,q_2,q_2),\qquad
b:(q_0,q_1,q_2)\mapsto(q_2,q_1,q_2).
\]
Then \(W=\{a,b\}\) distinguishes all states. Changing only \(q_0\)’s output produces a different minimal three-state Moore machine that agrees on **every nonempty input**. Thus every suite ending in a word from this \(W\) misses the discrepancy at \(\varepsilon\). This is my explicit counterexample, not a quotation from the literature.

| Result | Verdict | Decisive prior art and remaining distinction |
|---|---|---|
| **1. Causal influence and sharpness** | **PARTIALLY KNOWN** | [Xiang, Theorem 1 and Proposition 1](https://arxiv.org/html/2610.24133): causal prefix rate and linear sharpness. [Wu et al., Theorem 4.5](https://arxiv.org/html/2502.01951v3): exact ALiBi rollout order. [Chowdhury, equations (1)–(6)](https://arxiv.org/html/2603.10123v1): Cesàro kernels. I did not locate the full arbitrary-\(p\), nonlinear, width-2 package. |
| **2. Fixed-margin language class** | **PARTIALLY KNOWN** | [Kövér et al., Corollaries 3.3–3.4](https://arxiv.org/html/2606.08768v1): encoder margin collapse. [Li–Cotterell, Theorem 4.2](https://arxiv.org/html/2605.00768v3) and [Nowak et al., Theorem 29](https://arxiv.org/html/2607.26988v1): window/definite correspondence. [Yang–Cadilhac–Chiang, Lemma F.8](https://arxiv.org/html/2506.16055): finite-precision ALiBi locality. The exact real-valued causal necessity statement is **NEW as far as searched**. |
| **3. Autoregressive/table/reset corollary** | **PARTIALLY KNOWN** | [Xiang, Theorem 1 and Corollary 1](https://arxiv.org/html/2610.24133) directly imply fixed-prefix prediction convergence and the associated margin obstruction. [Cui et al., §5](https://arxiv.org/html/2605.19514) treats fixed decoders and context management. The sparse-edit formulation is an immediate consequence of result 1; the specific table application was not located. |
| **4. W-method final-output repair** | **KNOWN, with corrected wording** | [Kocsis–Rot, Definition 3(ii), §5.1 and Appendix D.1](https://arxiv.org/html/2411.13412v1) explicitly require \(\varepsilon\in W\) and cover Moore machines. Literal necessity for every suite is false. [Chow’s Definition 1](https://archiv.infsec.ethz.ch/intranet_secured/r/1/chow-testingFSMs.pdf) uses output sequences, so “erratum to Chow” is unsupported. |

What I could not access:

- **Google Scholar results:** direct searches failed; the browser fallback was unavailable. I therefore cannot claim completed Scholar coverage.
- **M. P. Vasilevskii, “Failure diagnosis of automata,” *Cybernetics* 9:653–665 (1973), [DOI:10.1007/BF01068590](https://link.springer.com/article/10.1007/BF01068590):** the publisher exposed bibliographic information but not the subscription full text. I cannot quote or independently assess its original theorem.
- **Author identities for the anonymous OpenReview injectivity version:** the inspected PDF is anonymous; its attribution above deliberately preserves that limitation.