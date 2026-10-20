# Is higher order a property of the representation?

Working note, 20 October 2026. Companion to `SEARCH.md`, `LOCAL.md` (the searches for a layer that beats softmax on
language; both no-go) and `FORMALISM.md` (subset attention). Code: `research/groups.py` (groups, character tables,
the ordered Match-k task, representation content), `research/polybench.py --model holo` (holonomy attention) and
`--embed char|charrot` (frozen characters), brute-force checks in `research/test_groups.py`, grids `grp_*` in
`research/modal_run.py`, raw rows in `research/results/grp_*.jsonl`.

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

## 5. Results

(filled in after)
