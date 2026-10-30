# What the contextualization block must be: a requirements theory

22 October 2026. Assumptions fixed by Neo: keep the residual stream and the MLP (the MLP is revisited in
section 5). Unknown: the block that contextualizes, and the inference procedure around it. Goal: a model
that is more capable in kind, including the capacity to interrupt itself ("no, wait") because a
background process reached a conclusion. Method: list every property the block must have, each with the
theorem or result that makes it necessary, then see what the conjunction forces. Citations are arXiv ids.

## 0. Three facts about the object we are replacing

The transformer block is attention plus MLP on a residual stream, trained by teacher-forced next-token
prediction and run as a synchronous, append-only, fixed-depth map per token. Three theorems bound it, and
they do not weaken with scale:

- **T1 (depth).** Fixed-depth, log-precision transformers compute only TC0 (Merrill & Sabharwal 2207.00729;
  Hahn 1906.06755). Iterated composition of unbounded length is outside, so the model learns shortcuts that
  fail off-distribution (Liu et al. 2210.10749), and state tracking is an illusion (2404.08819). Chain of
  thought of t steps buys t sequential steps: polynomial CoT gives polynomial time (2310.07923). The
  escape from TC0 is sequential depth, obtained today only by emitting tokens.
- **T2 (precision).** With bounded precision, attention over n items loses the ability to separate
  sequences that differ in one early token as n grows, and over-squashes information at the last position
  (Barbero et al. 2406.04267); counting and parity need precision that grows with n (Hahn). Selection
  therefore degrades with length unless the mechanism is rescaled or made exact.
- **T3 (objective).** Teacher-forced next-token prediction cannot learn tasks that require lookahead, even
  with unlimited capacity, because the per-token loss has a shortcut solution and the model never sees its
  own errors (Bachmann & Nagarajan 2403.06963). The state is never forced to be a sufficient statistic for
  the future (Myhill–Nerode; the incoherent-world-model metrics of 2406.03689 are exactly this test).

Everything "more intelligent" that the user wants is on the far side of T1 and T3. Everything we built in
the last two weeks addressed T2-class properties on data that does not need them.

## 1. The properties, with their anchors

**Group A: what a context has to be able to do (capacity).**

