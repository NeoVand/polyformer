# EVENTS: results report for review

21 October 2026. The follow-up to [LOOPS_REVIEW.md](LOOPS_REVIEW.md), run in the review's order. The
registrations, predictions and running log are in [EVENTS.md](EVENTS.md) on branch `claude/loops`
(worktree `/Users/neo/repos/polyformer/.claude/worktrees/loops`). Code: `research/events_model.py`
(the event model), `research/loops_layers.py` (gate, value residual, one-head transport, exact
block-causal attention), `research/lm.py`, jobs `research/loops_jobs.py`, launcher
`research/loops_modal.py`, evaluations `research/loops_eval.py`, `research/events_probe.py`,
`research/events_paired.py`, `research/events_report.py`. Raw per-run JSON:
`research/results/loops_runs/`.

**Budget:** $300 Modal cap for LOOPS and EVENTS together; ⟨SPEND⟩ spent in total, ⟨EVSPEND⟩ of it on
EVENTS (conservative resource estimates, not an invoice).

## 1. Summary

⟨SUMMARY⟩

## 2. What changed from LOOPS

- **The 1% gate is retired.** Claims are signs and minimum sizes of changes in a margin across
  context length and model size, with equal-parameter and wall-clock rows and a paired test across
  held-out windows.
- **Both arms get the published parts.** Gated attention output (Qiu et al. 2025) and the value
  residual (Zhou et al. 2024) go into every attention layer of every arm.
- **Context 512 is no longer the main regime.** The main cells are 2,048 and 8,192 tokens, with an
  exact block-causal attention (the Forgetting Transformer's bias reaches thousands at 8,192, beyond
  bf16 near the softmax maximum, so a stock kernel with a key bias is not exact).
- **The event model** (section 4) is the review's proposal: tokens are grouped into events by a
  learned router (H-Net's dynamic chunking), and the expensive network runs over events.

## 3. Cheap day: the published parts, in both arms (context 512)

### 3.1 Screen (seed 0, 3,051 updates, 100M tokens)

| Arm | rope+forget | hybrid GAGAGA holo+forget |
|---|---|---|
| plain (LOOPS) | 3.8308 | 3.8082 |
| + gated output | 3.8034 (−0.72%) | 3.8036 (−0.12%) |
| + value residual | 3.8073 (−0.61%) | 3.7973 (−0.29%) |
| + both | **3.7844 (−1.21%)** | 3.7926 (−0.41%) |
| + one transport head | | 3.8085 (+0.01%) |
| + both + one transport head | | 3.7881 (−0.53%) |

The gate is a reset atom, and the softmax model, which lacks resets, gains six times as much from it as
the hybrid, which already has them.

### 3.2 Confirmation (seeds 1–3, equal modeled FLOPs, 443M softmax tokens, 1,024 `val_big` windows)

| Arm | val_big | vs control | per seed | paired t | non-emb. params | wall |
|---|---|---|---|---|---|---|
| control: rope+forget+gate+vres | 3.5235 | | | | 20.5M | 1,241 s |
| hybrid holo+forget+gate+vres, one transport head | 3.5278 | +0.12% | +0.04 / +0.11 / +0.22 | +5.6 | 21.7M | 1,837 s |
| control with MLP widened to the hybrid's parameters | **3.5172** | **−0.18%** | −0.20 / −0.24 / −0.09 | −8.3 | 21.7M | 1,376 s |

Against LOOPS under the same protocol, the two parts lower rope+forget by 1.33% and the hybrid by
0.57%. **At context 512 the hybrid's LOOPS lead is gone**: it is behind the strengthened control on
every seed and behind the equal-parameter control by 0.30%, at 1.48 times the wall clock.

### 3.3 One transport head on A5 (one layer, four heads at width 128)

Accuracy 0.64, late positions 0.37, against 0.98 with all four heads transported. One head of four does
not keep the state-tracking result at this size, so the "free state tracking" claim needs most heads.

### 3.4 Frame ablation and loss by repeat distance (the 24 LOOPS checkpoints)

Holonomy moves set to the RoPE step at inference raise the trained hybrid's loss by 0.10% (0.09% at
width 768), 82% of it on tokens that repeat within 128 positions. The hybrid's largest edge over
rope+forget is on the farthest bucket (repeats more than 384 tokens back: −1.5%, −2.4% at width 768).
Recurrence alone is better than attention on tokens never seen in the window and worse on every repeat
bucket past 32.

