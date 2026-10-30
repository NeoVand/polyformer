# Deep Review 2 (Google, AI-generated, on v1 at e4d3a557/ded23017, 27 Oct 2026): triage

Neo: "be cautious and only use it to improve things, don't get derailed" (the same reviewer recommends rejecting
published Nature and Science papers). Verdicts by the orchestrator: AGREE (act), PARTLY, SKIP. Text and figure fixes
need no spend; experiments only with Neo's yes. Main text stays at 2,500 words and the abstract at 200 or fewer, so
every addition is paid for by a cut.

## Could change a claim

| # | item | verdict | action |
|---|---|---|---|
| H1 | "Aimed perturbation" is in the title and framed as co-equal with closure, but drop-one on S5 from scratch is 5/10 vs 10/10 with Holm p = 0.211; M vs NS+EQ on S5 has Holm p = 0.283; the counting gain comes from certified equivalence, not aiming; the isotropic control on S5 ran at weight 1 vs M's 10 ("not matched in dose"); its verified benefit is noise tolerance (Fig. 4a) | AGREE (and our later CFDBench breadth, The Well and dysts runs say the same: the kick does not carry over; closure does) | Abstract, introduction and discussion state each component's measured role exactly. Title unchanged in the text; propose 2 alternatives to Neo, one without "aimed perturbation". Optional X3 below |
| H2 | The closure-alone cells (O, O+Nc) that carry the reframe's central claim are 3 seeds (3/3 has a Clopper-Pearson interval [0.29, 1]); the S5 O cell (2/3) comes from a separate study's protocol | AGREE, matters more for us than the reviewer says, because the reframe leans on closure | Text: state n and intervals where the claim is made; label the S5 O cell. Optional X1 below |
| H3 | F's retuned stories and eight-variable-program settings were chosen after the test sets were scored | AGREE (we disclose it in SI, not in §4.1) | §4.1 gives F at default settings first (5/10 stories, 7/10 programs) and says the retunes were chosen on scored test sets. Optional X2 below |
| H4 | Theory precision: (a) on the centred sphere views span a (d−1)-dim subspace, so d (not d+1) affinely independent views fix an affine head (verified); (b) the γ-slower drift remark compares drifts at a fixed per-step miss ε, which must be said; (c) Theorem 2 / S4: perturbations are absorbed at block boundaries after the first k-event block following the prefix, not at t = p, unless (E_r) is strengthened; (d) N_0 undefined at the start of SI §1; η > 0 implicit in S8 | AGREE (a), (d); PARTLY (b); CHECK (c) against the Lean statement | Fix each in the form Lean proved; where Lean and the text differ, the text follows Lean |

## Fair and cheap (text and figures)

- **Sphere-radius convention (important).** Theory uses the centred unit sphere; the code's closure is RMS-scaled
  (√d norm: run files say `rmsc`). State one convention, the conversion, and which units σ, ball radii and Eq. (1)'s
  distances are in. Check Eq. (1)'s constants and the σ values against the code. Records: F uses σ² = 0.1
  (σ ≈ 0.316, file `...s0.316228...`), M uses σ = 0.1 (file `...aim4s0.1...`): both right, state both explicitly.
- **Reproducibility details.** Transition-network equations (cell type, widths, activations, z0); how tokens of one
  event are pooled; the NS loss formula (target, head, stop-gradients, weight); stop-gradient (or not) on the partner
  z(v) in Eq. (1) and EQ; CE averaging over events vs Nerode terms at the last event; AIM burn-in/window on sequences
  shorter than the window, base step choice, ψ0 initialisation; how certified partners are generated per setting
  (the cube, stories: by construction, not by chance collisions) and their length distributions; addition's state
  (carry vs (digit, carry)) matched to its readout; why S5 has no delay schedule and uses final weights; why Lean uses
  the uncentred RMS closure; the in-model L-TF target codes and multi-slot step.
- **Frontier framing.** Keep the comparison; add one sentence that frontier misses at length are mostly token-budget
  stops (a reliability limit of chain of thought, a different mechanism from hidden-state drift), and that frontier
  models are exact at 1,024 on reversible programs, Lean, counting and programs. Mark budget stops separately or add
  intervals on Extended Data Figs. 7a and 8b; give prompt templates in SI §9; note n per cell.
- **Discussion omissions.** Add: the isotropic control was not dose-matched; F on the in-model step broke 9 of 10
  seeds (say what was measured, e.g. the 0.18 cell radius against σ = 0.316, and what was and was not tested
  afterwards, from the records only); no tuned linear-RNN baselines on S5.
- **§4.5.** The Theorem 2 noise bound is vacuous on S5 and orders the Lean arms the wrong way (from our own ledger);
  M's noise tolerance on S5 is empirical. Report the S5 snapping failures with diagnostics already in the records; no
  new runs.
- **Counterexample loop.** Under M it cut periodic failures 155 → 59; under F they rose 96 → 105. Qualify "a window
  acts as a gain, not a horizon" for periodic inputs.
- **Citations.** Add DeltaProduct (Siems et al. 2025, arXiv 2502.10297, verified real in Deep Review 1) where SI §6
  names it and beside [7]; fix Myhill [23], Kleene [37], von Neumann [38] (the "in" placement; von Neumann pages
  43–98, verify).
- **Figures and notation.** Rename the midpoint M in Eq. (1); define c(w) in the noise formula; ED Fig. 1a is the
  eight-variable programs task, not A16; ED Fig. 6a missing EQ+Nc cells explained, the S5 O cell labelled; ED Fig. 6b
  ticks down to 0; λ 0.59 vs 0.637 and 96 vs 94 pairs are different registered cohorts (say so); define "cards";
  spell out the 21 task-seeds; SI Table 1 notes.

## Skip (out of scope for v1 or not worth the spend)

- DeltaProduct / Mamba / negative-eigenvalue runs on S5 (state as a limitation).
- More frontier problems per cell (API cost, refusals; add intervals instead).
- An L-F σ sweep (the in-model F path is not needed for v2).
- New mechanistic studies of S5 snapping.

## Optional experiments for Neo (each registered before spend; small trackers)

- **X1** O+Nc (and O) at 10 seeds where the paper has 3 (reversible programs, Lean, addition, counting), one uniform
  protocol: puts the reframe's central claim on 10 seeds. About $5–10.
- **X2** fresh, independent test sets for the retuned F checkpoints on stories and eight-variable programs, inference
  only: removes the test-set selection bias. About $1–2.
- **X3** dose-matched isotropic perturbation on S5 from scratch, 10–20 seeds (weight 10 under M, or the matched push
  under F), with repeated-word counts: decides whether "aimed" earns its place. About $10.
