# Let the data choose the arity: research plan

Working plan for the paper behind the Report tab. Updated as results land.
Scope (decided with Neo, Oct 2026): algorithmic and synthetic suites only, no
language modelling; the Report is public as it grows; heavy runs on Modal
(budget about $200), browser-sized versions of every experiment in the app.

## Thesis

**Arity is algebra.** For zero-sum relations over a finite abelian group, the
label of a k-tuple lives entirely on degree-k characters, so it is invisible to
every score built from fewer tokens. Hadamard-product attention computes in the
group algebra: products are convolutions, pooling gives power sums, and rounds of
products and pools compute elementary symmetric polynomials (Newton's
identities). So arity need not be fixed in advance. It can be built by
composition, at a cost linear in sequence length for every k, with width |G|,
and that width is necessary for attention-style readouts. A layer that offers
the right primitives in one softmax (its own value, one token, two at once,
pooled modes, self-products, round conditioning) lets the data pick the arity.

## Theory: status

| #   | Result                                                                                                                                                   | Status                                                           |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| T1  | Proper-subset scores have equal class means on zero-sum relations (characters, with replacement)                                                         | Proved; demo in Report                                           |
| T2  | Degree-2 three-role poly-attention: double-centred pair logits are query-independent                                                                     | Proved                                                           |
| T3  | DS-PA tree expansion: weights are products of softmax weights, sum to 1, at most 3^R leaves (2^R without exchange); polynomial only under frozen routing | Proved                                                           |
| T4  | Shared intermediates: the exchange kernel has rank at most M, the Match-4 kernel rank Q, so M >= Q                                                       | Proved, restricted to that factorisation                         |
| T5  | Newton's identities in the group algebra count Match-k witnesses for every k in O((kn + k^2) Q)                                                          | Proved; checked against brute force (Python, 60 tables; TS spec) |
| T6  | Width lower bound: any query-independent summary read bilinearly needs width >= Q - 1                                                                    | Proof sketch (contexts {h, 0, ..., 0}); write out                |
| T7  | Leap/SQ: Match-k labels are orthogonal to all functions of < k tokens, so leap = k (Abbe et al.); explains "snapping"                                    | To write; cite Abbe, Boix-Adsera, Misiakiewicz 2023              |
| T8  | Order hierarchy: k-role poly-attention needs mHp >= Omega(n / (4^k k^k)) for Match_{k+1} (NOF disjointness, Rao–Yehudayoff)                              | Stretch; first check arXiv 2606.11673 does not already prove it  |
| T9  | Indexed pair-sum memory: all-query Match-4 in O(n^2); colour coding gives Match-k in O(n^ceil(k/2))                                                      | Classical construction (Alon–Yuster–Zwick); cite as such         |

Known pitfalls in collaborator drafts: the full logit tensor is NOT identically
distributed under matching and non-matching tuples (only single entries are);
cubic value aggregation is O(n^3 d), not O(n^2 d).

## Architecture: DS-PA v5 (what the theory says is missing)

1. Round conditioning: a learned round vector added to queries and keys (fixes tied 3-hop composition).
2. Sum-pooled modes with a vacuum sink: counts, not averages; empty buckets representable.
3. Self-products: a token's state times its own value (Hadamard powers for power sums).
4. Mode-mode and token-mode products in the same softmax (Newton recursion).
5. Keep: one softmax across sectors, sector potentials, RMS readout, absorbing carry.
   Rename before submission: "poly-attention" collides with Chakrabarti, Pitassi & Alman.

## Results so far (19 Oct 2026, three seeds each, balanced accuracy)

- Phase A (Match-k ladder): no operator without a native k-way term leaves chance for k >= 4.
  DS-PA with every Newton primitive stays at 50.0 on Match-4 at width 64, 128 and 192:
  composition is representable but not learned (the leap barrier, T1 + T7).
- Newton attention (polybench `--model newton`): complex phase features, leave-one-out power
  sums, Newton's identities, every arity up to K read out at once, O(nKr).
  Rank 256, four heads: SET 100, Match-3 100, smallest-arity 95.1 (best fixed-order 54),
  four-card SET 75.5, Match-4 70.6, Match-5 56.8 (only model above chance).
  Order capped below the task's arity gives exactly 50.0 (ranks 32 and 128).
  Width-matched cubic (0.52M) and standard 3L (2.4M) stay at chance on Match-4/5.
  Width is the lever (rank 8 -> 128: 54.7 -> 63.6 on Match-4); steps are not (6k vs 20k).
- Open: a read-out that shares weights across arities (0.79M of 0.96M params are read-out);
  why learned phases fall short of exact characters; routing for chain tasks.

## Experiments

Phase A, mechanism (Match-k ladder in Z_3^m, k = 2..6, m = 2..4; mixtures of k):

- Models: standard attention 1-4 layers, cubic, quartic (k = 4 only), Strassen, tree, DS-PA v4, DS-PA v5 and its ablations.
- Metrics: balanced accuracy, per witness count, learned sector mass per task (the arity the data chose).
- Width sweep around |G| (predicted phase transition, T6). Three seeds minimum.

Phase B, established benchmarks (numbers to beat):

- Match3 on HOMA's protocol (N = 6, 8; M = 30, 56): HOMA 0.993 / 0.925; pairwise 0.835 / 0.761. SET-in-5: RelConvNet 0.979 vs Transformer 0.563.
- CLUTRR graph, train k <= 3 test to 10: Edge Transformer 58.1 +- 2.8, EpiGNN 0.85, R5 0.97; Graphlog World 6: NCRL 0.702.
- CLRS-30 subset, strict protocol (train n = 16, test n = 64, 10k steps, batch 32, >= 5 seeds): Floyd–Warshall, SCC, LCS, Optimal BST; controls BFS, insertion sort, DFS. To beat: Edge Transformer 61.5 (FW), G-ForgetNet / Open-Book about 82.9 average; FloydNet 81.4 FW / 90.1 average on fixed data. Same encoder/decoder for every model (Pozgaj et al. interface confound).
- GraphQA triangle counting (Sanford et al. 2024): 60M transformer 40.5 on 100K examples.
- p-hop (Saunshi et al. 2025): 1 / 2 / 3 / 6 layers at p = 16: 48.9 / 68.8 / 97.2 / 99.9.

Phase C, browser: reduced versions of each suite in the app's jax-js engine.

## Budget (Modal)

| Phase                          | GPU-hours | Notes                   |
| ------------------------------ | --------- | ----------------------- |
| Replication baseline (87 runs) | ~3 (L4)   | running                 |
| Phase A                        | ~10       | L4 / A10                |
| Phase B                        | ~25       | H100 for CLRS and p-hop |
| Confirmatory reruns            | ~5        |                         |

## Must-cite and position against

Clift et al. 2020 (2-simplicial, virtual entities); Chakrabarti, Pitassi & Alman
ICLR 2026 (poly-attention); Dussolle & Lio 2512.15600 (N-simplicial, all-ones
key); Amiraslani & Gao 2603.11133 (HOMA); Chen et al. 2512.03377 (Nexus); FloydNet
2601.19094; Sanford, Hsu & Telgarsky 2023, 2024; Kozachinskiy et al. 2025;
Alman & Song 2024; Roy et al. 2025; Edge Transformer 2021; DIORA 2019; Pi-nets;
DeepSets and Wagstaff et al. 2019 (sum decompositions); Nanda et al. 2023 and
Chughtai et al. 2023 (Fourier features for group operations); Abbe et al. 2023 (leap).
