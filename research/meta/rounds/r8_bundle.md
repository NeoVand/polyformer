**Objects:** camera poses \(C_i\); landmarks \(X_j\); reprojection factors \(r_{ij}(C_i,X_j)\).

**Techniques:** Schur-complement landmark elimination; Bayes-tree incremental elimination; gauge fixing and observability analysis.

**HIT: a Nerode state is an elimination message across a separator.** Partition historical variables into interior \(I\) and boundary \(B\), where every permitted future factor touches history only through \(B\). Define
\[
m_h(B)=\min_I E_h(I,B).
\]
Every future optimization has value \(\min_B[m_h(B)+F(B)]\). Thus equal messages imply indistinguishable futures; conversely, if future probes can clamp every boundary assignment, unequal messages are distinguishable. Quotient additive constants only when outputs ignore absolute objective values, and fix the geometric gauge.

In linearized Gaussian bundle adjustment, the message is exactly a Schur-complement quadratic. In nonlinear or ambiguous-association problems, a single quadratic generally loses future distinctions. The useful transfer is **preserve the boundary response function**, not merely the current best reconstruction.

**To the problem.** Each row gives state / rule / check / search and the transferred technique.

| Problem | Bundle-adjustment mapping |
|---|---|
| P1 representation | Joint landmark hypotheses / common geometric consistency / joint residual / candidate tracks: elimination exposes interactions. |
| P2 learning | Boundary message / absorb observations / held-out boundary clamps / maximally distinguishing clamps: observability-guided supervision. |
| P3 memory | Separator factors / eliminate interior / future-objective agreement / elimination ordering: Schur compression, bounded by separator complexity. |
| P4 retrieval | Message signature / substitute equivalent histories / probe agreement / signature matching: retrieve by future geometric effects. |
| P5 language | Unresolved entities as boundary / accumulate constraints / hypothetical continuations / discriminating questions: **FRAME**, not established transfer. |
| P6 verification | Reduced quadratic / Schur elimination / residual and rank checks / nullspace search: **TOOL**, exact only for the fixed quadratic problem. |
| P7 capability | Ambiguous track state / defer commitment / later-view consistency / association search: retain alternatives through long distraction. |
| P8 test | Discrete landmark hypotheses / exact elimination / exhaustive continuation probes / adversarial observations: small falsifiable benchmark. |

**From the problem.** Nerode equivalence is relative to allowed future measurements: discarding an old pose is safe only if future loop closures cannot address it independently. Higher-order terms belong especially to association ambiguity; Gaussian elimination creates dense couplings but remains quadratic, so clique size alone does **not** justify higher-order attention.

**Proposal: separator-memory attention for ambiguous tracks.** Use discretized bundle adjustment with three landmark hypotheses and observations admitting sets \(\{a,b\},\{b,c\},\{a,c\}\): every pair is feasible, but the triple is impossible. Over inclusion bits, infeasibility is \(x_1x_2x_3\), an exact cubic interaction; train cubic attention to update separator memory using exhaustive future-clamp targets. This joins binding with future-equivalence supervision while keeping certificates confined to evaluation.

Train on 32 observations; test 1,024 with 95% irrelevant observations. Kill the proposal if joint training achieves under 99% continuation accuracy or gains under five percentage points over matched-compute pairwise and either-component ablations; include exact set intersection as an oracle.

Closest prior art: [Square Root SAM (2006)](https://www.cs.cmu.edu/~kaess/pub/Dellaert06ijrr.pdf), [iSAM2 (2012)](https://www.cs.cmu.edu/~kaess/pub/Kaess12ijrr.pdf).