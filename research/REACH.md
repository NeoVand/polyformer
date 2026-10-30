# REACH: what Nerode training actually solves (24 Oct 2026, 07:40, written at the airport)

Neo's question: what is the general lesson, and does the full recipe solve a big problem X beyond our tasks?
The worry: a strong CS, maths or ML reader laughing that we hit something large and misnamed it.

## The claim, stated at its true size

1. **Likelihood is blind to exactness.** Next-token loss scores a rare per-step state error at a cost that carries the
   loss floor as a factor, so a fluent model with a slowly drifting state sits in a valley as deep as the exact one
   (selection theorem; landscape figure). This is a statement about the objective, not about architecture or scale.
2. **Error compounding is a property of the objective, not of autoregression.** The standard argument says an
   autoregressive model with per-step error eps fails after about 1/eps steps. With the certified signal and closure,
   the state contracts back onto class centres (repair-model equilibrium), so errors do not accumulate. Exact at 64x
   the training length is the empirical face of this.
3. **Equivalence is the cheap supervision.** We never tell the model the state. A checker only says "these two
   histories end in the same state". Every interpreter, compiler, CAS, proof kernel, simulator and game engine emits
   this for free, at any length. Myhill-Nerode says that is exactly the information that defines the state.

The one-line version for a professor: exact state is the minimal automaton, the standard loss cannot select it,
and checker-certified equivalences can, at any length, with a fixed norm closing the loop.

## What a strong reader will say, and our answer

| They will say | Answer in the paper |
|---|---|
| "This is bisimulation / self-predictive RL" (Ferns et al.; Zhang et al. DBC; Ni et al. 2024; Tang et al. 2023) | Cited. Our three clauses are the bisimulation conditions on histories. New: the blindness theorem (why likelihood cannot get there), certified pairs from external checkers, closure, exact extrapolation. |
| "Vafa et al. 2024 already used Myhill-Nerode" | Cited. They use Nerode to diagnose incoherent world models; we train with it and show why likelihood leaves the incoherence. Diagnosis then cure. |
| "This is Angluin's L* with gradient descent" | NOT cited yet. It is a strength: L* learns the minimal automaton from membership and equivalence queries; our checker plays the equivalence oracle on histories. Add Angluin 1987. |
| "Pitfalls of next-token prediction" (Bachmann & Nagarajan, ICML 2024) | NOT cited yet. Closest conceptual ally: teacher-forced likelihood fails to learn some tasks. Our theorem is a quantitative version for state. Must cite. |
| "Othello-GPT has a world model from next-token alone" (Li et al. 2023; Nanda et al.) | NOT cited yet. Linear probes find an approximate board; we are about exactness at length, where approximate fails. Cite and contrast. |
| "Arithmetic length generalisation is solved by position tricks" (McLeish et al. 2024 Abacus; Cho et al. 2024 position coupling; Zhou et al.) | Zhou cited; add the other two. Those fix the architecture's addressing; ours fixes the objective and needs no task-specific embedding. |
| "Context distillation" (Snell et al. 2022) | Self-distillation (EXEC_LM §12) is certified context distillation; cite. |

## Where X lives (the honest reach)

- **Long-horizon code and agents.** Tracking program or tool state over thousands of steps, with the interpreter or
  environment as the checker. This is the commercial X: agents that do not lose the plot.
- **Arithmetic and counting.** Both are state machines over digits or tokens. Any two prefixes with the same running
  value or carry are certified equal by a calculator. The recipe should give exact counting and exact long addition
  far past the training length. This is the demo a reader instantly understands.
- **Formal mathematics.** Lean certifies rewrite chains (our LEAN_S result: exact to 4,096 on 9 of 9).
- **Games, planning, simulators.** The engine certifies equal positions.
- **Language.** Only with soft checkers; the noise theory says near-miss errors are tolerated, far errors are not.

## The bridge to LLMs (why §12 matters most)

