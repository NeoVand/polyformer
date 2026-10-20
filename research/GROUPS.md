# Is higher order a property of the representation?

Working note, 20 October 2026. Companion to `SEARCH.md`, `LOCAL.md` (the searches for a layer that beats softmax on
language; both no-go) and `FORMALISM.md` (subset attention). Code: `research/groups.py` (groups, character tables,
the ordered Match-k task, representation content), `research/polybench.py --model holo` (holonomy attention) and
`--embed char|charrot` (frozen characters), brute-force checks in `research/test_groups.py`, grids `grp_*` in
`research/modal_run.py`, raw rows in `research/results/grp_*.jsonl`. Section 7 (word problems over A5 and S5): grids
`wp_*`, rows in `research/results/wp_*.jsonl`, tables from `research/wp_summary.py`.

## 0. The idea being tested

Everything higher-order we built defined order as "a score that depends jointly on k tokens". Three results do not
fit that definition:

1. **Newton attention's operator is first-order.** With phases, the product over tokens is the exponential of a sum,
   prod_t (1 + z phi_t) = exp(sum_j (-1)^(j+1) z^j P_j / j) with P_j = sum_t phi_t^j, so every k-subset sum is a
   polynomial in one-token sums. What has to be learned is phi, and the characters law says exactly that: a run is
   exact iff its channels hold all 40 characters of Z_3^4. In those coordinates SET is not a three-way relation but
   theta_a + theta_b + theta_c = 0 (mod 2 pi).
2. **Depth already builds every order.** Attention is a three-legged vertex; a deep transformer is a sum over tree
   diagrams of such vertices. Feynman attention could represent Match-4 and still sat at 50.0: the gap was finding
   the solution, not expressing it.
3. **On language only first-order fixes paid** (look-back keys; local-linear correction of the softmax estimator).

The reframe: **order is a property of a relation in a representation.** A relation looks higher-order when its
low-order statistics vanish in the model's coordinates, which happens when the data has a symmetry the coordinates
do not factor out. Corollaries:

- Softmax attention is the k = 2 member: in character coordinates the dot product sum_chi chi(a) chi(b)* tests
  a b^-1 = e ("the same token"), which is what copying and induction need; Match-k tests a_1 ... a_k = e. The
  generalisation of attention is from similarity to composition under a group law.
- What abelian features (sums, dot products, phases) cannot linearise is non-commutative composition, a b != b a.
  Every relational task we built was commutative except pointer chains, and the only layer that solved chains in
  one step, the walk sector, is a product of matrices.

Two experiments test this. Experiment 1 separates the representation from the composition on our own Match-k tasks.
Experiment 2 asks whether commutativity of the learned representation is what separates solvable from unsolvable
relations, with a quantitative prediction from the Plancherel measure.

**A correction to the first proposal.** "Freeze the token embeddings to the characters" does not test coordinates
alone: the 80 real character features of Z_3^4 are an orthogonal transform of the one-hot code (Gram matrix
81/2 I - 1/2, checked), and the model's first operation on them is linear. What it does test is whether softmax with
an MLP can learn the multiplicative read-out (Newton's identities) when a complete set of characters is handed to
it. That is the cleaner question: representation, or composition?

## 1. Experiment 1: representation or composition? (Z_3^4, Match-k)

- **Tasks:** `zs3`, `zs4`, `zs5` (Match-3/4/5 over Z_3^4 cards, n = 12/9/9), balanced accuracy on 2,048 held-out
  tables.
- **Arms:** softmax attention with an MLP, 1 and 2 layers, width 192, no positional embeddings (the task is a set),
  with three embeddings:
  - `char`: frozen [X, -X, bos, 0], X the cosine and sine of the 40 conjugate character pairs; zero mean and equal norm
    per card, so LayerNorm is a constant scale;
  - `charrot`: X rotated by a fixed random orthogonal matrix (same geometry, other coordinates);
  - `table`: learned tables at the same width (the usual model).
- **Protocol:** polybench defaults (AdamW, rate 2e-3, cosine, 6,000 steps, batch 128), 3 seeds.
- **Reference:** Newton attention, rank 256, shared normalised read-out (`newton_e`): 100 / 100 / 85 on zs3 / zs4 / zs5;
  softmax 1-3 layers at width 64 (`phase_a`): 57-66 on zs3, 50 on zs4 and zs5.

**Readings, registered:**

- **Representation suffices** if the better softmax depth on `char` reaches >= 90% on zs4 on 3 of 3 seeds. Then the
  higher-order layer's advantage on Match-k was a representation prior, and a softmax layer given the right
  features learns the composition in its MLP.
- **Composition is needed** if both depths on `char` stay <= 60% on zs4 on 3 of 3 seeds. Then knowing the characters is
  not enough: the multiplicative read-out (the generating function) is the higher-order content, and the reframe must
  say "composition under a group law", not "coordinates".
- Otherwise partial; the zs3 / zs4 / zs5 trend says whether the read-out's polynomial degree (3, 4, 5) is the limit.
- **Controls:** `charrot` within the seed spread of `char` means only the geometry matters (expected, since the first
  operation is linear); a larger gap means Adam's per-coordinate scaling makes the basis matter. `table` at width 192
  should stay near `phase_a`.

## 2. Experiment 2: commutative or not? (ordered Match-3 over groups)

**Task** (`g3_<group>`): a BOS token, then n elements drawn uniformly from a group G; position i is positive iff it
lies in some positions i1 < i2 < i3 whose product in position order g_i1 g_i2 g_i3 is the identity. For an abelian
group this is Match-3 over G; for a non-abelian one the order of the sequence matters (reversing an A5 sequence
changes 46% of the labels, a Z60 sequence none). Two sizes, an abelian and a non-abelian group at each:

| Task | Group | Order | n | Positive rate | Irreps (dimension) |
|---|---|---|---|---|---|
| g3_z12 | Z12 | 12 | 6 | 0.58 | 12 x 1 (complex) |
| g3_a4 | A4 | 12 | 6 | 0.58 | 1, 1', 1'' (complex pair), 3 |
| g3_z60 | Z60 | 60 | 11 | 0.53 | 60 x 1 (complex) |
| g3_a5 | A5 | 60 | 11 | 0.53 | 1, 3, 3', 4, 5 (all real) |

**Layer: holonomy attention** (`--model holo --gdim d`). Every token gets, per head, a gate and a rotation
U = exp(A(x)) in SO(d), A skew-symmetric and linear in the token. The layer reads, for every position i and arity
m + 1 <= K, the sum over (m+1)-subsets of positions containing i of their matrix products in position order,
F_m(i) = sum_{a+b=m} L_a(i) M_i R_b(i) with prefix and suffix sums L, R (O(T K^2 d^3) per head). Each arity is
divided by its subset count and RMS-normalised, and one shared projection reads all arities, as in Newton attention.
With d = 2 the rotations commute and the layer is exactly Newton attention's phi_i e_m(others) (checked to 2e-16);
with d >= 3 it is not commutative and sees order. No positional embeddings: order enters only through the products.

**What a head can hold.** A finite group's irreps are realisable by rotations; a head of dimension d can hold a real
irrep of dimension <= d, or a complex one-dimensional pair as a 2 x 2 rotation. The **reachable Plancherel mass** at
dimension d is the share of the nontrivial sum of d_rho^2 (= |G| - 1) held by those irreps:

| Group | d = 2 | d = 3 | d = 4 | d = 5 | d = 8 |
|---|---|---|---|---|---|
| Z12, Z60 | 1 | 1 | 1 | 1 | 1 |
| A4 | 2/11 = 0.18 | 1 | 1 | 1 | 1 |
| A5 | 0 | 18/59 = 0.31 | 34/59 = 0.58 | 1 | 1 |

Detecting "the product is e" from sums of products needs the whole Fourier inversion,
delta_e(g) = (1/|G|) sum_rho d_rho chi_rho(g), so a model missing irreps of mass 1 - p can at best use the part p.

**Arms:** holonomy attention at d = 2, 3, 4, 5, 8 with heads x d near 256 (128, 85, 64, 51, 32 heads), K = 3;
Newton attention (4 heads x 64 channels, K = 3, no positions); softmax attention with positions at 1 and 3 layers
(reference only). 6,000 steps, polybench defaults, 3 seeds. After training, `rep_content` reads the rotations each
element gets, measures every head's homomorphism error mean ||U_a U_b - U_ab|| / ||U_ab|| (random rotations sit near
1.4) and its irrep multiplicities <tr U, chi_rho>, and reports the irreps held (multiplicity >= 1/2 in a head with
error < 0.5) and their Plancherel mass.

