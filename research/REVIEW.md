# Review of "Learning to compose": what holds, what is missing, and what would have made it a result

Written 21 October 2026 after reading the full paper (`src/lib/paper`, nine parts) and every research
note it rests on (THEORY, GROUPS, FORMALISM, SEARCH, LOCAL, BEYOND, BEYOND_REPORT, NEXT, PRIOR_ART, PLAN),
re-deriving the core algebra by hand, and a literature search for what the project did not engage with.
Sources are linked at the end.

## 0. The one-paragraph verdict

The mathematics is correct and the measurements are unusually honest. The paper reads well: concrete
before abstract, failures stated plainly, prior art credited. What it lacks is not rigour or clarity but a
thesis that survives its own results. The project asked "can a layer that scores k tokens at once do more
than pairwise attention?", answered "yes on puzzles, no on text", and then discovered, late, that the
thing that mattered was never how many tokens a score touches but what algebra the layer multiplies in.
That discovery is right. It was not followed to its end. Followed to its end it says: the higher order
that pays is in the state (products of features carried along the sequence, and iteration of the same
block in depth), not in the score; the brain motivation points at exactly that; and the field, in the
same twelve months, built that layer (DeltaProduct, Gated DeltaNet, PaTH, looped language models, tiny
recursive models) and got the results this project was looking for. The paper should say so, and the
research should have been designed around it from the point the Newton result landed.

## 1. Verification: is it correct?

I checked every derivation the paper states, against the notes and by hand. All pass:

- SET inclusion-exclusion: `1[rule] = 1 - (δab + δbc + δac) + 3·1[a=b=c]` gives 1, 0, 1 on the three cases.
- Pair blindness: 1,080 SETs among 85,320 triples; each pair in 1 SET and 79 triples, and 85,320/79 = 1,080,
  so pairwise averages coincide. Correct.
- Hand-built head: `Σ_t cos(2π(a_t+b_t+c_t)/3) = 4 - 3m/2`; SETs score 4, everything else at most 2.5. Correct.
- Characters: `(1/81) Σ_c φ_c(x)φ_c(y)φ_c(z) = 1[x+y+z=0]` is character orthogonality on Z_3^4; 80 nontrivial
  characters in 40 conjugate pairs. Correct. The 80 real character features are an orthogonal transform of
  the one-hot code (Gram matrix 81/2·I − 1/2), as the notes say.
- Newton's identities and the O(nKr) cost. Correct.
- Order-blind ceiling: `B* = 1/2 + E|p(O) − π| / (4π(1−π))` follows from `max(a,b) = (a+b+|a−b|)/2` applied
  per observation; I re-derived it. The cyclic-rotation and commutator classification of triples
  (`bca = a⁻¹(abc)a`; `acb = e` iff `ab = ba`) is correct, as is `cp(G) = #classes/|G|`.
- Representation facts: A5 irreps 1,3,3′,4,5 (sum of squares 60); A4 irreps 1,1′,1″,3; S5 determinants
  from the character values on a transposition (only the 5 has det +1 among faithful irreps; 4 ⊕ sign fits
  SO(5)); Householder counts (A5 needs 2, S5 needs 4, from the fixed-space codimension of a 5-cycle). All
  correct, and consistent with the independent spectral obstruction published this year (Complex KDA,
  Theorem 4: one layer of DeltaProduct with k ≤ 3 cannot track S5 with any number of heads).
- Theorems 1–6 in THEORY.md are stated with the right scope (position-free, finite domain, existence of a
  readout), and the numerical checks back them.

Three soft spots, none a mistake, all a matter of what the words claim:

1. **The frozen-character experiment does not test what the narrative says.** Because the 80 character
   features are a rotation of the one-hot code and the model's first operation is linear, "softmax handed
   every character" is the same experiment as "softmax with learned embeddings", which the controls
   confirm (54.8 vs 58.1 on Match-3, 50.0 everywhere else). The paper admits this in a parenthesis. The
   honest reading is stronger and simpler: the leap barrier applies to the read-out MLP exactly as it
   applies to attention; handing in the Fourier basis does not lower the leap of a degree-k target.
   State it that way and cite Abbe et al. for it. The experiment that would separate "coordinates" from
   "composition" is to hand softmax the leave-one-out power sums `P_r(χ)` (the multiset statistics), which
   Theorem 6 shows suffice, and ask whether an MLP learns Newton's identities from them.
