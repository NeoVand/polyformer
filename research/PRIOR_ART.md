# Prior art and the boundary of the group-composition result

Audit date: 20 October 2026. Companion to [THEORY.md](THEORY.md) and
[GROUPS.md](GROUPS.md). This is a positioning audit, not an exhaustive systematic review.

**The ordered-subset construction is not new mathematics.** The closest previously published
sequence layer found in this audit is **Seq2Tens** (Toth, Bonnier and Oberhauser, ICLR 2021).
Its basic feature map already sums noncommutative tensor products over all ordered
subsequences, graded by their length; our matrix polynomial is an algebraic compression of
that feature map. Path Development Networks already learn Lie-group-valued products, and
earlier work already combines signatures with attention. I did **not** find a source that
implements the complete present combination—learned group matrices, scalar gates, sums over
distinct ordered subsets, and a separate readout for each subset arity and each position
contained in the subset. That limited search finding is not a proof of priority.

The strongest defensible story is therefore a **specific relational use of established
noncommutative sequence features**, with a task-specific separation, constructive
representation result and measured learning behavior. It is not the invention of
noncommutative sequence composition, signature pooling, trainable matrix development,
group representations in neural networks, or higher-order attention.

## 1. What was verified

Every arXiv identifier linked below was checked by fetching its abstract page with `curl`,
starting with `https://export.arxiv.org/abs/<id>` and falling back to
`https://arxiv.org/abs/<id>` if needed. The reproducible command is:

```sh
python3 research/verify_prior_art.py
```

[The verification manifest](results/prior_art_verified.json) records 36 successful checks,
the fetched title and author list, submission metadata, comments and journal-reference
fields, HTTP status, timestamp, URL and response SHA-256. **VERIFIED** below means identity
and bibliographic metadata were checked against that abstract page; it does not mean an
abstract proves every technical claim. The closest papers' full texts were also read, with
equation or section pointers given where the distinction matters. Venue claims use the
arXiv journal/comments fields or the linked proceedings/publisher source. Where no
publication venue was verified, the entry says **arXiv preprint**, even if the work may have
subsequently appeared elsewhere.

Older papers without a located arXiv version use an authoritative publisher or author
source. “No arXiv identifier located” is not an invented identifier and is not a claim that
no version exists. Incomplete leads are explicitly marked **UNVERIFIED**.

Metadata corrections worth preserving:

- Lou–Li–Ni first appeared on arXiv in **2022** and was published in **TMLR in 2024**.
- The current HLA author list includes **Mengdi Wang**, absent from some indexed summaries.
- DeltaProduct's current title is **Improving State-Tracking in Linear RNNs via Householder
  Products**, not the earlier *Increasing the Expressivity of DeltaNet Through Products of
  Householders*.
- MesaNet's current author list includes **Sarthak Mittal**.
- The arXiv journal-reference field for *Generalized iterated-sums signatures* says volume
  **623**; the publisher gives **632**, which is the volume used here.
- Grazzi et al.'s arXiv comments record corrections to Theorems 1–2 and Proposition 1.
  Cite the corrected paper, not an early abstract's stronger informal wording.

## 2. The closest mathematical overlap

Let \(M_t=g_tU_t\), where \(g_t\) is a scalar gate and \(U_t\) is a learned rotation. Write

\[
P(z)=\prod_{t=1}^n(I+zM_t),\qquad
P_k=\sum_{i_1<\cdots<i_k}M_{i_1}\cdots M_{i_k}.
\]

For the vector space \(V=M_d(\mathbb R)\), form the tensor feature

\[
S_k=\sum_{i_1<\cdots<i_k}
M_{i_1}\otimes\cdots\otimes M_{i_k}.
\]

The multiplication map \(\mu_k(A_1\otimes\cdots\otimes A_k)=A_1\cdots A_k\)
gives \(P_k=\mu_k(S_k)\). This is an exact identity, not an analogy. \(S_k\) is the
simple-lift Seq2Tens level and the strict, singleton-letter part of an iterated-sums
signature. “Noncommutative” refers to concatenating ordered feature factors; the
commutative quasi-shuffle algebra of coordinate functions in the signature literature is
a different algebraic operation and does not make the sequence representation order-blind.
See Seq2Tens §2, equations (2), (6)–(7), and Diehl–Ebrahimi-Fard–Tapia §3.

The present position-containing sector also has a simple relationship to that feature map.
Introducing independent scalar marks \(\lambda_t\),

\[
F_{k-1}(i)
=\left.
\lambda_i\frac{\partial}{\partial\lambda_i}
[z^k]\prod_{t=1}^n(I+z\lambda_tM_t)
\right|_{\lambda_1=\cdots=\lambda_n=1}.
\]

