# LOOPS: position is a loop, and the group decides what it remembers

Started 21 October 2026, overnight, after reading [REVIEW.md](REVIEW.md). Budget: **$100 of Modal**,
all stages included. This file holds the synthesis, the registered predictions and gates, and the log.
Predictions are written and committed before the runs they predict.

## 1. Where the review leaves us

The review's thesis is right and the project's own data support it: the higher order that pays is in
the **state** (products carried along the sequence) and in **iteration**, not in the score. Its
sharpest pointers:

- Krohn–Rhodes: every finite automaton is a cascade of **resets** (write, erase, keep: gates, the
  delta rule, softmax selection) and **groups** (permutations, rotations). Our commuting layers are
  the abelian special case; our exact order-blind ceilings measure what that case gives up.
- The brain motivation points to recurrence, multiplicative units and fast synaptic state, not to
  scoring k tokens at once.
- At our scale the only language wins were recurrent (Gated DeltaNet −1.0%, DeltaProduct −1.3% vs
  convolved softmax, one seed), plus the short convolution (1.1–1.3%).

What the review does not say, and what this study is about, is where the loop and the symmetry meet
**inside attention itself**.

## 2. The synthesis: three loops, one group

A sequence model runs three loops.

1. **The sequence loop.** A state is carried from token to token. Whatever the state is, reading a
   stretch of text applies one transition per token, and the stretch acts on the state by the
   product of its transitions. In geometry that product is the **holonomy** of the path: what you
   get when you carry a frame along it.
2. **The memory loop.** Something is written at token j and read back at token i. Softmax attention
   is this loop in its purest form (a modern Hopfield memory); fast weights and the delta rule are
   its compressed form.
3. **The depth loop.** The same block is applied again to its own output (looped and universal
   transformers, tiny recursive models, cortical recurrence).

The symmetry is the window into the first loop, because **the group the transitions live in decides
what the loop can remember**. If the transitions commute (clock hands, phases, RoPE, Newton
attention, grid-cell phases), the state after a stretch depends only on how many of each move it
contains, never on their order: that is our Theorem 1 and the 77.23% ceiling on A5. If they do not
commute (rotations in 3 or more dimensions, Householder products), the state records order. Add
resets and you can build any finite-state machine.

Now the observation that joins the first two loops. **Attention already reads its memory through a
sequence loop: the position encoding.** With RoPE, the key k_j is compared with the query q_i after
being rotated by R^(i−j), the product of i−j identical small rotations. That is parallel transport
of k_j along the path from j to i, and its holonomy is abelian and blind to content: every token
moves the frame by the same amount. RoPE is the trivial loop.

This is exactly the brain's arrangement, and neuroscience has a name for it. In the hippocampal
formation, memories are stored and recalled against a code produced by **path integration**: grid
cells and head-direction cells integrate self-motion into phases, at several spatial scales
(modules). Whittington et al. showed that a transformer whose position code is computed by such a
path integrator (actions applied as matrices, g_{t+1} = W_{a_t} g_t) is the Tolman–Eichenbaum
Machine, and learns place and grid cells. Two features of the biological version are missing from
RoPE:

- **The clock is driven by content.** Grid phases advance when the animal moves, not when time
  passes; in abstract tasks they advance when the latent state changes. A text model's analogue:
  the frame should advance by a learned, token-dependent amount (a word boundary, a new clause, a
  new entity), and different modules can count different things.
- **The moves need not commute.** Orientation in three dimensions (head direction is not only a
  ring), object rotation and sequences of actions compose non-commutatively. A frame transported by
  content-dependent rotations remembers the order of what happened between key and query.

So the candidate "magical combination" is not a new score or a bigger state. It is **attention
that reads memory in a frame carried along the sequence by content-dependent group elements**: the
memory loop indexed by the sequence loop, with the group chosen on purpose. Abelian modules give a
learned, multi-scale clock (grid cells); non-abelian blocks give order-sensitive frames (holonomy);
a forget gate supplies the reset atom (synaptic decay). In Krohn–Rhodes terms the layer contains
both atoms; in TEM terms it is hippocampal retrieval keyed by a cognitive-map code; in our own
terms it is holonomy attention moved from the values into the frame, where it costs almost nothing.

Why it is cheap: for orthogonal transitions the transport from j to i factorises,
U_i ⋯ U_{j+1} = P_i P_jᵀ with P_t = U_t ⋯ U_1, so the score is (P_iᵀ q_i) · (P_jᵀ k_j). Each token
rotates its own query and key once by its own prefix product, exactly as RoPE rotates by its
position. With small blocks (4×4) the extra work is O(n · d · 4) per layer, well under 1% of the
layer. PaTH attention (Yang et al. 2025) uses Householder transitions that are not orthogonal and
needs a special kernel; this construction keeps the transitions orthogonal and needs none.

**Prior art, stated up front.** RoPE (Su et al.); contextual position CoPE (Golovneva et al. 2024);
PaTH (data-dependent Householder transport, 2025); LieRE and ComRoPE (higher-dimensional and
commuting rotation encodings for given coordinates); the Forgetting Transformer (FoX, Lin et al.
2025); hybrids of attention and Gated DeltaNet (Yang et al. 2025, and many others); TEM and
TEM-t (Whittington et al. 2020, 2022). The combination (content-driven abelian modules plus
orthogonal non-abelian blocks in the frame, with a forget gate, alone and in a hybrid) and its
measurement under this project's protocol are what is tested here. No claim to be first.

The third loop, depth, is the review's other recommendation. At **equal compute** a looped model
can only trade parameters for iterations, so it should not beat an untied model of the same depth;
its case is parameter efficiency and reasoning tasks. One equal-compute arm measures where it
stands, so that the answer is on record.

