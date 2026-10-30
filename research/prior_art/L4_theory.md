# L4. Theory: prior art for the blindness theorem, robust Myhill–Nerode, Theorem P and the unsnapped history

Literature agent L4, 28 October 2026. Scope: exposure bias and compounding error, horizon theory of
next-token and imitation learning, stability and contraction of recurrent models, robust finite-state
computation, length-generalisation theory, testing and certification, neural program execution, the
digital abstraction. Claims checked: C1 (blindness), C2 (closure + aimed kick + Nerode training, no
continuous certificate), C3 (robust Myhill–Nerode), C5 (Theorem P and `no_finite_test_suite`), C8 (the
emitted token snaps the state, not the context).

**How entries were verified.** Every entry below was fetched live on 28 October 2026. arXiv entries: the
arXiv API (`export.arxiv.org/api/query?id_list=…`) returned title, authors, first-version date, comment
and journal reference. DOI entries: the Crossref API. Venue pages (PMLR, ICML and NeurIPS virtual
pages, ACM/IEEE via Crossref) were fetched where the venue is claimed. "Theorem read" means the formal
statement was read in the paper's own text (arXiv HTML or the PDF converted with `pdftotext`); "abstract
read" means only the abstract. The raw API output is in `L4_verified_records.txt` next to this file.
Nothing here is cited from memory; items I could not verify are listed in §7.

**Search coverage caveat.** The shared web-search budget for this session ran out partway through. After
that point I only fetched known URLs and verified known identifiers. Four sub-areas got less searching than
the rest: Lean, Coq and Isabelle proofs about transformers; PAC limits of testing learned models; noise
injection for robust state tracking from 2025 to 2026; and Krohn–Rhodes in neural networks beyond Liu et
al. 2023 and Knorozova and Ronca 2024. A follow-up session should finish these (§7).

---

## V. Verdict per theorem (read this first)

There are three possible verdicts: **still ours**, **ours with a narrower wording** (the wording to use
is given), or **pre-empted**. No theorem is pre-empted outright. Two special cases are: Theorem 2 at
k = 1 with p = 0, and the sufficiency half of Theorem P.

| Theorem (v1 or v2 label) | Verdict | Use this wording | Closest prior art |
|---|---|---|---|
| **Theorem 1(a), blindness, with the likelihood corollary** (C1; Lean `blindness`, `likelihood_is_blind`) | Ours with a narrower wording | "No objective that reads a closed tracker only at the views its training data reach (next-token likelihood, certified-equivalence and next-state terms included) can tell it apart from closed trackers with any prescribed Jacobians there. This is the objective-level, class-free form of the indistinguishability behind compounding-error lower bounds in imitation learning (Simchowitz et al. 2025), and it explains failures observed in training (Block et al. 2023; Howe 2026). Removing scale from the loop (Sharma & Vu 2026) does not remove it." Do **not** present the "architecture or off-distribution probe" dichotomy as ours. | Simchowitz et al. 2025; You et al. 2026; Zhang et al. 2026; instances: Howe 2026, Sharma & Vu 2026, Block et al. 2023 (§1.7) |
| **Theorem 1(b), readout bounds** | Not a contribution: textbook softmax saturation, already conceded to referee T12 | Keep it as a lemma. | standard |
| **Theorem 1(c), excess loss and sharp drift time** | Still ours | "For non-expansive trackers the bound is sharp: a miss ε fails exactly beyond N = m/(√2Kε), and a loss resolved to ρ cannot exclude failure beyond mL/log(1+ρ/s̄)." Quadratic compounding bounds are classical (Ross & Bagnell 2010), so claim only the sharp constant, the factor s̄ and the resolution form. | Ross & Bagnell 2010; Arora et al. 2022 (informal); Rohatgi et al. 2025 (training horizon only) |
| **Corollary 1, finite reads** (`finite_reads`) | Ours with a narrower wording | "Among closed smooth trackers, an objective that reads finitely many values and derivatives, even adaptively, cannot certify the robust condition (C_r) for given radii." Present it as the closed-tracker instance of the classical principle that finitely many observations certify nothing about a continuum without a fault domain (Moore 1956; Back de Luca & Fountoulakis 2026 at fixed input length), not as a discovery. Never write "no such loss certifies exactness at every length", which is refuted (THEOREMS.md §I.4.1). | Moore 1956; Back de Luca & Fountoulakis 2026; Boffi et al. 2020; TaSIL (a finite-order read with a stability assumption) |
| **Theorem 2, robust Myhill–Nerode** (C3; `robustMyhillNerode_full`) | Ours with a narrower wording. The k = 1, p = 0 case is **pre-empted** (Brandoit et al. Thm 3.2, sufficient direction) | "A block-and-prefix form of the cell condition for exactness at every length (Casey 1996; Brandoit et al. 2026). Balls need only map into readout cells within a block of k events and contract at block ends, after a prefix p. Perturbations at block boundaries may depend on the whole history. The automaton may be partial, and views may lie in any pseudometric space." Credit Brandoit for the per-step iff. Note that Bugaud's single invariant set certifies only absorbing-state languages, and per-state cells avoid that limit. Keep `rmn_no_converse`, which is ours. | Brandoit et al. 2026; Casey 1996; Omlin & Giles 1996; Bengio et al. 1994; Bugaud 2026 (workshop) |
| **C2, closure + aimed kick + Nerode training; snapped tracker certified by enumeration** | Ours with a narrower wording | Do not claim very long exact extrapolation, or certificates as such: Bugaud reaches 10⁶ (66,667×) with weight-only certificates on absorbing languages; Brandoit certifies NFSM tables at every length; Howe reaches 1.00 at 16×. Claim instead: "an objective that makes *trained* trackers exact on non-absorbing (group) automata and proof-state rewriting, certified by enumeration. A continuous certificate is not achieved for these group-like automata; the single-invariant-set certificates that work for absorbing languages cannot certify them." | Bugaud 2026a/b; Brandoit et al. 2026; Howe 2026; Simchowitz et al. 2025 (spread data) and DART (isotropic noise) for the kick |
| **Theorem P** (C5; `pinned_regeneration_iff`, `cache_sound`, `regeneration_of_close`) | Ours with a narrower wording. The **sufficiency half is pre-empted** (Cai et al. 2017; Schuurmans et al. 2024; Lewandowski et al. 2026) | "Theorem P turns the bounded-view verification argument of Cai et al. (2017), and the fresh-call induction of Schuurmans et al. (2024) and Lewandowski et al. (2026), into an equivalence. It holds for a pinned KV-cache policy inside one decoding run of a causal decoder, has a margin version for inexact arithmetic, and is proved in Lean." Do not claim the pin (the masking) as new: it is the inductive scratchpad of Abbe et al. 2024. | Cai et al. 2017; Lewandowski et al. 2026; Abbe et al. 2024 (§1.6) |
| **`no_finite_test_suite`** | Ours with a narrower wording | "For decoders that keep the history in context, no finite test suite certifies exactness, even among decoders that pass the per-row certificate and every test with strict margins (exact arithmetic; Lean)." Credit Moore (1956) for the principle and Cai et al. (2017) for the informal claim about carried state. Cite Back de Luca & Fountoulakis (2026: exponential certificates at fixed input length) and Yang et al. (2026: no computable bound) as the learning-theory companions. Add the arithmetic caveat (§1.4). | Moore 1956; Cai et al. 2017; Back de Luca & Fountoulakis 2026; Yang et al. 2026 (§1.6) |
| **C8, the token snaps the state but not the context** | Still ours as a formal statement | Cite Sinha et al. (ICLR 2026, self-conditioning) and Cai et al. 2017 as the empirical and informal precedents, and Veličković et al. 2025 and Xiao et al. 2024 for the dispersion mechanism. | Sinha et al. 2026; Cai et al. 2017 |

**What is new after Cai, Lewandowski, Back de Luca, Abbe and Yang**, in one list (details and
quantifiers in §1.6):

1. **The necessity direction of Theorem P.** It is easy, and it is classical in conformance testing
   (a complete suite must exercise every reachable transition). None of the five states it.
2. **P(1) as a theorem about one decoding run.** A causal decoder whose cache holds Π and is never
   written gives each tick the view (Π, s, e) (`cache_sound`, `cachedForward_eq`). Cai resets the
   LSTM per call, Lewandowski uses fresh calls, and Abbe masks and re-indexes without a proof.
3. **Generality of the sufficiency.** It holds for any closed set of rows, and for Mealy blocks.
4. **Corollary P2.** Certification on one code path transfers to a run whose logits, which may depend on
   the history, are within τ, provided every certified margin exceeds 2τ. Lewandowski assumes
   temperature 0 and fixed seeds on the same stack.
5. **The negative theorem.** No finite suite, however large, certifies unpinned decoding within the
   class of decoders that already pass the per-row certificate with strict margins. In Back de Luca's
   terms, the certification complexity is infinite over unbounded length, where theirs is ≥ 2^t at
   fixed n. In the same terms, Theorem P says it is exactly the number of reachable rows for pinned
   clocks, independent of length.
6. **An explicit one-head mechanism (sink dilution) realising the failure**, with the converse failure
   (`unpinned_exact_not_certified`) and the metric positive version (`unpinned_exact_of_close`).
7. **All of it in Lean.**

---

## 0. Bottom line

- **C1 is not alone.** The imitation-learning theory of 2024–2026 already proves the shape of C1:
  - Simchowitz, Pfrommer and Jadbabaie (COLT 2025) show that the expert distribution cannot tell apart
    instances whose rollouts diverge exponentially. They show that only "improper" policy classes, or
    data spread off the expert's states, escape this.
  - Rohatgi et al. (COLT 2025) prove an Ω(H) barrier for per-step, next-token-style learners.
  - You et al. (2026) and Zhang et al. (2026) state the same zero-training-loss, arbitrary-off-support
    point for world models and for chain of thought.

  C1 adds three things, and it must say so in these terms:
  - it covers *any* objective that reads reached views, including our equivalence and next-state terms;
  - the indistinguishable trackers are closed (they stay on the sphere) and have arbitrarily prescribed
    Jacobians;
  - it carries a sharp excess-loss bound, and it is in Lean.

  C1 must not present the dichotomy "architecture or off-distribution probe" as new.
- **C3 is largely subsumed.** Brandoit et al. (arXiv 2609.32447, 2026) prove an *iff* cell
  characterisation of η-robust exactness at every length. At block length k = 1 and prefix p = 0, our
  robust Myhill–Nerode theorem is a special case of their sufficient direction. Casey (1996) proved the
  necessity direction thirty years ago. What C3 still adds:
  - the block-and-prefix form (perturbations absorbed at block boundaries only);
  - partial automata and pseudometric views;
  - history-dependent perturbations;
  - the Lean proof.
- **Theorem P has direct neural precedents for its sufficiency half.**
  - **Cai, Shin and Song (ICLR 2017)** verify a recursive neural program on a finite "verification set"
    that covers every reachable base case and reduction. They argue that this proves perfect
    generalisation at every length, and they say explicitly that a carried LSTM state is what makes this
    impossible without recursion. That is Theorem P and C8 in informal form.
  - **Lewandowski, Machado and Schuurmans (arXiv 2601.08061, 2026)**, following Schuurmans et al. 2024,
    prove the same sufficiency by induction for Llama-4 run with a fresh call per step. All 1,857 rules
    of a universal Lag system are checked exhaustively.
  - **Abbe et al. (NeurIPS 2024)** already use the pin itself, the "inductive scratchpad" mask, without a
    certificate.
  - **Back de Luca and Fountoulakis (arXiv 2605.22964, 2026)** prove that certification from examples is
    exponentially hard for transformers at a fixed input length.

  §V and §1.6 say exactly what remains ours.

  In conformance-testing terms, Theorem P(2) is the classical fact that a transition cover is a complete
  test when the implementation's state is observable and it has no hidden state. `no_finite_test_suite`
  is Moore's 1956 combination-lock argument applied to decoders. Chen, Ma and Li (ICML 2025) and Yang et
  al. (ICML 2026) restate that argument for length generalisation: no computable length bound exists for
  C-RASP or log-precision transformers.

  What we add:
  - a machine-checked *iff*;
  - the causal-decoder and cache model;
  - the margin version;
  - an explicit attention mechanism (a sink head diluted by length) realising the failure.
- **C2's "no continuous certificate" sentence needs a citation.** Bugaud (two ICML 2026 *workshop*
  papers) certifies small Elman RNNs from their weights alone, with interval-box Kleene iteration and
  CQLF/LMI checks. He reports 100% accuracy at length 10⁶ (about 66,667× training). His necessity result
  confines such certificates to "absorbing-state" languages. Per the ICML listing, a language is
  absorbing-state when its minimal DFA has an accept state that is a sink, and "non-absorbing languages
  … provably cannot admit forward-invariant sets of this form". That restriction is why S5 and our
  group-like tasks need per-state cells and enumeration: a single forward-invariant set cannot certify a
  permutation automaton. The full text was not accessible (OpenReview bot check), so this rests on the
  listing's abstract.
- **C8 has empirical precedent but no formal one.**
  - Sinha et al. (ICLR 2026) name and measure "self-conditioning": errors in the context raise later
    error rates.
  - Cai et al. (2017) state the carried-state obstacle informally.
  - Veličković et al. (ICML 2025) prove the dispersion mechanism that our counterexample's sink head
    uses.

  No source found states "the emitted token snaps the state, not the context" as a theorem.

---

## 1. The five most dangerous papers

### 1.1 Simchowitz, Pfrommer, Jadbabaie. The Pitfalls of Imitation Learning when Actions are Continuous. COLT 2025, PMLR 291:5248–5351. (C1; closeness 3)

