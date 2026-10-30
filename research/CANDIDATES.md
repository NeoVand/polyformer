# Candidate contextualization blocks: theory, guarantees, cheap validation

22 October 2026. Follows [BLOCK_THEORY.md](BLOCK_THEORY.md), whose property list (A1–A5 capacity, B1–B5
computation, C1–C4 training) is the specification. Four candidates, one of them a control. For each:
definition, properties, what can be proved today (with sketches), what would falsify it, and a validation
that runs on a laptop CPU in under an hour. Nothing here spends money; the decision rule for the first paid
run is in section 6.

## 1. The candidates at a glance

| | Candidate | What it adds | Theory it leans on |
|---|---|---|---|
| K1 | Event-clocked looped workspace | B1 B2 B3 B4(latent) B5, A3 A4 in the slow stream | TC0 bound; looped simulation; superposed search; Banach halting |
| K2 | Energy-descent block (MLP or whole block as descent on an energy) | B1 with certified halting, multiplicity of hypotheses, per-token variable compute | dense associative memory; convergence of descent; basin geometry |
| K3 | Draft, verify, retract with a looped verifier | B4 at the output, B5 at the system level | speculative-decoding exactness; imitation of own errors |
| K0 | Synchronous looped transformer with fixed budget (control) | B1 only | Huginn, Ouro, TRM |

K1 is the conjunction the property list forces. K2 is the principled replacement for the MLP and the
source of a halting theorem K1 lacks. K3 is the cheapest way to get "no, wait" at the output and is
compatible with K1 as its verifier. K0 is the control that tells us whether asynchrony matters at all.

## 2. K1: event-clocked looped workspace

**Definition.** Fast stream: the token residual stream with attention and MLP, unchanged. Slow stream: m
slots w ∈ R^{m×d} with their own residual, initialised once per sequence. A router (the EVENTS router,
p_t = (1 − cos(W_q h_t, W_k h_{t−1}))/2) marks event boundaries. At each boundary the workspace *ticks*:
w ← T_c^k(w), where T_c is one shared block (slot self-attention, cross-attention from slots to the fast
stream's tokens of the event just closed, MLP) applied k ≤ K times, with a loss at every iteration (deep
supervision). After the tick, a gate g = 1 if ‖w_k − w_{k−1}‖ ≤ ε or if a learned confidence head exceeds a
threshold; if g = 1 the workspace *broadcasts*: a projection of w is added to the fast stream at the
current position and, in latent form, to the stored keys and values of the closed event's tokens. The
workspace carries its own objective: predict a bag-of-tokens summary of the *next* event (a
suffix-conditioned loss, B3), plus a ponder cost on k. Compute per token: the tick costs k(m² + m·n_e)d
amortised over the event's n_e tokens; with m = 16, k = 8, n_e = 20 that is about 10% of the fast
stream's attention FLOPs at d = 512.

**Properties.** B1 (loop with budget and deep supervision), B2 (the state stays a vector until broadcast),
B3 (its own suffix objective), B4 in latent form (broadcast rewrites the event's keys and values), B5
(two clocks, event-driven, conditional broadcast). A3 and A4 in the slow stream: the looped block can
carry orthogonal state across ticks and the m slots attend to each other, so hub-less relations among
slots cost m². A1, C1, C4 untouched in the fast stream.

**Theorem K1.1 (separation on iterated composition).** Let G be a non-solvable finite group (S5) and let
each event determine one generator through a finite lookup of its tokens. A fixed-depth, log-precision
transformer cannot compute the product over e events for all e unless TC0 = NC1 (the word problem of S5
is NC1-complete, Barrington 1989; fixed-depth log-precision transformers are in TC0, Merrill & Sabharwal
2207.00729). K1 with one slot and k = 1 computes it exactly for all e: the slot holds the current group
element as a one-hot in d ≥ |G| coordinates; cross-attention reads the event's generator (a finite
lookup, implementable by one attention head plus the MLP); the MLP implements the transition table
(a finite function of (state, generator), representable exactly by a two-layer ReLU network with
|G|·|S| hidden units). Per-token cost is O(d²/n_e). *Sketch of the lower bound:* the model's output on
the sequence is a TC0 function of the input by Merrill & Sabharwal; a TC0 family computing the S5 word
problem for all lengths would put an NC1-complete problem in TC0. *Remark:* the separation is in the
length axis, which is the one that matters, and it is conditional on a standard conjecture, as every
such separation is.

