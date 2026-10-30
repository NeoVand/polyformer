Round 2 in progress. No new timing or refusal claims yet.

The orchestrator now permits waves: independent jobs share model passes, while their row costs add. The implementation will keep the supplied arithmetic costs fixed, use a light check by default, and retain strong checks. A wave saves waiting between independent calculations; it does not make their digit work free. The glossary candidate for this term is recorded below. No spending or model calls are planned.

## Round 1 archive

Passed: 49 tests covering 1,000 expressions, 200 each of six algebra families, and 150 reference-cost comparisons. TypeScript, ESLint and formatting checks pass.

Refusals: wrong roots 200/200 (100%); corrupted evaluations 168/200 (84%). The 32 missed faults left the answers unchanged; this is not a guarantee against arbitrary corruption.

Modeled seconds below show the median (middle case) and the 95th percentile (95% of cases at or below it), to expose typical and slower cases. Dry-run figures are simpler examples, not matched populations.

| Problem          | Median s | 95th s |     Prior dry-run s |
| ---------------- | -------: | -----: | ------------------: |
| Expressions      |    118.9 |  433.6 | No matched workload |
| Linear equations |     70.7 |  105.4 |                 4–8 |
| Quadratics       |     84.4 |  975.2 |                  29 |
| 2×2 systems      |     76.0 |  104.6 |                   5 |
| 3×3 systems      |    315.1 |  425.0 |        Not measured |
| Expansion        |    722.1 | 3219.4 |              21–118 |
| Factoring        |    209.8 |  651.7 |        Not measured |

Decisions: accept implicit multiplication and higher-degree solving; truncate decimals; keep unproved factors visible. Correctness passes, but these costs miss the short-demo target. Spend: $0. Changes committed only on `program`; nothing pushed.

## What ships

`index.ts` exports the parser, runner, Calc implementations, and display types. Production code in this folder is pure TypeScript with no browser, model or network dependency. `RefCalc` is a native-BigInt test double, not a trained model. Pass the CALC stream's implementation of the identical `Calc` interface to use the sheet.

```ts
import { RefCalc, run } from '$lib/sketchpad/program';

const calc = new RefCalc();
const output = await run('solve 3(x-2)+5=2x+14', calc);
// output.lines: ['= x = 15']
// output.results[0].algebra: recovered coefficients, grid, checked roots
// output.trace: every Calc invocation, operands and result
// calc.total: predicted sheet rows, model calls and seconds
```

`run` returns one `= ...` line per statement, per-line traces and a combined trace. Parse errors throw `ParseError` with a token and location, for the page to display. Arithmetic domain errors become `= error: ...`; failed checks become exactly `= check failed`, with no claimed algebra result. A failed assignment removes its old binding before later statements run.

`AlgebraResult` exposes ascending-power coefficients, grids, exact rational roots, exact bracket bounds for irrational roots, checks, unproved guesses and remaining factors. Systems return roots in x/y/z order. `factors` contains the actual proved `(q x - p)` factors, including multiplicity; multiplying those by `remaining` reproduces the recovered polynomial. Higher-degree results always set `complete: false`, even when the remaining factor is constant, to preserve the contract's conservative wording.

The runtime creates no arithmetic answer digits with host arithmetic. Sign changes, digit counts, decimal-point placement, loop counters, point selection and the explicitly untrusted root-search stage use host layout/control. All coefficient recovery, fractions, determinant arithmetic, exact divisions, root checks and signed unpacking use `Calc`. Integer results are already digit rows and need no arithmetic merely to display them.

## Grammar and precision decisions

