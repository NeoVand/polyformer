# LOOPS: results report for review

21 October 2026. A follow-up to [REVIEW.md](REVIEW.md), run overnight. This report is self-contained:
it states what was tested, every result, the predictions made before each stage and how they fared,
and the caveats a reviewer should weigh. The plan, the registrations and the running log are in
`research/LOOPS.md` on branch `claude/loops` (worktree `/Users/neo/repos/polyformer/.claude/worktrees/loops`).
Code: `research/loops_layers.py`, the `loop` architecture in `research/lm.py`, jobs in
`research/loops_jobs.py`, launcher `research/loops_modal.py`, probe `research/loops_probe.py`,
gate `research/loops_gate.py`. Raw per-run JSON: `research/results/loops_runs/`.

**Budget:** $100 Modal cap; $75.41 spent across 50 runs, none failed (conservative resource estimate,
not an invoice).

## 1. Summary

1. **On language, a two-memory model is the best of nine arms on every seed, but misses the registered
   bar.** Gated DeltaNet layers alternating with attention layers that carry a content-driven rotary
   frame and a forget gate reach 3.5479 nats/token (mean of three seeds, about 430M tokens, equal
   modeled training FLOPs). That is 0.89% below RoPE softmax (−0.97, −0.82, −0.88), 0.65% below the
   Forgetting Transformer, 0.82% below Gated DeltaNet, 0.59% below DeltaProduct and 1.82% below
   softmax with learned positions. The registered headline asked for at least 1% below the better
   softmax control on all three seeds. **It fails on all three, by 0.03 to 0.18 points.**
2. **Almost all of the gain is from known parts.** Alternating Gated DeltaNet with RoPE attention is
   worth 0.80% over RoPE softmax; the forget gate is worth 0.25% on its own; the new frames and the
   gate add 0.10% inside the hybrid. Hybrids and the forget gate are published.
3. **The new part, content-driven non-commuting frames, buys state tracking and nothing on text.**
   With values transported as well, one attention layer tracks A5 at 98.5% on late positions, where
   RoPE, abelian clocks and frames without value transport stay at chance (1.7%). On text the frames
   change the loss by less than 0.1%, and value transport costs 0.4%.
4. **The trained models rediscovered event segmentation and a timescale hierarchy.** Forget gates
   reset at sentence and line boundaries and their half-lives grow from 1–100 tokens in early layers
   to thousands in late ones; content-driven clocks tick on sentence ends, clause words and verbs and
   stop on sub-word fragments.
5. **A finding about the earlier study.** Under this protocol, Gated DeltaNet is only 0.07% better
   than RoPE softmax and DeltaProduct 0.30%. BEYOND's "recurrent networks beat softmax by about 1%"
   was mostly the softmax baseline's learned absolute positions.
6. **The margin does not grow with size** in one seed of a model with three times the non-embedding
   parameters (0.86% below RoPE, against 0.97% at the base size, same seed).

## 2. What was tested and why

