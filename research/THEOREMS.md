# Theorems and proofs

Every theorem the paper and its Supplementary Information (SI) use, and the research-note theorems
they draw on or may use. Each entry gives the statement, its assumptions, a human proof, the source
(file, label, commit) and a status. Where a statement is formalised, the entry also says how the
Lean statement corresponds to it. Gaps and errors are flagged in place and collected in Part III.
Part V lists the decisions that are Neo's. Part VI covers v2 of the paper, the pinned executor (an
LLM writes a literal transition table and a clock runs it with the table pinned, under a
per-question certificate): Theorem P, the Theorem 8(a) counterexample, the lookup lemma,
composition (Theorem C), registers, the bounded-window pointer, the cache policy, robust cells, and
the correctness of the 200-row adder and subtracter tables.

## Sources and commits

| Source | Commit read | Note |
|---|---|---|
| Paper `paper/jewel/main.tex`, `si.tex` (branch `paper`) | **`e4d3a557`** (HEAD, 27 Oct) | The brief cites `60c538a1`. The statements changed in `8c21003e` ("round 3 and the reframe"): Proposition 3 and Lemma 2 were removed, Corollary 1 was added, and Theorems 1(c) and 2 were restated. The earlier versions (`60c538a1`, `bb7003e4`) are covered in §I.9. |
| UNIFY `unify-85e792/research/UNIFY.md` | `ab7236b9` | UNIFY.md last changed at `252a6f87` |
| THEORY4 `theory4/research/theory4/THEORY4.md` | `7f334584` | |
| LEAP `leap/research/leap/LEAP.md` | `6b488853` (brief); HEAD `d5349805` | LEAP.md last changed at `d5349805`. That commit changed only the results from line 1359 on; the lettered statements are as at `2e8d8674` |
| MULTI `multi/research/multi/MULTI.md` | `d6cc16b9` | |
| INTERP `interp/research/interp/INTERP.md`, `interp_run.py`, `test_interp.py` | `52a9f521` | HEAD is `07ccf3f9`; INTERP.md is unchanged. The code was read at `07ccf3f9`. For Part VI, INTERP.md was re-read at `interp` HEAD `082e06c6` (INTERP.md last changed at `52a9f521`) |
| DEMO_DESIGN `demodesign/research/DEMO_DESIGN.md` (Part VI) | `9c6bbf84` | §5.1 Theorem P (line 353), §5.2 Theorem 8 (line 432), §5.3 Lemma Q (line 454), §8.1 the critiques' math (line 536) |
| ARITH_FORMAT `arith/research/arith/ARITH_FORMAT.md` (Part VI) | `a0d03c80` | §4 the block and the tick, §5 the certificate, §8 Theorem P for the Mealy block, §10 the forward-2 amendment |

Line numbers below are at `e4d3a557` unless stated otherwise.

## Status words

- **Formalised.** Proved in Lean 4.35 with Mathlib in `research/lean`. No `sorry`. `#print axioms`
  shows only `propext`, `Classical.choice` and `Quot.sound`.
- **Formalised (corrected).** The Lean theorem proves a corrected version of the paper's wording.
  The entry says exactly what was corrected.
- **Proved on paper.** A complete proof is written here, but the result is not in Lean.
- **Refuted.** A counterexample is written here, and it is in Lean where marked.
- **Open.** Neither proved nor refuted. "Not a theorem" marks a sentence that is too imprecise to be
  proved or refuted as worded.

Lean state at the last commit on branch `lean-p`: `lake build` completes (3102 jobs).
`AxiomCheck.lean` has 182 `#print axioms` lines (88 for Parts I–II, 94 for Part VI), and every one
is standard. `research/lean/README.md` is a reader's guide with the build commands, the index and
the axiom report. There is no `sorry`,
`admit` or `axiom` in `Polyformer/`.

## Summary