**The order-blind ceiling.** A layer whose features commute (Newton attention, holonomy attention at d = 2) sees a
position's element and the multiset of the others, never the order. The best balanced accuracy of any such
predictor is estimated by relabelling random reorderings of each sequence (`groups.order_blind_ceiling`, 8,000
sequences x 128 reorderings, two seeds): **A4 83.1%, A5 77.2%**, Z12 and Z60 100%. It is far above chance because a
triple that multiplies to e in one order does so in at least two others (cyclic rotations are conjugate), and
triples inside an abelian subgroup do so in every order.

**Predictions, registered** (balanced accuracy, every cell on 3 of 3 seeds):

- **P1 (abelian groups):** on Z12 and Z60, Newton and holonomy attention at every d reach >= 95%.
- **P2 (order needs non-commuting features):** on A5, Newton and d = 2 stay at or below the order-blind ceiling
  plus 2 points (<= 79.2%), and d = 5 and d = 8 reach >= 95%.
- **P3 (the same on A4):** Newton and d = 2 stay <= 85.1% (ceiling plus 2), and d >= 3 reaches >= 95%.
- **P4 (what dimension is needed; two hypotheses, the pilot made the second one live):**
  - *Plancherel:* detecting "the product is e" from sums of products needs the whole Fourier inversion
    delta_e(g) = (1/|G|) sum_rho d_rho chi_rho(g), so accuracy should grow with the reachable mass: on A5, d = 3
    (mass 0.31) and d = 4 (0.58) strictly between the ceiling and 95%.
  - *Faithfulness:* a head needs only a faithful representation, because per-token gates let different heads sum
    over different subsets and a faithful rho has rho(g) = I only at g = e. A5 and A4 have faithful irreps of
    dimension 3, so d = 3 should already be exact.
  - **Decision:** faithfulness if d = 3 on A5 reaches >= 95% on 3 of 3 seeds; Plancherel if d = 3 stays <= 90% on 3
    of 3 seeds and the A5 means rise over d = 3, 4, 5; otherwise undecided.
- **P5 (exploratory):** which irreps the trained heads hold at each d, and whether larger irreps (larger d_rho^2, so a
  larger share of the gradient signal) are found first.

**Decisions.** If P1-P3 hold, the reframe stands on this evidence: what abelian layers (and softmax, the two-token
abelian case) cannot do is non-commutative composition, and a layer of learned group representations does it. If
Newton or d = 2 exceed the ceiling by more than 2 points, order-free features see something they should not and the
ceiling or the layer is wrong; check before reading further. If d >= 5 cannot learn A5 (<= 60%) while abelian
groups work, the non-abelian layer is not learnable at this budget; one amendment is allowed, 20,000 steps on the
failing cells.

## 3. Budget

Pilot (11 runs, before freezing), experiment 1 (54 runs), experiment 2 (96 runs), on L4: cap $25.

## 4. Pilot (seed 0, before the predictions above were frozen)

Grid `grp_pilot`, 11 runs, 6,000 steps:

| Task | Arm | Balanced accuracy | Notes |
|---|---|---|---|
| zs4 | softmax 1L, frozen characters | 50.0 | chance |
| zs4 | softmax 1L, rotated characters | 50.0 | chance |
| zs4 | softmax 1L, learned tables (width 192) | 51.0 | chance |
| g3_z12 | softmax 1L | 96.3 | 12 elements, 6 positions: the sequence is small enough to read |
| g3_z12 | Newton | 100.0 | |
| g3_z12 | holonomy d = 2 | 100.0 | holds 2 characters (mass 0.18) in good heads: exact without a representation |
| g3_z12 | holonomy d = 5 | 100.0 | no head below the error threshold |
| g3_a5 | softmax 1L | 50.0 | |
| g3_a5 | Newton | 76.1 | at the order-blind ceiling (77.2) |
| g3_a5 | holonomy d = 2 | 73.5 | below the ceiling |
| g3_a5 | holonomy d = 5 | **99.97** | snaps between steps 1,800 and 2,400; best heads hold the 5-dimensional irrep (multiplicity 0.99, error 0.24; next 0.96, error 0.48) |

What the pilot changed, before freezing:

1. The first draft of P2 and P3 put Newton and d = 2 at chance (55%). Newton's 76.1% on A5 showed that order-blind
   features carry most of the label, so the bar is now the measured order-blind ceiling.
2. The first draft registered a Plancherel law (accuracy ~ 1/2 + mass/2). The exact d = 5 run holds only the
   5-dimensional irrep (mass 25/59 = 0.42), which contradicts it unless other heads hold the rest imperfectly. P4
   now registers the Plancherel and faithfulness hypotheses against each other, decided by d = 3.
3. The homomorphism-error threshold for "held" rose from 0.2 to 0.5: the exact run's best heads sit at 0.24 and 0.48
   while random rotations sit near 1.4.
4. Z12 and A4 (6 positions over 12 elements) are small enough to be read whole, so on them the experiment tests
   order-blind against order-aware features, not representation learning; Z60 and A5 carry the representation
   question.

## 5. Results (20 October 2026)

164 runs on L4 (pilot 11, experiment 1 54 + 3, experiment 2 96 + 3), about 3.6 GPU-hours, roughly $3 of the $25 cap.
Tables from `python3 research/grp_summary.py grp_e1 grp_e2`.

### 5.1 Experiment 1: composition is needed

Balanced accuracy %, mean (seeds 0, 1, 2):

| Arm | Match-3 | Match-4 | Match-5 |
|---|---|---|---|
| softmax 1L, frozen characters | 54.8 (54.9, 54.9, 54.6) | 50.0 (50.0, 50.0, 50.0) | 50.0 (50.0, 50.0, 50.0) |
| softmax 2L, frozen characters | 54.7 (55.2, 54.9, 54.0) | 50.0 (50.0, 50.0, 50.0) | 50.0 (50.0, 50.0, 50.0) |
| softmax 1L, rotated characters | 54.8 (54.5, 54.9, 54.8) | 50.0 (50.0, 50.0, 50.0) | 50.0 (50.0, 50.0, 50.0) |
| softmax 2L, rotated characters | 53.9 (54.5, 54.4, 52.9) | 50.0 (50.0, 50.0, 50.0) | 50.0 (50.0, 50.0, 50.0) |
| softmax 1L, learned tables | 58.1 (57.2, 59.4, 57.6) | 50.9 (50.7, 51.0, 50.9) | 50.0 (50.0, 50.0, 50.0) |
| softmax 2L, learned tables | 58.6 (60.9, 58.2, 56.9) | 50.5 (50.9, 50.0, 50.6) | 50.0 (50.0, 50.0, 50.0) |
| *Newton attention (newton_e, reference)* | *100* | *100* | *85* |

Exploratory: softmax 2L on frozen characters for 20,000 steps on Match-4 is 50.0 on all three seeds.

