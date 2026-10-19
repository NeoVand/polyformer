# Free-field attention: arity as particle number, chains as propagation

Working note, 19 October 2026. Companion to `research/PLAN.md` and the Report tab. It proposes one
formalism that keeps what works in this project (arity as Fourier degree, distinct subsets, Newton's
identities), says what it predicts for the three failures (language, chains, width), and reports the
first measurements of a prototype. Brainstormed with Astra (Codex) and Argon (Gemini); every claim of
theirs kept here was checked numerically or by hand, and the ones that did not survive are listed in
section 9.

Code: `research/polybench.py --model sfa` (subset attention, optional walk sector `--hops R`),
`research/lm.py --arch sfa` (causal version), brute-force tests in `research/test_sfa.py`, grids
`sfa_a`, `sfa_b`, `lm_sfa`, `lm_sfa_b` in `research/modal_run.py`, raw results in
`research/results/{sfa_a,sfa_b,lm_sfa,lm_sfa_b}.jsonl`.

## 0. Verdict

**The formalism is the right map, and it fixes two of the three failures; the seed idea (query-dependent
weights) earns a narrower place than hoped.** Measured, three seeds each (section 8):

- **Chains: fixed, by propagation, not by arity.** One layer with a walk sector solves pointer chasing
  (100%) and three-hop composition (95%, two seeds exact), where three softmax layers reach 100% and
  52%, Feynman attention 100% and 82%. Subset attention alone tracks softmax at equal depth and adds
  nothing; with walks present, knocking out any arity leaves chain accuracy unchanged.
- **Language: the regression is gone, no gain.** Subset attention contains softmax attention; with its
  higher arities switched off at initialisation it reaches 1.652 bpc against softmax's 1.650
  (Newton-only: 2.497). Switched on at initialisation it costs 0.017 bpc. Arity does not pay on bytes at
  3.3M parameters.
- **Selection x arity: a real but specific win.** On keyed Match-4 with a distractor curriculum,
  subset attention reaches 91.1% on the most distracted tables against Newton attention's 77.0% at
  equal width, every seed above every seed. On keyed Match-3 Newton attention's per-token gates already
  select by key (both 100% at rank 256). Without a curriculum, keyed Match-4 is a wall for every model,
  dense cubic and three softmax layers included.
- **Pure arity: selection costs a little.** Subset attention with zero-initialised queries matches
  Newton attention on Match-3, Match-4 and the smallest-arity task, but trails on Match-5 (82% vs 85% at
  rank 256, 93% vs 97.5% at rank 512). The vacuum that makes it numerically safe must stay small
  (mu = 0.05): at mu = 0.2 Match-5 falls to 63%.
- **Width: measured, not fixed.** One head needs far more channels than the 40 characters it must find
  (Match-4: 62 -> 87% from rank 32 to 256; four heads of 256 are exact). Selection does not reduce that
  on unkeyed tasks (one head of subset attention at mu = 0.2 is below Newton attention at every rank).
- **The characters law is explained**: an oracle with F exact characters and the best read-out
  reproduces it, and a Parseval argument gives its near-linear shape (section 4).

So: adopt **free-field attention** = softmax + subset sectors (small vacuum, zero-initialised queries,
higher arities off at init) + a walk sector, as the paper's layer; present selection as what makes
arity usable among distractors, walks as what chains need, and Feynman attention as the interacting
theory that cannot be trained for composed arity. It is not yet a NeurIPS paper (section 10): the
evidence is synthetic, the walk sector is close to prior art, and there is no kernel or scale story.

## 1. What the formalism has to keep and fix

Keep:

- **Arity is Fourier degree.** For a zero-sum relation on a finite abelian group the label is a sum of
  full-degree characters; uniform solutions of one linear equation in k unknowns are (k-1)-wise
  independent, so any score built from fewer than k of the tokens has equal class means (Theorem 1).
- **Distinct subsets, not tuples with repetition.** Newton attention's exactness comes from the signed
  power-sum recursion that removes repeated indices.
- **Native arity trains; composed arity does not.** Feynman attention represents Match-4 by composing
  cubic vertices and stays at chance; Newton attention, where each arity is one polynomial feature, is
  exact (the leap barrier).

Fix:

- **Language.** Newton-only LM 2.497 bpc vs softmax 1.651.
- **Chains.** Newton 62% on pointer chase, 33% on three-hop composition.
- **Width.** Unmeasured; Newton needs 4 heads x 256 complex channels where 40 characters suffice in
  principle.

The diagnosis in the Report is that Newton attention has no query-dependent selection. That is right
for language and for the keyed tasks below, but it is not what breaks chains: selection says *which*
tokens meet, chains need *a sequence* of lookups. The formalism separates the two.