URL: https://proceedings.mlr.press/v291/simchowitz25a.html ; arXiv https://arxiv.org/abs/2503.09722
(v4, 26 Jul 2025). Theorems 1–5 and Definitions 3.3–3.5 read in the PDF.

**What it proves.**
- **Theorem 1.** There is a problem family in ℝ^{k+2} whose dynamics and expert closed loop are both
  exponentially incrementally input-to-state stable. On it:
  - (a) some proper algorithm achieves an expert-distribution L2 error of at most C₁εₙ;
  - (b) for every (L, M)-"simple" algorithm (one that returns a policy with state-independent noise and
    an L-Lipschitz, M-smooth mean), some instance has rollout cost at least
    C₂·min{1.05^H εₙ, 1/(ML²)}.
- **Theorem 2.** The same holds on an event of constant probability.
- **Theorem 5.** If the expert's state distribution is "well spread" (a Lipschitz score on a convex set),
  plain behaviour cloning has only polynomial compounding.
- The paper adds two framing points:
  - the bound "depends only on the parameterization of the learned policy … not on the learning
    algorithm";
  - it rests on "the indistinguishability of different stabilizing system dynamics from the perspective
    of the learner" (§3.4). Expert trajectories never excite the direction e₁, so no data distinguishes
    the two gain matrices.

**Overlap with C1.** Both are indistinguishability theorems: the training distribution cannot tell apart
systems whose behaviour away from it differs, so the failure at deployment is invisible to the loss. Both
also name the same two remedies:
- **Their "improper" policy classes** (non-smooth, non-Markovian, action chunking, diffusion) correspond
  to our closure and snap.
- **Their "well-spread" data** corresponds to our probe off the reached states.

**Exact differences.**

| | Simchowitz et al. | C1 (`blindness`, `likelihood_is_blind`, `finite_reads`) |
|---|---|---|
| Object | closed-loop control: an unknown plant f in a family, a learned policy π̂ | a learned tracker F_x on the unit sphere; the target automaton is known |
| What is unseen | the plant's response along an unexcited direction | the tracker's own Jacobians at reached views, and its values off them |
| Quantifiers | ∃ family ∀ simple algorithm ∃ instance with cost ≥ C·min{1.05^H εₙ, 1/(ML²)} | ∀ closed Cⁿ F, ∀ prescribed tangent maps M at reached views, ∀ δ: ∃ closed Cⁿ F′ equal to F on reached views and outside δ, with Jacobians M, and J(F′) = J(F) for every J reading only reached views |
| Learner class | smooth (L, M); the threshold 1/(ML²) shrinks as the class gets rougher | none: F′ need not be representable by the network |
| Failure size | exponential in H, quantified | not quantified by `blindness`; Theorem 1(c)(iv)–(v) give a sharp linear drift time for non-expansive maps |
| Formal status | paper proof | Lean |

**Reword.**
- Present the dichotomy (architecture, or a probe off the reached states) as the state-tracking analogue
  of Simchowitz et al.'s dichotomy (improper policy class, or spread data), and cite them, DART (Laskey
  et al. 2017) and TaSIL (Pfrommer et al. 2022) there.
- Do not write "robustness must come from the architecture" as if the claim were ours.
- Say "a smooth-class version would need a radius" (§5, idea 1).

**What ours adds.**
- **Objective-level and class-free.** C1 covers every functional of reached views: next-token
  likelihood, certified equivalence, next-state prediction and the readout loss at any temperature. That
  is a statement about objectives rather than about learners.
- **Closure is preserved.** The indistinguishable tracker is still closed, so closure alone cannot rescue
  identifiability.
- **Lyapunov exponents.** The Jacobians, and hence the Lyapunov exponents along reached paths, are
  arbitrary.
- **An explicit price.** The excess-loss bound (Theorem 1(c)(ii)) carries the factor s̄, which explains
  why likelihood resolution ρ buys only N ≳ mL/log(1+ρ/s̄).

### 1.2 Brandoit, Fyon, Braipson, Clara, De Geeter, Sacré, Ernst, Drion. Length-Independent State Tracking Under a Parallel Scan. arXiv 2609.32447, 26 Sep 2026. (C3, and C2's certification; closeness 3)

URL: https://arxiv.org/abs/2609.32447 . Definitions and theorems read in the arXiv HTML (§§2–5 and the
appendix references). Already cited in v2 (`brandoit2026length`).

**What it proves.**
- **The setting (Def. 2.2).** A triple (ι, Φ, π) realises an automaton "with length independence at
  finite precision" under a per-step perturbation bound η > 0 when two conditions hold:
  - (T1) decoding is correct at every length along every η-trajectory;
  - (T2) the η-reachable set is bounded.
- **Theorem 3.1, iff.** Length independence holds iff three conditions hold:
  - (R1) the code is decodable;
  - (R2) restoration: Φ_x(U) ⊕ B̄_η ⊆ U;
  - (R3) the transition is correct under every perturbation of size ≤ η.
- **Theorem 3.2, iff.** The same holds iff a bounded U splits into cells U_q with
  Φ_x(U_q) ⊕ B̄_η ⊆ U_{δ_x(q)}.
- **Theorem 3.3.** For every word w, two conditions hold:
  - local contraction: diam Φ_w(U_q) ≤ diam U_{δ_w q} − 2η;
  - global separation: dist ≥ 2η between the images of cells whose states differ.
- **Theorem 4.1.** Affine recurrences either violate restoration or realise only definite automata.
- **Lemma F.17.** Restoration needs a non-affine operation on the previous state.
- **Certification.** The Neural FSM's transition tables are read off the trained logits and checked
  exactly. Props G.2–G.4 and a logit margin that exceeds the computation error give exactness at every
  length.

**Overlap with C3.** Take k = 1, p = 0 and cells U_q = B(c_q, r_q). Our (C_r) gives
F_x(U_q) ⊆ B(c_{q·x}, λr). With η = (1−λ)·min r this yields F_x(U_q) ⊕ B̄_η ⊆ U_{q·x}, which is exactly
their cell condition. So `robustMyhillNerode_cells` with k = 1 is an instance of their sufficient
direction, and their Theorem 3.2 also supplies the converse that our ball form lacks (`rmn_no_converse`).
Their certification route (exact tables plus a margin above the arithmetic error) is also our "snapped
tracker certified by enumeration" route, and their margin step is our Corollary P2 logic.

**Exact differences.**
- **Their side.** The perturbation is per step and its bound η is uniform. The cells are arbitrary
  sets. The statement is an iff, with necessity results (affine, budget, non-affinity).
- **Our side.**
  - Perturbations act only at block boundaries, after a prefix p.
  - Inside a block we require only readout-cell membership, and the tracker may expand within a block.
  - Automata may be partial and views may lie in any pseudometric space.
  - Perturbations may depend on the whole history.
  - Ours is sufficient only: the ball form has no converse.

  A tracker that is exact and absorbs perturbations at block boundaries, but is not per-step η-robust,
  satisfies ours and not theirs. That is the strict generalisation that remains.

**Reword.**
- Call C3 "a block-and-prefix form of the cell condition (Casey 1996; Brandoit et al. 2026)".
- Credit the per-step iff to them. Our Theorem 2 is not the robust Myhill–Nerode theorem.
- PRIMER.md line 280 already says this; the paper should say it in the theorem's lead-in.

**What ours adds.** Block contraction, the prefix, partial automata and history-dependent perturbations,
all in Lean, plus the no-converse result for balls.

### 1.3 Cai, Shin, Song. Making Neural Programming Architectures Generalize via Recursion. ICLR 2017. (C5 Theorem P; C8; closeness 3)

URL: https://arxiv.org/abs/1704.06611 (comment "Published in ICLR 2017"). §3.3 and Appendix A.6 read in
the PDF.

**What it proves.** Verification means checking ∀ i ∈ V, M(i) ⇓ P(i):
- i ranges over step-input sequences within one function call;
- V is the set of valid sequences;
- M is the neural network and P the reference program.

V is built by "iteratively applying the observation-to-observation mapping implied by the reference
implementation", which is a reachability fixed point. The verification set S_V is then run once. The
argument for perfect generalisation is informal but explicit:
- each recursive call "always runs for a fixed number of steps, even on arbitrarily long problems", so
  every step-input sequence that arises in any execution lies in V;
- without recursion, "the core LSTM module's hidden state is preserved over all these ADD1 calls", and
  verification would need "concretely evaluating the LSTM with an input of that length".

The addition verification set has 20,181 problems. The paper's own claim: "the first time one can
provide provable guarantees of perfect generalization for neural programs."

**Overlap with C5 and C8.** The shapes match one for one:

| Cai et al. | Ours |
|---|---|
| "Each call sees only its step inputs" | Theorem P(1), the tick sees only (Π, s, e) |
| V as a reachability fixed point | `Reach δ B s₀` |
| Run M on S_V | per-row certification |
| "A carried LSTM state defeats finite verification" | C8 and `no_finite_test_suite` |

**Exact differences.**
- **Their side.** Theirs is sufficiency only, argued in prose, for an LSTM-based NPI with a reset per
  call, with the reference program P known.
- **Our side.**
  - Ours is an iff (`pinned_regeneration_iff`, necessity via `pinned_certificate_necessary`).
  - P(1) is formalised for a causal decoder with a KV cache that is never written (`cache_sound`).
  - The table Π is written by a language model in context; the decoder is fixed.
  - Corollary P2 adds margins (> 2τ) and Mealy blocks.
  - We give a formal counterexample family for the carried-state case, with an explicit mechanism.

**Reword.** Never write "first certificate of a neural executor at every length". Write instead that
Theorem P gives a machine-checked iff for a pinned transformer clock, and that `no_finite_test_suite`
turns Cai et al.'s informal obstacle into a theorem. Cite Cai et al. in the sentence that introduces
per-row certification, together with Schuurmans et al. 2024 and Lewandowski et al. 2026, who make the
same sufficiency argument for an LLM run with fresh calls. §1.6 gives the quantifier-by-quantifier
comparison.

### 1.4 Moore. Gedanken-Experiments on Sequential Machines. Automata Studies (AM-34), 129–154, 1956; and its descendants in learning theory, Chen, Ma, Li (ICML 2025) and Yang, Bergsträßer, Zetzsche, Chiang, Lin (ICML 2026). (`no_finite_test_suite`, Theorem P(2); closeness 3)

URLs: https://doi.org/10.1515/9781400882618-006 (Crossref) ; https://proceedings.mlr.press/v267/chen25ar.html
(PMLR 267:8621–8682) and https://arxiv.org/abs/2506.03085 ; https://arxiv.org/abs/2603.02238 and
https://icml.cc/virtual/2026/poster/63411 .

Moore's text was not read; the conformance-testing reading is from Vaandrager and Melse (CONCUR 2025,
arXiv 2410.19405), which was read. The Chen–Ma–Li theorems were read in the arXiv HTML (Def. 3.9,
Prop. 3.10, Lemma 4.5, Prop. 4.6, Thm 5.5). The Yang et al. theorems were read in the arXiv HTML
(Def. 2.5, Prop. 2.6, Thm 3.1, Cor. 3.6, Thms 4.7, 5.1, 5.2).

**What they prove.**
- **Conformance testing (Moore 1956; Hennie 1964; Vasilevskii 1973; Chow 1978).** No finite test suite
  is complete without a fault domain. An implementation "may behave like 𝒮 for the first N inputs, but
  differently from that point onwards" (Vaandrager and Melse §1, on Moore's combination locks). With a
  bound of m states, m-complete suites exist.
- **Chen–Ma–Li.** For DFAs with c states, training data up to length 2c − 2 suffices (Prop. 3.10). For
  context-free grammars no computable bound exists (Prop. 4.6). A computable bound exists iff
  equivalence is decidable (Lemma 4.5).
- **Yang et al.** Two-layer C-RASP and (1, log n)-precision transformers have no computable
  length-generalisation bound (Cor. 3.6, Thm 5.1). Fixed-precision transformers do have one, and it is
  exponential and optimal (Thm 5.2).

**Overlap.**
- **`no_finite_test_suite`.** Its form is "∀ finite set C of contexts, ∃ decoder passing the certificate
  and every test with strict margins, wrong later". That is the combination-lock statement over the
  fault domain "decoders that pass the per-row certificate".
- **Theorem P(2).** It is the classical fact that when the implementation's state is observable (the
  emitted state token) and it has no hidden state (P(1)), checking each reachable transition once is
  complete. The fault domain is then the spec's own n states, and the W-method degenerates to a
  transition cover. This last reading is mine; I did not check it against the Lee–Yannakakis survey
  text.

**Exact differences.**
- Moore's result concerns black-box machines with unknown state counts. Ours concerns a concrete
  parametric family: a correct lookup plus one sink-attending head whose write
  4R(k+2)/(e^c+2k+6) falls with length. Every member passes a fixed, strong certificate with strict
  margins.
- Yang et al.'s result is about computability across a class under an idealised learner. Ours is about
  existence for every finite suite, in exact real arithmetic.

