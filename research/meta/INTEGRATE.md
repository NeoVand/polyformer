# INTEGRATE: a harness for making a model connect what it knows (Fable, 30 Oct 2026)

Neo: agents suggest narrow things, loop in desperation when results disappoint, and never connect the two or three
distant insights that would make the big idea. What harness would make a frontier model integrate its knowledge of
physics, algorithms, learning theory and its ability to build and train models?

## Why it fails (mechanism, not excuse)

1. **Retrieval is cued by context.** What a model recalls is what the recent tokens make likely. A context full of
   LoRA margins and canvas rows cues more of the same; general relativity never fires because nothing in the window
   points at it. Humans get random cues (walks, sleep, other people); a session gets none.
2. **Caution is rewarded twice.** Alignment training and our own rules ("honest, verify, narrow is fine") both pay for
   defensible claims. After a week of gates returning NARROW, the prior becomes "everything is known".
3. **No level change when stuck.** A disappointing result is answered with a variant at the same level (another
   hyperparameter, another seed) instead of a move up (what theorem is this an instance of), down (what mechanism), or
   sideways (what field has this problem).
4. **Shared transcripts, shared blind spots.** Orchestrator and worker read the same history; a second opinion from the
   same context is one opinion.
5. **Kill without repair.** Prior-art gates discard; nobody takes the "what remains open" column as a generator.

## The harness (each step is a prompt a session can run; keep outputs short and many)

- **Forced distant mappings.** Fix the problem in one paragraph. Draw 8 fields *by diversity, not relevance*
  (differential geometry, symbolic dynamics, coding theory, control theory, statistical physics/RG, category theory,
  thermodynamics, developmental biology, economics...). For each: restate the problem in that field's language, name the
  object there that plays the role of our state / view / certificate, name the theorem or technique that field uses for
  it, translate back. Most are junk by design; keep the one or two that import a theorem we did not have.
- **The level ladder.** Every idea written at five levels: phenomenon, mechanism, theorem, architecture, experiment.
  An idea with an empty theorem row is narrow by construction; an idea with an empty experiment row is not an idea yet.
- **Constraint sweep.** List every constraint (Neo's, and the ones we inherited by habit). Drop each one alone; write what
  becomes possible. This is the step that would have produced the frozen-twin family.
- **Generate / kill / repair, as three roles.** One pass generates 30 one-line ideas without checking anything. A gate
  kills with prior art. A third pass *repairs* each killed idea using the "what remains open" column as the seed, and
  sends the repaired idea back to the gate. Iterate twice before anything is called narrow.
- **Invariant hunting.** For the current system ask: what is conserved, what symmetry, what duality, what is the
  fixed point, what is the minimal realisation. Physics habits that find structure.
- **Read for unused theorems, not for prior art.** "List 20 theorems in dynamical systems that nobody has applied to
  certification of learned recurrences" is a different query from "has X been done".
- **Random pairs from the glossary / zoo.** Sample two nodes, force a connection, discard or keep. The idea zoo's edges
  are this machine run for years; the glossary is its seed.
- **Memory of dead framings.** A list of framings already tried and why they died, read before any brainstorm, so
  loops are not re-walked. No variant may be run without a stated level change.

## First pass on our problem (30 Oct, Fable alone, 8 fields, ~20 minutes)

Problem: learned recurrent state that is exactly certifiable; snap onto finite codes; finite certificates; robustness
to quantisation; "contract and separate" (Brandoit).

- **Symbolic dynamics (hyperbolic dynamical systems) — HIT.** A hyperbolic map admits a *Markov partition* (Sinai,
  Bowen): finitely many cells whose images are unions of cells, so the continuous dynamics is coded exactly by a
  shift of finite type, i.e. a finite automaton. Our snap is a Markov partition; the gate's basin condition
  F_a(B_q) ⊆ B_δ(q,a) *is* the Markov property; "contract and separate" is hyperbolicity (stable and unstable
  directions); UNIFY's finding that every miss lies along a near-neutral Lyapunov direction is the failure of uniform
  hyperbolicity; the aimed tube (perturb along the top Lyapunov direction) was a hyperbolicity-enforcing regulariser
  without the name. Imports: Bowen's **shadowing lemma** (every pseudo-orbit of a hyperbolic system is shadowed by a true
  orbit) is the theorem for *quantisation robustness*: a rounded (q4) trajectory stays within a computable distance of
  an exact one, which turns our empirical "margin ≥ 3 survives a 2.5 shift" into a bound; **structural stability** says
  hyperbolic systems keep their symbolic dynamics under small perturbation of the map, i.e. under weight quantisation;
  the **no-finite-test theorem** becomes "non-hyperbolic (neutral directions) ⇒ no finite Markov partition". Prior art
  to check: Casey 1996 (RNN dynamics as automata), Tiňo et al., Omlin & Giles (automata extraction), "shadowing" in
  neural ODE / RNN robustness.