2. **The "characters law" is not a law of learning.** FORMALISM §4 shows it is a Parseval property of any
   read-out of pooled character sums: an oracle with F exact characters reproduces it under logistic, MLP
   and equal-weight read-outs. The paper presents it as a discovered regularity about trained layers. Say
   it is a property of the task's Fourier structure that the layer inherits.
3. **Holonomy attention's word-problem result is a matrix RNN plus a curriculum**, and the paper says so,
   but the title block ("A layer that multiplies learned rotations discovers the symmetry group of an
   icosahedron") still lets a reader think the operator is the point. The operator that solved the hard
   tasks is the prefix product, which is prior art; the new part is the subset sectors as a learning aid.

## 2. Writing

It serves understanding well. The "short version" list, the source marks (prior / new / measured),
definitions on first use, equations followed by a sentence, and the honest Part VIII are the right
choices. Two structural problems:

- **Part III (Feynman diagrams, Dyson–Schwinger) is five sections for a layer the paper abandons.** It is
  the one place the text is decorative rather than load-bearing: a reader learns QED vocabulary to
  understand a layer whose only surviving lesson is "one softmax over several term types, iterated with
  shared weights, needs sector balancing and a carry". That lesson fits in one section. Keep one figure
  and the three fixes; move the physics to an aside.
- **The arc has two climaxes and no thesis at the end.** Newton attention (Part IV) and holonomy (Parts
  VI–VII) each feel like the result, then three negative studies follow, and Part IX ends on a diagnosis
  ("finding structure is the hard part") rather than a claim. The diagnosis is correct but it is where the
  next paper starts, not where this one should stop. Section 3 below is the thesis the evidence supports.

Smaller points: the motivation from the brain is absent (if it drove the project, say so in Part I, with
the correct neuroscience; see 4.1); "arity", "order" and "degree" overlap and a reader has to hold all
three; Parts VII–VIII carry many numbers in prose that the tables already hold.

## 3. The diagnosis: "higher order" meant three different things

The project used one phrase for three mechanisms and spent most of its budget on the one that does not pay:

| Meaning | Where it lives | Project's evidence | Outside evidence |
|---|---|---|---|
| **Higher-order scores**: a query scores k−1 tokens jointly (cubic, quartic, Strassen, poly-attention, Feynman) | the selection | wins only on pure-leap puzzles; costs n^k; loses on text at 19M params | 2-simplicial attention helps only above 2B active parameters, as a scaling-exponent change, in token-limited training (Roy et al. 2025) |
| **Higher-order state**: products of per-token features carried along the sequence (Newton phases, holonomy rotations, Householder products, delta-rule outer products) | the values / the recurrence | every exact puzzle result; the only language win (GDN, DeltaProduct, one seed); "composition paid as recurrence" | DeltaProduct, Gated DeltaNet(-2), PaTH, KDA: state tracking plus competitive language at scale |
| **Higher-order computation by iteration**: the same block applied R times, with the output fed back | the depth | Feynman attention (R rounds, shared weights) solved pointer chasing and was then dropped; ARC run with no iteration | looped LMs (Ouro 1.4B ≈ dense 4B; Huginn), tiny recursive models (7M params, 45% ARC-AGI-1) |

The paper's own sentence in Part VI, "the content of a higher-order layer is how it combines features, not
how many tokens it touches", is the thesis. The evidence for the second row is the project's; the third
row is the brain motivation, and it was never tested.

## 4. Blind spots

### 4.1 The brain motivation points to recurrence, not to arity

"Few layers, slow neurons, fast answers" is true, and the neuroscience of the last six years says what the
trick is. Core object recognition that feedforward networks get wrong is solved in IT cortex about 30 ms
later, and recurrent or deeper models predict those late responses (Kar et al. 2019). A single layer-5
pyramidal neuron needs a 5–8 layer temporal convolutional network to reproduce its input–output function,
because of dendritic NMDA nonlinearities (Beniaguev, Segev, London 2021); human layer-2/3 dendrites compute
XOR on their own (Gidon et al. 2020). So the biological "few layers" are (a) recurrent, (b) each unit is
itself deep and multiplicative, (c) massively wide. None of that is "score k tokens at once".

The machine-learning answer to the same premise arrived in 2025–26 and is exactly the third row of the
table: looped language models. Ouro pretrains 1.4B and 2.6B looped models that match 4B and 8B standard
transformers; Huginn (3.5B, recurrent depth) improves when unrolled further at inference; a 2026 recipe
gets looped models trained in 310B tokens instead of 7.7T, and a parameter-matched 1.4B looped model beats
its dense twin on all 12 benchmarks (about +14 GSM8K, +10 MATH, +22 DROP), while still trailing a dense
model of 2.8× the parameters at equal inference compute. The Tiny Recursive Model, a 2-layer network of 7M
parameters recursed with deep supervision, reaches 45% on ARC-AGI-1 and 8% on ARC-AGI-2, above most LLMs.
A 2026 ablation finds the design choices that matter: a sandwich (untied prelude, tied core, untied coda),
input injection at each loop, and memory tokens; a single-block universal transformer without memory
tokens fails Sudoku-Extreme on every seed.

The project had a looped layer. Feynman attention is a weight-tied block iterated R times with a carry; it
solved pointer chasing in one layer with four rounds, and it was dropped because it did not learn Match-4
by composing cubic vertices. The ARC experiment then used a single forward pass with a 1-D prefix scan over
raster cells, which is the one configuration the literature says cannot work. The brain motivation, taken
seriously, says: loop the block, supervise each loop, let the loop count adapt. That was never tried.

### 4.2 The learnability barrier has a name and known cures

Every negative result in the paper is the same result: the computation is representable and gradient
descent does not find it (Feynman on Match-4; softmax on Match-4 with characters; two of three combined
layers on fresh seeds; both models on the dilution task; ARC). The paper cites Abbe et al. 2023 for the
leap and stops. The same group's NeurIPS 2024 paper is the direct statement for transformers: targets with
high "globality degree" are not learned efficiently, agnostic scratchpads do not help, educated
scratchpads break the barrier, and an inductive scratchpad breaks it and generalises out of distribution.
Barak et al. 2022 show the sparse-parity plateau is hidden progress, not a wall, and it takes n^O(k) steps.

This changes what the project should have built. A native k-way term is one way to lower the leap (the
paper's way). The general way is intermediate supervision: per-step targets, a scratchpad, or a looped
block with loss at every iteration (the TRM recipe). The project's best mechanistic finding points the same
way: Match-3 teaches Match-5 (transfer), and the short holonomy sectors speed up the long prefix product
(GROUPS §7, "a built-in curriculum"). That is the merged-staircase mechanism. It should have been the
design principle: give every layer low-leap sub-targets, and test whether the native term is still needed.
On the dilution task the obvious next arm was never run: supervise the intermediate ownership state at
every clause, not just the final answer.

### 4.3 Selection and composition must be cascaded, not run side by side

The project ended with three ingredients, "selection, estimation, composition", and tried them in parallel
(B), transported (A) and coupled (C). Only B trained reliably and B's composition branch was worth 0.035
nats. There is a 60-year-old theorem for why. Krohn–Rhodes: every finite automaton is a cascade of two
atoms, reset automata (flip-flops: write, erase, keep) and simple-group automata (permutations). Softmax
attention, the delta rule and gating are the reset atom; rotations and Householder products are the group
atom; Liu et al. 2022 ("shortcuts to automata") use exactly this decomposition to explain which automata
constant-depth transformers can simulate (the solvable ones) and which need recurrence or log depth. A 2026
paper ("Rational Transductors") makes it an architecture: attention covers the aperiodic part, a
matrix-valued linear recurrence recovers the group part, and the two are composed. Barrington's theorem
adds the constructive half: width-5 permutation programs compute all of NC1, so an input-dependent product
of S5 (or SO(5)) elements along the sequence, with the choice of element made by content, is a universal
primitive for everything constant-depth attention cannot do. DeltaProduct with four Householders in five
dimensions is that primitive, and it is the layer that won on language in the project's last study.

The design consequence is a cascade: the reset decides what enters the product (content-gated,
delta-rule style), the product composes it, and the result conditions the next reset. Candidate C was
the right shape and failed on fresh seeds; the paper's own finding that random (not identity) matrix
initialisation gives first-order gradients to the commutators is the fix it did not get to apply
consistently. Candidate B, which passed, is the wrong shape by this theorem, and its 0.035-nat branch is
what the theorem predicts.

### 4.4 Capacity, not arity: higher order as dense associative memory

Softmax attention is a modern Hopfield network (Ramsauer et al. 2020), and the original reason to add
higher-order interactions to a Hopfield energy is capacity: pairwise energies store O(N) patterns,
degree-n interactions store N^(n−1), and suitable energies store exponentially many (Krotov and Hopfield
2016; Lucibello and Mézard 2024 for the exponential case). The paper never once frames cubic attention as
an energy or asks what it buys in capacity. The capacity frame predicts where higher-order terms pay:
memory-bound regimes, long context, many stored associations. That is exactly where the one demonstrable
win for higher-order feature maps in a 2025 language model sits: Atlas raises memory capacity with
polynomial feature maps on keys and queries (a reported perplexity drop from 22.1 to 20.0 in ablation)
and reaches about 80% on BABILong at 10M context. The test-time-regression framework (Wang, Shi and Fox,
JMLR 2026) unifies softmax attention, linear attention, gated variants and state-space models as
associative memories solving a regression at test time, and explicitly suggests higher-order
generalisations of softmax attention as local polynomial regression; the project's LLA and Parallax
results are the first two rungs of that ladder, and it found them without the frame that says why they
are the right ladder.

### 4.5 Binding: the project rediscovered vector-symbolic architectures

Newton attention's phase channels, "multiply phases to add group elements", are Fourier holographic
reduced representations (Plate), the standard binding operation of vector-symbolic architectures. The
order problem the project then discovered, that commuting bindings cannot encode sequence, is the
classical VSA commutativity problem, solved thirty years ago by permutation binding (Kanerva) and matrix
binding of additive terms (Gallant and Okaywe); holonomy attention is matrix binding. Hrrformer (ICML
2023) already recast self-attention as HRR binding and superposition; "Attention as Binding" (2025) reads
queries and keys as roles, values as fillers, and attention as soft unbinding.

Two things follow. First, the prior-art audit (36 arXiv records) missed the family the construction most
belongs to. Second, and more useful, the binding frame says what relation language actually needs from a
"higher-order" layer: role–filler binding and unbinding (which entity has which attribute; which variable
holds which value), not zero-sum relations. The SET/Match-k family is pure leap by construction, the worst
case for gradient descent and the least representative of text, as the paper's Part V says in its own
words. The project's two best task ideas, keyed Match-k with distractors and interleaved swap programs,
are binding-plus-composition tasks; they were treated as side benchmarks when they were the main line.

### 4.6 The language protocol could not have seen the effect it was looking for

The protocol (19M non-embedding parameters, 400M tokens, 1% lower loss at equal FLOPs on 3/3 seeds, one
scale) is well executed and underpowered for the hypothesis. The only published higher-order-attention
gain on language (Roy et al. 2025) appears as a change in the scaling exponent (GSM8k 0.142 → 0.168,
MMLU-pro 0.090 → 0.108), shows "no gains" below 2B active parameters, and is claimed only for
token-constrained training. The project tested two orders of magnitude below that threshold, at one
scale, in a Chinchilla-balanced regime, with a loss gate. A May 2026 Tencent study re-tested 20 post-2021
transformer modifications at 1.2B and 3B with a multi-seed noise floor: only two cleared Bonferroni at
1.2B, one of those failed at 3B, and attention-output modifications within 2–3% of baseline loss lost
6–16 downstream points. Petty et al. (NAACL 2024) find deeper models generalise more compositionally at
fixed parameters, with fast-diminishing returns, which is the "few layers" question in its measurable
form.

What this says about the search: a loss gate at one small scale answers "does this layer beat softmax at
19M params", which is a question nobody doubted the answer to. The question the project wanted answered
needs three or four scales and a fitted exponent, a token-limited regime (repeated epochs), and
downstream probes that target the capability (binding, state tracking, length extrapolation), with the
noise floor reported. The project's own data show the right lever: Parallax's gap grew with tokens
(+0.26% at 100M, −0.8% at 400M, seed 0); the one trend that crossed the bar was left untested at the next
scale.

### 4.7 The operator primitive was already in the paper

Part IX's best idea, "infer the operator from examples, then apply it", is where ARC was actually solved:
test-time training on the demonstrations (Akyürek et al. 2024: 53% on the public validation set with an
8B model, 61.9% ensembled with program synthesis; every top 2024 transduction entry used it) and recursion
with deep supervision (TRM). The project's own closed-form solver reaching 100% is the test-time-regression
view in miniature. And the primitive was already in Part II: the pair moment `M_i = Σ_{jk} P_ijk V_j V_kᵀ`
is a matrix-valued output, an operator estimated from the context; the paper keeps only its diagonal (the
Hadamard value). Reading the full moment and applying it to the query's value, `M_i v_i`, turns cubic
attention into an in-context operator layer in one line. That is the fast-weight programmer (Schmidhuber
1992; Schlag, Irie, Schmidhuber 2021) with a context-selected outer product, and it is a far more natural
home for "higher order" than a trilinear score.

## 5. Tiny tweaks (cheap, each with a reason)

1. **Keep the pair moment.** Output `M_i` (d×d per head, or low-rank) and apply it to the query's value
   instead of taking `diag(M_i)`. Test on the swap programs and the algebraic ARC tier where the solver
   is 100%.
2. **Cascade, don't parallel.** Rebuild the combined layer as reset → compose → reset: softmax (with the
   short convolution) selects, a content-gated Householder product composes the selected values, and the
   composed state conditions the next selection. Random matrix initialisation throughout (the project's
   own finding). This is C done with B's initialisation discipline.
3. **Loop it, with loss at every loop.** Tie the block across R iterations, inject the input each
   iteration, add a few memory tokens, and put the loss on every iteration's output (TRM/Huginn recipe).
   Feynman attention's carry and sector balance already solve the two failure modes this hits.
4. **Supervise the intermediate state on the synthetic tasks.** Per-position loss on the running
   product (already done for word problems) and per-clause loss on ownership in the dilution task. Then
   ask whether the native term is still needed. This is the globality-barrier experiment.
5. **Measure the exponent.** Three sizes (about 20M, 60M, 150M non-embedding), a token-limited regime,
   downstream binding and state-tracking probes, the seed noise floor on the plot.

## 6. The program that would have led somewhere

Start from the brain premise and state it: few layers, recurrent, each unit multiplicative, fast
synaptic state. Translate: a small block iterated in depth with adaptive halting; per-token multiplicative
state (outer products for binding, non-commuting products for order) updated by a reset rule; higher-order
feature maps where capacity binds. Build the one layer that is the cascade of a content-gated reset and a
group composition (4.3), inside a looped block with deep supervision (4.1, 4.2), with polynomial key
features for capacity (4.4). Test it on binding-plus-composition tasks (4.5), on state tracking at length,
on ARC with test-time training (4.7), and on language across three scales for the exponent (4.6). Keep the
puzzles as diagnostics, not as the headline.

This is roughly where the frontier is converging on its own (DeltaProduct and Gated DeltaNet-2 for the
state; Ouro, Huginn and TRM for the loop; Atlas and the test-time-regression framework for capacity). The
project's instincts were right and several of its measurements are sharper than the published ones (the
exact order-blind ceilings, the learning-speed finding, the Householder determinant table, the dilution
quantification). What it lacked was the recurrence axis and the capacity/binding frame, and a protocol
that could see a scaling effect.

