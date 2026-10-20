1. At lengths 16/64, holonomy class accuracy was **100.0%/100.0% on A₅**, **99.8%/98.4% on S₅**.
2. Softmax and commuting controls lost the product at later positions.
3. Short-product sectors helped learning; 20,000-step amendment runs brought the prefix-only RNN to **100.0%/99.4% on S₅**.
4. S₅ extrapolation from length 16 to 64 reached **97.3%** for holonomy and **98.2%** for Householder recurrence.
5. Binary-task predictions failed: an available faithful representation did not guarantee successful learning, and no method won everywhere.

Resolved and committed the merge, preserving both benchmarks. Updated report, Learn, abstract, conclusions, source references, e2e checks and the **Phase 3b done** log.

Both Python suites, check, 39 unit tests, build and 4 e2e tests pass. Reviewed 32 desktop/mobile screenshots in both preferences.

Commits: `85430bd`, `49d2425`. **Nothing pushed.**