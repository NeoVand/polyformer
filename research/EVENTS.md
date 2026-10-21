# EVENTS: events, not tokens, as the unit of memory

Started 21 October 2026 on the recommendation of [LOOPS_REVIEW.md](LOOPS_REVIEW.md), which read
[LOOPS_REPORT.md](LOOPS_REPORT.md). Budget: **$300 of Modal in total** for LOOPS and EVENTS together
($75.41 already spent by LOOPS; about $225 here). Predictions are committed before the runs they
predict; the log is at the end.

## 0. What changes from LOOPS

- **The 1% gate is retired.** Claims are registered as signs and minimum sizes of *changes* in a
  margin (across context length and model size), plus equal-parameter and wall-clock rows, plus a
  paired test on per-sequence losses. A fixed margin at one size and one context is not a claim.
- **Context 512 is no longer the main regime.** At 512 tokens, attention scores are about 7% of a
  layer's FLOPs (the review's table), so no attention change can win much there. The main cells are
  context 2,048 and 8,192.
- **The unit of memory becomes the event.** The LOOPS models segmented text into sentences and
  clauses and forgot at the boundaries on their own; the event model builds that in as computation.

## 1. Program, in the review's order

1. **Cheap day** (known parts, strengthen both sides of the comparison at context 512):
   gated attention output (Qiu et al. 2025: an element-wise sigmoid gate from the layer input on the
   attention output, before the output projection), value residual (Zhou et al. 2024: every
   attention layer's values receive a learned share of the first attention layer's values), value
   transport in **one** head only, an equal-parameter softmax row, wall-clock rows, the frame
   inference ablation and long-range loss buckets. The gate and the value residual go into **both**
   the softmax control and the candidate.
2. **The paper's recurrence claim is corrected** (review 1.4): under one protocol, recurrence beats a
   RoPE softmax baseline by 0.1–0.3%, and the hybrid by 0.8–0.9%; BEYOND's 1% came from learned
   absolute positions.
3. **The event model** (section 2), with exact long-context attention.
4. **Where order is dense:** the same arms on a Python corpus, and entity-tracking / long-range
   evaluations on the trained models, scored on answer tokens.
5. **The slope:** two context lengths (2,048 and 8,192), two sizes (the LOOPS base and large), three
   seeds at the headline cell (8,192, base).

## 2. The event model

Three memories and one boundary signal (review 3.3), in the style of H-Net (Hwang, Wang and Gu).

- **Encoder (tokens):** two Gated DeltaNet layers over tokens. Their decay is tied to the boundary
  probability, so the fast-weight state is sharply decayed at an event end.
- **Router:** H-Net's boundary probability p_t = (1 − cos(W_q h_t, W_k h_{t−1}))/2, p_0 = 1, and a
  boundary where p_t ≥ 1/2: a decision that depends on tokens up to t only. A ratio loss (H-Net's
  form, weight 0.03) pulls the boundary rate toward a target of one event per ℓ tokens.
- **Downsampler:** the encoder state at each boundary token becomes that event's vector, placed in a
  fixed buffer of K = T/ℓ_min slots (static shapes). Boundaries beyond the buffer merge into the last
  slot; whether that happens depends only on the past, so causality holds.
- **Main network (events):** attention over event vectors with the LOOPS frames carried over the
  event sequence (rotary over event index, content clocks, holonomy blocks) and the forget gate over
  events, plus MLPs. It processes one position per event, so at equal FLOPs per token it can be
  about ℓ times more expensive per position: deeper than the token-level models.
- **Dechunker:** H-Net's smoothing over events with the boundary probabilities, then each token
  receives the output of the event it belongs to (whose boundary is at or before it), multiplied by
  a straight-through confidence; added to a projected residual from the encoder.
- **Decoder (tokens):** two Gated DeltaNet layers over tokens, then the output head.

Token t's prediction uses only tokens ≤ t: the router is causal, the event containing t starts at or
before t, and the main network is causal over events. This is tested by perturbing future tokens.

**Long-context attention for the token-level controls.** The Forgetting Transformer's bias is
c_i − c_j with c a running sum of log forget gates, which reaches thousands at 8k tokens; bf16 cannot
hold it near the softmax maximum, so a stock flash kernel with a key bias is not exact. The controls
use an exact block-causal attention: queries in blocks of 512 against the keys up to their block, bf16
products with fp32 accumulation, and the bias added in fp32 per tile. FLOPs are counted causally as
before.

## 3. Predictions (registered before any EVENTS run)

Cheap day (context 512, seed 0 screens; then seeds 1–3 for the strengthened pair):

- C1. Gated attention output lowers the softmax control's loss by 0.2–1.0% and the candidate's by
  less than the control's (the candidate already has resets).
- C2. The value residual lowers both by 0.1–0.6%.
- C3. Value transport in one head costs the candidate less than 0.1% on text, and one layer with one
  transport head still tracks A5 above 90% on late positions.
- C4. With both parts in both arms, the candidate stays 0.5–1.0% below the softmax control at
  equal FLOPs, and stays below an equal-parameter softmax control (MLP widened to match).
- C5. Switching the trained candidate's holonomy moves to identity at inference raises its loss by
  less than 0.3%, and the increase is not concentrated on the long-distance repeat buckets.

Event study (equal modeled FLOPs per token; FineWeb-Edu windows of 2,048 and 8,192 tokens):

- E1. At context 2,048 the event model is within ±0.5% of the token-level candidate.
- E2. At context 8,192 and base size, the event model is at least 1% below the token-level candidate
  and at least 2% below the RoPE+forget softmax control, on each of three seeds.
- E3. **The slope:** the event model's margin over RoPE+forget softmax is larger at 8,192 than at
  2,048, by at least 0.5 points, and at 8,192 it is larger at the large size than at the base size
  (sign registered; no minimum at one seed).
- E4. On the long-range buckets and on entity tracking, the event model leads the token-level arms.
- E5. Learned boundaries fall mostly on sentence and clause ends (more than half of boundaries on
  or right after punctuation, newline or a function word that opens a clause), without supervision,
  at a mean event length within 25% of the target.
- E6. On code, the frames move from neutral to positive: the candidate with holonomy frames beats
  the same model with RoPE by more than it does on prose.

Every prediction is reported as held or failed, with the numbers.

## 4. Budget plan

| Phase | Est. cost |
|---|---|
| Cheap day: 8 screens, A5 check, 9 confirmation runs, evaluations | $35 |
| Event model development screens (2,048 and 8,192, seed 0) | $25 |
| 2,048 cells (three arms, one seed) | $10 |
| 8,192 headline cell (three arms, three seeds) | $55 |
| 8,192 large size (three arms, one seed) | $35 |
| Code corpus preparation and three arms at 2,048 | $15 |
| Entity-tracking evaluation | $5 |
| Margin for failures | $45 |

The ledger is `research/results/loops_budget.json`; `loops_modal.py` caps are raised to a $300 total.

## 5. Log
