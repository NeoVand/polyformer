# PROGRAM brief: the work-order parser, decimals and algebra by evaluation (T6)

You write a pure TypeScript module, `src/lib/sketchpad/program/`, in the worktree `/Users/neo/repos/polyformer-wt/program`
(branch `program`). Read first: `research/meta/sketchpad3/CONTRACT.md` (rules, seams 2 and 3, your files), then
`research/meta/SKETCHPAD3.md` §3, then `research/sketch/calc_dryrun.py` (reference procedures and the cost model).
No Modal, no model, $0. Log: `src/lib/sketchpad/program/NOTES.md`. Tests: `pnpm vitest run src/lib/sketchpad/program`.
Lint: `pnpm exec eslint` and `pnpm exec prettier --check` on your files. Commit to `program` only; never push.

## The idea in one paragraph

A small vision-language model does every digit of arithmetic on a rendered sheet, one certified step per forward pass.
Another stream exposes that as `Calc` (integer `add`, `sub`, `mul`, `divmod`, `isqrt`, each a promise). The model, in
chat, writes a short *work order* (CONTRACT seam 3). You write the fixed runtime between the two: parse the work order,
lay out decimals and signs, schedule `Calc` calls, and solve polynomial equations **by evaluation**: never by symbolic
rewriting. The runtime must never produce a digit of an answer by its own arithmetic; every number in a result comes
out of `Calc`. (Counting digits, choosing evaluation points, comparing signs and moving decimal points are layout and
allowed. Anything else, route through `Calc`.)

## Files

- `calc.ts`: the `Calc` interface exactly as in CONTRACT seam 2; `RefCalc` (BigInt) that also records every call
  (op, operands, result) and its sheet cost, porting the cost formulas of `calc_dryrun.py` (`add_rows`, `sub_rows`,
  `mul_cost`, `divide`, `sqrt_digits`), and reports seconds with the model `0.065 s per call + 0.037 s per row`;
  `LyingCalc` (wraps another `Calc` and corrupts one chosen call's result) for the refusal tests.
- `parse.ts`: the grammar of seam 3 → a typed AST, with clear errors (the page shows them). Accept `× * ÷ / − - √ sqrt`.
  Also computes the syntactic degree of a polynomial expression in `x` (and in `x, y, z` for systems).
- `run.ts`: runs a work order on a `Calc`: expressions with precedence, names, decimals (scale to integers, then place
  the point), `to k places`, `gcd` (Euclid by `divmod`), integer `^` by repeated `mul`. Returns the result lines of
  seam 3 and a trace for display.
- `algebra.ts`:
  - **Coefficients by evaluation.** For `solve L = R`, let f = L − R. Evaluate both typed sides on the sheet at
    deg + 1 integer points plus one more that must confirm the degree (−1, 0, 1, 2, … ; points chosen by the runtime),
    and recover the coefficients by differences and exact division (`divmod` must leave remainder 0, else refuse).
  - **Linear:** x = −b/a in lowest terms (gcd on the sheet); a = 0 → "no solution" or "every x".
  - **Quadratic:** discriminant on the sheet; `isqrt` with remainder 0 → two rational roots in lowest terms; remainder
    ≠ 0 → the exact form (−b ± √D)/(2a) plus decimals to 6 places; D < 0 → no real roots.
  - **Degree ≥ 3 and `factor`:** guess, then prove. A guess may come from anywhere: use float64 roots of the recovered
    coefficients, rounded to nearby rationals p/q with q dividing the leading coefficient, and label guesses "not
    certified". The proof is on the sheet: synthetic division (Horner) of the coefficient row by (q x − p) with
    remainder 0; divide each proven root out and continue on the quotient. Say plainly which roots were found and that
    the check proves those roots, not that no others exist.
  - **Systems:** coefficients of each linear equation by evaluation at (0,0[,0]), the unit points, and one confirming
    point; Cramer's rule for 2×2, fraction-free elimination (Bareiss) for 3×3; a zero determinant → say so.
  - **`expand`:** Kronecker substitution. Bound the coefficients on the sheet (evaluate the expression with every
    coefficient made positive at x = 1), take B = 10^k with 10^k > 2 × bound, evaluate the typed expression at x = B on
    the sheet, and read the coefficients off in base B with signed digits (as `calc_dryrun.unpack`). Example:
    (x + 2)^5 → 1002^5 = 1 010 040 080 080 032 → 1, 10, 40, 80, 80, 32.
  - **The check, for every root:** substitute the root into the *typed* equation (not the recovered coefficients) on
    the sheet, with exact fractions (numerator and denominator through `Calc`), and require both sides equal. For an
    irrational root shown to 6 places, prove the bracket instead: f at the two 6-place bounds has opposite signs.
  - **Display data:** the coefficient grid (one column per power of x, one row per evaluation and per recovered
    coefficient) and the list of `Calc` calls, for the page to draw later.

## Tests (vitest, all on `RefCalc` with fixed seeds)

- Parser: every statement form of seam 3, ASCII spellings, bad input gives an error that names the token.
- 1,000 random expressions (integers and decimals, brackets, signs, powers): exact against a BigInt-rational oracle.
- 200 each: linear equations (x on both sides, brackets), quadratics (rational, irrational and no real roots), 2×2
  systems, 3×3 systems, expansions ((a x + b)^e and products, e ≤ 12), factoring of products of known linear factors:
  every answer exact and every check passing.
- 200 corrupted answers that must be refused: (a) a wrong root offered to the check; (b) a `LyingCalc` that corrupts one
  evaluation, where the degree check, the exact-division check or the root check must catch it. Report the fraction
  caught for (b) honestly; a miss is a finding, not a test to delete.
- A cost table in `NOTES.md`: median and 95th-percentile seconds per problem type under the cost model, next to the
  dry-run numbers in `research/sketch/calc_dryrun.md`.

## Done

All tests pass, lint and format clean, committed on `program`, and `NOTES.md` opens with a short report: what passed,
the refusal rates, the cost table, any grammar decision you had to make, and a **Glossary candidates** section.