## 2. The generating function

Fix a query q. Let $p_{qt} \ge 0$ be its softmax weights over the other tokens ($\sum_t p_{qt} = 1$),
and $\phi_t \in \mathbb C^r$ per-token channels with $|\phi_{t,c}| \le 1$ (in the prototype
$\phi = \sigma(g)\,e^{i\theta}$ as in Newton attention). Per channel define

$$
Z_q(z;\phi) \;=\; e^{\mu z}\prod_{t\ne q}\bigl(1 + z\,p_{qt}\,\phi_t\bigr)
\;=\;\sum_{m\ge 0} z^m\,\mathcal E_m(q;\phi),
\qquad
A_m(q) \;=\; \frac{\mathcal E_m(q;\phi)}{\mathcal E_m(q;1)} .
$$

**Subset attention** reads every arity at once: $F_m(q) = \phi_q \odot A_m(q)$ is the arity-(m+1)
feature (the query and m others), for m = 0..K-1, each RMS-normalised and read by one shared matrix
with a learned scale per arity, exactly as in Newton attention. A plain softmax read-out of linear
values, $\sum_t \mathrm{softmax}(s_q)_t v_t$, uses the same scores.

**Proposition 1 (what $A_m$ is).** With no vacuum ($\mu = 0$),

$$
A_m(q) = \mathbb E_{S\sim\pi_{q,m}}\Bigl[\prod_{t\in S}\phi_t\Bigr],
\qquad \pi_{q,m}(S) = \frac{\prod_{t\in S}p_{qt}}{e_m(p_q)},\ |S| = m,
$$

the mean channel product over distinct m-subsets drawn with probability proportional to the product of
their attention weights. $\pi_{q,m}$ is an m-DPP with diagonal L-ensemble kernel $\mathrm{diag}(p_q)$,
and equally conditional Poisson (rejective) sampling: independent Bernoulli inclusions with odds
$\lambda p_{qt}$, conditioned on $|S| = m$, for any $\lambda > 0$. With a vacuum $\mu > 0$ a subset may
also hold empty slots of value 1 at price $\mu$ each:
$\mathcal E_m = \sum_{i\le m} e_i(p\phi)\,\mu^{m-i}/(m-i)!$, so $A_m$ is a mixture of arities
$m, m-1, \dots$ weighted by $e_i(p)\,\mu^{m-i}/(m-i)!$.
*Proof.* Expand the product; $e^{\mu z}$ is the generating function of a Poisson number of empty
slots. Checked against explicit enumeration in `test_sfa.py` (float64, error < 2e-11).

**Proposition 2 (special cases).** (a) m = 1, $\mu = 0$: $A_1 = \sum_t \mathrm{softmax}_t(s_q)\phi_t$,
softmax attention (exact with linear values through the extra read-out; with the root factor
$\phi_q$ it is a query-gated attention, as Astra pointed out). (b) Uniform $p$, $\mu = 0$:
$A_m = e_m(\phi_{-q})/\binom{n-1}{m}$, Newton attention's feature up to a constant that RMS
normalisation removes; zero-initialised queries therefore start the layer *as* Newton attention.
(c) m = 2: attention over unordered distinct pairs with score $s_{qj} + s_{qk}$ and value
$\phi_j\odot\phi_k$. (d) **Not** included: cubic attention with trilinear score
$\langle q_i, k_j\odot k_k\rangle$. Its mixed difference
$g(j,k) - g(j',k) - g(j,k') + g(j',k') = \sum_a q_a(k_{ja}-k_{j'a})(k_{ka}-k_{k'a})$ is generically
nonzero, while product weights have zero mixed difference (numerically: the pair-weight matrix of a
trilinear head has singular values 1, 0.27, 0.19, ...; of an additive one 1, 0, 0). (e) Replacing
$e_m$ by the complete homogeneous $h_m$ (sign flip in the recursion) gives multisets: the bosonic
variant, repeated tokens allowed.

**Proposition 3 (where the relation lives).** Subset weights are additive in the members' scores,
$\log w(S) = \sum_{t\in S} s_{qt}$. By Theorem 1 such a score has equal class means on k-way zero-sum
relations, and since $w > 0$ the trivial-character component of $w$ is at least as large as any other. So in this
operator **scores select and values relate**: the k-way relation must live in the channel product
$\prod_{t\in S}\phi_t$, which for characters is $\chi(\sum_S x_t)$. This is a division of labour, not a
limitation to remove: a trilinear score is what makes cubic attention $O(n^3)$.

