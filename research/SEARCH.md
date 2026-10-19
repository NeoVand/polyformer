# Beating softmax attention: a theory of where it can happen, and a staged search

Working note, 19 October 2026. Companion to `FORMALISM.md` (the operators) and `PLAN.md` (the
paper). The question: can a higher-order layer give a sizable improvement over pairwise (softmax)
attention on real sequence modelling, and how do we find out without fooling ourselves or burning
months on a dead end?

## 1. Where we stand

- On relations defined over many tokens (zero sums on a group, keyed relations, chains), the
  higher-order layers win decisively. Newton attention is exact where softmax at any depth we tried
  sits at chance. Free-field attention solves pointer chasing and three-hop composition in one layer,
  and holds keyed Match-4 among distractors.
- On text we have one regime measured: enwik8 bytes at 3.3M parameters and 8,000 steps. There
  free-field attention matches softmax (1.652 against 1.650 bits per character) and gains nothing.
- HOMA's published Match3 is beaten, but our cubic attention beats it by the same margin, so that
  win belongs to third-order attention in general.

## 2. Is quadratic attention "not the answer"?

Partly. What is established:

- Pairwise scores cannot see a relation whose lower-order marginals are uninformative (our Theorem 1,
  Sanford et al. 2023). Depth can compose it in principle, but gradient descent has to cross a leap
  to find the composition (Abbe et al. 2023, our Feynman attention result).
- Softmax attention costs O(n²) and still needs depth for multi-hop structure (p-hop needs about
  log p layers; induction needs two).

What is also established, and is the bar we have to clear:

- In language modelling, pairwise attention plus an MLP plus depth has been very hard to beat at
  equal compute. Linear attention, state-space models and most higher-order variants match it far
  more often than they beat it.
- The clearest positive result for a higher-order layer is 2-simplicial attention (Roy et al. 2025).
  It reports a better scaling exponent on reasoning, math and code at billion-parameter scale, with
  training tokens held fixed. That suggests where to look (token-limited, reasoning-heavy data, large
  enough models), not that small byte-level models should show it.

So the working hypothesis is not "softmax is wrong". It is: **pairwise attention spends depth and
data to build relations that a native higher-order term gets directly, and that difference pays
only where such relations are frequent and hard.** The search below measures exactly that.

## 3. Theory: when can a higher-order term beat softmax + MLP + depth?

### 3.1 Heads and an MLP already form conjunctions

H heads followed by an MLP can compute any smooth function of the query and H attended tokens. So
a k-way conjunction with k − 1 ≤ H is within reach of one pairwise layer, **provided each participant
can be selected on its own**: some score that depends on the query and that token alone singles it
out. Pairwise attention fails only when **selection is joint**, i.e. which tokens matter depends on the
others (as in "find two cards that, with me, sum to zero").

Define the **leap content** of a prediction problem as the share of its achievable loss reduction
that comes from joint-selection relations, those whose lower-order marginals carry (almost) no
signal. Theorem 1 says pairwise scores get none of it in one layer; Section 8 of FORMALISM.md says
composed depth finds it slowly or not at all.

**Prediction 1.** A higher-order layer beats softmax by a margin that grows with the leap content of
the data, and gives nothing where leap content is near zero.

### 3.2 Why bytes were the wrong place to look

At the byte level, most of the loss is spelling and local n-grams. These have strongly informative
pairwise marginals (the previous few bytes), so their leap content is close to zero. Tokenization
moves spelling into the vocabulary, and the remaining loss is about relations between words:
agreement, reference, argument structure, and in code, scopes and bindings. That raises leap content
somewhat, but natural text still has informative marginals for most of these relations.

**Prediction 2.** BPE tokens show a small effect, larger than bytes. Code and arithmetic show more.
Long-context retrieval with composite keys shows the most.

### 3.3 Three levers, and what each would look like

| Lever | Mechanism | Where it shows | Observable |
| --- | --- | --- | --- |
| Capability | joint selection that pairwise scores cannot represent in one layer | relational and algorithmic data | accuracy gap at fixed depth |
| Depth efficiency | one higher-order layer does the work of several pairwise layers (walks for chains, subsets for relations) | any data with multi-step structure | equal loss with fewer layers at equal FLOPs |
| Sample efficiency | a native term gives gradient a direct path, so circuits that need a leap under composition (induction heads, multi-hop lookups) form earlier | token-limited training | earlier phase changes; lower loss per token, especially when tokens repeat |