**Registered reading: composition is needed** (both depths <= 60% on Match-4 on 3 of 3 seeds; in fact exactly 50.0).
Handed every character of Z_3^4, softmax with an MLP does not learn the multiplicative read-out, at either depth or
with more steps; on Match-3 it does slightly worse than with learned tables. Rotating the characters changes nothing,
as expected for a model whose first operation is linear. So Newton attention's advantage is the product (its
generating function), not its coordinates. The reframe's strong form, "higher order is only a choice of
coordinates", is refuted.

### 5.2 Experiment 2: commutativity is the line

Balanced accuracy %, mean (seeds 0, 1, 2); order-blind ceilings A4 83.1, A5 77.2:

| Arm | Z12 | A4 | Z60 | A5 |
|---|---|---|---|---|
| holonomy d = 2 (commuting) | 100.0 | 81.1 (81.7, 81.0, 80.7) | 100.0 | 73.1 (73.6, 73.1, 72.5) |
| holonomy d = 3 | 100.0 | 100.0 | 100.0 | 94.1 (93.4, 94.0, 94.8) |
| holonomy d = 4 | 100.0 | 100.0 | 100.0 | 99.5 (99.2, 99.5, 99.7) |
| holonomy d = 5 | 100.0 | 100.0 | 100.0 | 100.0 (99.97, 99.96, 99.98) |
| holonomy d = 8 | 100.0 | 100.0 | 100.0 | 100.0 |
| Newton attention | 100.0 | 80.7 (81.1, 80.8, 80.3) | 100.0 | 76.1 (76.1, 76.4, 75.9) |
| softmax 1L (positions) | 98.2 (96.4, 100.0, 98.2) | 81.0 (80.6, 81.1, 81.2) | 50.1 | 50.0 |
| softmax 3L (positions) | 100.0 | 99.7 (99.6, 99.9, 99.8) | 50.8 (50.6, 50.2, 51.4) | 50.0 |

Exploratory (after the registered decision): holonomy d = 3 on A5 for 20,000 steps reaches **99.2, 99.4, 99.3** and is
still rising, holding the same two 3-dimensional irreps.

| Prediction | Registered criterion | Outcome |
|---|---|---|
| P1 | Z12, Z60: Newton and every d >= 95% | **holds** (all 100.0) |
| P2 | A5: Newton, d = 2 <= 79.2%; d = 5, d = 8 >= 95% | **holds** (76.1, 73.1; 100.0, 100.0) |
| P3 | A4: Newton, d = 2 <= 85.1%; d >= 3 >= 95% | **holds** (80.7, 81.1; all 100.0) |
| P4 | A5 d = 3 >= 95% (faithfulness) or <= 90% with rising means (Plancherel) | **undecided** at 6,000 steps (93.4-94.8); the exploratory 20,000-step runs (99.2-99.4) favour faithfulness |

**Irreps the trained heads hold** (multiplicity >= 1/2 in a head with homomorphism error < 0.5), per seed:

| Group | d = 2 | d = 3 | d = 4 | d = 5 |
|---|---|---|---|---|
| A4 | none; 1', 1''; 1', 1'' | 3; 3; 3 | 3; none; 3 | none (x3) |
| A5 | none (x3) | 3, 3'; 3, 3'; 3, 3' | 3'; 4; 3, 4 | 5; 5; 4, 5 |

The best heads are close to exact representations: on A5 at d = 3 the multiplicities of 3 and 3' are 0.95-1.01 with
homomorphism errors down to 0.05 (random rotations sit near 1.4). "None" at large d is a limit of the measure, not
an absence: it averages over every pair of elements, including those a head's gate switches off, so a head that is
a representation only where it is open fails it. The held-mass column is therefore a lower bound and P5's
"larger irreps first" is only suggestive (at d = 4 and 5 the heads usually take the largest irrep that fits).

**What the numbers say.**