- **Control theory (contraction analysis) — TOOL.** Lohmiller & Slotine's contraction theory certifies convergence of
  nonlinear systems with a state-dependent metric M(x), found by SOS programming. UNIFY searched for a continuous
  certificate only in the Euclidean metric and failed; a learned or SOS contraction metric is the general version.
  Kalman–Nerode duality says our Myhill–Nerode losses are minimal-realisation theory.
- **Coding theory — FRAME.** A certificate with margin m against a perturbation of size e is a code of distance ≥ 2e+1.
  Glyph alphabets and code vectors can be *designed* for distance (self-legibility as code design).
- **Renormalisation group — SPECULATIVE.** Collapsing tokens layer by layer is coarse-graining; an RG fixed point is a
  scale-invariant computation, i.e. length generalisation; parallel-prefix shortcuts are an RG flow on the sequence.
  Suggests training the fixed point *in scale* rather than in time. Untested framing.
- Differential geometry (holonomy): already mined (holonomy attention); category theory (certificates compose =
  functoriality; confluence = coherence): useful for Lean, not for ideas; thermodynamics, biology, economics: nothing.

## What the pass implies

The "sick" single paper is not "a VLM adds numbers" and not "a new layer". It is **exact reasoning as hyperbolic
symbolic dynamics**: one theory that (a) explains the snap, (b) states the certificate as the Markov property,
(c) derives quantisation robustness from shadowing, (d) classifies architectures by whether they can be uniformly
hyperbolic on the reachable set (full attention cannot; pinned, canvas and NFSM-style maps can), (e) gives a new training
term (enforce hyperbolicity), and (f) is demonstrated by the canvas machine and the interpreter in the browser. Theory
first, artefact as evidence. The pass took twenty minutes; the gate on it takes a day; the theorems take weeks.

## Second pass (30 Oct, Neo: "do it twice more, be open"; problem reframed as induction + exact execution, ARC-shaped)

Fields drawn by diversity: statistical learning theory, linguistics, compilers/PL, neuroscience, immunology, reversible
computing, game theory, music theory.

