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
