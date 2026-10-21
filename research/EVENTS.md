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
  fixed buffer of K = 1.5 T/ℓ slots (static shapes). Boundaries beyond the buffer merge into the last
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
use an exact block-causal attention: queries in blocks of 1,024 against the keys up to their block, bf16
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
| Event model development screens (2,048 and 8,192, seed 0) | $14 |
| 8,192 headline cell (three arms, three seeds, one ablation) | $64 |
| 2,048 cells (three arms, two seeds, one ablation) | $17 |
| 8,192 large size (three arms, one seed) | $38 |
| Code corpus preparation and four arms at 2,048 | $14 |
| Evaluations (buckets, boundaries, entity tracking) | $4 |
| Margin for failures | about $40 |

(Revised at the event-study registration in section 5, from measured step times.)

The ledger is `research/results/loops_budget.json`; `loops_modal.py` caps are raised to a $300 total.

## 5. Log

- 21 Oct. Paper correction committed on `claude/loops` (Question bullet, Part VIII closing paragraph,
  "what next" item): against rotary softmax, recurrence wins by 0.1–0.3% and the hybrid by 0.8–0.9%.
  Not published; main is only updated with Neo's OK.
- Code: `gate_out`, `vres` and `vtrans_heads` in `loops_layers.py`; the value residual is threaded
  through `lm.forward` (`loop_block`, rematerialisation kept); 17 CPU tests pass. Evaluator
  `loops_eval.py` launched on all 24 confirmation checkpoints (manifest `events_eval`).
- **Cheap-day screen registered** (seed 0, 3,051 updates, lr .008; manifest `events_cheap`):
  rope+forget with gate / vres / both; the candidate (hybrid GAGAGA holo+forget) with gate / vres /
  both / one transport head / all four; one-layer A5 with one transport head. Selection rule for the
  three-seed confirmation: the strengthened control is rope+forget plus whichever of {gate, vres,
  both} has the lowest screen loss (plain rope+forget if none beats it); the strengthened candidate
  is chosen the same way among {gate, vres, both}, and the one-head transport is added if
  `hybrid_hf_gate_vres_vt1` is within 0.1% of `hybrid_hf_gate_vres` (C3). Confirmation arms: the
  strengthened control, the strengthened candidate, and the strengthened control with its MLP
  widened to the candidate's non-embedding parameter count; seeds 1–3, equal modeled FLOPs.
- The first evaluation launch (`events_eval`, six L4 jobs) never got a container: every input stayed
  PENDING for 40 minutes while H100 jobs scheduled normally. Cancelled and settled at $0 in the
  ledger (no compute ran); relaunched on H100 as `events_eval_h100`.
- Event model implemented (`events_model.py`, arch `events` in `lm.py`) with exact block-causal
  attention (`loops_layers.causal_attention`) and a decay hook in `beyond_layers.apply_layer`.
  Tests: blockwise equals dense attention even with large forget biases; the event model is causal
  (future tokens change no earlier prediction, also when the slot buffer overflows); the router
  receives gradient. Modeled training FLOPs per token (lm convention): context 2,048: softmax+forget
  306.8M, hybrid 303.0M, events 283.8M; context 8,192: 422.7M, 361.0M, 291.0M, so at equal compute
  the event model sees 1.08x (2k) and 1.45x (8k) the tokens of softmax+forget. A timing pilot
  (`events_timing`) prices the study before its registration is finalised.
