# Local-regression attention: does it beat softmax, and is arity the reason?

Working note, 19 October 2026. Companion to `SEARCH.md` (the staged search; S0-S2 were a no-go for
free-field attention) and `FORMALISM.md` (subset attention, the vacuum). Two questions, one pre-registered
experiment:

1. Does a ridge local-linear attention layer beat softmax attention on token-level language modelling at
   equal FLOPs?
2. Is the layer's maximum arity the reason?

Code: `research/lm.py --arch lla` (the layer, `--chart r`), `--arch plx` (Parallax), `--opt muon`;
`research/diag.py --model lla|plx|softmaxl`; brute-force tests in `research/test_local.py`; grids
`tok_loc_*` and `diag_loc_*` in `research/modal_run.py`; tables and gates from
`research/local_summary.py`; raw rows in `research/results/{tok,diag}_loc_*.jsonl`.

## 0. Verdict

Filled in after the runs (section 7).

## 1. The layer

Fix a head and a query i with causal softmax weights $p_{ij}$, $j \le i$, $\sum_j p_{ij} = 1$. The head learns
a **chart** $R \in \mathbb R^{r\times d_h}$: keys get coordinates $c_j = R k_j$, the query $c_i = R q_i$ (this
harness has learned absolute positions and no RoPE, so the chart acts on $q$ and $k$ directly). The query fits

$$
\min_{b_0,\,b_1}\ \sum_{j\le i} p_{ij}\,\bigl\|v_j - b_0 - b_1(c_j - c_i)\bigr\|^2 + \lambda\|b_1\|^2
$$

and outputs $b_0$, the fit at the query. Softmax attention is the same problem without $b_1$
(Nadaraya-Watson, a local constant). With $m_1 = \sum_j p_{ij} c_j$, $M_2 = \sum_j p_{ij} c_j c_j^\top$ and the
covariance $C = M_2 - m_1 m_1^\top$, the normal equations give

$$
b_0 = \sum_{j\le i} p_{ij}\bigl(1 - (c_j - m_1)\cdot\rho_i\bigr)\,v_j,
\qquad \rho_i = (C + \lambda I)^{-1}(m_1 - c_i).
$$

The weights sum to one and live on the causal past; they can be negative. On query-centred moments
($\mu = m_1 - c_i$, $\Sigma = C + \mu\mu^\top$) the same weights read
$p_{ij}(1 - (c_j - c_i)\cdot\tilde\rho)/(1 - \mu\cdot\tilde\rho)$ with $\tilde\rho = (\Sigma + \lambda I)^{-1}\mu$, which
is LLA's eq. 8 (Zuo et al. 2025) with normalised weights; Sherman-Morrison turns one into the other
($\tilde\rho = \rho\,(1-\mu\cdot\tilde\rho)$, and $1 - \mu\cdot\tilde\rho = 1/(1 + \mu^\top (C+\lambda)^{-1}\mu) \in (0, 1]$). The centred form
has no denominator to guard, so the layer uses it.

**Computation** (per head): one moment pass with values $[c_j, c_j c_j^\top]$ (width $r + r(r+1)/2$), an
$r\times r$ Cholesky solve per query in float32, one score pass $\rho_i\cdot c_j$, then one $A V$ product with
the corrected weights. The chart is shifted by the first key before the moments (exact, since the fit is
translation invariant, and every query sees that key); moments and scores run at full float32 precision,
the projections and $A V$ in bf16 as in the baseline. $\lambda = \mathrm{softplus}(\cdot) + 10^{-3}$ per head.

**Initialisation.** The layer is softmax at init: output $= o_{\rm SA} + g\,(o_{\rm LLA} - o_{\rm SA})$ with a
per-head gate $g = 0$. The chart is random with coordinate scale 0.5 ($R \sim \mathcal N(0, 0.25/d_h)$), never
zero: the correction is quadratic in $R$, so $R = 0$ is a stationary point even with the gate open (checked
in the tests). $\lambda_0 = 1$. Every weight the layer shares with softmax attention is drawn exactly as in
the softmax model at the same seed, so at step 0 the two models are the same function.