**Theorem K1.2 (superposed frontier across slots).** Zhu et al. (2505.12514) construct a two-layer
transformer with continuous thoughts that decides directed reachability in D iterations (D the
diameter) by holding the reachable set in superposition, under nearly orthogonal node embeddings; the
construction fails when the frontier exceeds the superposition capacity C(d) of one vector (cross-talk
corrupts the attention that expands the frontier). In K1 with m slots and a fixed hash of node ids to
slots, each slot holds at most ⌈F/m⌉ frontier nodes, each slot expands its own part by cross-attention
to the edge list, and new nodes are routed to their hash slot through slot self-attention. *Claim:* the
same construction decides reachability in D iterations for frontiers up to m·C(d) minus the routing
overhead, which is one extra attention layer per iteration. *Sketch:* apply Zhu's per-vector argument
within each slot; the only new step is routing, which is a permutation-like map between slots computed
by one self-attention layer whose scores are the hash agreement; cross-talk is bounded per slot, so the
bound scales with m. This is the formal content of "many thoughts at once": capacity in the number of
hypotheses grows linearly in slots, not in depth.

**Proposition K1.3 (certified halting under contraction).** Let T_c be the tick map for a fixed context.
If T_c is a contraction on the workspace state with constant λ < 1 (enforceable by spectral
normalisation of the block's linear maps with a 1-Lipschitz nonlinearity, or measured empirically at
convergence), then the iterate converges to a unique fixed point w* with ‖w_k − w*‖ ≤ λ^k ‖w_0 − w*‖,
and the stopping rule "halt when ‖w_k − w_{k−1}‖ ≤ ε" guarantees ‖w_k − w*‖ ≤ ελ/(1 − λ). Proof: Banach.
*Use:* the broadcast gate opens on a certified condition, and the ponder cost has a meaning: it is the
number of steps to an ε-fixed point. *Cost:* contraction forbids multiple fixed points, so a contracting
workspace cannot hold competing hypotheses; that is K2's department (section 3). The honest design is a
contracting tick map *per hypothesis slot* with competition between slots at broadcast.

**Failure modes and falsifiers.** (i) The workspace goes local, as REVISE did: falsified if the suffix
objective's gradient is small relative to the fast stream's and the broadcasts carry no information
about the next event (measured by the suffix loss with the workspace ablated). (ii) The gate never
opens or always opens: measured as the tick-count distribution; degenerate if its entropy is near zero.
(iii) Router collapse, as in EVENTS: use the fixed punctuation boundaries as the first clock, learned
boundaries second. (iv) Loop instability: deep supervision and a bounded K are the known fixes.

**Validation V1, V2, V3 (section 5).**

## 3. K2: energy-descent block

**Definition.** Replace the MLP (first version) or the whole block (second version) by r steps of
gradient descent on a learned energy: h_{i+1} = h_i − η ∇_h E(h_i; c), E(h; c) = −Σ_j F(k_j(c)ᵀh) +
½‖h‖² + Σ_u ψ(a_uᵀh + b_u), where the first term is a dense associative memory over context keys (F =
exp gives modern Hopfield; F = x^n gives Krotov–Hopfield), the last an MLP energy with convex ψ
(softplus). Steps per token are data-dependent: stop when ‖∇E‖ ≤ ε. Training unrolls r steps.