- ASCII `* / - sqrt(...)` and Unicode `× ÷ − √(...)` share the same syntax. A work order may be plain text or a complete `sheet` fence. Statements occupy separate nonblank lines.
- Implicit multiplication is accepted before a name/function or `(`: `2x`, `3(x-2)`, and `(x-1)(x+2)`. Multiplication and division associate left to right, including implicit multiplication. Adjacent numeric literals are errors.
- Powers bind more tightly than unary minus. Exponents are signed literal integers with magnitude at most 12; polynomial exponents must be nonnegative. Products can have total degree above 12. An exponent expression such as `2^(1+2)` is rejected. `0^0` follows the empty-product convention and is 1.
- `x`, `y`, and `z` are reserved unknowns and cannot be assigned. Other names hold earlier numeric results. A single equation uses x; systems use x/y or x/y/z. Systems must be syntactically linear even when nonlinear terms would cancel.
- The seam limits single-equation solving to quadratics, while PROGRAM explicitly requests higher-degree solving. The implementation follows the more specific brief and marks higher-degree results as incomplete.
- `to k places` accepts 0 through 100. Each division and square root truncates toward zero to that precision; the final line is padded to that precision. Without the suffix, each division/root remains exact if it terminates within 12 places, otherwise truncates to 12. An ellipsis propagates after any truncation. Addition, multiplication and powers operate on those resulting values. A finite literal may contain more places, but default display still uses at most 12.
- Algebra evaluation always uses exact fractions, ignoring expression-display precision. An approximate named value is refused. Fractional coefficients are supported for solving and systems. Recovery on integer syntax uses exact factorial division; fractional syntax carries an exact numerator/denominator and checks each reduction division has remainder zero.
- `expand` and `factor` accept integer literal coefficients, integer-valued names, signs, sums, products and nonnegative powers. Direct decimal literals and division are rejected there; this syntactic restriction guarantees the integer-coefficient premise needed by packing. A separately assigned exact integer can be used as a coefficient.
- A zero determinant reports that there is no unique solution; it does not distinguish inconsistency from infinitely many solutions.
- Six-place irrational roots are displayed as an exact radical form plus adjacent six-place bounds. Both bounds are checked in the original equation with exact fractions. If two close roots occupy the same six-place cell, the opposite-sign check can fail; the runtime refuses rather than displaying an unproved decimal. A directed test covers that case.

Assumptions not supplied by Neo: truncation rather than rounding to nearest; reserved unknown names; a 100-place display cap; literal-only exponents; bounded candidate search. Rounding to nearest could also preserve model computation, at additional arithmetic cost. Retaining exact fractions through ordinary expression division would reduce some work but would change the seam's per-operation precision rule. Unlimited candidate search could find additional factors but would worsen the live-demo constraint (condition 11).

## Procedures and their limits

Coefficient recovery evaluates both typed sides at degree + 1 points starting at -1, then uses the next point as confirmation. Successive differences and numerical Newton basis conversion recover the coefficient row; this never rewrites the typed expression. The grid includes evaluated powers, both sides, differences and recovered coefficients.

The linear and quadratic formulas run on Calc. A rational root is reduced by Euclid's gcd and checked by exact substitution in both typed sides. A quadratic with a nonsquare discriminant uses extra root digits to locate a six-place interval, then checks opposite signs in the typed equation. Negative discriminants report no real roots.

Two-variable systems use Cramer's rule. Three-variable systems use Bareiss elimination with row swaps and exact division, then exact back-substitution. Each equation is evaluated at the origin, its unit points and a separate confirming point. Every returned solution is substituted into every original equation.

Expansion uses a positive-coefficient bound evaluated on Calc, chooses a decimal base strictly larger than twice that bound, and evaluates the typed polynomial at that base. Signed base digits are unpacked through Calc. The recovered polynomial is checked at -1, 0, 1 and 2. Both the bound and packed evaluation appear in the display grid.

Higher-degree solving and factoring propose real roots using ordinary approximate JavaScript numbers. The search splits intervals using derivative-root candidates, then tries nearby rational values with denominators up to 256 that appear to divide the leading coefficient. These are explicitly labeled “not certified.” Exact synthetic division by `(q x - p)` and substitution into the original typed equation must both pass before a root is reported. Large roots outside safe JavaScript integer range, larger denominators, numerical instability and unfound irrational roots can remain unproved. Their quotient stays visible; no completeness claim is made.