**Proposition 4 (cost).** The power sums are attention passes:
$P_j(q) = \sum_t p_{qt}^j\phi_t^j$ and $\Pi_j(q) = \sum_t p_{qt}^j$ for j = 1..K-1, then Newton's
identities $m\,\mathcal E_m = \sum_{j=1}^m (-1)^{j-1}\mathcal E_{m-j}\tilde P_j$ with
$\tilde P_1 = P_1 + \mu$, $\tilde P_{j\ge2} = P_j$ (the vacuum is a shift of the first power sum, no
other change). With FlashAttention: a pass at logits $j s$ with values $\phi^j$ returns the normalised
output $o_j$ and $\ell_j = \log\sum_t e^{j s_{qt}}$; then $P_j = o_j\,e^{\ell_j - j\ell_1}$ and
$\Pi_j = e^{\ell_j - j\ell_1}$. Using $o_j$ without the partition functions is wrong (both partners
flagged this). Cost per head: one softmax pass plus K-1 passes of value width 2r, plus $O(K^2 r)$ per
query for the recursion; memory as FlashAttention. **The power-sum matmuls must run at full float32
precision**: TF32 (JAX's default on Ampere and later) keeps 10 mantissa bits and destroys the
cancellations.

**Proposition 5 (numerics, and why the vacuum).** Without a vacuum, Newton's identities from float32
power sums are ill-conditioned when attention is sharp: the condition number grows like
$\prod_{a=2}^m p_{(1)}/p_{(a)}$, and the information is already gone in the rounded power sums
(Astra's example: $w = (1, 10^{-8})$ gives $P_1 = P_2 = 1$ in float32, so $e_2 = 0$ instead of
$10^{-8}$). Measured (scratch stability runs over one-hot, few-hot and geometric weights, logits capped at 5
or 8): errors reach order 1, or NaN, from arity 4 at n = 7 and from arity 5-6 at n = 256; capping the
logits only moves the threshold. `test_sfa.py` has a sharp-attention case. With the vacuum,
$\mathcal E_m(q;1) \ge \mu^m/m!$ while every term of the recursion is bounded by about
$(1+\mu)^m/m!$, so

$$ \bigl|\widehat A_m - A_m\bigr| \;\lesssim\; c_m\,\varepsilon_{32}\,\Bigl(\tfrac{1+\mu}{\mu}\Bigr)^m $$

uniformly in the logits (a forward-error sketch: $c_m$ absorbs error propagation through the
recursion). Measured worst case over one-hot, few-hot and geometric weights, n = 7..256, K = 6:
$4\times10^{-3}$ at $\mu = 0.1$, $6\times10^{-5}$ at $\mu = 0.3$; the test suite's sharp-attention
case gives $2.3\times10^{-4}$ at $\mu = 0.2$ against $1.1$ without the vacuum. The vacuum also
defines the read-out where fewer than m tokens are available (the first positions of a causal
sequence, or a query that selects two tokens): the subset fills with empty slots and the feature
degrades to a lower arity, instead of being forced through m-1 runner-up tokens of negligible weight.
**Its price is arity purity**: with uniform weights the arity-(m+1) feature is roughly a fraction
$1/(1+\mu m)$ pure (section 8 measures what that costs). The exact alternative, $\mu = 0$ with a
subtraction-free evaluator (the recurrence $E_m \leftarrow E_m + x_t E_{m-1}$, or its balanced product
tree / an online Chu-Vandermonde merge inside a FlashAttention-style kernel), has error
$\le \gamma_{2n}\,e_m(|x|)$ independent of the logits but needs a fused kernel; in plain JAX it
materialises $n^2 r$ values per pass. Gradient bound (exponential-family identity, $\mu = 0$):
$\partial A_m/\partial s_{qt} = \mathrm{Cov}_{\pi_{q,m}}\bigl(\prod_S\phi, \mathbf 1\{t\in S\}\bigr)$, of
modulus at most 1/2.

**Proposition 6 (causal and streaming).** Restrict t to the strict past; everything is unchanged and
the vacuum handles positions with fewer than m predecessors (position 0 reads $A_m = 1$). Decoding
costs K attention passes over the KV cache per token, like K heads. Exact *linear-time* versions need
the j-th power sum to use exactly the j-th power of one weight (independent kernels per power break
the distinctness cancellation by $\sum_t (w_t^2 - \tilde w^{(2)}_t)\phi_t^2$ at m = 2). For a rank-R
kernel $w_{qt} = \langle a_q, b_t\rangle$, $w^j = \langle a_q^{\otimes j}, b_t^{\otimes j}\rangle$
and the sufficient state is $(r+1)\bigl[\binom{R+K-1}{K-1} - 1\bigr]$ numbers (58,904 per channel at
R = 32, K = 5); a rank-1 kernel collapses to Newton attention with a per-arity query scale $a_q^m$.
So selection in linear time costs symmetric tensor powers, as in polynomial linear attention.

## 3. Walks: the propagation sector

Subsets answer "which tokens, taken together, satisfy a relation"; chains ask "where do I end up after
following pointers". A product weight has no factor $\mathrm{match}(\mathrm{next}(t_1),\mathrm{id}(t_2))$;
higher-rank channel products can encode such a relation only through its symmetrisation, at width
growing like (domain size)^(hops), and cannot orient it. Determinants do not help either: $L$ and
$L^\top$ have the same principal minors, and for $L = I + T$ with T strictly triangular every
principal minor is 1, so a determinantal subset law cannot see a forward chain at all (Astra).

Chains are the propagator of the same free theory. Let $A^{(\ell)}$ be row-stochastic hop matrices
(softmax over all tokens, self-loops allowed so terminals absorb). The walk sector reads

$$ W_\ell(q) = \bigl[A^{(1)}A^{(2)}\cdots A^{(\ell)}\,V\bigr]_q,\qquad \ell = 1..R, $$

the value where a walker starting at q stands after $\ell$ hops; with tied $A^{(\ell)} = A$ it is
$a_q^\top A^{\ell} V$, the coefficients of $a_q^\top(I-uA)^{-1}V$. Cost $O(R n^2 d)$ given the hops
($O(R n^3)$ in the prototype, which forms the products for all queries; fine at n < 32).

**One generating functional.** With $X_q = \mathrm{diag}(p_q\phi)$,

$$
\mathcal Z_q(z,u,\eta) = e^{\mu z}\,\frac{\det\bigl(I - uA + zX_q + \eta\,v a_q^\top\bigr)}{\det(I-uA)} ,
$$

has (i) at u = eta = 0 the subset generating function $e^{\mu z}\prod_t(1+zp_{qt}\phi_t)$ (particle
number m = arity), (ii) at z = 0 the walk sector as a source derivative,
$\partial_\eta\log\mathcal Z|_{\eta=0} = a_q^\top(I-uA)^{-1}v$ (Jacobi's formula), and (iii) mixed
sectors $\det\bigl(I + zX_q(I-uA)^{-1}\bigr) = \sum_S z^{|S|}\prod_{t\in S}x_t\,\det(G_S)$ that weight
subsets by minors of the walk Green's function $G = (I-uA)^{-1}$; we have not studied them. The
logarithm is the linked-cluster expansion: $\log\det(I+zX) = \sum_j (-1)^{j-1} z^j\,\mathrm{tr}(X^j)/j$,
fermion loops of length j, which on the diagonal are exactly the power sums Newton's identities use.

| Sector | What it is |
| --- | --- |
| one particle, no hops | softmax attention |
| m particles, no hops, uniform weights, no vacuum | Newton attention |
| m particles, no hops | subset attention (this note) |
| 2 particles, trilinear score | **not** a sector: cubic attention is an interaction |
| no particles, R hops, one source | walk attention (pointer chase, composition) |
| repeated indices, $\det(I-zX)^{-1}$ | bosonic / permanental variant |
| non-diagonal symmetric kernel | DPP attention: exclusion by content, $O(nR^2 + KR^3)$ per query per channel (rank-R kernel) |
| tree-level Dyson-Schwinger recursion | Feynman attention: the *interacting* theory |

The organising claim, which the measurements in section 8 support: **the free sectors (subsets,
walks) are exactly summable, and each arity or hop reaches the read-out as one feature; the interacting
sector (Feynman attention) can represent everything but composes arity through shared
intermediates, which hits the leap barrier.** Free-field attention is the layer that offers all the
free sectors side by side, with one read-out.

## 4. The characters law, explained

Observed: across 74 Match-k runs, balanced accuracy is within 5 points of 1/2 + F/80, where F is the
number of the 40 conjugate character pairs of $\mathbb Z_3^4$ found by the layer.

**Oracle test (new).** Exact character features $f_a(i) = \mathrm{Re}\bigl(\chi_a(x_i)\,e_{k-1}(\chi_a(x_{-i}))\bigr)$
for all 40 pairs (their sum with the constant term reproduces every label exactly), keep a random F of
them, fit the best read-out on 6,000 tables, score on 3,000 held-out tables (`research/charlaw.py`):

| F | 4 | 8 | 12 | 16 | 20 | 24 | 28 | 32 | 36 | 40 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1/2 + F/80 | .550 | .600 | .650 | .700 | .750 | .800 | .850 | .900 | .950 | 1 |
| Match-4, equal-weight sum | .603 | .655 | .699 | .738 | .779 | .821 | .864 | .919 | .966 | 1 |
| Match-4, logistic | .601 | .654 | .699 | .738 | .779 | .820 | .864 | .918 | .965 | 1 |
| Match-4, MLP (256 hidden) | .600 | .651 | .690 | .720 | .755 | .795 | .845 | .907 | .969 | 1 |
| Match-3, logistic | .606 | .658 | .699 | .740 | .782 | .823 | .868 | .924 | .977 | 1 |

So the law is a property of **pooled character sums under any read-out**, not of training dynamics:
an MLP does no better than an equal-weight sum, and exact accuracy needs every pair. (For an isolated
tuple four independent characters suffice with an AND rule, BA = 1 - (3^{4-d}-1)/160 for d
independent characters, so the "all 40" requirement comes from pooling over many subsets.)

**Derivation (Argon, checked).** Let $c_a(s) = \mathrm{Re}\,\chi_a(s) \in \{1, -1/2\}$. Character
orthogonality gives $\sum_{s\in G} c_a c_b = \tfrac{81}{2}\delta_{ab}$, hence over the 80 non-zero sums,
for any set C of F pairs and $S_C = \sum_{a\in C} c_a$: mean $-F/80$ and variance
$81F(40-F)/6400$, depending on F only. A positive card adds one zero sum ($S_C = F$) to a background of
M subsets; treating the background as M independent non-zero sums,
$d' = \tfrac{9}{\sqrt M}\sqrt{F/(40-F)}$ and $\mathrm{BA} \approx \Phi\bigl(\alpha\sqrt{F/(40-F)}\bigr)$ with
$\alpha = 9/(2\sqrt M)$. The finite-population factor $1/(40-F)$ bends the Gaussian CDF into a near
line. Fit to the oracle: with $\alpha$ fitted, max deviation 1.8 points (Match-4) and 1.2 points
(Match-3); with $\alpha$ from the nominal $M = \binom{n-1}{k-1}$ (56, 55) it is 5.3-5.4 points (the
fitted values correspond to $M_{\rm eff} \approx 35$-39, because subsets share tokens and labels are
existential). The linear law itself is off the oracle by up to 5.9 points. Status: functional form
verified, constant open. This turns an unexplained correlation into a short theorem plus one
measured constant, and it predicts that at fixed F accuracy falls with n as $\binom{n-1}{k-1}^{-1/2}$
inside $\Phi$ (a zero-cost test on existing checkpoints).

## 5. Width

- **Representation (exact).** $C_{q,k} = \frac1{|G|}\sum_{\chi}\chi(x_q)\,e_{k-1}(\chi(x_{-q}))$, so
  $(|G|-1)/2$ complex channels plus a constant suffice for every k at once on odd-order groups:
  oracle width is independent of arity.
- **Lower bound (bilinear).** $H_{x,y} = \mathbf 1\{x+y=0\} - 1/|G|$ has rank $|G|-1$, so an exact
  bilinear factorisation needs $|G|-1$ real dimensions. It does not bound thresholded or non-linear
  read-outs.
- **Learned width (measured, section 8).** One head on Match-4: Newton attention 62 / 70 / 75 / 87%
  at rank 32 / 64 / 128 / 256 (three seeds); four heads of 256 are exact. So learned width is roughly
  10-25x the oracle 40, and subset attention with a vacuum of 0.2 is below Newton attention at every
  rank (56 / 65 / 72 / 77%). Hypothesis (both partners): channels discover character pairs roughly like
  coupons, $r \gtrsim (P/p_k)\log(P/\delta)$ with $P = 40$ and a per-channel discovery rate $p_k$
  that falls with k; trained layers show about one channel in eleven is a character.
- **Selection divides width by the number of keys.** On keyed tasks a query-independent layer must
  carry the characters once per key (gates can confine a channel to one key); subset attention
  carries them once and selects by score. Measured: on keyed Match-3 both reach 100% at rank 256
  (93% vs 90% at rank 64, within seed spread), so four heads of 256 already hold three keys' worth of
  characters; under heavier distraction (keyed Match-4, seven distractor cards) selection is worth 14
  points at rank 256.

## 6. Predictions for the three failures

Written while the first grid was running; the first language and chain results were in by then, the
keyed, width and curriculum results were not. Outcomes are in section 8.

| Failure | Mechanism in the formalism | Prediction |
| --- | --- | --- |
| Language | the one-particle sector is softmax attention; subsets add conjunctions of attended tokens | closes the Newton-only gap (2.50 bpc) to within a few hundredths of softmax; no reliable gain at 3.3M params; arity >= 2 helps only if the data has multi-token conjunctions softmax+MLP cannot form |
| Chains | walk sector; arity and depth of subset attention do not compose pointers | one layer with R hops solves pointer chase and three-hop composition; subset attention alone tracks softmax at equal depth |
| Width | oracle (G-1)/2 for every k; selection removes the per-key factor | learned width far above oracle; on keyed tasks subset attention needs fewer channels than Newton attention |
| Arity purity | vacuum mixes lower arities in | small or zero vacuum on pure-arity tasks; vacuum where attention is sharp (LM, keyed) |
| Exclusion | fermions remove repeated tokens; bosons do not | bosonic variant fails Match-4 (it counts $x_q + 2x_t + x_u$, which can vanish) |

## 7. Falsifiable plan with go / no-go

Each line: experiment, go criterion, what a no-go means.

1. **Selection + arity (the decisive test).** Keyed Match-k with a distractor curriculum (`kd4`):
   go if subset attention beats Newton attention by >= 10 points at the most distracted level
   (d = 7) on 3/3 seeds at equal width. No-go: selection does not buy width, and the paper should
   present Newton + walks without the selection claim.
2. **Arity retention.** Subset attention with zero-initialised queries and $\mu \le 0.05$ matches
   Newton attention on Match-3/4/5 and smallest-arity within 2 points (3 seeds). No-go: selection
   interferes with character learning; keep the uniform layer for relations.
3. **Chains in one layer.** Walk sector reaches >= 95% on pointer chase and three-hop composition on
   3/3 seeds, against softmax at 1-3 layers and Feynman attention. Then p-hop (p = 16) and CLUTRR.
   No-go on p-hop: propagation length does not extrapolate; report as a limitation.
4. **Language.** Subset attention with arities 2..K initialised off (`--alpha0 1`) is within 0.01 bpc
   of softmax at 3.3M and scale-up to ~20M/enwik8 or OpenWebText bytes; go if it improves bpc by
   >= 0.01 on 3 seeds at any scale, else report "contains softmax, no gain" and drop LM claims.
5. **Characters law.** Evaluate existing checkpoints at n = 8..32 cards: go if accuracy at fixed F
   follows $\Phi(\alpha\sqrt{F/(40-F)}\,/\sqrt{M(n)/M(n_0)})$ within 3 points.
6. **Width.** Groups $\mathbb Z_3^d$, d = 2..5, k = 3..5, rank ratio $r/P$ in {0.5 .. 8}, with planted
   characters, random frozen channels and learned channels: go if planted width is P for every k and
   learned width follows the coupon-collector curve; this is the scaling figure a reviewer will ask
   for.
7. **Systems.** A fused kernel (FlashAttention with K power-sum outputs, or the subtraction-free
   merge) within 1.5x of K softmax heads in wall clock at n = 4k.

## 8. First measurements

One layer, width 64, four heads, three seeds, unless noted. Balanced accuracy (chance 50%) except the
chain tasks (accuracy over eight answers, chance 12.5%). Raw rows in `research/results/`; tables from
`python3 research/summarize.py <grid> --print`. Total cost of the four grids: about 14 GPU-hours,
$13-15 on Modal.

**8.1 Selection x arity (`sfa_a`, `sfa_b`).** Keyed Match-3: 3 keys x 10 cards, zero sums count only
within a key (61% of cards sit in a cross-key zero sum that does not count). Keyed Match-4: 2 keys x 8
cards. Curriculum (`kd4`): 9 cards with key 0, d ~ U{0..7} distractor cards with key 1, padding for the
rest; 10,000 steps; scored on d = 0, 3, 7 separately.

| Model | Keyed Match-3 | Keyed Match-4 | Curriculum, all | d = 0 | d = 7 |
| --- | --- | --- | --- | --- | --- |
| Subset attention, rank 256, mu 0.2 / 0.05 (curriculum) | **100.0** (100-100) | 54.3 (50-56) | **90.4** (89-92) | 87.2 | **91.1** (89-93) |
| Subset attention, rank 256, mu 0 | | | 86.8 (86-87) | 82.9 | 85.5 |
| Newton attention, rank 256 | **100.0** (100-100) | 50.9 (50-53) | 82.1 (75-88) | 79.7 | 77.0 (71-83) |
| Subset attention, rank 64 | 92.9 (87-96) | 50.0 | | | |
| Newton attention, rank 64 | 89.8 (88-93) | 50.0 | | | |
| Cubic attention | 83.0 (50-100) | 50.0 | | | |
| Softmax, 3 layers | 50.0 | 50.0 | | | |

Steps to 95% on keyed Match-3 at rank 256: subset 1,800 / 2,400 / 1,800, Newton 2,400 on every seed.
Knockouts: keyed Match-3 rests on arity 3 for both (removing it gives 50-52%).

**8.2 Pure arity (`sfa_a`, `sfa_b`; Newton rows from `newton_e`).**

| Model | Match-3 | Match-4 | Match-5 | Smallest arity |
| --- | --- | --- | --- | --- |
| Newton attention, rank 256 | 100.0 | 100.0 | 84.8 (78-90) | 100.0 |
| Newton attention, rank 512 | | 100.0 | 97.5 (96-100) | 100.0 |
| Subset attention, rank 256, mu 0.2 | 100.0 | 96.5 (95-100) | 62.9 (60-68) | 100.0 |
| Subset attention, rank 256, mu 0.05 | | 99.4 (98-100) | 80.1 (75-84) | |
| Subset attention, rank 256, mu 0 | | 100.0 | 82.3 (80-84) | |
| Subset attention, rank 512, mu 0 | | | 93.3 (90-97) | |
| Subset attention, bosonic (h_m), rank 256, mu 0.2 | | 71.4 (69-73) | | |

The vacuum mixes lower arities into each feature (Proposition 5): at mu = 0.2 the Match-4 layer leans on
arities 2, 3 and 4 (knockouts 80, 64, 50%), at mu = 0 on arity 4 alone, as Newton attention does.
Exclusion matters: the bosonic variant, which lets a token repeat, stays at 71% on Match-4.

**8.3 Width, one head, Match-4, 6,000 steps (`sfa_a`).**

| Rank | 32 | 64 | 128 | 256 |
| --- | --- | --- | --- | --- |
| Newton attention | 62.3 | 69.7 | 75.1 | 86.8 |
| Subset attention, mu 0.2 | 56.4 | 65.2 | 71.8 | 76.7 |

**8.4 Chains, 4,000 steps (`sfa_a`; other rows from `baseline`, `newton_a`).**

| Model | Params | Pointer chase | Three-hop composition |
| --- | --- | --- | --- |
| Softmax, 1 / 2 / 3 layers | 54k / 104k / 154k | 65.3 / 96.8 / 100.0 | 32.5 / 51.0 / 51.9 |
| Cubic attention | 63k | 85.4 | 44.0 |
| Feynman attention (DS-PA v4) | 62k | 100.0 | 81.8 (46-100) |
| Newton attention, rank 32 | 153k | 62.3 | 32.8 |
| Subset attention, 1 / 2 / 3 layers | 88k / 171k / 254k | 64.6 / 94.4 / 79.3 | 32.5 / 45.0 / 43.8 |
| **Subset + walks, 1 layer** (R = 4 / 3) | 142k / 129k | **100.0** (100-100) | **95.2** (85-100) |

With walks, pointer chase is at 82-97% by the first evaluation (step 400) and above 99% by step 800 on every seed. Switching off
any arity changes nothing: the walk sector carries the chains.

**8.5 Language, enwik8 bytes, 3.3M parameters, 8,000 steps (`lm_a`, `lm_sfa`, `lm_sfa_b`).**

| Model | Bits per character (seeds) |
| --- | --- |
| Softmax (lm_a) | 1.651 (1.641, 1.654, 1.656); rerun of seed 0: 1.642 |
| Softmax + Newton branch | 1.657 |
| Newton only | 2.497 |
| Subset attention K = 4, arities on at init, mu 0.2 | 1.669 (1.671, 1.669, 1.665) |
| Subset attention K = 1 (softmax + per-token phases) | 1.654 (1.654, 1.654, 1.653) |
| Subset attention K = 4, arities 2-4 off at init, mu 0.2 | 1.652 (1.654, 1.652, 1.650) |
| Subset attention K = 4, arities 2-4 off at init, mu 0.05 | 1.652 (1.654, 1.650, 1.653) |

Wall clock on an H100 in plain JAX: 58 s per run for softmax, about 150 s for subset attention (three
extra power-sum passes at full float32 precision, no fused kernel).

**Go / no-go against section 7.** (1) Selection x arity: **go** (14 points at d = 7, 3/3 seeds), with
the caveat that keyed Match-3 needed no selection. (2) Arity retention: **partial** (within 2 points on
Match-3/4 and smallest arity; 2.5-4 points short on Match-5). (3) Chains in one layer: **go** on pointer
chase (3/3 at 100%); three-hop misses the bar on one seed (100, 100, 85). (4) Language: **no gain**, as predicted; no regression with
arities off at init. (5)-(7) not run.

## 9. What did not survive checking

- "Factorised cubic attention is the m = 2 case": only for additive scores (Proposition 2d).
- "Feed normalised attention outputs into Newton's identities": wrong without the partition functions.
- "A non-diagonal (determinantal) kernel can express a chain in one layer" (Argon): a determinantal
  subset law cannot see forward edges; Argon's working construction is the propagator with a source,
  i.e. the walk sector, not a subset sector.
- Argon's predicted constant in the characters law ($M = \binom{n-1}{k-1}$) is off by about 5 points;
  the functional form survives with a fitted constant.
- Argon's coupon-collector numbers assumed every channel becomes a character; measured layers convert
  about one channel in eleven.
- Logit soft-capping as the stability fix (both partners offered it, and the first prototype used it):
  bounded logits do not save arity >= 4 on short sequences (errors of order 1 at n = 7, cap 5); the
  vacuum does.

## 10. NeurIPS readiness

**What is strong.**

1. A theory spine that is short and checkable: arity is Fourier degree ((k-1)-wise independence); an
   exact distinct-subset evaluator at the cost of K attention passes, with its sampling law (diagonal
   k-DPP / conditional Poisson) and a numerically safe form (the vacuum); an exact character
   construction with width (|G|-1)/2 for every arity and a matching bilinear lower bound; and now an
   explanation of the characters law (oracle plus Parseval form).
2. Causal evidence a reviewer can not easily wave away: order caps send the layer to exactly chance,
   knockouts show it uses exactly the arities a task contains, exclusion matters (bosons 71% vs
   fermions 96.5% at the same vacuum), features transfer across arities.
3. One map with a measured consequence for every sector: subsets solve relations, selection keeps
   them clean among distractors, walks solve chains in one layer, and the interacting theory (Feynman
   attention) represents composed arity but never learns it. That is a cleaner story than "a new
   operator wins".

**What is missing (in order of how much a reviewer will care).**

1. **Established benchmarks.** Everything is Z_3^m or pointer tables built for this project. Needed:
   Match3 on HOMA's protocol (published 99.3 / 92.5), SET-in-5 (RelConvNet 97.9), CLUTRR (train
   k <= 3, test to 10), a CLRS-30 subset (Floyd-Warshall, SCC), p-hop at p = 16, and MQAR for
   retrieval. PLAN.md's Phase B list already has the numbers to beat.
2. **Prior art for each piece.** Newton's identities and power sums are classical; the k-subset
   distribution and its exact marginals by dynamic programming appear in SIMPLE (Ahmed et al.,
   ICLR 2023); multi-hop attention diffusion sum_l theta_l A^l is MAGNA (Wang, Ying, Huang, Leskovec,
   IJCAI 2021), close to the walk sector; Janossy pooling, DPPs, HLA and 2-simplicial attention
   bracket the rest. A search found no attention layer that reads distinct subsets of every arity
   through Newton's identities, but the walk sector should be presented as a known component placed in
   the formalism, not as a contribution.
3. **A kernel and a scale story.** Plain JAX at n <= 31 and a 3.3M-parameter LM. Needed: a fused
   FlashAttention-style implementation (K power-sum outputs from one pass, or the subtraction-free
   merge), wall clock and memory at n = 2-8k, and one larger LM run to state "no regression" with
   confidence (and drop LM gains from the claims).
4. **Statistics.** Three seeds, some spreads wide (three-hop 85-100, Match-5). Headline cells need 5+
   seeds and intervals.
5. **Width scaling across groups.** The planted / random / learned sweep over Z_3^d, d = 2..5
   (section 7, item 6) is the figure that turns "it needs rank 256" into a law.
6. **Theory scope.** Theorem 1 is about class means, not classifiers; the leap connection has to
   match Abbe et al.'s assumptions; the vacuum error bound is a sketch; the characters-law constant
   (M_eff) is fitted, not derived.

**Shortest path (about two months of focused work, roughly $150-250 of Modal).**

1. Freeze the layer: free-field attention = softmax + subset sectors (mu = 0.05, zero-initialised
   queries, arities 2..K off at init) + walk sector, one read-out; ablations by sector.
2. Benchmarks: HOMA Match3 and SET-in-5 (arity), keyed Match-k with curriculum (selection x arity, a
   new task worth releasing), CLUTRR and p-hop (walks), CLRS FW/SCC (both); baselines softmax 1-4
   layers, 2-simplicial, HOMA, Edge Transformer, Feynman attention, Newton attention.
3. The width-scaling figure and the characters-law theorem with its n-sweep test.
4. A Pallas or Triton kernel and one 20-50M-parameter LM run.
5. Write it as "How many tokens make a relation?": arity as particle number, chains as propagation,
   composition as interaction, with Newton attention and the characters law as the mechanistic core.

Title, scope and claims should follow the evidence: a layer for relations among many tokens that does
not cost softmax anything on text, not a better language model.