- **Commuting features reach exactly what order-blind information allows.** Newton attention and d = 2 sit at or
  under the ceilings on A4 (80.7, 81.1 against 83.1) and A5 (76.1, 73.1 against 77.2). On A4 the commuting layer
  finds precisely the characters of the abelian quotient Z3 (1', 1''), the only nontrivial one-dimensional
  representations A4 has.
- **Non-commuting rotations learn the group.** One layer at d >= 3 solves both non-abelian groups, and its heads are
  the groups' irreducible representations: the tetrahedral 3 of A4 and the two icosahedral 3s of A5 at d = 3, the 4
  and 5 of A5 at d = 4 and 5.
- **The smallest faithful representation is enough; dimension buys speed.** A5's 3-dimensional irreps carry only 31%
  of the Plancherel mass, yet d = 3 reaches 99.3% with more steps. The ladder at 6,000 steps (73.1, 94.1, 99.5, 100,
  100 for d = 2, 3, 4, 5, 8) is a learning-speed ladder above d = 3, not a capacity ladder. The Plancherel law as
  registered in the first draft is wrong for a layer with per-token gates.
- **Softmax composes nothing.** On the 60-element groups, 1 and 3 layers stay at chance even on abelian Z60, where
  every phase or rotation layer is exact. On the 12-element groups with 6 positions, 3-layer softmax reads the whole
  sequence (100 and 99.7): a small-universe effect, not composition.

## 6. What this means

1. The strong reframe was wrong and the experiment says why: the higher-order content of Newton attention is the
   **composition** (a product of group-valued features summed over subsets), not the coordinates. Softmax given the
   coordinates still cannot compose.
2. The refined reframe holds on this evidence: **what a layer can relate is set by the group its features compose
   in.** Softmax composes nothing; Newton attention composes in an abelian group (phases) and reaches exactly the
   order-blind information; holonomy attention composes in SO(d), learns the irreducible representations of a
   non-abelian group from labels alone, and solves what order-blind layers cannot. Newton attention is its
   commuting d = 2 case (checked to 2e-16); the walk sector, which solved pointer chains, is the same idea with hop
   matrices.
3. So the generalisation of attention this project has been looking for is not "more tokens per score" but **attention
   over learned group representations**: tokens carry elements of a learned matrix group, and the layer reads
   ordered products over subsets of positions.

**What it does not show.** These are synthetic tasks with an explicit group law. Nothing here says natural data has
such structure at the scale we can test, and none of it bears on the language results of SEARCH.md and LOCAL.md.
Products of learned matrices along a sequence are also the core of linear RNNs with matrix-valued state (DeltaNet,
DeltaProduct, negative-eigenvalue state tracking, unitary RNNs), which track non-abelian groups by composing the
whole prefix into one state. Holonomy attention differs in summing ordered products over every subset of positions
(a non-abelian elementary symmetric function), so it answers relational queries ("which k elements compose to the
identity") rather than carrying one running product; the relation between the two needs to be worked out before
any claim of novelty.

**Next, cheapest first.**

1. **State tracking**: running products over A5 and S5 (the NC1-complete word problems) with holonomy attention,
   softmax and a linear RNN with matrix state, one and two layers; the prefix product is the arity-n sector, so the
   layer should do it in one step where softmax cannot at constant depth. (Done: section 7.)
2. **Selection with composition**: keyed versions of the group tasks, combining subset attention's query weights
   with rotations (the non-abelian subset attention).
3. **Real data**: a holonomy branch in the S6 language-model harness at equal FLOPs under Muon, and on code, where
   scopes and stacks are non-commutative.

## 7. State tracking: the word problem over A5 and S5

Next step 1 of section 6, registered before its main runs (20 October 2026). Code: `groups.task_word`,
`groups.word_commuting_ceiling`, `groups.irrep_det`, `groups.householders_needed`, `polybench.holonomy_causal`,
`--model deltaprod` and `--hh`; checks in section 7 of `test_groups.py`; grids `wp_*` in `modal_run.py`; tables
from `research/wp_summary.py`.

### 7.1 Question and tasks

The open question from section 6: products of learned matrices along a sequence are already the core of linear RNNs
with matrix state, which track non-abelian groups. Does the composition view give anything there? The word problem
is the cleanest test: read g_1 ... g_T and output, at every position t, the running product g_1 g_2 ... g_t. For a
non-solvable group it is NC1-complete, so constant-depth softmax attention cannot solve it at every length unless
TC0 = NC1.

| Task | Group | Length | Scored at every position | Chance |
|---|---|---|---|---|
| wp_a5_16, wp_a5_64 | A5 (60) | 16, 64 | the product, one of 60 classes | 1.7% |
| wp_s5_16, wp_s5_64 | S5 (120) | 16, 64 | the product, one of 120 classes | 0.8% |
| ws_a5_16, ws_a5_64 | A5 | 16, 64 | does the product fix the letter 5 (in A4)? positive rate 0.20 | 50% |
| ws_s5_16, ws_s5_64 | S5 | 16, 64 | does the product fix the letter 5 (in S4)? positive rate 0.20 | 50% |

A BOS token comes first and is not scored. The binary variant is cheaper (two outputs) and still NC1-complete:
the stabiliser's coset action on the 5 letters is faithful, so the automaton that tracks one letter has the whole
group as its transition group. Classes are uniform at every position, so balanced accuracy equals token accuracy
on the class tasks. Every model trained at length 16 is also scored at length 64 (`--evallen 64`).

### 7.2 What each layer can represent

**Holonomy attention, causal.** For the word problem the layer is made causal: at position i it reads, for arity
m + 1 <= K = 3, the sum over subsets of positions <= i that end at i of their ordered products (L_m(i) M_i, divided
by the count C(i, m)), and one more sector, the **prefix product** P_i = U_0 U_1 ... U_i, the full-arity sector with
its gates divided out. All sectors are RMS-normalised and read by one shared projection, as before. P_i alone is an
orthogonal RNN with matrix state, H_i = H_{i-1} U(x_i), read linearly: that is the `orth` arm (`--order 0`). So on
this task the prefix sector *is* the prior art, and the experiment can only show (a) that the layer finds it and
(b) whether the subset sectors add or cost anything.

**Which groups fit in SO(d): determinants matter.** The rotations exp(A) have determinant 1, so a head can hold a
real irrep rho only if det rho = 1, or rho + det rho one dimension up. A5 is perfect, so every irrep has det 1. In S5
transpositions act as reflections in the 4-dimensional irreps, so det 4 = det 4' = sign; of the faithful irreps
(4, 4', 5, 5', 6) only the 5 has det 1 (determinants computed from the characters and checked against explicit
matrices):

| Head dimension d | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|
| A5: irreps a head can hold | none | 3, 3' | 3, 3', 4 | all | all | all |
| S5: irreps a head can hold | sign (as sign + sign) | sign | sign | sign, 4 + sign, 4' + sign, 5 | + 5' | all |
| S5: faithful? | no | no | **no** | yes | yes | yes |

So one layer of holonomy attention can hold A5 exactly from d = 3, but S5 only from **d = 5**, not d = 4: a faithful
representation of S5 must contain a faithful irrep (its normal subgroups are 1, A5, S5), and none fits SO(4). (S5's
smallest faithful irrep has dimension 4, but it lives in O(4), not SO(4).) DeltaProduct's Householders can reflect, so
it is not bound by this: the standard 4 is a product of at most 4 of them.

**Two layers reach S5 at d = 3.** S5 = A5 x| Z2. With p_s the parity of g_1 ... g_s and tau a transposition,
h_s = tau^(p_(s-1)) g_s tau^(p_s) is even and g_1 ... g_t = h_1 ... h_t tau^(p_t) (checked on 500 random words).
A first layer can hold the sign (d >= 2, a rotation by pi) and so give every position its prefix parity; a second
layer can then hold an A5 irrep of h_s, which is a function of g_s and p_s. So two layers at d = 3 or 4 can solve
S5; whether training finds this is a question for the data.

**Commuting layers.** Newton attention is holonomy attention at d = 2 (section 2), so the commuting control is
d = 2 with the same causal sectors and prefix. One causal commuting layer sees at position t its element, the
multiset of the elements before it and the position, never their order. Given that, every ordering of the prefix is
equally likely, so the best accuracy is the plug-in estimate of `word_commuting_ceiling` (1,000 words, 256
reorderings per position):

| Task | 16, every position | 16, second half | 64, every position | 64, second half |
|---|---|---|---|---|
| A5 classes | 20.9 | 1.7 (chance) | 6.6 | 1.6 |
| S5 classes | 20.1 | 1.9 (parity known: 1/60) | 6.3 | 1.6 |
| A5 stabiliser (balanced) | 62.7 | about 50 | 53.3 | about 50 |
| S5 stabiliser (balanced) | 61.7 | about 50 | 53.3 | about 50 |

The first two positions are exact (one element; one element and one before it), the third is about one half (two
orders), and from position 8 on the answer is at chance. Two causal layers are not order-blind (the second layer
sees the nested prefix multisets), so the ceiling binds only at one layer.

**DeltaProduct.** I - beta k k^T fixes the hyperplane orthogonal to k, so a product of r of them fixes a subspace of
codimension at most r. An exact faithful representation therefore needs, per token, at least the largest
codimension of a fixed space over the group, minimised over faithful irreps (`groups.householders_needed`): **A5 2,
S5 4** (the 5-cycles; Cartan-Dieudonne constructs the decompositions, checked). This matches Siems et al.'s
constructions (S_n in one layer with n_h = n - 1; A5 as a rotation group of R^3 with n_h = 2). With two layers the
semidirect route above needs one reflection per odd element for the parity layer and two per token for A5, so
n_h = 2 can solve S5 in two layers; n_h = 1 cannot hold A5 in any one layer.

### 7.3 Arms and protocol

Every arm is causal and reads the same tokens; residual width 64, one MLP per layer, polybench defaults (AdamW,
rate 2e-3, cosine, batch 128), **6,000 steps at length 16 and 12,000 at length 64** (the pilot's length-64 S5 run
was still rising at 6,000), three seeds.

- **holonomy attention** d = 3, 4, 5 (85, 64, 51 heads), causal sectors K = 3 plus the prefix product, no positions;
- **holonomy without the prefix** (d = 5, K = 3 only): the layer of section 2, made causal;
- **orthogonal RNN** (d = 3 or 5): the prefix product alone, H_i = H_(i-1) exp(A(x_i)), read as a full matrix;
- **Householder RNN** (d = 4 or 5, n_h = 1, 2, 4; `--hh`): the same matrix state and read-out, with DeltaProduct's
  transitions U(x) = prod_j (I - beta_j k_j k_j^T), beta in (0, 2), in place of rotations;
- **Newton attention** = holonomy at d = 2 (128 heads), same sectors;
- **softmax attention** with learned positions (causal mask), 1 and 2 layers. Positions 17-64 are untrained in the
  length-16 models, so softmax's length-64 numbers are not a test of anything;
- **DeltaProduct** (`--model deltaprod`, Siems et al.): 4 heads of 16, n_h = 1, 2, 4 generalised Householder steps
  per token with beta = 2 sigmoid in (0, 2), unit keys and queries, per-head RMS norm, read-out S_t q_t; no short
  convolution and no gating (a minimal implementation, checked against an explicit loop).

Readings: balanced accuracy over every position, over the second half of the positions (where the commuting ceiling
and softmax are at chance), whole sequences right, accuracy by position, and the length-16 models scored at length
64. For holonomy runs the first layer's matrices are a function of the element alone, so `rep_content` reads which
irreps they hold.

### 7.4 Pilot (seed 0, before the predictions below were frozen)

Grids `wp_pilot` (31 runs), `wp_pilot_dp` and `wp_pilot_dp2` (DeltaProduct settings, 14 runs), `wp_pilot_hh`
(Householder RNN, 6 runs); 6,000 steps unless noted. Balanced accuracy %, every position / second half; length 64
for a length-16 model:

| Task | Arm | All | Second half | At 64 | Notes |
|---|---|---|---|---|---|
| A5 classes, 16 | holonomy d = 3, 4, 5 | 100 | 100 | 100 | exact by step 1,200; d = 3 heads hold 3 and 3' (best homomorphism error 0.002) |
| | orthogonal RNN d = 5 | 100 | 100 | 99.97 | |
| | Householder RNN d = 5, n_h = 2 / 1 | 100 / 16.9 | 100 / 1.6 | 100 / 5.4 | n_h = 1 cannot hold A5 |
| | holonomy d = 5 without prefix | 20.3 | 1.7 | | positions 1-3 exact, then chance: exactly its arity |
| | Newton (d = 2) | 17.3 | 1.7 | | ceiling 20.9 |
| | softmax 1L / 2L | 14.0 / 14.0 | 1.8 / 1.8 | | positions 1-2 exact, then chance |
| | DeltaProduct n_h = 1 / 2 / 4 | 13.4 / 14.1 / 14.1 | 1.6 / 1.5 / 1.8 | | positions 1-2 only |
| S5 classes, 16 | holonomy d = 5 | 98.4 | 97.1 | 81.3 | holds sign and 4' (4' + sign is in SO(5)) |
| | orthogonal RNN d = 5 | 99.5 | 99.1 | 89.7 | sign and 4'; snaps near step 4,000 |
| | holonomy d = 4 / d = 3 | 41.3 / 22.8 | 10.1 / 1.9 | 11.5 / 7.0 | no faithful SO(d) representation: accuracy decays with position |
| | Householder RNN d = 5, n_h = 4 / 2 | 100 / 24.6 | 100 / 2.8 | 100 / 7.2 | n_h = 4 as the codimension bound says |
| | Householder RNN d = 4, n_h = 4 | 99.3 | 98.7 | 90.3 | reflections reach O(4), which rotations cannot |
| | holonomy d = 5 without prefix | 19.7 | 0.9 | | positions 1-3 exact |
| | Newton (d = 2) | 12.0 | 1.8 | | ceiling 20.1 |
| | softmax 1L / 2L | 7.3 / 7.1 | 0.9 / 0.9 | | only position 1 (S5 has 14,400 pairs) |
| | DeltaProduct n_h = 1 / 2 / 4 | 8.7 / 9.5 / 10.5 | | | |
| | holonomy d = 3, 2 layers | 13.2 | 0.7 | | the semidirect route is not found |
| | DeltaProduct n_h = 2, 2 layers | 12.5 | 0.9 | | |
| S5 classes, 64 | holonomy d = 5 | 89.5 | 82.6 | | still rising at 6,000 steps; 876 s |
| | softmax 1L; DeltaProduct n_h = 4 | 2.5; 3.0 | 0.8; 0.8 | | |
| S5 stabiliser, 16 | holonomy d = 5 | 98.0 | 96.3 | 80.9 | |
| | DeltaProduct n_h = 4 | **99.0** | 98.3 | 75.3 | DeltaProduct *does* track S5 when one letter is read |
| | Newton; softmax 1L | 56.9; 57.7 | 50.0; 50.0 | | ceiling 61.7 |
| A5 stabiliser, 16 | DeltaProduct n_h = 2 | 58.9 | 50.0 | | |

DeltaProduct settings tried on the class tasks, all at 11-14% on A5 (n_h = 2) and 10-13% on S5 (n_h = 4), i.e.
positions 1-2 only: beta starting at 2 sigmoid(3) = 1.9 (near reflections) or 2 sigmoid(-3) = 0.1 (near the
identity) instead of 1; 20,000 steps; width 128; 8 heads of 16; one head of 64; rates 5e-4 and 5e-3.

What the pilot changed, before freezing:

1. **The Householder RNN arm was added.** DeltaProduct failed the class tasks under every setting but solved the S5
   stabiliser, so its transitions can learn S5 here. Putting the same transitions into the full matrix read-out
   solved A5 at n_h = 2 and S5 at n_h = 4 in about 1,200 steps, and failed at n_h = 1 and 2 respectively, exactly
   the Householder bound. So DeltaProduct's failure on the class tasks is its narrow read-out (dv numbers per
   head, S_t q_t) at this width and budget, not its transitions, and the comparison that bears on holonomy
   attention is between parametrisations of the same matrix state.
