# Astra brief: what survives from the higher-order attention work (audit, 1 Nov 2026)

**Neo's words:** "I'm eager to go back and see what can survive from the work we have done and I think we may have made
mistakes and gotten bad results because AI makes mistakes ... Our Feynman and Newton stuff might have legs and are
innovative. They might have mistakes in them tho."

**Your job.** Be an adversarial auditor of the October 2026 higher-order attention results in
`/Users/neo/repos/polyformer`. Spend no money. Make no Modal runs. CPU checks on this Mac are allowed: `nice -n 19`,
small, at most 20 minutes each.

For every claim:
- find the code that produced it and the result files;
- check the math;
- look for bugs that could have produced a *false negative* (a null that was really a bug) or a *false positive*.

Write `research/meta/survive/AUDIT.md` (at most 250 lines) and commit only that file on main.

## Claims to audit, in priority order

1. **The language-model nulls.**
   - Newton branch on enwik8: 1.657 bpc against softmax 1.651.
   - Subset attention: 1.652 against 1.650.
   - The S0–S2 token-LM search and the S6 local-regression results: −0.4% / −0.75%.
   - **Specific suspicions to check, using git history of `research/lm.py` and the grids in `research/modal_run.py`:**
     - Were the power sums computed at `Precision.HIGHEST` in the runs that produced those numbers, or under TF32
       on the H100? The memory notes say TF32 breaks the cancellations, and that fix came later on 19 Oct than the
       first Newton LM run.
     - Did the Newton branch get keys and values at all?
     - Was the leave-one-out or causal masking right? A future-token leak or an over-masked branch both matter.
     - Were the arity normalisations right, and was float32 Newton stable at the sequence lengths used?
     - Was each arm given equal learning rate, warm-up and steps?
2. **Newton attention on Match-k / SET.**
   - The results: exact at rank 256; Match-5 84.8; the characters law, "exact iff all 40 characters of Z_3^4",
     accuracy ≈ 1/2 + F/80.
   - Check the task generators for label leaks and the balanced-accuracy computation. Is the characters law real or
     an artefact of the probe?
   - Files: `research/polybench.py --model newton`, the results under `research/results/`, `research/summarize.py`.
3. **Free-field formalism, `research/FORMALISM.md`.**
   - The generating function e^{μz} ∏_t (1 + z p_qt φ_t): softmax as one particle, subset attention, the Poisson
     vacuum and the walk sector.
   - Re-derive the identity. Run `research/test_sfa.py`. Check the claims "trilinear cubic is not a special case"
     and "m = 1 is softmax".
4. **Feynman attention (DS-PA, ids `dspa*`).** Pointer chase at 100% with 62k params against softmax at 154k. Check
   for parameter-count fairness and leaks.
5. **The coupling barrier and order-k blindness.** For degree-2 forms, the double-centred logit matrix is
   query-independent. Prove it or refute it.
6. **The Nerode metric loss under dilution** (`research/METRIC.md` on branch `claude/metric-0160e1`, if present).
   - Does L_M average over random futures where Nerode quantifies over all? Say exactly how the pairs and the
     question were sampled.
   - Could under-training or a bug explain the "first owner" result?

## Output format

For each claim give:
- one line stating the claim;
- the evidence: code and result files, with commits;
- what you checked;
- each bug found, its severity, and whether it plausibly changes the conclusion;
- a verdict: HOLDS, DOUBTFUL or BROKEN;
- the cheapest re-run that would settle it, with an estimated cost on Modal.

End with a ranked list: "the three results most likely to have legs once fixed", with reasons. Label anything you
did not verify as unverified. Never print keys or tokens. Use `/bin/rm` and `/bin/cp -f`.
