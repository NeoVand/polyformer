# Deep Review 2 triage (24 Oct, on review_v2.pdf)

Verdict: the reviewer checked every theorem and found the theory mathematically sound; the strengths section names
the blindness theorem, the recipe, the cocycle and the transparency of the ledger. The weaknesses are real but
fixable. Nothing found invalidates a headline result. Three findings change claims and need experiments; the rest are
precision, protocol disclosure and consistency.

## A. Substantive (experiments; total roughly $70-100)
| # | Finding | Action | Owner | Cost |
|---|---|---|---|---|
| A1 | Closure in theory needs both the mean and the centred scale fixed; we fix only the raw norm (RMS), leaving their split free. | Add a centred-sphere closure arm h <- sqrt(d) N0(h) (FULL+Nc, and O+Nc) in every domain; if it holds, make it the main closure so theory and practice match; re-run the certificate analysis on it. | each domain session; theory | ~$15 |
| A2 | S5 picks mu per arm at length 256 (16x training), out of distribution, with shortest-word partners. | Re-run S5 with the protocol the text states: random-length partners, mu fixed at 1, no tuning; report the old row as a footnote. | invariance | ~$2 |
| A3 | In-model ladder: the canonical prefix at t > 16 is built from the interpreter's true state, and long transcripts are teacher-forced with true states, so "no label beyond 16" means no target label, not no state information. Runs also stopped at 81-92% of schedule on a time cap. | (a) Re-run coverage + self-distillation to the full schedule. (b) A genuinely label-free variant: build the canonical prefix from the student's own decoded state line (on-policy). Rewrite the claim precisely. | exec-d | ~$35 |
| A4 | Soft checker: the pair count fell 2.4x (5,000 to 2,088); a size-matched certified set is already not exact (0.943). The deficit is size plus selection, not selection alone. | Add certified controls at 1,058 pairs (consensus size); restate the reading. | lean-n-data | ~$1 |
| A5 | Prior work: Buitrago Ruiz & Gu, ICML 2025 (arXiv 2507.02782), "unexplored states", fix length generalisation by widening state coverage (noise or another sequence's final state). This is our coverage ingredient for recurrent models. | Cite prominently; position coverage as theirs, ours being the three-way recipe with closure and certified equivalence, its theory, and the in-model use. | literature, writer | $0 |

## B. Protocol and statistics (cheap)
- B1 Lean pilots read evaluation sets up to 1,024; report the untouched 4,096 column next to 1,024 everywhere (records exist).
- B2 Stories n = 128 and Lean n = 256 cannot certify 0.99 per seed; pooling seeds on one test set is not independent.
  Re-evaluate at n = 512 where checkpoints exist, else rerun.
- B3 Lean baselines (transformers, DeltaProduct) underfit at the training length; tune them to fit in distribution
  (and give DeltaProduct the fixed norm and next-state too), or present them as underfit. Fix the DP+I column mix-up.
- B4 Selection and validation: document sizes, frequency, and why some domains use final weights.
- B5 Frontier: identifiers are the API model ids (say so, with dates); fix 7 of 13 to the right count; rerun the
  429 call; frame Fig 6d as token cost and input format, not capability.
- B6 Lean readout rank: recompute the effective rank on active target tokens; the "no dark directions" claim may not
  hold, which touches the clause criterion.

## C. Theory precision (proofs session, $0)
"First order" wording (margin-free gradient and curvature, not floor-suppressed); Lemma 1.2(c) lower bound
(|u_j - u_y|); Theorem E at block boundaries vs within blocks; Theorem 2.1(ii) conditioning and the linear-recursion
hypothesis; Corollary 2.3 constant (4z^2); Prop 4.6 view closure, two-point contraction, N vs N0; P = 11 vs 7 tokens
and per-token averaging; Lambda >= 1; P_t defined before use; 944 visited classes; the continuous certificate in
tangent-space charts and with the RMS scale-split coordinate (or moot under A1); the Markov horizon bound's start
law, C^q, q >= 1 and Jordan blocks; overbar rendering.

## D. Text, consistency and Methods (writer + domain sessions, $0)
Distinguish the three theoretical conditions (coverage, closure, stiffness) from the three mechanisms varied in the
table (norm, next-state, equivalence). Table 1 footnotes for S5 and rerun variance. Fig 6 caption sentence on the
registered bar (gap vs margin). The consensus-teacher paragraph (it had no coverage; how its contexts were built; why
it fell). Methods details: event pooling for x_{t+1}; addition partner boundary cases; story partner construction;
the soft-checker prompt; Lean/S5 tracker architecture; S5 task and optimiser settings; arithmetic optimiser and time
budget; ladder positions and KL weight; H100 vs CPU for Lean; internal report tags to prose; define z at first use;
"tier-1". Ledger: PHE1 (needs seed 2), 19.4-F2 (results exist), totals 143 / 29, reused-record wording. Extended Data:
normed-run count (26, not 21), pendulum phase (the full recipe does lower phase error, 0.97-1.07 vs about 1.57: the
caption is wrong), Table 4 blanks and trimmed rows, Table 7 medians, Table 6 seed batches, empty cells.
Placeholders: authors, D'Amour et al. 2022 citation, duplicate reference list, "stif" typo.
