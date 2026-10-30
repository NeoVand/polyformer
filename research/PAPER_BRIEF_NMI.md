# Brief for the Nature Machine Intelligence paper

24 October 2026. Written by the orchestrating session for the writing session. This file fixes the narrative, the
figures and the rules; the numbers come from the reports that `HANDOVER.md` indexes (open a report only for the numbers
you cite) and from `COURSE.md` §11–13 for the execution results and the boundary.

## 0. What the paper is

One sentence: **a learned state can be made exact far beyond its training length by one extra training signal, the
requirement that histories a checker certifies as equivalent produce the same state; we prove why the ordinary loss
cannot do this, show the mechanism, and demonstrate exact program execution at 64 times the training length with no
chain of thought.**

Working title (choose one, or better): "Exact state from certified equivalences"; "A learned state that stays exact";
"Keeping an exact state without writing it down". Recommendation: the first, with a plain subtitle.

Audience: Nature Machine Intelligence readers, who are broad, busy and allergic to jargon. The paper must be skimmable
from its figures and first sentences alone. It is a paper, not an audit: the pre-registration, kill rules, caps and
session names stay out of the main text (one paragraph in Methods says the predictions were written before the runs,
with a pointer to the supplementary claims table).

## 1. The narrative arc (necessary and sufficient; nothing else)

1. **Problem.** Models lose track of state over long sequences. Transformers recompute from the whole input and have no
   carried state; recurrent states drift; the standard remedy is to write every intermediate state down (chain of
   thought), which is expensive and still fails beyond the lengths seen in training.
2. **Why training does not fix it (theorem).** A next-token loss over sequences of length L is blind to a per-step state
   error ε: it changes by O(Lε²), while exactness at length N needs ε of order 1/N. Nothing in the ordinary loss selects
   exactness.
3. **The missing signal.** When a checker (a proof kernel, an interpreter, a group law) certifies that two different
   histories lead to the same state, requiring their learned states to coincide is a first-order signal in ε. With a
   second clause, predicting the next state from the current one, the pair becomes a learning rule whose only zero is
   the minimal automaton of the task (the three-clause reading: outputs agree, transitions are consistent, equivalent
   histories meet). The geometric picture: equivalent histories are closed loops; the signal asks for trivial holonomy;
   drift is curvature.
4. **Result on certified domains.** Lean-certified rewrite chains, code execution and group words: exact at 128 to 512
   times the training length on every seed; the same tracker without the signal drifts; a transformer with identical
   supervision collapses. Next-latent prediction alone gets most of the way; the combination is the most robust and has
   the lowest floor. A prover-search proxy: one kernel call per solved problem against 64 to 442.
5. **Result with a language model.** A small recurrent state reading each Python statement through a frozen 0.5B code
   model, trained on programs of at most 16 statements, executes programs exactly to 1,024 statements on every seed,
   generating no tokens; the same model fine-tuned to write its state after every statement is exact at 16 and collapses
   by 64 to 256 while paying 8 tokens per statement; asked for the final state alone it learns less than a shallow table.
   (Use the Modal-confirmed numbers when they land; until then the local 3/3 at 1,024 with the hardware caveat in Methods.)
6. **Mechanism.** The exact state is the minimal automaton: 960 tight clusters for 960 expressions, a ~20-dimensional
   affine code on which rewrites act as near-linear maps; the dynamics correct perturbations (recovery below a threshold
   radius, multi-step contraction); the growth of the distance between certified-equivalent states at training length
   predicts which seeds will drift.
7. **Reach, stated as a law.** The signal selects exactness only within what the per-step transition can fit; it adds
   consistency, never knowledge. Where a step needs routing by name (arithmetic over named variables), a flat state
   cannot learn even the training length, a register-shaped state fits it at once, and at length exactness settles into
   an equilibrium between fresh errors and repair by overwrite that a one-parameter model predicts. On natural mathlib
   proofs a critic given the true proof state does no better than a one-word table at our scale: the content, not the
   tracking, is the limit there. Language supplies no certified distinction for free.
8. **Implications.** Checkers as supervisors: wherever a kernel, interpreter or algebra can certify equivalence, the same
   signal applies. Exact latent computation without chain of thought. The register result points at where structure
   must come from the architecture. The prover is the natural next application.

Everything else (the hardening sweeps, the metric variants, the audit, the dead ends) goes to Methods or the
Supplement, or is cut.