## 4. Long context: contexts 2,048 and 8,192

Protocol: FineWeb-Edu, 32,768 tokens per update, equal modeled training FLOPs against the strengthened
softmax control at 13,531 updates (443M tokens), exact block-causal attention, `val_big` of 2^21 tokens
(1,024 windows at 2,048, 256 at 8,192), paired t across windows of the seed-averaged difference.

### 4.1 Development screens (seed 0, 100M softmax tokens)

| Arm | 2,048 | vs soft | 8,192 | vs soft |
|---|---|---|---|---|
| soft: rope+forget+gate+vres | 3.7246 | | 3.7020 | |
| hyb: hybrid holo+forget+gate+vres, one transport head | 3.7239 | −0.02% | **3.6584** | **−1.18%** |
| ev_l8 (event model, target length 8) | 3.8540 | +3.47% | 3.7615 | +1.61% |
| ev_l16 | | | 3.7842 | +2.22% |
| ev_l8_wide (event network width 768) | | | 3.8197 | +3.18% |
| ev_l8_rope (rotary frames over events) | | | 3.7476 | +1.23% |

### 4.2 Main cells

| Context | Arm | val_big | vs soft | per seed | paired t | wall |
|---|---|---|---|---|---|---|
| 512 | hyb | 3.5278 | +0.12% | +0.04 / +0.11 / +0.22 | +5.6 | 1.48× |
| 2,048 | soft | 3.4415 | | (seeds 1–2) | | 1,899 s |
| 2,048 | hyb | 3.4391 | −0.07% | −0.07 / −0.08 | −4.2 | 1.23× |
| 2,048 | hyb_rope | 3.4464 | +0.14% | seed 1 | +6.6 | |
| 2,048 | ev_l8 | 3.5664 | +3.63% | +3.55 / +3.71 | +80 | |
| 8,192 | soft | 3.4418 | | (seeds 1–3) | | 3,872 s |
| 8,192 | **hyb** | **3.4192** | **−0.66%** | −0.72 / −0.72 / −0.53 | **−23.0** | 1.35× |
| 8,192 | hyb_rope | ⟨A1⟩ | | seed 1 | | |
| 8,192 | ev_l8 | 3.6097 | +4.87% | +3.15 / +6.59 (seed 3 cancelled) | +68 | 1.5× |
| 8,192 | ev_l8_rope | 3.5493 | +3.14% | seed 1 | +47 | |
| 8,192 | ev_punct (fixed boundaries) | ⟨R1⟩ | | seed 1 | | |

The hybrid's margin over the strengthened softmax grows with context: +0.12% at 512, −0.07% at 2,048,
−0.66% at 8,192 (H1 and H2, registered after the development screens, hold).

### 4.3 Where the 8,192 gain comes from: loss by repeat distance (seeds 1–3)

| Last seen, tokens back | soft | hyb | change |
|---|---|---|---|
| never in window | 5.6106 | 5.5792 | −0.56% |
| 1–32 | 1.6487 | 1.6399 | −0.53% |
| 33–128 | 2.1597 | 2.1545 | −0.24% |
| 129–256 | 2.8678 | 2.8565 | −0.39% |
| 257–384 | 3.2687 | 3.2464 | −0.68% |
| 385–1,024 | 3.7149 | 3.6741 | −1.10% |
| 1,025–4,096 | 4.4018 | 4.3284 | **−1.67%** |
| over 4,096 | 4.8728 | 4.8155 | −1.18% |