The review argued that the higher order that pays lives in the state and in iteration, and that the
brain motivation points to recurrence, resets and fast synaptic state. This study added one
observation and tested it: **attention already reads its memory through a loop, the position
encoding.** With RoPE, key j is compared with query i after being rotated by R^(i−j), the product of
i−j identical rotations: parallel transport along the path from j to i, with an abelian holonomy that
ignores content. The group the per-token moves live in decides what such a loop can remember:
commuting moves remember counts (the project's order-blind ceiling); non-commuting moves remember
order. The hippocampal formation does exactly this kind of thing, keying memory by path-integrated
codes (grid and head-direction cells; Whittington et al.'s TEM and its transformer form), and its
path integrator is driven by movement, not by a clock.

For orthogonal moves the transport factorises: U_i ⋯ U_{j+1} = P_i P_jᵀ with P_t the running product,
so the score is (P_iᵀ q_i)·(P_jᵀ k_j). Each token rotates its own query and key once, exactly as RoPE
does, with no per-pair work and no special kernel (PaTH uses non-orthogonal Householder moves and
needs one). Extra cost: under 2% of the layer's modeled FLOPs.

**Arms** (all attention arms share the short causal QKV convolution of width 3):

| Arm | Definition |
|---|---|
| abs | learned absolute positions (BEYOND's convolved softmax) |
| rope | RoPE on all 64 head dims, base 10,000 |
| grid | abelian, content-driven: RoPE frequencies split into 4 modules per head; module m advances by a learned velocity softplus(w·x_t + c)/log 2, exactly 1 at init (starts as RoPE) |
| holo | grid on 48 dims, plus four 4-d blocks per head moving by R_b·L(p_t)·R(q_t): the fixed RoPE step times left and right multiplication by unit quaternions computed from x_t (identity at init); running products by associative scan |
| +forget | the Forgetting Transformer's gate, logits_ij += Σ_{j<s≤i} log σ(w·x_s + 5) per head |
| +vtrans | values transported on the holonomy dims too (v_j → P_jᵀ v_j, output → P_i·out) |
| hybrid PATTERN | per-layer letters: A attention arm, G Gated DeltaNet (one update), D DeltaProduct (four updates); BEYOND's recurrent implementation, chunk 32 |
| loop | depth loop: four distinct blocks applied 0,1,2,1,2,3 with a learned re-injection of the first block's output |
| gdn, deltaproduct | BEYOND's recurrent controls, unchanged (learned positions, own short convolutions) |

**Protocol:** BEYOND's language protocol unchanged. FineWeb-Edu with GPT-2 tokens; 6 layers of width
512 with 8 heads and a 2048 GELU MLP; context 512; batch 64; bf16; Muon at learning rate .008 for
every arm (BEYOND's selected rate for all six of its arms; .012 was worse for both arms where it was
checked). Screens: seed 0, 3,051 updates (about 100M tokens), metric `val` (1,024 windows, sampler
seed 1234). Confirmation: seeds 1–3, metric `val_big` (1,024 fresh windows, seed 5678), each arm
given the modeled training FLOPs of abs at 13,531 updates (lm.py's convention).

## 3. Results

### 3.1 Synthetic check (L4, one seed)

A5 word problems (16 elements, the running product at every position), one layer, width 128, 4 heads,
6,000 updates. Accuracy on the second half of the positions, chance 1.7%:

| Arm | Late accuracy | All positions |
|---|---|---|
| rope | 1.6% | 22.7% |
| grid | 1.9% | 23.0% |
| holo | 1.7% | 20.8% |
| **holo + vtrans** | **98.5%** | 99.2% |

Two-layer MQAR (16 pairs, context 128): rope 100%, holo+forget 100%.

S5 was not used, deliberately: S5 has no faithful representation in SO(4) (both 4-d irreps send odd
permutations to determinant −1), so a 4-d block can only track parity there. This was registered
before the run.

### 3.2 Language screen 1 (seed 0, about 100M tokens)

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
| loop (4 blocks, 6 applications) | .008 | 3.874952 | −0.63% | +0.54% |
| abs | .008 | 3.899646 | 0 | +1.18% |

abs reproduces BEYOND's convolved-softmax tuning run (3.897961) to 0.04%. BEYOND's same-protocol
seed-0 recurrent references: Gated DeltaNet 3.855246, DeltaProduct 3.840066.

### 3.3 Language screen 2 (seed 0, about 100M tokens): which hybrid

| Hybrid | Loss | Modeled FLOPs vs abs |
|---|---|---|
| DADADA holo+forget | 3.798680 | +17.9% (excluded by the registered 5% rule) |
| GAGAGA grid+forget | 3.805733 | +3.2% |
| GGAGGA holo+forget | 3.808107 | +4.7% |
| GAGAGA holo+forget (screen 1) | 3.808238 | +3.9% |
| GAGAGA rope+forget | 3.808816 | |
| AGAGAG holo+forget | 3.813344 | |
| GAGAGA holo+forget+vtrans | 3.814397 | |
| rope with 4 blocks (for the loop arm) | 3.909783 | |

Registered rule: the default (GAGAGA holo+forget) stays unless an eligible hybrid beats it by more
than 0.1%. None did, so it went to confirmation. The frame type inside the hybrid is worth at most
0.08% here.

### 3.4 Confirmation (seeds 1–3, equal modeled training FLOPs, `val_big`)

| Arm | Updates | Tokens | Non-embedding params | Seed 1 | Seed 2 | Seed 3 | Mean | SD |
|---|---|---|---|---|---|---|---|---|
| **hybrid GAGAGA holo+forget** | 13,017 | 427M | 20.9M | 3.549097 | 3.547497 | 3.547073 | **3.547889** | 0.0011 |
| hybrid GAGAGA rope | 13,131 | 430M | 20.5M | 3.550674 | 3.551037 | 3.552143 | 3.551284 | 0.0008 |
| deltaproduct | 10,095 | 331M | 32.9M | 3.570849 | 3.566316 | 3.569971 | 3.569045 | 0.0024 |
| rope+forget | 13,518 | 443M | 19.0M | 3.573876 | 3.568775 | 3.570093 | 3.570914 | 0.0026 |
| gdn | 12,756 | 418M | 22.1M | 3.579267 | 3.574195 | 3.578025 | 3.577162 | 0.0026 |
| rope | 13,527 | 443M | 18.9M | 3.583959 | 3.576787 | 3.578579 | 3.579775 | 0.0037 |
| abs | 13,531 | 443M | 18.9M | 3.612944 | 3.606994 | 3.621186 | 3.613708 | 0.0071 |

abs reproduces BEYOND's seed-1 and seed-2 convolved softmax (3.612649, 3.609362) to 0.07%.

Per-seed differences (negative = the first arm is better):

| Comparison | Seed 1 | Seed 2 | Seed 3 | Mean |
|---|---|---|---|---|
| candidate vs rope | −0.973% | −0.819% | −0.880% | −0.891% |
| candidate vs rope+forget | −0.693% | −0.596% | −0.645% | −0.645% |
| candidate vs gdn | −0.843% | −0.747% | −0.865% | −0.818% |
| candidate vs deltaproduct | −0.609% | −0.528% | −0.641% | −0.593% |
| candidate vs hybrid GAGAGA rope | −0.044% | −0.100% | −0.143% | −0.096% |
| candidate vs abs | −1.767% | −1.649% | −2.047% | −1.821% |
| hybrid GAGAGA rope vs rope | −0.929% | −0.720% | −0.739% | −0.796% |
| rope+forget vs rope | −0.281% | −0.224% | −0.237% | −0.248% |
| rope vs abs | −0.802% | −0.837% | −1.177% | −0.939% |
| gdn vs rope | −0.131% | −0.072% | −0.015% | −0.073% |
| deltaproduct vs rope | −0.366% | −0.293% | −0.241% | −0.300% |

### 3.5 Scale check (seed 1, width 768, 8 layers, 12 heads, MLP 3072)

About 57M non-embedding parameters (three times the base), 2.1 times the FLOPs per token, equal
modeled FLOPs to abs at 13,531 updates at that size.

| Arm | Loss | vs rope |
|---|---|---|
| hybrid GAGAGAGA holo+forget | 3.416956 | −0.86% (base, seed 1: −0.97%) |
| rope+forget | 3.433903 | −0.37% (base: −0.28%) |
| rope | 3.446651 | 0 |

### 3.6 Probes of trained checkpoints (seed 1, 48 held-out windows)

Files: `research/results/loops_probe_rope_forget_s1.json`, `research/results/loops_probe_hybrid_holo_forget_s1.json`.

- **Forget gates (rope+forget).** Mean half-life per head, by layer: layer 1: 9–109 tokens; layer 2:
  1–57; layer 3: 2–74; layer 4: 2–66; layer 5: 4–1,010; layer 6: 70–13,253. Every layer forgets
  most at '.', '?', newline and sentence-initial 'The'. The hybrid's attention layers show the same
  pattern, with half-lives up to about 40,000 tokens in the last one.
- **Content clocks (hybrid).** Modules that stay on tick fastest on sentence ends, on clause words
  ('who', 'which', 'that', 'when', 'with') or on verbs ('was', 'is', 'has', 'will'), and nearly stop
  on sub-word continuations and commas; many modules switched their clock off (velocity near 0).
- **Holonomy blocks (hybrid).** Most blocks moved far from the RoPE step (mean Frobenius distance of a
  move from R_b about 2.6, where 4 is the maximum between two 4×4 rotations) and consecutive moves
  fail to commute (commutator norm about 2.6); a few stayed at RoPE. The model uses non-commuting
  frames, and they do not change the loss.

## 4. Predictions and how they fared

All written and committed before the runs they predict (git history on `claude/loops`).

| Prediction | Outcome |
|---|---|
| P1 rope beats abs by 0.3–1.5% at 100M | held (1.17%) |
| P2 grid beats rope by 0.1–0.6% | **failed** (grid 0.30% worse) |
| P3 holo within ±0.3% of grid on text; holo+vtrans tracks A5 in one layer where rope fails | held |
| P4 forget gate adds 0.1–0.5% | **missed** at 100M (0.60%, above the range); within it at 443M (0.25%) |
| P5 hybrid beats pure attention and pure GDN; with the best frame beats with rope | held, the second part by 0.04–0.14% |
| P6 loop 0.3–1.5% worse than 6 distinct blocks, better than 4 | held (−0.54%, +0.89%) |
| S3-1 candidate ≥1% below the better softmax control on all seeds (even odds) | **failed** (0.82–0.97%) |
| S3-2 candidate below GDN on all seeds | held |
| S3-3 candidate less than 1% below rope+forget | held |
| S3-4 candidate below DeltaProduct on at least two seeds | held on all three |
| S3-5 rope stays ahead of abs, by less than at 100M | held (0.94% vs 1.17%) |
| S4-1 the hybrid's margin over rope at the larger size within 0.4 points of base | held (0.86 vs 0.97) |

## 5. Caveats a reviewer should weigh

1. **Equal modeled FLOPs is not equal wall time.** Measured H100 wall clock for the confirmation runs:
   rope 1,180 s, rope+forget 1,200 s, hybrid with rope 1,623 s, candidate 1,817 s, GDN 2,034 s,
   DeltaProduct 3,725 s. The JAX recurrent kernels and the frame scans are unoptimised. At equal
   wall time the candidate would have about two thirds of RoPE softmax's updates.
2. **Parameters are not matched.** The candidate has 20.9M non-embedding parameters against 18.9M for
   softmax (+10%); DeltaProduct 32.9M with fewer tokens.
3. **One learning rate.** .008 for every arm, at the top of BEYOND's grid; only two arms were checked at
   .012. A tuned softmax could close part of the gap; so could a tuned hybrid widen it.
4. **Selection on seed 0.** The candidate and the hybrid layout were chosen on seed-0, 100M-token
   screens; confirmation used fresh seeds and four times the tokens, as registered.
5. **The recurrent controls keep BEYOND's recipe** (learned absolute positions, their own
   convolutions), so they are not tuned to their best either.
6. **One scale, one dataset, one context length** for the 3-seed result; the scale check is one seed.
   Context 512 is short for anything that needs a forget gate or a recurrent state to shine.
7. **Novelty is narrow.** The language gain comes from published parts (attention–DeltaNet hybrids,
   the Forgetting Transformer, RoPE). What is new is the orthogonal, content-driven frame (cheap
   holonomy transport with no special kernel), its one-layer A5 result, the probes, and the measured
   decomposition under one protocol. PaTH, CoPE, LieRE/ComRoPE and TEM are the nearest prior art.
8. **Evaluation windows** come from one held-out file; per-sequence losses are saved for paired
   tests, but no significance test was registered. Seed spread (SD 0.001–0.007) is small next to the
   gaps that are claimed.

## 6. Proposed next steps (not funded yet)

- **Build the discovered structure in.** One shared, learned event clock that drives the forget gate
  in every attention layer and the decay of every recurrent layer; forget and decay rates initialised
  as a timescale hierarchy matching the learned half-lives. Hypothesis: faster learning and a
  larger margin, because each layer no longer has to discover boundaries on its own.
- **Measure the exponent.** The hybrid against rope+forget at three sizes, with a token-limited arm,
  so the question "does the margin grow" has an answer with a slope and a noise floor.
- **Put the frames where they matter.** State-tracking probes inside trained language models (entity
  and ownership tracking, swap programs), with value transport in one head only to avoid its 0.4%
  cost on text.
- **Fix the wall-clock gap** before claiming a practical win: a fused kernel for the chunked delta
  rule and the frame scan.

## 7. Questions for the reviewer

1. Is equal modeled FLOPs the right comparison here, or should the next study match wall time or
   parameters as well?
2. Given that the gain decomposes into published parts, is the event-clock/timescale direction the
   most valuable next step, or should the money go to scale (the exponent) first?
3. The non-commuting frames are used by the model (large commutators) yet do not move the loss. Is
   there a language-side probe or task family you would trust to show whether they matter at all?
4. Should the 1% gate stay, or be replaced by a paired test on per-sequence losses with a registered
   effect size?