A transformer LLM has no carried state to normalise. Nerode self-distillation needs none:
p_theta(next | long history u, then w) is pulled to stop-grad p_theta(next | certified short equivalent v, then w).
For counting, v is "count = n"; for arithmetic, v is the simplified expression; for code, v is the canonical program.
If §12 passes (SD within 0.05 of ORACLE at 256), the recipe applies to any LLM as a consistency loss on certified
rewrites of its own context. That is the sentence that turns this from "a trick for small trackers" into
"a training principle for language models".

## One cheap test worth registering (proposed, NOT launched; Neo decides)

Counting and multi-digit addition with a small model: train to 32 digits or tokens, test at 1,024 and 4,096, arms
ordinary / next-state + norm / full recipe, 3 seeds, certified pairs from Python ints. Under $5 on Modal.
Baselines to quote: Abacus embeddings (about 6x extrapolation). If the full recipe is exact at 32x to 128x, that is
a Figure 4 panel and a line in the abstract.

## Caveats a reviewer will press

- S5 group words (INVARIANCE R2, 07:31): with the fixed norm, next-state alone is near exact
  (0.994 / 1.000 / 0.998 at 1,024) and adding the signal is exact on only 1 of 3 (0.855 / 0.916 / 1.000).
  The signal is not uniformly needed. The claim must be "the signal is what makes exactness selectable when
  next-state is not enough", with the domains where each ingredient matters stated plainly.
- All exact results are small models. The LLM claim rests on §12 and the in-model work.

## Beyond language models: what the full recipe is, in general (added 07:42 after Neo: "it might have more legs")

The recipe, stripped of our tasks: from any stream of observations, learn a state that (i) predicts the next
observation, (ii) predicts its own next value, (iii) coincides for histories a checker certifies as interchangeable,
and (iv) lives on a closed set so errors can be pulled back. The joint minimiser is the minimal realisation of the
process, and the blindness theorem says prediction alone cannot select it at length. Nothing here is about language.
The same four pieces already exist, separately, in five other fields. That is the real reach, and also the list a
professor will check us against.

| Field | Their "state" | Their certified equivalence | Their closure | What our result adds there |
|---|---|---|---|---|
| Automata and learning theory | Nerode classes; Angluin's L* | equivalence queries to a teacher | finite state | gradient-trained, length-exact, with a checker as the teacher |
| Computational mechanics, predictive state representations | causal states, the epsilon-machine (Crutchfield and Young 1989; Shalizi); PSRs (Littman, Sutton and Singh 2002) | equal predictive futures | none | a training signal that selects the causal state, and a theorem that likelihood cannot |
| Reinforcement learning and world models | bisimulation (Ferns et al. 2004); value equivalence (Grimm et al. 2020); MuZero, Dreamer latents | the simulator: two action sequences reaching the same state | none | long latent rollouts without compounding error, the known weakness of model-based RL |
| Robotics, navigation, neuroscience | SLAM pose; grid cells and the hippocampal map (Tolman-Eichenbaum Machine, Whittington et al. 2020; clone-structured cognitive graphs, George et al. 2021) | loop closure: two paths that return to the same place | continuous attractor manifolds | a normative account: path integration + landmarks + loop closure + attractor = our four clauses |
| Reliable computation | von Neumann's restoring organ (1956); fault-tolerance threshold theorems | majority agreement | restoring to codewords | the repair-model equilibrium is a learned restoring organ, with a threshold flavour: exact at any length when repairs outpace fresh errors |
| Scientific machine learning | neural surrogates for PDEs, weather, molecular dynamics, which drift and blow up in long rollouts | the solver: two step schedules reaching the same time (semigroup property), symmetries, conservation laws | projection onto the conserved-quantity manifold (our fixed norm is the simplest case) | a reason one-step losses drift, and a stiff path-equivalence signal to stop it |

The thesis line this supports: **exactness at length is a property of the objective, and it needs three things: a
reachable code, a closed state space, and certified equivalences.** Language models, world models, simulators and
brains each have some of these and lack others.