| Item | Source (`e4d3a557`) | Status | Lean |
|---|---|---|---|
| Theorem 1(a), blindness | main `thm:blind`; SI `thm:si-blind` | formalised | `blindness` |
| Theorem 1(a), likelihood corollary | main §2; SI §1.2 | formalised | `likelihood_is_blind`, `fderiv_run_eq_tangentRun` |
| Theorem 1(b), readout | main `thm:blind`(b); SI §1.2 | formalised | `norm_gradient_readoutLoss_le`, `hessian_readoutLoss_le`, `tendstoUniformlyOn_readoutLoss`, `readoutLoss_bounds` |
| Theorem 1(c) = S3 (i)–(v) | main `thm:blind`(c); SI `thm:si-a` | formalised | `norm_run_sub_run_le`, `excess_loss_le`, `readout_correct_of_lt_margin`, `theoremA_sharp`, `theoremA_resolution` |
| S3, non-expansion cannot be dropped | SI after `thm:si-a` | formalised | `theoremA_false_without_nonexpansion` |
| Corollary 1, finite reads | main `cor:finite`; SI `cor:si-finite` | formalised | `finite_reads` |
| Main §2: "no such loss certifies exactness at every length" | main line 72 | **refuted** | `parity_enumeration`, `reachedPairs_congr` |
| Theorem 2, robust Myhill–Nerode | main `thm:rmn`; SI `thm:si-rmn` | formalised | `robustMyhillNerode_full` (also `_cells`, `_prefix`, `_ball`, `rmn_core`) |
| Theorem 2 has no converse | main `thm:rmn`; SI line 107 | formalised (on ℝ); proved on paper (on the circle) | `rmn_no_converse` |
| Theorem 2 at radius 0 and k = 1 | main line 78; SI line 107 | formalised (the injectivity remark is on paper) | `myhillNerode` |
| Lemma 1, split; the secant remark | main `lem:split`; SI `lem:si-split`, line 121 | formalised | `kick_split`, `kick_chord`, `kick_secant_le` |
| Growth along ψ | SI line 123 | formalised | `norm_wordMap_eq_prod_gain` |
| S5, enumeration | SI `thm:si-enum` | formalised (the operation count is on paper) | `trackerExact_iff`, `reachedPairsPos_eq`, `reachedPairs_eq`, `reachedPairs_subset` |
| S6, a certificate must read the readout | SI `thm:si-certblind` | formalised (corrected): false at the start state as worded | `certificate_reads_readout` |
| SI line 149: "a point certificate therefore costs at least one readout evaluation per reached state" | SI after `thm:si-certblind` | **does not follow** for the trained trackers (affine heads are not closed under local readout changes); proved on paper | — |
| S7, finite under perturbation forces a snap | SI `thm:si-finite` | formalised | `finite_perturbed_forces_snap` |
| S8, the clip | SI `thm:si-clip` | formalised | `clip_perturbed_eq`, `clip_perturbed_continuum`, `clip_robust_exact_iff` |
| S9, the certificate | SI `cor:si-certif` | formalised (one hypothesis unused, finite event set made explicit) | `clip_certificate` |
| S10, contract then snap | SI `prop:si-h` | formalised (corrected: "h a corner" dropped, Λ > 0 added) | `contract_snap_radius`, `contract_snap_trajectory` |
| Withdrawn from the paper in `8c21003e`: Proposition 3(a), 3(b), Lemma 2, the snap and zero-set claims | `60c538a1`/`bb7003e4` | refuted or corrected; see §I.9 | `Certify.lean`, `CertifyGeneric.lean`, `Transverse.lean`, `SnapCounter.lean`, `Kick.lean` |
| INTERP Theorem 1(i), (iii) | INTERP §3 | formalised | `regeneration`, `snapped_step_locally_constant`, `fderiv_eq_zero_of_finite_range` |
| INTERP Theorem 2(a)–(d) (factorised bound) and its corollary | INTERP §3 | formalised | `attn_factorises`, `margin_mul_eq`, `four_situations`, `factorised_bound`, `certified_tables_exact` |
| INTERP Theorem 2(d), role-split bound, as implemented in `_split_rows` | INTERP §3; `interp_run.py` | formalised (from the code; the prose description does not match it) | `split_bound`, `split_margin_gt`, `split_certified_tables_exact` |
| INTERP Theorem 2(e), symmetry corollary | INTERP §3 | not a theorem; under full renaming symmetry its hypothesis is unsatisfiable on INTERP's vocabulary | — |
| INTERP Theorem 3(a), (d) | INTERP §3 | formalised; in (d) the letter gap needs ‖K_L‖ | `homogeneous_size_law`, `homogeneous_exact`, `gapN_le`, `gapL_le`, `gaps_le_two_kappa` |
| INTERP Theorem 3(a), "the last term decides", "slope one" | INTERP §3 | **refuted** (on paper) | — |
| INTERP Theorem 3(c), "far smaller than the adversarial harm" | INTERP §3 | **refuted** for the residual tick at \(m=n\) (on paper) | — |
| INTERP Theorem 4(c), "only if" | INTERP §3 | **refuted** (on paper) | — |
| UNIFY Theorem 6.3 (transverse force, linear model) | UNIFY supplement | formalised in that model | `transverse_term_expectation`, `transverse_force`, `transverseRate_pos` |
| UNIFY U6 (snap forced at fixed σ) | UNIFY | refuted | `analytic_tracker_zero_kick_term` |
| **v2** Theorem P(1), information flow and the cache | DEMO_DESIGN §5.1; ARITH_FORMAT §4 | formalised (causal decoder, exact arithmetic) | `cache_sound`, `cachedForward_eq`, `prog_resid_fixed`, `block_first_blind`, `forward2_refeed_eq` |
| **v2** Theorem P(2), pinned regeneration, both directions | DEMO_DESIGN §5.1 | formalised (any closed set of rows; H2 not needed) | `pinned_regeneration`, `pinned_regeneration_table`, `pinned_certificate_necessary`, `pinned_regeneration_iff`, `pinned_regeneration_decoder` |
| **v2** Theorem P(3), each tick reproduces its certified row | DEMO_DESIGN §5.1; ARITH_FORMAT §8 | formalised | `tick_logits_eq_row`, `mealy_tick_logits_eq_row` |
| **v2** Corollary P2, margin `> 2τ` | DEMO_DESIGN §5.1 | formalised (the run's logits may also depend on the history) | `sel_eq_of_close`, `regeneration_of_close` |
| **v2** Theorem P for the Mealy block (two cells per row) | ARITH_FORMAT §8 | formalised | `pinned_regeneration_mealy`, `mealy_certificate_necessary`, `pinned_regeneration_mealy_table` |
| **v2** INTERP Theorem 8(a) for unpinned decoding | INTERP §3; DEMO_DESIGN §5.2 | **refuted** (both directions); true version formalised | `not_theorem8a`, `theorem8a_counterexample`, `no_finite_check`, `no_finite_test_suite`, `unpinned_exact_not_certified`, `unpinned_exact_of_close` |
| **v2** Lemma Q and the lookup lemma | DEMO_DESIGN §5.3, §8.1 | formalised (corrected draft refuted; `1/2` sharp) | `matched_weight_ge`, `lemmaQ`, `lemmaQ_argmax`, `lookup_argmax_half`, `half_lt_matched_weight`, `lookup_half_sharp`, `lemmaQ_without_Z0_false` |
| **v2** Theorem C, composition of certified calls; the error decomposition | INSIGHTS C; PAPER_V2_PLAN | formalised (terms read at the right inputs) | `compose_exact`, `error_decomposition`, `error_decomposition_certified`, `error_bound` |
| **v2** Corollary P3, registers (independent and cascades) | DEMO_DESIGN §5.1 | formalised | `registers_exact`, `registers_certificate_necessary`, `cascade_exact` |
| **v2** The pointer cannot live in a bounded window | BIGIDEA §2, §4.6; INSIGHTS 12 | formalised (corrected: a long stretch then a change, \(2m\ge k+2|S|\); no position ids) | `window_loses_place`, `window_determines`, `window_eventually_periodic` |
| **v2** The cache policy (sink, evict, restart positions) computes the pinned tick | BIGIDEA §4.5; INSIGHTS 12 | formalised (exact arithmetic) | `policy_tick_eq`, `policyRun_eq_pinned`, `policy_regeneration` |
| **v2** Robust cells | CIRCUITS; PAPER_V2_PLAN | formalised (Lipschitz constant assumed) | `robust_cell`, `robust_cell_radius`, `robust_run` |
| **v2** The 200-row adder computes `x + y`; certified, the clock does too, at every length | ARITH_FORMAT §1–§8 | formalised (rows checked by `decide`) | `adderRows_spec`, `adderRows_check`, `adder_correct`, `adder_table_correct`, `adder_clock_correct` |
| **v2** The 200-row subtracter: borrow 0 iff `y ≤ x`, then `x − y`; borrow 1 iff `x < y` | REASON_FORMAT §2 | formalised (rows checked by `decide`) | `subRows_spec`, `subRows_check`, `sub_correct`, `sub_clock_correct` |

---

# Part I. The paper and SI at `e4d3a557`

## I.0 Setting

From main `\subsection*{Statements}` (lines 174–179) and the SI header (line 38):

- **Views and trackers.** A view is a state after closure. Views lie on the centred unit sphere
  \(S\). A tracker acts by one map \(F_x\) per event \(x\), and \(F_w\) is the map of a word \(w\).
  The tracker is **closed** when every \(F_x\) sends views to views.
- **Readout.** Class codes \(c_1,\dots,c_C\in S\) have \(\sum_j c_j=0\). The readout loss at
  temperature \(\tau\) is \(\ell_\tau(z,y)=\tau(\mathrm{CE}(\langle z,c_\cdot\rangle/\tau,y)-\log C)\),
  and its error probability is \(s=1-p_y(z)\).
- **Automaton.** The task's minimal automaton has states \(q\), outputs \(o(q)\) and transitions
  \(q\cdot w\). Theorem 2 adds codes \(c_q\), radii \(r_q>0\), a block length \(k\ge1\) and a rate
  \(\lambda\in[0,1)\).
- **Distance.** \(d(a,b)=\frac12|a-b|^2\) is the centred cosine distance.

**Lean conventions** (`research/lean/STATUS.md`, "Modelling choices"):

- Views are the unit sphere of a real inner product space \(E\). This loses nothing: take \(E\) to
  be the centred subspace.
- A tracker is `F : X → E → E` with each `F x` of class \(C^n\) (\(n\ge1\)) on an open set
  containing the sphere and mapping the sphere into itself. `run F z₀ u` is the view after the
  word \(u\).
- An automaton is `PAutomaton X Q O`, with partial transitions (`step : Q → X → Option Q`) and
  outputs.
- A Jacobian at a view is the ambient derivative applied to tangent vectors \(c^\perp\).

## I.1 Theorem 1(a): blindness

**Source.** main `thm:blind`(a), lines 181–182; SI `thm:si-blind`, lines 42–52 (proof);
Methods "Proofs", line 245. UNIFY U3(a).

**Statement (SI).** Let a closed tracker's views on the training data take finitely many values.
For any linear maps between the tangent spaces at those views there is a smooth tracker, not
necessarily one the network family can represent, that agrees with it at every reached view and
has those maps as its Jacobians there. Every objective that reads the transition only through its
values at reached views takes the same value at both trackers.

**Precise form and assumptions.**

- **The data.** \(E\) is a finite-dimensional real inner product space and \(S\) its unit sphere.
  Each \(F_x\) is \(C^n\) (\(1\le n\le\infty\)) on an open \(U\supseteq S\), with
  \(F_x(S)\subseteq S\). \(T\) is a set of training words. The reached set \(R\) consists of the
  views \(F_{u'}(z_0)\) for prefixes \(u'\) of words in \(T\); it includes \(z_0\) and is finite.
- **The prescribed maps.** For every event \(x\) and \(c\in R\), \(M_{x,c}\) is a linear map from
  \(T_c=c^\perp\) to \(T_{F_x(c)}\).
- **The conclusion.** For every \(\delta>0\) there is a closed \(C^n\) tracker \(F'\) such that:
  1. \(F'_x(c)=F_x(c)\) for every \(c\in R\);
  2. \(DF'_x(c)v=M_{x,c}v\) for every \(v\in T_c\);
  3. \(F'_x=F_x\) at distance at least \(\delta\) from \(R\);
  4. \(F'\) and \(F\) have the same view on every prefix of every training word;
  5. every \(J\) that depends only on those views satisfies \(J(F')=J(F)\).

**Proof.**

1. **Separation.** Fix \(\varepsilon\le\delta\) below half the least distance between distinct
   points of \(R\). For \(c\in R\) let \(P_c\) be the orthogonal projection onto \(T_c\), and put
   \(L_{x,c}=(M_{x,c}-DF_x(c))\circ P_c\), a linear map on \(E\). On \(T_c\),
   \(L_{x,c}v=M_{x,c}v-DF_x(c)v\).
2. **Bumps.** Since \(|F_x(c)|=1\), continuity gives \(\rho\le\varepsilon\) such that, on the ball
   \(B(c,\rho)\), \(|F_x(z)|>1/2\) and \(\|L_{x,c}\|\,|z-c|<1/4\). Take smooth bumps
   \(\varphi_c\) equal to 1 on \(B(c,\rho/2)\) and supported in \(B(c,\rho)\). Their supports are
   disjoint. Put \(G_x(z)=F_x(z)+\sum_{c\in R}\varphi_c(z)L_{x,c}(z-c)\). On each support
   \(|G_x|>1/4\).
3. **Closure.** Put \(F'_x(z)=|F_x(z)|\,G_x(z)/|G_x(z)|\).
   - Off the supports \(G_x=F_x\), so \(F'_x=F_x\) on an open set; this gives item 3.
   - On each support both \(F_x\) and \(G_x\) are away from 0, where the norm is smooth, so \(F'_x\)
     is \(C^n\) on \(U\).
   - On \(S\), \(|F_x|=1\), so \(F'_x(z)=G_x(z)/|G_x(z)|\in S\). So \(F'\) is closed.
4. **Values.** At \(c\in R\), \(G_x(c)=F_x(c)\) (the added term vanishes at its centre and the
   other bumps vanish there), so \(F'_x(c)=F_x(c)\). This is item 1.
5. **Jacobians.** Since \(\varphi_c\equiv1\) near \(c\), \(DG_x(c)=DF_x(c)+L_{x,c}\).
   - The map \(N(a,g)=|a|\,g/|g|\), at \(a=g=F_x(c)=:e\) with \(|e|=1\), has derivative
     \((\dot a,\dot g)\mapsto\langle e,\dot a\rangle e+(I-ee^\top)\dot g\).
   - For \(v\in T_c\), \(DF_x(c)v\in T_e\), because \(|F_x|^2\equiv1\) along curves in \(S\). So
     \(\langle e,DF_x(c)v\rangle=0\).
   - Also \(DF_x(c)v+L_{x,c}v=M_{x,c}v\in T_e\).
   - Hence \(DF'_x(c)v=(I-ee^\top)M_{x,c}v=M_{x,c}v\). This is item 2.
6. **Training views.** Induct on the prefix length. The view before each event of a training prefix
   is in \(R\), and \(F'\) agrees with \(F\) there. This gives item 4, and item 5 follows. ∎

**Lean.** `Polyformer.blindness` (`Blindness.lean`). It matches the statement above item by item,
with `ReadsOnlyReachedViews J z₀ T` as the meaning of "reads the transition only through its values
at reached views". The tracker class is \(C^n\) on an open set containing the sphere, with
\(n=\infty\) meaning smooth. "Not necessarily one the network family can represent" is literally
true: \(F'\) is an arbitrary closed \(C^n\) map.

**Status.** Formalised.

**Notes.**

- The main text says "a tracker"; the SI says "a closed tracker". The proof needs the closure, or
  at least maps of views into views, so the SI's wording is the right one.
- The analytic (\(C^\omega\)) version is not formalised. A bump function is not analytic.
- Referee T1 (the theorem does not explain the failures) is answered by the current wording (main
  line 53): "The theorem does not say what gradient descent finds; it says the loss gives no reason
  to find contraction."

### I.1.1 The next-token-likelihood corollary

**Source.** main line 72 ("No objective on reached states constrains the Jacobians along a word"),
SI line 64.

**Statement (Lean form).** Take the \(F'\) of I.1.

1. For every finite sample of training words and every labelling, these take the same value at
   \(F\) and \(F'\):
   - the next-token loss \(\sum_k\sum_{t\le|h_k|}g(z(h_k[{:}t]),\mathrm{lab}_k(t))\), for every
     per-view loss \(g\) (the readout loss \(\ell_\tau\) at any temperature and codes included);
   - the certified-equivalence term \(\sum_p d(z(h_{p_1}),z(h_{p_2}))\), for every \(d\);
   - the next-state loss, for every predictor.
2. Along every reached path, the derivative of the word map on tangent vectors is the composition
   of the prescribed \(M\)s. So the error cocycle, and with it the Lyapunov exponents along reached
   paths, is whatever \(M\) prescribes.

**Proof.** Every quantity in item 1 is a function of the views on training prefixes (I.1, item 4).
For item 2, apply the chain rule. Each \(DF'_{x_i}(c_{i-1})\) maps \(T_{c_{i-1}}\) into
\(T_{c_i}\), because \(F'\) is closed. ∎

**Lean.** `likelihood_is_blind`, `readoutLikelihood_eq` and `fderiv_run_eq_tangentRun`
(`Likelihood.lean`). **Status.** Formalised.

**The identification of likelihood with the readout loss** (main line 72; SI line 64). If the head's
rows \(w_j\) have equal norm \(1/\tau\) and there is no bias, the logits are
\(\langle z,c_j\rangle/\tau\) with unit codes \(c_j=\tau w_j\). Then
\(\mathrm{CE}=\ell_\tau/\tau+\log C\), an increasing affine function of \(\ell_\tau\). With unequal
norms or a bias the identification fails, as the SI says.

The paper's readout is a layer norm followed by a linear head (Methods "Trackers"). On the centred
unit sphere of dimension \(d\), the layer norm is \(z\mapsto\gamma\odot\sqrt d\,z+\beta\), which is
affine. The identification therefore needs the *effective* rows \(\sqrt d\,(\gamma\odot w_j)\) to
have equal norm and the effective bias \(\langle\beta,w_j\rangle\) plus the head's bias to vanish.
The blindness corollary does not need any of this: it holds for every per-view loss.

## I.2 Theorem 1(b): the readout

**Source.** main `thm:blind`(b), line 183; Methods "Proofs"; SI line 64. UNIFY U2.

**Statement.** At every \(\tau>0\), \(\|\nabla_z\ell_\tau\|\le2s\) and
\(\nabla^2_z\ell_\tau\preceq(4s/\tau)I\). As \(\tau\to\infty\),
\(\ell_\tau(z,y)\to-\langle z,c_y\rangle\) uniformly.

**Assumptions.**

- The two bounds need codes with \(|c_j|\le1\) and \(\tau\ne0\) (respectively \(\tau>0\)).
- The limit needs, in addition, \(\sum_jc_j=0\) and \(|z|\le1\).
- "Uniformly" means over labels \(y\) and over \(z\) in the closed unit ball, which contains the
  views.

**Proof.** Write \(a_j=\langle z,c_j\rangle/\tau\) and \(p=\mathrm{softmax}(a)\). Then
\(\ell_\tau=\tau\log\sum_je^{a_j}-\langle z,c_y\rangle-\tau\log C\).

- **Gradient.** \(\nabla\ell_\tau=\sum_jp_jc_j-c_y=\sum_{j\ne y}p_j(c_j-c_y)\), since \(\sum p_j=1\).
  Its norm is at most \(\sum_{j\ne y}p_j\,|c_j-c_y|\le2\sum_{j\ne y}p_j=2s\).
- **Hessian.** \(\nabla^2\ell_\tau=\tau^{-1}\bigl(\sum_jp_jc_jc_j^\top-\bar c\bar c^\top\bigr)
  =\tau^{-1}\mathrm{Cov}_{J\sim p}(c_J)\), with \(\bar c=\sum_jp_jc_j\). This is \(\succeq0\).
  For a direction \(v\), \(\langle v,\mathrm{Cov}\,v\rangle=\mathrm{Var}\langle v,c_J\rangle\). A
  variance is at most the second moment about any point, here \(\langle v,c_y\rangle\), so it is at
  most \(\sum_{j\ne y}p_j\langle v,c_j-c_y\rangle^2\le4s|v|^2\).
- **Limit.** \(\ell_\tau+\langle z,c_y\rangle=\tau\log\bigl(\tfrac1C\sum_je^{a_j}\bigr)\).
  - Lower bound: by Jensen, \(\tfrac1C\sum_je^{a_j}\ge e^{\frac1C\sum_ja_j}=e^{0}=1\), using
    \(\sum_jc_j=0\).
  - Upper bound: \(|a_j|\le1/\tau\), and \(e^x\le1+x+\tfrac12x^2e^{|x|}\), so
    \(\tfrac1C\sum_je^{a_j}\le1+e^{1/\tau}/(2\tau^2)\). Then \(\log(1+u)\le u\) gives
    \(\tau\log(\dots)\le e^{1/\tau}/(2\tau)\).
  - So \(0\le\ell_\tau+\langle z,c_y\rangle\le e^{1/\tau}/(2\tau)\to0\) uniformly. ∎

**Lean.** `norm_gradient_readoutLoss_le` (\(\tau\ne0\), \(|c_j|\le1\)); `hessian_readoutLoss_le`
(\(0\le\langle\nabla^2\ell\,v,v\rangle\le(4s/\tau)|v|^2\), \(\tau>0\));
`tendstoUniformlyOn_readoutLoss` (\(\sum c=0\), \(|c_j|\le1\), uniform on
\(\{(y,z):|z|\le1\}\)); `readoutLoss_bounds` (the sandwich) (`Readout.lean`).

**Status.** Formalised.

**Notes.**

- The bounds do not need \(\sum c=0\); only the limit does.
- Referee T12 (this is textbook saturation) is acknowledged at SI line 64.
- Main line 72 adds that the error probability is something "training drives to its floor". That
  is an empirical gloss, not part of the theorem.
- **Fig. 2a caption** (main line 92): "at high temperature, where it tends to \(1-\cos\theta\)
  (computed exactly on a centred code)". By the theorem, \(\ell_\tau\to-\langle z,c_y\rangle=-\cos\theta\).
  \(1-\cos\theta\) is that limit minus its value at the code. The caption is right if the panel
  plots \(\ell_\tau\) relative to its value at the code, and off by 1 otherwise. Check the panel.

## I.3 Theorem 1(c) = SI Theorem S3: the excess loss

**Source.** main `thm:blind`(c), line 184; SI `thm:si-a`, lines 68–76, proof lines 78–86, remarks
lines 88 and 91; main line 72 (the ρ and γ sentences).

**Statement (SI).**

- **Hypotheses.**
  - The exact tracker has views \(z_t\) and the learned one has views \(\hat z_t\), from the same
    start.
  - Every learned event map \(\hat F_x\) is non-expansive on a set that contains every \(z_t\) and
    \(\hat z_t\).
  - \(\hat F_x\) misses the exact map by at most \(\varepsilon\) at exact views:
    \(|\hat F_x(z_t)-F_x(z_t)|\le\varepsilon\).
  - The logit vector is \(K\)-Lipschitz in the view (Euclidean norms).
  - \(m\) is the exact tracker's smallest logit margin, and \(\bar s\) is its mean error
    probability over the loss's positions \(t\le L\).
- **Conclusions.**
  1. (i) \(|\hat z_t-z_t|\le\varepsilon t\).
  2. (ii) The mean cross-entropy over those positions exceeds the exact tracker's by at most
     \(\bar s(e^{\sqrt2K\varepsilon L}-1)\).
  3. (iii) The readout is right at every \(t\le N\) when \(\sqrt2K\varepsilon N<m\).
  4. (iv) The constant is sharp: some non-expansive transition with miss \(\varepsilon\) fails at
     every \(N>m/(\sqrt2K\varepsilon)\).
  5. (v) For a loss resolved to \(\rho\), the transition of (iv) with
     \(\varepsilon=\log(1+\rho/\bar s)/(\sqrt2KL)\) lies within \(\rho\) of the exact loss and fails
     at every \(N>mL/\log(1+\rho/\bar s)\).

**Proof.**

- **(i)** \(|\hat z_{t+1}-z_{t+1}|\le|\hat F(\hat z_t)-\hat F(z_t)|+|\hat F(z_t)-F(z_t)|
  \le|\hat z_t-z_t|+\varepsilon\). Both \(\hat z_t\) and \(z_t\) lie in the non-expansion set.
  Induct.
- **(ii)** Write \(\Delta\ell=\ell(\hat z_t)-\ell(z_t)\). For a wrong label \(j\):
  - the gap changes by at most \(|\Delta\ell_j-\Delta\ell_y|\le\sqrt2|\Delta\ell|_2\), using
    \(|a-b|\le\sqrt{2(a^2+b^2)}\);
  - and \(\sqrt2|\Delta\ell|_2\le\sqrt2K|\hat z_t-z_t|\le a_t:=\sqrt2K\varepsilon t\).

  Write \(\mathrm{CE}=\log(1+S)\) with \(S=\sum_{j\ne y}e^{\ell_j-\ell_y}\). Each term of \(S\) grows
  by at most \(e^{a_t}\). So
  \[\widehat{\mathrm{CE}}-\mathrm{CE}\le\log\frac{1+e^{a_t}S}{1+S}=\log(1+s_t(e^{a_t}-1))\le s_t(e^{a_t}-1),\]
  where \(s_t=S/(1+S)\). Averaging with non-negative weights over positions \(t\le L\), and using
  \(a_t\le a_L\), gives \(\bar s(e^{a_L}-1)\).
- **(iii)** Every gap starts at least \(m\) and falls by at most \(a_N<m\).
- **(iv)** On \(\mathbb R\), take logits \((m/2-Kx/\sqrt2,\,-m/2+Kx/\sqrt2)\). They are \(K\)-Lipschitz
  and their gap is \(m-\sqrt2Kx\). The exact view stays at 0. The learned map \(x\mapsto x+\varepsilon\)
  is an isometry missing by \(\varepsilon\). After \(N\) events the gap is \(m-\sqrt2K\varepsilon N\),
  negative exactly when \(N>m/(\sqrt2K\varepsilon)\).
- **(v)** In that model \(\bar s=1/(1+e^m)\) at every position. With the given \(\varepsilon\),
  (ii) gives an excess of at most \(\bar s(e^{\log(1+\rho/\bar s)}-1)=\rho\), and (iv) gives failure
  at every \(N>m/(\sqrt2K\varepsilon)=mL/\log(1+\rho/\bar s)\). ∎

**The γ remark** (SI line 88; main line 72). A non-expansive drift whose margin falls by
\(\gamma^{-1}\sqrt2K\varepsilon\) per event has margin \(m-\gamma^{-1}\sqrt2K\varepsilon N\). That
is negative only for \(N>\gamma m/(\sqrt2K\varepsilon)\). **Proved on paper** (one line).

**Non-expansion cannot be dropped** (SI line 88). Take the exact view fixed at 0 and the learned map
\(x\mapsto2x+\varepsilon\). The miss is \(\varepsilon\) and the error after \(t\) events is
\(\varepsilon(2^t-1)\), so (i) fails for \(t\ge2\). The Lean instance is
\(m=1\), \(K=\sqrt2\), \(\varepsilon=1/25\), \(N=10\):

- \(\sqrt2K\varepsilon N=4/5<m\), yet the readout is wrong after 10 events: the error is
  \(1023/25\) and the gap is \(1-2\cdot1023/25<0\). So (iii) fails.
- (ii) fails too (computed, not in Lean). The bound at \(L=10\) is
  \(\bar s(e^{0.8}-1)\approx0.330\) with \(\bar s=1/(1+e)\). The actual excess cross-entropy,
  averaged over positions \(t=1,\dots,10\), is about \(15.4\).

**Lean** (`ExcessLoss.lean`). The hypotheses are bundled in `TheoremAHyp`:

- every exact and every learned view lies in \(V\);
- each `Fh x` is 1-Lipschitz on \(V\);
- the miss is at most \(\varepsilon\) at every exact view;
- the logits are \(K\)-Lipschitz from the view norm to the Euclidean norm.

| Clause | Lean theorem | Form |
|---|---|---|
| (i) | `norm_run_sub_run_le` | |
| (ii) | `excess_loss_le` | any non-negative weights over positions of length at most \(L\); `excess_crossEntropy_le` per position; `crossEntropy_add_sub_le`, `abs_sub_le_sqrt_two_mul_l2` for the two steps |
| (iii) | `readout_correct_of_lt_margin` | |
| (iv) | `theoremA_sharp` | drift model \(z\mapsto z-\varepsilon\), mirror image of the SI's |
| (v) | `theoremA_resolution` | |
| non-expansion needed | `theoremA_false_without_nonexpansion` | |

The views may live in any normed space.

**Status.** Formalised, with the paper's own hypotheses. Since `e1bacb65` the Lean hypothesis is
exactly "a set that contains every \(z_t\) and \(\hat z_t\)"; before, it was a stronger invariance
assumption.

**Notes.**

- Referee T3 has been resolved by the current statement. Non-expansion is stated; \(K\), \(m\) and
  \(\bar s\) are defined; the strict \(N>\) is used; and the failing construction is a drift in
  state space.
- SI line 91 ("The bound is what the loss can see …") is interpretation, and correctly labelled.

## I.4 Corollary 1: finite reads

**Source.** main `cor:finite`, lines 187–189; SI `cor:si-finite`, lines 54–56, proof lines 58–60;
Methods "Proofs".

**Statement (SI).** Let an objective read values, and finitely many derivatives, of the transition at
finitely many points, possibly chosen from what it has already read. For any closed tracker with at
least two readout cells, any radii \(r_q\), any event \(x\) and any point \(h\) of a ball
\(B(c_q,r_q)\) that the objective does not read, there is a smooth closed tracker with the same
objective value whose map \(F_x\) sends \(h\) out of the readout cell of \(o(q\cdot x)\).
Reached-state objectives and F are such objectives, so none of them certifies (C_r) for given radii.

**Precise form.** "Reads at finitely many points, possibly adaptively" is modelled as follows.

- A map \(G\mapsto P(G)\) gives the read points, with \(P(F)\) finite.
- Whenever \(G'\) equals \(G\) near every point of \(P(G)\), \(J(G')=J(G)\). An adaptive procedure
  then reads the same points and the same values.
- Values and derivatives of finite order at those points are determined by the germs there, so
  this covers the paper's class.

**Proof.**

1. **A target view.** The readout takes two values on views, so some view \(u\) has a readout
   different from \(o(q\cdot x)\).
2. **Room around \(h\).** \(h\notin P(F)\) and \(P(F)\) is finite, so
   \(\varepsilon=\min_{p\in P(F)}|p-h|>0\).
3. **Moving one value.** Assume first \(u\ne-F_x(h)\).
   - Put \(a=F_x(h)\) and \(\kappa=\sqrt{(1+\langle a,u\rangle)/2}>0\).
   - For every real \(t\), \(|(1-t)a+tu|^2=1-2t(1-t)(1-\langle a,u\rangle)\ge\kappa^2\).
   - Choose a bump \(\varphi\) at \(h\) of radius at most \(\varepsilon/2\), small enough that
     \(|F_x(z)-a|<\kappa\) on its support.
   - Put \(f'(z)=|F_x(z)|\,N\bigl(F_x(z)+\varphi(z)(u-a)\bigr)\), where \(N\) normalises. The
     argument of \(N\) is \(((1-\varphi)a+\varphi u)+(F_x(z)-a)\), of norm greater than 0, so
     \(f'\) is \(C^n\), closed, equal to \(F_x\) outside \(B(h,\varepsilon/2)\), and \(f'(h)=u\).
   - If \(u=-a\), move twice: first to a unit \(m\perp a\), then to \(u\). This needs
     \(\dim E\ge2\).
4. **Same objective.** \(F'\) (\(F\) with \(F_x\) replaced by \(f'\)) equals \(F\) on the open set
   \(\{|z-h|>\varepsilon/2\}\). That set is a neighbourhood of every read point, so
   \(J(F')=J(F)\). And \(F'_x(h)=u\) is out of the readout cell of \(o(q\cdot x)\).
5. **The examples.** For F, take \(P(G)\) to be the reached views on training prefixes, the two
   perturbed views per history, and the partner views.
   - Equal germs there give the same reached views (by induction), the same Jacobians at reached
     views, hence the same \(\psi\) (power iteration of the closed tangent map along the past),
     the same perturbed views and the same values at them.
   - So F is such an objective. Reached-state objectives are the case where \(P\) is the reached
     views.
6. **No certificate of (C_r).** Let \(F\) satisfy (O_r) and (C_r) for given radii. Pick any \(q\),
   an \(x\) applicable at \(q\), and a view \(h\in B(c_q,r_q)\setminus P(F)\). Such an \(h\)
   exists: the ball holds infinitely many views when \(\dim E\ge2\).
   - If \(k\ge2\), \(F'\) violates the cell clause of (C_r).
   - If \(k=1\), (O_r) puts \(B(c_{q\cdot x},\lambda r_{q\cdot x})\) inside that cell, so \(F'\)
     violates the ball clause.
   - In both cases the objective takes the same value at a tracker satisfying (C_r) and at one
     violating it. ∎

**Lean.** `finite_reads` (`CertifyGeneric.lean`), with the adaptive form
`ReadsOnlyGermsAdaptive J P`.

- **Hypotheses:** views of dimension at least 2; the readout takes two values on views; `F` is
  closed and \(C^n\); \(P(F)\) is finite; `h` is an unread view.
- **Conclusion:** a closed \(C^n\) `F'` with `J F' = J F` and
  `readout (F' x h) ≠ A.out q'`.
- The paper takes \(h\) in a ball \(B(c_q,r_q)\). The Lean theorem allows any unread view, which is
  stronger.
- Item 5 (F is such an objective) is a modelling statement, checked here by inspection, not in Lean.

**Status.** Formalised.

**Notes.** In dimension 1 the sphere is \(\{\pm1\}\). The only other view is antipodal, and the
normalised construction is not needed. The paper's views are high-dimensional, so nothing changes.

### I.4.1 Error: "no such loss certifies exactness at every length" (main line 72)

**Sentence.** "The argument covers any objective that reads the transition at finitely many points
and to finite order (Corollary 1), certified equivalence and our own perturbation term included: no
such loss certifies exactness at every length."

**Status.** **Refuted as worded.**

**Counterexample.** The SI's own enumeration (S5) is such an objective and certifies exactness.

- **The objective.** Put \(V(F)\) = "\(P(F)\) is finite and the readout is right on \(P^+(F)\)".
- **It is sound.** \(V(F)\) implies exactness (S5).
- **It reads finitely many values.** If \(G\) agrees with \(F\) at every reached view, the two have
  the same reached pairs, so \(V(G)=V(F)\). The reads are adaptive, and finitely many whenever \(V\)
  certifies.
- **It certifies an exact tracker.** The parity tracker \(z\mapsto-z\) with the sign readout reaches
  two pairs, and \(V\) certifies it.

**Lean.** `reachedPairs_congr`, `trackerExact_iff`, `parity_enumeration` (`Snap.lean`).

**What is true.**

- The Corollary's own conclusion: no such objective certifies (C_r) for given radii.
- For exactness, a version restricted to unread reached views: if the tracker reaches a view the
  objective does not read, an objective with the same value is attained by a tracker that is not
  exact. This is `germ_objective_cannot_certify` and `exists_tracker_failing_rmn` for fixed
  \(P\). The adaptive case follows from the same construction, because the modified tracker
  equals \(F\) near \(P(F)\).

## I.5 Theorem 2: robust Myhill–Nerode

**Source.** main `thm:rmn`, lines 191–197; SI `thm:si-rmn`, lines 95–101, proof lines 103–105,
remark line 107; main line 78.

**Statement (SI).**

- **Data.** Let a closed tracker act by \(F_x\), with codes \(c_q\), radii \(r_q>0\), a block length
  \(k\ge1\) and a rate \(\lambda\in[0,1)\).
- **Hypotheses.**
  - (O_r) Every ball \(B(c_q,r_q)\) lies in the readout cell of \(o(q)\).
  - (C_r) For every state \(q\) and applicable word \(w\), \(F_w(B(c_q,r_q))\) lies in the readout
    cell of \(o(q\cdot w)\) if \(|w|<k\), and in \(B(c_{q\cdot w},\lambda r_{q\cdot w})\) if
    \(|w|=k\).
  - (E_r) For some prefix length \(p\ge0\), the readout is right on every word shorter than \(p\),
    and the view reached by every word \(u\) of length \(p\) lies in
    \(B(c_{q_0\cdot u},r_{q_0\cdot u})\).
- **Conclusions.** The readout is exact on every input at every length. If, after the prefix, the
  view is moved by at most \((1-\lambda)\min_qr_q\) at each block boundary and stays a view, the
  readout is still exact.

**Proof.** Let \(u\) be applicable with \(q_0\cdot u=q\).

1. **Short words.** If \(|u|<p\), the readout is right by (E_r).
2. **The blocks.** Otherwise write \(u=u_0v\) with \(|u_0|=p\), and cut \(v\) into blocks
   \(w_1,\dots,w_j\) of length \(k\) followed by a part \(v'\) with \(|v'|<k\). Let \(z_i\) be the
   view at the \(i\)-th boundary and \(q_i\) its state.
3. **Induction over boundaries.** \(z_0\in B(c_{q_0\cdot u_0},r)\) by (E_r). If
   \(z_i\in B(c_{q_i},r_{q_i})\), then by (C_r) with \(|w|=k\),
   \(z_{i+1}=F_{w_{i+1}}(z_i)\in B(c_{q_{i+1}},\lambda r_{q_{i+1}})\subseteq B(c_{q_{i+1}},r_{q_{i+1}})\).
4. **The last part.** \(z(u)=F_{v'}(z_j)\) is in the readout cell of \(o(q_j\cdot v')=o(q)\), by
   (C_r) with \(|w|<k\). For \(v'\) empty this is (O_r).
5. **Perturbations.** At a boundary the unperturbed image lies in
   \(B(c_{q'},\lambda r_{q'})\). A move of at most \((1-\lambda)r_{q'}\) keeps it in
   \(B(c_{q'},r_{q'})\) by the triangle inequality. The same induction then applies. ∎

**Lean** (`RobustMN.lean`). `robustMyhillNerode_full` is this statement with closed balls:

- (C_r) in the cell form inside blocks and the ball form at block ends;
- (E_r) with prefix \(p\);
- exactness on every applicable input;
- absorption, along any trajectory that equals the run up to \(p\), follows the tracker inside the
  later blocks, and moves by at most \(\delta\le(1-\lambda)r_q\) (for every \(q\)) at block
  boundaries after \(p\). The perturbation may depend on the whole history.

It needs only \(r_q\ge0\) and \(\lambda\le1\). Partial automata and any pseudometric space of views
are allowed. "Stays a view" is automatic there, because \(F\) is defined everywhere.

Variants:

| Lean theorem | Form |
|---|---|
| `robustMyhillNerode` | the earlier form: start ball, ball form inside blocks |
| `robustMyhillNerode_ball` | open balls, prefix 0 |
| `robustMyhillNerode_cells` | cell form, prefix 0 |
| `robustMyhillNerode_prefix` | exactness from a prefix |
| `rmn_core`, `rmn_core_cells` | the induction for arbitrary sets |

**Status.** Formalised.

### I.5.1 Theorem 2 has no converse

**Source.** main line 197 ("The converse does not hold in general"); SI line 107.

**Statement.** Exactness at every length does not imply that codes, radii \(r_q>0\), a block length
and a rate \(\lambda\in[0,1)\) satisfying (C_r) exist.

**Proof.** Parity: one event flips the state, and the output is the state. The tracker is
\(z\mapsto-z\), the readout is the sign, and the start is 1. It is exact: by induction the view is
\(\pm1\) according to the state.

1. Suppose \(c\), \(r>0\), \(k\) and \(\lambda\in[0,1)\) satisfy the block clause. \(F_w\) with
   \(|w|=k\) is \(z\mapsto(-1)^kz\), an isometry.
2. On \(\mathbb R\), the image of \(B(c_q,r_q)\) contains two points \(2r_q\) apart. If it lies in
   \(B(c_{q'},\lambda r_{q'})\), then \(r_q\le\lambda r_{q'}\).
3. With \(M=\max_qr_q\), this gives \(M\le\lambda M\), which contradicts \(M>0\) and \(\lambda<1\).
4. **On the circle**, with codes on the circle and balls of views (caps), the same holds.
   - (O_r) with two outputs forces \(r_q<2\), so no cap is the whole circle.
   - A rotation maps a cap onto a congruent cap.
   - A cap of angular radius \(\alpha\) lies in a cap of angular radius \(\beta\) only if
     \(\alpha\le\beta\). (Spherical triangle inequality: the far boundary point of the first cap is
     at angular distance \(\alpha+\angle(a,b)\ge\alpha\) from \(b\).)
   - The angular radius increases with \(r\), so steps 2–3 go through. ∎

**Lean.** `rmn_no_converse` (on \(\mathbb R\), closed balls). **Status.** Formalised on
\(\mathbb R\); proved on paper on the circle.

### I.5.2 Radius 0 and one-event blocks

**Source.** main line 78; SI line 107.

**Statement.** With closed balls of radius 0 and \(k=1\), the clauses say that \(F_x(c_q)=c_{q\cdot x}\)
and that the readout at \(c_q\) is \(o(q)\). Then \(q\mapsto c_q\) realises the automaton inside the
tracker. For the minimal automaton the map is also injective.

**Proof.**

- **Realisation.** By induction \(F_w(c_{q_0})=c_{q_0\cdot w}\), so the readout is \(o(q_0\cdot w)\).
- **Injectivity.** If \(c_q=c_{q'}\), then for every \(w\) applicable at both,
  \(o(q\cdot w)\) and \(o(q'\cdot w)\) are both the readout at \(F_w(c_q)=F_w(c_{q'})\), so they are
  equal. So \(q\) and \(q'\) are Nerode-equivalent, and minimality gives \(q=q'\). ∎

**Lean.** `myhillNerode` gives the realisation and exactness. **Status.** Formalised; the injectivity
remark is proved on paper.

**Notes.**

- Open balls of radius 0 are empty; the remark needs closed balls, or a limit as \(r\to0\).
- "Minimality of the tracker is not a consequence" (SI) is correct.

### I.5.3 Wording: main line 78

The main text paraphrases (E_r) as "every history past a short prefix inside its class's ball". (E_r)
asks this only at length \(p\). After that, views are in balls only at block boundaries, and inside
blocks only in readout cells. **Suggested:** "the view after a short prefix inside its class's ball".

## I.6 Lemma 1 (split), its remark, and growth along ψ

**Source.** main `lem:split`, lines 199–201; SI `lem:si-split`, lines 113–119; remark line 121;
"Growth along ψ" line 123.

**Lemma.** With \(M\pm D\) the two perturbed images and \(y=z(v)\),
\(\frac12\sum_{s=\pm1}d(M+sD,y)=\frac12|M-y|^2+\frac12|D|^2\).

**Proof.** Put \(E=M-y\). The left side is \(\frac14(|E+D|^2+|E-D|^2)=\frac12|E|^2+\frac12|D|^2\) by
the parallelogram law. ∎

**Remark (secant).** If the bracket at \(G=1\) is at most \(\tau\), then \(|M-y|\le\sqrt{2\tau}\) and
the secant ratio is at most \(\sqrt{2\tau}\sqrt{1+\sigma^2}/\sigma\).

**Proof.**

- Both halves of the bracket are at most \(\tau\), so \(|M-y|,|D|\le\sqrt{2\tau}\).
- The perturbed views are \((z\pm\sigma\psi)/\sqrt{1+\sigma^2}\), for a unit \(\psi\perp z\). Their
  chord is \(2\sigma/\sqrt{1+\sigma^2}\).
- The images differ by \(2D\). So the ratio is at most
  \(2\sqrt{2\tau}\big/(2\sigma/\sqrt{1+\sigma^2})\). ∎

**Growth along ψ.** With \(g_t=|J_{t+1}\psi_t|\) and \(\psi_{t+1}=J_{t+1}\psi_t/g_t\),
\(|J_{t+n}\cdots J_{t+1}\psi_t|=\prod_{j<n}g_{t+j}\).

**Proof.** By induction, \(J_{t+n}\cdots J_{t+1}\psi_t=(\prod_{j<n}g_{t+j})\psi_{t+n}\), and
\(|\psi_{t+n}|=1\). If some \(g\) is 0, both sides are 0 from then on. ∎ The SI calls this
"notation, not a constraint", which is right (referee T7).

**Lean.** `kick_split`, `kick_chord`, `kick_secant_le`, `norm_wordMap_eq_prod_gain` (`Kick.lean`).
**Status.** Formalised.

## I.7 Snap and the certificate (SI S5–S10 = LEAP Theorems A–E and Proposition H)

Pre-closure vectors are in \(\mathbb R^d\) with the sup norm. "Exact" means the readout is right
after every nonempty applicable input. This is the S5 reading, with \(P^+\).

### S5, enumeration (Observation, SI lines 133–139)

**Statement.**

- Let \(P\) be the (state, automaton state) pairs reachable from the start, and \(P^+\) those after
  a nonempty word.
- The tracker is exact iff the readout is right on \(P^+\).
- If \(P\) is finite, breadth-first search computes it with \(|P|\cdot|X|\) evaluations of one
  event.

**Proof.**

- Exactness gives the condition, since every pair of \(P^+\) is the pair after some nonempty word.
- Conversely, the pair after any nonempty word is in \(P^+\).
- \(P^+\) is the one-event image of \(P\), and \(P\) is the least set containing the start pair and
  closed under one event. So the search visits exactly \(P\), adding each pair once and applying
  each event once. ∎

**Lean.** `trackerExact_iff`, `reachedPairsPos_eq`, `reachedPairs_eq`, `reachedPairs_subset`.
**Status.** Formalised; the operation count is proved on paper.

### S6, a certificate must read the readout (SI lines 141–149)

**Statement (SI).** Let \(V\) return "certified" or not after reading only values, and finitely many
derivatives, of the transition, the closure and the readout at finitely many points. Suppose \(V\) is
sound for a class of trackers closed under changing the readout on a neighbourhood of one point. If
\(V\) certifies a tracker, then every state that tracker reaches is a point at which \(V\) read the
readout.

**Status.** **False at the start state as worded; formalised (corrected).**

**Counterexample.**

- Automaton \(s_0\xrightarrow{x}s_1\xrightarrow{x}s_1\), with outputs \(a\ne b\).
- Tracker on \(\mathbb R\): \(h_0=0\), \(F\equiv1\), readout \(b\) at 1 and \(a\) elsewhere.
- \(V\) = "the readout is right on \(P^+\)" reads the readout only at 1. It is sound for every
  tracker (S5), and it certifies this one.
- The start state 0 is reached (by the empty word), but \(V\) never reads the readout near it.

The earlier record already notes that LEAP's search never reads \(h_0\).

**Corrected statement.** Every state reached after a nonempty input is a point at which \(V\) read the
readout. This needs at least two outputs.

**Proof.** Suppose \((h,q)\in P^+\) and \(V\) read the readout at no point near \(h\).

1. Pick a ball \(U\) around \(h\) that avoids the read points (they are finitely many), and an output
   different from \(o(q)\).
2. Change the readout on \(U\) so that \(h\) reads that output. The new tracker is in the class.
3. The transition and the closure are unchanged, so \((h,q)\) is still reached, and the new tracker
   is not exact.
4. Every value \(V\) reads is unchanged, adaptive queries included, so \(V\) still certifies.
   Soundness is contradicted. ∎

**Lean.** `certificate_reads_readout` (`Snap.lean`). The read set may depend on (transition,
readout); the hypothesis `hlocal` is the adaptive form, `hchange` is the class closure and `hO`
gives two outputs.

**Scope: the sentence after S6 (SI line 149) does not follow.** It reads: "This does not cover
procedures that read the parameters, such as interval bounds. On the trained trackers those bounds
were vacuous or divergent. A point certificate therefore costs at least one readout evaluation per
reached state". S6 constrains only certificates that are sound for a class closed under changing the
readout near one point. A certificate for the trained trackers need only be sound for their
architecture. Their readout is an affine head on the closed view (main 72 and 227). Changing an
affine map near one point changes it everywhere, so that class is not closed in S6's sense. For that
class a point certificate can read the readout far less often:

1. Read the logits at \(d+1\) affinely independent views. This fixes the affine logit map
   \(\ell(v)=Wv+\beta\), and with it each gap's Lipschitz constant \(\|w_o-w_{o'}\|\).
2. Enumerate the reached pairs \(P\) with transition evaluations only, as in S5.
3. For each automaton state \(q\), read the logits at one reached view \(c_q\). Then compute
   \(r_q=\max\|v-c_q\|\) over the reached views \(v\) of \(q\). This uses no readout reads.
4. Certify if, for every \(q\) and every \(o'\ne o(q)\), the gap at \(c_q\) exceeds
   \(\|w_{o(q)}-w_{o'}\|\,r_q\). That is the gap's Lipschitz constant, so the gap stays positive on
   the ball \(B(c_q,r_q)\), which holds every reached view of \(q\).

This certificate is sound for every tracker with an affine head. It reads the readout at
\(d+1+|Q|\) points, not at every reached state. It certifies whenever each state's reached views
cluster within the margin, as they do for a snapped or contracting tracker. So the cost claim holds
for certificates sound for a class closed under local readout changes, and not for the trained
trackers' class as stated. The sentence needs that qualification (Part V). Observation S5's
\(|P|\cdot|X|\) count of transition evaluations is unaffected.

### S7, finite under perturbation forces a snap (SI lines 151–157)

**Statement.** Let states update as \(h_t=c(G(h_{t-1},x_t)+e_t)\) with \(\|e_t\|_\infty<\eta\), and
let \(R_\eta\) be the set reachable under all such perturbations. If \(c\) is continuous and
\(R_\eta\) is finite, then \(c\) is constant on the open ball of radius \(\eta\) about \(G(h,x)\), for
every reached \(h\) and every event \(x\).

**Proof.** For reached \(h\), the map \(e\mapsto c(G(h,x)+e)\) on the open sup-norm ball is
continuous, and its values lie in \(R_\eta\). The ball is convex, hence connected. A connected
subset of a finite Hausdorff space is a point. ∎

**Lean.** `finite_perturbed_forces_snap`. `finite_perturbed_analytic_const` covers the analytic
remark of the earlier SI, which is no longer in the text. **Status.** Formalised.

### S8, the clip (SI lines 159–165)

**Statement.**

- Let \(c\) clip each coordinate to \([-1,1]\), and let \(m(h,x)=\min_i|G_i(h,x)|-1\).
- If \(m(h,x)\ge\eta\) on every edge out of the unperturbed reachable set \(R_0\), then
  \(R_\eta=R_0\subseteq\{h_0\}\cup\{\pm1\}^d\).
- If some edge has margin below \(\eta\), \(R_\eta\) contains a continuum.
- Under the first alternative, exactness under every such perturbation is equivalent to a correct
  readout on \(P^+\).

**Proof.**

1. **First alternative.** If \(|G_i|\ge1+\eta\) and \(|e_i|<\eta\), then \(G_i+e_i\) has the sign of
   \(G_i\) and modulus above 1, so the clip gives the same corner. By induction every perturbed
   trajectory equals the unperturbed one. Every state after a nonempty word is a corner.
2. **Second alternative.** If \(|G_i(h,x)|<1+\eta\) at a reached \(h\), then
   \((G_i-\eta,G_i+\eta)\) meets \((-1,1)\) in a nonempty open interval. The clip is the identity
   there. Varying \(e_i\) alone fills that interval.
3. **Readout criterion.** This is S5, because perturbed runs equal unperturbed runs. ∎

**Lean.** `clip_perturbed_eq`, `clip_perturbed_continuum`, `clip_robust_exact_iff`.
**Status.** Formalised.

### S9, the certificate (SI lines 167–169)

**Statement (SI).** On a clip-closed tracker, suppose every reachable edge has positive margin, no
corner is reached with two automaton states, and the readout is right on \(P^+\). Then the tracker is
exact on every input at every length, and it stays exact under every per-step perturbation of the
pre-closure vector smaller than that margin.

**Proof.**

1. \(R_0\subseteq\{h_0\}\cup\{\pm1\}^d\) is finite. With a finite event set, there are finitely
   many reachable edges, so the least margin \(m^*\) is positive.
2. Apply S8 with \(\eta=m^*\): perturbed runs equal unperturbed runs.
3. Exactness follows from S5. ∎

The hypothesis "no corner is reached with two automaton states" is never used. With different outputs
it is implied by the readout condition; with equal outputs it is harmless.

**Lean.** `clip_certificate [Finite X]`. **Status.** Formalised. The two-states hypothesis is
unnecessary, and a finite event set is needed for "that margin".

### S10, contract then snap gives a radius (SI lines 171–177)

**Statement (SI).** Let \(h\) be a corner and \(z=G(h,x)\) have margin \(m>0\), and suppose
\(\|G(h',x)-G(h,x)\|_\infty\le\Lambda\|h'-h\|_2\) for all \(h'\) in the ball of radius \(\rho\) about
\(h\). Then the radius of carried-state perturbations that the clip absorbs is at least
\(\min(\rho,m/\Lambda)\). If every reachable edge satisfies this with the same \(m^*\) and
\(\Lambda\), perturbations of the carried state below \(\min(\rho,m^*/\Lambda)\) leave the trajectory
unchanged.

**Proof.**

1. **Radius.** For \(\|h'-h\|\le\min(\rho,m/\Lambda)\), \(\|G(h')-G(h)\|_\infty\le m\). Each
   \(|G_i(h)|\ge1+m\), so \(G_i(h')\) keeps its sign and has modulus at least 1. The clip therefore
   returns the same value.
2. **Trajectory.** Induct over events: each carried state is within the radius of the unperturbed
   reached state. ∎

**Lean.** `contract_snap_radius` and `contract_snap_trajectory`, for any metric on carried states and
any post-clip map \(\kappa\). **Status.** Formalised (corrected):

- "Let \(h\) be a corner" is never used.
- As worded it blocks the trajectory claim, because the start \(h_0\) need not be a corner.
- \(\Lambda>0\) is needed for \(m/\Lambda\).

The SI remark after S10 (two balls proved directly; a continuous certificate remains open) is
empirical and correctly labelled.

## I.8 Other mathematical sentences in the text

| Where | Sentence | Verdict |
|---|---|---|
| main 53 | "We prove that no loss evaluated only on the states the training data reach can tell apart smooth trackers whose errors evolve differently away from them, and that next-token likelihood prices a rare per-step state error at a cost carrying the model's own error rate as a factor" | correct (Theorem 1(a) and Theorem 1(b), (c)(ii)) |
| main 72 | "the readout's restoring force carries its own error probability, which training drives to its floor" | first half is Theorem 1(b); second half is empirical, not a theorem |
| main 72 | the \(\rho\) and \(\gamma\) sentences | correct (S3(v) and the γ remark) |
| main 72 | "no such loss certifies exactness at every length" | **refuted** (§I.4.1) |
| main 78 | "every history past a short prefix inside its class's ball" | **inaccurate paraphrase** of (E_r) (§I.5.3) |
| main 78 | radius to 0 and one-event blocks: "the task's minimal automaton is realised inside the tracker" | correct with closed balls (§I.5.2) |
| main 86 | "At \(G=1\) the bracket is the mean centred cosine distance of the two perturbed images to \(z(v)\)"; "It reads one secant at the last event … and does not bound the growth at every event" | correct (Lemma 1; Corollary 1 applies to F) |
| main 92 | Fig. 2a: "tends to \(1-\cos\theta\)" | the limit of \(\ell_\tau\) is \(-\cos\theta\); right only if the panel plots \(\ell_\tau\) relative to its value at the code (§I.2). Check |
| main 218 | the order-blind phase "pulls its code towards the abelianisation …, which on \(S_5\) is the sign of the permutation" | the group fact is standard (\([S_5,S_5]=A_5\), so \(S_5^{ab}=\mathbb Z/2\) via the sign); UNIFY D1(a), (b) prove the reached-view statements (§II.1); "pulls" is a gradient-dynamics reading that is not proved |
| main 227 | "r_q is the distance from \(c_q\) to the nearest facet of its readout cell, which is a polyhedron because the readout is affine in the view; (O_r) holds by construction" | correct on the **centred** unit sphere, where layer norm is affine (\(z\mapsto\gamma\odot\sqrt d\,z+\beta\)); not for the RMS closure (\(h\leftarrow\sqrt d\,h/\|h\|\), not centred), where layer norm is not affine on views. The ball study's tracker (M on \(S_5\)) should use the centred closure. Check |
| main 230 | "Because the noise has unbounded support, we report rates at this length only" | correct reasoning (cited to Maass–Sontag) |
| main 245, 248 | "the corollary and Theorem 2 have not [been formalised]"; "covers Theorem 1 so far" | **out of date**: Corollary 1, Theorem 2, S3, Lemma 1 and S5–S10 are formalised (with the corrections above) |
| SI 107 | "It is a sufficient condition and has no converse" | correct (§I.5.1) |
| SI 109 | "No trained tracker is shown to satisfy (C_r) uniformly" | correct, and honest (empirical) |

## I.9 Statements withdrawn in `8c21003e` (they were at `60c538a1` and `bb7003e4`)

They are recorded because the Lean results exist and in case the claims return.

- **Proposition 3(a), first sentence:** "whether a tracker satisfies (C_r) for some \(r>0\) is not
  determined by reached values".
  - **Refuted as worded:** every closed tracker satisfies (C_r) alone with radius 4
    (`every_closed_tracker_satisfies_cr`).
  - **True** for "satisfies Theorem 2's hypotheses": on the circle, \(z\mapsto1\) and
    \(z\mapsto z^2\) (`circle_rmn_not_determined_by_reached_values`).
  - The SI's proof step "(C_r) constrains the Jacobian at the centre" is **false**
    (`cr_does_not_constrain_jacobian`).
- **Proposition 3(a), second sentence:** "no objective that reads only reached views has a zero set
  inside the trackers that satisfy Theorem 2".
  - **False** with one output (`every_closed_tracker_satisfiesRMN_of_one_output`), and vacuous for an
    empty zero set (cross-entropy has none).
  - **Proved** when some input reaches a view outside the reached views
    (`reachedView_objective_cannot_certify`, `germ_objective_cannot_certify`,
    `exists_tracker_failing_rmn`).
  - Corollary 1 now plays its role.
- **Proposition 3(b), the transverse force.**
  - In UNIFY's linear transverse model (supplement eq. (6.1)), the expected kick term is
    \(\frac{\sigma^2}{2}(S_{\ell_u}(\lambda^2)+S_{\ell_v}(\lambda^2))\), with
    \(S_\ell(x)=\sum_{k<\ell}x^k\).
  - Its \(\lambda\)-derivative is \(\sigma^2\sum_k k\lambda^{2k-1}(\cdots)\), positive for
    \(\lambda>0\) when \(\max\ell\ge2\). Pairwise independent errors with mean 0 and variance
    \(\sigma^2\) suffice.
  - Lean: `transverse_term_expectation`, `transverse_force`, `transverseRate_pos`
    (`Transverse.lean`). **Formalised in that model.**
  - Not formalised: for cross-entropy, UNIFY gives only a bound; for smooth objectives the
    \(\sigma^2\) law holds to leading order (needs \(\xi=\sigma\zeta\) with a finite third moment).
- **Lemma 2 (gain), second sentence (chord ratio).** It needs nonzero chords, including at the start
  (`chord_ratio_prod`). "Constrains every horizon" was not a theorem (referee T7).
- **The Snap paragraph, Methods 266 and main 53/96** (the zero set is the minimal automaton with
  basins; analytic networks are forced to snap). **Refuted.** `analytic_tracker_zero_kick_term`
  (`SnapCounter.lean`) is an analytic, norm-preserving tracker on \(\mathbb C\) with:
  - an exact zero of the kick term at every kicked view;
  - exact parity runs;
  - and no locally constant neighbourhood at the reached views.

  The kick reaches two points per view, not a ball.
- **"At least as deep" (referee T2):** removed. It did not follow.

---

# Part II. Research notes

Assessments are mine unless marked *(reading agent, not re-verified)*. Those come from reading
agents whose reports were not committed. They are pointers, not results.

## II.1 UNIFY (`ab7236b9`; UNIFY.md last changed at `252a6f87`)

| Item | Verdict | Lean |
|---|---|---|
| U2 (readout bounds) | correct; = Theorem 1(b) | `Readout.lean` |
| U3(a) (blindness) | correct; = Theorem 1(a) | `blindness` |
| U3, closing sentence (§2.3, lines 204–205): "A term whose zero set certifies exactness on every input must evaluate the transition at states that are not reached" | **false** (verified). U3(a) shows that such a zero set does not constrain derivatives. It does not show that it cannot certify exactness. U5(b)'s own proof uses only (i), (ii) and the start view, all values at reached views. This is the main-72 point | `parity_enumeration`, `reachedPairs_congr` |
| U4 (small noise) | the expansion is correct. The gloss after it (lines 232–233) drops a factor \(n-2\) (verified): \(\sigma^2\|A_w\|_F^2/(2(n-2))\) is \(\sigma^2/2\) times the mean squared singular value, not \(\sigma^2/(2(n-2))\) times it. The certified-pair formula perturbs both members, which the implementation (certified pairs at \(k=0\)) does not | — |
| U10 (robust Myhill–Nerode) | correct; = Theorem 2. The name is a stretch (referee T5) | `RobustMN.lean` |
| Supplement Theorem 6.3 (transverse force) | correct in the linear model (6.1) | `Transverse.lean` |
| U5 (zero set: trackers that snap within \(k\) events) | the proof is correct, given one unstated hypothesis: the start view is the start class's centre (the empty history is in the support). (b) uses only (i) and (ii); (iii) is needed for (a) and (c). Hypothesis (iii) asks \(F_w(\tilde z)=F_w(z(u))\) at *every* \(\tilde z\) within chord \(\sigma\). A zero of the loss gives that only if the perturbations fill the ball. With finitely many kicks per view (as in F), a zero constrains finitely many points | — |
| U6 (analytic networks have no zero) | correct when the trivial-pair part averages over perturbations that fill a ball (an analytic map constant on a ball is constant). **Refuted** for the two-point kick: an analytic, norm-preserving tracker has an exact zero of the kick term, exact parity runs and no locally constant neighbourhood | `analytic_tracker_zero_kick_term` |
| D1(a), (b) (order-blind phase, abelianisation) | correct as statements about reached views; the title overstates (at most \(G^{ab}\)'s information); the gradient reading is unproved | — |
| D1(c) | standard: \([S_5,S_5]=A_5\) | — |
| G1 ("normal maps, every \(k\)") | stated and proved for symmetric \(A\) (verified): the proof uses a real orthogonal eigenbasis. The title and lines 29 and 1117 say "normal maps", which the proof does not cover. A reading agent says the result extends to normal maps *(not re-verified)* | — |
| Prop K | the expansion \(\mathbb E d=\tfrac12\sigma^2\|A_w\hat v\|^2+O(\sigma^3)\) is correct. The sentence after the proof, "its gradient pushes the top singular direction of the block cocycle to contract", fails for non-normal maps at \(k\ge2\) by UNIFY's own (b′) (line 1110; verified) | — |
| Prop N(b) | inconsistent *(reading agent)* | — |

## II.2 THEORY4 (`7f334584`)

| Item | Verdict |
|---|---|
| Lemma 1 | correct; its corollary (iii) needs \(C^3\) *(reading agent)* |
| Lemma 2 | correct, given \(\lvert\psi\rvert=1\) and \(g>0\). It is the growth identity, verified and formalised (`norm_wordMap_eq_prod_gain`) |
| Lemma 3 | correct, with a domain slip *(reading agent)* |
| Theorem 1 | correct *(reading agent)* |
| Theorem 4 | only the edge-wise bounds are proved; the robust-cell conclusion is unproved *(reading agent)* |
| Prop 5 | correct *(reading agent)* |
| "Robust exactly when …" | **necessity is false** (verified). An isometry is robustly exact without contracting: an irrational rotation with one output, or the parity tracker (`rmn_no_converse`) |

## II.3 LEAP (`6b488853`; LEAP.md last changed at `d5349805`)

`d5349805` changed only LEAP's results (from line 1359 on), not its lettered statements. It also
removed the sentence "No ball has come back with negative slack": the new results report negative
slacks. LEAP's lettered results are the SI's S5–S10:

| LEAP | SI | Verdict |
|---|---|---|
| Theorem A (enumeration) | S5 | as §I.7 |
| Theorem B (blindness forces enumeration) | S6 | as §I.7, including the start-state slip |
| Theorem C (finite under perturbation forces a snap) | S7 | as §I.7 |
| Theorem D (the clip) | S8 | as §I.7 |
| Corollary E (the certificate) | S9 | as §I.7 |
| Proposition H (contract, then snap) | S10 | as §I.7 |

| Item | Verdict | Lean |
|---|---|---|
| Theorem G (the certified set is flat) | correct. If \(Dc=0\) on an open set containing every reachable pre-closure point, the chain rule gives \(dh_t=Dc(z_t)(\cdots)=0\), so every differentiable loss of the readouts along reachable trajectories has zero gradient in \(\theta\), \(h_0\) and the input embeddings. Local constancy in \(\theta\) uses finitely many reachable edges and \(G\) continuous in \(\theta\). Proved on paper | not formalised; INTERP's analogue is `fderiv_eq_zero_of_finite_range` |
| §7.7 point 2 | holds only for rich function classes *(reading agent)* | — |

## II.4 MULTI (`d6cc16b9`)

| Item | Verdict |
|---|---|
| Theorem 1(a) | correct *(reading agent)* |
| Theorem 1(c) | **the proof's key inequality is false** (verified). Take \(d(x,y)=\lvert\varphi(x)-\varphi(y)\rvert\) with \(\varphi\) piecewise linear of slopes 1 and \(K\). A constant shift by \(\rho\) then moves \(d\) at rate \(K\rho\), not \(\rho\). The bound survives as a tolerance \(b-\varepsilon\) |
| Theorem 6(a) | wrong, by MULTI's own account |
| Theorem 6(d); Corollary 7(ii) | unsupported *(reading agent)* |
| Prop 3 | the conclusion does not follow *(reading agent)* |
| Theorem 8(a) | hides a \(K\)-dependence *(reading agent)* |
| Theorem 9 | correct given two hypotheses *(reading agent)* |
| Prop 12 | one false line *(reading agent)* |
| STEP1 lemmas | correct *(reading agent)* |

## II.5 INTERP (`52a9f521` = `07ccf3f9` for INTERP.md)

**Model** (§2). One event, from state vector \(z\) and letter \(a\), on a table \((S,B,\delta)\):

- query \(q=Q_Nz+Q_Lf_a\);
- key \(k_{sb}=K_Nc_s+K_Lf_b\);
- value \(v_{sb}=V_Nc_s+V_Lf_b+V_Tc_{\delta(s,b)}\);
- attention \(w=\mathrm{softmax}\langle q,k_{sb}\rangle/\sqrt D\) over \(S\times B\);
- output \(y=\iota z+W_O\sum w_{sb}v_{sb}\), with \(\iota=0\) for the overwrite tick and 1 for the
  residual tick;
- logits \(\ell_m=\langle y,c_m\rangle/\sqrt D\).

The snap moves to a name of largest logit. Notation (§3): \(x_s=e^{-\Delta_N(s)}\),
\(y_b=e^{-\Delta_L(b)}\), \(X=\sum_Sx_s\), \(Y=\sum_By_b\), the pushes
\(g_N,g_L,g_T\), and \(g_I=\iota\langle z,c_t-c_m\rangle/\sqrt D\).

**Lean** (`Interp.lean`).

- The row-vector products of the source are linear maps.
- The snap is any argmax selection, so every tie rule is covered.
- "The sum of the \(k\) largest leaks" is the maximum over subsets of size at most \(k\) (`topSum`).
  For positive leaks this is the same thing.

**Theorem 1(i)** (regeneration). The snapped interpreter is right on every word over \(B\) iff its
single step from exact codes is right at every reachable (state, letter) pair.

*Proof.*

- Forward: apply exactness to \(u\) and to \(u\,b\).
- Backward: induct on the word. The name after \(u\) is the table's state, which is reachable, and
  the step there is right. ∎

`regeneration`. **Formalised.**

**Theorem 1(iii).** The snapped step is locally constant away from readout ties, and its derivative
is zero wherever it exists.

*Proof.*

- The logits are continuous in \(z\): scores are continuous, the softmax denominator is positive,
  and the rest is linear.
- So a strict argmax stays the strict argmax near \(z_0\), and the selection is constant there.
- The snapped step takes finitely many values (the codes). A map with finite range is locally
  constant near any point of continuity, because its other values form a closed set missing that
  value. So its derivative vanishes wherever it exists, ties included. ∎

`continuous_logit`, `snap_eventually_eq`, `snapped_step_locally_constant`,
`fderiv_eq_zero_of_finite_range`. **Formalised**, and stronger than stated: the derivative vanishes
even at ties, wherever it exists.

**Theorem 1(ii)** ("the states it visits at test time are the table's exact codes …") is true by
construction, since the snap's image is the codes. Larger test tables lie outside the training
support. **Theorem 1(iv)** ("no training gradient passes through the snap") describes the protocol;
it is not a theorem.

**Theorem 2(a).** \(w_{sb}=x_sy_b/(XY)\).

*Proof.* The score is a name part plus a letter part, so
\(e^{\mathrm{score}(s,b)}=e^{\mathrm{score}(n,a)}x_sy_b\). Sum over \(S\times B\). ∎
`attn_factorises`. **Formalised.**

**Theorem 2(b).**
\((\ell_t-\ell_m)XY=\sum_{s\in S}\sum_{b\in B}x_sy_b[g_N(s)+g_L(b)+g_T(\delta(s,b))+g_I]\),
for nonempty \(S\) and \(B\).

*Proof.*

- By linearity, \(\ell_t-\ell_m=g_I+\sum w_{sb}[g_N+g_L+g_T]\).
- Multiply by \(XY\), use (a) and \(\sum\sum x_sy_b=XY\). ∎

`logit_sub_eq`, `margin_mul_eq`. **Formalised** (for any \(t,m\)).

**Theorem 2(c)**, the four situations. Regroup, using \(x_n=y_a=1\). `four_situations`.
**Formalised.**

**Theorem 2(d), factorised bound.**

- **Data.** Fix a vocabulary quadruple \((n,a,t,m)\) and a table with \(S\subseteq V_N\),
  \(B\subseteq V_L\), \(\delta\) into \(S\) and \(\delta(n,a)=t\), whose leaks satisfy
  \(X\le1+X^+\) and \(Y\le1+Y^+\).
- **Quantities.** \(\Omega=-(\min g_N+\min g_L+\min g_T)\) over the vocabulary,
  \(R_0=g_N(n)+g_L(a)+g_T(t)\), and \(\lambda=1-1/((1+X^+)(1+Y^+))\).
- **Claim.** \(\ell_t-\ell_m\ge g_I+(1-\lambda)R_0-\lambda\Omega\).

*Proof.*

1. In (b), divided by \(XY\), every row's bracket minus \(g_I\) is at least \(-\Omega\). The
   matching row's is \(R_0\), with weight \(w_0=1/(XY)\ge1-\lambda\).
2. So \(\ell_t-\ell_m-g_I\ge w_0R_0-(1-w_0)\Omega=w_0(R_0+\Omega)-\Omega\).
3. \(R_0+\Omega\ge0\), because \(n\), \(a\) and \(t\) are vocabulary items. So the right side is at
   least \((1-\lambda)(R_0+\Omega)-\Omega\). ∎

`factorised_bound`. **Formalised.** The step \(R_0+\Omega\ge0\) is not in INTERP's proof but holds
automatically.

**Corollary.** If the bound is positive for every quadruple with \(m\ne t\), with \(X^+\) and \(Y^+\)
the top sums of \(N-1\) and \(A-1\) leaks, then every table with at most \(N\) names and \(A\)
letters from the vocabulary runs exactly.

*Proof.*

- A table's leak is at most \(1+\) the top sum (`leak_le_topSum`).
- So at every reachable pair the right name is the strict argmax.
- Apply Theorem 1(i). ∎

`certified_tables_exact`, `exact_of_margins`. **Formalised.**

The factorised certificate as computed (`certificate`, `interp_run.py` lines 346–404) is this
corollary with a tolerance. `lam_star` is the least of \((g_I+R_0-\mathrm{TOL})/(R_0+\Omega)\) over
\((t,m)\), and the test `frac < lam_star` is \(\lambda<\) that ratio, i.e. the factorised bound
\(>\mathrm{TOL}=10^{-3}\).

**Theorem 2(d), role-split bound.** INTERP describes it in words (lines 164–167). What INTERP
certifies with is `_split_rows` (`interp_run.py` lines 471–531), and the statement below follows
that code.

- **Data.** A quadruple \((n,a,t,m)\) at \(z=c_n\); vocabulary \(V_N,V_L\); head names \(H\). The
  code takes the 32 largest \(x_s\).
- **Quantities.** Code names are in brackets.
  - \(h=\min_{r\in V_N}g_T(r)+g_I\) (`gTstar + gI`).
  - \(R_m=g_N(n)+g_L(a)+g_T(t)+g_I\) (`R0`).
  - \(LB\): the most negative sum of at most \(A-1\) of the terms
    \(\min(0,y_b(g_N(n)+h+g_L(b)))\), \(b\in V_L\setminus\{a\}\) (`LBL`).
  - \(G\): the same for the terms \(\min(0,y_bg_L(b))\) (`GLm`). \(Y^+\): the sum of the \(A-1\)
    largest \(y_b\) (`ys`).
  - \(\beta(g)=g+g_L(a)+h+G+Y^+\min(0,g+h)\) (`br`, `brmin`).
  - \(HS\): the most negative sum of at most \(N-1\) of the terms \(x_s\min(0,\beta(g_N(s)))\),
    \(s\in H\setminus\{n\}\) (`Hc`).
  - \(TS\): the sum of the \(N-1\) largest \(x_s\), \(s\in V_N\setminus(\{n\}\cup H)\) (`Tc`).
- **Claim.** Take a table with at most \(N\) names and \(A\) letters from the vocabulary, \(n\in S\),
  \(a\in B\) and \(\delta(n,a)=t\). Then
  \((\ell_t-\ell_m)XY\ge RS=R_m+LB+HS+\min(0,\beta(\min g_N))\,TS\).
  The code also subtracts \(\tau(1+X^+)(1+Y^+)\), with \(\tau=\mathrm{TOL}\). If what remains is
  positive, then \(\ell_t-\ell_m>\tau\).

*Proof.*

1. By (b) and (c), \((\ell_t-\ell_m)XY\) is the matching bracket \(R_m\) plus the same-state,
   same-letter and cross terms.
2. A row's destination is a vocabulary name, so every bracket is at least
   \(g_N(s)+g_L(b)+h\).
3. **Same-state rows.** \(y_b\varphi(n,b)\ge y_b(g_N(n)+h+g_L(b))\ge\min(0,\cdot)\). There are at
   most \(A-1\) of them, all from \(V_L\setminus\{a\}\), so their sum is at least \(LB\).
4. **A leaked source** \(s\ne n\) contributes \(x_s[\varphi(s,a)+\sum_{b\ne a}y_b\varphi(s,b)]\).
   - Write \(Y_B=\sum_{b\in B\setminus a}y_b\in[0,Y^+]\).
   - By step 2 the bracket is at least
     \(g_N(s)+g_L(a)+h+(g_N(s)+h)Y_B+\sum y_bg_L(b)\).
   - \((g_N(s)+h)Y_B\ge\min(0,g_N(s)+h)\,Y^+\).
   - \(\sum y_bg_L(b)\ge\sum\min(0,y_bg_L(b))\ge G\).
   - So the bracket is at least \(\beta(g_N(s))\), and the contribution is at least
     \(x_s\min(0,\beta(g_N(s)))\).
5. **Head and tail.**
   - The head sources are at most \(N-1\) names of \(H\setminus\{n\}\), so their sum is at least
     \(HS\).
   - \(\beta\) is non-decreasing because \(Y^+\ge0\). So each tail term is at least
     \(x_s\min(0,\beta(\min g_N))\).
   - The tail leaks sum to at most \(TS\), and \(\min(0,\cdot)\le0\).
6. **Tolerance.** \(XY\le(1+X^+)(1+Y^+)\), so \(RS>\tau(1+X^+)(1+Y^+)\ge\tau XY\). Divide by
   \(XY>0\). ∎

`botSum`, `splitBeta`, `splitBound`, `split_bound`, `split_margin_gt`,
`split_certified_tables_exact`. **Formalised.** As in the code, the certificate quantifies over
every \((n,a,t,m)\) with \(m\ne t\) (`flat` masks only \(t=m\)). The head set may depend on
\((n,a)\), as `top_k` does.

**Correspondence.**

- The code gives the matching source and letter leak 0 (`exp(-inf)`). So its pools are
  \(V_N\setminus\{n\}\) and \(V_L\setminus\{a\}\), as in Lean.
- A sorted cumulative sum of non-positive terms is `botSum` (the \(k\) most negative). A sorted
  cumulative sum of leaks is `topSum`.
- The caps `min(N−1, head)` and `min(N−1, P_N−1−head)` are automatic in Lean.
- Floating point is outside the model. TOL is the code's guard against it.
- INTERP takes, for each \(A\), the larger of the two certificates' \(N^*\) (`N_star_best`,
  line 879). Each certificate's soundness covers that.

**The prose does not match the code.** INTERP says the bound charges "the \(N-1\) most harmful"
names. The code charges up to \(N-1\) head names one by one, and on top of them the \(N-1\) largest
tail leaks at the worst source push. So a table slot can be charged twice, as INTERP's Check and §8
say. The code's bound is sound (above). INTERP §8 proposes taking the minimum over how the \(N-1\)
leaked names split between head and tail. That alternative is also sound and tighter, but it is not
implemented or formalised.

**The Check (lines 184–189).** "On one hand-built case its tail term … certifies 4 names where the
factorised bound certifies 6." This is an artefact of the grid.

- `test_interp.py` sets `N_GRID = (2, 3, 4)` (line 20). So the role-split certificate is never
  evaluated above 4 names.
- The factorised certificate scans \(N=2,\dots,6\) (`certificate`, line 394).
- The enumeration lists tables of at most 4 names. So the factorised "6" was never checked by
  enumeration. `certified_tables_exact` covers it.

**Theorem 2(e)**, the symmetry corollary, is not a theorem as worded (verified).

- **The hypothesis cannot hold.** Under renaming by every permutation of names, the Gram matrix of
  the codes is \((\alpha-\beta)I+\beta J\). Distinct codes need \(\alpha\ne\beta\), and then its
  rank is at least \(V-1\). INTERP has \(V=256\) names in \(D=128\) (`interp_run.py` lines 48–49).
- **The conclusion fails even where it holds.** A push \(g_N(s)\) still depends on whether \(s\) is
  \(t\), \(m\) or neither. So a quantity can take three values in one situation.
- **Nothing is lost.** Theorem 3(a) needs no symmetry.

**Theorem 3(a), homogeneous form.**

- **Hypotheses.** At every query each same-letter row trails by at least \(\Delta_N\), each
  same-state row by at least \(\Delta_L\), the matching bracket is at least \(R\), and the harms (the
  negative parts of the brackets, \(g_I\) included) are at most \(\eta_L,\eta_N,\eta_X\).
- **Claim.** \((A-1)e^{-\Delta_L}\eta_L+(N-1)e^{-\Delta_N}\eta_N+(N-1)(A-1)e^{-(\Delta_N+\Delta_L)}\eta_X<R\),
  with \(N=|S|\) and \(A=|B|\), implies exactness on the table.

*Proof.* In (c), the matching term is at least \(R\). Each leaked term is at least \(-(\text{its
weight})(\text{its harm})\), and the weights are at most \(e^{-\Delta_L}\), \(e^{-\Delta_N}\) and
\(e^{-\Delta_N}e^{-\Delta_L}\). So \((\ell_t-\ell_m)XY>0\). Finish with \(XY>0\) and Theorem 1(i). ∎

`homogeneous_size_law` (one query), `homogeneous_exact` (the table). **Formalised**, with each
bracket and harm including \(g_I\). If \(g_I\) were left out of the harms, the claim would need
\(g_I\ge0\). The residual tick at \(m=n\ne t\) has
\(g_I=(\langle c_n,c_t\rangle-D)/\sqrt D<0\).

**Refuted in Theorem 3(a): "for large programs the last term decides", "slope one".** INTERP
states \(NA<(R/\eta_X)e^{\Delta_N+\Delta_L}\) and \(\log(NA)=\Delta_N+\Delta_L+\log(R/\eta_X)\).

- **Counterexample.** Take \(\Delta_N=\Delta_L=10\), \(R=\eta_L=\eta_N=\eta_X=1\) and \(A=2\).
  - The four-term condition is \(e^{-10}+(N-1)(e^{-10}+e^{-20})<1\), so
    \(N-1<(e^{10}-1)/(1+e^{-10})\approx22{,}024.5\), i.e. \(N\le22{,}025\).
  - The "last term" law gives \(N<e^{20}/2\approx2.43\times10^8\), four orders of magnitude more.
- **When the cross term decides.** With \(A\) fixed, the terms linear in \(N\) are
  \((N-1)e^{-\Delta_N}(\eta_N+(A-1)e^{-\Delta_L}\eta_X)\). The cross term dominates only if
  \((A-1)e^{-\Delta_L}\eta_X\ge\eta_N\), that is \(A-1\ge e^{\Delta_L}\eta_N/\eta_X\). Otherwise the
  same-letter term sets the size, with slope one in \(\Delta_N\) alone. The symmetric condition
  holds for \(N\).
- **What holds.** The four-term inequality, which is formalised.

**Theorem 3(b)** is Theorem 2(d) with top sums (above).

**Theorem 3(c), random programs.**

- **Proved on paper.** The expectation part is linearity in each destination.
- **Open.** The Hoeffding statement is not written out.
- **Heuristic.** "Random programs run exactly far past \(N^*\)".
- **Refuted for the residual tick at \(m=n\) (verified):** "A random program's harm is therefore
  only the destination-free part of the push. It is far smaller than the adversarial harm".
  - With \(\iota=1\), \(z=c_n\), \(m=n\ne t\) and codes of norm \(\sqrt D\),
    \(g_I=(\langle c_n,c_t\rangle-D)/\sqrt D\approx-\sqrt D\). That is \(-11.3\) at \(D=128\), the
    size of a code's own logit.
  - In the residual arm the value of row \((s,b)\) carries \(-c_s\). So \(g_N(n)\approx+\sqrt D\)
    cancels \(g_I\) in the matching and same-state rows, but not in rows with source \(s\ne n\).
  - Those rows' destination-free part is about \(g_I\approx-\sqrt D\), and about \(-2\sqrt D\) when
    \(s=t\). INTERP's §8 finds the worst source to be \(t\) itself, with push \(-11.3\). In every
    residual cell that breaks, the worst competitor is \(m=n\).

**Theorem 3(d), capacity.** With \(z=c_n\) and codes of norm \(\sqrt D\):

- \(\Delta_N(s)\le(\|Q_N\|+\|Q_L\|)\|K_N\|\,\|c_n-c_s\|\le2\kappa_N\sqrt D\);
- \(\Delta_L(b)\le(\|Q_N\|+\|Q_L\|)\|K_L\|\,\|f_a-f_b\|\le2\kappa_L\sqrt D\).

*Proof.* Cauchy–Schwarz on \(\langle q,K_N(c_n-c_s)\rangle/\sqrt D\), with
\(\|q\|\le(\|Q_N\|+\|Q_L\|)\sqrt D\). ∎

`gapN_le`, `gapL_le`, `gaps_le_two_kappa`. **Formalised.**

**Correction to INTERP 3(d).** \(\kappa\) is defined with \(\|K_N\|\) only. The letter gap needs
\(\|K_L\|\), so "\(e^{4\kappa\sqrt D}\)" needs \(\kappa=(\|Q_N\|+\|Q_L\|)\max(\|K_N\|,\|K_L\|)\).

"Certified program size at most of order \(e^{4\kappa\sqrt D}\)" is not a theorem as worded. It
needs the certificate to fail once the leaks are large, which holds only if \(\Omega>g_I\).

**Theorem 4(c), "only if": refuted (verified).** INTERP: "A free interpreter is exact on a table only if
its one-step certificate holds on balls of radius ρ around the codes, where ρ is the distance of an
output from its code."

- **Counterexample.**
  - Take \(D=1\), one letter, and two names with codes \(c_1=1\) and \(c_2=-1\). \(\delta\) swaps
    them.
  - Use the overwrite tick, \(Q_N=K_N=W_O=1\) and \(V_T=3\), with every other map 0.
  - The scores are \(\pm z\), so the event is \(F(z)=-3\tanh z\).
- **The free run is exact.** \(F(z)\) has the sign opposite to \(z\) for \(z\ne0\). So from \(c_1\)
  the free run alternates sign forever, and the readout (the sign) is right at every step.
- **The certificate fails on the ball.** \(\rho\ge|F(1)-c_2|=3\tanh1-1>1\), because
  \(\tanh1>2/3\iff e^2>5\). So the ball of radius \(\rho\) around \(c_1\) contains \(z=-0.1\).
  There \(F(-0.1)>0\) reads name 1, while the table says name 2.
- **What holds.** The certificate is sufficient when it holds on balls that the step maps into the
  next ball.

**Later INTERP results** *(reading agent, not re-verified)*: Theorem 8(a), (b) fail (8(a) is now
refuted in Lean, §VI.6); Prop 6(c) has
issues; Theorem 7's "certified slack" is undefined.

---

# Part III. Gaps and errors in the current paper (`e4d3a557`)

1. **main 72, last sentence.** "No such loss certifies exactness at every length" is false. The
   enumeration certifies exactness with finitely many adaptive reads (`parity_enumeration`). True
   versions: "none certifies (C_r)", or "none certifies exactness of a tracker that reaches a view
   the loss does not read".
2. **main 78.** (E_r) is paraphrased as "every history past a short prefix inside its class's ball".
   (E_r) asks this at length \(p\) only.
3. **main 92 (Fig. 2a caption).** The high-temperature limit of \(\ell_\tau\) is \(-\cos\theta\).
   "\(1-\cos\theta\)" is right only if the panel plots \(\ell_\tau\) relative to its value at the
   code.
4. **main 245, 248.** The formalisation status is out of date (see §I.8).
5. **SI S6.** "Every state that tracker reaches" is false at the start state. Correct: "every state
   reached after a nonempty input". Alternatively, count the empty word in exactness and use \(P\),
   not \(P^+\), in S5.
6. **SI S9.** "No corner is reached with two automaton states" is unused. "That margin" needs a
   finite event set, which holds in all settings but is unstated.
7. **SI S10.** "Let \(h\) be a corner" is unused, and as worded it excludes the start state from the
   trajectory claim. \(\Lambda>0\) is needed.
8. **main 227.** "(O_r) holds by construction" relies on the readout being affine on views. That
   holds on the centred sphere and fails for the RMS closure. Check which closure the ball study's
   tracker used.
9. **main 72.** "Which training drives to its floor" is empirical. Cite the measurement or soften
   it.
10. **main `thm:blind`(a).** Says "a tracker"; the SI says "a closed tracker". The proof needs
    closure.
11. **SI line 149.** "A point certificate therefore costs at least one readout evaluation per
    reached state" applies S6 outside its hypothesis. The trained trackers have affine heads, a
    class not closed under local readout changes. For that class, \(d+1\) reads fix the head, and a
    Lipschitz ball check then needs one read per automaton state (§I.7, S6). The claim holds for
    certificates sound for a class closed under local readout changes.

Resolved since `bb7003e4`:

- Theorem 1(c) now states non-expansion, defines \(K\), \(m\) and \(\bar s\), and uses the strict
  \(N>\) and the state-space drift (T3).
- Theorem 2 now has the cell and prefix forms (T4).
- Corollary 1 covers F explicitly (T6).
- The gain lemma was reworded (T7).
- The zero-set, snap and transverse-force claims were removed (T8, T9).
- "At least as deep" was removed (T2).

# Part IV. Referee report T1–T12 against the current paper

| Item | Status at `e4d3a557` |
|---|---|
| T1 Theorem 1 does not explain the failures | answered in wording (main 53: the loss gives no reason to find contraction) |
| T2 "At least as deep" | removed |
| T3 Theorem 1(c) false as stated, threshold drops a factor | fixed; Lean matches the new statement |
| T4 Theorem 2's hypotheses violated by the trackers | the cell form and prefix are now in the statement; SI says no trained tracker is shown to satisfy (C_r) uniformly |
| T5 Not a Myhill–Nerode theorem | the name is kept; the SI explains the \(r\to0\) case. **Neo's decision** |
| T6 No result links the trained loss to the theorem; Prop 3(a) applies to F | Corollary 1 applies to F, and the SI says Nerode training is "motivated by … not derived from" Theorem 2 |
| T7 "One event is every horizon" | reworded ("notation, not a constraint"; the window "acted as a gain") |
| T8 Zero-set and snapping claims | removed (refuted in Lean: `SnapCounter.lean`) |
| T9 Proposition 3(b) has no proof | removed (UNIFY's model version is formalised: `Transverse.lean`) |
| T10 Printed loss is not the trained loss | outside this document (eq. (F) now has the gain \(G\); Methods describes F and M) |
| T11 The perturbation clause does not cover the noise experiment | the theorem still absorbs bounded moves at block boundaries only; Methods "Noise" reports rates at one length because the noise is unbounded. The gap stands but is no longer claimed away |
| T12 Known results presented as findings | acknowledged (the SI's "familiar saturation"; citations) |

# Part V. Decisions for Neo

1. **main 72, last sentence.** Restrict it (to (C_r), or to trackers that reach a view the loss does
   not read) or delete it.
2. **main 245 and 248.** Whether to update the formalisation claims (Corollary 1, Theorem 2, S3,
   Lemma 1 and S5–S10 are formalised), and how to word the corrections in items 5–7 of Part III.
3. **SI S6.** Exactness with or without the empty word. Then fix either S6's wording or S5's
   \(P^+\).
4. **SI S9 and S10.** Drop the unused hypotheses ("two automaton states", "a corner"), and state
   \(\Lambda>0\) and a finite event set.
5. **Theorem 2's name** (referee T5).
6. **main 78, the (E_r) paraphrase, and Fig. 2a's "\(1-\cos\theta\)".** Wording.
7. **main 227.** Confirm that the ball study used the centred closure.
8. **INTERP, if it enters the paper.**
   - Define \(\kappa\) with \(\max(\|K_N\|,\|K_L\|)\).
   - Drop or restrict "slope one" and "the last term decides". They fail when
     \(A-1<e^{\Delta_L}\eta_N/\eta_X\).
   - Restate 2(e) or remove it.
   - Describe the role-split bound as the code computes it (head names one by one, plus the top
     \(N-1\) tail leaks), or implement INTERP §8's head/tail split.
   - Drop the "4 names vs 6" comparison, which is the test grid's cap.
   - Restrict 3(c)'s "far smaller" to the overwrite tick.
   - Turn 4(c)'s "only if" into "if".
9. **The brief's paper commit** (`60c538a1`) is two rounds old. This document tracks `e4d3a557`.
   Say if a different commit should be the reference.
10. **SI line 149.** Qualify the cost sentence: "for a certificate sound for every readout", or
    "for a class closed under local readout changes". The alternative is to state the cost for
    affine heads separately.

---

# Part VI. Paper v2: the pinned executor

Lean files: `Pinned.lean` (Theorem P, Corollary P2, the Mealy block), `Unpinned.lean` (Theorem
8(a)), `Lookup.lean` (Lemma Q), `Compose.lean` (Theorem C), `Registers.lean` (Corollary P3),
`Window.lean` (the pointer), `Policy.lean` (the cache policy), `Robust.lean` (robust cells),
`Adder.lean` (the adder and subtracter tables). Every
result below is **formalised**; its axioms are listed with it. "Standard" means `propext`,
`Classical.choice`, `Quot.sound` or a subset of them. Sources added in round 2: INSIGHTS.md §1 row C
and §2 items 11–12, PAPER_V2_PLAN.md (both in the main checkout, 28 Oct), and BIGIDEA.md §2, §4.5,
§4.6 (`bigidea` at `768f965e`). Round 3: ARITH_FORMAT §1–§7 and `arith_core.py` (`arith` at
`a0d03c80`), REASON_FORMAT §2 (`reason` at `59c4d6aa`).

## VI.0 Setting and modelling choices

- **The model.** A deterministic function `step : List Tok → List Tok → Tok`: the token chosen at
  the block's last position, from the context Π and the block. "Chosen" is any argmax selection,
  so every tie rule is covered (`IsArgmax O sel`: `sel ℓ ∈ O` maximises `ℓ` over the output set
  `O`, the whole vocabulary or the program's state names).
- **H1** (single tokens, the same id in the block as in Π's rows, injective names) is the
  modelling choice that states and events *are* tokens. The table `δ : Tok → Tok → Tok` is any
  function. Parsing Π into `δ` (total, single-valued, destinations in `S`) is not modelled; the
  well-formedness the theorems need is stated as a hypothesis.
- **H3** (deterministic forward, no other mutable state) is that `step` is a function. Section 3 of
  `Pinned.lean` derives the abstraction from a causal decoder with a cache that is never written.
- **H2** (strict margins) is not needed for Theorem P(2) in exact arithmetic when certification and
  the run use the same selection. It is what makes the check independent of the tie rule, and
  Corollary P2 needs it (as margin `> 2τ`).
- **Closed set of rows.** `ClosedFrom δ B s₀ Q`: `s₀ ∈ Q` and `δ s e ∈ Q` for `s ∈ Q`, `e ∈ B`. A
  set of rows closed under the table's transitions from the start state is `Q × B` for such a `Q`.
  `Reach δ B s₀` is the smallest one (`reach_closed`, `reach_subset`).
- **Runs.** The clock's trace is `tape.scanl (tick step Π) s₀` with `tick step Π s e = step Π [s, e]`;
  its final state is `tape.foldl …`. The table's run is `tape.scanl δ s₀`.

## VI.1 Theorem P(1): the tick sees only (Π, s, e)

**Statement** (DEMO_DESIGN §5.1). Tick \(i\)'s logits are a function of \((\Pi,s_{i-1},e_i)\) only.
They do not depend on \(i\), \(T\), earlier ticks, or anything outside Π.

**Lean model** (`CausalDecoder`). Token-and-position embedding; `depth` layers, where layer
\(\ell\) at position \(p\) may read anything at positions \(0,\dots,p\) of the previous layer
(attention under the causal mask, MLPs, norms); a head at the last position. Position ids are the
indices. `forward D xs` is a full forward; `prefill D Π` is Π's residuals at every layer;
`cachedForward D cache P blk` runs the block at positions \(P,P+1,\dots\) reading positions \(<P\)
from the cache, which it never writes.

**Results.**

| Statement | Lean | Axioms |
|---|---|---|
| The residual at \(p\) depends only on the tokens at positions \(\le p\) | `resid_congr` | `propext` |
| Π's residuals are the same whatever block follows (fixed by Π) | `prog_resid_fixed` | `propext` |
| A forward of the block on Π's prefilled cache computes the residuals of Π ++ block at every layer and position | `cache_sound` | `propext`, `Quot.sound` |
| So a tick's logits are `forward D (Π ++ [s, e])`: a function of (Π, s, e) | `cachedForward_eq` | `propext`, `Quot.sound` |
| The block's first position cannot see the event (§8.1, Codex) | `block_first_blind` | standard |
| ARITH §4: forward 2 as `[t]` at \(P+3\) on the cache extended by forward 1 equals the re-fed block `[s, a, b, t]` on Π's cache | `forward2_refeed_eq` | `propext`, `Quot.sound` |
| The clock that prefills Π once and runs every tick and every certification row on that cache satisfies P(2) | `pinned_regeneration_decoder` | standard |

*Proof.* Induction on the layer: the residual at \(p\) is a function of the residuals at
\(\le p\) one layer down, and at layer 0 of the token and position id at \(p\). Π's positions see
only Π. The cached forward reads Π's positions from the cache, which holds exactly those residuals,
and computes the block's positions by the same layers. ∎

**Correspondence.** Exact arithmetic. Corollary P2's point, that floating-point evaluation also
depends on the code path, is outside this model; ARITH §10 found the 1-token forward 2 not bitwise
reproducible on an H100, although `forward2_refeed_eq` shows it is the same function.

## VI.2 Theorem P(2): pinned regeneration

**Statement** (DEMO_DESIGN §5.1(2)). Let δ be the table Π encodes. The run equals δ's run on every
tape of every length over \(B\), from \(s_0\), iff \(F_\Pi(s,e)=\delta(s,e)\) for every \((s,e)\)
reachable from \(s_0\) under δ over \(B\). Checking all of \(S\times B\) suffices.

**Lean.**

| Statement | Lean | Axioms |
|---|---|---|
| If every row of \(Q\times B\) passes, for a closed \(Q\), then on every tape over \(B\) the clock's whole trace \(s_0s_1\dots s_T\), its final state, and any answer read from the final state are the table's | `pinned_regeneration` | `propext`, `Quot.sound` |
| Well-formed table (\(s_0\in S\), destinations in \(S\)) certified on all of \(S\times B\): the run is exact | `pinned_regeneration_table` | `propext`, `Quot.sound` |
| If the final state is right on every tape over \(B\), every reachable row passes | `pinned_certificate_necessary` | `propext`, `Quot.sound` |
| Trace right on every tape ⟺ certified on the reachable rows ⟺ certified on \(Q\times B\) for some closed \(Q\) | `pinned_regeneration_iff` | `propext`, `Quot.sound` |
| The same for any step \(F\) (INTERP Theorem 1(i) with traces); trace right ⟺ final state right | `regeneration_trace_iff`, `scanl_eq_iff_foldl_eq` | `propext`, `Quot.sound` |

*Proof.* Induction on the tape: if \(s_{i-1}\) is the table's state, it lies in \(Q\), so
\(s_i=F_\Pi(s_{i-1},e_i)=\delta(s_{i-1},e_i)\). Conversely, for a reachable row \((s,e)\) reached by
\(u\), compare the runs on \(u\) and on \(ue\). The trace is right iff every prefix's final state
is, and the prefixes of a tape over \(B\) are tapes over \(B\). ∎ (The Lean proof reuses
`Interp.regeneration`.)

**Changes from the informal statement.**

- None to the truth of the statement. Sufficiency holds for any set of rows closed under the
  table's transitions from the start state, not only the reachable rows or \(S\times B\).
- "Checking all of \(S\times B\) suffices" needs the table well formed (\(s_0\in S\), every
  destination in \(S\)), which H1 asks the certifier to check.
- H2 is not used (VI.0).
- The whole trace, not only \(s_T\), is right (Corollary P4's premise).

## VI.3 Theorem P(3): each tick reproduces its certified row

**Statement** (DEMO_DESIGN §5.1(3); ARITH §8). Each tick's logit vector equals that of its row's
certification block, exactly in exact arithmetic.

`tick_logits_eq_row` (`propext`, `Quot.sound`): under the certificate on a closed \(Q\times B\),
the logits of tick \(i\), on the block `[s_{i−1}, e_i]`, equal the logits of the certification
block of the *table's* row \((\delta(s_0,e_1\dots e_{i-1}),e_i)\). `mealy_tick_logits_eq_row`
(`propext`, `Quot.sound`): both logit vectors of a Mealy tick (forward 1 on `[s, a, b]`, forward 2
on `[s, a, b, t]` with \(t\) forward 1's argmax) equal those of the table's row's two certification
forwards.

*Proof.* The same function on the same inputs; the inputs agree because the clock's state is the
table's (P(2)). ∎ The content beyond "the same function" is that the tick's row is the table's row.

## VI.4 Corollary P2: certification on another code path

**Statement** (DEMO_DESIGN §5.1, P2; §8.1). If the run's logits differ from the certified logits by
at most \(\tau\) per logit, the argmax agrees wherever the margin exceeds \(2\tau\).

| Statement | Lean | Axioms |
|---|---|---|
| Two logit vectors within \(\tau\) per output; margin of \(t\) in the first \(>2\tau\): every argmax of the second is \(t\) | `sel_eq_of_close` | standard |
| The run's tick logits \(L_{\rm run}(h,s,e)\) may depend on anything, including the history \(h\), and lie within \(\tau\) of the certified \(L_{\rm cert}(s,e)\); every row of a closed \(Q\times B\) has argmax \(\delta(s,e)\) with margin \(>2\tau\): the run is exact on every tape over \(B\) | `regeneration_of_close` | standard |

No change; the Lean version is stronger (history-dependent perturbations).

## VI.5 Theorem P for the Mealy block (ARITH_FORMAT §8)

**Statement** (ARITH §8). Each tick computes \(G_\Pi(s,a,b)=(t,o)\): forward 1 on `[s][a][b]` gives
\(t\), forward 2 on `[s][a][b][t]` gives \(o\). By induction, the run's states and outputs equal the
table's on every tape of every length over \(A\times B\) iff \(G_\Pi\) agrees with the table on
every reachable cell. Certifying all of \(S\times A\times B\) checks every cell.

**Lean.** The event is the pair \((a,b)\); `mealyTick step Π s (a, b) = (t, step Π [s, a, b, t])`
with \(t\) = `step Π [s, a, b]` (forward 2 is fed forward 1's argmax, never the row's written
value). `MealyCertified`: at every row of \(Q\times E\), forward 1 gives \(\delta(s,(a,b))\) and
forward 2, fed forward 1's argmax, gives \(\mathrm{out}(s,(a,b))\). `mealyRun` returns the final
state and the output tape.

| Statement | Lean | Axioms |
|---|---|---|
| Rows of a closed \(Q\times E\) pass both checks ⇒ on every tape over \(E\): state trace, final state, output tape, and any answer read from them (e.g. `<final> c=s_T s=V`) are the table's | `pinned_regeneration_mealy` | `propext`, `Quot.sound` |
| Well-formed table (start and destinations in \(S\); outputs unchecked), all rows of \(S\times E\) certified ⇒ exact | `pinned_regeneration_mealy_table` | `propext`, `Quot.sound` |
| Final state and output tape right on every tape over \(E\) ⇒ every reachable row passes both checks | `mealy_certificate_necessary` | `propext`, `Quot.sound` |

**Changes.** None. One precision: the converse needs the final state as well as the output tape.
Outputs alone do not determine the rows in general: two states with the same output behaviour can
be swapped in forward 1 without changing any output tape. ARITH §8 says "states and outputs", which
is right; the `<final>` line prints \(s_T\).

## VI.6 INTERP Theorem 8(a) is false for unpinned decoding (DEMO_DESIGN §5.2)

**Statement** (INTERP §3, Theorem 8(a)). "Emitting the most likely state name and re-embedding it
is a snap onto the model's own codebook, so Theorem 1 holds: errors cannot accumulate across
steps."

**The claim formalised** (`Theorem8a Tok`). For every decoder (logits as any function of the
context), every argmax selection over the vocabulary, every program Π and well-formed table: if the
decoder passes the certificate, then unpinned decoding (context `Π s₀ e₁ s₁ e₂ s₂ …`, each state
decoded from the whole context) runs the table exactly on every tape.

**What "passes every check" means.**

- `PassesCert`, DEMO_DESIGN §2.5's certificate: at every row \((s,e)\in S\times B\), on the context
  `Π ++ [s, e]` (also the context of an unpinned first tick from \(s\) on \(e\)), the argmax over
  the whole vocabulary is \(\delta(s,e)\), with strictly positive margin over every other token.
- In `no_finite_check`, additionally: the unpinned run is right on every tape of length \(\le N\).
- In `no_finite_test_suite`, additionally: the step is right, with strictly positive margins, at
  every context of an arbitrary finite set \(C\) of contexts that extend Π and end in a row
  `[s, a]` (any earlier states, right or wrong, any lengths).

**Counterexample** (DEMO_DESIGN §5.2 with Π explicit).

- Tokens `sink, u, v, a`. Π = `sink u a u v a v` (the rows `u a u`, `v a v`). \(\delta(u,a)=u\),
  \(\delta(v,a)=v\), start \(u\).
- Logits at the last position: a correct lookup, \(R>0\) on the block's state token (the second
  token from the end), plus one head's write on \(v\)'s logit.
- The head scores \(c\) at position 0 and 0 elsewhere, over every position of the context. Its
  value is \(\beta=4R\) on an `a` token and 0 otherwise. So it writes
  \(\beta\cdot\#a/(e^c+n)\), with \(n\) tokens after the sink (`headPush_sink`).
- At a certification block `Π ++ [s, a]` the write is \(12R/(e^c+8)\), constant per row. At the
  \(k\)-th unpinned tick of the all-\(u\) run it is \(4R(k+2)/(e^c+2k+6)\) (`headPush_uRun`).

| Statement | Lean | Axioms |
|---|---|---|
| For \(e^c>4\): passes the certificate; the pinned run is exact on every tape; the unpinned run is right after \(n\) events while \(2n<e^c-2\) and wrong (state \(v\), table \(u\)) once \(2n>e^c-2\) | `theorem8a_counterexample` (with `passesCert8`, `run8_right`, `run8_wrong`) | standard |
| The claim is false (\(c=\log5\): wrong after 2 events) | `not_theorem8a` | standard |
| For every \(N\): a decoder that passes the certificate and is exact unpinned on every tape of length \(\le N\), wrong on a longer one | `no_finite_check` | standard |
| For every finite test suite \(C\) as above: a decoder right with positive margins on all of \(C\) and on the certification blocks, wrong unpinned on some tape | `no_finite_test_suite` | standard |
| The converse direction fails too: a step whose unpinned run is exact on every tape fails the certificate at the reachable row \((v,a)\), a context the unpinned run never sees | `unpinned_exact_not_certified` | `propext`, `Quot.sound` |
| **True version.** If at every context `Π ++ mid ++ [s, e]` with \(s\in Q\), \(e\in B\) every logit is within \(\tau\) of the pinned row's, and every pinned row of a closed \(Q\times B\) has argmax \(\delta(s,e)\) with margin \(>2\tau\), unpinned decoding is exact on every tape | `unpinned_exact_of_close` | standard |

*Why.* The emitted token snaps the state, not the context. The context is a second state, unsnapped
and growing, and Theorem 1 does not cover it. In a pinned block the head's write is the same at
every tick for a given row, so it is part of \(F_\Pi\), and the certificate passes or fails with it.

**Changes from the informal statements.**

- **Theorem 8(a) is false as stated**, in both directions of "Theorem 1 holds" (`not_theorem8a`,
  `unpinned_exact_not_certified`). It holds for the pinned clock (Theorem P) and, for unpinned
  decoding, under a bound on the history's effect (`unpinned_exact_of_close`). No finite check of
  the step certifies that bound for this family (`no_finite_test_suite`).
- **DEMO_DESIGN §5.2's count is idealised** ("after \(n\) run tokens, half of them \(a\) … crosses
  at \(n=e^c\)"). With Π's own `a` tokens and the block counted, the crossing is at \(2k=e^c-2\)
  for the \(k\)-th event, i.e. after about \(e^c-2\) run tokens. The conclusion stands, as the source
  says.
- **"In a pinned block the push is 0"** (first draft) is wrong, as Codex said: it is
  \(12R/(e^c+8)\), constant per row; the certificate passes iff \(e^c>4\).

## VI.7 Lemma Q and the lookup lemma (DEMO_DESIGN §5.3, §8.1)

**Setting.** A head attends to a finite set \(P\) of positions (rows and everything else it sees),
weights \(w_p=e^{\sigma_p}/\sum_{q\in P}e^{\sigma_q}\) (the denominator over **all** positions).
Logits \(\ell_m=g_m+\sum_pw_p\,\mathrm{val}_p(m)\): a residual part plus a readout linear in the
head's output (`headLogit`).

**Statement** (DEMO_DESIGN §5.3, as corrected in §8.1). Scores \(\sigma_r=\sigma^0_r+\varepsilon_r\),
\(|\varepsilon_r|\le\varepsilon\) on rows; pushes \(P_r=P^0_r+u_r\), \(|u_r|\le\eta\);
\(XY=\sum_{\rm rows}e^{\sigma^0_r-\sigma^0_{r_0}}\); \(R_0=P^0_{r_0}\);
\(\Omega\ge-\min P^0\) over every non-matching position, row or not;
\(Z_0\ge\sum_{p\notin\rm rows}e^{\sigma_p-\sigma_{r_0}}\); \(g_I\) a lower bound on the residual
gap. If \(R_0+\Omega\ge0\), then \(\ell_t-\ell_m\ge g_I+w(R_0+\Omega)-\Omega-\eta\) with
\(w=1/(1+e^{2\varepsilon}(XY-1)+Z_0)\).

| Statement | Lean | Axioms |
|---|---|---|
| \(w_{r_0}\ge1/(1+e^{2\varepsilon}(XY-1)+Z_0)\) | `matched_weight_ge` | standard |
| For weights \(\ge0\) summing to 1 with \(w_{r_0}\ge w\): \(\sum_pw_pP_p\ge w(R_0+\Omega)-\Omega-\eta\) | `weighted_margin_ge` | standard |
| Lemma Q, the margin bound | `lemmaQ` | standard |
| If the bound is positive for every competitor (constants may depend on it), every argmax is \(t\) | `lemmaQ_argmax` | standard |
| **Lookup lemma.** Matched weight \(\ge1/2\); the matched value separates \(t\) from every competitor by \(\Delta\); every other position favours a competitor over \(t\) by at most \(\Lambda\), \(0\le\Lambda<\Delta\); the residual prefers no competitor: every argmax is \(t\) (margin \(\ge w(\Delta+\Lambda)-\Lambda>(\Delta-\Lambda)/2\)) | `lookup_argmax_half` | standard |
| \(e^{2\varepsilon}(XY-1)+Z_0<1\) ⇒ matched weight \(>1/2\) (CIRCUITS' "guaranteed matched-row weight \(>\tfrac12\)" test) | `half_lt_matched_weight` | standard |
| \(1/2\) is sharp: for every \(w<1/2\), a head with matched weight \(w\), \(0\le\Lambda<\Delta\), no residual, and a wrong argmax | `lookup_half_sharp` | standard |
| The first draft (no \(Z_0\)) is false: one row and a sink of equal score; the draft's weight bound is 1 and its margin bound \(+1\); the true weight is \(1/2\) and the true margin \(-1\) | `lemmaQ_without_Z0_false` | standard |

*Proof.* \(1/w_{r_0}=\sum_pe^{\sigma_p-\sigma_{r_0}}=1+\sum_{{\rm rows}\setminus r_0}+\sum_{\rm
non\text{-}rows}\le1+e^{2\varepsilon}(XY-1)+Z_0\), since
\(\sigma_r-\sigma_{r_0}\le\sigma^0_r-\sigma^0_{r_0}+2\varepsilon\). Then
\(\sum w_pP_p\ge w_{r_0}(R_0-\eta)-(1-w_{r_0})(\Omega+\eta)=w_{r_0}(R_0+\Omega)-\Omega-\eta\), which
is non-decreasing in \(w_{r_0}\) because \(R_0+\Omega\ge0\). For the lookup lemma take
\(R_0=\Delta\), \(\Omega=\Lambda\), \(\eta=0\): \(w(\Delta+\Lambda)-\Lambda\ge(\Delta-\Lambda)/2>0\). ∎

**Changes from the informal statement.**

- \(Z_0\) is necessary (`lemmaQ_without_Z0_false`), as both critiques said; η outside the slope, as
  corrected.
- Role-additivity of \(\sigma^0\) is not used. It matters only for computing \(XY\) from the
  vocabulary, as \(X\cdot Y\le(1+X^+)(1+Y^+)\) (INTERP Theorem 2(a), `attn_factorises`).
- \(R_0=P^0_{r_0}\) relaxes to \(R_0\le P^0_{r_0}\).
- The readout must be affine in the head's output. A final RMSNorm is not (§8.1, Codex), so the
  lemma applies before it, or to a head whose output is read linearly.
- The lookup lemma's threshold is "at least \(1/2\)", and it is sharp.

## VI.8 Theorem C: composition of certified calls (INSIGHTS C)

**Statement** (INSIGHTS §1, row C; PAPER_V2_PLAN). In a transcript that calls certified programs,
P(final answer wrong) ≤ P(table wrong) + P(quote wrong) + P(reasoning glue wrong); the execution
term is exactly 0 at any length.

**Lean model.** \(K\) calls in transcript order. Call \(i\) has its own context `prog i` (built fresh
from its rows), table `δ i`, start `s₀ i`, events `B i` and readout `out i`. Its tape is the model's
quote `q i v`, which may cite the results `v j` of earlier calls only (`CitesEarlier`). Its result is
`clockOut i (q i v)`: the pinned clock on the call's own Π, a function of the program and the tape
alone. The answer is the glue `g v`, which reads only the \(K\) results (`ReadsResults`). The right
tables `tab'`, quotes `q'` and glue `g'` give the right results `v'` and answer `g' v'`.

| Statement | Lean | Axioms |
|---|---|---|
| Every call certified on its reachable rows, every quoted tape over the call's events: every call's result is its table's output on its actual input (so every cited result is exact), at any tape length and in any order of calls | `compose_exact` | `propext`, `Quot.sound` |
| No certificate: a wrong answer means an executor error on some call's actual input, or a table wrong on its right input, or a quote wrong given the right earlier results, or glue wrong on the right results | `error_decomposition` | standard |
| Every call certified: the executor term is empty; a wrong answer means a wrong table, a wrong quote or wrong glue | `error_decomposition_certified` | standard |
| For any measure over transcripts: P(wrong) ≤ P(some table wrong) + P(some quote wrong) + P(glue wrong) | `error_bound` | standard |

*Proof.* With no executor, table, quote or glue error, strong induction on \(i\): \(v_i\) is the
executor's output on \(q_i(v)\), which is the table's; \(q_i(v)=q_i(v')\) because the quote cites
only earlier results, which agree; that is the right quote, and the table is right on it, so
\(v_i=v'_i\). The glue then sees the right results. The probability bound is the event inclusion
plus the union bound. ∎

**Changes from the informal statement.**

- The three terms must be read at the right inputs: "table wrong" is the written table's output
  differing from the right one on the *right* tape, "quote wrong" is the model's quote differing
  from the right one *given right earlier results*, and "glue wrong" is the glue's answer differing
  *on the right results*. Each term is then a property of one component with everything upstream
  right, so the terms can be measured separately, as REASON plans. (Read at the model's own inputs,
  the inclusion also holds if the right quotes and glue cite only earlier results; that variant is
  not in Lean.)
- Hypotheses the informal version leaves implicit: a quote cites only earlier results; the glue
  reads only the results; every quoted tape is over the call's events (the clock rejects others).
- "Every cited result is exact" means equal to its table's output on its actual input, not to the
  right answer. The table and the quote can still be wrong.

## VI.9 Corollary P3: registers (DEMO_DESIGN §5.1)

**Statement** (DEMO_DESIGN, Cor. P3, narrowed). With one block per register per tick, each register's
step is a fixed function of its inputs. Independent registers (demo 1) and cascades (register \(j\)
reads registers \(<j\) as new values, or any registers as previous values) are certified by
enumerating each register's own (inputs, event) set.

| Statement | Lean | Axioms |
|---|---|---|
| Independent registers (own Π, table and start; the same event tape; PROMPTBOX's robot has two): per-register certificates on closed sets give the joint table's trace on every tape | `registers_exact` | `propext`, `Quot.sound` |
| Conversely, a right joint run certifies every register's reachable rows | `registers_certificate_necessary` | `propext`, `Quot.sound` |
| The joint table's run is the product of the registers' runs | `jointTable_foldl` | none |
| Cascade over `Fin r`: register \(j\)'s letter reads the event, the old joint state and the new values of registers \(i<j\) only; if each register's step agrees with its table on a set of (state, letter) pairs containing every pair the table's run presents to it, the joint trace is the table's on every tape | `cascade_exact` | standard |

*Proof.* Independent: the product of closed sets is closed, and the joint tick agrees with the joint
table on it; apply Theorem P. Cascade: on a reachable joint state, induct on \(j\) within the tick:
register \(j\)'s letter is the table's because the registers it reads are already right, so its step
is its table's; then apply regeneration to the joint machine. ∎

**Changes.** None. The cascade certificate is stated with any set `C j` that covers the pairs the
table's run presents; all own states × all letters is the enumeration DEMO_DESIGN counts
(\(\sum_j|B|\,|S_j|\prod_{k\in D_j}|S_k|\) rows; the count is not formalised).

## VI.10 The pointer cannot live in a bounded window (BIGIDEA H2; BRIDGE)

**Statement** (BIGIDEA §2): "a decoder that sees only Π and a bounded window cannot find the next
event of a long, low-entropy tape by itself, because nothing in the window says how far along the
tape it is (a counter needs log T bits that no bounded window of state and event names carries)."

**Lean model** (`WindowGen`). A window-\(k\) decoder emits \(y\) with
\(y_{t+k}=f(y_t,\dots,y_{t+k-1})\): every next token is a function of the last \(k\) tokens. Π (the
program and the question, which contains the whole tape) is fixed, so it is part of \(f\). No position
id enters. The run format (`runTarget`) is \(k\) prompt tokens, then \(e_1s_1e_2s_2\dots\).

| Statement | Lean | Axioms |
|---|---|---|
| The next token is a function of the window: if the decoder emits a target correctly, equal windows of the target are followed by equal tokens | `window_determines` | `propext`, `Quot.sound` |
| A repeated window makes the emitted sequence periodic from there on | `periodic_of_win_eq` | `propext`, `Quot.sound` |
| A window decoder is a finite-state machine: with tokens in \(\Gamma\), the output is periodic from some \(i\) with period \(p\), \(i+p\le|\Gamma|^k\) | `window_eventually_periodic` | standard |
| A table's states on a stretch of one event repeat within \(|S|\) steps | `stretch_states_periodic` | standard |
| **The pointer.** If the tape has a stretch \(a^m\) followed by \(b\ne a\), and \(S\) is a finite set of states closed under \(a\) that contains the state at the stretch's start, then no window-\(k\) decoder emits the run correctly through that \(b\) once \(2m\ge k+2|S|\) | `window_loses_place` | standard |

*Proof.* On the stretch the target run is periodic with period \(2\lambda\le2|S|\) once past the
states' preperiod (\(\mu+\lambda\le|S|\)). If \(2m\ge k+2|S|\), the window just before the \(b\) and
the window \(2\lambda\) tokens earlier lie in that periodic part and are equal. A window decoder
must then emit the same token after both, but the target has \(b\) after one and \(a\) after the
other. ∎

**Sharpness** (on paper, not in Lean). For \(k\ge2\), take \(S=\{1,\dots,n\}\),
\(\delta(i,a)=\min(i+1,n)\) from \(1\), and a marker as the prompt's last \(k\) tokens. Every window
before the \(b\) contains a marker or a state \(<n\) at a known offset, except windows of all-\(n\)
states, which start at or after position \(k+2n-4\). So if \(2m\le k+2n-4\), the windows before the
\(b\) that are equal have equal next tokens, and a decoder (built from Π) is right through the \(b\).
The bound is sharp to within two events.

**Changes from the informal statements.**

- The coordinator's draft ("on a tape of \(n\) identical events, the emitted sequence is eventually
  periodic with period at most \(|S|^k\)") is not the failure. On a tape of identical events the run
  is periodic and a window decoder can follow it. What it cannot do is find where a stretch ends.
  The period on the stretch is at most \(2|S|\), and the bound on \(m\) is linear in \(k\) and
  \(|S|\), not \(|S|^k\). The \(|\Gamma|^k\) bound is the general finite-state fact.
- BIGIDEA's "log T bits" is an information count, not a proof: a window decoder that sees Π *does*
  know the whole tape. It fails because it does not know where it is, and that needs a long
  low-entropy stretch. On a tape whose every window-sized factor occurs once, matching the window
  against Π locates it.
- **Not covered:** decoders that read position ids. With true text positions (BIGIDEA's WIN2–WIN8,
  0/36 exact), RoPE's distance to the sink could count in principle; those failures are a
  measurement, not this theorem. Streaming the events (the pinned clock) escapes the theorem, since
  the event is an input. Full attention escapes it too, but then the history is a second, unsnapped
  state (VI.6).

## VI.11 The cache-policy equivalence (BIGIDEA H2, policy TOK)

**Statement** (INSIGHTS item 12; PAPER_V2_PLAN, "is it a tool call?"). Decoding token by token
under the policy "Π as sink, evict each (state, event) block, positions restart after Π" computes
the pinned two-token tick.

**Lean model.** The `CausalDecoder` of VI.1. `decodeStep D cache P x` decodes one token at
position \(P\) on a cache and returns the cache with its residuals added. `policyLogits D Π s e`
decodes \(s\) alone at \(|\Pi|\) on Π's cache, then \(e\) alone at \(|\Pi|+1\) on that cache, and
reads the logits at \(e\). Each tick starts from Π's cache (eviction) at the same positions
(restart).

| Statement | Lean | Axioms |
|---|---|---|
| Decoding \(s\) on Π's cache leaves exactly the cache of Π ++ [s] | `decodeStep_eq_prefill` | `propext`, `Quot.sound` |
| The policy's logits equal the pinned block's, `cachedForward D (prefill D Π) |Π| [s, e]`, and both equal `forward D (Π ++ [s, e])` | `policy_tick_eq` | `propext`, `Quot.sound` |
| The policy's run is the pinned clock's run | `policyRun_eq_pinned` | `propext`, `Quot.sound` |
| Theorem P for the policy, with its own certificate | `policy_regeneration` | `propext`, `Quot.sound` |

*Proof.* `cache_sound` gives the first line. Then `cachedForward_eq` twice: once for Π ++ [s] with
the block [e], once for Π with the block [s, e]; both are `forward D (Π ++ [s, e])`. ∎

**Changes.** None in exact arithmetic. "Up to the kernel's floating-point order" is outside the
model. BIGIDEA measured max |Δ logit| 0.375 between the two paths and no argmax difference, with each
path bitwise equal to its own certificate (24,336/24,336 ticks). The other policies are not modelled:
advancing positions and sliding windows need masks or position offsets that `CausalDecoder` does not
express.

## VI.12 Robust cells (CIRCUITS; PAPER_V2_PLAN fig. v2-2(d))

**Statement** (the brief). Under Corollary P2's τ-bound, with certified margins above \(2\tau\), a
perturbation of the state token's embedding below a radius set by the margins and a Lipschitz
constant cannot change the tick.

**Lean model.** For a row \((s,e)\), \(L(x)\) is the tick's logit vector when the state token's
embedding is replaced by \(x\) (all else fixed); \(c\) is the token's own embedding. The Lipschitz
hypothesis is local at the code: \(|L(x)_m-L(c)_m|\le K\|x-c\|\) for \(\|x-c\|<r\).

| Statement | Lean | Axioms |
|---|---|---|
| Certified margin \(\mu\) at the code; computed logits within \(\tau\) of \(L(x)\); \(2(\tau+K\|x-c\|)<\mu\): every argmax is the row's destination | `robust_cell` | standard |
| The cell is the ball of radius \(\min(r,(\mu-2\tau)/(2K))\) | `robust_cell_radius` | standard |
| A run whose fed state embeddings are always within \(\rho<r\) of their codes (noise, a kick, any history dependence), with \(2(\tau+K\rho)<\mu\): exact on every tape | `robust_run` | standard |

*Proof.* \(|\ell_m-L(c)_m|\le\tau+K\|x-c\|\), and Corollary P2 applies with that bound; for runs,
histRun regeneration. ∎

**Changes.** The margin must exceed \(2\tau\) strictly for a positive radius. The Lipschitz constant
is a hypothesis: logits are locally Lipschitz in one input embedding, but a bound from layer norms
would make the radius vacuous for a 36-layer model, so CIRCUITS' measured sharp cells remain
evidence, not a consequence of this theorem.

## VI.13 The adder and the subtracter (ARITH_FORMAT; REASON_FORMAT)

**Statement** (ARITH_FORMAT §1, §3, §7, §8: "What it does not cover … whether the table is the
adder"; REASON_FORMAT §2). The adder's 200 rows `c a b c' s` satisfy \(c'\cdot10+s=c+a+b\). Run
from carry 0 on the digit pairs from the right, a missing digit read as 0, then one more `0 0` pair,
the final carry is 0 and the outputs read backwards are the sum. The subtracter's 200 rows
`b a c b' d` satisfy \(d-10b'=a-c-b\); with the extra pair, the final borrow is 0 iff
first ≥ second, and then the outputs read backwards are first − second; a final borrow of 1 says
first < second, and the outputs are then \(10^{n+1}-(\text{second}-\text{first})\).

**Lean model.** Numbers are digit lists as written, most significant first; `numVal x` is the
value, so leading zeros are allowed. `adderRows` and `subRows` are the 200 rows each, written out
in ARITH's order (state, then the first digit, then the second). `digitPairs` is `arith_core`'s
`digit_pairs`. `dropLeading` is `final_ids`'s "drop leading zeros while more than one is left";
`decimal n` is the decimal digits of \(n\) (`[0]` for 0). On tokens, the rows are written through
any injective digit-to-token map (Qwen3's ids 15–24), and the table is read from the token rows by
key, as the parser does. `RowsCertified` is ARITH §5's check, row by row in the order written.

| Statement | Lean | Axioms |
|---|---|---|
| 200 adder rows, each \(c'\cdot10+s=c+a+b\), \(s<10\), \(c'\le1\) | `adderRows_length`, `adderRows_spec` | none (`decide`) |
| 200 subtracter rows, each \(d+c+b=a+10b'\) (i.e. \(d-10b'=a-c-b\)), \(d<10\), \(b'\le1\) | `subRows_length`, `subRows_spec` | none (`decide`) |
| ARITH §2's parser checks pass: keys unique and \(|S|\cdot|A|\cdot|B|\) of them, destinations and start in \(S\) | `adderRows_check`, `subRows_check` | none (`decide`) |
| Every cell \((s,a,b)\), \(s\le1\), \(a,b\le9\), has a row | `adderRows_complete`, `subRows_complete` | `propext`, `Quot.sound` (`decide`) |
| The table read from the rows is \(((c+a+b)/10,(c+a+b)\bmod10)\), resp. the borrow cell | `lookupRow_eq`, `lookup_adder`, `lookup_sub` | standard |
| **Adder.** Final carry 0; \(\max(|x|,|y|)+1\) output digits whose value is \(x+y\); the `<final>` digits are the decimal digits of \(x+y\) | `adder_correct` (via `add_fold`, `dropLeading_eq_decimal`) | standard |
| **Subtracter.** Final borrow 0 iff \(y\le x\), 1 iff \(x<y\); with borrow 0 the outputs are \(x-y\) and the `<final>` digits its decimal digits; with borrow 1 the outputs' value is \(10^{n+1}-(y-x)\) | `sub_correct` (via `sub_fold`) | standard |
| The table read from the token rows runs as the digit machine, in tokens | `table_eq_digit_run`, `tokLookup_tokRows`, `mealyRun_map` | standard |
| The adder table, on tokens: final state the token of 0, `<final>` digits those of \(x+y\) | `adder_table_correct` | standard |
| **With Theorem P.** If all 200 rows pass the certificate on the context, the clock's `<final>` line is `c=0`, `s=` the decimal digits of \(x+y\), for numbers of every length | `adder_clock_correct` (via `clock_eq_digit_run`, `pinned_regeneration_mealy`) | standard |
| The same for the subtracter: final borrow 0 iff \(y\le x\), 1 iff \(x<y\), and with borrow 0 the digits of \(x-y\) | `sub_clock_correct` | standard |

*Proof.* On equal-length little-endian digit lists, induction on the column: from carry
\(c\le1\), \(\mathrm{val}(\text{outputs})+10^n c'=c+\mathrm{val}(x)+\mathrm{val}(y)\) (adder) and
\(\mathrm{val}(\text{outputs})+\mathrm{val}(y)+\beta=\mathrm{val}(x)+10^n\beta'\) (subtracter).
Padding with zeros does not change a value. The extra pair writes the last carry as a digit and
leaves carry 0; for the subtracter it keeps the borrow and writes 0 or 9. The outputs are digits, so
their value is below \(10^n\), which decides the borrow. Dropping leading zeros from digits whose
last is nonzero gives Mathlib's `Nat.digits`. On tokens, injectivity carries the lookup and the
run across, and Theorem P's Mealy form carries the certified clock to the table. ∎

**Changes and notes.**

- None to the sources' statements. ARITH §8 left "whether the table is the adder" outside Theorem P;
  for the fixed 200 rows it is now proved. What remains outside is whether the model *wrote* those
  rows (a byte comparison against `adderRows` decides it) and whether the clock read the right spans.
- The extra `(0, 0)` pair matters: it turns the last carry into the leading output digit. Without it
  the final carry would be lost from the `<final>` digits.
- The theorems hold for numbers with leading zeros and of any lengths, and for any injective
  digit-to-token map. Margins (H2) are not needed.

## VI.14 Not formalised

- Corollary P4 (a Mealy machine as a Moore machine on (state, output) pairs) is superseded by the
  Mealy block (VI.5); the whole-trace statement it needs is in `pinned_regeneration`.
- Floating point (P2's "bit for bit only on the same code path"): outside exact arithmetic. The
  Lean P2 is the \(\tau\)-bound version.
- Parsing Π into δ from token lines, the reading of spans (anchors, commas), and the fidelity of the
  table to the question (compile): outside Theorem P, as the sources say. For addition and
  subtraction the table's fidelity reduces to comparing the written rows with `adderRows` or
  `subRows` (VI.13).
- The sharpness of the window bound (VI.10), the certificate cost counts (VI.9), and the other cache
  policies (VI.11).

## VI.15 Decisions for Neo (v2)

1. **INTERP Theorem 8(a).** Withdraw it or restate it for the pinned clock (Theorem P). For
   unpinned decoding the true statement needs a bound on the history's effect
   (`unpinned_exact_of_close`), which no finite check certifies.
2. **Theorem P's hypotheses.** H2 can be dropped from P(2) and kept for P2 only; "checking all of
   \(S\times B\)" should say "for a well-formed table".
3. **Lemma Q.** State that the readout is affine in the head's output (before the final norm), and
   that role-additivity is used only to bound \(XY\).
4. **Theorem C.** State the three terms at the right inputs (VI.8), and name the hypotheses that a
   quote cites only earlier results and the glue reads only the results.
5. **The pointer.** State it for a long stretch of one event followed by a different one, with the
   bound \(2m\ge k+2|S|\), and say it assumes no position information.
6. **Addition and subtraction end to end.** Have the harness compare the written rows with the
   canonical 200 (byte for byte). With that check and the certificate, the table and executor terms
   of Theorem C are zero for these calls, and only the reading of the spans remains.