At 2,048 the hybrid wins the far buckets (1,025–4,096: −1.44%) but loses on repeats within 32 tokens
(+0.65%), netting to −0.07%; at 512 the same pattern (385+: −0.95%; 1–32: +0.58%). Setting the
holonomy moves to the RoPE step at inference raises the 8,192 hybrid's loss by 0.18% (2,048: 0.14%).

### 4.4 Size (8,192, width 768, 8 layers, seed 1)

⟨LARGE⟩

### 4.5 The event model

- **Router collapse.** The learned router held one event per ~9 tokens for 100M tokens and then
  drifted: at the end of the long runs its mean boundary probability is 0.4992–0.4996, just under the
  threshold, and boundaries nearly vanish (mean event length 42 and 830 tokens at 8,192 seed 1, 14 and
  7.5 at 2,048, 341 on code). Seed 2 at 8,192 kept 11.8. The ratio loss constrains the hard rate only
  through the threshold, at weight 0.03; the language loss pays for every boundary through the
  decoder's state cut.
- **Boundaries, where they held** (E5): at 8,192 seed 2, 53.5% of boundaries fall on or right after
  punctuation or a newline or on a clause word, against 25.8% of tokens (on punctuation 19.4% vs 9.5%;
  after a newline 10.3% vs 2.1%; on a clause word 10.0% vs 5.4%). The most frequent boundary tokens
  are '.', ' and', '\n', 'The', 'In', ' If', 'What'; 'In' starts an event 84% of the time and 'What' 92%.
  At 2,048 the routers placed boundaries *below* the base rate (16.8–18.7% vs 25.9%). E5 fails as
  registered (mean length 11.8 is 48% above target).
- **Exact tokens are lost.** The development screens' in-context copying probe: 0.18 for events
  against 0.23–0.25 for the token arms at 8,192; in the long runs the event models are worst on every
  repeat-distance bucket, including tokens never seen in the window.
- **Fixed boundaries** (R1, after punctuation or a newline, at least every 16 tokens): ⟨R1TEXT⟩

### 4.6 Code (CodeParrot-clean Python, 2,048, seed 1)

| Arm | val_big | vs soft | paired t |
|---|---|---|---|
| soft | 0.9061 | | |
| hyb | 0.9045 | −0.17% | −2.3 |
| hyb_rope | 0.9044 | −0.18% | −2.1 |
| ev_l8 | 1.0299 | +13.7% (router collapsed, one event per 341 tokens) | +52 |

On code the holonomy frames are worth nothing over RoPE (E6 fails: frames gain 0.21 points on prose at
2,048 and −0.01 on code). The trained hybrid depends on its frames far more on code (holonomy off at
inference: +3.8%, against +0.14% on prose), so the frames are used, not rewarded.

### 4.7 Entity tracking and variable tracking (answer tokens, multiple choice)

Prompts: four keyed facts then up to 4,096 tokens of held-out text then the question (variable
tracking); three objects in boxes or people holding objects, k transfers, then where a moved object is
(entity tracking, after Kim and Schuster 2023). Every model is at chance on variable tracking (0.21–0.31
of 0.25) and on entity tracking with no transfers (0.32–0.45 of 0.33). With transfers the arms split by
heuristic, not by tracking: attention models copy the first mention (boxes, one transfer: 0.22–0.39,
below chance), and the event models, which are mostly recurrent once the router collapses, copy the
most recent mention (0.64–0.77). At 22M non-embedding parameters and 443M tokens, none of these models
tracks entities; E4 fails on these probes and on the loss buckets.



## 5. Predictions and how they fared

Registered in EVENTS.md before the runs they predict (H1–H2, R1 and A1 after the development screens,
as confirmations).