**A caveat to state in the paper.** By Yang et al. Thm 5.2, fixed-precision transformers admit a
computable (exponential) bound. Our counterexample needs the crossing length (e^c−2)/2 to exceed any
given suite, so c must be unbounded. That needs exact arithmetic or unbounded precision. Under any fixed
precision a finite, but exponentially long, suite exists in principle. State the arithmetic model next
to the theorem ("over the reals; under fixed precision the obstruction becomes exponential cost, by Yang
et al.").

**What ours adds.**
- The fault domain is not "all machines" but decoders that already pass the per-row certificate and
  every finite test with strict margins.
- A one-head attention mechanism realises the failure.
- The converse also fails (`unpinned_exact_not_certified`).
- A metric positive version exists (`unpinned_exact_of_close`).
- All of it is in Lean.

### 1.5 Bugaud. (a) Which Regular Languages Admit Provably Correct RNN Implementations? A Lattice-Theoretic Characterisation via Forward-Invariant Sets; (b) Combining Theory and Benchmarks for Length Generalisation: Formal Certificates Meet Large-Scale Evaluation. ICML 2026 workshop posters. (C2, C3; closeness 2–3)

URLs: (a) https://icml.cc/virtual/2026/82548 (3rd AI for Math Workshop; OpenReview
https://openreview.net/forum?id=L4kh17ZuSa); (b) https://icml.cc/virtual/2026/68270 (Workshop "Combining
Theory and Benchmarks"; OpenReview https://openreview.net/forum?id=shPakbYAoQ).

Only the abstracts on the ICML pages were read. OpenReview and the PDFs were behind a browser challenge,
which I did not attempt, and there is no arXiv version. **Correction:** NOVELTY.md lists (a) as "ICML
2026"; it is a workshop paper.

**What they claim.**
- **(a)**
  - For Elman RNNs, length generalisation under a forward-invariant certificate is equivalent to the
    existence of a forward-invariant positive-margin set.
  - The languages that admit such implementations lie within the "absorbing-state" languages (closed
    under union and intersection, not under complement).
  - The page says that "necessity is proven, while the converse is supported empirically", which
    conflicts with the abstract's "if-and-only-if".
  - Kleene iteration on axis-aligned boxes converges in about 14 iterations, and CQLF certificates
    verify 109/110 models.
- **(b)**
  - A gap-suppression mechanism plus a margin condition certify generalisation "from the weights alone".
  - Certified models reach 100% at L = 1,000,000 (about 66,667× training) on 10/10 seeds, with zero
    false positives at H ≥ 4k.
  - The certificate, inverted, becomes a training recipe that works for k = 3–10 and 12.
  - The recipe fails on non-absorbing DFAs; GRU and LSTM resist certification; capacity shortfalls give
    false positives.

**Overlap.**
- C2 says "a continuous certificate is not achieved". Bugaud achieves a continuous, weight-only
  certificate and a far-extrapolation headline (66,667×), and he turns the certificate into a training
  objective, as Nerode training does.
- C3 and (a) are both forward-invariance conditions.

**Exact differences** (from the listings; the definitions in the full text could not be read).
- **The model.** (a) models the Elman RNN as the switched system h_{t+1} = tanh(W_hh h_t + u_{x_t}).
  "Absorbing-state" means the minimal DFA has an accept state q_a with δ(q_a, σ) = q_a for every σ.
- **(a) certifies one invariant set.** A single forward-invariant positive-margin set certifies "once in
  the accepting region, stay there", which is why the admissible class is the absorbing-state languages.
  The listing also gives a gap formula, gap_d ≈ sech²(z̄_d)·|Δz_d| (r = 0.743), as an analytic
  sufficient condition.
- **C3 uses a family of cells.** C3 uses one ball per automaton state, mapped into one another along
  transitions, so it covers permutation automata (S5, parity with contraction).
- **Different tasks.** Bugaud's tasks are absorbing regexes on small Elman RNNs; ours are group word
  problems, Lean rewriting and arithmetic.

**Reword.** Write: "for group-like automata we found no continuous certificate. Bugaud (2026) certifies
small Elman RNNs from their weights, but only for absorbing-state languages, which a single invariant set
can certify." Do not write that continuous certificates are unachieved in general.

**What ours adds.** Per-state cells for non-absorbing automata, exactness at length on S5 and Lean, and
proofs in Lean. Bugaud's proofs are on paper, and the workshop format is unreviewed or lightly reviewed.

**Honourable mentions** (just outside the five):
- Rohatgi et al. (COLT 2025): the next-token barrier, against C1's likelihood clause (§2.2).
- Casey (1996): the necessity direction of C3 (§2.7).
- Bengio, Simard and Frasconi (1994): the robust-latching clause with the same (1−λ) absorption as C3,
  and the latching–gradient trade-off (§2.8).
- Sinha et al. (ICLR 2026): self-conditioning, against C8 (§2.11).
- Lewandowski, Machado and Schuurmans (2026): the sufficiency half of Theorem P on Llama-4 (§1.6).
- Back de Luca and Fountoulakis (2026): certification from examples is exponentially hard, the companion
  of `no_finite_test_suite` (§1.6).

### 1.6 Theorem P (both directions) and `no_finite_test_suite`, quantifier by quantifier

**Sources.**
- **Cai, Shin, Song (ICLR 2017).** §3.3 and App. A.6 read in the PDF.
- **Lewandowski, Machado, Schuurmans. Universal computation is intrinsic to language model decoding.**
  arXiv 2601.08061, v2.
  - https://arxiv.org/abs/2601.08061
  - Theorem 1 (App. C/F), Corollary 2, §§5–6 and the App. F induction were read in the HTML.
  - Its predecessor, Schuurmans, Dai, Zanini, *Autoregressive Large Language Models are Computationally
    Universal*, https://arxiv.org/abs/2410.03170 (2024), was verified by the arXiv API.
- **Back de Luca, Fountoulakis. Certification from Examples is Hard for Circuits and Transformers under
  Minimal Overparametrization.** arXiv 2605.22964, 21 May 2026.
  - https://arxiv.org/abs/2605.22964
  - The certificate definition, Theorems 4.1 and 4.2, Proposition 4.2 and Lemma A.1 were read in the
    HTML (first 100k characters).
- **Abbe, Bengio, Lotfi, Sandon, Saremi. How Far Can Transformers Reason? The Globality Barrier and
  Inductive Scratchpad.** NeurIPS 2024.
  - https://arxiv.org/abs/2406.06467 (comment "To appear in NeurIPS 2024")
  - The inductive-scratchpad section was read in the HTML.
- **Yang et al. (ICML 2026)** and **Chen, Ma, Li (ICML 2025)**: §1.4.

**Our statements** (THEOREMS.md Part VI):

- **P(2), sufficiency** (`pinned_regeneration`): ∀ causal decoder D, ∀ argmax selection, ∀ table δ,
  ∀ Q closed under δ from s₀ over B:
  [∀ (s,e) ∈ Q×B: tick_D(Π,s,e) = δ(s,e)] ⇒ ∀ T, ∀ tape ∈ B^T: the clock's trace equals δ's trace.
- **P(2), necessity** (`pinned_certificate_necessary`):
  [∀ T, ∀ tape ∈ B^T: the final state is δ's] ⇒ ∀ (s,e) reachable from s₀: tick_D(Π,s,e) = δ(s,e).
  Together with sufficiency this gives `pinned_regeneration_iff`.
- **P(1)** (`cache_sound`, `cachedForward_eq`): with Π prefilled once and never written, tick i's logits
  are forward_D(Π ++ [s,e]), so they depend on neither i nor T nor the history.
- **P2** (`regeneration_of_close`): if ∀ h, s, e: |L_run(h,s,e) − L_cert(s,e)|_∞ ≤ τ, and every row
  of a closed Q×B has margin > 2τ, then the run is exact on every tape.
- **`no_finite_test_suite`**: ∀ finite set C of contexts, each extending Π and ending in a row [s, a]
  (any lengths, any earlier states), ∃ D in the family "correct lookup + one sink head" such that all
  three hold:
  - D passes the per-row certificate with strict margins;
  - D's step is right with strict margins at every context in C;
  - ∃ a tape on which unpinned decoding with D is wrong.

**Comparison.**

| Work | Direction | Quantifiers and object | Assumption doing the work | Necessity? | Negative result? | Formal? |
|---|---|---|---|---|---|---|
| Cai et al. 2017 | sufficiency | [∀ i ∈ V: M(i) ⇓ P(i)] ⇒ ∀ valid inputs, M is correct. V = the step-input sequences reachable from valid inputs, computed as a fixed point of the reference program's observation map. | Recursion makes each call run a fixed number of steps on a bounded observation, so the per-call behaviour of the NPI depends only on that call's step inputs. | no | informal: a non-recursive LSTM carries hidden state, so verification would need "concretely evaluating the LSTM with an input of that length" | prose proof |
| Schuurmans et al. 2024; Lewandowski et al. 2026 | sufficiency | Thm 1 / Cor. 2: [∀ rules r of U(15,2) (1,857, enumerated): model(S E(s₁)E(s₂)) = E(output_r)] ⇒ ∀ inputs, iterated decoding simulates the Lag system exactly (induction on steps). | Temperature 0, fixed seeds, an injective codebook, and a **fresh call per step** whose context is the system prompt plus the current pair. The system prompt was found by search with feedback on failing rules. | no | none; history in context is "not analysed" | paper proof (an enumeration plus induction) |
| Abbe et al. 2024 | mechanism | Each new state sees only the question and the previous state, via attention masking and position re-indexing (or by deleting earlier states); training uses the same view. | the same bounded view | — | — | no theorem; empirical (parity 30→50–55 bits; addition 10→18 digits, 4→26 with shifts) |
| Back de Luca & Fountoulakis 2026 | lower bound | Def.: S is a certificate for f* in H if every h ∈ H consistent with f* on S equals f* on all of 𝒳; cert(f*, H) = min\|S\|. Thm 4.1 / 4.2: ∀ n, ∀ f* in the base class (depth-d threshold circuits of size s, or AHAT transformers on {0,1}^n), ∀ t ≤ n: cert(f*, base class + one gate, or + one head and six coordinates) ≥ 2^t. Lemma A.1: in every finite H some f has cert ≤ ⌈log₂\|H\|⌉. | fixed input length n, one output bit, black-box labelled examples | — | yes: exponential in n | paper proofs |
| Yang et al. 2026 | non-computability | ∄ computable N(c) such that any two distinct depth-2 C-RASP programs of size ≤ c are distinguished by a string of length ≤ N(c). The same holds for (1, log n)-precision transformers. Fixed precision: an exponential N exists (Thm 5.2). | idealised learner; language recognition | — | yes: not computable | paper proofs |
| Moore 1956; Chow 1978; Vaandrager & Melse 2025 | completeness of test suites | No finite suite is complete for all machines. Under an m-state fault domain, m-complete suites exist. | black-box machines with unknown state counts | trivially (a complete suite must cover every transition) | yes | classical |
| **Ours** | **iff, plus a negative result** | as above | **P(1) derived for a causal decoder with a cache that is never written** | **yes** | **yes, within the class that passes the per-row certificate** | **Lean** |

**What each paper takes from our claim.**

- **Cai et al.** have the sufficiency logic (Theorem P(2) ⇐) and the reachability construction (our
  `Reach`), and they state C8's obstacle informally.
- **Lewandowski et al.** have the sufficiency logic on a modern open-weights LLM (Llama-4-17B-128E),
  with the per-rule check exhaustive. Their fresh-call harness is our pin, realised as an outer loop.
  Their silent dependence on fresh calls is exactly what `no_finite_test_suite` shows is load-bearing.
  L1's suggested demonstration (L1 §1.1(b)) would show the theorem on their own construction: run their
  1,857 certified rules with history kept in context, unpinned.
- **Abbe et al.** have the pin as a training-and-inference mechanism, with no certificate and no
  guarantee.
- **Back de Luca and Fountoulakis** have the hardness of black-box certification for fixed-length
  inputs.
  - Our negative result is of the same type, but over unbounded length (certification complexity ∞
    rather than ≥ 2^t) and within a stronger fault domain (decoders that pass the per-row certificate).
  - Our positive result is the escape their paper does not consider. Under P(1), the class of pinned
    clocks has certification complexity *exactly* the number of reachable rows (sufficiency plus
    necessity), independent of tape length.
  - Their non-vacuity results and ours are consistent: theirs needs the input dimension to grow; ours
    needs the context to grow.
- **Yang et al.** have non-computability for learning. Ours concerns verifying a given decoder. Their
  fixed-precision positive result bounds what `no_finite_test_suite` can mean under finite precision
  (§1.4).

### 1.7 Instances of C1 that predate our proof: Howe 2026, Sharma & Vu 2026, Block et al. 2023

**Sources.**
- **Howe. The Automaton Underneath: The Additive Input Pathway Is a Parasitic Attractor for State Tracking
  in Householder Linear RNN.** arXiv 2609.18966 (submitted 16 Jul 2026).
  - https://arxiv.org/abs/2609.18966
  - The abstract and the §5 arm "E3" were read in the HTML.
- **Sharma, Vu. Dense Supervision Is Not Enough: The Readout Blind Spot in Looped Language Models.**
  arXiv 2606.24898 (12 Jun 2026).
  - https://arxiv.org/abs/2606.24898
  - Lemmas 1–2 and Eqs. 3–4 were read in the HTML.
- **Block et al. 2023**: entry 23.

**What they show.**
- **Howe, E3.** Started at a verified exact solution with W_b = 0, Adam grows the additive path
  (‖W_b e‖ → 0.41 on parity, 0.77 on S5) and position-512 accuracy falls to 0.50 and 0.23. The −b
  controls stay at 1.00. Zeroing W_b at inference keeps in-domain fit in all 49 fitting seeds and
  restores exactness at law-minimal width. There is no theorem, and the paper does not frame this as
  loss blindness.
- **Sharma & Vu, Lemma 1.** If r(αH) = r(H) for all α > 0 and ℒ(H) = CE(W_out r(H), y) is
  differentiable at H ≠ 0, then ⟨∇_H ℒ, H⟩ = 0. This is pointwise, at every H.
- **Sharma & Vu, Lemma 2.** Pre-norm residual recurrence updates the scale anyway. The paper analyses
  no Jacobian of the recurrence and no length.
- **Block et al.** Minibatch SGD noise barely moves the behaviour-cloning loss but causes large swings in
  long-horizon reward. The paper is empirical, with convex-model vignettes.

**Does Theorem 1 generalise them or do they pre-empt it?** Neither pre-empts it, and Theorem 1
generalises only the *indistinguishability* content, not the optimiser dynamics.

- **Howe and Block.** These perturbations change the values at reached states slightly; they do not keep
  them fixed. They are therefore covered by Theorem 1(c), not 1(a):
  - a miss ε at the exact views costs at most s̄(e^{√2KεL} − 1) in loss over the training horizon;
  - yet it fails beyond m/(√2Kε) (sharp for non-expansive maps, by (iv));
  - and by (v), a loss resolved to ρ cannot exclude this failure.

  That is the quantitative reason Howe's drift is "harmless in-domain and fatal out-of-distribution".
  Two things lie beyond our theorems:
  - that Adam actively *moves* along the blind direction (C1 "does not say what gradient descent
    finds");
  - that the culprit is the additive path. Howe's linear RNN is also not a closed tracker.
- **Sharma and Vu.** Theirs is a *static* blind spot: one direction, the radial scale, invisible to the
  readout at every state. Ours is *dynamic*: Jacobians and values away from reached views, invisible to
  every reached-view objective, for **closed** trackers in which the radial direction has already been
  removed. Their recommended architectural fix, "scale-removing recurrence", is our closure.
  - **What follows.** Theorem 1(a) shows that their fix does not end the blindness, because tangent
    Jacobians stay free. Their Lemma 1 is the scale-invariance instance of our corollary that every
    per-view loss g of the normalised view is constant along rays.
  - **Cite them in the closure sentence:** "closure removes the radial blind spot (Sharma & Vu 2026);
    Theorem 1 shows the tangent one remains".
- **Wording for C1.** Cite all three, with Simchowitz et al., as instances or precedents. Claim the
  objective-level, closed-tracker, prescribed-Jacobian theorem and the sharp drift bound, in Lean.

---

## 2. Theorem-level comparisons for the next closest papers

### 2.1 Pfrommer, Zhang, Tu, Matni. TaSIL: Taylor Series Imitation Learning. NeurIPS 2022. (C1; closeness 2)

https://arxiv.org/abs/2205.14812 (comment "Appeared at NeurIPS 2022"); abstract read.

**What it shows.** TaSIL penalises mismatch of higher-order Taylor terms (Jacobian, Hessian and so on)
between learner and expert on expert trajectories. If the expert closed loop is incrementally
input-to-state stable (δ-ISS), a small TaSIL loss implies a small loss on the learner's own trajectories.

**Relation to C1.** TaSIL is the canonical objective that reads Jacobians at reached states, so it
targets exactly the gap `likelihood_is_blind`(2) exposes. It is still inside `finite_reads` (finitely
many derivatives at finitely many points), so it cannot certify (C_r) for given radii over all smooth
trackers. Its guarantee is imported from the expert's δ-ISS and, in the body, smoothness of the class.

**Implication.** State that C1 and Corollary 1 are class-free, and that with a bounded-smoothness class,
derivative-matching objectives do control a neighbourhood whose radius scales with margin/smoothness
(§5, idea 1).

### 2.2 Rohatgi, Block, Huang, Krishnamurthy, Foster. Computational-Statistical Tradeoffs at the Next-Token Prediction Barrier. COLT 2025 (extended abstract), PMLR 291:4831–4837. (C1; closeness 2)

https://proceedings.mlr.press/v291/rohatgi25a.html ; https://arxiv.org/abs/2502.12465 . §4 read in the
arXiv HTML.

**What it proves.**
- **The target.** The goal is D²_H(P^π̂, P^π⋆) ≤ C_apx · min_π D²_H + ε_stat.
- **Log-loss BC.** It reaches C_apx ≈ H log W/δ, and that is tight.
- **The barrier (§4.3, Eq. 19).** For every *iterative* proper learner (π̂_h a function of π⋆_{1:h} and
  π̂_{1:h−1}, no parameter sharing), some π⋆ forces C_apx = Ω(H), with misspecification 2^{−H}.
- **Linear models.** Sub-polynomial C_apx is computationally hard.

**Relation to C1.** Both say per-step objectives cannot control sequence-level error. Theirs is
statistical, at the training horizon H, under misspecification, with Hellinger distance. Ours is
deterministic and realisable (an exact tracker exists). It concerns extrapolation to N ≫ L, and its
loss-resolution statement (Theorem 1(c)(v)) has no counterpart in their framework.

**Companion.** Xu, Yuan and Zhan (arXiv 2605.12316, 2026) show that the Ω(H) approximation
amplification disappears under joint KL; the amplification is a property of the divergence. When we say
"likelihood cannot see drift", specify the horizon: at the training horizon likelihood is horizon-free;
beyond it, it is blind.

### 2.3 Foster, Block, Misra. Is Behavior Cloning All You Need? Understanding Horizon in Imitation Learning. NeurIPS 2024. (C1; closeness 2)

https://arxiv.org/abs/2407.15007 ; abstract read.

**What it shows.** With log loss, offline behaviour cloning has horizon-independent sample complexity
when the payoff range and the supervised complexity are controlled (realisable setting). Online IL cannot
improve on it without further assumptions.

**Relation to C1.** A reviewer will raise this against "likelihood prices drift weakly". It does not
conflict with C1: the guarantee is at the training horizon and in trajectory-level Hellinger distance.
C1 is about what the same loss implies for lengths it never evaluated.

### 2.4 You, Zhang, Ran, Yang, Zhang, Xue, Song, Tian, Guo. A Control Theory of Predictability in Latent World Models. arXiv 2607.10362, Jul 2026. (C1; closeness 2)

https://arxiv.org/abs/2607.10362 ; Lemmas 1–2 read in the HTML.

**What it proves.**
- **Lemma 1.** If ν places mass off supp μ, the error under μ gives no bound on the error under ν. The
  construction sets ε ≡ 0 on supp μ and leaves it free elsewhere.
- **Lemma 2.** A "hole" (a candidate that looks best in prediction yet is bad) bounds decision regret,
  and rollout training "which reduce[s] exposure bias on the support" leaves holes unchanged.
- **Theorem H5 (title only):** "Exposure Bias Is Orthogonal to Holes."

**Relation to C1.** This is the same off-support decoupling for world models. It has no closure, no
Jacobian prescription and no formalisation. Cite it in the C1 paragraph as concurrent.

### 2.5 Zhang, Dong, Cesari, Mao. On the Cost and Benefit of Chain of Thought: A Learning-Theoretic Perspective. arXiv 2605.21260, May 2026. (C1; closeness 2)

https://arxiv.org/abs/2605.21260 ; abstract read.

**What it proves.** The reasoning risk splits into oracle-trajectory risk and trajectory-mismatch risk.
If the loss, the answer map or the chain rule lacks stability, the mismatch risk "can be arbitrarily
large even when the OTR is zero and the hypothesis is uniformly close to the ground truth". Under
stability, an amplification factor separates bounded, linear and exponential regimes.

**Relation to C1.** This is the chain-of-thought form of "zero loss on reached states, arbitrary failure
off them", together with our Theorem 1(c) regimes (linear under non-expansion,
`theoremA_false_without_nonexpansion` otherwise). Cite it next to Theorem 1(c).

### 2.6 Chung, Choi, Kim. Rethinking State Tracking in Recurrent Models Through Error Control Dynamics. NeurIPS 2026. (C1, C3; closeness 1–2)

https://arxiv.org/abs/2605.07755 (journal_ref "NeurIPS 2026"); Theorem 1 and Corollary 1 read in the
HTML. Already cited in v2 as a preprint; **update the venue**.

**What it proves.**
- **Theorem 1.** If a state-preserving return map is affine and fixes the reference codes c*_g, then
  A_s restricted to their difference span 𝒰 is the identity, so affine trackers cannot contract errors
  along 𝒰.
- **Corollary 1.** Coherent residuals accumulate linearly.

**Scope.** It has no statement about objectives, no certificate and no training method. Training ran to
length 60 and evaluation to 1,000.

**Relation to C1 and C3.** It supports the closure (non-affine) half of C1 and C3. It does not touch the
blindness theorem's objective-level content.

### 2.7 Casey. The Dynamics of Discrete-Time Computation, with Application to Recurrent Neural Networks and Finite State Machine Extraction. Neural Computation 8(6):1135–1178, 1996. (C3; closeness 2)

https://doi.org/10.1162/neco.1996.8.6.1135 (Crossref). The abstract was read via
https://mlanthology.org/neco/1996/casey1996neco-dynamics ; the full text is paywalled. Brandoit et al.
cite it for "η-pseudo-orbit analysis under bounded noise".

**What it proves.** An RNN performing a finite-state computation must organise its state space to
mirror the minimal DFA, and the paper describes the attractor structure precisely. This is the necessity
direction that our C3 lacks (`rmn_no_converse`), and it is the basis of our injectivity remark (I.5.2).

**Relation to C3.** Our Theorem 2 is the sufficiency counterpart for any closed tracker, with blocks
and a prefix. Already cited in v2.

### 2.8 Bengio, Simard, Frasconi. Learning Long-Term Dependencies with Gradient Descent is Difficult. IEEE TNN 5(2):157–166, 1994. (C3, C1; closeness 2)

https://doi.org/10.1109/72.279181 (Crossref). The primary text was not read. The definitions below come
from a course presentation of the paper
(https://cs.nyu.edu/~yann/2006s-G22-3033-013/diglib/ayse_mkg_bengio_recurrent.pdf, read): "robustly
latched", maximum shrinkage rate λ, and the image "will remain within a radius d … as long as
‖u_t‖ < (1−λ)d".

**Relation to C3.** That is the absorption clause of C3, (1−λ)·min r, in the 1994 paper.

**Relation to C1.** The paper's dichotomy (robust latching forces vanishing gradients with respect to
earlier states) is a training-dynamics companion of blindness: once latched, the gradient no longer sees
the basin choice.

**Implication.** Cite it in the robust Myhill–Nerode paragraph. Note that our aimed kick acts on the
current state, so it does not rely on gradients through the latched past.

### 2.9 Omlin, Giles. Constructing Deterministic Finite-State Automata in Recurrent Neural Networks. JACM 43(6):937–972, 1996; and Stable Encoding of Large Finite-State Automata … Neural Computation 8(4):675–696, 1996. (C3; closeness 2)

https://doi.org/10.1145/235809.235811 ; https://doi.org/10.1162/neco.1996.8.4.675 (Crossref). JACM
§5 read in the PDF (Theorems 5.7.2 and 5.10.2, Corollaries 5.7.3 and 5.10.3).

**What it proves.**
- **The construction.** For a DFA with n states and m symbols, a second-order sigmoid network with n+1
  state neurons and weights ±H classifies strings of arbitrary length correctly if the low and high
  fixed points satisfy explicit inequalities and H > max(H₀⁻(n), H₀⁺(n)) (Thm 5.7.2, Cor. 5.7.3).
- **Noisy weights.** With random extra weights in [−W, W], the same holds under adjusted conditions
  (Thm 5.10.2).
- **The proof.** It shows that the low and high signal intervals are forward-invariant under the worst
  case.

**Relation to C3.** This is C3 with k = 1, specialised to one constructed architecture with
programmed weights. **Gap in v2:** the paper cites Omlin and Giles's *extraction* paper (Neural Networks
1996), not this stability result. Add JACM 1996 (and Carrasco et al. 2000).

### 2.10 Bakija, De Geeter, Brandoit, Sacré, Drion. Train Short, Act Long: Multistability and the Horizon Independence of Recurrent Policies. arXiv 2605.12206, May 2026 (v2 Oct 2026). (C3, C1; closeness 2)

https://arxiv.org/abs/2605.12206 ; abstract read.

**What it shows.**
- A recurrent policy is delay-horizon independent iff it admits a continuous readout of memory that is
  invariant under the idle dynamics and separates the cues.
- Monostable memory, including contracting affine SSMs and gated linear RNNs, precludes this at every
  parameter value.
- Multistable models trained short stay optimal to 10⁶ steps.

**Relation to C3.** This is the RL form of "exactness needs separated attracting cells". It comes from
the same Liège group as Brandoit et al., which is now the strongest competing theory group on C3.

### 2.11 Sinha, Arun, Goel, Staab, Geiping. The Illusion of Diminishing Returns: Measuring Long Horizon Execution in LLMs. ICLR 2026. (C8; closeness 2)

https://arxiv.org/abs/2509.09677 (comment "Published at ICLR 2026"); abstract read. Cited in v2 as a
preprint; **update the venue**.

**What it shows.** "Models become more likely to make mistakes when the context contains their errors
from prior turns" (self-conditioning). Scale does not remove it; thinking does.

**Relation to C8.** This is the empirical phenomenon C8 explains: the history is a second, unsnapped
state, and `no_finite_test_suite` builds a decoder whose drift comes only from it. Cite it at C8 as
evidence. Our contribution there is the formal statement and the pinned clock's immunity (P(1)).

### 2.12 Veličković, Perivolaropoulos, Barbero, Pascanu. Softmax is not Enough (for Sharp Size Generalisation). ICML 2025. (C8, `no_finite_test_suite` mechanism; closeness 1–2)

https://arxiv.org/abs/2410.01104 ; abstract read.

**What it proves.** Any learned softmax circuitry "must disperse as the number of items grows".

**Relation to our counterexample.** Our counterexample's head is a sink-attending head whose write
falls as 1/(e^c + n). It is a concrete instance of this dispersion turned against the certificate. Cite
it, together with attention sinks (Xiao et al. ICLR 2024) and over-squashing (Barbero et al. 2024), when
explaining why the unpinned run drifts.

### 2.13 Huang, Yang, Bhattamishra, Sarrof, Krebs, Zhou, Nakkiran, Hahn. A Formal Framework for Understanding Length Generalization in Transformers. ICLR 2025. (C2, C5; closeness 1–2)

https://arxiv.org/abs/2410.02140 ; Def. 6 and Thm 7 read in the HTML.

**What it proves (Thm 7).** f is expressible by a Limit Transformer with periodic and local positional
terms iff the idealised inference procedure (fit all inputs up to length n/2, near-minimise a norm and
precision regulariser) yields T_n that, for some N₀ and all m > N₀, match f on all inputs up to length m.
No bound on N₀ is given; Yang et al. 2026 show none is computable.

**Relation to C2 and C5.** It is the "generalisation in the limit" baseline against which Theorem P's
finite certificate is the point: pinning reduces the obstruction to |reachable rows| one-step checks.

---

## 3. Annotated list

Format:
- citation, venue, verified URL, accessed 28 Oct 2026;
- what it shows;
- **closeness (0–3), claim**;
- implication for us.

"Abstract" or "theorem read" says what was read.

### A. Exposure bias, compounding error, next-token objectives (C1)

1. **Bengio, Vinyals, Jaitly, Shazeer. Scheduled Sampling for Sequence Prediction with Recurrent Neural
   Networks. NIPS 2015.** https://arxiv.org/abs/1506.03099 .
   Feeds the model's own predictions back during training to reduce the train–test mismatch.
   **1, C1.** It moves the training distribution, but it still trains on reached states, now the model's
   own. C1 covers it, because only reached views are read.

2. **Ranzato, Chopra, Auli, Zaremba. Sequence Level Training with Recurrent Neural Networks.**
   https://arxiv.org/abs/1511.06732 (venue ICLR 2016 per common citation; not verified here).
   MIXER trains with sequence-level REINFORCE on the model's own samples.
   **1, C1.** Same point as scheduled sampling: own-distribution training is still a reached-state
   objective.

3. **Lamb, Goyal, Zhang, Zhang, Courville, Bengio. Professor Forcing. NIPS 2016.**
   https://arxiv.org/abs/1610.09038 .
   An adversarial loss matches hidden-state dynamics under teacher forcing and free running.
   **1, C1.** It reads hidden states on reached trajectories (both modes), so it remains within
   `likelihood_is_blind`'s class. Mention it as the first "match dynamics" objective.

4. **Ross, Bagnell. Efficient Reductions for Imitation Learning. AISTATS 2010, PMLR 9:661–668.**
   https://proceedings.mlr.press/v9/ross10a.html .
   Behaviour cloning's regret "grows quadratically in the time horizon".
   **2, C1.** The canonical compounding bound. Our Theorem 1(c)(i) gives linear drift under
   non-expansion and exponential drift without it; contrast the two.

5. **Ross, Gordon, Bagnell. A Reduction of Imitation Learning and Structured Prediction to No-Regret
   Online Learning (DAgger). AISTATS 2011.** https://arxiv.org/abs/1011.0686 .
   Training on the learner's own state distribution gives linear regret.
   **2, C1.** Already in LITERATURE.md. DAgger's fix is a coverage fix; ours is a robustness fix
   (closure plus an off-trajectory probe).

6. **Venkatraman, Hebert, Bagnell. Improving Multi-Step Prediction of Learned Time Series Models. AAAI
   2015.** https://doi.org/10.1609/aaai.v29i1.9590 (Crossref).
   "Data as Demonstrator" retrains a one-step model on its own multi-step predictions, with a
   DAgger-style bound.
   **1, C1/C2.** The world-model ancestor of next-state training at length. Cite it with Brandstetter's
   pushforward trick.

7. **Arora, El Asri, Bahuleyan, Cheung. Why Exposure Bias Matters: An Imitation Learning Perspective of
   Error Accumulation in Language Generation. Findings of ACL 2022.** https://arxiv.org/abs/2204.01171 .
   Imports the Tε ≤ regret ≤ T²ε bounds and defines AccErr. It argues *informally* (no theorem) that
   perplexity is linear in average per-step error and so cannot see accumulation.
   **2, C1.** This is the informal ancestor of our likelihood clause; our Theorem 1(c)(ii) is the formal
   version, with the factor s̄. Cite it.

8. **Schmidt. Generalization in Generation: A closer look at Exposure Bias. WNGT 2019.**
   https://arxiv.org/abs/1910.00292 .
   Argues that exposure bias is a generalisation problem, not a train–test mismatch per se.
   **1, C1.** Consistent with C1: what matters is behaviour off the reached set.

9. **He, Zhang, Zhou, Glass. Exposure Bias versus Self-Recovery: Are Distortions Really Incremental for
   Autoregressive Text Generation? EMNLP 2021.** https://arxiv.org/abs/1905.10617 .
   Measures exposure bias in open-ended generation and finds self-recovery.
   **1, C1/C8.** A rebuttal of inevitable compounding. In C1's language, language models are partly
   contracting on content; our point is that the objective does not select that contraction.

10. **Zhang, Press, Merrill, Liu, Smith. How Language Model Hallucinations Can Snowball.**
    https://arxiv.org/abs/2305.13534 (venue not verified).
    Models over-commit to early mistakes they can recognise separately (67% and 87%).
    **1–2, C8.** Context as an unsnapped state, empirically.

11. **Bachmann, Nagarajan. The Pitfalls of Next-Token Prediction. ICML 2024.**
    https://arxiv.org/abs/2403.06963 .
    Teacher forcing can fail to learn the right next-token predictor at all (the "Clever Hans" cheat on
    path-star graphs), beyond inference-time compounding.
    **2, C1.** Already flagged in LITERATURE.md. The difference: theirs is a learnability failure on
    in-distribution data; C1 is objective indistinguishability off-distribution. Cite both phases
    explicitly.

12. **Dziri et al. Faith and Fate: Limits of Transformers on Compositionality. NeurIPS 2023.**
    https://arxiv.org/abs/2305.18654 .
    Accuracy collapses with problem size. Later work describes the paper as having "more formally
    proven" LeCun's compounding view; that proposition was not read here.
    **1, C1.** Cite it as the empirical and independence-model compounding claim our Theorem 1(c)
    refines.

13. **Arbuzov, Bei, Dong, Kalaev, Shvets. Beyond Exponential Decay: Rethinking Error Accumulation in
    Large Language Models.** https://arxiv.org/abs/2505.24187 (2025).
    Argues against independent per-token error decay: errors concentrate at sparse "key tokens"
    (5–10%).
    **1, C1.** The only arXiv rebuttal to LeCun's argument found. LeCun's own 2023 slides were not
    verifiable (§7). Our Theorem 1(c) gives the sharper, assumption-explicit version: linear drift under
    non-expansion, exponential without.

14. **Kalai, Vempala. Calibrated Language Models Must Hallucinate. STOC 2024.**
    https://arxiv.org/abs/2311.14648 .
    Calibration forces a hallucination rate near the singleton fraction (a Good-Turing estimate).
    **1, C1.** Another "the objective itself forces errors" theorem, about facts rather than state. A
    tangential cite.

15. **Kalai, Nachum, Vempala, Zhang. Why Language Models Hallucinate.**
    https://arxiv.org/abs/2509.04664 (2025).
    Hallucinations arise as binary-classification errors, which training and evaluation reward.
    **0–1, C1.** Context only.

### B. Horizon theory of imitation and next-token learning (C1)

16. **Simchowitz, Pfrommer, Jadbabaie (COLT 2025).** §1.1. **3, C1.**
17. **Rohatgi et al. (COLT 2025).** §2.2. **2, C1.**
18. **Foster, Block, Misra (NeurIPS 2024).** §2.3. **2, C1.**

19. **Xu, Yuan, Zhan. Autoregressive Learning in Joint KL: Sharp Oracle Bounds and Lower Bounds.**
    https://arxiv.org/abs/2605.12316 (May 2026).
    Under joint KL the approximation factor is horizon-free; estimation needs Ω(H). The Hellinger Ω(H)
    is a divergence artefact.
    **1–2, C1.** Specify the divergence and horizon whenever we say "likelihood".

20. **Pfrommer, Zhang, Tu, Matni. TaSIL (NeurIPS 2022).** §2.1. **2, C1.**

21. **Tu, Robey, Zhang, Matni. On the Sample Complexity of Stability Constrained Imitation Learning.**
    https://arxiv.org/abs/2102.09161 (venue not verified).
    Links the expert's incremental gain stability to the horizon dependence of the generalisation bounds.
    **1–2, C1.** The robustness comes from the *expert's* stability, which is the assumption C1 refuses
    (our learned tracker has no imposed stability).

22. **Block, Jadbabaie, Pfrommer, Simchowitz, Tedrake. Provable Guarantees for Generative Behavior
    Cloning: Bridging Low-Level Stability and High-Level Behavior.**
    https://arxiv.org/abs/2307.14619 (venue not verified).
    With low-level stabilising controllers and a strong generative learner, behaviour cloning matches
    per-step distributions.
    **1, C1.** Again robustness is supplied by a stabiliser outside the objective, which is our closure.

23. **Block, Foster, Krishnamurthy, Simchowitz, Zhang. Butterfly Effects of SGD Noise: Error
    Amplification in Behavior Cloning and Autoregression.** https://arxiv.org/abs/2310.11428 (venue not
    verified).
    Minibatch noise that barely moves the behaviour-cloning loss causes large swings in long-horizon
    reward ("gradient variance amplification"). An EMA of iterates fixes it.
    **2, C1.** Empirical evidence of exactly what C1 predicts: the loss does not see the rollout
    instability. Cite it.