2. Length-64 cells train for 12,000 steps.
3. The two-layer semidirect route (S5 at d = 3) was not found in the pilot; it is registered as expected to fail
   rather than as an open hypothesis.
4. A5 extrapolates from 16 to 64 exactly for every arm that solves it; S5 does so only with Householder transitions
   (100) and not with rotations (81, 90). This is registered as a prediction from one seed.

### 7.5 Prior art

The word problem of a non-solvable group (A5, S5) is NC1-complete
(Barrington 1989, JCSS 38). Constant-depth transformers and diagonal state-space models sit in TC0 and cannot
compose permutations at arbitrary length unless TC0 = NC1 (Merrill, Petty and Sabharwal, arXiv:2404.08819);
transformers simulate any automaton at depth O(log T), and at constant depth only when its groups are solvable
(Liu, Ash, Goel, Krishnamurthy and Zhang, arXiv:2210.10749). The models that do track non-solvable groups carry
one running product of matrices. Unitary and orthogonal RNNs fix the transition (Arjovsky, Shah and Bengio,
arXiv:1511.06464; Householder products, Mhammedi et al., arXiv:1612.00188; the exponential of a skew-symmetric
matrix, which holonomy attention uses, Lezcano-Casado and Martinez-Rubio, arXiv:1901.08428). Input-dependent
transitions are the newer line: DeltaNet's state update is a generalised Householder transformation (Yang et al.,
arXiv:2406.06484); allowing its eigenvalues into [-1, 1] lets it reflect, which parity and state tracking need
(Grazzi et al., arXiv:2411.12537); DeltaProduct takes n_h Householder steps per token and solves S_n in one layer
with n_h = n - 1, and A5, a rotation group of R^3, with n_h = 2 (Siems et al., arXiv:2502.10297). The closest
construction in form is the path development layer, which maps each increment of a path into a matrix Lie algebra
and multiplies the exponentials along the path (Lou, Li and Ni, arXiv:2204.00740): that product is holonomy
attention's prefix sector. What holonomy attention adds is the subset sum: for every position it sums the ordered
products over all (m+1)-subsets of positions, F_m(i) = sum_{a+b=m} L_a(i) M_i R_b(i), which is the image in a
matrix group of the iterated-sums signature of the token sequence (Diehl, Ebrahimi-Fard and Tapia,
arXiv:1906.05823) truncated at arity K, and the coefficient of z^m in prod_t (I + z M_t), a non-commutative
elementary symmetric function. A linear RNN reads the single top-arity term; holonomy attention reads every arity
and, without a causal mask, every position on both sides. So on the word problem, which needs only the top arity,
the prefix sector is an orthogonal RNN with matrix state and the experiment must say whether the subset sums add
anything; on relational tasks (section 2: which three elements compose to the identity) the low arities do the
work and a running product does not answer the question.

### 7.6 Predictions, registered (balanced accuracy, every cell on 3 of 3 seeds unless noted)