Prior art this adds to the citation list: Crutchfield and Young 1989; Shalizi and Crutchfield 2001; Littman, Sutton
and Singh 2002 (PSRs); Grimm et al. 2020 (value equivalence); Schrittwieser et al. 2020 (MuZero); Hafner et al.
(Dreamer); Whittington et al. 2020 (TEM); George et al. 2021 (CSCG); von Neumann 1956; Lippe et al. 2023
(PDE-Refiner, rollout stability); Ho and Kalman 1966 (minimal realisation).

### Two cheap cross-domain tests (proposed, not launched; Neo decides)
- **Loop closure on a torus.** A path integrator on an m-by-m torus, trained on short walks, tested on walks 64x
  longer; certified pairs are walks with equal net displacement. Three arms, three seeds, under $3 with the K1 tracker.
  The picture is a grid-cell-like torus, and it links straight to neuroscience.
- **A learned physics surrogate.** A pendulum or Kepler orbit stepped by a small network; the pairs are two step
  schedules certified by the solver to reach the same time; closure is projection onto the energy shell. Ordinary
  training drifts off the orbit; the prediction is that the full recipe stays on it at 64x. Under $5.

## Bigger problems: Neo's 07:44 brainstorm, ranked by how strong the checker and the closure are

The recipe has leverage exactly where a field has (a) a cheap, exact checker of history equivalence, (b) a known closed
set to project onto, and (c) a documented failure from drift at length. Ranked:

1. **Learned physics simulators that do not drift** (weather, climate, fluids, molecular dynamics). Checker: the solver,
   via the semigroup property (two step schedules to the same time), symmetries and conservation laws. Closure: the
   conserved-quantity manifold. Failure: long autoregressive rollouts blur or blow up. Competing fixes a reviewer will
   name: unrolled training, the pushforward trick (Brandstetter et al. 2022), noise injection, PDE-Refiner (Lippe et al.
   2023), hybrid models such as NeuralGCM (Kochkov et al. 2024), ACE (Watt-Meyer et al.). Our theory may explain why
   those help (they are next-state prediction at length plus repair). Caveat: in chaos, trajectories cannot stay exact
   past the Lyapunov time; the claim becomes "stays on the attractor and exact on invariants". **Best single
   cross-domain demo**, because it shows the recipe is not only about discrete automata.
2. **Long-horizon reliability of agents.** Agent success decays with task length (METR time horizons, Kwa et al. 2025).
   Checker: tests, environments, tools. Our claim that compounding is the objective's fault speaks to this directly,
   but it needs the in-model bridge (EXEC_LM §12 and the in-model work). Largest audience.
3. **Quantum error-correction decoders.** The decoder tracks the class of an error history; the stabiliser group
   certifies exactly when two histories are equivalent (same homology class), for free. AlphaQubit (Bausch et al.,
   Nature 2024) already generalises from short to very long memory experiments (to check: reported 25 to 100,000
   rounds), so the question there is cost and size, not possibility. Strong checker, crowded and specialised field.
4. **Discovering the state variables of a physical system from data.** The Nerode quotient of observation histories is
   the system's phase space; the minimal realisation is the "theory's state". Prior art: Chen et al. 2022 (hidden
   variables from video), AI Poincare (Liu and Tegmark 2021). Bottleneck: in real experiments the equivalence
   certificates must come from symmetries, gauge redundancy or repeated preparations. High reward, high risk.
5. **Compression.** Prediction is compression, and the minimal automaton is the minimum-description-length model.
   A drifting state pays bits at every lost step, so length-exact state compresses long structured sequences better.
   This is a true reframing more than a new problem. Low priority.
6. **Program equivalence and chemistry.** E-graphs (equality saturation) are literal stores of certified equivalences;
   canonical SMILES certifies that two synthesis routes reach the same molecule. Natural checkers, medium reward.
7. **Systematicity.** The old Fodor-Pylyshyn / Marcus challenge: our results answer the length half (exact at 64x)
   but not the compositional half (MECHANISM: new atoms fail). Say this plainly in the Discussion.

**Recommendation.** The paper claims the principle and shows it on code, proofs, groups, stories and arithmetic.
One cross-domain demo, the physics surrogate, earns the word "general". Items 2 to 7 go in the Discussion and become
follow-up papers. The physics test is ready to launch on Neo's word (under $5).