24. **Laskey, Lee, Fox, Dragan, Goldberg. DART: Noise Injection for Robust Imitation Learning. CoRL
    2017.** https://arxiv.org/abs/1703.09327 .
    Injects noise into the supervisor during data collection to cover recovery states.
    **2, C1/C2.** The isotropic ancestor of our aimed kick. Run or cite an isotropic-noise control at the
    same norm (§5).

25. **Wang, Wu, Wei, Jegelka, Wang. A Theoretical Understanding of Self-Correction through In-context
    Alignment. NeurIPS 2024.** https://arxiv.org/abs/2405.18634 .
    Self-correction is possible when self-examination rewards are accurate.
    **0–1, C8.** Context only.

### C. Error accumulation in chain of thought and long-horizon reasoning, 2024–2026 (C1, C8)

26. **Zhang, Dong, Cesari, Mao (2026).** §2.5. **2, C1.**

27. **Li, Duan, Zhang, Zhang. Stability in Multi-Step Reasoning via Jacobian-based Error Accumulation
    Analysis. NeurIPS 2026 poster.** https://neurips.cc/virtual/2026/poster/151921 (abstract read).
    Bounds test error by the product of input-Jacobian spectral norms across steps (an "error
    amplification factor"). It regularises that factor with CoT compression and quantisation-aware
    training, giving +8.2% on length generalisation.
    **1–2, C1/C2.** The Jacobian-product view of our Lyapunov reading. Their regulariser acts on reached
    trajectories, and C1 says such reads leave the off-trajectory exponents free.

28. **Li, Wu, Wang, Zhao. Limited Reasoning Space: The cage of long-horizon reasoning in LLMs.**
    https://arxiv.org/abs/2602.19281 (2026).
    Treats CoT as a non-autonomous stochastic dynamical system with a linearised error propagation, and
    proposes a model-predictive planner.
    **1, C1.** Context.

29. **Sinha, Arun, Goel, Staab, Geiping (ICLR 2026).** §2.11. **2, C8.**

30. **Cai, Wang, Zhang, Li, Ma, Fang et al. Complex Problem Solving in Large Language Models: A
    Statistical Control Survey and Diagnostic Framework.** https://arxiv.org/abs/2609.20973 (2026,
    survey).
    Discusses contractive versus expanding per-step updates (per the search summary; the body was not
    read).
    **0–1.** A survey to check for missed citations.