**Parallax** (Zuo et al. 2026) drops the solve and learns the probe: weights
$p_{ij}(1 - t_{ij} + \bar t_i)$, $t_{ij} = \rho_i\cdot k_j$, $\rho_i = W_R x_i$ ($W_R$ is $D\times D$ with a bias, so
each head has a $d_h$-dimensional probe, as Parallax shares Q's head layout). Here $W_R = 0$ at init (softmax at
init), with no RMSNorm on $\rho$ and no RoPE (the harness has none). The published RMSNorm on $\rho$ was tried
in the design pilot (section 4.1) with its gain at zero, to keep softmax at init, and failed under AdamW.

## 2. The subset expansion

**Theorem.** For $\lambda > 0$, the local-linear output is a normalised sum over subsets $S$ of the query's
past of every size $m = 1, \dots, r+1$:

$$
o_i \;=\; \frac{\displaystyle\sum_{S}\ \lambda^{\,r+1-m}\prod_{j\in S}p_{ij}\ \mathrm{Vol}^2(S)\ f_S(c_i)}
{\displaystyle\sum_{S}\ \lambda^{\,r+1-m}\prod_{j\in S}p_{ij}\ \mathrm{Vol}^2(S)},
\qquad
\mathrm{Vol}^2(S) = \sum_{|A| = m-1}\det\bigl[\,1,\ c_{S,A} - c_{i,A}\bigr]^2 = \det(D_S D_S^\top),
$$

where $A$ runs over sets of $m-1$ chart axes, $D_S$ holds the differences $c_j - c_{j_0}$ of the members
($\mathrm{Vol}^2 = 1$ for $m = 1$; it is the squared $(m-1)$-volume of the parallelotope the members span,
$(m-1)!^2$ times the squared simplex volume), and $f_S(c_i)$ is the value at the query of the
minimum-norm affine interpolant through $\{(c_j, v_j)\}_{j\in S}$. Term by term over $(S, A)$, each pair
contributes the exact fit through $S$ in the axes $A$.

*Proof.* Absorb the ridge into $r$ pseudo-rows $\sqrt\lambda\,[0, e_k]$ with target 0 and weight the data rows
by $\sqrt{p_{ij}}$. The fit is then ordinary least squares on an $(n + r)\times(r+1)$ design, and Jacobi's
formula (Ben-Tal and Teboulle 1990; Dereziński and Warmuth's volume sampling) writes it as the
$\det^2$-weighted average of the exact fits through all $(r+1)$-row subsets. A subset with $m$ data rows
holds $r+1-m$ pseudo-rows on distinct axes $K$; Laplace expansion along them gives
$\det^2 = \lambda^{r+1-m}\prod_S p\ \det[1, u_{S, A}]^2$ with $A$ the other $m-1$ axes, and the exact fit sets
$b_{1,K} = 0$ and interpolates $S$ in the axes $A$. Summing over $A$ at fixed $S$ is Cauchy-Binet for the
weight and, for the value, the $\varepsilon \to 0$ ridge on $S$ alone, which is the minimum-norm interpolant.
$\square$ Checked by enumeration in float64 for $(n, r) \in \{(5,2), (6,3), (4,3)\}$ at $\lambda \in \{0, 0.37, 5\}$,
in both forms, sector by sector, and on the layer's own causal prefixes (`test_local.py`, errors below
$4\times10^{-14}$).

**Corollaries** (each checked numerically):

- $m = 1$ is softmax attention exactly; $\lambda \to \infty$ leaves only it, so the layer recovers softmax.
- First order in $1/\lambda$ is the **pair sector**: $o = o_{\rm SA} + \lambda^{-1}\sum_{j<l} p_j p_l |c_j - c_l|^2
  (f_{jl}(c_i) - o_{\rm SA}) + O(\lambda^{-2})$, with $f_{jl}$ the line through two keys read at the query's
  projection onto it.
- At $\lambda = 0$ only subsets of size exactly $r + 1$ carry weight: pure arity $r+1$.
- **Arity.** The largest subset has $r + 1$ members ($r + 2$ tokens counting the query; this note counts
  members, so softmax is arity 1). The chart dimension $r$ is the arity dial.
- **The vacuum.** Each pseudo-row is a token at infinity along one chart axis (the limit of a token at
  $t e_k$ with weight $\lambda/t^2$), and $\lambda$ is its fugacity: a subset with $m$ real members carries
  $r + 1 - m$ vacuum tokens at price $\lambda$ each. This is the role of the Poisson vacuum $\mu$ in
  FORMALISM.md, with one difference: here the vacuum fixes slopes, there it fixed empty factors.
