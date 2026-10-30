# UNIFY: the anomalies, and the one term (brief, 25 Oct 2026)

Neo's words: "a stronger more elegant and the true candidate for loss that will collapse it all into one gorgeous
term ... we might or not find it but we are close and it might take a creative or super deep or even a simple leap
... we might even be able to look deeper into our theorems and they might just reveal a deeper proof."

Two topics, worked together. The bet is that they are one topic: the anomalies are the places where today's
four-part recipe is visibly a sum of patches, and the right single term should explain them.

## Where things stand (read these, in this order, and nothing else unless a lead needs it)
- The theory, the error cocycle and the scorecard of misses:
  `/Users/neo/repos/polyformer/.claude/worktrees/gracious-panini-dde55f/paper/nmi_v2/supplement.md`
  Supplementary Note 1 (Theorems A to F, §15 "What is not proved"), Note 2 (§0 one-page answer, §2 what each
  mechanism acts on, §3 to 3.2 the clause table and its misses, §6 what failed, §7 open), Note 4 (negatives).
- The generated master table: `/Users/neo/repos/polyformer/.claude/worktrees/notes-2026-10-22/research/master/master_table.md`
  (built by `build_master.py` from each domain's ABLATION json; never type numbers by hand).
- The one earlier attempt at a single term, the Nerode/bisimulation metric loss L_M:
  `/Users/neo/repos/polyformer/.claude/worktrees/metric-0160e1/research/METRIC.md` §0, §4, §5, §7. It reached parity only
  where the base was already exact; its squared floor grew; the note's own next step was the unsquared distance on
  certified pairs.
Proof sources behind the supplement: `.claude/worktrees/gracious-panini-dde55f/research/PROOFS.md` to `PROOFS4.md`,
`THEORY_DEEP.md`, scripts in `research/results/theory_deep/`.

Today's recipe ("Nerode training"): output cross-entropy + next-state prediction (NS) + certified-equivalence term (EQ,
centred cosine distance on checker-certified pairs, weight μ) + closure (centred fixed norm h ← √d·N₀(h), Theorem C).
FULL+Nc is 3/3 at length in six of seven settings; S5 is 2/3, where NS+N alone is 3/3.

## Topic 1: anomalies nobody has explained (start list; add any you find, drop any the sources already explain)
1. **S5 punishes the signal.** Under the stated protocol (random-length partners, μ = 1) every arm carrying EQ misses one
   seed (FULL+N 415/512/507, FULL+Nc 512/512/501, EQ+N 2/3, FULL 2/3); NS+N is 3/3. At μ = 0.1 FULL+N is 3/3.
   Note 2 §3.2 conjectures slow escape from merges for non-abelian irreducible blocks; untested (prediction: longer
   training at μ = 1 closes it).
2. **Next-state prediction works where theory says it cannot.** Its zero set contains every tracker exact on the
   support (Theorem D), it is blind to deterministic dark error, yet NS+N is 3/3 on S5 and on counting (predicted
   unreliable: commutant phase, Z10 phase). Note 2 §7.2: the benefit must come through the path of training; no
   mechanism, no test.
3. **Centred closure hurts ordinary training on S5.** O 2/3, O+N 1/3, O+Nc 0/3. Fixing the mean removed a freedom the
   ordinary objective was using.
4. **The partial-overwrite pattern.** NS+N fails only where events overwrite part of the state (code: 1 of 8 bits;
   stories: 1 of 6 objects) and holds on every bijection/reset domain. Fits all seven columns, read off after the fact,
   confounded with "read through frozen LM features".
5. **What decides which representation training forms.** Note 2 §7.1. Both S5 misses are about it; S5 two-copy seeds
   (SO(8) commutant drift, the parity attractor in ENERGY E2); first failing length L*·√d16 ≈ 15 on nine runs (an
   empirical law with no derivation).
6. **Exact in law, not on every input.** Lean trackers without closure fail on repeated 2-cycles (18-24 events);
   closure added after training rescues 92 of 96 (which 4 do not, and why?); closure-trained FULL+N passes every
   2-cycle, ρ̂ ≤ 0.948/0.946 at the centres on seeds 0 and 2, but seed 1 does not meet the linear hypothesis and no
   continuous network is certified. Snapped trackers are certified 12/12.
7. **Physics.** T13 says conservative systems have no restoring direction for phase, yet the full recipe without the
   shell lowers the pendulum's phase error (0.97-1.07 rad vs ordinary). Closure must be onto the invariant set, and
   the fixed norm is not the energy shell.