It retains exactly the monomials whose subset contains \(i\). Splitting each such monomial
before and after \(i\) gives the implemented prefix/suffix formula
\(\sum_{a+b=k-1}L_a(i)M_iR_b(i)\). This derivative identity and the matrix compression
are our explicit comparisons of the formulas; they are not priority claims for a new
signature theorem.

Path development instead composes \(\prod_t\exp(A_t)\). Expanding
\(\prod_t\exp(zA_t)\) includes repeated selections at one time, with factorial weights.
The strict subset polynomial \(\prod_t(I+zM_t)\) allows each position at most once.
Both are noncommutative generating constructions, but their coefficients are different.
Also, the sums \(P_k\) generally lie in a matrix **algebra**, not in the rotation group,
even though the individual \(U_t\) lie in that group.

### Signatures, development and sequence layers

**[S1] Kuo-Tsai Chen. _Iterated Integrals and Exponential Homomorphisms._**
Proceedings of the London Mathematical Society, s3-4(1):502–512, 1954.
ArXiv: no identifier located; publisher identity **VERIFIED**,
[DOI 10.1112/plms/s3-4.1.502](https://londmathsoc.onlinelibrary.wiley.com/doi/10.1112/plms/s3-4.1.502).
**Does:** Establishes foundational algebra connecting iterated path integrals with
exponential/multiplicative constructions.
**Overlap/difference:** Ordered composition and generating series have this classical
lineage; the present discrete, gated relational layer is not an invention of that algebra.

**[S2] Terry J. Lyons. _Differential equations driven by rough signals._**
Revista Matemática Iberoamericana 14(2):215–310, 1998.
ArXiv: no identifier located; publisher identity **VERIFIED**,
[DOI 10.4171/RMI/240](https://ems.press/journals/rmi/articles/5137).
**Does:** Develops the rough-path framework in which iterated integrals support controlled
differential equations driven by irregular paths.
**Overlap/difference:** This supplies the broader theory behind signatures and development,
whereas our finite token experiment studies a particular discrete matrix evaluation and
does not introduce a new rough-path construction.

**[S3] Joscha Diehl, Kurusch Ebrahimi-Fard and Nikolas Tapia.
_Time-warping invariants of multidimensional time series._**
Acta Applicandae Mathematicae 170:265–290, 2020; first preprint 2019.
ArXiv **VERIFIED**: [1906.05823](https://arxiv.org/abs/1906.05823).
**Does:** Develops iterated-sums signatures and their algebraic description for discrete
time series.
**Overlap/difference:** The ordered distinct-index sums underlying holonomy sectors are
already present; we evaluate them in small matrix algebras and use position-containing
sectors to predict identity-product relations.

**[S4] Joscha Diehl, Kurusch Ebrahimi-Fard and Nikolas Tapia.
_Generalized iterated-sums signatures._**
Journal of Algebra **632**:801–824, 2023; first preprint 2020.
ArXiv **VERIFIED**: [2012.04597](https://arxiv.org/abs/2012.04597);
[publisher volume and DOI](https://www.sciencedirect.com/science/article/pii/S0021869323002934).
**Does:** Studies nonlinear transformations of iterated-sums signatures and the associated
deformed quasi-shuffle structures.
**Overlap/difference:** Our ordered subset features belong to this established family of
sequence statistics, while the finite-group classification construction and head-dimension
experiments are specific to this project.

**[S5] Joscha Diehl, Kurusch Ebrahimi-Fard and Nikolas Tapia.
_Tropical time series, iterated-sums signatures and quasisymmetric functions._**
SIAM Journal on Applied Algebra and Geometry 6(4):563–599, 2022; first preprint 2020.
ArXiv **VERIFIED**: [2009.08443](https://arxiv.org/abs/2009.08443).
**Does:** Extends iterated-sums features to commutative semirings and shows how they encode
chronological aspects of time series efficiently.
**Overlap/difference:** It already makes the choice of feature algebra consequential;
our particular order-blind theorem requires identical per-token commutative features,
not the false assertion that every ordered sum over scalar features loses order.

**[S6] Patric Bonnier, Patrick Kidger, Imanol Perez Arribas, Cristopher Salvi and Terry Lyons.
_Deep Signature Transforms._**
NeurIPS 2019.
ArXiv **VERIFIED**: [1905.08494](https://arxiv.org/abs/1905.08494);
[proceedings](https://proceedings.neurips.cc/paper_files/paper/2019/hash/d2cdf047a6674cef251d56544a3cf029-Abstract.html).
**Does:** Makes signatures differentiable network layers and learns transformations of a
stream before taking its signature.
**Overlap/difference:** Learning token features before a compositional sequence summary is
prior art; our specialization uses gated rotations and separate relational arities.

**[S7] Csaba Toth, Patric Bonnier and Harald Oberhauser.
_Seq2Tens: An Efficient Representation of Sequences by Low-Rank Tensor Projections._**
ICLR 2021; first preprint 2020.
ArXiv **VERIFIED**: [2006.07027](https://arxiv.org/abs/2006.07027).
**Does:** Lifts token features into a free tensor algebra, multiplies them in sequence
order, and computes learned low-rank projections of the resulting sums over ordered
subsequences.
**Overlap/difference:** This is the closest single precedent for our generating feature
map; our proposed distinction is its compact group-matrix parameterization and
position-containing readout, together with the finite-group separation, rather than
noncommutative products or subsequence pooling themselves.

**[S8] Hang Lou, Siran Li and Hao Ni.
_Path Development Network with Finite-dimensional Lie Group Representation._**
Transactions on Machine Learning Research, August 2024; first preprint 2022.
ArXiv **VERIFIED**: [2204.00740](https://arxiv.org/abs/2204.00740).
**Does:** Learns a Lie-algebra map and recurrently multiplies its exponentials to obtain
compact Lie-group-valued sequence features; equation (1) is
\(z_{t+1}=z_t\exp(M_\theta(x_{t+1}-x_t))\).
**Overlap/difference:** This is the closest single precedent for our learned rotation
products, but it accumulates development of the path rather than separately reading
strict-subset products containing every designated position and arity.

**[S9] Nicola Muca Cirone, Antonio Orvieto, Benjamin Walker, Cristopher Salvi and Terry Lyons.
_Theoretical Foundations of Deep Selective State-Space Models._**
NeurIPS 2024.
ArXiv **VERIFIED**: [2402.19047](https://arxiv.org/abs/2402.19047);
[conference paper](https://openreview.net/pdf?id=3SzrqwupUx).
**Does:** Uses rough-path/signature tools to analyze how selective recurrent transitions
and cross-channel interactions determine sequence-model expressivity.
**Overlap/difference:** The connection between recurrence, signature projections and
expressive restrictions is already explicit; our result concerns a particular finite-group
identity-subset query and its order-blind Bayes ceiling.

**[S10] Fernando Moreno-Pino, Álvaro Arroyo, Harrison Waldon, Xiaowen Dong and Álvaro Cartea.
_Rough Transformers: Lightweight and Continuous Time Series Modelling through Signature Patching._**
NeurIPS 2024.
ArXiv **VERIFIED**: [2405.20799](https://arxiv.org/abs/2405.20799).
**Does:** Uses multiview signature attention to combine path-signature features with
transformer processing of time series.
**Overlap/difference:** Combining signatures with attention is prior art; these signature
patches are not the present sums of learned group products anchored at a designated token.

**[S11] Joscha Diehl, Rasheed Ibraheem, Leonard Schmitz and Yue Wu.
_Tensor-to-Tensor Models with Fast Iterated Sum Features._**
Neurocomputing 675:132884, 2026; first preprint 2025.
ArXiv **VERIFIED**: [2506.06041](https://arxiv.org/abs/2506.06041);
[publisher](https://doi.org/10.1016/j.neucom.2026.132884).
**Does:** Builds efficient differentiable iterated-sum layers for tensor/image data using
combinatorial point configurations.
**Overlap/difference:** Efficient neural layers based on learned iterated sums are already
established; our restriction to group-matrix features and finite-group relational labels
is different from their image/tensor construction.

**[S12] Leonard Schmitz. _Attention on Signature-type Features: Beating Quadratic Costs._**
15th Berlin–Oxford Young Researchers' Meeting, 2022, talk abstract; arXiv identifier
not located.
Talk title, author and abstract **VERIFIED** in the
[organizers' booklet, §4.3](https://www.wias-berlin.de/workshops/YRM2022/Booklet_15th_Oxford_Meeting.pdf).
**Does:** Announces an efficient subsequence-matching mechanism combining attention and
signature features through low-rank structure.
**Overlap/difference:** It prevents a “first signature attention” claim, but the abstract
does not establish the exact group-gated, position-containing arity construction.
The related thesis, _Hopf Algebras Related to Image and Time Series Data_, chapter 5,
is a particularly relevant **UNVERIFIED full-text comparison**: the repository
[PDF endpoint](https://epub.ub.uni-greifswald.de/files/11693/LSdiss-finalBibVersion.pdf)
returned a bot challenge to direct retrieval, so no claim of non-overlap rests on its
unread full text.

One additional lead remains **UNVERIFIED**: Richard Krieg, _Towards a Unifying
Sequence-to-Sequence Deep Learning Layer Based on Iterated Sums_, master's thesis,
University of Greifswald, 2024, listed in [S11]'s bibliography. No arXiv identifier or
direct full text was verified in this audit. It should be checked before an archival
paper makes a strong first-architecture claim.

## 3. Orthogonal recurrence and state tracking

**[R1] Martin Arjovsky, Amar Shah and Yoshua Bengio.
_Unitary Evolution Recurrent Neural Networks._**
ICML 2016; first preprint 2015.
ArXiv **VERIFIED**: [1511.06464](https://arxiv.org/abs/1511.06464);
[proceedings](https://proceedings.mlr.press/v48/arjovsky16.html).
**Does:** Parameterizes unitary recurrent weights to control vanishing and exploding
gradients.
**Overlap/difference:** Norm-preserving recurrence is established, but a shared recurrent
weight plus nonlinear state update is not our token-dependent group map or subset readout.

**[R2] Scott Wisdom, Thomas Powers, John R. Hershey, Jonathan Le Roux and Les Atlas.
_Full-Capacity Unitary Recurrent Neural Networks._**
NeurIPS 2016.
ArXiv **VERIFIED**: [1611.00035](https://arxiv.org/abs/1611.00035).
**Does:** Optimizes over the full unitary manifold rather than a capacity-restricted
structured parameterization.
**Overlap/difference:** The distinction between a matrix family's dimensional capacity
and trainability is prior art; our dimension experiment concerns which finite-group
representations and relational statistics a token-dependent head learns.

**[R3] Mario Lezcano-Casado and David Martínez-Rubio.
_Cheap Orthogonal Constraints in Neural Networks: A Simple Parametrization of the
Orthogonal and Unitary Group._**
ICML 2019.
ArXiv **VERIFIED**: [1901.08428](https://arxiv.org/abs/1901.08428).
**Does:** Uses Lie-algebra/exponential parameterizations to train orthogonal and unitary
weights efficiently.
**Overlap/difference:** Exponentiating skew matrices is an established parameterization,
not a novelty of `holo_mats`; the new question is how its resulting token maps support
the chosen relation.

**[R4] Bingbin Liu, Jordan T. Ash, Surbhi Goel, Akshay Krishnamurthy and Cyril Zhang.
_Transformers Learn Shortcuts to Automata._**
ICLR 2023; first preprint 2022.
ArXiv **VERIFIED**: [2210.10749](https://arxiv.org/abs/2210.10749);
[author project page](https://clarabing.github.io/shortcut_automata/).
**Does:** Constructs and studies transformer simulations of finite automata, including
logarithmic-depth general simulations and constant-depth cases characterized through
algebraic/circuit structure.
**Overlap/difference:** Algebra-sensitive transformer state tracking is already central
there; our one-layer label separation is for ordered subsets at fixed arity and does
not prove that transformers cannot compose.

**[R5] William Merrill, Jackson Petty and Ashish Sabharwal.
_The Illusion of State in State-Space Models._**
ICML 2024.
ArXiv **VERIFIED**: [2404.08819](https://arxiv.org/abs/2404.08819).
**Does:** Places specified log-precision SSM families, including fixed-transition and
diagonal selective models, within uniform \(TC^0\) and studies permutation tracking.
**Overlap/difference:** Their upper bound does not cover arbitrary input-dependent
noncommuting matrix recurrences, which are exactly the relevant full-product baseline
here; an \(NC^1\)-based impossibility remains conditional on \(TC^0\ne NC^1\).

**[R6] Riccardo Grazzi, Julien Siems, Arber Zela, Jörg K. H. Franke, Frank Hutter and
Massimiliano Pontil. _Unlocking State-Tracking in Linear RNNs Through Negative Eigenvalues._**
ICLR 2025; first preprint 2024.
ArXiv **VERIFIED**: [2411.12537](https://arxiv.org/abs/2411.12537);
[accepted paper record](https://discovery.ucl.ac.uk/id/eprint/10211968/).
**Does:** Analyzes restrictions on linear recurrent transitions and shows how negative
eigenvalues and products of elementary updates enable substantially richer state tracking.
**Overlap/difference:** Matrix-transition structure already has proved consequences for
group/automaton computation; our additional object is the family of proper-subset
statistics and designated-token relational predictions.

**[R7] Imanol Schlag, Kazuki Irie and Jürgen Schmidhuber.
_Linear Transformers Are Secretly Fast Weight Programmers._**
ICML 2021.
ArXiv **VERIFIED**: [2102.11174](https://arxiv.org/abs/2102.11174);
[proceedings](https://proceedings.mlr.press/v139/schlag21a.html).
**Does:** Connects linear attention to fast-weight programming and replaces purely
additive updates with a learned delta rule for correcting associative memory.
**Overlap/difference:** This is an origin of the delta-rule baseline, whose matrix state
already mixes previous information multiplicatively; our layer makes subset cardinality
and membership explicit.

**[R8] Songlin Yang, Bailin Wang, Yu Zhang, Yikang Shen and Yoon Kim.
_Parallelizing Linear Transformers with the Delta Rule over Sequence Length._**
NeurIPS 2024.
ArXiv **VERIFIED**: [2406.06484](https://arxiv.org/abs/2406.06484).
**Does:** Uses structured products of Householder-type matrices to train DeltaNet
efficiently in parallel over sequence chunks.
**Overlap/difference:** Parallel products and matrix-valued recurrent memory are not ours;
our recurrence tracks a graded collection of subset sums instead of only the delta-rule
state.

**[R9] Songlin Yang, Jan Kautz and Ali Hatamizadeh.
_Gated Delta Networks: Improving Mamba2 with Delta Rule._**
ICLR 2025; first preprint 2024.
ArXiv **VERIFIED**: [2412.06464](https://arxiv.org/abs/2412.06464).
**Does:** Combines global forgetting gates with delta-rule memory updates and supplies an
efficient parallel training algorithm.
**Overlap/difference:** Gating plus matrix state already appears here, but the gates control
a recurrent associative memory rather than directly weighting each selected factor in
an explicitly arity-separated subset polynomial.

**[R10] Julien Siems, Timur Carstensen, Arber Zela, Frank Hutter, Massimiliano Pontil and
Riccardo Grazzi. _DeltaProduct: Improving State-Tracking in Linear RNNs via Householder Products._**
NeurIPS 2025.
ArXiv **VERIFIED**: [2502.10297](https://arxiv.org/abs/2502.10297).
**Does:** Increases per-token transition expressivity using products of generalized
Householder matrices, with state-tracking theory and empirical group-word experiments.
**Overlap/difference:** This is the closest prior-art baseline for the claim that richer
matrix composition helps group tracking, while the present target additionally asks which
proper subsets containing a specified token realize a relation.

A pure matrix recurrence \(H_t=H_{t-1}U(x_t)\) yields the full prefix product.
The degree-\(t\) coefficient of \(\prod_{j\le t}(I+zU_j)\) is exactly that product.
Thus the full-arity sector includes this familiar computation, but a claim about
constant \(K\) cannot silently include arbitrarily long words.

## 4. Learning group operations and representations

**[G1] Bilal Chughtai, Lawrence Chan and Neel Nanda.
_A Toy Model of Universality: Reverse Engineering How Networks Learn Group Operations._**
ArXiv preprint, 2023.
ArXiv **VERIFIED**: [2302.03025](https://arxiv.org/abs/2302.03025).
**Does:** Reverse engineers networks learning finite-group composition in terms of
group-representation-theoretic algorithms.
**Overlap/difference:** Learning nonabelian group representations from task supervision is
already demonstrated; our evidence concerns their emergence inside gated subset-composition
heads, and the accuracy and learning-speed changes with head dimension.

**[G2] Neel Nanda, Lawrence Chan, Tom Lieberum, Jess Smith and Jacob Steinhardt.
_Progress measures for grokking via mechanistic interpretability._**
ICLR 2023.
ArXiv **VERIFIED**: [2301.05217](https://arxiv.org/abs/2301.05217);
[conference paper](https://openreview.net/pdf?id=9XFSbDPmdW).
**Does:** Identifies Fourier/trigonometric circuits learned by small transformers on
modular addition and uses them to explain training dynamics.
**Overlap/difference:** This directly rules out a general claim that softmax-based
transformers cannot learn composition; our frozen-character Match-k result is a failure
under a specified task, architecture and optimization budget.

## 5. Higher-order attention

**[H1] James Clift, Dmitry Doryn, Daniel Murfet and James Wallbridge.
_Logic and the 2-Simplicial Transformer._**
ICLR 2020; first preprint 2019.
ArXiv **VERIFIED**: [1909.00668](https://arxiv.org/abs/1909.00668);
[authors' implementation and venue](https://github.com/dmurfet/2simplicialtransformer).
**Does:** Extends attention to higher-dimensional scores and tensor products of value
vectors for logical reasoning.
**Overlap/difference:** Higher-order value composition and relational inductive biases
are prior art; our operator specializes to ordered associative matrix products and an
efficient dynamic program over subset arity.

**[H2] Clayton Sanford, Daniel Hsu and Matus Telgarsky.
_Representational Strengths and Limitations of Transformers._**
NeurIPS 2023.
ArXiv **VERIFIED**: [2306.02896](https://arxiv.org/abs/2306.02896);
[proceedings](https://proceedings.neurips.cc/paper_files/paper/2023/hash/73bf692447f174984f30499ec9b20e04-Abstract.html).
**Does:** Gives attention expressivity bounds, including a triple-detection/Match3
obstruction under explicit resource assumptions, using communication complexity.
**Overlap/difference:** Match-k and attention lower bounds are not new here; the present
order-blind result conditions on a coarsened input statistic and the benchmark varies
the group's multiplication law.

**[H3] Aurko Roy, Timothy Chou, Sai Surya Duvvuri, Sijia Chen, Jiecao Yu, Xiaodong Wang,
Manzil Zaheer and Rohan Anil. _Fast and Simplex: 2-Simplicial Attention in Triton._**
ArXiv preprint, 2025.
ArXiv **VERIFIED**: [2507.02754](https://arxiv.org/abs/2507.02754).
**Does:** Implements efficient 2-simplicial attention and reports token-efficiency gains
on language-related tasks.
**Overlap/difference:** Practical higher-order attention and positive language evidence
already exist, whereas our group results concern a distinct matrix-composition mechanism
and do not overturn our own negative language experiments.

**[H4] Yifan Zhang, Zhen Qin, Mengdi Wang and Quanquan Gu.
_Higher-order Linear Attention._**
ArXiv preprint, 2025; current checked version v3, May 2026.
ArXiv **VERIFIED**: [2510.27258](https://arxiv.org/abs/2510.27258).
**Does:** Computes higher-order interactions from compact prefix sufficient statistics
with exact serial/chunk-scan identities; its second-order unmasked numerator is
\(q_t^\top S_t^K C_t^{QV}\), with causal corrections.
**Overlap/difference:** Linear-time higher-order computation and associative scans are
prior art, but these moment contractions are different from homogeneous products of
token-dependent group matrices along distinct-index subsequences.

**[H5] Shirin Amiraslani and Xin Gao.
_Beyond Pairwise Attention: Higher-Order Modular Attention for Efficient Sequence Learning._**
ArXiv preprint, 2026.
ArXiv **VERIFIED**: [2603.11133](https://arxiv.org/abs/2603.11133).
**Does:** Combines pairwise and explicit triadic pathways using blocks, windows, low-rank
projection and learned fusion, evaluated on PARITY, MATCH3 and TAPE.
**Overlap/difference:** Our MATCH3 comparisons inherit an established higher-order
benchmark, while ordered finite-group composition and the representation-dimension
question are different experiments.

**[H6] Sayak Chakrabarti, Toniann Pitassi and Josh Alman.
_Poly-attention: a general scheme for higher-order self-attention._**
ICLR 2026.
ArXiv **VERIFIED**: [2602.02422](https://arxiv.org/abs/2602.02422);
[conference paper](https://openreview.net/pdf?id=amivrmQyvQ).
**Does:** Defines a broad polynomial-score family of higher-order attention and proves
computational/representational bounds, including efficient fixed-length function
composition mechanisms.
**Overlap/difference:** “Attention beyond pairwise relations” and native composition
are already central there; their Definition 2.2 uses exponential polynomial scores and
Hadamard-composed values, whereas ours reads ordered matrix-product coefficients.
The distinct formulas do not establish a formal noncontainment in their broad framework.

## 6. Set functions and equivariance

**[E1] Manzil Zaheer, Satwik Kottur, Siamak Ravanbakhsh, Barnabas Poczos, Ruslan
Salakhutdinov and Alexander Smola. _Deep Sets._**
NeurIPS 2017.
ArXiv **VERIFIED**: [1703.06114](https://arxiv.org/abs/1703.06114).
**Does:** Characterizes and constructs permutation-invariant/equivariant functions through
shared feature maps and pooling under its stated domain assumptions.
**Overlap/difference:** Losing order through symmetric pooling is established; our
contribution is a task-specific balanced-accuracy ceiling and comparison with a
noncommutative sequence statistic.

**[E2] Ryan L. Murphy, Balasubramaniam Srinivasan, Vinayak Rao and Bruno Ribeiro.
_Janossy Pooling: Learning Deep Permutation-Invariant Functions for Variable-Size Inputs._**
ICLR 2019; first preprint 2018.
ArXiv **VERIFIED**: [1811.01900](https://arxiv.org/abs/1811.01900).
**Does:** Builds invariant functions by averaging order-sensitive functions over
permutations, with tractable approximations including k-ary interactions.
**Overlap/difference:** It explicitly removes ordering, whereas our ordered products
preserve the observed subsequence order; both make clear that arity and order sensitivity
are independent choices.

**[E3] Taco S. Cohen and Max Welling. _Group Equivariant Convolutional Networks._**
ICML 2016.
ArXiv **VERIFIED**: [1602.07576](https://arxiv.org/abs/1602.07576).
**Does:** Encodes known group actions through convolution and weight sharing to obtain
equivariance.
**Overlap/difference:** Using groups in network design is established, but learning a
token-to-matrix composition map is not itself a proof of equivariance to a specified
input group action.

**[E4] Risi Kondor and Shubhendu Trivedi.
_On the Generalization of Equivariance and Convolution in Neural Networks to the Action
of Compact Groups._**
ICML 2018.
ArXiv **VERIFIED**: [1802.03690](https://arxiv.org/abs/1802.03690).
**Does:** Relates compact-group equivariance to generalized convolution using
representation theory.
**Overlap/difference:** The representation-theoretic language is shared, but our main
claim concerns the information retained by a compositional statistic, not a new
characterization of equivariant networks.

## 7. Local regression attention and MesaNet

**[L1] Yifei Zuo, Yutong Yin, Zhichen Zeng, Ang Li, Banghua Zhu and Zhaoran Wang.
_Local Linear Attention: An Optimal Interpolation of Linear and Softmax Attention For
Test-Time Regression._**
ArXiv preprint, 2025.
ArXiv **VERIFIED**: [2510.01450](https://arxiv.org/abs/2510.01450).
**Does:** Replaces local constant attention regression with a local linear estimator and
develops theory and efficient implementation.
**Overlap/difference:** The local-regression mechanism in `LOCAL.md` is prior art; our
determinantal subset interpretation is a separate algebraic observation and does not
make LLA our invention or directly establish the group-composition claims.

**[L2] Yifei Zuo, Dhruv Pai, Zhichen Zeng, Alec Dewulf, Shuming Hu and Zhaoran Wang.
_Parallax: Parameterized Local Linear Attention for Language Modeling._**
ArXiv preprint, 2026.
ArXiv **VERIFIED**: [2605.29157](https://arxiv.org/abs/2605.29157).
**Does:** Replaces the LLA solve with a learned covariance probe and evaluates it at
language-model scale with architecture/optimizer ablations.
**Overlap/difference:** Our small language gain is explicitly a replication of this
prior mechanism; its covariance correction is not an ordered finite-group product
readout.

**[L3] Johannes von Oswald, Nino Scherrer, Seijin Kobayashi, Luca Versari, Songlin Yang,
Sarthak Mittal, Maximilian Schlegel, Kaitlin Maile, Yanick Schimpf, Oliver Sieberling,
Alexander Meulemans, Rif A. Saurous, Guillaume Lajoie, Charlotte Frenkel, Razvan Pascanu,
Blaise Agüera y Arcas and João Sacramento.
_MesaNet: Sequence Modeling by Locally Optimal Test-Time Training._**
ICLR 2026; first preprint 2025.
ArXiv **VERIFIED**: [2506.05233](https://arxiv.org/abs/2506.05233).
**Does:** Builds sequence layers by solving in-context regression objectives to
optimality, using numerically stable chunkwise computation.
**Overlap/difference:** Matrix state and test-time regression are prior art, but this
regression memory has a different defining operation from the gated ordered-subset
matrix polynomial.

## 8. Word-problem complexity: citations and limits

**[C1] David A. Barrington.
_Bounded-width polynomial-size branching programs recognize exactly those languages
in NC¹._**
Journal of Computer and System Sciences 38(1):150–164, 1989; conference precursor STOC 1986.
ArXiv: no identifier located; **VERIFIED**
[publisher](https://www.sciencedirect.com/science/article/pii/0022000089900378) and
[author-hosted full text](https://people.cs.umass.edu/~barring/publications/bwbp.pdf).
**Does:** Proves the width-five branching-program characterization of \(NC^1\) and
relates it to finite-group product problems.
**Overlap/difference:** The hardness of appropriate non-solvable finite-group word
problems is classical; evaluating a full-arity holonomy sector supplies their sequential
product primitive rather than a new shallow-threshold-circuit simulation.

**[C2] David A. Mix Barrington and Denis Thérien.
_Finite monoids and the fine structure of NC¹._**
Journal of the ACM 35(4):941–952, 1988.
ArXiv: no identifier located; bibliographic identity **VERIFIED** through
[ACM DOI 10.1145/48014.63138](https://doi.org/10.1145/48014.63138) and the
[JACM bibliography hosted by MIT](https://projects.csail.mit.edu/jacm/References/barringtont1988%3A941.html).
**Does:** Relates algebraic properties of finite monoids/groups to small-depth circuit
classes, including the role of solvable groups in modular-counting circuits.
**Overlap/difference:** The solvable/non-solvable complexity distinction predates this
work and differs from the commutative/noncommutative distinction tested by A4 versus A5.

**[C3] William Merrill and Ashish Sabharwal.
_The Parallelism Tradeoff: Limitations of Log-Precision Transformers._**
Transactions of the Association for Computational Linguistics, 2023; first preprint 2022.
ArXiv **VERIFIED**: [2207.00729](https://arxiv.org/abs/2207.00729).
**Does:** Simulates the specified log-precision transformer family with constant-depth
uniform threshold circuits.
**Overlap/difference:** This is an asymptotic resource-sensitive upper bound, not a
proof that a fixed-length softmax layer with sufficiently many features and an MLP
cannot classify our finite input domain.

**[C4] William Merrill and Ashish Sabharwal.
_A Logic for Expressing Log-Precision Transformers._**
NeurIPS 2023; first preprint 2022.
ArXiv **VERIFIED**: [2210.02671](https://arxiv.org/abs/2210.02671).
**Does:** Gives a logical characterization/upper-bound description of log-precision
transformers using majority quantification.
**Overlap/difference:** It sharpens the computational model relevant to asymptotic
comparisons; the gates, head count, readout size, precision and arithmetic depth of
our construction must be stated before such comparisons apply.

The safe positioning is: fixed solvable-group word problems admit the classical
\(ACC^0\subseteq TC^0\) upper bounds; fixed non-solvable examples such as A5 and S5
have \(NC^1\)-complete word problems under the appropriate reductions. A separation
from \(TC^0\) therefore uses an unproved complexity assumption. A4 is nonabelian but
solvable, so noncommutativity alone is not the \(NC^1\) boundary. The matrix prefix
scan takes sequential or logarithmic-depth composition work inside the nominal
“one layer”; layer count is not Boolean-circuit depth.

## 9. Novelty statement

The table distinguishes a result we can present from a broader statement we cannot.
For mathematical assumptions and constructions, the authority is [THEORY.md](THEORY.md).
For measurements and their limitations, it is [GROUPS.md](GROUPS.md) and the linked raw
results, not this literature audit.

| Claim | Status for this project | Closest single prior work and precise boundary |
|---|---|---|
| Ordered products summed over every distinct-index subsequence, separated by arity | **Not ours as a construction.** Our matrix polynomial is a specialization/compression. | **Seq2Tens [S7]**, equation (7), already has the full ordered-subsequence tensor sum. |
| Learned compact Lie-group products encode sequence order | **Not ours.** | **Path Development Networks [S8]**, equation (1), already learns matrix development; our proper-subset sectors are different from its full product. |
| A gated matrix implementation with a separate product-sum for each arity and each position contained in a subset | **Candidate architectural contribution, narrowly stated.** The audit found no exact prior instance. | **Seq2Tens [S7]** provides the underlying feature map; the marked-factor readout and constrained matrix parameterization are the concrete differences, with [S12] still requiring a full-text check. |
| An order-blind balanced-accuracy ceiling for ordered Match-k, plus the A4/A5 comparison | **Task-specific result here.** The Bayes decision principle and permutation-invariance obstruction are standard. | **Deep Sets [E1]** is the closest invariance framework; the label distribution, conditional probabilities and numerical ceiling audit are particular to this task. |
| A faithful representation supports exact identity detection after suitable gated selection | **Task-specific constructive application here, under explicit gate and readout assumptions.** Faithfulness itself is a standard definition, and this is not a universal necessary dimension threshold. | **Path Development Networks [S8]** is closest for matrix representation of composition; its result does not supply this ordered-subset identity classifier and explicit head construction. |
| Heads learn finite-group representations from labels | **Not new in general; new evidence in this operator/task setting.** Approximate homomorphism diagnostics do not certify exact representations. | **Chughtai–Chan–Nanda [G1]** already reverse engineers learned group-representation algorithms. |
| The chosen composition algebra affects what a sequence model retains and learns | **Not a new general principle.** The present contribution is a precise restricted instance and its measured behavior. | **Seq2Tens [S7]** explicitly motivates its algebra by noncommutative order structure; [S9] further analyzes this for selective SSMs. |
| Larger noncommutative matrix families help finite-group state tracking | **Prior art; any new benchmark is a comparative test, not the first demonstration.** | **DeltaProduct [R10]** directly studies this connection with group-word experiments. |
| Softmax cannot compose, or character features cannot suffice | **Withdraw as a capacity claim.** Report the specific optimization failure and use fixed-domain constructions to distinguish it from expressibility. | **Nanda et al. [G2]** directly demonstrates a learned Fourier composition circuit in a transformer. |
| A one-layer full-product result defeats known transformer \(TC^0\) bounds | **Not claimed.** Internal scan depth, arity, width and precision matter. | **Merrill–Petty–Sabharwal [R5]** distinguishes the restricted SSM computations whose circuit bounds actually apply. |
| A language-model improvement from the group mechanism | **Not established.** The earlier language outcomes remain negative for the proposed higher-order mechanisms. | **Parallax [L2]** is the source of the small replicated local-regression gain, and **Roy et al. [H3]** supplies separate positive higher-order language evidence. |

A suitable paper-level claim is: **We study a gated matrix realization of ordered
subsequence features, with per-position, per-arity relational readouts. On finite-group
identity-subset tasks, we derive the exact information limit of order-blind statistics,
give a constructive sufficient representation under stated selection assumptions, and
measure how learned rotation heads cross that information limit and acquire approximate
group structure.** This claim credits the signature/development lineage, leaves
optimization separate from representation, and does not depend on an unverified
first-of-its-kind assertion.