- **Probes 1–2 on the 24 LOOPS checkpoints** (`events_eval_h100`; per-token loss on the 1,024
  `val_big` windows, seed means; buckets by how far back the target token last occurred):

  | Arm | all | never | 1–32 | 33–128 | 129–256 | 257–384 | 385+ |
  |---|---|---|---|---|---|---|---|
  | hybrid GAGAGA holo+forget | 3.5479 | 4.9424 | 1.6806 | 2.2165 | 2.9121 | 3.3218 | 3.6289 |
  | hybrid GAGAGA rope | 3.5513 | 4.9432 | 1.6850 | 2.2235 | 2.9199 | 3.3336 | 3.6777 |
  | deltaproduct | 3.5690 | 4.9492 | 1.7027 | 2.2541 | 2.9908 | 3.4409 | 3.7363 |
  | rope+forget | 3.5709 | 4.9687 | 1.7002 | 2.2346 | 2.9304 | 3.3535 | 3.6851 |
  | gdn | 3.5772 | 4.9568 | 1.7099 | 2.2648 | 3.0035 | 3.4381 | 3.7390 |
  | rope | 3.5798 | 4.9776 | 1.7059 | 2.2450 | 2.9465 | 3.3694 | 3.7023 |
  | abs | 3.6137 | 5.0251 | 1.7273 | 2.2644 | 2.9599 | 3.3847 | 3.6738 |

  Recurrence alone is better than attention on tokens never seen in the window and worse on every
  repeat bucket past 32; the hybrid is best everywhere, with its largest edge over rope+forget on the
  farthest bucket (−1.5%; −2.4% at width 768). Frame ablation on the trained candidate: holonomy
  moves set to the RoPE step raise the loss by 0.10% (0.09% at width 768), 82% of it on repeats
  within 128 tokens; **C5 holds**. Clock velocities set to 1 raise it by 14%: the model built its
  position code on the clocks, so this ablation measures dependence, not benefit.

- **Cheap-day screen** (`events_cheap`, seed 0, 3,051 updates, 100M tokens, equal updates; plain
  rows from `loops_screen`):

  | Arm | rope+forget | hybrid GAGAGA holo+forget |
  |---|---|---|
  | plain | 3.8308 | 3.8082 |
  | + gate | 3.8034 (−0.72%) | 3.8036 (−0.12%) |
  | + value residual | 3.8073 (−0.61%) | 3.7973 (−0.29%) |
  | + both | **3.7844 (−1.21%)** | 3.7926 (−0.41%) |
  | + one transport head | | 3.8085 (+0.01%) |
  | + both + one transport head | | 3.7881 (−0.53%) |

  **C1 holds** (the gate: −0.72% on the control, −0.12% on the candidate). **C2 fails narrowly** at
  the control (−0.61%, above the registered 0.1–0.6%) and holds at the candidate (−0.29%). **C3's
  text half holds** (one transport head: +0.01% alone, −0.12% with both parts); its A5 half is pending.
  The ordering reversed: with both parts, the softmax control (3.7844) is below the candidate (3.7881)
  at equal updates, although the candidate has 2% more modeled FLOPs per token. The published parts
  supply most of what resets and frames supplied. Wall clock per 3,051 updates: control 344 s,
  candidate 540 s.
- **Selection rule applied:** strengthened control = rope+forget+gate+vres (`rope_forget_gate_vres`);
  strengthened candidate = hybrid+gate+vres with one transport head (`hybrid_hf_gate_vres_vt1`,
  3.7881, within 0.1% of and below `hybrid_hf_gate_vres`); equal-parameter control =
  `rope_forget_gate_vres_eqp`, the control with MLP width 2,234 (21,687,484 non-embedding parameters
  against the candidate's 21,686,272). Seeds 1–3, equal modeled FLOPs (13,071 / 12,806 / 12,766
  updates against the reference 13,531 for abs), `val_big` and final checkpoints saved; the paired
  test is on per-sequence losses over the 1,024 `val_big` windows (`loops_eval.py`). Manifest
  `events_confirm`.
- The A5 check's L4 input again never got a container (12 minutes PENDING); cancelled, settled at $0,
  relaunched on H100 (`events_a5`).

### Event-study registration (before any event-model training)