8. **Soft-checker cliff.** Certified pairs at 2,088: 0.92-0.97; at 1,058: 0.42-0.58. A stricter consensus checker is
   far worse (0.18-0.23 vs 0.77-0.85). Pair count plus selection cost; is the cliff a threshold the theory can
   predict (Note 1 §15.5 says no threshold is derived)?
9. **In-model ladder asymmetries.** Label-free on-policy SD 0.945 / 0.770 at 256; ORACLE 0.941 / 1.000; consensus
   teacher's errors were correlated (Note 2 §5 explains part: length clocks are correlated across same-length contexts).
10. **Counting vs addition under the bare norm.** Addition: every fixed-norm arm 3/3 (π ≈ 0.23); counting O+N 1/3 at
    0.990 / 0.982 / 0.908. Code O+N 0/3. Closure alone is 0/3 on programs, S5, stories.
11. **Drift diagnostics that work too well.** Growth of the certified-pair distance from 16 to 256 sorts all 27 S5 runs
    perfectly (≤0.0016 exact, ≥0.0045 inexact) and predicts drift elsewhere (Spearman 0.85/0.91). Without the norm each
    step's turn collapses ~300-fold while the norm grows 16-fold. Why is one label-free number this predictive?
12. **Lean's dark directions.** 99 of 126 dark at one step, ~0-5 after two events: the dynamics, not the readout,
    expose them. Is there a general "observability in two steps" principle the term should use?
For each: is it explained by an existing theorem (say which), by a new argument (write it), or still open (say what
cheap test would decide it)?

## Topic 2: the one term
What it must do (each is a theorem or a measured fact; a candidate that loses one must say so):
- Zero set = the minimal (Nerode) automaton up to isometry, with no trivial minima (Theorem B/T3: the distance must
  factor through the readout's normalisation).
- Stiff: first-order response to drift that does not carry the loss floor s̄ (Theorems A, B).
- Act on every dark direction, including deterministic ones (Note 2 §2), and on the radial/mean coordinates that EQ
  misses (Proposition 2.2) — today closure does that by architecture.
- Give a restoring direction: contraction onto class centres (Theorem E), ideally the constrained spectral radius
  ρ̂ < 1 that a certificate needs (Note 2 §4); the snapped tracker shows what certified looks like.
- Explain the anomalies above better than the sum does (especially 1, 2, 3, 5), and reduce to CE, NS, EQ and closure as
  limits or special cases.
- Have a label-free form (the in-model bridge works label-free) and a soft-checker form.
Leads, not instructions: the bisimulation-metric fixed point (L_M, unsquared, on certified pairs); Nerode's own
definition (x ~ y iff every continuation agrees) as one relation of which output loss, NS and EQ are three
projections; closure as a gauge choice (state lives on the space where the admissible distance is a metric) rather
than a term; contraction of the error cocycle written as the objective itself; snapping/commitment (make the centres
attractors); MDL/finite precision; a variational principle from which Theorems A, B, C and E fall out as corollaries.
Rejected before, do not revive without a new reason: K0⋈H (a Frankenstein), plain energy descent (ENERGY E0: no
barrier after the cue), the hindsight gap (V8 dead).

## How to work
- Theory first, in `research/UNIFY.md` in your worktree: a running log with dated entries, each claim tagged proved /
  computed / conjectured / failed, as the supplement does. Proofs written out, not sketched.
- Brainstorm partners are welcome: Astra (Codex) `/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex exec -s
  read-only --skip-git-repo-check -c model_reasoning_effort="high" -o out.md - < brief.md` and Argon
  `/Applications/Gemini.app/Contents/Helpers/agy -p "<prompt>" --model gemini-4-argon-high`. Check their math line by
  line; credit what you use; record what failed.
- Experiments: register numeric predictions in UNIFY.md (committed) before any run. Mac CPU runs are free (Lean trackers
  via LEAN_S's `lean_run.py` as THEORY_DEEP §9 did; S5 code in `.claude/worktrees/invariance-3e22f3/research/`). Any
  Modal spend: message the parent session with the registration and cost first and wait for the go. Modal launches are
  `modal deploy` + `.spawn()` from a script that exits, results on a Modal volume. Checkpoint selection only after every
  term is fully on, on validation at training length, never on test lengths.
- A candidate term is worth Neo's attention only if it matches FULL+Nc on the cheap domains (Lean, S5, counting if
  affordable) with fewer moving parts, or explains an anomaly with a prediction that then comes true.
- Do not edit the paper or the master table. Do not push. Never touch main. Keys in `~/.polyformer_keys` are never
  printed or logged. zsh aliases are interactive: use `/bin/rm`, `/bin/cp -f`.
- Report to the parent in one or two lines when something lands (a proof, a failed candidate, a registration that
  needs spend); results live in UNIFY.md. Being wrong is fine and expected; say so plainly.