The **sample-efficiency lever is the most promising for language**. Induction heads form through
a two-layer composition and appear as a sudden phase change (Olsson et al. 2022), which is a leap.
The walk sector computes a two-step lookup in one layer. If it removes that leap, in-context learning
should arrive earlier and the loss per token should drop early in training. That is cheap to measure
at small scale and would matter at any scale.

### 3.4 What a higher-order layer will not fix

- **State tracking** (composing permutations, as in S5 word problems) needs depth that grows with
  length for any constant-depth threshold circuit (Merrill and Sabharwal). Subsets and a fixed
  number of walks are still constant depth, so this is not a target.
- **Compute.** A free-field layer costs about K softmax heads. Any gain has to survive comparison at
  equal FLOPs, not equal parameters.

## 4. Rules so we do not fool ourselves

1. **Equal FLOPs first, equal parameters second.** Report loss against training FLOPs and against
   tokens, with the FLOP count including every power-sum and walk pass.
2. **Tune every architecture.** Sweep at least three learning rates per architecture at the smallest
   scale and keep the best, so a new layer is not handicapped by a borrowed schedule.
3. **Three seeds** on every cell that enters a claim; five on headline cells. Report spreads.
4. **Two scales minimum** before any language claim; a gain that shrinks with scale is a no-go.
5. **Pre-register** the effect size that counts (below) before each stage runs.
6. **Same data order** for all models at a scale (seeded sampler), the same tokenizer, the same
   held-out set.
7. **Negative results are kept**, written up and published in the report; they bound the claims.

## 5. The staged search

Each stage has a budget cap, a go criterion fixed in advance and a meaning for failure. Stages S1
and S2 can run beside S0; S3 onwards waits for their gates.

### S0. Token-level language, the regime check (cap $75)

- **Data:** TinyStories (fast signal for small models) and one FineWeb-Edu shard (realistic text),
  GPT-2 tokenizer, context 512.
- **Models:** about 20M non-embedding parameters, roughly Chinchilla-sized data (about 400M
  tokens): softmax; free-field with arities 2..4 off at init (mu = 0.05); the same at equal FLOPs
  (fewer layers); softmax with one more layer as a depth reference.
- **Protocol:** learning-rate sweep on one seed at 100M tokens, then three seeds at the best rate.
- **Go:** at least 1% lower held-out loss at equal FLOPs on three of three seeds, on either dataset.
  The equivalent is matching softmax with 25% fewer FLOPs.
- **No-go means:** the token regime does not change the byte result at this scale. Move the
  language question to S2 and S4; do not scale up yet.

### S1. Diagnostic map, where pairwise attention runs out (cap $25)

At fixed small depth (one and two layers), equal FLOPs, three seeds:

