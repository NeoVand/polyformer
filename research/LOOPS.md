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

- 21 Oct, stage 1 (L4, `loops_synthetic`, 6 runs, about $1.8). One-layer A5 word tracking, late-position
  accuracy (chance 1.7%): rope 1.6%, grid 1.9%, holo 1.7%, **holo + vtrans 98.5%** (all positions 99.2%).
  **P3's synthetic half holds**: a non-abelian frame carried along the sequence tracks A5 in a single
  attention layer once the values are transported too; abelian frames cannot, and without value
  transport the running product never reaches the output. Two-layer MQAR: rope and holo+forget both
  100% (retrieval intact).
- 21 Oct, stage 2 (H100, `loops_screen`, 13 runs, seed 0, 3,051 updates ≈ 100M tokens). Final
  validation loss (1,024 windows, sampler seed 1234), change against abs:

  | Arm | lr | Loss | vs abs | vs rope |
  |---|---|---|---|---|
  | hybrid GAGAGA holo+forget | .008 | 3.808238 | −2.34% | −1.19% |
  | hybrid GAGAGA rope | .008 | 3.815074 | −2.17% | −1.01% |
  | grid+forget | .008 | 3.826246 | −1.88% | −0.72% |
  | holo+forget | .008 | 3.829548 | −1.80% | −0.63% |
  | rope+forget | .008 | 3.830838 | −1.76% | −0.60% |
  | holo+forget | .012 | 3.841079 | −1.50% | −0.34% |
  | holo+forget+vtrans | .008 | 3.846718 | −1.36% | −0.19% |
  | rope | .008 | 3.853963 | −1.17% | 0 |
  | holo | .008 | 3.854309 | −1.16% | +0.01% |
  | rope | .012 | 3.857376 | −1.08% | +0.09% |
  | grid | .008 | 3.865385 | −0.88% | +0.30% |
  | loop 0,1,2,1,2,3 (rope) | .008 | 3.874952 | −0.63% | +0.54% |
  | abs | .008 | 3.899646 | 0 | +1.18% |

  abs reproduces BEYOND's convolved softmax tuning run (3.897961) to 0.04%. BEYOND's same-protocol
  seed-0 references: Gated DeltaNet 3.855246, DeltaProduct 3.840066, convolved Parallax 3.871201.
  Against the predictions: P1 holds (rope −1.17%). **P2 fails**: content-driven abelian clocks alone
  are 0.30% worse than RoPE. P3's language half holds (holo within ±0.3% of rope; vtrans costs 0.4% on
  text). P4 holds and is the largest single effect: the forget gate is worth 0.60% on top of rope.
  P5 holds at this seed: both hybrids beat every attention arm and both recurrent references, and
  the hybrid with holo+forget beats the hybrid with rope (by 0.18%, which this screen cannot separate
  from the forget gate). P6 holds: the depth loop is 0.54% worse than six distinct blocks at equal
  compute, with two thirds of the block parameters (the four-block comparison is in screen 2).
  .012 is worse than .008 for both arms tested, so .008 stays.

  Reading: the gains come from the **reset atom** (the forget gate, synaptic decay) and from the
  **complementary memory** (a fast-weight recurrent layer beside attention). Learned frames, abelian
  or not, are neutral on text at this scale even though they are what makes state tracking possible.

- Screen 2 (registered now, before running; seed 0, 100M tokens, lr .008): which hybrid goes to the
  3-seed stage. Arms: GAGAGA with rope+forget, with grid+forget, with holo+forget+vtrans; AGAGAG
  and GGAGGA with holo+forget; DADADA (DeltaProduct layers) with holo+forget; and a 4-block rope
  model for P6. Selection rule: the lowest seed-0 loss among hybrids whose modeled training FLOPs are
  within 5% of abs goes to stage 3 as the candidate; GAGAGA holo+forget is the default if nothing
  beats it by more than 0.1%.