The arithmetic boundary is a trusted Calc implementation. A confirming point is a consistency check, not an adversarial certificate for the provider. One corrupted intermediate value can be multiplied by zero and disappear. A malicious provider changing several coordinated calls can evade these checks. The tests do not claim otherwise.

## Validation and reproducibility

The population harness uses independent native-BigInt rational arithmetic for expressions and linear equations, independent determinants for systems, coefficient convolution for expansions, and known factor products for factoring. Quadratics include 67 rational-root, 67 irrational-root and 66 no-real-root cases. Irrational brackets are checked independently with integer cross-products. Factoring checks multiplicities and reconstructs the full coefficient row from the proved factors and remaining scalar.

The frozen cost vectors contain 30 cases for each of addition, subtraction, multiplication, division and square root. They were generated with Python seed 39; `verify_costs.py` rereads the actual reference procedures and checks all values, rows and calls without writing outside this folder. The reference square-root normalizer has no zero case; `RefCalc` uses one halt row for zero, covered separately.

The two fault populations are separate: 200 deliberately wrong offered roots, then 200 single-call `+1` corruptions inside the first typed evaluation of mixed linear/quadratic equations. The latter deliberately includes zero-masked arithmetic. Every injected call is reached; every miss, source statement and call index is preserved in `metrics.json`. Misses were compared with the uncorrupted run's exact result line, and all were unchanged. This sampling is not a claim about corruption of every possible call or operand.

`metrics.json` contains the fixed seeds, population sizes, full-precision statistics, exact-demo row/call totals and all misses. Median uses the mean of the two central costs; the 95th percentile uses the nearest-rank rule. Final population runs reproduced the same unformatted metrics SHA-256:

`ec003320ad8b14ebd074189333642e9b3bab56bf88e1d9b7ac53b1a2e764cb8e`

Prettier changes whitespace in the committed JSON; rerunning the reporting command restores the reproducible unformatted bytes. All model estimates use `0.065 × calls + 0.037 × rows` seconds. Here “calls” means model forward passes in the ported sheet procedure, not the number of high-level Calc invocations. No measured model latency or model accuracy is claimed.

Commands, from this worktree root:

```sh
PROGRAM_REPORT=1 nice -n 19 pnpm vitest run src/lib/sketchpad/program
nice -n 19 python3 src/lib/sketchpad/program/verify_costs.py
nice -n 19 pnpm exec eslint src/lib/sketchpad/program
nice -n 19 pnpm exec prettier --check src/lib/sketchpad/program
nice -n 19 pnpm exec tsc --ignoreConfig --noEmit --target es2022 --module esnext --moduleResolution bundler --types node --strict --skipLibCheck src/lib/sketchpad/program/*.ts
```

The isolated TypeScript command checks this stream without generating or changing Svelte project files. No dev server or watch process was started. No model or paid service was used.

## Same-example cost comparison

The earlier figures below are reread from `research/sketch/calc_dryrun.md`, states left on the GPU. They are rounded to whole seconds in that source. This runtime includes the actual typed evaluations, coefficient recovery, exact fractions, checks, display grid arithmetic and decimal formatting. The source's algebra estimates simplify or omit some of those steps. These differences explain why the comparison is not a model-speed regression measurement.

| Work order                   | Rows | Model calls | Runtime s | Prior dry-run s |
| ---------------------------- | ---: | ----------: | --------: | --------------: |
| `123456 * 654321`            |   96 |          46 |       6.5 |               7 |
| `solve 3(x-2)+5=2x+14`       |  224 |         217 |      22.4 |               4 |
| `solve 7x+13=2026-4x`        |  394 |         361 |      38.0 |               8 |
| `solve 2x+3y=7,x-y=1`        |  252 |         246 |      25.3 |               5 |
| `expand (x+2)^5`             | 1803 |        1271 |     149.3 |              23 |
| `expand (2x-3)^4`            | 1808 |        1231 |     146.9 |              21 |
| `expand (x+1)^10`            | 8264 |        4366 |     589.6 |             118 |
| `solve (2x-3)(x+5)=x^2+1-16` |  516 |         484 |      50.6 |              29 |
| `solve x^2-x-6=0`            |  392 |         358 |      37.8 |              29 |

