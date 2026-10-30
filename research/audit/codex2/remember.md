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

## This experiment: REMEMBER and REMEMBER-2 (directory: research/remember)
Report: REMEMBER.md (both rounds). Code: rem_*.py (round 1), r2_*.py (round 2). Results: results/, results2/.
Headline claims to check:
- Round 1: the pinned arm (table Π kept, history evicted, positions restarted) is exact on 80/80 runs over 10 machine
  families, 163,840 bitwise ticks; full-history arms fail. Check: what exactly the pinned context contains each step;
  whether the true state (rather than the model's own prediction) is ever fed back; how a "tick" is counted; whether
  the 10 families are distinct machines; whether the full-history arm uses the same table encoding and positions.
- Round 2: the "fair" arm shows only the pin is learnable at rank 1. Check what "fair" means in code, that all arms
  get identical training budgets and data, how "learnable" is decided, and the rank-1 adapter implementation.