- Stage 3 registration (written before screen 2's results). Seeds 1, 2, 3; every arm gets the
  modeled training FLOPs of abs at 13,531 updates (about 443M tokens): abs 13,531, rope 13,527,
  rope+forget 13,518, hybrid GAGAGA rope 13,131, GDN 12,756, DeltaProduct 10,095, the candidate per
  `loops_jobs.equal_flop_steps`. Final metric: `val_big` (1,024 fresh windows, seed 5678), as BEYOND.
  Arms: abs, rope (the registered softmax controls), rope+forget (the Forgetting Transformer, the
  strongest attention control, reported against the candidate even though it is not in the
  registered gate), hybrid GAGAGA rope (the plain hybrid), the screen-2 candidate, GDN; DeltaProduct
  if the budget allows after the core arms.
  Predictions: S3-1 the candidate is at least 1% below the better of abs and rope on all three seeds
  (I put this at even odds; the screen margin over rope was 1.19% at 100M tokens). S3-2 it is below
  GDN on all three seeds (likely). S3-3 it is less than 1% below rope+forget on every seed (likely:
  the screen margin was 0.59%). S3-4 it is below DeltaProduct on at least two seeds (60%). S3-5 rope
  stays ahead of abs at 443M tokens, by less than at 100M.
- Screen 2 results (seed 0, 100M tokens): DADADA holo+forget 3.798680 (but about 17% more modeled
  FLOPs than abs, so outside the rule), GAGAGA grid+forget 3.805733, GGAGGA holo+forget 3.808107,
  GAGAGA rope+forget 3.808816, AGAGAG holo+forget 3.813344, GAGAGA holo+forget+vtrans 3.814397,
  rope with 4 blocks 3.909783. No eligible hybrid beats GAGAGA holo+forget (3.808238) by 0.1%, so
  **the registered default is the stage-3 candidate**. The frame type inside the hybrid is worth at
  most 0.08% here; the forget gate and the recurrent layers carry the gain. P6 completed: the depth
  loop (3.874952) beats the 4-block model with the same distinct blocks by 0.89%.
- Budget: $14.48 spent (conservative) after stages 1, 2 and screen 2. Caps moved to development $5,
  screen $20, language $75 (total unchanged at $100) so stage 3 plus DeltaProduct fit.
  Stage 3 core: abs, rope, rope+forget, hybrid GAGAGA rope, hybrid GAGAGA holo+forget, GDN; seeds
  1/2/3, seed-major order. Then DeltaProduct and DADADA holo+forget (both at equal FLOPs) if the core
  leaves at least $30.
- Stage 3, first results (val_big, 1,024 windows, seed 5678; about 443M tokens at equal modeled FLOPs):

  | Arm | Seed 1 | Seed 2 |
  |---|---|---|
  | hybrid GAGAGA holo+forget (candidate) | 3.549097 | pending |
  | hybrid GAGAGA rope | 3.550674 | 3.551037 |
  | rope+forget | 3.573876 | 3.568775 |
  | rope | 3.583959 | 3.576787 |
  | abs | 3.612944 | 3.606994 |

  abs reproduces BEYOND's convolved softmax (3.612649, 3.609362) to 0.07%. **Seed 1 misses the
  registered gate by a hair**: the candidate is 0.973% below rope; 1% needed 3.548119. It is 0.69%
  below rope+forget and 0.44% below BEYOND's seed-1 DeltaProduct (3.564820). The margin over rope
  shrank from 1.19% at 100M tokens. Inside the hybrid the forget gate is worth 0.04% at this length.
  Per what I told Neo, the extra $100 is conditional on a ≥1% win on every seed, so spending stays
  under $100.
- Forget-gate probe (rope+forget, seed 1, 48 held-out windows): the gates learned a hierarchy of
  timescales, half-lives of 1–110 tokens in layers 1–4 and 58–13,000 in layers 5–6, and every layer
  forgets most at event boundaries ('.', '?', newline, sentence-initial 'The'). This is the cortical
  hierarchy of temporal receptive windows (Hasson et al. 2008; Lerner et al. 2011) and boundary-
  triggered event segmentation (Baldassano et al. 2017), found from next-token loss alone.
- Registered before running (within the $100): **scale check**, width 768, 8 layers, 12 heads, MLP
  3072 (about 2.1x the FLOPs per token), seed 1, equal modeled FLOPs to abs at 13,531 updates:
  rope, rope+forget, hybrid GAGAGAGA holo+forget. Prediction S4-1: the hybrid's margin over rope at
  the larger size is within 0.4 points of its base-size margin (no clear growth). **DeltaProduct**,
  seeds 1–3, equal FLOPs (10,095 updates): S3-4 as registered.