- **Parallax** is a pair sector without volume selection: its correction is exactly
  $-\tfrac12\sum_{j,l}p_j p_l\,((k_j - k_l)\cdot\rho_i)(v_j - v_l)$ (checked), product weights $p_j p_l$, no
  $|c_j - c_l|^2$, a learned probe instead of $(m_1 - c_i)/\lambda$, and no sectors beyond pairs.

**What the volume buys and what it does not.** The subset weight is not additive in its members: the
volume couples the keys among themselves (a pairwise key-key term at $m = 2$, a determinant beyond). It
does not couple them through the query: the query enters selection only through $\prod_S p_{ij}$, which is
additive in log. The query-subset coupling sits in the value $f_S(c_i)$, a rational function of all $m+1$
chart points. So FORMALISM's Proposition 3 still holds in modified form (selection is additive in the query
scores, the relation lives in the value), and Theorem 1 is not escaped for selection; what is new is that
the value is an interpolant, not a channel product, and that subsets are weighted by how well they span
the chart. The squared minors $\det[1, u_{S,A}]^2$ are the squared Plücker coordinates of the subset's row
space in $\mathbb R^{r+1}$; ordinary least squares as attention (Goulet Coulombe 2025) is the $r = d$,
no-locality corner.

**Prediction.** If arity helps language at all, held-out loss falls as $r$ grows with everything else fixed.

## 3. Stage 0: tests (local, $0)

`python research/test_local.py`: 82 checks, all pass. Highlights (float64 unless noted):

| Check | Max error |
| --- | --- |
| (a) gate 0: weights equal softmax | 0 (exact) |
| (a) $\lambda = 10^9$: weights equal softmax | $9\times10^{-9}$ |
| (b) layer = explicit per-query weighted ridge solve, r = 1, 2, 4 | $2\times10^{-14}$ |
| (b) layer = closed form $p(1 - (c_j - c_i)\cdot\tilde\rho)/(1 - \mu\cdot\tilde\rho)$ | $1\times10^{-14}$ |
| (c) Jacobi on the augmented design; subset expansion in minor and volume forms, $\lambda \in \{0, 0.37, 5\}$ | $4\times10^{-14}$ |
| (c) the layer equals the expansion on causal prefixes | $4\times10^{-15}$ |
| (c) first order in $1/\lambda$ = pair sector | $2\times10^{-9}$ |
| (d) Parallax: layer = eq. 8 = $o_{\rm SA} - \Sigma_{KV}\rho$ = streaming eq. 14 (online softmax over key blocks) | $1\times10^{-15}$ |
| (e) weights on future tokens; changing token t moves no earlier output (both models) | 0 |
| init: shared weights and output identical to the softmax model at the same seed | 0 |
| float32 vs float64 weights, sharp attention, key offset 4, r = 16 | $1\times10^{-4}$ |