### D. Stability, contraction, Lyapunov and Jacobian control (C1, C2)

31. **Miller, Hardt. Stable Recurrent Models. ICLR 2019.** https://arxiv.org/abs/1805.10369 .
    Contractive (stable) RNNs are well approximated by feed-forward truncations, for inference and
    training.
    **2, C3/C1.** A reviewer will say "contraction kills memory". The answer: C3 needs contraction *onto
    separated cells* (multistability, as in Bakija; separation, as in Brandoit Thm 3.3), not global
    contraction. Global contraction gives only definite memory (cf. Brandoit Thm 4.1(ii); Hammer and Tiňo
    2003, cited).

32. **Lohmiller, Slotine. On Contraction Analysis for Non-linear Systems. Automatica 34(6):683–696,
    1998.** https://doi.org/10.1016/S0005-1098(98)00019-3 .
    The contraction-metric framework.
    **1, C3.** Our C3 is a discrete, set-valued, multi-cell contraction. Cite it when the word
    "contraction" is used.

33. **Revay, Wang, Manchester. Recurrent Equilibrium Networks. IEEE TAC.**
    https://arxiv.org/abs/2104.05942 .
    Parametrisations with built-in contraction and Lipschitz guarantees.
    **1, C1/C3.** Robustness by architecture; global contraction again.

