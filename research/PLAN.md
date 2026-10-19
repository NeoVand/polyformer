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
- Read-out fix (newton_c, newton_e): normalising each arity's features to unit RMS before the
  read-out (`--fnorm 1`) is the change that matters; sharing one read-out across arities with a
  per-arity scale (`--readout shared`) cuts params 0.96M -> 0.30M. Rank 256, shared + normalised:
  SET 100, four-card SET 99.9, Match-3 100, Match-4 100, smallest-arity 100, Match-5 84.8.
  Rank 512: Match-5 97.5 (shared) / 98.1 (own read-outs), three of six seeds exact.
- Knockouts on the fixed layer: Match-k depends on arity k alone; smallest-arity on exactly 3, 4, 5.
- Characters: across 93 probed runs, a run is exact iff it has all 40 characters of Z_3^4 (up to
  conjugation); on all 74 Match-k runs balanced accuracy is within 5 points of 1/2 + found/80
  (r = 0.997). Unexplained: why linear.
- Transfer (newton_d, newton_f): one layer on Match-3/4/5 together (first token announces k),
  each arity a third of the data. Own read-outs: 89.5 / 84.2 / 82.7 vs alone 100 / 70.6 / 56.8.
  Shared + normalised, rank 256: 100 / 100 / 100 on every seed (Match-5 alone: 84.8).
- Match3 on HOMA's protocol (homa_m3, details under Phase B): accuracy, three seeds, N = 6 / N = 8.
  Newton at HOMA's parameter count (rank 24 / 84, 28k / 91k): 100.0 / 99.8 (HOMA 99.3 / 92.5).
  Standard 1L: 84.4 / 74.6 (their pairwise at the same widths 83.0 / 73.1), so the protocol reproduces.
  But cubic (27k / 107k): 99.9 / 99.7, so the margin over HOMA is our third-order block, not Newton.
  Standard 2L 98.3 / 81.1, 3L 99.4 / 76.4. Newton rank 256: 99.9 / 99.8. Knockouts: arities 1-3 used
  (repeats make 2x_i + x_j and 3x_i relations of fewer tokens), 4-6 unused.
- Language model (lm.py, lm_a): enwik8 bytes, 4 layers, d 256, ctx 256, 8k steps, 3.3M params,
  three seeds. Softmax 1.651 bpc; softmax + causal Newton branch 1.657; Newton only 2.497.
  No gain on text: Newton attention has no keys/values, so no retrieval.
- Open: why accuracy is linear in characters found; width needed vs arity and group; routing
  for chain tasks; a query-dependent selection of which tokens enter the subsets; transfer
  between different relations, not just arities of one group.

## Experiments

Phase A, mechanism (Match-k ladder in Z_3^m, k = 2..6, m = 2..4; mixtures of k):

- Models: standard attention 1-4 layers, cubic, quartic (k = 4 only), Strassen, tree, DS-PA v4, DS-PA v5 and its ablations.
- Metrics: balanced accuracy, per witness count, learned sector mass per task (the arity the data chose).
- Width sweep around |G| (predicted phase transition, T6). Three seeds minimum.

Phase B, established benchmarks (numbers to beat):

- Match3 on HOMA's protocol (N = 6, 8; M = 30, 56): HOMA 0.993 / 0.925; pairwise 0.835 / 0.761 (done, see below and Results). SET-in-5: RelConvNet 0.979 vs Transformer 0.563.
- CLUTRR graph, train k <= 3 test to 10: Edge Transformer 58.1 +- 2.8, EpiGNN 0.85, R5 0.97; Graphlog World 6: NCRL 0.702.
- CLRS-30 subset, strict protocol (train n = 16, test n = 64, 10k steps, batch 32, >= 5 seeds): Floyd–Warshall, SCC, LCS, Optimal BST; controls BFS, insertion sort, DFS. To beat: Edge Transformer 61.5 (FW), G-ForgetNet / Open-Book about 82.9 average; FloydNet 81.4 FW / 90.1 average on fixed data. Same encoder/decoder for every model (Pozgaj et al. interface confound).
- GraphQA triangle counting (Sanford et al. 2024): 60M transformer 40.5 on 100K examples.
- p-hop (Saunshi et al. 2025): 1 / 2 / 3 / 6 layers at p = 16: 48.9 / 68.8 / 97.2 / 99.9.

