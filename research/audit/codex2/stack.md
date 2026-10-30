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

## This experiment: STACK (directory: research/stack)
Report: STACK.md (design, invariant, registered predictions, results). Code: the stack job and forward code in this
directory, plus research/promptbox/pb_pin.py and research/scan. Results: results/ and the Modal records named in
STACK.md.
Headline claims to check:
- A canonical-KV pushdown policy on Savant r3: 488/488 rows certify zero-shot (Dyck-2, Dyck-4, Boolean).
- Every counted step is bitwise equal to its certified row, including depth 4,096 and 20,000-symbol inputs (135,078
  canonical steps).
- BBH boolean_expressions 250/250 with a host compiler (Python ast).
- Naive frames (keeping the original KV) differ from the canonical template and cause step errors.
- Speed: 24 ms/step on H100, 64 ms on L4.
- Check:
  - that the canonical frame really is history-independent on the counted path;
  - that the certificate covers every row the runs use (closed cover), including bottom, malformed and halting
    rows;
  - that the bitwise checks compare the right tensors;
  - what exactly the host does: compile, stack maintenance, operation application. State precisely which part of
    the computation is the model's.
  - Are the comparator arms (plain history with a host-supplied top frame; base thinking) fair and correctly scored?
  - Is any claim stronger than the evidence?