34. **Gokhale, Proskurnikov, Kawano, Bullo. Contracting Neural Networks: Sharp LMI Conditions
    (arXiv 2604.00119, 2026); and A Nonlinear Separation Principle via Contraction Theory (arXiv
    2604.15238, 2026).** https://arxiv.org/abs/2604.00119 ; https://arxiv.org/abs/2604.15238 .
    Sharp LMI certificates of contractivity for firing-rate and Hopfield RNNs.
    **1, C2.** LMI certificates exist for *global* contraction. Our missing continuous certificate is for
    per-cell contraction with separation, which global LMIs cannot express.

35. **Manek, Kolter. Learning Stable Deep Dynamics Models. NeurIPS 2019.**
    https://arxiv.org/abs/2001.06116 .
    Learns dynamics together with a Lyapunov function, so stability holds by construction.
    **1, C2.** Lyapunov by architecture.

36. **Boffi, Tu, Matni, Slotine, Sindhwani. Learning Stability Certificates from Data.**
    https://arxiv.org/abs/2008.05952 (venue not verified; v2 corrects Thms 5.1 and 5.2).
    Learns certificates from trajectories and converts generalisation bounds into global stability
    guarantees under regularity assumptions.
    **2, C5/C2.** The positive counterpart of `no_finite_test_suite`: finite data certify *given
    Lipschitz regularity*. That is our `unpinned_exact_of_close` (a τ-bound on the history's effect). Cite
    them together.

37. **Engelken. Gradient Flossing: Improving Gradient Descent through Dynamic Control of Jacobians.
    NeurIPS 2023.** https://arxiv.org/abs/2312.17306 .
    Computes the leading Lyapunov exponents during training (QR iterations of the tangent map) and
    regularises them towards zero.
    **2, C2.** The same machinery as our aimed kick (power iteration of the closed tangent map along the
    past, `norm_wordMap_eq_prod_gain`), used for a different purpose. Cite it as the method precedent for
    computing ψ.

38. **Vogt, Puelma Touzel, Shlizerman, Lajoie. On Lyapunov Exponents for RNNs.**
    https://arxiv.org/abs/2006.14123 (2020).
    Lyapunov spectra as a diagnostic of RNN training.
    **1, C2.** Context.

39. **Mikhaeil, Monfared, Durstewitz. On the difficulty of learning chaotic dynamics with RNNs.**
    https://arxiv.org/abs/2110.07238 (NeurIPS 2022 per common citation; not verified).
    Proves that loss gradients relate to the Lyapunov spectrum of generated orbits: bounded for stable
    or cyclic behaviour, divergent for chaotic.
    **1, C1.** Lyapunov exponents enter the gradient only along generated orbits, which is C1's "along
    reached paths".

40. **Hess, Monfared, Brenner, Durstewitz. Generalized Teacher Forcing for Learning Chaotic Dynamics.
    ICML 2023 (PMLR 202).** https://arxiv.org/abs/2306.04406 .
    Interpolates between teacher forcing and free running to control gradient explosion.
    **1, C1.** Context.

41. **Pascanu, Mikolov, Bengio. On the difficulty of training Recurrent Neural Networks.**
    https://arxiv.org/abs/1211.5063 (2012/2013).
    The exploding and vanishing gradient analysis.
    **0–1.** Background.

42. **Bengio, Simard, Frasconi (1994).** §2.8. **2, C3/C1.**

43. **Lim, Erichson, Hodgkinson, Mahoney. Noisy Recurrent Neural Networks. NeurIPS 2021.**
    https://arxiv.org/abs/2102.04877 .
    Noise injection in the hidden state acts as an implicit regulariser that favours stability.
    **1–2, C2.** Isotropic state noise. Our kick is aimed, and it is evaluated against Nerode classes;
    cite it as the noise baseline.

44. **Camuto, Willetts, Şimşekli, Roberts, Holmes. Explicit Regularisation in Gaussian Noise Injections.
    NeurIPS 2020.** https://arxiv.org/abs/2007.07368 .
    Derives the explicit regulariser that noise injection induces.
    **1, C2.** It complements Bishop 1995 (cited).

45. **Hoffman, Roberts, Yaida. Robust Learning with Jacobian Regularization.**
    https://arxiv.org/abs/1908.02729 (2019).
    Input-Jacobian norm penalties.
    **1, C1.** A Jacobian penalty at data points is a finite-order read; Corollary 1 applies.

46. **Czarnecki, Osindero, Jaderberg, Świrszcz, Pascanu. Sobolev Training for Neural Networks.**
    https://arxiv.org/abs/1706.04859 (2017).
    Matches target derivatives as well as values.
    **1–2, C1.** The general form of TaSIL. Same note.

47. **Novak, Bahri, Abolafia, Pennington, Sohl-Dickstein. Sensitivity and Generalization in Neural
    Networks. ICLR 2018.** https://arxiv.org/abs/1802.08760 .
    The input-Jacobian norm at data correlates with generalisation.
    **0–1.** Context.

48. **Haber, Ruthotto. Stable Architectures for Deep Neural Networks. Inverse Problems 34(1), 2017.**
    https://arxiv.org/abs/1705.03341 ; and **Chang, Chen, Haber, Chi. AntisymmetricRNN. ICLR 2019.**
    https://arxiv.org/abs/1902.09689 .
    Stability by architecture.
    **1, C1.** Precedents for "from the architecture".

49. **Sussillo, Barak. Opening the Black Box: Low-Dimensional Dynamics in High-Dimensional Recurrent
    Neural Networks. Neural Computation 25(3):626–649, 2013.** https://doi.org/10.1162/NECO_a_00409 .
    Fixed-point analysis of trained RNNs.
    **1, C2/C3.** The standard tool for finding codes c_q and checking contraction in trained trackers.

50. **Tiňo, Čerňanský, Beňušková. Markovian Architectural Bias of Recurrent Neural Networks. IEEE TNN
    15(1):6–15, 2004.** https://doi.org/10.1109/TNN.2003.820839 .
    Contractive RNNs are biased towards Markov (definite-memory) behaviour.
    **1, C3.** It sits with Hammer and Tiňo 2003 (cited); this is why global contraction is not enough.

### E. Robust finite-state computation, automata in networks (C3)

51. **Casey (1996).** §2.7. **2, C3.** Already cited.

52. **Omlin, Giles (JACM 1996; NC 1996).** §2.9. **2, C3.** **Not cited in v2; add.**

53. **Carrasco, Forcada, Valdés-Muñoz, Ñeco. Stable Encoding of Finite-State Machines in Discrete-Time
    Recurrent Neural Nets with Sigmoid Units. Neural Computation 12(9):2129–2174, 2000.**
    https://doi.org/10.1162/089976600300015097 (Crossref; abstract not available).
    Extends the stable-encoding constructions to other architectures (from the title and the Omlin–Giles
    lineage; body not read).
    **1–2, C3.** Cite it with Omlin and Giles.

54. **Maass, Orponen. On the Effect of Analog Noise in Discrete-Time Analog Computations. Neural
    Computation 10(5):1071–1095, 1998.** https://doi.org/10.1162/089976698300017359 (abstract read via
    Semantic Scholar).
    "Arbitrarily small amounts of analog noise" reduce analog computation to finite automata.
    **1–2, C3/C2.** Already cited. With unbounded-support noise, Maass and Sontag (1999, cited) leave only
    definite languages. C3's bounded-radius perturbations are the regime where exact regular-language
    tracking survives. Say so.

55. **Bugaud (ICML 2026 workshops).** §1.5. **2–3, C2/C3.**

56. **Brandoit et al. (2026).** §1.2. **3, C3.**

57. **Brandoit, Fyon, Ernst, Drion. Improving the Performance and Learning Stability of Parallelizable
    RNNs Designed for Ultra-Low Power Applications. ICML 2026 spotlight.**
    https://arxiv.org/abs/2605.11855 .
    Same group's architecture paper (abstract not read).
    **1.** Check that the NFSM claims in 2609.32447 are not also made here with a venue.

58. **Bakija et al. (2026).** §2.10. **2, C3.**

59. **Chung, Choi, Kim (NeurIPS 2026).** §2.6. **1–2, C3/C1.**

60. **Weiss, Goldberg, Yahav. Extracting Automata from RNNs Using Queries and Counterexamples. ICML
    2018.** https://arxiv.org/abs/1711.09576 .
    Uses L* with the network as teacher.
    **1, C2.** Already cited.

61. **Michalenko, Shah, Verma, Baraniuk, Chaudhuri, Patel. Representing Formal Languages: A Comparison
    Between Finite Automata and Recurrent Neural Networks. ICLR 2019.**
    https://arxiv.org/abs/1902.10297 .
    Trained RNN states decode to *superstates* (clusters of minimal-DFA states), not to the minimal DFA
    itself.
    **1–2, C2/C3.** Next-token training yields a coarsening of the Nerode partition. Our certified
    equivalence makes the partition exact; cite this as the "before" picture.

62. **Mayr, Yovine. Regular Inference on Artificial Neural Networks. CD-MAKE 2018, LNCS, 350–369.**
    https://doi.org/10.1007/978-3-319-99740-7_25 (Crossref).
    PAC-style automaton extraction from networks by sampling.
    **1–2, C5.** PAC guarantees are distributional, so they cannot certify every length. This is the
    statistical side of `no_finite_test_suite`.

63. **Khmelnitsky, Neider, Roy, Barbot, Bollig et al. Property-Directed Verification of Recurrent Neural
    Networks.** https://arxiv.org/abs/2009.10610 (2020; venue not verified).
    Learns a DFA surrogate by active learning, then model-checks it.
    **1, C5.** The surrogate's correctness for the network is the gap that Theorem P closes for a pinned
    clock.

64. **Slimi, Le Gall, Lemesle. Passive Learning of Lattice Automata from Recurrent Neural Networks.
    OVERLAY 2025 workshop.** https://arxiv.org/abs/2509.22489 .
    Abstract-interpretation over-approximations plus passive learning.
    **1, C5.** Context.

65. **Marzouk. On Computability, Learnability and Extractability of Finite State Machines from Recurrent
    Neural Networks. Master's thesis.** https://arxiv.org/abs/2009.06398 .
    Revisits the clustering hypothesis of RNN state space.
    **1, C3.** Context.

66. **Knorozova, Ronca. On the Expressivity of Recurrent Neural Cascades. AAAI 2024.**
    https://arxiv.org/abs/2312.09048 ; and **… with Identity. KR 2024.** https://arxiv.org/abs/2405.11657 .
    Positive-weight cascades capture exactly the star-free languages; uses canonical (Myhill–Nerode)
    systems. These are the Krohn–Rhodes results in neural form.
    **1, C3.** They pair with Liu et al. 2023 (cited); expressivity only.

67. **Svete, Chan, Cotterell. On Efficiently Representing Regular Languages as RNNs.**
    https://arxiv.org/abs/2402.15814 (2024; venue not verified).
    Compact RNN constructions for regular language models.
    **0–1.** Context.

68. **Dhayalkar. Neural Networks as Universal Finite-State Machines: A Constructive DFA Theory.**
    https://arxiv.org/abs/2505.11694 (2025).
    Feedforward unrolled DFA simulation; Myhill–Nerode classes embedded separably.
    **0–1, C3.** Weak preprint; a cite is optional.

69. **Hopfield. Neural networks and physical systems with emergent collective computational abilities.
    PNAS 79(8):2554–2558, 1982.** https://doi.org/10.1073/pnas.79.8.2554 .
    Attractor memories restore corrupted patterns.
    **1, C2/C3.** The original "restoring" dynamics in neural networks; it belongs in the regeneration
    sentence.

### F. Length-generalisation theory (C2, C5)

70. **Huang et al. (ICLR 2025).** §2.13. **1–2, C5/C2.**

71. **Yang, Bergsträßer, Zetzsche, Chiang, Lin. Length Generalization Bounds for Transformers. ICML
    2026.** https://arxiv.org/abs/2603.02238 ; https://icml.cc/virtual/2026/poster/63411 . §1.4.
    **2–3, C5.**

72. **Chen, Ma, Li. Non-Asymptotic Length Generalization. ICML 2025, PMLR 267:8621–8682.**
    https://proceedings.mlr.press/v267/chen25ar.html . §1.4.
    **2, C5.**

73. **Zetzsche, Jiang, Yang, Bergsträßer, Sälzer, Chiang et al. Length Generalization for Transformers
    via Compression.** https://arxiv.org/abs/2609.08851 (Sep 2026).
    Refines the C-RASP hypothesis in response to the non-computability result.
    **1, C5.** Watch this group: they are the formal-language reviewers for C5.

74. **Izzo, Nichani, Lee. Quantitative Bounds for Length Generalization in Transformers.**
    https://arxiv.org/abs/2510.27015 (ICLR 2026 per Yang et al.'s bibliography; not independently
    verified).
    Length generalisation occurs when the behaviour on long inputs "can be 'simulated' by its behavior on
    shorter sequences".
    **1–2, C5.** Theorem P(3) (`tick_logits_eq_row`) is the extreme case: every tick *equals* a certified
    short computation.

75. **Zhou et al. What Algorithms can Transformers Learn? (RASP-L). ICLR 2024.**
    https://arxiv.org/abs/2310.16028 .
    Already in LITERATURE.md.
    **1, C2.**

76. **Abbe, Bengio, Lotfi, Rizk. Generalization on the Unseen, Logic Reasoning and Degree Curriculum.
    ICML 2023 / JMLR.** https://arxiv.org/abs/2301.13105 .
    A min-degree interpolator bias explains out-of-distribution failure.
    **1, C1.** The implicit bias picks among interpolants, which is the same underspecification that C1
    states for dynamics.

