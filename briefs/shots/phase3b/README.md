# Phase 3b production review

32 Playwright screenshots from the final production preview, at **1440 × 900**
and **390 × 844**, with both light and dark browser preferences. The app retains
its existing dark palette in both preferences.

- `report-word-problems-*`: complete new results subsection, including Table 7,
  prediction failures, amendment runs, extrapolation and limits.
- `report-abstract-*` and `report-meaning-*`: updated framing and conclusions.
- `learn-programs-*` and `learn-word-problems-*`: lesson context and the entire new
  two-sentence summary, including its link to the report.
- `compare-source-*`: corrected swap-program source reference to GROUPS §8.

The images were opened and visually reviewed in both sizes and preferences.
The five-column report table fits the 350-pixel phone text column. Captures wait
for the active chapter illustration to settle, and the mobile Learn captures
allow for its sticky illustration so the complete new paragraph is visible.
No layout corrections to the app were needed. `audit.json` records no browser
errors, horizontal page overflow, or tables wider than their containers.

Reproduce from the repository root:

```sh
pnpm build
pnpm preview --host 127.0.0.1 --port 4173
# In another terminal:
node scripts/capture-word-problems.mjs
```

Validation passed: both Python research suites with CPU JAX, `pnpm check`
(zero errors and warnings), all 39 unit tests, the production build, and all
four e2e tests against the preview. All three edited Svelte pages pass the
Svelte MCP autofixer without issues or suggestions. The new displayed numbers
were independently checked against the raw `wp_*.jsonl` files.