Ceilings below are the one-layer commuting ceilings of section 7.2 plus 2 points.

- **W1 (one exact representation solves the word problem in one layer).** Class tasks at length 16: holonomy
  d = 3, 4, 5, the orthogonal RNN d = 5 and the Householder RNN d = 5 n_h = 2 reach >= 99% on A5; holonomy d = 5, the
  orthogonal RNN d = 5 and the Householder RNN d = 5 n_h = 4 reach >= 95% on S5, and the Householder RNN d = 4 n_h = 4
  >= 95%. At length 64 (12,000 steps): holonomy d = 3, the orthogonal RNN d = 3 and the Householder RNN n_h = 2 >= 95%
  on A5; holonomy d = 5, the orthogonal RNN d = 5 and the Householder RNN n_h = 4 >= 90% on S5. Stabiliser tasks:
  the same arms (holonomy d = 3 on A5, d = 5 on S5, Householder n_h = 2 / 4) >= 95% at length 16 and >= 90% at 64.
- **W2 (no exact representation, no tracking).** Second-half balanced accuracy <= 20% at length 16 for: holonomy
  d = 3 and d = 4 on S5 classes (no faithful SO(d) representation), the Householder RNN n_h = 2 on S5 and n_h = 1 on
  A5 (below the Householder bound); and <= 60% for holonomy d = 3 on the S5 stabiliser.
- **W3 (commuting control).** Newton (d = 2), one layer, at or below the ceiling plus 2: A5 classes <= 22.9 (16) and
  <= 8.6 (64); S5 classes <= 22.1 (16) and <= 8.3 (64); A5 stabiliser <= 64.7 (16); S5 stabiliser <= 63.7 (16).
- **W4 (constant-depth softmax).** Softmax, one and two layers: second-half balanced accuracy <= 5% on every class
  cell and <= 60% on every stabiliser cell, at both lengths.
- **W5 (arity).** Holonomy d = 5 without the prefix sector, length 16, mean over seeds: accuracy >= 95% at each of
  positions 1-3 and <= 10% at every position from 5 on, on A5 and S5. The causal subset sectors compose at most
  K = 3 elements, so the running product beyond that has to come from the top-arity sector.
- **W6 (do the subset sectors add anything?).** On every class cell where both run, holonomy attention and the
  orthogonal RNN of the same d are within 3 points (seed means): A5 16 (d = 5), A5 64 (d = 3), S5 16 and 64 (d = 5).
  If holonomy is ahead by more than 3 points anywhere, the subset sectors help state tracking; if behind, they cost.
- **W7 (two layers).** Holonomy d = 3 with two layers on S5 classes stays <= 30% (the semidirect route of 7.2 exists
  but is not found); DeltaProduct n_h = 2 with two layers <= 20%; Newton and softmax with two layers on the class
  tasks: second half <= 5%.
- **W8 (DeltaProduct as implemented).** At every n_h, class tasks <= 20% at length 16 and second half <= 5%; S5
  stabiliser at n_h = 4 >= 95% at length 16; A5 stabiliser at n_h = 2 <= 70%.
- **W9 (length generalisation, from one pilot seed).** Trained at 16, scored at 64: every arm that meets W1 on A5
  classes >= 95%; on S5 classes the Householder RNN n_h = 4 (d = 5) >= 95%, while holonomy d = 5 and the orthogonal
  RNN d = 5 are below 95% on at least 2 of 3 seeds.

**Decisions.** If W1, W5 and W6 hold, the composition view pays on state tracking **only through its top-arity
sector, which is a linear RNN with matrix state**: holonomy attention solves the word problems that softmax and
commuting layers cannot (W3, W4), but it does so as an orthogonal RNN does, and the subset sums contribute nothing
there. Their value, if any, stays with relational queries (section 2). If W9 holds as well, reflections are the
better parametrisation for the prefix (O(d) rather than SO(d)), and holonomy attention should take Householder
products for its matrices. If W6 fails in holonomy's favour, the subset sectors help state tracking and that is the
next thing to explain. If W1 fails for an arm with an exact representation, check learnability (one amendment
allowed: 20,000 steps on the failing cells) before reading W6.

### 7.7 Budget

Pilot 51 runs; main grid `wp_main` 210 runs (48 + 54 class runs at length 16, 42 at length 64, 42 stabiliser runs at
16 and 24 at 64), estimated 12 GPU-hours on L4, about $10; cap $20.

### 7.8 Results (20 October 2026)

294 runs on L4 (pilot 51, main grid 210, amendment 27, exploratory 6), about 19 container-hours, roughly $15 of
the $20 cap. Tables from `python3 research/wp_summary.py wp_main`; every cell is balanced accuracy %, mean (seeds
0, 1, 2). Chance is 1.7% (A5) and 0.8% (S5) on the class tasks, 50% on the stabiliser tasks.

**Word problem, |G| classes, every position** (one layer unless marked 2L):

| Arm | A5, 16 | A5, 64 | S5, 16 | S5, 64 |
|---|---|---|---|---|
| holonomy d = 3 | 100 (100, 100, 100) | 100 (100, 100, 100) | 22.9 (22.6, 23.7, 22.4) | |
| holonomy d = 4 | 100 (100, 100, 100) | | 38.3 (40.6, 38.8, 35.5) | |
| holonomy d = 5 | 100 (100, 100, 100) | | **99.8** (100.0, 99.7, 99.8) | **98.4** (97.3, 97.9, 100.0) |
| orthogonal RNN d = 3 | | 100 (100, 100, 100) | | |
| orthogonal RNN d = 5 | 100 (100, 100, 100) | | 71.4 (99.6, 100.0, 14.5) | 29.3 (78.5, 4.7, 4.8) |
| holonomy d = 5 without prefix | 20.6 (20.3, 20.8, 20.8) | | 19.6 (19.7, 19.5, 19.6) | |
| Householder RNN d = 5, n_h = 1 | 17.0 (17.0, 16.7, 17.2) | | | |
| Householder RNN d = 5, n_h = 2 | 98.9 (100.0, 100.0, 96.6) | 100 (100, 100, 100) | 20.4 (24.5, 20.3, 16.3) | |
| Householder RNN d = 5, n_h = 4 | | | **99.9** (99.8, 100.0, 100.0) | **100** (100, 100, 100) |
| Householder RNN d = 4, n_h = 4 | | | 99.9 (99.8, 100.0, 100.0) | |
| Newton (d = 2) | 17.5 (17.2, 17.3, 17.9) | 5.5 (5.4, 5.4, 5.8) | 12.3 (11.9, 12.6, 12.3) | 4.5 (4.5, 4.7, 4.3) |
| softmax | 14.0 (13.9, 14.0, 14.0) | 4.7 (4.8, 4.7, 4.8) | 7.3 (7.2, 7.4, 7.2) | 2.8 (3.0, 2.8, 2.7) |
| DeltaProduct n_h = 1 | 13.2 (13.7, 13.1, 13.0) | | 8.6 (8.7, 8.6, 8.6) | |
| DeltaProduct n_h = 2 | 14.2 (14.2, 14.1, 14.2) | 4.8 (4.8, 4.8, 4.8) | 9.4 (9.6, 9.1, 9.4) | |
| DeltaProduct n_h = 4 | 14.2 (14.2, 14.1, 14.2) | | 10.4 (10.5, 10.2, 10.6) | 3.5 (3.5, 3.5, 3.6) |
| holonomy d = 3, 2L | | | 13.3 (13.3, 13.3, 13.3) | |
| Householder RNN n_h = 1 / n_h = 2, 2L | 14.6 (14.4, 14.7, 14.5) | | 13.6 (13.5, 14.1, 13.1) | |
| Newton, 2L | 14.3 (14.3, 14.3, 14.3) | | 13.6 (13.9, 13.1, 13.8) | |
| softmax, 2L | 14.0 (14.0, 14.0, 14.0) | 4.8 (4.8, 4.8, 4.7) | 7.2 (7.1, 7.2, 7.3) | 2.4 (2.4, 2.4, 2.4) |
| DeltaProduct n_h = 1 / n_h = 2, 2L | 14.1 (14.1, 14.2, 14.0) | | 12.1 (12.4, 11.8, 12.1) | |