77. **Xiao, Liu. Conditions for Length Generalization in Learning Reasoning Skills.**
    https://arxiv.org/abs/2311.16173 (2023; venue not verified).
    Theoretical conditions on the reasoning DAG under which length generalisation is possible.
    **1, C5.** Context.

78. **Ahuja, Mansouri. On Provable Length and Compositional Generalization.**
    https://arxiv.org/abs/2402.04875 (2024; venue not verified).
    Guarantees for deep sets, transformers, SSMs and RNNs under limited capacity and realisability.
    **1, C1.** Its positive results need capacity matching, which our C1 shows likelihood does not
    enforce for drift.

79. **Golowich, Jelassi, Brandfonbrener, Kakade, Malach. The Role of Sparsity for Length Generalization
    in Transformers.** https://arxiv.org/abs/2502.16792 (2025).
    Length generalisation holds when each token depends on a small fixed number of previous tokens.
    **1, C5.** This is why the pinned tick, which depends on two tokens and Π, generalises; cite it in
    P(1)'s discussion.

80. **Marsden, Dogariu, Agarwal, Chen, Suo, Hazan. Provable Length Generalization in Sequence
    Prediction via Spectral Filtering.** https://arxiv.org/abs/2411.01035 (2024).
    Asymmetric regret for linear dynamical systems.
    **0–1.** Context.

81. **Hahn, Rofin. Why are Sensitive Functions Hard for Transformers? ACL 2024.**
    https://arxiv.org/abs/2402.09963 .
    High-sensitivity transformers occupy isolated points in parameter space.
    **1, C1.** It complements the blindness theorem on why exact state is not selected.

82. **Koiran, Sontag. Vapnik-Chervonenkis dimension of recurrent neural networks. Discrete Applied
    Mathematics 86(1):63–79, 1998.** https://doi.org/10.1016/S0166-218X(98)00014-6 .
    The VC dimension grows with sequence length.
    **1, C5.** Uniform finite-sample guarantees across all lengths fail, which is the statistical form of
    no finite test.

83. **Strobl, Merrill, Weiss, Chiang, Angluin. What Formal Languages Can Transformers Express? A Survey.
    TACL 12:543–561, 2024.** https://arxiv.org/abs/2311.00208 ; and **Hahn. Theoretical Limitations of
    Self-Attention. TACL 2020.** https://arxiv.org/abs/1906.06755 .
    **0–1.** Background (FIELD_GUIDE.md already lists them).

### G. Testing theory and conformance testing (C5)

84. **Moore (1956).** §1.4. **3, C5.**

85. **Hennie. Fault detecting experiments for sequential circuits. Proc. 5th Symp. Switching Circuit
    Theory and Logical Design, 95–110, 1964.** https://doi.org/10.1109/SWCT.1964.8 (Crossref lists the
    author as "Hennine").
    The origin of checking sequences.
    **2, C5.**

86. **Vasilevskii. Failure diagnosis of automata. Cybernetics 9(4):653–665 (English translation 1973/75,
    Crossref year 1975).** https://doi.org/10.1007/BF01068590 ; and **Chow. Testing Software Design
    Modeled by Finite-State Machines. IEEE TSE SE-4(3):178–187, 1978.**
    https://doi.org/10.1109/TSE.1978.231496 .
    The W-method gives m-complete suites, polynomial for fixed m − n.
    **2, C5.** Theorem P(2) is the m = n, observable-state case (a transition cover). The positive
    version of `no_finite_test_suite` under a bounded history effect is an m-complete statement (§5).

87. **Lee, Yannakakis. Principles and methods of testing finite state machines — a survey. Proc. IEEE
    84(8):1090–1123, 1996.** https://doi.org/10.1109/5.533956 .
    The standard survey.
    **1–2, C5.** Cite it as the entry point for formal-methods readers.

88. **Vaandrager, Melse. New Fault Domains for Conformance Testing of Finite State Machines. CONCUR
    2025.** https://arxiv.org/abs/2410.19405 (§1 read).
    States the no-complete-finite-suite fact and introduces fault domains with exponentially many extra
    states.
    **2, C5.** The modern citation for "no finite suite without a fault domain".

89. **Budd, Angluin. Two notions of correctness and their relation to testing. Acta Informatica
    18(1):31–45, 1982.** https://doi.org/10.1007/BF00625279 .
    Relates test adequacy to deciding program equivalence (abstract per search summary; body not read).
    **1–2, C5.** The same equivalence-decidability link as Chen–Ma–Li Lemma 4.5.

90. **Goodenough, Gerhart. Toward a theory of test data selection. IEEE TSE SE-1(2):156–173, 1975.**
    https://doi.org/10.1109/TSE.1975.6312836 ; and **Weyuker. Assessing Test Data Adequacy through
    Program Inference. ACM TOPLAS 5(4):641–655, 1983.** https://doi.org/10.1145/69575.357231 .
    Reliable and valid test criteria; adequacy as inference.
    **1, C5.** Background.

91. **Dijkstra. The Humble Programmer (EWD340), ACM Turing Lecture 1972.**
    https://www.cs.utexas.edu/~EWD/transcriptions/EWD03xx/EWD340.html (read).
    "program testing can be a very effective way to show the presence of bugs" (and is inadequate for
    showing their absence).
    **1, C5.** The slogan `no_finite_test_suite` makes precise for decoders.

### H. Verification and certification of neural computation; proof assistants (C2, C5)

92. **Gowal et al. On the Effectiveness of Interval Bound Propagation for Training Verifiably Robust
    Models (ICCV 2019 as "Scalable Verified Training…").** https://arxiv.org/abs/1810.12715 .
    **1, C2.** IBP is the tool for computing box enclosures F_x(B_q). See §5, idea 6.

93. **Zhang, Weng, Chen, Hsieh, Daniel. Efficient Neural Network Robustness Certification with General
    Activation Functions (CROWN). NeurIPS 2018.** https://arxiv.org/abs/1811.00866 .
    **1, C2.** Same use as IBP.

94. **Ko, Lyu, Weng, Daniel, Wong, Lin. POPQORN: Quantifying Robustness of Recurrent Neural Networks.
    ICML 2019.** https://arxiv.org/abs/1905.07387 .
    Certified bounds for RNNs over bounded unrolling.
    **1, C5/C2.** Bounded-length certification only, which is the gap C3 and Theorem P close by
    invariance.

95. **Shi, Zhang, Chang, Huang, Hsieh. Robustness Verification for Transformers. ICLR 2020.**
    https://arxiv.org/abs/2002.06622 .
    **1, C5.** Bound propagation through attention. Our Corollary P2 (margin > 2τ) is the same
    certificate logic applied per row.

96. **Jacoby, Barrett, Katz. Verifying Recurrent Neural Networks Using Invariant Inference. ATVA 2020,
    LNCS, 57–74.** https://doi.org/10.1007/978-3-030-59152-6_3 ; https://arxiv.org/abs/2004.02462 .
    Inductive invariants reduce RNN verification over unbounded inputs to non-recurrent checks.
    **2, C3/C5.** The proof shape of C3 (`rmn_core`: one-step invariance gives all lengths) in the
    verification literature. Cite it.

97. **Selsam, Liang, Dill. Developing Bug-Free Machine Learning Systems With Formal Mathematics. ICML
    2017.** https://arxiv.org/abs/1706.08605 .
    Certigrad: ML implementation correctness proved in Lean.
    **1.** The first Lean and ML precedent.

98. **Bagnall, Stewart. Certifying the True Error: Machine Learning in Coq with Verified Generalization
    Guarantees. AAAI 2019, 33(01):2662–2669.** https://doi.org/10.1609/aaai.v33i01.33012662 .
    **1.** A Coq precedent.

99. **Viswanathan, Dimitrov, Rocca, Sirikonda. Formally Verified Autoresearch for Analyzing the
    Expressivity of Multi-Head Attention. NeurIPS 2026 workshop oral (Autonomous ML Research).**
    https://neurips.cc/virtual/2026/157626 (abstract read).
    Head-complexity theorems for one-layer attention, generated and machine-verified in Lean.
    **1, C5.** The only other Lean result about attention found. Ours is broader (decoders, caches,
    certificates). Limited search here; see §7.

100. **Pnueli, Siegel, Singerman. Translation validation. TACAS 1998, LNCS, 151–166.**
     https://doi.org/10.1007/BFb0054170 .
     Validate each compilation output rather than the compiler.
     **1, C5.** Theorem P's per-question certificate is translation validation for an LLM-written
     table. Corollary P2's code-path caveat is the floating-point analogue.

101. **Yuan, Li, Ding, Xie, Li, Zhao et al. Understanding and Mitigating Numerical Sources of
     Nondeterminism in LLM Inference.** https://arxiv.org/abs/2506.09501 (2025).
     **1, C5 (P2).** Evidence that certified logits and run logits can differ by code path. Cite it at
     Corollary P2.

### I. Neural program execution (C5, C8)

102. **Cai, Shin, Song (ICLR 2017).** §1.3. **3, C5/C8.**

103. **Reed, de Freitas. Neural Programmer-Interpreters. ICLR 2016.** https://arxiv.org/abs/1511.06279 .
     **1.** The architecture Cai et al. verify.

104. **Zaremba, Sutskever. Learning to Execute.** https://arxiv.org/abs/1410.4615 (2014).
     **0–1.** Background.

105. **Yan, Swersky, Koutra, Ranganathan, Hashemi. Neural Execution Engines: Learning to Execute
     Subroutines. NeurIPS 2020.** https://arxiv.org/abs/2006.08084 .
     Strong generalisation by learning subroutines with masks.
     **1, C5.** It is also a bounded-context-per-step design.

106. **Qiu, Xu, Bao, Tong. Ask, and it shall be given: On the Turing completeness of prompting. ICLR
     2025.** https://arxiv.org/abs/2411.01992 .
     One fixed finite transformer computes any computable function given the right prompt (with CoT).
     **1–2, C5.** The expressivity counterpart of Theorem P's "program Π in context, fixed decoder". Ours
     adds certification and the pinned clock.

107. **Giannou, Rajput, Sohn, Lee, Lee, Papailiopoulos. Looped Transformers as Programmable Computers.**
     https://arxiv.org/abs/2301.13196 (2023; venue not verified); and **Lindner et al. Tracr: Compiled
     Transformers. NeurIPS 2023.** https://arxiv.org/abs/2301.05062 .
     Exact execution by hand-set or compiled weights.
     **1, C5.** Exactness by construction, against our exactness by certification.

108. **Li, Liu, Zhou, Ma. Chain of Thought Empowers Transformers to Solve Inherently Serial Problems.
     ICLR 2024.** https://arxiv.org/abs/2402.12875 ; **Feng et al. Towards Revealing the Mystery behind
     Chain of Thought. NeurIPS 2023.** https://arxiv.org/abs/2305.15408 ; **Merrill, Sabharwal. The
     Expressive Power of Transformers with Chain of Thought. ICLR 2024.** https://arxiv.org/abs/2310.07923
     (cited) ; **Malach. Auto-Regressive Next-Token Predictors are Universal Learners.**
     https://arxiv.org/abs/2309.06979 .
     **1, C5/C8.** The expressivity of unpinned decoding. Our `no_finite_test_suite` says that
     expressivity is not certifiability.

### I′. Added after the coordinator's follow-up (all read; see §1.6–§1.7)

116. **Lewandowski, Machado, Schuurmans. Universal computation is intrinsic to language model decoding.**
     https://arxiv.org/abs/2601.08061 (Jan 2026, v2).
     Exhaustive per-rule checks (1,857 rules) plus a fresh-call induction prove that Llama-4 simulates
     U(15,2) exactly. A frozen random network becomes universal once its codebook is learned.
     **3, C5 (sufficiency).**

117. **Schuurmans, Dai, Zanini. Autoregressive Large Language Models are Computationally Universal.**
     https://arxiv.org/abs/2410.03170 (2024).
     The predecessor of entry 116 (Gemini, now deprecated). Already LITERATURE.md #71.
     **2, C5.**

118. **Back de Luca, Fountoulakis. Certification from Examples is Hard for Circuits and Transformers under
     Minimal Overparametrization.** https://arxiv.org/abs/2605.22964 (May 2026).
     With one extra gate or head, certificates for targets on {0,1}^n need ≥ 2^t examples, for every
     t ≤ n. Approximate certification is no easier.
     **2–3, `no_finite_test_suite`.** Ours differs in having unbounded length, certification complexity ∞
     within a fault domain that passes the per-row certificate, and the pinned escape with exactly
     |Reach| rows.

119. **Abbe, Bengio, Lotfi, Sandon, Saremi. How Far Can Transformers Reason? The Globality Barrier and
     Inductive Scratchpad. NeurIPS 2024.** https://arxiv.org/abs/2406.06467 .
     The inductive scratchpad masks each step down to the question plus the last state. No theorem and
     no certificate; 2–6× length generalisation trained from scratch.
     **2, C5 (the pin).** Do not claim the KV policy as new.

120. **Howe. The Automaton Underneath: The Additive Input Pathway Is a Parasitic Attractor for State
     Tracking in Householder Linear RNN.** https://arxiv.org/abs/2609.18966 (Jul 2026).
     Removing the additive input path gives exact automata at 16×. From an exact initialisation, Adam
     regrows the path and destroys exactness at length; zeroing it at inference restores exactness.
     **2, C1 (an instance), C2.**