Protocol: FineWeb-Edu, GPT-2 tokens, 32,768 tokens per update (16 windows at 2,048, 4 at 8,192),
Muon at lr .008, warmup a tenth of the updates, cosine to a tenth, bf16 with fp32 accumulation.
Every attention in every arm carries the gate and the value residual (the cheap day's result), and
every arm with holonomy frames has one transport head. Equal modeled training FLOPs per run (lm's
convention, `loops_jobs.long_flops`): the reference is the strengthened softmax control at a given
number of updates, and every other arm gets the updates that match its FLOPs.

Arms (`loops_jobs.LONG`):

- `soft`: rope+forget+gate+vres, 6 layers × 512 (the control in E1–E4).
- `hyb`: hybrid GAGAGA holo+forget+gate+vres, one transport head (the token-level candidate).
- `ev_l8`, `ev_l16`: the event model, target event length 8 or 16; 2 Gated DeltaNet layers in, 6
  attention layers over events (holo+forget+gate+vres, one transport head), 2 Gated DeltaNet layers
  out, width 512.
- `ev_l8_wide`: as `ev_l8` with the event network at width 768 (12 heads): FLOPs spent per event
  instead of on more tokens.
- `ev_l8_rope`: as `ev_l8` with rotary frames over event index instead of holonomy (no transport):
  the frames-over-events ablation.
- `hyb_rope`: as `hyb` with rotary frames (for E6).

Modeled training FLOPs per token, base size: 2,048: soft 316.3M, hyb 307.8M, ev_l8 276.9M,
ev_l16 263.6M, ev_l8_wide 307.7M; 8,192: soft 432.2M, hyb 365.7M, ev_l8 281.0M, ev_l16 264.6M,
ev_l8_wide 313.8M. So at 8,192 the event model sees 1.54× the softmax control's tokens.

Stages, in order:

1. **Development screens** (`events_dev`, seed 0, reference 3,051 updates = 100M softmax tokens):
   at 8,192: soft, hyb, ev_l8, ev_l16, ev_l8_rope, ev_l8_wide; at 2,048: soft, hyb, ev_l8.
   **Selection rule:** the headline event arm is whichever of ev_l8, ev_l16, ev_l8_wide has the lowest
   8,192 screen loss. **Guard:** if that arm is more than 2% above `soft` at 8,192, the headline is not
   run as registered; the event model is debugged first and the change logged.
2. **Headline cell** (8,192, base, seeds 1–3, reference 13,531 updates = 443M softmax tokens):
   soft, hyb, the selected event arm; plus ev_l8_rope (or the selected arm with rotary frames) at
   seed 1. Final checkpoints and `val_big` (256 windows) saved. E2 and the 8,192 half of E3.
3. **Context 2,048** (seeds 1–2, reference 13,531): soft, hyb, the selected event arm, and hyb_rope
   at seed 1. E1, the 2,048 half of E3, and the prose half of E6.
4. **Large size** (8,192, width 768, 8 layers, 12 heads, MLP 3,072; the event network 8 layers;
   seed 1, reference 13,531): soft, hyb, the selected event arm. The size half of E3 (sign only).
5. **Code** (`/data/code_python`: CodeParrot-clean Python, 921M training tokens, 2,048, seed 1,
   reference 13,531): soft, hyb, hyb_rope, the selected event arm. E6.
6. **Evaluations** on the saved checkpoints: repeat-distance buckets extended to 1,025–4,096 and
   4,097+ at 8,192 (E4); boundary statistics on held-out text (E5); entity tracking scored on answer
   tokens (E4).

E2 at each seed is the loss on the 256 `val_big` windows; the paired test is across those windows.
Estimated cost: development $14, headline $64, 2,048 $17, large $38, code $14, evaluations $4: $151,
which with the cheap-day confirmation ($20) and the $88 already committed leaves about $40 of margin
in the $300.
- **A5 with one transport head** (`events_a5`, one layer, 4 heads at width 128, 6,000 updates):
  accuracy 0.64, on late positions 0.37 (all four heads transported: 0.98). **C3's A5 half fails**: one
  head of four does not keep the state-tracking result at this size and budget.
- **Development screens** (`events_dev`, seed 0, equal modeled FLOPs to `soft` at 3,051 updates;
  validation on 2^20 tokens):

  | Arm | 2,048 | vs soft | 8,192 | vs soft | non-emb. params | wall (s) |
  |---|---|---|---|---|---|---|
  | soft (rope+forget+gate+vres) | 3.7246 | | 3.7020 | | 20.5M | 482 / 984 |
  | hyb (hybrid holo+forget+gate+vres, 1 transport head) | 3.7239 | −0.02% | **3.6584** | **−1.18%** | 21.7M | 684 / 1,336 |
  | ev_l8 | 3.8540 | +3.47% | 3.7615 | +1.61% | 37.0M | 773 / 1,494 |
  | ev_l16 | | | 3.7842 | +2.22% | 37.0M | 1,485 |
  | ev_l8_wide (event network width 768) | | | 3.8197 | +3.18% | | |
  | ev_l8_rope (rotary frames over events) | | | 3.7476 | +1.23% | 36.4M | 1,418 |

  The routers hit their targets without supervision (mean event length 8.95 and 18.7 at 8,192, 9.9
  at 2,048). Every event arm is behind the softmax control, and further behind it at 2,048 than at
  8,192 (−3.47% → −1.61%: the slope has the registered sign, at one seed and 100M tokens). The
  in-context copying probe is the clearest cost of compression: 0.18 for events against 0.23–0.25
  for the token-level arms at 8,192. Rotary frames over events beat holonomy frames (−0.37%).
  The token-level hybrid gains with context: −0.02% at 2,048, −1.18% at 8,192 (and +0.10% at 512 with
  the same parts, `events_confirm` seed 1, below).
- **Selection applied:** ev_l8 has the lowest 8,192 loss among ev_l8, ev_l16 and ev_l8_wide; it is
  1.61% above `soft`, inside the 2% guard, so the headline runs as registered with ev_l8, and the
  ablation arm is ev_l8_rope at seed 1.
- **Registered now, after seeing the development screens (a confirmation, not a blind prediction):**
  H1. At 8,192 and base size, `hyb` is below `soft` on each of seeds 1–3 at 443M softmax tokens, by
  at least 0.5% on the mean. H2. Its margin at 2,048 (seeds 1–2) is smaller than at 8,192 by at least
  0.5 points.
- **Cheap-day confirmation** (`events_confirm`, context 512, seeds 1–3, equal modeled FLOPs, 443M
  softmax tokens; `val_big` 1,024 windows; paired t over windows of the seed-averaged difference):

  | Arm | val_big | vs control | per seed | paired t | non-emb. params | wall |
  |---|---|---|---|---|---|---|
  | control: rope+forget+gate+vres | 3.5235 | | | | 20.5M | 1,241 s |
  | candidate: hybrid holo+forget+gate+vres, 1 transport head | 3.5278 | +0.12% | +0.04 / +0.11 / +0.22 | +5.6 | 21.7M | 1,837 s |
  | equal-parameter control (MLP 2,234) | **3.5172** | **−0.18%** | −0.20 / −0.24 / −0.09 | −8.3 | 21.7M | 1,376 s |

  Against LOOPS's rows under the same protocol, the two parts lower rope+forget by 1.33% (3.5709 →
  3.5235) and the hybrid by 0.57% (3.5479 → 3.5278). **C4 fails**: with the gate and the value
  residual in both arms, the candidate is above the control on every seed, and above the
  equal-parameter control by 0.30%, at 1.48 times the wall clock. At context 512 the hybrid's 0.64%
  over rope+forget in LOOPS was something the published parts give softmax for free.