- multi-query associative recall (Zoology's MQAR), and a composite-key variant where a key is two
  tokens and only the pair identifies the value (joint selection);
- induction and copying with distractors; p-hop at p = 4, 8, 16;
- Dyck-2 bracket matching; multi-digit addition with carries;
- Match-k with tokens drawn from a vocabulary (language-like inputs).

**Output:** a table of where each layer wins, which defines the data most likely to show an
improvement. **Go** if free-field beats softmax at equal FLOPs on at least two families by ≥ 10
points.

### S2. Sample efficiency: do circuits form earlier? (cap $25)

- On TinyStories and on a synthetic in-context-learning stream, track the induction score through
  training: the in-context loss drop from token 50 to token 500 (Olsson et al.).
- Do this for softmax, for free-field with a causal walk sector, and for free-field without walks.
- **Go:** the walk sector reaches the induction phase change in ≤ 60% of the tokens softmax needs, on
  three seeds.
- **No-go means:** the walk sector's one-layer lookups are not what limits in-context learning
  early on. Drop the sample-efficiency claim.

### S3. Depth substitution (cap $40; runs if S0 or S1 passes)

- Compare L softmax layers against L/2 free-field layers, and other pairings, at equal FLOPs, for
  L = 4, 8, 12.
- **Go:** a free-field model with half the layers is within 0.5% of the deeper softmax model's loss
  at equal FLOPs. That is a latency win even with no loss win.

### S4. Data where leap content is higher (cap $50; runs if S1 shows a capability gap)

- Code (a Python subset such as codeparrot-clean) and arithmetic text, against FineWeb-Edu at the
  same scale.
- **Go:** the free-field advantage, if any, is at least twice as large on code or arithmetic as on
  prose. That confirms Prediction 1 and tells us where to scale.

### S5. Confirmation at scale (cap $150 plus a kernel; only after a go in S0, S3 or S4)

- Two larger scales (about 60M and 150M non-embedding), with a fused kernel so the FLOP
  comparison is honest in wall clock as well. This is the result the paper would lead with.

## 6. Why this is fail-safe

- **Bounded cost.** S0, S1 and S2 cost about $125 together and settle the main question: is there a
  language regime where the layer helps, and through which lever?
- **Useful either way.** A no-go at every stage still gives the paper a clean, defensible scope: a
  layer for relations among many tokens, a map of where pairwise attention runs out, and an
  explanation of why language gains are small (low leap content). That is publishable alongside the
  theory, Newton attention's mechanism results and the HOMA benchmark.
- **A go is cheap to confirm.** S3 to S5 only run behind a gate, at scales chosen by the stage that
  passed.

## 7. What the app shows meanwhile

Nothing from free-field attention yet. Learn, Compare and the report keep Newton attention as the
layer and the formalism as theory in progress. The first gate that passes earns an Explore view (most
likely the walk sector forming an induction circuit live) and a report section.

## 8. Results

Run on 19 October 2026 with `research/lm.py` (token models), `research/diag.py` (S1) and the grids
`tok_*` and `diag_*` in `research/modal_run.py`; raw rows in `research/results/`. Brute-force tests
for every new piece (power sums, causal walks, look-back keys, causality of the whole model) are in
`research/test_sfa.py`.

### 8.0 Pre-registration (written before any S0, S1 or S2 result came in)

**Common.** GPT-2 tokens, context 512, batch 64 x 512 tokens, AdamW (weight decay 0.1), warmup then
cosine to 10%, bf16 matmuls with float32 accumulation, power sums in full float32. Held-out loss on
128 fixed sequences. FLOPs per token are counted analytically for what each layer must compute
(`lm.flops_per_token`: projections, MLP, causal QK and AV, every power-sum pass, the Newton recursion,
read-outs, walk and look-back passes, the LM head); training FLOPs are three times forward. Data order
is fixed by the seed and shared by every model at that seed.

**S0 models** (width 512, 8 heads, about 19M non-embedding parameters):

| Model | Layers | Non-embedding params | FLOPs per token | vs softmax |
| --- | --- | --- | --- | --- |
| softmax | 6 | 18.9M | 92.5M | 1.000 |
| free-field, equal parameters (K = 4, rank 32, mu = 0.05, arities 2..4 off at init, one read-out) | 6 | 18.9M | 97.6M | 1.056 |
| free-field, equal FLOPs | 5 | 15.8M | 89.9M | 0.972 |
| softmax + 1 layer (depth reference) | 7 | 22.1M | 99.3M | 1.074 |

Learning rates {1e-3, 2e-3, 4e-3} at 100M tokens, seed 0, per architecture and corpus; then three seeds
at each one's best rate for 400M tokens. **Go:** free-field at equal FLOPs (5 layers, 0.97x) reaches a
held-out loss at least 1% below softmax (6 layers) on 3/3 seeds, on either corpus. Also reported: every
model's loss against training FLOPs, and the free-field 6-layer model against the softmax frontier
interpolated between 6 and 7 layers.

**S1** (`diag.py`): ten tasks in six families (recall: MQAR and composite-key MQAR; copying and
induction: selective copying, induction with distractors; p-hop at 4, 8, 16; Dyck-2; 10-digit
addition; Match-3 over a token vocabulary), one and two layers, three seeds, 3,000 steps at one
learning rate (3e-3) for every model. Free-field models have width 128; each softmax baseline is
widened until its FLOPs per token match the free-field model it is compared with (`softmax` against
free-field, `softmaxw` and `lookback` against free-field with walks). **Go:** a free-field model beats
its FLOP-matched softmax by at least 10 points on at least two families, mean of three seeds.

**S2** (TinyStories, 100M tokens, evaluation every 50 steps early on): softmax; softmax with look-back
keys (the control for the walk sector's key hop); free-field; free-field with walks (look-back keys and
A^2 V). Two induction measures: the repeated-random-token gap (loss on a first copy of 256 random
tokens minus loss on its second copy) and the in-context score (held-out loss at token 50 minus loss at
token 500). **Phase-change point:** the first evaluation at which a measure reaches half of the softmax
run's final value at the same seed. **Go:** free-field with walks reaches it in at most 60% of softmax's
tokens on 3/3 seeds, on the repeated-token gap.

**Amendment after the S1 pilot (before the S1 grid ran).** A one-seed pilot at two layers showed
free-field with walks at 0% on addition where softmax reached 99.9%. Ablations traced it to the arity-1
term (the query's own phases), which the S0 specification leaves switched on at initialisation: it adds a
unit-scale random feature to the residual stream. With every arity off at initialisation (`--alpha0 2`,
the layer then starts as exactly softmax attention) free-field learns addition as fast as softmax. S1 uses
that initialisation; S0 and S2 keep the specified one (arities 2..4 off), so the language results test
the design as written.


### 8.1 Summary

| Stage | Gate | Result | Headline |
| --- | --- | --- | --- |
| S0, token LM | free-field at equal FLOPs >= 1% below softmax, 3/3 seeds | **No-go** | FineWeb-Edu, 400M tokens: free-field at 0.97x FLOPs is 2.2% worse (0.8% worse with every arity off at init); at equal parameters 1.1% worse for 5.6% more FLOPs. TinyStories, 100M: 4.3% worse. |
| S1, diagnostic map | a free-field model >= 10 points over its FLOP-matched softmax on >= 2 families | **Go as registered, but explained by the control** | Free-field with walks wins recall (MQAR 97% vs 2%), copying/induction and one addition cell; softmax with the same look-back keys and no free-field sectors does as well or better everywhere. Subsets alone win nothing. |
| S2, induction timing | walks reach the induction phase change in <= 60% of softmax's tokens, 3/3 seeds | **No-go** | FineWeb-Edu: free-field with walks gets there in 1.10-1.23x softmax's tokens (later); without walks 1.20-1.45x. TinyStories has no measurable induction. |

**Spend:** about $64 of Modal GPU time at list prices (S0 $36 including the sweep, S1 $8, S2 $19, timing and
tokenisation under $1), against a cap of $125.

**Reading.** Moving from bytes to GPT-2 tokens does not change the answer at this scale: the subset
sectors cost loss at equal FLOPs, and the gap grows with training (free-field 5L: +1.2% at 100M tokens,
+2.2% at 400M). The one mechanism that produces a large capability gap in small models is the look-back
key hop, which lets a single layer form an induction head; it works just as well in plain softmax
attention, it is close to known short-convolution or key-shift layers, and on language it does not lower
the loss either (FineWeb-Edu at 100M tokens: 4.094 against softmax's 4.074). The arity sectors' native
territory (Match-3 over a token vocabulary) is not learned by any model at this width and budget; the
clean Match-k results needed about 1,000 channels and twice the steps.

### 8.2 S0: token-level language models

**S0 learning-rate sweep** (100M tokens, seed 0; held-out loss in nats per token, best rate in bold)

| Corpus | Model | lr 0.001 | lr 0.002 | lr 0.004 |
|---|---|---|---|---|
| fineweb_edu | free-field 5L | 4.2294 | 4.1434 | **4.1376** |
| fineweb_edu | free-field 6L | 4.1995 | 4.1152 | **4.1006** |
| fineweb_edu | softmax 6L | 4.1825 | 4.0903 | **4.0868** |
| fineweb_edu | softmax 7L | 4.1713 | **4.0754** | 4.0840 |
| tinystories | free-field 5L | 1.4955 | 1.4411 | **1.4410** |
| tinystories | free-field 6L | 1.4699 | **1.4205** | 1.4262 |
| tinystories | softmax 6L | 1.4201 | **1.3817** | 1.3884 |
| tinystories | softmax 7L | 1.4040 | **1.3678** | 1.7575 |

Best loss relative to softmax 6L at 100M tokens: fineweb_edu free-field 5L: +1.24%; fineweb_edu free-field 6L: +0.34%; fineweb_edu softmax 7L: -0.28%; tinystories free-field 5L: +4.29%; tinystories free-field 6L: +2.81%; tinystories softmax 7L: -1.01%

**S0 at 400M tokens, FineWeb-Edu** (three seeds; loss mean, then each seed; FLOPs relative to softmax 6L)

| Model | Non-embedding | Training FLOPs | x softmax | Rate | Loss (mean) | Seeds | vs softmax 6L, per seed |
|---|---|---|---|---|---|---|---|
| free-field 5L | 15.8M | 1.08e+17 | 0.972 | 0.004 | 3.7635 | 3.7604, 3.7614, 3.7686 | +2.05%, +2.24%, +2.20% |
| free-field 5L, all arities off at init | 15.8M | 1.08e+17 | 0.972 | 0.004 | 3.7144 | 3.7184, 3.7074, 3.7174 | +0.91%, +0.77%, +0.81% |
| softmax 6L | 18.9M | 1.11e+17 | 1.000 | 0.004 | 3.6838 | 3.6848, 3.6790, 3.6875 | +0.00%, +0.00%, +0.00% |
| free-field 6L | 18.9M | 1.17e+17 | 1.056 | 0.004 | 3.7249 | 3.7253, 3.7244, 3.7250 | +1.10%, +1.23%, +1.02% |
| softmax 7L | 22.1M | 1.19e+17 | 1.074 | 0.002 | 3.6693 | 3.6751, 3.6667, 3.6662 | -0.26%, -0.33%, -0.58% |

Free-field 6L against the softmax frontier interpolated to its FLOPs: seed 0 +1.30%, seed 1 +1.49%, seed 2 +1.46%

Gate (free-field 5L at 0.97x FLOPs, >= 1% below softmax 6L on 3/3 seeds): NO-GO (0/3 seeds)

Gate (free-field 5L, all arities off at init at 0.97x FLOPs, >= 1% below softmax 6L on 3/3 seeds): NO-GO (0/3 seeds)

TinyStories was settled at the sweep (free-field 2.8% behind at 6 layers and 4.3% at 5 layers, each at its
best rate, and behind at every rate tried), so the
three-seed confirmation ran on FineWeb-Edu only, the corpus where the models were closest. The
all-arities-off initialisation (the S1 amendment) is the better free-field design on language too: it
removes 60% of the gap at 5 layers. It still loses on every seed.

### 8.3 S1: diagnostic map

**S1 diagnostic map** (accuracy on answer positions, mean of seeds with min-max; balanced for Match-3, whole sums for addition; ff vs softmax and ffw vs softmaxw/lookback are FLOP-matched)

| Task | Layers | softmax | ff | softmaxw | lookback | ffw |
|---|---|---|---|---|---|---|
| mqar | 1 | 2.1 (2-2) | 2.0 (2-2) | 2.2 (2-2) | 100.0 (100-100) | 96.9 (94-100) |
| mqar | 2 | 2.6 (3-3) | 2.5 (2-3) | 2.8 (3-3) | 99.0 (97-100) | 67.5 (3-100) |
| mqar2 | 1 | 2.9 (3-3) | 3.3 (3-3) | 3.3 (3-4) | 31.4 (29-33) | 31.6 (29-33) |
| mqar2 | 2 | 3.8 (4-4) | 3.7 (4-4) | 3.9 (4-4) | 32.6 (33-33) | 32.4 (32-33) |
| selcopy | 1 | 43.9 (44-44) | 53.1 (52-54) | 44.5 (44-45) | 99.9 (100-100) | 99.9 (100-100) |
| selcopy | 2 | 98.9 (98-100) | 98.9 (99-99) | 97.5 (95-99) | 99.9 (100-100) | 99.9 (100-100) |
| indist | 1 | 0.7 (1-1) | 0.8 (1-1) | 0.6 (1-1) | 23.8 (1-50) | 17.7 (1-26) |
| indist | 2 | 0.6 (1-1) | 0.6 (1-1) | 0.5 (0-1) | 0.6 (1-1) | 1.1 (0-2) |
| phop4 | 1 | 5.6 (5-6) | 5.2 (4-6) | 3.9 (3-6) | 4.3 (3-6) | 5.5 (4-7) |
| phop4 | 2 | 2.8 (2-3) | 2.5 (1-3) | 2.0 (1-4) | 2.0 (1-3) | 1.6 (1-2) |
| phop8 | 1 | 4.5 (3-7) | 7.7 (6-9) | 4.9 (5-5) | 3.8 (2-5) | 6.1 (4-8) |
| phop8 | 2 | 2.0 (2-2) | 3.0 (2-4) | 2.4 (2-3) | 3.2 (1-5) | 3.5 (2-5) |
| phop16 | 1 | 6.4 (5-8) | 7.4 (7-8) | 6.3 (4-8) | 4.5 (3-6) | 5.9 (5-6) |
| phop16 | 2 | 3.7 (2-5) | 2.4 (2-3) | 2.9 (2-3) | 2.8 (2-3) | 4.1 (3-5) |
| dyck2 | 1 | 96.8 (96-98) | 97.2 (97-98) | 97.4 (97-98) | 97.8 (98-98) | 98.8 (99-99) |
| dyck2 | 2 | 100.0 (100-100) | 100.0 (100-100) | 100.0 (100-100) | 100.0 (100-100) | 100.0 (100-100) |
| add | 1 | 66.7 (0-100) | 33.3 (0-100) | 62.2 (14-98) | 66.5 (0-100) | 33.8 (0-100) |
| add | 2 | 66.7 (0-100) | 33.6 (0-100) | 14.7 (0-29) | 4.6 (0-12) | 66.7 (0-100) |
| match3 | 1 | 75.6 (75-76) | 75.6 (75-76) | 75.6 (75-76) | 75.6 (75-76) | 75.6 (75-76) |
| match3 | 2 | 75.6 (75-76) | 75.6 (75-76) | 75.6 (75-76) | 75.6 (75-76) | 75.6 (75-76) |

Families where a free-field model beats its FLOP-matched softmax by >= 10 points: recall: mqar 1L ffw, mqar 2L ffw, mqar2 1L ffw, mqar2 2L ffw; copy/induction: indist 1L ffw, selcopy 1L ffw; addition: add 2L ffw
Gate (>= 2 families): GO
Where free-field with walks and the look-back control differ by >= 10 points: mqar 2L: ffw 67.5 vs look-back 99.0; add 1L: ffw 33.8 vs look-back 66.5; add 2L: ffw 66.7 vs look-back 4.6

Rates used: fineweb_edu free-field 6L: 0.004; fineweb_edu free-field 6L + look-back + walks (R = 2): 0.002; fineweb_edu softmax 6L: 0.004; fineweb_edu softmax 6L + look-back: 0.002; tinystories free-field 6L: 0.002; tinystories free-field 6L + look-back + walks (R = 2): 0.002; tinystories softmax 6L: 0.002; tinystories softmax 6L + look-back: 0.002

Notes. Chance is about 1.6% on p-hop (64 tokens) and 0.0% on addition (whole sums). Addition is
bimodal for every model (each seed ends at 0% or 100%), so its differences are noise at three seeds.
Match-3 sits at 75.6% for every model and seed: a positional baseline, the relation is not learned.
p-hop is not learned by any model at 1 or 2 layers in 3,000 steps (one answer per sequence). Two-layer
softmax does not learn MQAR in this budget either (Zoology trains far longer); with look-back keys one
layer is enough. **Attribution:** comparing free-field with walks against softmax with look-back keys at
the same FLOPs, they differ by 10 points or more only on MQAR at two layers (look-back better) and on
addition (bimodal). Comparing free-field (subsets only) against softmax at equal FLOPs, no family moves by
10 points.

### 8.4 S2: does the walk sector make induction form earlier?

**S2 inductionthrough training** (100M tokens; tokens, in millions, until a measure first reaches half of softmax's final value at the same seed)


_repeated-token gap_

| Corpus | Seed | softmax final | free-field 6L | free-field 6L + look-back + walks (R = 2) | softmax 6L | softmax 6L + look-back |
|---|---|---|---|---|---|---|
| fineweb_edu | 0 | 6.836 | 41.0 | 36.0 | 31.1 | 31.1 |
| fineweb_edu | 1 | 7.569 | 39.3 | 44.2 | 36.0 | 33.3 |
| fineweb_edu | 2 | 6.286 | 47.5 | 36.0 | 32.8 | 27.9 |
| tinystories | 0 | 0.097 | 6.6 | 3.3 | 1.6 | 1.6 |
| tinystories | 1 | 0.090 | 4.2 | 3.3 | 4.2 | 1.6 |
| tinystories | 2 | 0.099 | 3.3 | 3.3 | 1.6 | 1.6 |

Gate (fineweb_edu, free-field 6L + look-back + walks (R = 2): <= 60% of softmax's tokens on 3/3 seeds): NO-GO (ratios 1.16, 1.23, 1.10)

Gate (tinystories, free-field 6L + look-back + walks (R = 2): <= 60% of softmax's tokens on 3/3 seeds): NO-GO (ratios 2.00, 0.79, 2.00)

_in-context score_

| Corpus | Seed | softmax final | free-field 6L | free-field 6L + look-back + walks (R = 2) | softmax 6L | softmax 6L + look-back |
|---|---|---|---|---|---|---|
| fineweb_edu | 0 | 0.067 | 36.0 | 33.3 | 26.2 | 29.2 |
| fineweb_edu | 1 | 0.044 | 39.3 | 33.3 | 36.0 | 37.5 |
| fineweb_edu | 2 | 0.063 | 42.6 | 36.0 | 37.5 | 36.0 |
| tinystories | 0 | -0.031 | never | never | never | never |
| tinystories | 1 | -0.027 | never | never | never | never |
| tinystories | 2 | -0.020 | never | never | never | never |

_final held-out loss at 100M tokens_

- fineweb_edu, free-field 6L: 4.1008 (4.1087, 4.0740, 4.1198)
- fineweb_edu, free-field 6L + look-back + walks (R = 2): 4.1115 (4.1108, 4.1172, 4.1065)
- fineweb_edu, softmax 6L: 4.0742 (4.0795, 4.0630, 4.0802)
- fineweb_edu, softmax 6L + look-back: 4.0939 (4.0964, 4.0955, 4.0899)
- tinystories, free-field 6L: 1.4213 (1.4232, 1.4171, 1.4235)
- tinystories, free-field 6L + look-back + walks (R = 2): 1.4169 (1.4147, 1.4152, 1.4208)
- tinystories, softmax 6L: 1.3802 (1.3806, 1.3817, 1.3783)
- tinystories, softmax 6L + look-back: 1.3799 (1.3778, 1.3865, 1.3755)

Notes. At softmax's tuned rate (4e-3) both look-back variants spiked right after warmup on FineWeb-Edu
(one softmax-with-look-back seed ended at 5.64 nats; free-field with walks at 4.39-4.57), so they were
rerun at 1e-3 and 2e-3 with three seeds (`tok_s2b`) and the tables use each model's best rate. The rate
does not explain the result: softmax at 2e-3 (sweep run, seed 0) crosses the same threshold between steps
890 and 1,017 (29-33M tokens), as at 4e-3, while free-field with walks at 2e-3 needs 36-44M. On
TinyStories the repeated-random-token gap never exceeds 0.1 nats for any model (the corpus teaches no
generic copying), and the token-50-to-500 score is negative for all models because stories are about 200
tokens long, so the two positions sit in different documents; TinyStories cannot measure this lever.

### 8.5 What this means for the search

- **S3 (depth substitution) and S4 (leap-rich data) should not run with free-field attention.** S1's
  go is real only for the look-back key hop, and that hop is not ours: one-layer induction from a key
  shift is the mechanism behind short-convolution and token-shift layers. A free-field model with half
  the layers would start 1-2% behind at equal FLOPs (S0).
- **The language question is answered for this scale and design:** no gain from bytes or tokens,
  arities off or on at initialisation, with or without walks.
- **What stands** is unchanged: the relational results (Newton attention exact on Match-3/4/5 and
  SET, keyed Match-4 among distractors, walks for pointer chasing), the characters-law explanation, and
  this negative result, which bounds the claims. If the search continues, the one untested lever with a
  theoretical reason to help is data whose leap content is high by construction (code, arithmetic
  traces) at a width large enough for the arity sectors to find their characters; S1's Match-3 row says
  that width is the first thing to fix.
