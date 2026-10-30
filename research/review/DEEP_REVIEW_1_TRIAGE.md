# Deep Review 1 (Google, AI-generated, 24 Oct 2026): triage

Checked against our code, reports and proofs by the orchestrating session. Verdicts: AGREE (act), PARTLY, DISAGREE.

## Could change a claim (do first)

| # | item | verdict | evidence checked | action | cost |
|---|---|---|---|---|---|
| 1 | Headline lacks a factorial: on the frozen-code-model task we never ran ordinary + fixed norm, next-state alone (± fixed norm), signal alone (± fixed norm) | AGREE, highest risk | Table 1 / S4 jump from ordinary to signal+next-state | 5 arms × 3 seeds on Modal CPU, registered before launch; if ordinary + fixed norm is exact, the headline's credit moves to the norm | ~$20–25 |
| 2 | Theorem 3: assumption (c) (next-state prediction) is logically redundant given (b) on all of U and (e); the clock counterexample violates (e), not (c); the main text credits next-state prediction with stopping the clock, but the clock persisted until the fixed norm | AGREE | reproduced the reviewer's argument on PROOFS2 Thm 2.4's proof: z(ux)=z(u'x) follows from w(u')=w(u) alone | restate Thm 3 with closure as the crux; the fixed norm is the architectural form of closure on the scale fibre (a cleaner, predictive story); give next-state prediction its real role (right congruence when pairs are sparse, Thm 2.1); fix the counterexample; rewrite abstract, p. 3, Box 1 | $0 (theory session) |
| 3 | Missing closest prior art: Hint-ReLIC (Bevilacqua et al., ICML 2023, arXiv 2302.10258) enforces invariance across inputs with the same next algorithmic step; also DeltaProduct (2502.10297) and PD-SSM (2509.22284) for architectural state tracking | AGREE (all three verified real) | not in NOVELTY.md or the paper | cite and differentiate; rewrite the "none of these" sentence, crediting next-latent prediction's extrapolation in our own Table 1 | $0 |
| 4 | Abstract places the Markov-step LM result beside the method, but it uses neither the signal nor a latent state, and its exactness relies on overwrite repair | AGREE | EXEC_LM §10.3 | move out of the abstract or frame as a diagnosis of chain of thought; say "repair" plainly | $0 |
| 5 | Markov result confounded: uniform states and train-in-cut-context changed together; key baselines single-seed; seed-10 pilot rows contradict the stated seed protocol | AGREE | EXEC_LM §7.6, §10.3; Methods p. 16 | control: single-step training in the cut context on zero-start states, 3 seeds; rerun the single-seed baselines at seeds 0–2 or label them as pilots | ~$8–12 |
| 6 | Register state never run with ordinary training, so the signal's contribution there is unmeasured | AGREE | EXEC_LM §7.7, §10.2 | registers, ordinary training, 3 seeds | ~$6 |

## Fair and cheap (text, or small runs)

- Prover framing: temper to closed finite domains; explain why the within-proof negatives let a first-word table reach ~0.7 (AGREE).
- Drift diagnostic is measured at 16–32× the training length, not within it; pooled ρ mixes objectives. Report the within-objective ranking we already have (growth vs drift within R's six seeds: Spearman 0.94, MECHANISM §7) (AGREE).
- Transformer control uses RoPE; add a NoPE variant (PARTLY: LEAN_H already swept depth and steps to 8× compute; position encoding not swept) (~$3).
- Next-state predictor reads LN([e, h]) on the raw state, so it can see the scale it should not; specify and consider LN(h) first (AGREE, and it explains item 2's empirical clock).
- Data-scaling caveat (80k chains, μ = 3 trade-off) belongs in the main limitations (AGREE).
- "Exact" = ≥ 0.99 final state: keep, but report "never wrong along the way" beside it (we have it) (PARTLY).
- Proof fixes: local Hessian bound 2s in Lemma 2(b) (verified: Var_p(v) ≤ 2s‖v‖²) restoring s̄ in Thm 1(ii)/(v) and Thm 2(iii); N vs N₀ scaling; state-autonomous S5 construction; Thm 4 initial condition and block-boundary wording; p_w = p/ω and "uniform operands" stated (AGREE, all).
- Reproducibility details: heads, widths, weight decay, schedules, precision, partner mixtures for programs, register β parametrisation (soft attention, per EXEC_LM §7.7) (AGREE).
- Natural-proof table: probe counts per bin, bootstrap clustered by proof (it is, per D1_AUDIT), missing intervals (AGREE).
- Typos, notation collisions (m, μ), subscripts, the internal verification log after the references (AGREE).

## Where the review is wrong

- Rewrite-chain partners are not palindromic w w⁻¹ backtracks. `reverse_partner` in `lean_chains.py` walks m steps away from the end tree and replays the inverted walk forward from its far end, so the partner starts at a different expression, has its own length, and ends at the same tree: a non-trivial certified loop (generator also has `comm; comm` detours and disjoint swaps). Our Methods sentence ("replaying the walk backwards") invited the misreading; rewrite it.
- "Lean 4.35.0 is not a real version": it is the current toolchain on this machine; natural proofs used v4.10.0-rc1 because the LeanDojo benchmark pins it. Say so in Methods.
- "Active synthesis vs passive verification": fair framing note, not an error; canonical program partners do encode final values as input syntax, which we should state.

## Proposed order and spend (needs Neo's word: ~$40–50)

1. Item 1 factorial (decides the headline's attribution). 2. Items 5 and 6 controls. 3. NoPE transformer. 4. Theory rewrite (item 2) in parallel at $0. 5. All text fixes after the runs, then a second deep review.

## Dispatched (24 Oct, Neo: "Get it started. All costs are approved.")

- exec-d session (EXEC_LM §11, cap raised to $160 in all): headline factorial (ordinary + fixed norm; next-state alone ± norm; signal alone ± norm; 3 seeds); Markov confound control (single steps in the cut context on zero-start states, 3 seeds); 3-seed reruns of the single-seed rows; registers with ordinary training (3 seeds); reproducibility details.
- lean-h session (LEAN_H §8, cap $25): NoPE transformer (depth 4 and 8, 3 seeds); DeltaProduct (or PD-SSM) baseline with and without the signal, 3 seeds.
- proofs session ($0): Theorem 3 rework with closure as the crux and the fixed norm as architectural closure; proof fixes; related work (Hint-ReLIC, DeltaProduct, PD-SSM, next-latent credit); all text-only items; run-dependent numbers held as placeholders.