Every arm below 25% is right only at the first few positions (one to three) and at chance after: the second-half balanced
accuracy of every such cell is 0.8-2.2% (table in `wp_summary.py`), except holonomy d = 4 on S5 (7.7%; accuracy by
position 100 100 98 85 65 47 33 23 17 12 9 7 6 4 4 3, an approximate tracker that loses the product as it grows).

**Stabiliser membership (binary), every position:**

| Arm | A5, 16 | A5, 64 | S5, 16 | S5, 64 |
|---|---|---|---|---|
| holonomy d = 3 | 63.0 (63.4, 62.5, 63.1) | 53.5 (53.5, 53.4, 53.4) | 60.2 (60.3, 59.7, 60.4) | |
| holonomy d = 5 | | | **99.2** (99.8, 99.5, 98.4) | 92.3 (93.8, 84.1, 99.0) |
| Householder RNN n_h = 2 | 62.2 (62.0, 61.7, 62.9) | 55.3 (55.7, 56.6, 53.7) | | |
| Householder RNN n_h = 4 | | | 95.4 (92.4, 95.9, 98.1) | 72.5 (73.5, 74.2, 69.7) |
| Newton (d = 2) | 57.7 (58.0, 57.4, 57.8) | | 56.9 (56.9, 56.8, 57.0) | |
| softmax 1L / 2L | 59.2 / 60.6 | 52.3 | 57.1 / 58.3 | 52.2 |
| DeltaProduct n_h = 2 | 59.4 (60.9, 59.2, 58.0) | 53.7 (53.5, 54.3, 53.4) | | |
| DeltaProduct n_h = 4 | **96.2** (96.7, 97.9, 94.0) | | 84.5 (95.2, 96.5, 61.7) | 83.0 (100.0, 78.8, 70.1) |

**Length generalisation** (trained at 16, scored at 64; every position / positions 33-64):

| Arm | A5 classes | S5 classes | S5 stabiliser |
|---|---|---|---|
| holonomy d = 3, 4, 5 (A5); d = 5 (S5) | 100 / 100 (all nine runs) | 97.3 (99.7, 96.9, 95.3) / 95.3 | 90.0 (94.1, 92.6, 83.3) / 83.3 |
| orthogonal RNN d = 5 | 100 / 100 | 61.2 (80.0, 98.7, 4.9) / 54.5 | |
| Householder RNN n_h = 2 (A5); n_h = 4 (S5) | 92.4 (100.0, 100.0, 77.2) / 87.9 | 98.2 (96.8, 97.9, 100.0) / 96.9 | 69.9 (65.9, 69.2, 74.7) / 55.0 |
| Householder RNN d = 4, n_h = 4 | | 95.1 (96.9, 91.6, 96.8) / 90.7 | |
| Newton, softmax, DeltaProduct, holonomy without the right representation | 2.4-6.4 / chance | 2.4-10.7 / chance | 51.7-63.9 / 50-53 |

**Steps to 90%** (first evaluation at or above 90%; evaluations every 600 steps at length 16, 1,200 at 64):

| Arm | A5, 16 | A5, 64 | S5, 16 | S5, 64 |
|---|---|---|---|---|
| holonomy (d = 3 for A5, d = 5 for S5) | 1,200 (x3) | 2,400, 1,200, 1,200 | 2,400, 2,400, 3,000 | 3,600, 4,800, 4,800 |
| orthogonal RNN, same d | 1,200, 1,800, 1,200 (d = 5) | 3,600, 4,800, 3,600 | 4,200, 4,200, never | never (x3) |
| Householder RNN (n_h = 2 for A5, 4 for S5) | 1,200, 1,200, 1,800 | 2,400 (x3) | 1,800 (x3) | 2,400 (x3) |

**Amendment** (registered in 7.6: 20,000 steps on the W1 cells that failed, three seeds; grids `wp_amend`,
`wp_amend2`). The holonomy d = 5 cell on the S5 stabiliser at 64 (93.8, 84.1, 99.0) was left unamended to stay
inside the budget.

| Cell | 6,000 steps (12,000 at 64) | 20,000 steps |
|---|---|---|
| orthogonal RNN d = 5, S5 classes, 16 | 99.6, 100.0, 14.5 | **100, 100, 100** |
| orthogonal RNN d = 5, S5 classes, 64 | 78.5, 4.7, 4.8 | **98.2, 100, 100** (90% at 8,000, 12,000, 8,000 steps) |
| Householder RNN n_h = 2, A5 classes, 16 | 100, 100, 96.6 | **100, 100, 99.1** |
| Householder RNN n_h = 4, S5 stabiliser, 16 | 92.4, 95.9, 98.1 | **99.2, 98.9, 98.5** |
| Householder RNN n_h = 4, S5 stabiliser, 64 | 73.5, 74.2, 69.7 | 80.9, 71.1, 66.8 |
| holonomy d = 3, A5 stabiliser, 16 | 63.4, 62.5, 63.1 | 65.5, 65.2, 65.3 |
| holonomy d = 3, A5 stabiliser, 64 | 53.5, 53.4, 53.4 | 53.9, 53.6, 53.7 |
| Householder RNN n_h = 2, A5 stabiliser, 16 | 62.0, 61.7, 62.9 | 78.8, 78.1, 77.1 |
| Householder RNN n_h = 2, A5 stabiliser, 64 | 55.7, 56.6, 53.7 | 57.0, 56.9, 54.3 |

**Irreps held by the first layer** (multiplicity >= 1/2 in a head with homomorphism error < 0.5; best head's error
in brackets):

| Task | Arm | Seed 0 | Seed 1 | Seed 2 |
|---|---|---|---|---|
| A5 classes, 16 | holonomy d = 3 | 3, 3' (0.00) | 3' (0.00) | 3 (0.04) |
| A5 classes, 16 | holonomy d = 4 | 3, 4 (0.01) | 3, 3' (0.08) | 3, 4 (0.03) |
| A5 classes, 64 | holonomy d = 3; orthogonal RNN d = 3 | 3'; 3 | 3'; 3' | 3; 3 |
| A5 classes, 16 | Householder RNN n_h = 2 | 3' (0.10) | 3 (0.08) | 3 (0.12) |
| S5 classes, 16 | holonomy d = 5 | sign, 4' (0.13) | sign, 4 (0.10) | sign, 4 (0.10) |
| S5 classes, 64 | holonomy d = 5 | sign, 4' (0.06) | sign, 4 (0.06) | 5 (0.03) |
| S5 classes, 16 | orthogonal RNN d = 5 | sign, 4' (0.21) | 5 (0.13) | none (0.93) |
| S5 classes, 16 | Householder RNN d = 4, n_h = 4 | 4 (0.11) | 4 (0.15) | 4 (0.15) |
| S5 classes, 16 and 64 | Newton (d = 2) | sign | sign | sign |
| S5 stabiliser, 16 and 64 | holonomy d = 5 | sign, 4 | sign, 4 | sign, 4 |
| S5 classes, 16 | holonomy d = 3, d = 4 | none (0.84-0.89, 0.71-0.74) | | |