**Properties.** B1 with a built-in stopping rule; per-token variable compute, the weak form of B5 (not a
second clock, but a second time axis per token); multiplicity: a non-convex E has several minima, which
is what competing hypotheses are; B4 in the sense that the minimiser moves as c changes.

**Theorem K2.1 (convergence and certified halting).** If E(·; c) has L-Lipschitz gradient and η < 2/L,
descent is monotone in E and converges to a stationary point; if E is additionally strongly convex in h
(true for the Hopfield term with exp F in the region ‖h‖ bounded, plus the ½‖h‖² term dominating), the
fixed point is unique and convergence is geometric. Proof: standard descent lemma; strong convexity from
the quadratic term when the memory term's Hessian is bounded, which holds for bounded h. *Use:* halting at
‖∇E‖ ≤ ε certifies ‖h − h*‖ ≤ ε/μ with μ the strong-convexity constant.

**Theorem K2.2 (capacity and multiplicity).** For the dense associative memory term alone, the number of
stored patterns that are stable fixed points with basins of a fixed radius grows exponentially in d for
exp F (Ramsauer et al. 2008.02217) and as d^{n−1} for F = x^n (Krotov & Hopfield 1606.01164); one update
converges to the stored pattern up to exponentially small error when patterns are well separated. *Use:*
with the convexifying quadratic term removed, E has many minima, each a hypothesis; the descent from the
current state selects one. Near a basin boundary the gradient is small, so the step count to convergence
is large: **ambiguity is measurable as compute**, and a change of context that moves the state across a
boundary produces a switch of minimum, the "no, wait" of this block. This is a theorem-level signature,
unlike K1's, which is empirical.

**Failure modes.** Cost (r forward passes per token; EBT reports gains below 1B at several times the
compute); training through unrolled descent is second-order and noisy; convexity, if enforced, kills
multiplicity; if not enforced, convergence is only to a stationary point and K2.1's certificate weakens
to "gradient small".

**Validation V4 (section 5).**

## 4. K3: draft, verify, retract

**Definition.** A drafter (the fast stream) emits tokens. A verifier, which can be K1's workspace or a
separate small looped model, scores the committed suffix asynchronously (on its own ticks) and, when its
score of the last r tokens falls below a threshold, emits a retract action that removes them; the
drafter resumes conditioned on the retraction. Training: imitation on self-generated continuations
(SequenceMatch 2306.05426), where the retract action is labelled from the verifier's disagreement with
the reference, plus an outcome reward when one exists.

**Proposition K3.1 (exactness of verify-and-resample).** Speculative decoding's theorem (Leviathan,
Kalman & Matias 2211.17192): accepting a drafted token with probability min(1, q(x)/p(x)) and resampling
rejections from the normalised residual (q − p)^+ yields samples exactly from q. With retraction after
commitment, the same holds for the final output provided every emitted token is eventually verified
before the sequence ends, since the retained prefix is then the accepted prefix of an ordinary
speculative run. *Use:* the output distribution of the system equals the verifier's, so "no, wait" has a
clean semantics: the drafter's errors are corrected at the verifier's acceptance rate, and the expected
number of retracted tokens is the expected number of rejections.

**Properties.** B4 at the output; B5 at the system level; B1 and B2 if the verifier loops. It does not
make the drafter more capable; it makes the system's output as good as the verifier's at the drafter's
latency. That is also its limit.

**Failure modes.** Retractions oscillate (draft, retract, redraft the same tokens): bounded by capping
retractions per position. Verifier no better than drafter: then exactness buys nothing, which V5 checks.

**Validation V5 (section 5).**

## 5. The validation ladder (local CPU, JAX, no Modal, $0)