121. **Sharma, Vu. Dense Supervision Is Not Enough: The Readout Blind Spot in Looped Language Models.**
     https://arxiv.org/abs/2606.24898 (Jun 2026).
     A scale-invariant readout gives zero radial gradient, while recurrence still updates the scale.
     **2, C1 (a static instance; our closure is their fix).**

### J. Attention dilution and history effects (C8)

109. **Veličković et al. (ICML 2025).** §2.12. **1–2, C8.**

110. **Xiao, Tian, Chen, Han, Lewis. Efficient Streaming Language Models with Attention Sinks. ICLR
     2024.** https://arxiv.org/abs/2309.17453 .
     Attention mass collects on initial "sink" tokens.
     **1–2, C8.** Our counterexample's head attends to the sink at position 0. Cite it so readers see the
     mechanism is realistic, not contrived.

111. **Barbero, Banino, Kapturowski, Kumaran, Araújo, Vitvitskyi et al. Transformers need glasses!
     Information over-squashing in language tasks.** https://arxiv.org/abs/2406.04267 (2024; venue not
     verified).
     Representational collapse of long sequences under softmax averaging.
     **1, C8.**

### K. Digital abstraction and regeneration (C2, C3 framing)

112. **von Neumann (1956)** and **Pippenger (1985)**: cited in v2.
     **1–2, C2/C3.** Restoring organs; our snap and closure are learned restoring organs.

113. **Sarpeshkar. Analog Versus Digital: Extrapolating from Electronics to Neurobiology. Neural
     Computation 10(7):1601–1638, 1998.** https://doi.org/10.1162/089976698300017052 (Crossref; abstract
     not available).
     The classic argument for hybrid computation, in which digital restoration periodically regenerates
     analog signals (from the title and its standard reading; body not read).
     **1–2, C2.** The precedent for "an analog state with a periodic digital snap"; it belongs beside von
     Neumann.

### L. Perturbations along unstable directions (C2's aimed kick)

114. **Toth, Kalnay. Ensemble Forecasting at NCEP and the Breeding Method. Monthly Weather Review
     125(12):3297–3319, 1997.** https://doi.org/10.1175/1520-0493(1997)125%3C3297:EFANAT%3E2.0.CO;2 ;
     and **Buizza, Palmer. The Singular-Vector Structure of the Atmospheric Global Circulation. JAS
     52(9):1434–1456, 1995.** https://doi.org/10.1175/1520-0469(1995)052%3C1434:TSVSOT%3E2.0.CO;2 .
     Bred vectors and leading singular vectors are perturbations aimed along the fastest-growing
     directions.
     **1–2, C2.** Our aimed kick along the top Lyapunov direction is a bred vector used as a training
     probe. Cite it so the choice of ψ is not presented as new.

115. **Khrulkov, Oseledets. Art of singular vectors and universal adversarial perturbations.**
     https://arxiv.org/abs/1709.03582 (submitted to CVPR 2018).
     Adversarial perturbations from the top singular vectors of hidden-layer Jacobians.
     **1, C2.** The ML precedent for Jacobian-aimed perturbations. VAT (Miyato, cited) is the power-
     iteration precedent.

---

## 4. The frontier in 2026

Theory about length and error now runs in four strands.

1. **Horizon theory for next-token and imitation learning.** Foster et al. 2024, Rohatgi et al. 2025,
   Simchowitz et al. 2025 and Xu et al. 2026 settle when log-loss is horizon-free (realisable, the right
   divergence) and when amplification is unavoidable (misspecification, per-step learners, smooth policy
   classes under unknown dynamics). The escape routes are improper policy classes or spread data.
2. **Dynamical-systems theory of state tracking.** Chung et al. 2026, Brandoit et al. 2026, Bakija et al.
   2026 and Bugaud's 2026 workshop papers converge on one picture:
   - exactness at length needs non-affine restoration, multistability, and contraction plus separation
     onto per-state cells;
   - the picture comes with iff characterisations under bounded perturbation;
   - certification is either by reading off tables plus a margin or, for absorbing languages only, by
     weight-only interval and LMI checks.
3. **Learnability of length generalisation.** Huang et al. 2025 (in the limit), Chen–Ma–Li 2025, Izzo et
   al. 2026 and Zetzsche et al. 2026 study when length generalisation is learnable. Yang et al. 2026 make
   the negative result sharp: no computable length-generalisation bound exists for log-precision
   transformers, and an exponential one exists at fixed precision.
4. **Chain-of-thought and agent error theory.** Zhang et al. 2026, Li et al. 2026 and Sinha et al. 2026
   give a no-free-lunch bound, Jacobian-product amplification factors, and a measured self-conditioning
   effect.

**What is not there.**
- An objective-level indistinguishability theorem for state trackers: every functional of reached
  views, with closure and arbitrary Jacobians.
- A machine-checked iff certificate for a transformer executor that runs an in-context program with
  the history pinned out.
- A formal statement that the decoded token snaps the state but not the context.
- Proof-assistant work on transformers that goes beyond small expressivity lemmas: the closest is a
  NeurIPS 2026 workshop paper on head complexity, in Lean.

Our position is defensible exactly at these points, and nowhere else.

---

## 5. Ideas

1. **A smoothness-relative blindness radius (answers TaSIL and Simchowitz).** C1 is class-free; a
   reviewer will ask what happens for an M-smooth class.
   - **Proposition to prove.** For trackers whose second derivative is bounded by M on views, values and
     Jacobians at the reached views determine F_x within O(M r²) on B(c, r).
   - **Consequence.** A finite-order objective that pins values and Jacobians then certifies (C_r) for
     r ≲ √(margin/M).
   - **Why it is cheap.** Corollary 1's escape needs a bump with second derivative of order
     margin/dist², which pins the trade-off exactly.
   - **Payoff.** This would make C1 quantitative against the smooth-class lower bounds, and should be
     cheap in Lean from `finite_reads` plus a Taylor bound.

2. **State Theorem P and `no_finite_test_suite` as conformance testing.**
   - **The framing.** Theorem P(2) is "a transition cover is complete when state is observable and there
     is no hidden state (P(1))". `no_finite_test_suite` is "no complete finite suite without a fault
     domain" for decoders.
   - **A positive fault-domain theorem.** Suppose an unpinned decoder's dependence on the history
     factors through at most m classes, a bounded-memory fault domain. Then a finite m-complete suite of
     W-method type certifies it. `unpinned_exact_of_close` is the metric version.
   - **Payoff.** This makes the pinned/unpinned contrast a fault-domain statement that formal-methods
     reviewers recognise. The Lean cost is moderate, since the W-method proof is standard.

3. **State the arithmetic model of `no_finite_test_suite`.** By Yang et al. Thm 5.2, fixed precision
   gives a finite, exponential bound. Add one sentence and, ideally, a quantitative corollary: at
   precision p, the counterexample's crossing length is bounded by roughly 2^p, so a passing suite must
   reach that length.

4. **Reposition C3.**
   - **Credit and reword.** Credit the per-step iff to Brandoit et al. (Thm 3.2) and the necessity
     direction to Casey. Present Theorem 2 as the block-and-prefix generalisation.
   - **A cheap corollary.** Prove in Lean (from `rmn_core_cells`) that Brandoit's cell condition with
     margin η implies `robustMyhillNerode_cells`, to show subsumption.
   - **Show strict generality.** Exhibit a tracker that satisfies the k = 2 block form but no k = 1 cell
     condition, for example a map that expands in one step and contracts over two.

5. **Explain why C2 has no continuous certificate.** Bugaud's single-invariant-set certificate is limited
   to absorbing languages; group automata need per-state cells.
   - **The test.** Run interval bound propagation (Gowal; CROWN) on our *pre-snap* S5 tracker with one
     box per automaton state.
   - **The check.** Iterate F_x(B_q) ⊆ B_{q·x} (Kleene iteration on the product lattice of boxes, as in
     Bugaud) over blocks of length k.
   - **If it closes,** we have the continuous certificate C2 says we lack.
   - **If it fails,** the failure locates where the snap is doing the work.
   - **Cost.** Zero GPU, a CPU script on saved weights.

6. **Kick ablation against the IL baselines.** Compare three conditions at equal norm:
   - **Aimed kick** along ψ.
   - **Isotropic noise** (DART, Lim et al.).
   - **Random-direction kick** off the reached views.

   Simchowitz's Theorem 5 predicts that spread data suffices when it is spread enough. Our claim must be
   that aiming buys the same robustness with a far smaller perturbation budget. Only run this if the
   existing ablations do not already cover it; check ABLATION_BRIEF.md first.

7. **Self-conditioning on the clock.** Reproduce Sinha et al.'s protocol (inject wrong states into the
   history) on the unpinned decoder and on the pinned clock. P(1) predicts the pinned clock is invariant
   by construction. This is a cheap demonstration of C8 on real models, on CPU or a small GPU.

8. **Cite the method lineage for ψ.** Use Engelken 2023 (QR Lyapunov vectors in training), Toth and
   Kalnay 1997 (breeding), Buizza and Palmer 1995 (singular vectors) and Khrulkov and Oseledets 2018. The
   novelty is what the kick is measured against (Nerode classes), not the direction.

9. **Use Rohatgi's and Xu's language for Theorem 1(c)(v).** Restate it as an approximation factor at
   horizon N relative to the loss at horizon L. This makes clear the result is about extrapolation, a
   regime their frameworks do not cover.

---

## 6. Corrections to project files (suggested; not applied, this agent edits only `prior_art/`)

- **NOVELTY.md item 4.** "Bugaud, ICML 2026" is an ICML 2026 *workshop* paper (3rd AI for Math
  Workshop). The page says necessity is proven and the converse is empirical. A second workshop paper,
  "Combining Theory and Benchmarks …", claims 66,667× extrapolation with weight-only certificates.
- **refs.bib**
  - `chung2026error` is now NeurIPS 2026 (arXiv journal_ref).
  - `sinha2025horizon` is ICLR 2026 (arXiv comment).
  - The Omlin and Giles stability result (JACM 43(6):937–972, 1996) and Carrasco et al. 2000 are missing;
    v2 cites only Omlin and Giles's extraction paper.
- **Missing high-priority citations in v2:**
  - Simchowitz et al. 2025;
  - Cai, Shin and Song 2017;
  - Bengio, Simard and Frasconi 1994;
  - Moore 1956 or Vaandrager and Melse 2025;
  - Yang et al. 2026;
  - Chen, Ma and Li 2025;
  - Rohatgi et al. 2025;
  - TaSIL 2022;
  - Engelken 2023;
  - Jacoby et al. 2020;
  - Veličković et al. 2025;
  - Xiao et al. 2024 (attention sinks);
  - Lewandowski et al. 2026 and Schuurmans et al. 2024;
  - Back de Luca and Fountoulakis 2026;
  - Abbe et al. 2024 (inductive scratchpad);
  - Howe 2026;
  - Sharma and Vu 2026.

---

## 7. Items not verified or not read

**Not accessible.**
- **Bugaud's two workshop papers.** OpenReview pages and PDFs sit behind a browser challenge, which I
  did not attempt to pass (bot checks are off-limits). There is no arXiv version. Both icml.cc listings
  were re-read in full: their only paper links are the OpenReview forum, with no poster, slides, PDF or
  code. So the theorem statements, and the definitions of "forward-invariant certificate", "gap
  suppression", k and H, are known only from the listing abstracts. If the full texts matter for the
  v1 wording, Neo can download the two PDFs from OpenReview in a browser and hand them to a session to
  read.
- **Casey 1996.** The full text is paywalled; I read the abstract via ML Anthology. PubMed returned a
  CAPTCHA.
- **Moore 1956.** The full text was not read; I used Vaandrager and Melse's account.
- **Bengio et al. 1994.** The primary text was not read; the robust-latching definition is from a course
  presentation of the paper.

**Identifiers not verified, so no entry.**
- **LeCun's 2023 slides ("auto-regressive LLMs are doomed").** Only blogs and secondary mentions were
  found.
- **Kääriäinen 2006**, the lower bound for reductions.
- **Kolen 1994**, "Fool's gold".
- **Goldwasser et al. 2021**, interactive proofs for ML: the DOI tried returned 404.
- **Evans and Schulman 1999**, noisy circuits: the DOI tried resolved to a different paper.
- **Brucker and Stell 2023**, Isabelle/HOL network verification, and **Necula 2000**: Crossref
  rate-limited.

**Claims not checked in the text.**
- Lee and Yannakakis on "observable state ⇒ transition tour suffices" (§1.4): my reading, not checked in
  the survey.
- Dziri et al.'s formal compounding proposition.
- Carrasco et al. 2000 and Sarpeshkar 1998: no abstract was available; their annotations rest on title
  and lineage.

**Venues reported but not verified.** Ranzato (ICLR 2016), Mikhaeil (NeurIPS 2022), Czarnecki (NeurIPS
2017), Zhang et al. snowball, Block et al. ×2, Tu et al., Boffi et al., Xiao and Liu, Ahuja and Mansouri,
Golowich et al., Svete et al., Barbero et al., Giannou et al., Malach, Khmelnitsky et al.; Izzo et al.
(ICLR 2026 per Yang et al.'s bibliography only). These are listed as arXiv.

**Searches the exhausted budget cut short** (recommended for a follow-up session):
- Lean, Coq and Isabelle formalisations of transformers or RNNs at length;
- PAC or statistical limits of testing learned sequence models;
- 2025–2026 papers training recurrent state trackers with noise or adversarial state perturbations;
- Krohn–Rhodes decompositions learned by neural networks;
- direct searches for "Nerode" and "equivalence" as a training loss (one search found none).