## 2. Figures (four display items in the main text; make them, do not describe them)

- **Figure 1, conceptual (the one a reader remembers).** Three panels in one row. (a) Histories as paths through states;
  two certified-equivalent histories form a closed loop; an exact state closes it, a drifting state leaves a gap (curvature).
  (b) The three clauses as three short arrows into one state box, with the checker (kernel / interpreter) stamping the
  equivalence. (c) Loss against per-step error: the next-token loss is flat near zero (quadratic), the consistency signal
  is a straight line (first order). Monochrome, few words, no equations in the figure.
- **Figure 2, headline.** (a) Exact final state against program length (log axis, 16 to 1,024) for the four arms on code
  execution with the frozen language model, shallow floor dashed, three seeds as light marks, mean as line. (b) Tokens
  generated per statement, four bars. (c) Small panel: the Lean rewrite chains, exact state against length for the plain
  tracker, the signal, next-latent, the combination and the transformer, to 4,096.
- **Figure 3, mechanism.** (a) A 2-D projection of the exact state: 960 clusters for 960 expressions, coloured by one
  attribute, the plain tracker's cloud beside it. (b) Perturbation recovery: distance to the class centre after a kick,
  exact tracker versus plain. (c) Drift prediction: growth of the certified-pair distance at training length against
  exactness at 1,024, with the rank correlation.
- **Figure 4, reach.** (a) Fit at the training length on the arithmetic rung: flat state against register state (and the
  chain-of-thought model), bars. (b) Exactness along a 1,024-statement program for Markov chain of thought and the register
  state, flattening to plateaus, with the repair model's predicted levels as horizontal lines. (c) Natural proofs: the
  critic given the true state, the blind baseline and the one-word floor, three bars with intervals.
- **Table 1.** Exactness at the longest tested length, by domain and arm, seeds exact over seeds run, training length and
  test length. One table, every number traceable.

Figures are produced with matplotlib from the JSON records in the worktrees (paths in HANDOVER.md and the reports);
vector PDF and PNG; consistent monochrome palette with one accent; axis labels in words; captions that state the
finding, not the procedure. If a record is missing, say so in the caption draft and leave a placeholder; do not invent.

## 3. Length and form

Nature Machine Intelligence Article: check the current author guidelines page for limits and follow them; as a working
target, abstract ≤ 150 words, main text about 3,500 words (Introduction, Results with short declarative subheadings,
Discussion), Methods about 2,500 words, up to 4 figures and 1 table in the main text, references about 50, Supplement
unlimited (claims table, proofs, the audit, all per-seed tables). Before writing, read two or three recent NMI articles
of the method-plus-theory kind (open-access versions) and note the wavelength: how the first paragraph is built, how
results subheadings are phrased, how figures are captioned, how limitations are handled. Match it.

## 4. Writing rules

- Plain prose. One idea per sentence. Present tense for what the paper shows. No em-dashes.
- No audit vocabulary in the main text: not "registered", "verdict", "kill rule", "cap", "session", "branch", "arm" (say
  "model" or name the model). Pre-registration is one sentence in Methods plus the supplementary claims table.
- No numbers in prose that are not in a figure or table, except the two or three the abstract needs.
- Honest about every negative, in one sentence each, with its reason; never defensive.
- Prior work named where it belongs: next-latent prediction (arXiv 2511.05963), bisimulation metrics, path independence
  (Anil et al. 2022), the transformer depth bounds (Merrill and Sabharwal), RNN automata extraction, chain-of-thought
  length failures. Verify every citation (POSITIONING.md and NOVELTY.md have the verified ones).
- Theorems in the main text are stated in words with the symbols in Methods; full proofs in the Supplement (PROOFS.md,
  PROOFS2.md, PROOFS3.md are the sources).

## 5. Deliverables

- `paper/nmi/main.md` (abstract, main text, figure captions, Table 1), `paper/nmi/methods.md`, `paper/nmi/supplement.md`
  (claims table with file and section for every number; proofs; per-seed tables; the audit and the dead ends in brief).
- `paper/nmi/figures/fig1.pdf … fig4.pdf` and PNGs, with the scripts under `paper/nmi/figures/src/`.
- `paper/nmi/REVIEW.md`: the ten objections a careful referee would raise and the honest answer or the pending experiment.
- A one-line reply when the first complete draft is committed, with word counts and which figures are real versus
  placeholder.
