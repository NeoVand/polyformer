# Base-model probes, 29 Oct 2026 ($0, M4 MPS, untouched weights)

Scripts and JSON in this folder. Direct answers, no chain of thought, few-shot, teacher-forced exactness (every answer
token is the argmax), 40 examples per task (Ouro, LFM3) or 20 trials (Qwen3.5).

## Ouro-1.4B (ByteDance, Apache-2.0; whole 24-layer stack looped, trained at 4 passes) — ouro_probe_T32.json
Exact rate by loop passes 1..32 (one 32-pass forward read out at every pass):
- add5: 0.50, 0.93 at 2, 0.93-0.95 through 11, 0.38 at 16, 0 from 24.
- add8: peak 0.88 (3 passes); add12: peak 0.78 (3); mul2: peak 0.93 (10-13); mul3: max 0.28; swaps (full 5-letter
  permutation): ~chance at every pass.
- Text perplexity: 70.9 (1), 11.0 (4, the minimum), 15.3 (16), 102 (32).
- Hidden state never settles: relative change per pass stays 0.1-0.4 out to 32. Exit gate puts its mass on passes 3-4.
Verdict: no native affordance for exact computation; passes beyond the trained 4 add nothing and beyond ~12 destroy.
Agrees with STARS (2605.26733) and 2604.11791.

## LFM3-1.7B (Liquid, LFM Open License v1.0, <$10M revenue) — lfm3_probe.json
Digits tokenised in 3-digit chunks. add3 0.62, add5 0.20, add8 0.05, add12 0.10, mul2 0.62, mul3 0.10, swaps 0.00-0.10.
No matrix state, no loop. Strong chat/tool model per vendor; not a computer.

## Qwen3.5-0.8B (Apache-2.0; 18 Gated DeltaNet layers x 16 heads x 128x128 state + 6 gated-attention layers;
natively image+video) — qwen35_probe.json, qwen35_window_W32.json, qwen35_film_untouched.png
- Decay: median head half-life 19 tokens; a few heads 1.8k-7.6k tokens; L0H8 ~2.2M (alpha ~ 1).
- "Secret number" recall across 0-1,024 filler tokens: 1.00. Zeroing or swapping every DeltaNet state at the question:
  no effect (answer stays own) -> the number is read through attention.
- Attention windowed to 32 tokens (6 x 32 < filler): recall 0.30 (64), 0.30 (256), 0.10 (1,024; chance 0.10);
  with states zeroed 0.10 / 0.10 / 0.00; states swapped from a donor -> donor's number 0.15 / 0.30 / 0.15.
  A weak, fading trace in the state; not usable as registers without training.
- Film strip of the four longest-lived heads while "Now x = 3 ... 7 ... 1 ... 9 ... 4" is written: raw states are sparse
  stripes and rank-one crosses; no register picture in the untouched model (Fable's warning holds: needs the key basis).

## Theory constraint found today
Brandoit et al., arXiv 2609.32447 (26 Sep 2026): affine recurrences (DeltaNet, Mamba, RWKV-7, DeltaProduct) realise at
most definite automata at finite precision; length-independent tracking needs one map that both contracts and
separates. So registers held only in a Gated DeltaNet state cannot be exact for all lengths without a nonaffine refresh.