## 7. Specific edits to the paper

- Part I: state the brain motivation and what it actually implies (4.1), in two sentences, with Kar 2019
  and Beniaguev 2021.
- Part II–III: cut Part III to one section; keep the computation graph, the three training fixes and the
  pointer-chase result; say plainly that it is a looped, weight-tied block, which connects to 4.1.
- Part VI, "coordinates": reframe as the leap barrier applying to the read-out (section 1, point 1); say
  the experiment is equivalent to the baseline and what the separating experiment would be.
- Part IV, "characters law": say it is a Parseval property of pooled character features, explained in
  FORMALISM §4, not a learning law.
- Part VII: lead with "a matrix RNN plus a curriculum" rather than "the heads learn the group"; the
  irreps are a diagnostic, the capacity is prior art, the learning speed is the finding.
- Part VIII: add the cascade reading of A/B/C (4.3) as the explanation of why B passed and contributed
  nothing; add the Tencent and Roy thresholds to Part V's reading of the language results.
- Part IX: replace the diagnosis with the thesis of section 3 and the program of section 6; add 4.2's
  cure (intermediate supervision) and 4.7's primitive (pair moment) to "what we would try next".
- Related work: add Krohn–Rhodes/Barrington (constructive), dense associative memory, vector-symbolic
  binding (Plate, Gayler, Kanerva, Gallant–Okaywe, Hrrformer), looped language models and TRM, the
  globality barrier, Atlas and the test-time-regression framework.