- **Statistical learning theory (MDL / Solomonoff induction) — FRAME.** Few-shot rule induction is compression: the
  shortest program consistent with the demonstrations is the one that generalises. Under our canvas ISA the selection
  criterion among programs that fit is description length, and the language model is the prior over programs. Known in
  the ARC community (Ferré's MDL approaches; LLMs as program priors), but it fixes the metric and says the ISA must make
  ARC rules *short*: the ISA's inductive bias is the whole game.
- **Linguistics (grammar induction; Gold 1967; Angluin's L* 1987) — HIT for interactive environments.** Gold: a class
  of languages is not identifiable from positive examples alone without bias, which is why ARC needs a DSL prior. Angluin:
  a finite automaton *is* exactly learnable with membership and equivalence queries. ARC-AGI-3's interactive games are an
  environment you can query. So: L*-style active probing learns the environment's automaton exactly, and the certified
  canvas machine then runs it exactly. Known algorithm, new seat; perception → symbols is the learned part. Prior art to
  check: active automata learning for games / reward machines.
- **Compilers and programming languages — TOOL.** Version-space algebras (FlashFill) represent *all* programs consistent
  with input/output examples compactly: exact few-shot synthesis. Sketch-based synthesis: the LM proposes a sketch with
  holes, an exact procedure fills them. Partial evaluation: specialising the interpreter to a fixed program is the first
  Futamura projection, i.e. a per-program adapter is a compiled interpreter (a cute reading of LoRA-per-program).
- **Neuroscience (complementary learning systems; hippocampal replay) — FRAME.** Fast per-task adaptation (test-time
  training, the 2024 ARC winners' trick) is the hippocampus; consolidation into slow weights by replay is the cortex. A
  model that gets better at ARC by solving ARC = per-task certified adapters consolidated with replay.
- **Immunology (clonal selection) — LOW.** Generate many candidate programs, select by fit, mutate the fit ones: FunSearch
  already does LLM-mutate + evaluate; with exact in-model verification it is the same shape.
- **Reversible computing (Toffoli, Margolus block rules) — FRAME for undo and physics.** Reversible cellular automata are
  local, parallel, exactly invertible and conserve by construction; a reversible ISA gives exact undo for free and is the
  right substrate for the lattice-physics demos.
- Game theory, music theory: nothing.

## Third pass (30 Oct)

Fields: cryptography, operations research, topology, algorithmic information theory, probability, ecology, chemistry, law.

- **Cryptography (verifiable computation, PCPs, zero knowledge) — business FRAME only.** Spot-check certificates for a
  long run exist (encode the transcript, check few random positions). For us the reference automaton is known, so a run
  is verified by re-running it; PCPs add nothing to exactness. They matter for *audit*: a verifiable transcript of an
  agent's ledger is a product feature, not a research result.
- **Operations research (SAT/CDCL, constraint programming) — TOOL.** Synthesis as constraint solving with the demos as
  constraints is how exact synthesisers (Sketch, CEGIS proper) work; the LM proposes, the solver fills, the executor
  verifies. The transferable idea is **nogood learning**: keep *why* a hypothesis failed (which cells mismatched) and
  constrain the next one. Feed the mismatch diff back as a fovea view: the visual revision loop with structured feedback.
- **Topology (connected components, holes) — FRAME.** ARC speaks in objects: components, holes, symmetry. The canvas ISA
  needs topological perception primitives (flood fill, component labelling, hole count), as every strong ARC DSL has.
- **Algorithmic information theory — same as MDL.** Chollet's skill-acquisition-efficiency definition is this.
- **Probability (PAC bounds) — nothing for ARC's 2–5 examples;** and the certificate makes generalisation bounds for the
  executor unnecessary (rows are checked, not estimated).
- **Chemistry (reaction networks, Petri nets) — known.** Petri nets are concurrent local rewriting with place invariants;
  that is the lattice-physics canvas and its conservation laws (S4).
- **Law (precedent; case-based reasoning) — HIT: certified library learning.** DreamCoder grows a library of reusable
  functions from solved tasks so later programs get shorter. With our Theorem C (certificates compose), every solved task
  can add a *certified macro* to the ISA: its certificate is composed from its parts, no new rows. The MDL prior sharpens
  as the library grows; the model gets measurably smarter by solving. Prior art to check: DreamCoder on ARC, library
  learning with verification.
- Ecology: nothing.

## What three passes add up to (the ARC-shaped "ideal model", as a sketch to be gated)

Perception → symbols (the VLM reads the grid; topological primitives). Synthesis = the LM proposes short canvas-ISA
programs (MDL prior), sketches filled exactly (version spaces / CEGIS). Execution exact and in-model (certified rows).
Verification = exact match against demos; the mismatch diff is fed back visually (nogood learning) for revision. Fast
per-task adaptation (test-time training) consolidated by replay, plus **certified library learning** so programs shorten
over time. For interactive ARC-AGI-3: L*-style active probing of the environment, then exact execution. Theory: MDL as the
induction principle, Gold for why the ISA's bias is everything, Theorem C for composed certificates, hyperbolicity for the
executor's reliability. Every piece has a name from a different field; the conjunction is the thing to gate.

---

## Hill-climbing the harness (30 Oct, after Neo set the goal: beat ARC, ARC-AGI-3 first)

### What limited rounds 1–3

1. **I chose the fields.** "Diversity" drawn by me still landed on physics and CS theory. Fix: a fixed list of 40 fields,
   including non-academic crafts and practices, drawn by dice (digits of π), not by taste.
2. **Shallow dismissals.** Most fields got one sentence of "nothing". Fix: a minimum per field: name 3 objects and 3
   techniques there, and run the mapping both ways (what does our problem teach that field?) before dismissing.
3. **Whole-problem mapping.** I mapped "the problem" each time. Fix: decompose the goal into sub-problems first and map
   fields to sub-problems; fits are sharper.
4. **No recombination, no scoring.** Hits were listed, not combined into a candidate system with an experiment, and not
   scored, so there was nothing to climb. Fix: recombine into 1–2 candidate systems; score novelty / feasibility / cost /
   impact 1–5; the next round attacks the best candidate's weakest sub-problem plus one random restart.
5. **No adversary inside the round.** Fix: for every hit, the strongest objection and the closest prior art I can recall,
   immediately.
6. **No grounding.** I mapped without the benchmark's facts. Fix: a ten-minute ground-truth read before mapping (the ARC
   survey session supplies it for round 6).
7. **Constraints unexamined.** Rounds 2–3 skipped the constraint sweep. Fix: sweep at round start; "history is lessons,
   not a prison" (Neo).

### Decomposition of "beat ARC-AGI-3" (interactive games, no instructions, scored on actions vs humans)

P1 perception (cells → objects, sprites, counters) · P2 rule induction from transitions (state, action → next state) ·
P3 exploration (which action next, to learn fastest) · P4 goal inference (what counts as progress with no reward text) ·
P5 planning with the learned model · P6 memory across levels (mechanics persist and compose) · P7 efficiency (few
actions; compute per step) · P8 execution exactness (no drift once the rule is known).

### Round 4 (fields by π digits over the 40-list: archaeology, accounting, architecture, astronomy, cooking, ethology, cartography, child development)

- **Accounting → P2/P8: reconciliation.** Every transition must balance against the current model; a mismatch is an
  audit exception that triggers repair. The canvas as the agent's *ledger* of observed transitions (the data for
  synthesis). FRAME.
- **Architecture (pattern language) → P2/P6: a pattern library of mechanics** (gravity, pushing, keys and doors,
  counters, teleports) as priors. The LM's cultural knowledge of game conventions is a prior over mechanics that
  theory-based RL (EMPA, 2021) did not have. HIT-ish: rank hypotheses by game-design plausibility.
- **Astronomy (Kepler; transits) → P2: hidden-variable induction.** When observed cells cannot explain a transition,
  posit a hidden counter or flag (a planet you cannot see, inferred from its pull). Add latent state to the hypothesis
  space, penalised by MDL. FRAME, important for games with hidden counters.
- **Ethology (play, curiosity, violation of expectation) → P3: act to split hypotheses.** Choose the action on which
  surviving hypotheses disagree most (expected information gain). Known in Bayesian RL and as L*'s equivalence query;
  the efficiency of the whole agent lives here. TOOL.
- **Cartography (frontier exploration, SLAM) → P3/P5: a state graph of visited states with frontier-based exploration**
  and planning on the graph. TOOL.
- **Child development (core knowledge; "the child as scientist") → P1/P2: ground the ISA in core-knowledge priors**
  (object permanence, contact causality, number, geometry, agents), which is exactly what ARC was designed around
  (Chollet cites Spelke). FRAME; EMPA did this with hand-coded parsers.
- Archaeology (experimental re-enactment = test by acting; seriation = order levels by complexity), cooking: little.

**Round-4 candidate system, "theory-based agent with exact models":** VLM parses the grid into objects; the LM proposes
short rule programs in a core-knowledge ISA, ranked by MDL and by game-convention plausibility; hidden variables allowed;
every transition reconciled against the current program; exploration chooses the action that best splits surviving
programs; planning searches the *exact* learned model; mechanics that survive a level join a certified library.
Adversary and prior art: Theory-based RL / EMPA (Tsividis, Tenenbaum et al. 2021) learned Atari-like games by
synthesising theories in a DSL and planning; WorldCoder (2024) had an LLM write a Python world model from interactions
and plan; Code World Models (2025); VGDL rule induction; Schema Networks (2017); object-oriented MDPs (2008). Our deltas:
perception by the VLM instead of hand-coded parsers (and ARC-3 grids may not need it, which shrinks the delta), exact
certified execution of the induced model, the LM's convention prior, certified library across levels, in-browser. Scores
(1–5): novelty 3, feasibility 3, cost 3, impact 5 if it places. Weakest sub-problems: P3/P7 (sample efficiency of
synthesis) and P4 (goal inference with no reward text).

### Round 5 (hill-climb on P3, P4, P7; fields: experimental design, philosophy of science, detective fiction, military doctrine, medicine, reverse engineering, puzzle design, pedagogy/cognitive science)

- **Reverse engineering (symbolic execution, differential testing) → P3/P7: compute the discriminating action.** For two
  surviving rule programs, run the exact executor symbolically to find an action sequence on which they differ, then do
  it in the environment. One action per bit of hypothesis uncertainty. TOOL, concrete, ours to implement.
- **Philosophy of science (Lakatos: protect the core, adjust auxiliaries) → P2/P7: program repair, not resynthesis.**
  When a transition contradicts the model, search minimal edits of the program (edit distance in the ISA) before
  sampling a new one. Known in PL as program repair / CEGIS refinement; cheap and exactly the generate–kill–repair loop.
  TOOL.
- **Detective fiction (the dog that did not bark) → P2: null transitions are evidence.** An action that changed nothing
  constrains the rule as much as one that did; log and use no-ops. TOOL.
- **Medicine (differential diagnosis; treat empirically while diagnosing) → P5: plan robustly under model uncertainty.**
  Choose actions that make progress under most surviving hypotheses while discriminating among them. Bayesian RL in
  practice. TOOL.
- **Military doctrine (reconnaissance by fire) → P3:** provoke the environment to reveal mechanics; same as information
  gain, different emphasis on cheap probes early. LOW.
- **Puzzle design + pedagogy (Shafto, Goodman & Griffiths 2014, pedagogical sampling) → P4/P2: the designer-intent
  prior. HIT.** ARC environments are made by humans who intend them to be learnable without instructions: one new
  mechanic per level, goals signalled by salient objects (exits, keys, counters), examples chosen to be informative.
  Pedagogical-sampling theory formalises inference from a helpful teacher: a shown example or level is evidence not only
  of the rule but of *why that example was chosen*. Applied to ARC-1/2 demos it is a principled Occam-plus (a corner case
  appears because it matters); applied to ARC-3 it gives goal inference for free: the goal is the state the designer made
  salient and reachable. Prior art to check: pedagogical priors in program induction; "designer intent" in ARC analyses.
- Experimental design (Bayesian adaptive design) → P3: the formal version of information-gain exploration. TOOL.

**Round-5 candidate, "the pedagogical theory-based agent":** round 4's system plus the designer-intent prior for goals
and example selection, symbolic execution for discriminating actions, repair before resynthesis, null transitions as
evidence, robust planning. Scores: novelty 4 (the pedagogical prior and exact discriminating actions are the new parts),
feasibility 3, cost 3, impact 5 if it places. Weakest remaining: P1 if ARC-3 grids need no VLM (then the VLM's role is
only the convention prior and the language), and the unknown of ARC-3's action space and scoring, which the survey must
settle before round 6.

### Dead framings (do not re-walk)
"Loops that converge" as a headline (Attractor Models); passive registers in a delta-rule state (PROBES, Brandoit);
latent programs written into hidden states (three collapses); adapter-per-operation as the general method; the
hyperbolic framing as an intelligence result (it is a reliability result).

## Round 6 (30 Oct): isolated agents on dice-drawn subfields — mixing

Eight isolated agents (Opus), each one subfield, no knowledge of each other or of our candidates; reports in
`research/meta/rounds/r6_*.md`. **Zero HITs.** Every agent wrote an honest "nothing" after the minimum effort, which the
old rounds never did. The new signal is *convergence*: independent fields landed on the same handful of tools, which says
these are the real structure of the ARC-3 problem rather than one analyst's taste.

Converged tools (count = how many of the eight found it independently):
- **Discriminating probe** (4: SIR identifiability, comping sitter-in, DMAIC alias-breaking, tectonics Wilson–Sykes):
  act where surviving hypotheses disagree most; prune pairs no action can separate. Prior art: Lindley 1956, L* 1987,
  Box & Hill 1967, query by committee 1992.
- **Conservation ledger / budget closure** (3: SIR stoichiometry, tectonics Hess budget + NUVEL loop closure, status
  see-saw): the left null space of per-transition count changes gives invariants; a broken invariant reveals hidden
  state or a new mechanic; closed action loops that fail to close localise model errors. Prior art: Feinberg 1979,
  Liu & Tegmark 2021, homing sequences 1993.
- **Replay-then-tilt** (3: comping contrafact, status platform/tilt, RRS overriding Sections): on a new level, replay
  the old mechanics and open new hypotheses only at the first failed prediction; new rules override, never rewrite.
  Prior art: options 1999, kishōtenketsu level design.
- **Two-sided acceptance** (2: DMAIC Red-X "make it come and go at will", QDE identification grade): a mechanic enters
  the planner only when the agent can both produce and suppress it by choice. Prior art: Bhote 1988, version spaces 1982.
- **Residual typing** (2: DMAIC chart patterns → counter/timer/toggle, GUM non-shrinking residual → re-segment): the
  *shape* of mispredictions names the missing hidden variable. Prior art: Rivest & Schapire 1993, AutumnSynth 2023.
- **Guard-banded commit** (1, GUM; echoed by comping "laying out"): act when the risk carried by unresolved rules is below
  the cost of the cheapest probe; the efficiency controller for RHAE scoring. Prior art: information-directed sampling
  (Russo & Van Roy 2014).
- **Goal from reincorporation / salience** (status, QDE rare-feature LR): the goal reincorporates what the designer
  showed twice; agrees with round 5's pedagogical prior.
- **Latches and hearings** (RRS): event-triggered facts held until release; on a misprediction, exonerate first.
- **Diagnosis** (comping, status, RRS, independently): humans are fast because the repertoire of designed game forms is
  small; recognising a form from 1–3 events, not inducing from scratch, is where the efficiency is.

**Candidate R6, "the efficiency layer":** a standard-harness ARC-3 agent whose world model is a precedence-ordered
decision list over pairwise relations with latches; a conservation ledger that flags hidden state; discriminating probes
chosen by symbolic execution; two-sided acceptance before planning; residual typing to seed hidden variables; replay-then-
tilt across levels; guard-banded commit to spend actions only when probing costs more than the risk. Scores: novelty 2
(every piece has prior art; the package is engineering), feasibility 4, cost 2, impact 3 (legible only through cost or
the standard-harness gap). Against the survey: Tycho/Retrodict/baseline1 already reach ~100% on the public demo with
LLM-written Python world models at $400–3,000 per run; the frontier's standard-harness score is 62.7% because of memory
management, not induction.

**Hill-climb rule:** round 5 had one HIT (pedagogical prior), round 6 none. One more round under a *restated* goal; if it
adds no HIT, stop generating and build the best candidate under a cost/standard-harness framing.

**What the harness improvements did:** isolation produced honest "nothing" and a convergence signal; dice-drawn
subfields produced depth (GUM's decision rules, RRS's latches, DMAIC's two-sided test) that broad fields never did.
Cost: eight agents ≈ 610k tokens, about 20 minutes wall.
