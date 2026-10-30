You are auditing an experiment's code and records for bugs before anyone believes its results. Read-only; do not edit
files. Find shared helpers with grep and read them. Quote exact lines (file:line) for every claim.

For each checklist item give a verdict: **OK**, **BUG** (the fix and its effect on the numbers) or **DESIGN FLAW**
(what the result does and does not show). Then:
1. **Recompute every headline number** in the report independently from the raw records (runs.json / CSV / JSONL),
   with your own short script logic described in words, and say whether it matches.
2. Check that the verdict rules in code match the registered (frozen) predictions and falsifiers in the report.
3. Check for leakage: can any arm see the answer, the label, or test items during training or prompting?
4. Check fairness of comparisons: same budget, data, format, rank, steps, learning rate and selection rule for every
   arm that is compared; checkpoint selection only after every loss term is on.
5. Check that figures plot what their captions say.

Finish with: the BUGs by severity; which headline claims survive, in one line each; the minimal re-runs needed.
Be concise and exact.

## This experiment: SCAN (directory: research/scan)
Report: SCAN.md (and HANDOFF_PAGE.md). Code: scan_*.py, test_scan_algebra.py. Results: results/.
Headline claims to check:
- Certified carry-lookahead addition: tables D (digit pair to K/P/G), M (monoid), S (sum); packed forwards with a
  block-diagonal mask, shared Π KV, restarted positions; a margin certificate (max |Δlogit| < min margin) per row.
- 4,096-digit sums in about 2.2 s on H100, 100k digits in about 115 s, a 1,000,000-digit sum exact; the in-model
  associativity check flags 14/18 injected corruptions.
- Check: is every answer compared against an independent exact reference (Python int / BigInt), digit by digit?
  Is the certificate logic sound (does max |Δlogit| < margin really imply the packed forward equals the single
  forward for every row used)? Does the block-diagonal mask really isolate rows (no cross-row attention), and do
  restarted positions match the single-row forward? Is timing measured end to end with GPU sync, excluding or
  including compile/warm-up as the report says? Are the 18 corruptions a fair set, and is the 14/18 counted right?