The same-width product matches the ported reference cost exactly before display rounding. The general algebra procedures are too expensive for the plan's short live-demo target. No training money should be spent on the assumption that the earlier simplified estimates describe this scheduler. Optimizing the schedule and reducing grid-only arithmetic are follow-up choices for the parent stream, not evidence of a faster model.

## Scope, alternatives and commit record

This stream changes only `src/lib/sketchpad/program/`, on branch `program`, and never pushes. The contract assigns shared-glossary edits to the orchestrator; candidates below are ready to lift. No other worktree or branch was touched.

The field is computer algebra. The plan's standard alternatives are symbolic rewriting and recovery by numerical evaluation. This stream implements evaluation as instructed. Host-side answer arithmetic would be faster but breaks condition 2 (the model computes). A single confirming point protects against some accidental errors, but claiming arbitrary-provider certification would break condition 5 (checkable exactness). Presenting these costs as a fast live demonstration would conflict with condition 11. These limitations remain visible.

Small implementation/test commits:

- `8ea40f54`: parser, arithmetic, traced reference Calc, Python-derived cost vectors and initial notes.
- `8767226b`: evaluation-based algebra, runner, exports and integration cases.
- `62805cb9`: precision edge cases, polynomial grammar boundaries and redundant integer-work removal.
- `a79fcde9`: seeded acceptance populations and live Python cost verification.

The final report/metrics commit completes the stream. There are no remote pushes.

## Glossary candidates

- **Computer algebra:** computation with mathematical expressions and equations. A long-established field; the SKETCHPAD3 plan (30 Oct 2026) chooses evaluation over rewriting for this runtime. It frames the alternatives without inventing a new field.
- **Rational number:** an integer numerator divided by a nonzero integer denominator. Classical arithmetic, used throughout this implementation (30 Oct 2026) to check equations without decimal rounding.
- **Interpolation [zoo]:** recovering polynomial coefficients from values at chosen points. The plan cites black-box polynomial work by Kaltofen and Trager (1990); this implementation uses classical successive differences and numerical Newton basis conversion. It permits coefficient recovery using Calc alone.
- **Finite differences / Newton basis [zoo]:** successive adjacent differences of a value table, expressed in products associated with chosen evaluation points. Classical numerical methods, implemented here on 30 Oct 2026; they recover coefficients without rewriting the user's expression.
- **Kronecker substitution [zoo]:** packing polynomial coefficients into digits of one sufficiently large integer. The plan credits Kronecker (1882); this stream uses its integer-coefficient premise to expand by arithmetic and signed digit extraction.
- **Synthetic division / Horner [zoo]:** dividing or evaluating a coefficient row by repeated multiplication and addition. Named in the PROGRAM brief (30 Oct 2026); used to prove proposed linear factors and to evaluate recovered coefficient rows.
- **Cramer's rule [zoo]:** solving a square linear system using ratios of determinants. Named in the SKETCHPAD3 plan (30 Oct 2026); used for two unknowns.
- **Bareiss elimination [zoo]:** elimination using exact integer divisions to avoid growing fractions. Named in the SKETCHPAD3 plan (30 Oct 2026); used for three unknowns, including row swaps.
- **Bracket [zoo]:** two bounds where a continuous function has opposite signs. The classical intermediate value theorem guarantees a root between them; this implementation (30 Oct 2026) uses exact arithmetic to check displayed irrational-root bounds.
- **Float64 candidate:** an approximate number in JavaScript's ordinary numeric format. Used only in the candidate search implemented here (30 Oct 2026), never accepted as a root without exact proof.
- **Median / 95th percentile:** respectively the middle measured cost and a cost covering at least 95% of the population. Standard descriptive statistics; the report generated here (30 Oct 2026) uses them to expose typical and slower predicted workloads.

- **Wave [zoo]:** independent sheet jobs sharing model forward passes; authorized by the orchestrator in PROGRAM2 (30 Oct 2026). Its call count is the longest job, and its row count is the sum, so it reduces scheduling cost without changing arithmetic.