## Sources

Looped / recurrent-depth models
- Closing the Loop: practical training recipes for looped LMs (2026): https://arxiv.org/html/2610.00673v1
- Towards Looped Models Done Right (Huginn vs Ouro ablation, 2026): https://arxiv.org/html/2610.23036
- Universal Transformers Need Memory (2026): https://arxiv.org/pdf/2604.21999
- Less is More: Recursive Reasoning with Tiny Networks (TRM, 2025): https://arxiv.org/abs/2510.04871
- Looped LM survey: https://www.preprints.org/frontend/manuscript/07176648ad0d1a09ab839b7c90c888b1/download_pub

Learnability
- Abbe, Bengio, Lotfi, Sandon, Saremi, How far can transformers reason? The globality barrier and inductive scratchpad (NeurIPS 2024): https://arxiv.org/pdf/2406.06467
- Barak et al., Hidden progress in deep learning (NeurIPS 2022): https://arxiv.org/abs/2207.08799
- Abbe, Boix-Adserà, Misiakiewicz, merged-staircase (COLT 2022): https://proceedings.mlr.press/v178/abbe22a.html

Automata, groups, state tracking
- Liu et al., Transformers learn shortcuts to automata: https://arxiv.org/pdf/2210.10749
- Rational Transductors (2026): https://arxiv.org/abs/2602.07599
- Barrington's theorem (lecture notes): https://people.cs.umass.edu/~immerman/cs601/BarringtonThmLect.pdf
- Complex KDA, incl. Theorem 4 (S5 obstruction for one layer, k ≤ 3): https://arxiv.org/html/2609.24797
- DeltaProduct (NeurIPS 2025): https://arxiv.org/pdf/2502.10297
- Gated DeltaNet-2 (2026): https://arxiv.org/pdf/2605.22791
- PaTH attention: https://arxiv.org/pdf/2505.16381
- Merrill and Sabharwal, A little depth goes a long way (NeurIPS 2025): https://arxiv.org/abs/2503.03961v2

