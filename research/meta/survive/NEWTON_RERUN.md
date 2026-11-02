# Newton rerun: the per-arity normalisation floor (registered 1 Nov 2026, before launch)

**Why.** `survive/AUDIT.md` §1a found a likely false negative in `lm_a`, the enwik8 bpc result: hybrid 1.6571 against
GPT 1.6505.
- Newton divides each arity feature by C(t, m) *before* an RMS normalisation with a 1e-6 floor.
- Higher-arity features are tiny, about 2e-5 RMS at length 256 for random phases, so the floor holds them at about
  0.02 to 0.29 RMS where they should be about 1.
- In effect, arities 3 and 4 were switched off.
- The TF32 hypothesis was ruled out.

Neo, 1 Nov: "rerun Newton. Let's see if we had an edge there."

**Change.** `lm.py --nfloor` (default 1e-6, the original behaviour). The fixed arm uses 1e-12, a scale-aware floor
under float32.

**Grid `lm_newton_fix`.** lm_a's settings unchanged: enwik8 bytes, 8,000 steps, context 256, batch 64, lr 1e-3, seeds
0–2, H100. Three arms:
- GPT;
- hybrid at rank 32 with nfloor 1e-6 (the original);
- hybrid at rank 32 with nfloor 1e-12 (the fix).

Nine runs, about $2–4.

**Predictions (orchestrator, before launch):**

| Measure | Prediction |
|---|---|
| GPT mean | reproduces lm_a's 1.6505 within ±0.004 |
| hybrid at 1e-6 mean | reproduces 1.6571 within ±0.004 |
| hybrid at 1e-12 minus GPT, mean of paired seeds | +0.002 (band −0.006 to +0.010): the fix closes most of the gap but gives no gain |
| P(fixed hybrid below GPT on all 3 paired seeds by ≥ 0.005 mean) | about 0.15 |

**Decision rule.**
- **Edge.** The fixed hybrid is below GPT on all three paired seeds, with a mean gain of ≥ 0.005 bpc. Then, and only
  then, a per-arm learning-rate sweep and a compute-matched comparison follow, before any claim.
- **Otherwise.** The language-model null stands for this configuration, now without the floor bug.
- **Either way.** One run cannot speak for Newton at larger scale, or with keys and values.

## Result (1 Nov 2026, Modal app ap-5wzCR3a3uuJPo4LwehALdg; `research/results/lm_newton_fix.jsonl`)

Validation bits per character; lower is better. Nine runs, no errors, about 15 H100-minutes (about $1).

| Arm | Seed 0 | Seed 1 | Seed 2 | Mean | Minus GPT, per seed | Mean difference |
|---|---|---|---|---|---|---|
| GPT | 1.6435 | 1.6515 | 1.6581 | **1.6510** | | |
| hybrid, floor 1e-6 (original) | 1.6590 | 1.6637 | 1.6546 | **1.6591** | +0.0155 / +0.0122 / −0.0035 | +0.0081 |
| hybrid, floor 1e-12 (fixed) | 1.6639 | 1.6629 | 1.6515 | **1.6594** | +0.0204 / +0.0114 / −0.0066 | +0.0084 |

**Against the predictions:**
- GPT reproduced: 1.6510 against 1.6505.
- The original hybrid reproduced within the band: 1.6591 against 1.6571 ± 0.004.
- The fixed hybrid is +0.0084 against GPT. That is inside the registered band (−0.006 to +0.010) but worse than the
  point prediction (+0.002).

**No edge.** The fixed hybrid is behind GPT on two of three seeds, and the decision rule's edge condition fails.
Fixing the floor changed nothing measurable: 1.6594 against 1.6591.

**What this settles.** The floor was not why Newton gives no gain on language modelling; in this configuration the
null is real. Newton's standing result is still the synthetic relational one (exact Match-k, SET). No follow-up rate
sweep is triggered.