| | Prediction | Result |
|---|---|---|
| C1 | Gate lowers the control 0.2–1.0%, the candidate less | **Holds** (−0.72%, −0.12%) |
| C2 | Value residual lowers both 0.1–0.6% | Fails narrowly at the control (−0.61%); holds at the candidate (−0.29%) |
| C3 | One transport head: < 0.1% on text, A5 > 90% late | Text holds (+0.01%); **A5 fails** (0.37 late) |
| C4 | With both parts, candidate 0.5–1.0% below control and below equal-params | **Fails** (+0.12%; +0.30% vs equal-params) |
| C5 | Holonomy off at inference < 0.3%, not concentrated far | **Holds** (+0.10%, 82% within 128 tokens) |
| E1 | 2,048: events within ±0.5% of the hybrid | **Fails** (+3.7%) |
| E2 | 8,192: events ≥ 1% below hybrid and ≥ 2% below soft, every seed | **Fails** (+3.1% to +6.6% above soft) |
| E3 | Events' margin larger at 8,192 than 2,048 by ≥ 0.5 pt; larger at large size | Context: sign holds (−3.6 → −3.1 on seed 1) but between collapsed routers; size: cancelled |
| E4 | Events lead on long buckets and entity tracking | **Fails** (worst on every bucket; probes at chance or heuristic) |
| E5 | > half of boundaries at clause ends, mean length within 25% | **Fails** as registered; one checkpoint reaches 53.5% at length 11.8 |
| E6 | Frames gain more over RoPE on code than on prose | **Fails** (−0.01 pt on code, 0.21 on prose) |
| H1 | 8,192: hybrid below soft on every seed, ≥ 0.5% mean | **Holds** (−0.72 / −0.72 / −0.53) |
| H2 | Hybrid margin at 2,048 smaller by ≥ 0.5 pt | **Holds** (0.07% vs 0.66%) |
| R1 | Fixed-boundary events between soft and collapsed events, above soft | ⟨R1V⟩ |
| A1 | 8,192 hybrid with RoPE ≥ 0.4% below soft, ≤ 0.25% above hybrid | ⟨A1V⟩ |

## 6. Caveats

- **Scale.** 22M non-embedding parameters (base), 443M softmax tokens; one large-size seed. Hybrid
  results in the literature are at 0.3–7B parameters and tens of billions of tokens.
- **Wall clock.** Every advantage is at equal modeled FLOPs. In our pure-JAX kernels the hybrid takes
  1.35× the softmax wall clock at 8,192 and 1.23× at 2,048; at equal wall clock it would lose. Real
  kernels (FlashAttention, flash-linear-attention) would change both sides.
- **Equal FLOPs means unequal tokens.** At 8,192 the hybrid sees 18% more tokens than softmax for the
  same modeled FLOPs, because half its layers are linear in the context.
- **Parameters.** The 8,192 hybrid has 21.7M non-embedding parameters against softmax's 20.5M; at
  512 the equal-parameter row showed that 1.1M extra MLP parameters are worth 0.18%. No
  equal-parameter row was run at 8,192.
- **The event model is our implementation, not H-Net's.** Its router collapsed in long runs; the
  decoder state cut and the ratio-loss weight are the likely causes. The fixed-boundary run removes
  the router but not the bottleneck.
- **Probes.** Entity and variable tracking are beyond these models; the probes separate heuristics
  (first mention vs most recent mention), not tracking ability.

## 7. Questions for the reviewer

1. The hybrid's long-context margin is the one result that survived. Is the right next step a scaling
   study of that slope (sizes to ~1B, contexts to 32k, real kernels, RULER-style evaluations), or is
   the effect too well known from the hybrid literature to be worth the money?
2. The event model failed on two counts: the router drifted, and the bottleneck loses exact tokens.
   Is there a version worth one more try (events beside token-level attention, as a third memory,
   rather than instead of it)?
3. The frames are used (+0.18% when removed at 8,192, +3.8% on code) but not rewarded. Do you read
   that as "the group atom is unneeded on text" or as "the training budget never makes it pay"?
