# PROGRAM, round 2: make the algebra fast enough to show live

Your round 1 (`src/lib/sketchpad/program/NOTES.md`) is correct, and its costs are honest: 22 s for a linear equation and
149 s for `(x+2)^5`, against 4 s and 23 s in the dry run. The demo needs every beat **under about 12 s** under the same
cost model. Same rules, files and branch as round 1 (`CONTRACT.md`, `PROGRAM.md`); $0; no model.

## Contract change (orchestrator, 30 Oct): waves

Add to `Calc` in `calc.ts`:

```ts
/** run independent jobs together: on the sheet their steps share forward passes, one wave */
wave<T>(jobs: (() => Promise<T>)[]): Promise<T[]>;
```

`RefCalc` costs a wave as: model calls = the largest call count of any job, rows = the sum of all jobs' rows. (Each
forward pass carries one step of every job still running; on the M4 a pass costs about 0.065 s plus 0.037 s per row,
so rows still cost and calls get shared.) The CALC stream is told to support mixed-operation waves on the sheet.

## Levers, in the order I expect them to pay

1. **Waves everywhere independence allows:** both sides of an equation, every evaluation point, the equations of a
   system, independent subexpressions, the determinants of Cramer's rule.
2. **Kronecker unpacking is reading, not division.** The coefficients of `P(10^k)` are its digit groups, a layout fact.
   Read them by position; only the signed-digit correction (a group above B/2 borrows from the next) needs sheet
   arithmetic, and only where it occurs. No `divmod` by the base.
3. **A light check by default, the strong one on request.** Light: the confirming evaluation point (already there) plus
   the root checked by Horner on the recovered integer coefficients, cross-multiplied (for p/q: `a_n p^n + … + a_0 q^n
   = 0`), integers only. Strong: today's exact-fraction substitution into both typed sides. Both stay tested; report the
   refusal rates of each on the same 200 + 200 fault populations. For `expand`, the light check is one extra point.
4. **gcd only when needed:** skip the reduction when the division leaves remainder 0.
5. **Small numbers first:** evaluation points in the order 0, 1, −1, 2, …; share powers of x and repeated
   subexpressions within a point; Horner's form for the recovered polynomial.

Keep the line: the runtime never makes an answer digit by its own arithmetic. Reading digit groups, placing points and
choosing points are layout; anything that changes a number goes through `Calc`.

## Done

The same correctness suites pass in both check modes; a cost table for the nine work orders of your round-1 comparison
plus `solve 2x+3y-z=1, x-y+2z=3, 3x+y+z=8` and `factor x^3-6x^2+11x-6`, light and strong, each with rows, calls (after
waves) and seconds; which beats are under 12 s and what the rest would need. Commit on `program`, update the top of
`NOTES.md`, and finish with the short report.