- **A1 Selection.** Content-addressed retrieval of one item among n, at cost at most linear in n per query,
  with accuracy independent of n. Anchor: T2. Softmax attention has A1 up to the precision bound;
  scaling logits by log n (scalable softmax) or exact lookup (hashing, T2's input addresses) removes the
  bound. Non-negotiable: every layer that dropped selection lost on language (our SEARCH, BEYOND).
- **A2 Aggregation with counting.** Both mean and sum over a selected set; sum is needed for multiset
  injectivity, counting and parity (Xu et al. 1810.00826; Hahn). Softmax is mean only; unnormalized linear
  attention sums. Cheap; the hybrid already has both.
- **A3 Composition.** Carrying a non-commutative state across unbounded length with O(1) state per token:
  the group atoms of Krohn–Rhodes, Barrington's S5. Anchor: T1 and 2404.08819; constructive: DeltaProduct
  (2502.10297), our holonomy frames (one layer for A5/S5). Necessary for exact state tracking, unrewarded
  by prose at any scale we can run; must therefore be nearly free (a recurrent layer with Householder or
  orthogonal transitions), not a cost the whole model pays.
- **A4 Arity.** Detecting relations among k items with no lexical hub. Anchor: one attention layer cannot
  compose two functions when the domain is large (communication-complexity bound, Peng et al. 2402.08164),
  and pairwise attention needs width or depth polynomial in n for triple detection where a cubic head is
  constant (Sanford, Hsu & Telgarsky 2306.02896). Our SET and Match-3 results are instances. Rewarded by
  reasoning data at scale (2-simplicial exponent change above 2B, 2507.02754); not by prose.
- **A5 Binding.** Role–filler binding at bounded width without interference. Anchor: superposition
  capacity (Elhage et al. 2022, toy models); the taxi world model's failures are interference between
  superposed intersection features (2609.21748). Tensor-product and holographic representations give
  binding by multiplication (Smolensky 1990; Plate); RoPE and frames are the group-action form. Cost: a
  multiplicative path in the block.

**Group B: what the computation has to be able to do (this is where intelligence lives).**

- **B1 Iteration with halting.** The block can be applied k times to its own output with k chosen per
  input, converging to a fixed point, and trained to stop. Anchor: T1 says fixed depth is TC0; looped
  transformers simulate programmable computers (Giannou et al. 2301.13196); an L-layer block looped k
  times matches a kL-layer model on reasoning tasks (Saunshi et al. 2502.17416); recurrent depth at 3.5B
  (Huginn 2502.05171) and looped 1.4B models matching 4B (Ouro 2510.25741) show it scales. Halting is the
  hard part: adaptive computation time (Graves 1603.08983) is unstable; recursive models fix the budget
  and use deep supervision at every iteration (TRM 2510.04871; HRM 2506.21734). Required: iterate, with a
  learnable stopping signal that has a training target.
- **B2 Latent parallel search.** Iteration in a continuous state can hold many hypotheses in
  superposition: continuous chain of thought encodes a breadth-first frontier and solves reachability in
  D steps where discrete tokens need polynomially more (Zhu et al. 2505.12514). This is the formal reason
  to loop in latent space rather than in tokens: tokens collapse the superposition every step. Required:
  the iterated state is a vector, not a symbol, and the read-out is delayed.
- **B3 Belief state.** The state at position t must be a sufficient statistic for the future, not for the
  next token. Anchor: T3; constructive: suffix-conditioned objectives (Belief State Transformer
  2410.23506) learn it where next-token loss does not. Required: an objective term on the block's state,
  not only on the output.
- **B4 Revision.** Committed state and committed output can be retracted. Append-only decoding cannot
  express "no, wait" except by generating more tokens that argue against earlier ones. Anchor: learned
  backspace actions trained by imitation rather than teacher forcing remove the compounding-error
  pathology (SequenceMatch 2306.05426); diffusion and edit models revise anywhere; in latent space our
  REVISE block was free to revise and chose a local mixer, which is T3 again: nothing in the loss asked
  for revision at 2k. Required: a retract action with an objective that needs it.
- **B5 Asynchrony.** At least two clocks: a fast stream that emits, and a slow process that iterates (B1)
  on a state of its own, reads the fast stream, and writes into it only when a condition is met. This is
  the architectural form of "a thought bubbling up". Anchor: multiscale recurrence with learned boundaries
  (HM-RNN 1609.01704; Clockwork RNN 1402.3511); a shared global workspace with limited capacity and write
  competition improves systematic generalization (Goyal et al. 2103.01197); two-timescale modules in HRM
  (2506.21734), with the caveat from the ARC Prize analysis that HRM's gains came mostly from the outer
  refinement loop, not the hierarchy; energy-based blocks whose forward pass is iterative minimization
  with a per-token step count (Energy Transformer 2302.07253; Energy-Based Transformers 2507.02092, which
  report better scaling exponents than standard transformers below 1B and "thinking longer" on harder
  inputs). Our own evidence: forget gates learned a timescale hierarchy and the event router found clause
  boundaries unsupervised; the model wants two clocks. Required: a slow state, an event trigger, a
  broadcast gate, and a reason to use it.

**Group C: what makes it trainable and worth training.**

- **C1 Learnability.** The block's intended computations must be low-leap for gradient descent: functions
  that need coordinated discovery of many features take exponentially many samples on standard
  architectures (Abbe et al. 2302.11055). Our two-week constraint "native terms get learned, compositions
  over depth mostly do not" is this. Required: the property is a primitive of the block, learnable with a
  short curriculum, not an emergent composition.
- **C2 Objective alignment.** A property is learned only if the loss rewards it. Token-averaged loss
  dilutes long-range decisions by about 1/p, roughly 100× (our dilution test); reweighting (Rho-1, LongCE)
  and reinforcement learning on outcomes (the "aha" of DeepSeek-R1, 2501.12948, is "no, wait" learned by
  RL inside sequential CoT) are the known remedies. Every null we produced on prose is C2: the block had
  the property and the loss did not ask for it.
- **C3 Scale robustness.** The payoff must not vanish with size. Mixer gains do (our holonomy margin;
  the Tencent 2026 survey of non-transferring modifications); the T1 and T3 barriers do not, since depth
  and objective are not parameter counts. Required: the block must target T1 or T3.
- **C4 Parallel training and kernels.** Training must not serialize beyond the loop's own depth; the
  block must run on existing kernels or need one small scan. Looped blocks satisfy this (iterations are
  depth); token-level recurrence serializes unless chunked.

## 2. What attention plus MLP already has

| Property | Status | Why |
|---|---|---|
| A1 selection | yes, degrading with n | T2 |
| A2 counting | mean only | softmax normalizes |
| A3 composition | no | shortcuts, TC0 |
| A4 arity | no in one layer | 2402.08164, 2306.02896 |
| A5 binding | weak | superposition interference |
| B1 iteration | no | fixed depth; CoT externalizes it |
| B2 latent search | no | tokens collapse superposition |
| B3 belief state | not enforced | T3 |
| B4 revision | no | append-only |
| B5 asynchrony | no | one clock |
| C1 learnability | yes | its decisive strength |
| C3 scale robustness | yes | |
| C4 kernels | yes | |

Scale absorbs most of group A on natural text, which is why A-class blocks (ours included) return
sub-1% and shrink. Group B is where capability in kind is, and nothing in the standard block has it.

## 3. What the conjunction forces

Keep A1, C1, C4 (do not touch token-level attention; it is the selection organ and the learnable one).
Add B1–B5 without serializing training or diluting the loss. The minimal structure that satisfies the
list:

1. **Two streams on one residual.** The fast stream is the token stream with attention and MLP. The slow
   stream is a small workspace of m slots (m of order 8–64) with its own residual state, read by
   cross-attention from the fast stream and written to it through a gate. Capacity limit and write
   competition are what the workspace result needs (B5).
2. **The workspace is looped.** One shared block applied k times per tick on the workspace state, with
   deep supervision at every iteration and a fixed maximum k (B1, learnable as in TRM); the state is a
   vector throughout and is read out only at broadcast (B2).
3. **Ticks are events.** The workspace ticks at learned boundaries, not every token: the event router we
   already have supplies the clock (B5). Between ticks the fast stream keeps emitting; the workspace's
   previous broadcast persists in the stream.
4. **Broadcast is conditional.** The gate opens when the loop has converged (change in state below a
   threshold) or a learned confidence crosses a threshold, and the broadcast enters the fast stream at the
   current position and, in latent space, revises the stored keys and values of the current event (B4 in
   latent form). This is the bubble-up.
5. **Retraction is an action.** A backspace action at the output, trained by imitation on
   self-generated errors rather than teacher forcing (B4 in output form), so a broadcast that contradicts
   committed tokens can retract them: literally "no, wait".
6. **The workspace has its own objective.** A suffix-conditioned or future-summary loss on the workspace
   state (B3), plus the deep-supervision loss per iteration (B1), plus a ponder cost on k. Without this
   term the workspace will do what REVISE did and go local (C2).
7. **Composition and arity live in the workspace, not the fast stream.** The looped block can carry
   orthogonal state (A3) and, with m slots attending to each other, form hub-less relations among slots
   (A4) at cost m², which is tiny. The fast stream stays pairwise and cheap.

Each piece exists somewhere in the literature; the conjunction does not. Looped models loop the whole
stream synchronously (Huginn, Ouro, MoR), workspaces are not looped and have no halting, belief-state
objectives are applied to the token stream, and backspace is trained without any latent process behind
it. The two-clock, looped, conditionally broadcasting workspace with its own objective is the block the
list forces.

## 4. What can be proved, and what cannot

- **Provable, modest.** A separation: with per-token FLOPs matched, a model with a looped workspace that
  ticks e times per input and iterates k times per tick computes iterated compositions of length
  Θ(ek) that a fixed-depth transformer cannot (corollary of T1 and 2301.13196). Also a capacity statement
  for superposed search in an m-slot workspace, extending 2505.12514 from one thought vector to m slots
  (the frontier splits across slots; the bound improves by about a factor m until interference, by the
  superposition capacity argument). Both are worth writing down; neither is a surprise to a theorist.
- **Provable in principle, hard.** That conditional broadcast strictly helps over periodic broadcast at
  equal compute. One would need a task family where the time at which a conclusion becomes available is
  input-dependent; the statement is then about adaptive versus fixed computation (a known theme since
  ACT) and the proof would be a lower bound for the fixed schedule. Possible on synthetic families.
- **Not provable, only measurable.** Learnability of halting and of the broadcast gate; whether the
  workspace objective avoids the local collapse; whether any of it survives scale. These are C-class
  questions and the field answers them empirically. The honest statement is that the theory gives
  necessary conditions and separations, and that no theorem will pick the block. Good work can still
  start from the theorem: T1 and T3 say what the block must add, and the list says what it must not lose.

## 5. The MLP, since the assumption was flagged

The MLP is a key–value memory (Geva et al. 2012.14913). Two facts bear on replacing it. First, at small
scale the lever is memory capacity in the input, not in the MLP: T2's hashed n-gram addresses were worth
−0.79% at 22M for 1% FLOPs, and lookup layers beat dense and MoE from 400M (L³ 2601.21461; Engram
2601.07372). So the first change to the MLP is to let it be a lookup where the key is settled, which is a
capacity change, not a computational one. Second, an MLP whose forward pass is a few steps of descent on
an energy (Energy Transformer; Energy-Based Transformers) turns the MLP into a B1 object, iterating to a
fixed point with a natural halting criterion. If the MLP is to change, that is the change that serves
group B; the energy formulation also gives the workspace loop a principled stopping rule (convergence of
the energy), which TRM lacks.

## 6. Where to test group B honestly

Not on FineWeb loss at 22M. C2 says prose at this scale rewards none of B1–B5, which is the lesson of
every null we have. Group B is tested where conclusions arrive late and must overturn earlier ones:
reachability and path-finding with latent search (the 2505.12514 family), puzzles with refinement
(Sudoku, mazes, ARC, where TRM at 7M parameters is the baseline to beat), lookahead tasks that defeat
teacher forcing (path-star, 2403.06963), and reasoning-dense text with hidden intermediates (iGSM
2407.20311), with length extrapolation as the capability metric. A model with the block should show
input-dependent tick counts, broadcasts that change the answer, and retractions that are correct more
often than not. Those are the three observable signatures of a thought bubbling up, and they can be
measured at a few million parameters on public tasks before any language run.

## Sources

Merrill & Sabharwal 2207.00729, 2310.07923; Hahn 1906.06755; Barbero et al. 2406.04267; Bachmann &
Nagarajan 2403.06963; Vafa et al. 2406.03689; Liu et al. 2210.10749; Merrill, Petty & Sabharwal
2404.08819; Peng et al. 2402.08164; Sanford, Hsu & Telgarsky 2306.02896; Roy et al. 2507.02754; Xu et al.
1810.00826; Elhage et al. 2022 (transformer-circuits.pub/2022/toy_model); Beckmann et al. 2609.21748;
Giannou et al. 2301.13196; Saunshi et al. 2502.17416; Geiping et al. 2502.05171; Ouro 2510.25741; Graves
1603.08983; Dehghani et al. 1807.03819; TRM 2510.04871; HRM 2506.21734; Zhu et al. 2505.12514; Hao et al.
2412.06769; Hu et al. 2410.23506; Cundy & Ermon 2306.05426; Chung, Ahn & Bengio 1609.01704; Koutník et
al. 1402.3511; Goyal et al. 2103.01197; Hoover et al. 2302.07253; Gladstone et al. 2507.02092; Abbe et al.
2302.11055; DeepSeek-R1 2501.12948; Geva et al. 2012.14913; Tseng & De Sa 2601.21461; Cheng et al.
2601.07372; Ye et al. 2407.20311; Smolensky 1990; Plate 1995; Krohn & Rhodes 1965; Barrington 1989.
