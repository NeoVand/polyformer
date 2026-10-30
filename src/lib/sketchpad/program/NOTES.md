Implementation in progress; no measured results claimed yet.

Scope: pure TypeScript under this folder, branch `program`, no model or paid service.
The contract assigns shared-glossary edits to the orchestrator; glossary candidates live here.

Assumptions and decisions registered before execution:

- This is computer algebra: calculation with expressions and equations. The brief chooses evaluation and numerical recovery of coefficients; symbolic rewriting is the standard alternative but outside this stream's contract. Host arithmetic would be faster but breaks condition 2 (the model computes).
- Keep exact fractions for algebra and checks. Expression precision uses truncation toward zero; an ellipsis marks discarded digits. Accept implicit multiplication such as `2x` and `3(x-2)` because the supplied examples require it.
- The contract limits `solve` to quadratics; the more specific PROGRAM brief asks for higher degrees. Accept them, with explicitly incomplete guess-and-prove results.
- Guesses can be approximate; accepted roots must pass exact checks against both original typed sides. A single confirming point is a consistency check, not protection against an adversarial arithmetic provider.
- Costs include every scheduled operation, recovery and check. They are predictions from the supplied model, not device timings. Do not assume the simplified dry-run examples predict this general runtime's costs.
- Fixed seeded suites will cover the requested populations. Fault injection will report misses, not remove them. No model use; spend is $0.

## Glossary candidates

- Computer algebra: computation with mathematical expressions; a long-established field, used here to recover and check equations using arithmetic rather than rewriting.
- Rational number: an integer numerator divided by a nonzero integer denominator; classical arithmetic, used to check roots without decimal rounding.
- Interpolation [zoo]: recovering polynomial coefficients from values at chosen points; classical finite-difference methods, used here with every arithmetic operation delegated to Calc.
- Kronecker substitution [zoo]: packing polynomial coefficients into digits of one sufficiently large integer; attributed in the plan to Kronecker (1882), used for expansion.
- Synthetic division / Horner [zoo]: evaluating or dividing a polynomial by successively multiplying and adding its coefficient row; classical, associated with Horner (1819), used to prove proposed factors.
- Cramer's rule [zoo]: solving a square linear system by ratios of determinants; Cramer (1750), used for two unknowns.
- Bareiss elimination [zoo]: elimination using exact integer divisions to avoid growing fractions; Bareiss (1968), used for three unknowns.
- Bracket: two bounds where a continuous function has opposite signs; the intermediate value theorem guarantees a root between them, used for irrational-root decimal checks.