Capacity, memory, test-time regression
- Krotov and Hopfield lineage; Lucibello and Mézard, exponential capacity of dense associative memories (PRL 2024): https://www.marcmezard.fr/wp-content/uploads/2024/01/2024-Lucibello-Mezard-The-Exponential-Capacity-of-Dense-Associative-Memories-PRL.pdf
- Biologically plausible dense associative memory with exponential capacity (ICLR 2026): https://arxiv.org/abs/2601.00984
- Wang, Shi, Fox, Test-time regression (JMLR 2026): https://arxiv.org/abs/2501.12352
- Behrouz et al., Atlas: https://arxiv.org/abs/2505.23735
- Behrouz et al., It's All Connected / Miras (ICLR 2026): https://arxiv.org/abs/2504.13173
- Schlag, Irie, Schmidhuber, Linear transformers are secretly fast weight programmers: https://arxiv.org/abs/2102.11174

Binding / vector-symbolic architectures
- Alam et al., Recasting self-attention with holographic reduced representations (ICML 2023): https://huggingface.co/papers/2305.19534
- Attention as Binding (2025): https://arxiv.org/abs/2512.14709
- Kleyko et al., VSA survey: https://arxiv.org/pdf/2111.06077

Higher-order attention and scale
- Roy et al., Fast and Simplex: 2-simplicial attention in Triton (exponent table, 2B threshold): https://arxiv.org/html/2507.02754v1
- Linearized 2-simplicial attention (2026): https://arxiv.org/abs/2608.09307
- Zhao et al. (Tencent), Most transformer modifications still do not transfer at 1–3B (2026): https://arxiv.org/abs/2605.20798
- Petty et al., The impact of depth on compositional generalization (NAACL 2024): https://arxiv.org/abs/2310.19956
- Kozachinskiy et al., Strassen attention: https://arxiv.org/html/2501.19215v3
- Chakrabarti, Pitassi, Alman, Poly-attention: https://arxiv.org/html/2602.02422v1

ARC
- Akyürek et al., The surprising effectiveness of test-time training for abstract reasoning: https://arxiv.org/abs/2411.07279v2
- ARC Prize 2024 technical report: https://arxiv.org/pdf/2412.04604

Neuroscience
- Kar, Kubilius, Schmidt, Issa, DiCarlo, Nature Neuroscience 2019: https://pmc.ncbi.nlm.nih.gov/articles/PMC8785116
- Beniaguev, Segev, London, Single cortical neurons as deep artificial neural networks (Neuron 2021): https://www.biorxiv.org/content/10.1101/613141v2
- Gidon et al., Dendritic action potentials and computation in human layer 2/3 cortical neurons (Science 2020): https://modeldb.science/254217

Group representations in networks
- Chughtai, Chan, Nanda: https://arxiv.org/abs/2302.03025v2
- Wu, Jaburi, Drori, Gross, unifying irreps and cosets: https://arxiv.org/abs/2410.07476