All runs at d = 64–128, 1–2 layers, minutes to an hour each, three seeds where a number is compared.
Tasks are synthetic and public-domain in design; the harness pieces exist (`research/polybench.py`,
`research/groups.py`, `research/events_model.py`'s router).

- **V1, late evidence (B4, B5; K1 vs K0 vs fixed depth).** Sequences of e events; a query posed in
  event 1 whose answer is fixed by evidence in event j ∈ {2, …, e}, which may *overturn* a tentative
  answer supported by events before j. Measure accuracy as a function of j and e, and for K1 the tick
  count and the fraction of broadcasts occurring at event j. Pass: K1 accuracy flat in j where the fixed
  model's falls; broadcasts concentrate at j (signature 2 of BLOCK_THEORY §6). K0 (synchronous loop,
  same K) is the control that decides whether asynchrony or just depth did the work.
- **V2, iterated composition over events (Theorem K1.1).** S5 word problem with one generator per
  event, train at e ≤ 16, test at e = 64 and 256. Pass: K1 with one slot extrapolates at above 95%;
  the fixed-depth model at the same per-token FLOPs degrades to chance by e = 64. Reuses
  `groups.py`; the lower-bound side is known, so this validates the construction and its learnability
  (C1), which the theorem does not give.
- **V3, superposed frontier (Theorem K1.2).** Directed reachability on random graphs with frontier
  size F controlled by branching; m ∈ {1, 4, 16} slots. Pass: the largest F solved at fixed D grows with m
  (near-linearly up to interference), and single-vector capacity matches the Zhu construction's.
- **V4, basin switch (Theorem K2.2).** An ambiguous-cue task: early context supports hypothesis A,
  a later cue flips to B. For K2 measure the step count to convergence per token and the identity of
  the minimum reached. Pass: step count spikes at the flip token and the minimum switches; a standard
  block's hidden state moves continuously with no spike. This is the cheapest test in the ladder and
  the only one with a theorem predicting its exact shape.
- **V5, retraction value (Proposition K3.1).** A path-generation task on a graph where early choices
  can lead to dead ends only visible later. Drafter alone, drafter with verify-and-retract (verifier
  = a K1 workspace or a small looped model). Pass: system accuracy exceeds the drafter's and approaches
  the verifier's at the drafter's latency; retractions are correct (the retracted span was wrong) more
  than 70% of the time.

Each validation reports: pass or fail against the registered criterion, the signature plots, and the
wall time. Everything runs with `uv run --no-project --with "jax[cpu]" --with optax --with numpy` as
the existing tests do.

## 6. Decision rule for the first paid run

Advance a candidate to a $10 run only when (a) its construction validation passes (V2 for K1, V4 for
K2, V5 for K3) and (b) at least one *signature* validation passes (V1 or V3 for K1; the spike in V4 for
K2; correct retractions in V5 for K3). The first paid run is then on reasoning-dense text with hidden
intermediates (iGSM-style) or on ARC-style refinement puzzles against TRM, never on FineWeb loss at 22M,
for the reason C2 gives. K0 runs alongside in every case as the control for "it was just depth".

My ranking before validation: K1 first, since it is the conjunction; K2 second, since it is the only one
with a theorem predicting the interrupt signature and the natural MLP replacement; K3 third, as the
cheapest route to visible "no, wait" and the verifier role for K1. I would not be surprised if V1 shows
K0 matching K1, in which case asynchrony is a cost story (fewer ticks) rather than a capability story,
and the paper is about halting and latent search, not about clocks.

## Sources

Barrington 1989; Merrill & Sabharwal 2207.00729; Liu et al. 2210.10749; Giannou et al. 2301.13196; Zhu
et al. 2505.12514; Saunshi et al. 2502.17416; TRM 2510.04871; HRM 2506.21734; Ramsauer et al.
2008.02217; Krotov & Hopfield 1606.01164; Hoover et al. 2302.07253; Gladstone et al. 2507.02092;
Leviathan, Kalman & Matias 2211.17192; Cundy & Ermon 2306.05426; Goyal et al. 2103.01197; Graves
1603.08983; Bachmann & Nagarajan 2403.06963; Hu et al. 2410.23506.