The fourth piece is the complementary-learning-systems reading of hybrids: a neocortex-like fast
weight memory (Gated DeltaNet: compressed, state-tracking, error-correcting) beside a
hippocampus-like exact episodic memory (attention). If the frame idea is right, the hybrid's
attention layers should also benefit from it.

## 3. The layers (all in `research/loops_layers.py`, arch `loop` in `lm.py`)

Shared backbone: the BEYOND language protocol unchanged (6 layers, width 512, 8 heads of 64, MLP
2048 GELU, pre-LayerNorm, Muon at .008, context 512, batch 64, bf16, FineWeb-Edu GPT-2 tokens),
with the short causal QKV convolution (width 3) in every attention arm. With any rotary frame the
learned absolute positions are switched off.

- **abs**: learned absolute positions (the BEYOND "convolved softmax" control).
- **rope**: RoPE on all 64 dims of each head, base 10,000.
- **grid** (abelian, content-driven): the 32 RoPE frequencies of a head are split into M = 4
  contiguous modules. Module m of head h has a velocity u_t = softplus(w·x_t + c)/log 2, which is
  exactly 1 at initialisation (w = 0), and a position τ_t = Σ_{s≤t} u_s. Phases are ω_f τ_t. At
  initialisation the layer is RoPE.
- **holo** (non-abelian): the last 16 dims of each head form four 4-dimensional blocks. Block b at
  token t moves by U_t = R_b · Cayley(S_t), where R_b is the fixed RoPE step for those dims and
  S_t is a 4×4 skew-symmetric matrix linear in x_t (6 numbers per block, small random init).
  P_t = U_t ⋯ U_1 by an associative scan; q and k are rotated by P_tᵀ. The other 48 dims use the
  grid modules. At S = 0 the layer is RoPE.
- **+forget**: FoX's gate, logits_ij += Σ_{j<s≤i} log f_s with f = sigmoid(w·x + 5) per head
  (starts close to 1).
- **+vtrans**: values are transported too on the holonomy dims: v_j → P_jᵀ v_j before averaging,
  output rotated back by P_i. This lets the output carry the running product itself.
- **hybrid**: layers alternate Gated DeltaNet (the BEYOND implementation, one update, chunk 32) and
  attention, GDN first: G A G A G A.
- **loop**: depth loop at equal compute: four distinct blocks applied in the order 0,1,2,1,2,3
  (prelude, a two-block core run twice with the prelude output re-injected through a learned
  gate, coda), with rope.

## 4. Predictions (registered before any run)

Numbers are final validation loss in nats/token; "gain" is relative to convolved softmax with
learned positions (abs) at the same seed and budget.

- P1. rope beats abs by 0.3–1.5% at 100M tokens.
- P2. grid beats rope by 0.1–0.6%.
- P3. holo (on top of grid) changes language by less than ±0.3% vs grid, but solves A5 word
  tracking in one layer with vtrans where rope fails (synthetic check). Not S5: S5 has no faithful
  representation in SO(4) (both 4-dimensional irreps send odd permutations to determinant −1), so a
  4-d block can track only S5's parity; A5 sits inside SO(3) ⊂ SO(4).
- P4. +forget adds 0.1–0.5%.
- P5. The hybrid beats both pure attention and pure Gated DeltaNet; hybrid with the best frame
  beats hybrid with rope.
- P6. loop (4 distinct blocks, 6 applications) is 0.3–1.5% worse than the 6-block rope model at
  equal compute, and better than a 4-block rope model.

**Headline gate (for the 400M-token, 3-seed stage):** a candidate "beats softmax" if its loss is at
least 1% below the better of the two convolved softmax controls (abs, rope) on each of three seeds,
at modeled training FLOPs no greater than the control's. It "beats both" if it is also below Gated
DeltaNet (one update) on every seed. DeltaProduct is reported as an extra reference.

## 5. Stages and budget

| Stage | What | Est. cost |
|---|---|---|
| 0 | CPU unit tests: RoPE equivalence at init, causality, factorised transport equals the literal product, gradients finite | $0 |
| 1 | Synthetic check on L4: A5 word tracking (one layer) for rope / grid / holo / holo+vtrans; MQAR (two layers) for rope / holo+forget | ≤ $4 |
| 2 | Language screen, seed 0, 100M tokens (3,051 updates), lr .008: abs (exactly BEYOND's convolved softmax, a reproducibility check against its 3.897961), rope, grid, grid+forget, holo, holo+forget, holo+forget+vtrans, rope+forget, hybrid GAGAGA with rope and with holo+forget, loop; rope and holo+forget also at .012 | ≤ $15 |
| 3 | Language, 400M tokens, seeds 1/2/3: abs, rope, best two candidates, best hybrid; GDN seeds 2/3 | ≤ $60 |
| 4 | If budget remains: one larger width for the winner vs its control (the scaling question) | rest |

Learning rate: .008 for every arm (BEYOND's selected rate for all six of its arms). A rate check at
.012 for the best candidate and its control is run in stage 2 if a candidate looks ahead.

## 6. Log

- 21 Oct, stage 0: `loops_layers.py`, the `loop` arch in `lm.py` (pattern, depth loop, FLOPs),
  `loops_modal.py` (own ledger, caps development $10 / screen $25 / language $65, total $100).
  `test_loops.py`: 14 CPU tests pass (grid equals RoPE at init; holo at identity is translation
  invariant; the factorised score equals the literal ordered product of moves; frames orthogonal;
  holo frames change when two tokens swap while grid phases do not; causality; one training step
  finite for every option, hybrids G/D and the depth loop; frame+gate+vtrans FLOPs under 2%).
  Existing BEYOND/LOCAL tests still pass. CPU smoke runs of `lm.py` succeed for every variant.