**FLOP counter** (`lm.flops_per_token`, forward per token, training is 3x; reproduces S0's 92,473,464 for
softmax 6L). Counted for what a fused kernel must compute. L_r: chart projections, outer products, the
moment pass, covariance, Cholesky ($r^3/3$) and the two triangular solves, and a second pass that
recomputes the scores and softmax, forms $\rho\cdot c$ and the weights (the $A V$ product is softmax's own).
Parallax: its one-pass Algorithm 1 (the $\rho$ projection, $\rho K^\top$, the composite scores and their row sum,
a second $P V$ product, the epilogue).

| Model (6 layers, width 512) | FLOPs per token | x softmax | S's tokens at equal FLOPs |
| --- | --- | --- | --- |
| S (softmax) | 92,473,464 | 1.0000 | 400.0M (12,207 steps) |
| L1 | 94,234,504 | 1.0190 | 407.6M |
| L2 | 94,346,168 | 1.0203 | 408.1M |
| L4 | 94,645,048 | 1.0235 | 409.4M |
| L8 | 95,547,704 | 1.0332 | 413.3M (12,613 steps) |
| L16 | 98,594,104 | 1.0662 | 426.5M |
| P (Parallax) | 98,817,216 | 1.0686 | 427.4M (13,044 steps) |

## 4. Pre-registration (written and committed before any Stage 1 or Stage 2 run)

### 4.1 Before freezing: timing and a design pilot

Two short grids ran before this section was frozen, to measure cost and to choose between two versions of
P (`tok_loc_time`: 200 steps of each arm, rate 4e-3, warmup 20; `tok_loc_pilot`: 1,500 steps, 49M tokens,
rate 4e-3, warmup 150, seed 0). Step times on one H100 (bf16, two micro-batches): S 0.079 s, P 0.093-0.098 s,
L8 0.117-0.120 s, L16 0.181 s.

| Pilot, 49M tokens, `val` | S | P, $W_R = 0$, no norm | P, RMSNorm on $\rho$, gain 0 | L8 |
| --- | --- | --- | --- | --- |
| AdamW | 4.7837 | 4.4762 | 6.1608 (blew up, never recovered) | 4.6275 |
| Muon | 4.1401 | 4.1628 | 4.1367 | 4.1317 |

In the 200-step run with a 20-step warmup, P without normalisation also blew up under AdamW (`val` 10.1,
correction 4-8x the softmax output); with 150 warmup steps it was stable. **Decision:** P is the
unnormalised version ($W_R = 0$), as in the brief; the RMSNorm version's zero gain moves at AdamW's full rate
and destabilises the layer at the rates this model needs (Parallax's AdamW rate is 3e-4, ours 2e-3 to 8e-3).
Under the 400-step warmup of the real runs, the sweep decides whether P survives each rate. L8's gates opened
in the pilot (mean |g| 0.15-0.6 per layer, correction-to-output ratio 0.13-0.46), so the layer is in use.
The pilot's S and L8 numbers were seen before this section was frozen; no gate was changed after them (the
gates are the brief's).

### 4.2 The registered protocol

**Model and data (S0's scale and protocol).** GPT-2 tokens, FineWeb-Edu shard (the `polyformer-data`
volume), context 512, width 512, 8 heads ($d_h = 64$), 6 layers, MLP 2048, pre-LayerNorm, GELU, learned
positions, tied embeddings; batch 64 x 512 tokens (two accumulated micro-batches), bf16 matmuls with float32
accumulation; warmup 400 steps then cosine to 10% of the peak rate; gradient clipping 1.0; data order fixed
by the seed and shared by every arm; initial weights shared with the softmax model at the same seed.

**Arms** (all softmax at init): S = softmax; P = Parallax ($W_R = 0$); L8 = ridge local-linear, $r = 8$,
chart scale 0.5, $\lambda_0 = 1$, gate 0. No other hyperparameter of the layers is tuned.

**Optimizers.** AdamW exactly as S0 ($\beta = (0.9, 0.999)$, $\epsilon = 10^{-8}$, weight decay 0.1 on every
parameter). Muon (`optax.contrib.scale_by_muon`, optax 0.2.8): Nesterov momentum 0.95, five Newton-Schulz
steps with the default quintic coefficients, Frobenius pre-scaling, Moonlight's RMS matching
(update RMS 0.2 x rate, so Muon's rates sit on AdamW's scale), decoupled weight decay 0.1, on the hidden
matrices (qkv, o, fc1, fc2, $W_R$, and each head's chart); embeddings, positions, norms, biases, gates and
$\lambda$ take the AdamW above at the same rate. Same schedule for both.

**Held-out metric.** Gates use `val_big`: mean loss in nats per token on 1,024 held-out sequences (524,288
tokens, generator seed 5678), scored once at the end of each run. `val` (S0's 128 sequences, seed 1234) is
reported for continuity, and for the curve at 100M, 200M and 400M tokens.

**Stage 1, mechanism diagnostics** (cap $10; informative, not a gate). `diag.py` tasks MQAR, composite-key
MQAR, induction with distractors, Match-3 over a vocabulary; one and two layers; arms S (`softmaxl`, gpt
widened in steps of 4 until its FLOPs per token are nearest L8's), P, L8 at width 128, 4 heads; 3 seeds;
S1's protocol (3,000 steps, rate 3e-3, warmup 5%, cosine to 5%) under both optimizers. P is at width 128;
its FLOP ratio to L8 is reported per cell. If L8 is below S by more than the seed spread anywhere, suspect
a bug before reading anything else.

**Stage 2, the language-model test** (cap $100).

1. Sweep: rates {2e-3, 4e-3, 8e-3} for each arm and optimizer, seed 0, 100M tokens (18 runs). S0 showed
   1e-3 worst for every model, so the grid moves up one octave. Best rate = lowest `val_big` at 100M.
2. Confirmation: each arm and optimizer at its best rate, seeds 0, 1, 2, 400M tokens (18 runs).
3. Equal FLOPs: S at its best rate for each optimizer, seeds 0, 1, 2, trained to 413.3M tokens (L8's FLOPs)
   and to 427.4M tokens (P's FLOPs), each with its own full schedule (12 runs). S at 400M is the
   equal-token point.
4. Harness check: S under AdamW at 4e-3 reproduces S0's 3.684 `val` (3.6838 mean, seeds 3.6848, 3.6790,
   3.6875) within the seed spread.

**Best configuration** of an arm = the optimizer (with its best rate) whose three-seed mean `val_big` at
400M is lowest; for S at a matched point, the optimizer with the lower mean at that point.

**Gates** (per seed s; same seed = same data order and shared initial weights):

- **Headline go:** L8's best configuration beats S's best configuration at L8's FLOPs by at least 1%,
  $\mathrm{L8}(s) \le 0.99\,\mathrm{S}_{413M}(s)$, on 3 of 3 seeds. Equal-token results (S at 400M) are reported
  beside it.
- **Ours vs prior art:** L8's best configuration below P's best configuration on 3 of 3 seeds, both at
  400M tokens. L8 then also uses 3.3% fewer FLOPs, so a win counts at equal FLOPs; a loss is reported with
  S's measured loss-per-FLOP slope (S at 400M against S at 427.4M) to say whether it survives the FLOP
  difference. If L8 beats P: the exact solve and the volume selection matter. If only P beats S, that is a
  small-scale replication of Parallax and is reported as such. P against S is scored at P's FLOPs
  (S at 427.4M), with any margin and with 1%.
- **No-go at Stage 2:** the headline gate fails. Then stop: write it up here and as a new section of
  SEARCH.md, with a recommendation.

**Stage 3** (only after a headline go).

- **Arity ladder** (cap $25): L1, L2, L4, L16 at 400M tokens, seed 0, L8's best optimizer and rate (the
  L8 run is seed 0 of Stage 2). **Arity lever:** `val_big` falls monotonically in r from 1 to 8 and by at
  least 0.5% in total (L1 to L8). L16 is reported.
- **Leap content** (cap $25): a codeparrot-clean subset tokenised like FineWeb-Edu; S and L8 at their
  FineWeb-Edu best configurations, 400M tokens (S also at L8's FLOPs), 3 seeds. **Go** if the L8 - S gap
  (relative, equal FLOPs) on code is at least twice the FineWeb-Edu gap.

**Diagnostics reported for every L and P run** (not gates): the gates $g$ per head and layer, $\lambda$,
chart norm, $\|W_R\|$, the correction-to-output ratio $\|o - o_{\rm SA}\| / \|o_{\rm SA}\|$ per layer
(Parallax's COR) and the range of the corrected weights, on 8 held-out sequences.

**Total cap $150**; a stage that would exceed its cap stops and is reported. Estimated from the measured
step times (H100 $3.95/h, L4 $0.80/h, plus 10% for container start): timing and pilot $2.9 (spent), Stage 1
about $4, Stage 2 about $50 (sweep $8, confirmation $27, S at equal FLOPs $15), Stage 3 about $20.

## 5. Confounds fixed in advance

- **Scale.** 19M non-embedding parameters and 400M tokens; Parallax's gains were at 0.6B-1.7B and 79-157B
  tokens. A null here bounds the effect at this scale only.
- **Positions.** No RoPE (learned absolute positions, as S0); Parallax found RoPE on $\rho$ helps.
- **Muon recipe.** RMS-matched Muon with the AdamW part at the same rate and S0's cosine schedule, not
  Parallax's spectral scaling, WSD schedule and 0.3x / 0.015x embedding and norm rates.
- **The chart.** L uses a learned $r$-dimensional chart per head; LLA regresses on the full head
  dimension. $\lambda$ is per head, not data dependent (LLA's appendix uses $\mathrm{sigmoid}(W_\lambda x)$).
- **Initialisation.** P starts at $W_R = 0$ and L with its gate closed, so both start as softmax; published
  Parallax starts with a random probe and normalised $\rho$.
- **FLOPs, not wall clock.** The JAX implementation materialises the weights; FLOPs are counted for a fused
  kernel, including L's recomputation in its second pass.
- **Parameters.** P adds 0.26M parameters per layer (1.6M in all, +8%); L8 adds 0.004M per layer.