- `events_2k` and `events_code` were planned before a change to `loops_jobs.py` and refused to launch
  (sources changed since planning); nothing ran. The same job lists are re-planned as `events_2k_b`
  and `events_code_b`.
- **Router collapse.** The learned router held its target in the 100M-token development screens
  (mean event length 8.9–9.9) but not over 443M tokens: at the end of training the mean boundary
  probability sits just under the threshold (0.4992–0.4996) and boundaries nearly vanish. Mean event
  length: 42 tokens (`events_8k` ev_l8 seed 1), 830 (ev_l8_rope seed 1), 14 (2,048 seed 1), 341
  (code). The ratio loss only constrains the hard boundary rate through the threshold, at weight 0.03,
  while the language loss pays for every boundary through the decoder's state cut; the event network
  is then fed a handful of events per window. So the long event runs test a collapsed router, not
  memory over events. Final `val_big` at 8,192, seed 1: ev_l8 3.5493 and ev_l8_rope 3.5483 against
  soft 3.4414 (+3.1%).
- **Two runs cancelled** at 18:42 UTC and settled at elapsed time: the large-size event arm (it would
  compare one collapsed router with another, so E3's size half cannot be read from it) and
  `events_8k` ev_l8 seed 3 (at about 25%; seed 2 continues as the second seed).
- **Registered before launch (R1):** an event model with fixed boundaries, so nothing about them is
  trained: a boundary after every token that ends in punctuation or holds a newline, and at least
  every 16 positions (`ev_punct`; 2,560 slots; ratio loss off; otherwise ev_l8). 8,192, seed 1,
  equal modeled FLOPs (307.0M per token, 19,048 updates). Prediction: it lands between soft and the
  collapsed ev_l8 (3.4414 < x < 3.5493), and stays above soft: memory over events loses exact
  copying, which the development screens already showed at a working router (+1.6% at 100M tokens).