Every exact cell holds what section 7.2 says it must: A5 one of its 3-dimensional irreps (or the 4); S5 in SO(5)
the 4 or 4' together with the sign, or the 5; S5 with reflections the standard 4 in four dimensions; the commuting
layer the sign of S5, which is all of S5 that commutes. The stabiliser runs hold the 4 (not the 4'), the irrep the
label reads (below).

**Exploratory, after the results (not registered):** the A5 stabiliser's indicator 1_A4 has Fourier support on the
irreps 1 and 4 only (its multiplicities are those of the permutation action on the five letters, 1 + 4; computed).
A head that holds only a 3-dimensional irrep sees nothing of the label to first order, however exact its
representation. Holonomy at d = 4, which can hold the 4, solves the A5 stabiliser on **100, 100, 100** (the heads
that pass the error test hold the 4; 99.8-99.9 at length 64), and the Householder RNN at n_h = 4 (the 4 of A5
needs four reflections for its 5-cycles) on 98.8, 95.6, 92.1. DeltaProduct's 96.2 at n_h = 4 against 59.4 at n_h = 2
is the same split.

| Prediction | Registered criterion | Outcome |
|---|---|---|
| W1 | exact representation solves the task in one layer | **fails as registered, holds on the class tasks after the amendment** (every class cell >= its threshold on 3 of 3 seeds); fails on the stabiliser tasks at A5 with d = 3 / n_h = 2 (63, 62 at 16; 65, 78 at 20,000 steps: a wrong prediction, explained above) and at S5 length 64 (holonomy one seed 84.1; Householder 81, 71, 67 at 20,000 steps) |
| W2 | no exact representation, no tracking (second half <= 20%) | **holds** (S5 at d = 3: 2.0, d = 4: 7.7; Householder n_h = 2 on S5: 2.2, n_h = 1 on A5: 1.7) |
| W3 | Newton at or below the commuting ceiling + 2 | **holds** (17.5, 5.5, 12.3, 4.5; stabilisers 57.7, 56.9) |
| W4 | softmax second half <= 5% (classes), <= 60% (stabiliser) | **holds** (0.8-1.7; 50.0 everywhere) |
| W5 | without the prefix: exact at positions 1-3, <= 10% from 5 | **holds** (A5 100 100 100 9 3 2 ...; S5 100 100 100 3 2 1 ...) |
| W6 | holonomy within 3 points of the orthogonal RNN | **fails, in holonomy's favour** at S5 16 (99.8 vs 71.4) and S5 64 (98.4 vs 29.3); equal on A5 (100, 100) |
| W7 | two layers do not help | **holds** (holonomy d = 3: 13.3; DeltaProduct: 12.1; Newton and softmax: second half <= 1.7) |
| W8 | DeltaProduct: classes fail, S5 stabiliser at n_h = 4 >= 95%, A5 stabiliser at n_h = 2 <= 70% | **fails on one seed** (S5 stabiliser 95.2, 96.5, 61.7); the class and A5 parts hold |
| W9 | length generalisation: A5 >= 95%; S5 Householder >= 95%, rotations < 95% | **fails**: holonomy d = 5 extrapolates on S5 (99.7, 96.9, 95.3), and the Householder seed that was 96.6 at 16 on A5 is 77.2 at 64 |

**What the numbers say.**

- **The word problem separates the layers by the group their features compose in**, as Match-3 did in section 5.
  Softmax with one or two layers gets the first one or two positions (a lookup of g_1 g_2) and nothing after; the
  commuting layer stays under its order-blind ceiling and holds only the sign of S5, which is all of S5 that
  commutes; every layer that holds an exact representation of the group tracks it at every position and both
  lengths.
- **Representation theory predicted every capacity outcome.** SO(d) heads track A5 from d = 3 and S5 only from
  d = 5 (at d = 4 accuracy decays position by position: an approximate tracker); Householder transitions need two
  per token for A5 and four for S5, and fail at one and two; with reflections S5 fits in d = 4. The one wrong
  prediction (the A5 stabiliser at d = 3) is a representation-theory fact the registration missed: a binary label
  reads only the irreps in its Fourier support, and the icosahedral 3s are not in the support of the A4 indicator.
  Which representation must be learned is set by the read-out, not by the group alone.
- **Arity is literal.** Without the prefix sector holonomy attention is exact on the first three positions and at
  chance after: the subset sectors compose at most K = 3 elements, and the running product has to come from the
  top-arity sector.
- **The subset sectors buy learning speed, not capacity.** At the same d and heads, holonomy attention (prefix plus
  arity 1-3 sectors) reaches 90% sooner than the prefix alone (A5 at 64: 1,200-2,400 steps against 3,600-4,800; S5
  at 16: 2,400-3,000 against 4,200, 4,200 and never; S5 at 64: 3,600-4,800 against never on all three seeds in
  12,000 steps). Given 20,000 steps the orthogonal RNN gets there too (100 on S5 at 16; 98.2, 100, 100 at 64, but
  reaching 90% only at 8,000-12,000 steps), so the capacity is the same. A plausible mechanism: the short-product
  sectors give the rotations a gradient from products of one to three elements at every position, a built-in
  curriculum that the single running product lacks.
- **Reflections are fastest on S5 classes, not everywhere.** The Householder RNN, with no subset sectors at all,
  reaches 90% first on both S5 class cells (1,800 steps at 16 and 2,400 at 64 on every seed; on A5 holonomy is as
  fast or faster: 1,200 against 1,200-1,800 at 16, 1,200-2,400 against 2,400 at 64), holds S5 in d = 4
  where rotations cannot, and extrapolates from 16 to 64 as well as holonomy (98.2 against 97.3). On the S5
  stabiliser it is worse than holonomy d = 5 (95.4 against 99.2 at 16; 72.5, and 72.9 after 20,000 steps, against
  92.3 at 64), so which parametrisation is better is not settled. Its transitions are DeltaProduct's; what
  DeltaProduct lacks here is the read-out (S_t q_t, 16 numbers per head), which tracks one letter (the stabiliser
  at n_h = 4) but not the whole permutation at width 64.
- **A second layer rescued no arm that failed with one.** The semidirect route of 7.2 (sign in layer 1, A5 in
  layer 2) exists for holonomy d = 3 and for Householders with n_h = 2, and neither found it.

**Decision, by the registered rules.** W1 (on the class tasks, after the amendment) and W5 hold and W6 fails in
holonomy's favour, so the registered reading is: the composition view pays on state tracking through its top-arity
sector, a linear RNN with matrix state, and the subset sectors help; the help measured here is learning speed and
reliability, not capacity. W9 failed, so the registered conclusion that reflections are the better parametrisation
does not follow; unregistered, they are faster on S5 classes and fit S5 in d = 4, and worse on the S5 stabiliser.

**What this means for the project.** On state tracking, holonomy attention is a matrix-state RNN plus a curriculum:
it solves what softmax and commuting layers provably cannot, and it does so the way DeltaProduct-style and
orthogonal RNNs do, by carrying one running product. Novelty here is not "a layer that can track state"; it is one
layer that reads both the running product (state tracking) and every short ordered product (the relational queries
of section 2), with the short products speeding up the long one. Two things to do next, cheapest first:

1. **Householder holonomy attention**: replace exp(A) by n_h generalised Householders in the holonomy layer (the
   `--hh` flag already does it for the prefix-only arm) and test whether it keeps both the Householder speed and the
   subset curriculum, on the word problems and on ordered Match-3 of section 2.
2. **Selection with composition** (section 6, step 2): keyed group tasks where a query must pick which positions to
   compose, which neither a running product nor unweighted subset sums can do alone.

The DeltaProduct comparison is limited by this implementation (width 64, no short convolution, 6,000-20,000 steps):
with the published architecture at its own scale it solves S5 classes (Siems et al.), so "DeltaProduct fails the
class task" is a statement about its read-out at this width, not about the method.