Match3 on HOMA's protocol (grid `homa_m3`, tasks `match3_n6` / `match3_n8`). Every detail we rely
on and where it is stated in Amiraslani & Gao, arXiv 2603.11133 v2 (24 Sep 2026). No code is public
(App. H describes an anonymised package; none is linked), so the generator follows the text.

- Label (Sec. 3.1, after Sanford et al.; App. D.1): y_i = 1[exists j, z: x_i + x_j + x_z = 0 mod M], j and z
  over the whole sequence, "may equal each other or i". Our `task_match3_homa` uses exactly this.
- Tokens: uniform on Z_M. Implied, not stated: D.1 calibrates M "for approximately uniform tokens",
  Pr(y = 0) ~ exp(-L_N / M) with L_N = N(N+1)/2. Check: our positive rates are 0.534 (N = 6) and 0.475
  (N = 8), inside their stated majority-class range 0.500-0.540 (App. A) and "within 0.04 of 0.50" (D.1).
- Sizes (Table 2, D.1): N = 6 with M = 30, N = 8 with M = 56. No BOS token; every position labelled
  (Table A.1, "per position").
- Data (Table A.1): 30,000 train, no validation, 2,000 test sequences; "independent train and test streams
  for each seed" (App. A). We draw a fixed train set per seed and a test set from a separate generator.
- Optimisation (Table A.3): Adam, lr 3e-3, weight decay 0, no schedule, no clipping, batch 256, 40 epochs,
  CE loss, seeds 0, 1, 2. Steps: 40 x ceil(30000 / 256) = 4,720 (we keep the short last batch; whether
  they drop it is not stated).
- Metric (Table A.3, App. B): plain accuracy over labelled test positions at the last epoch, no checkpoint
  selection; chance 0.50. Mean +- sample sd over three seeds (App. H). We report `tok_acc`.
- Model (Sec. 3.1, Table A.2, App. A): one attention layer, 4 heads, no FFN, linear 2-way head, a frozen
  sine-cosine Fourier feature then a learned projection, no positional embeddings. The Fourier size is
  not given; D.1 says a complete basis needs about M - 1 coordinates and that their widths include one,
  so we use the complete real basis (M - 1 coordinates) at every width. Residual connection and LayerNorm
  are not stated for Match3; ours keep the harness's pre-LN residual block and final LN for every model.
- Their numbers (Table 2 / D.2, mean +- sd): HOMA best 0.993 +- 0.002 (N = 6, d = 64) and 0.925 +- 0.008
  (N = 8, d = 128); HOMA-add 0.990 / 0.921; Blockwise-3D (pure triadic) 0.958 +- 0.008 (d = 64) /
  0.912 +- 0.004 (d = 128); pairwise best 0.835 +- 0.001 (d = 32) / 0.761 +- 0.009 (d = 64), and at HOMA's
  widths 0.830 +- 0.003 (d = 64) / 0.731 +- 0.012 (d = 128).
- Parameter budget (our estimate; Match3 counts are given only as ratios to pairwise): from Table C.2,
  HOMA minus pairwise is exactly 16d + 385d/4 + 128 at d = 8, 16, 32, 64 (low-rank U of rank 8 plus a
  fusion MLP 2d_h -> 128 -> d_h shared by heads). With Table 2's ratios (1.60x at d = 32, 1.19x at d = 128)
  and the pairwise layer at d = 64, HOMA's best runs have about 28k (N = 6) and 91k (N = 8) parameters.
  Newton attention at width 64 with rank 24 has 27.5k and with rank 84 has 91.1k.

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
