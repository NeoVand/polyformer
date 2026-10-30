# B2. The cognitive lens: three behaviours no one expects from a language model

Reason's (1990) taxonomy of human error separates **slips and lapses** (misapplying a rule, losing your place) from
**mistakes** (holding the wrong rule). Your clock and certificate remove slips and lapses, with a proof. What remains is
the interesting part of a mind: choosing rules, knowing which ones you can trust, and getting faster at them.

## 1. Three examples, one question, forever

**The demo.** You type three input→output examples of a rule you just invented. The 4B model in your browser proposes
rules, tests them in its own certified execution, asks you the one input that splits its finalists, then states the
rule with a guarantee and applies it without error to an input 10,000 times longer. Shown a counterexample, it revises
in one shot.

**Human capacity.** Learning a rule over variables from a few examples (infants: Marcus et al. 1999), applying it to
anything, and choosing the decisive experiment, which people do badly (Wason's 2-4-6). The
standing objection to neural networks is that they cannot extend a rule universally (Fodor & Pylyshyn 1988; Marcus
1998). In-context learners of regular languages use n-gram heads (Akyürek et al. 2024). Your
theorem says plain decoding never can.

**Assets.**
- Savant writes tables; INTERP's small interpreter ran unseen random tables exactly to 10,000 events.
- The certificate makes "this candidate fits the examples" a trustworthy check, and "these two candidates disagree
  here" an exact one.
- Myhill–Nerode minimisation picks the simplest consistent rule and merges equivalent candidates.
- Execution cannot slip, so any later mismatch indicts the rule, never noise: one counterexample suffices.

Nothing guarantees the right rule from three examples (Gold 1967); the guarantee is consistency and identical
application forever. Known: hypothesis search in Python (Wang et al. 2024), ARC
induction (Li et al. 2024), L\*. New: the proposer is the certified executor.

**48-hour experiment.**
- **Rules:** 100 hidden random minimal Mealy machines (2–4 states, 2–3 renamed input symbols) and 20 nameable ones
  (parity, mod-3 counter, "flip after two b's"), each with three examples of length 12.
- **Search:** Savant, untrained for this, samples 32 tables. A fixed outer loop, like the clock, certifies each
  (≤12 rows), runs it on the examples, keeps and minimises the survivors, then runs the finalists on probes the model
  proposes and asks the one where they differ.
- **Scoring:** exact product-automaton equivalence with the hidden rule, then 1,000 strings of up to 10,000 symbols.
- **Baselines:** Qwen and a frontier model transducing in context at 100–10,000 symbols; a frontier model writing
  Python is the honest ceiling.
- **Kill:** fewer than 20% of 2-state rules yield any consistent candidate (REASON's known
  bottleneck), or induced tables fail certification at twice the rate of described ones.

**Why it matters.** A learner without slips learns from every error: it picks up an exact skill from a few
demonstrations at use time, with no training run, and keeps it. It answers the systematicity critique from inside a
pretrained network, not a hand-built hybrid.

## 2. It tells you where it will fail

**The demo.** Before a 100,000-step task, the model says either "guaranteed exact" or "my first mistake will be at
step 41,307: I confuse `tau` with `taub` in row 12". It fails at exactly that step. Then it renames its own symbols,
re-checks itself and runs clean.

**Human capacity.** Metacognitive monitoring and control (Nelson & Narens 1990): knowing what you know, then changing
strategy, here choosing distinct names (pattern separation by choice). Humans introspect poorly (Nisbett &
Wilson 1977). LLMs cannot self-correct reasoning without external feedback (Huang et al. 2024), and their calibration
is statistical (Kadavath et al. 2022). Your no-finite-test theorem goes further: an ordinary LLM cannot know its
long-run reliability, even in principle.

**Assets.** The iff certificate; bitwise-deterministic ticks; head maps and per-row margins; the measured failure mode
(near-duplicate names). Under the clock the first error is a deterministic function of the input and the failing rows,
so the forecast is near-certain by theorem; the real risks are the deployment path and the repair.

**48-hour experiment.**
- **Programs:** every PROMPTBOX, REGS and ARITH program with a failing row, plus programs built with confusable names.
- **(a) Forecast:** on 100 long inputs per program, forecast the first error step; score exact agreement on the WebGPU
  path and the server.
- **(b) Repair,** in up to 3 rounds, with three arms: random renaming from the pool; renaming proposed by the model,
  told which rows failed; and margin-guided renaming by key separation in its own lookup heads.
- **Kill:** forecasts miss on more than 1% of browser runs (the guarantee is not real where users run it), or no arm
  repairs 30% of failing programs (the model has no lever for control).

**Why it matters.** Its confidence is a theorem: guarantee and refusal are both exact, and it locates a failure before
it happens. Safety cases need exactly this; no model offers it.

## 3. Practice makes it faster, never sloppier

**The demo.** Run the same 10,000-event task again and again: the tick count falls along the power law of practice,
and every answer stays exact, because the model takes only shortcuts it has certified.

**Human capacity.** Automatisation: a deliberate procedure turning into recognition at a glance (Newell &
Rosenbloom 1981; Logan 1988; ACT-R's production compilation). LLMs spend fixed compute per token and never get
faster at a skill while using it. Their learned shortcuts are brittle (Liu et al. 2023).

**Assets.** The composition theorem, the certificate, and free ground truth: a two-event shortcut row is checked against
two certified slow ticks. As in Logan's race, the first time the model meets a (state, event pair) it answers both
ways; if they agree, that pair becomes a certified one-tick shortcut. Speculative decoding re-verifies every token; a
certified shortcut is checked once.

**48-hour experiment.**
- **Tasks:** S5 words and digit addition.
- **Arm A:** one tick on a two- or three-event block (the raw intuitive span).
- **Arm B:** certified composite rows appended to the program (production compilation); this also measures
  Anderson's fan effect as the program grows.
- **Report:** the certified fraction of k-step rows, ticks and wall-clock against practice, and exactness at 10,000.
- **Kill:** under 20% of 2-event rows certify in either arm, or wall-clock does not fall because tick cost rises with
  block length.

**Why it matters.** A system that gets cheaper with use without trading accuracy for speed. It also measures, with a
certificate, how many steps one forward pass can take: an intuitive span to set beside Cowan's four chunks.

## If I could only pursue one

Idea 1. Learning is what an outsider instantly calls intelligence. It answers the oldest critique of neural networks
with a guarantee, not a benchmark; it uses every asset (writing, certifying, running, minimising); and it attacks your
real bottleneck, writing programs, instead of avoiding it. It also contains idea 2's best moment: a learner with no
slips knows every surprise is about the world, not about itself.

Register the identification rate by rule size first. If Savant cannot write a 2-state table from three examples, that
number tells you where to train next.
