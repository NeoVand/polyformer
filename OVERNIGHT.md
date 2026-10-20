# Overnight wrap-up (started 20 October 2026)

Neo's request, verbatim: "ask astra to do the three remaining pieces. also the app and the paper in the app, the
visuals, everything i suppose needs new updates to wrap up the story after astra finishes the three items ...
The whole thing should become understandable to a non-mathematician with ML background."

This file is the single source of truth for the overnight work. Anyone resuming (Claude after a context loss, or
Astra) reads it first and updates the status table. Integration branch: `claude/story-wrapup`, worktree
`.claude/worktrees/wrapup`, cut from `claude/group-representations` (GROUPS.md results, a6b533d).

## The story being wrapped up

Pairwise attention cannot see relations whose low-order statistics vanish; native higher-order terms can, but on
language nothing higher-order beat softmax (SEARCH.md S0-S2, LOCAL.md S6). GROUPS.md then showed that the real
content of the winning layers is **composition**: softmax handed every character of Z_3^4 still cannot learn
Match-4, and what a layer can relate is set by the algebra its features compose in. Softmax composes nothing;
Newton attention composes in an abelian group (it learns characters and stops exactly at the order-blind ceiling);
holonomy attention composes in SO(d), learns the irreducible representations of A4 and A5 from labels, and solves
what commuting layers cannot. The smallest faithful irrep suffices.

## Phases

| # | Who | What | Status |
|---|---|---|---|
| 0 | Claude session `holonomy-attention-on-a5` (worktree `groups-words`) | A5/S5 word problems vs matrix-state linear RNNs (GROUPS.md section 6, step 1) | running |
| 1 | Astra (Codex) | A: separation theorems; B: verified prior-art positioning; C: a second benchmark. Brief: `briefs/astra-phase1.md` | complete; handoff `briefs/astra-phase1.out.md` |
| 2 | Claude | merge phase 0 and phase 1 branches into `claude/story-wrapup`; check numbers | pending |
| 3 | Astra | app, paper (report route), Learn, landing, visuals for the new story. Brief: `briefs/astra-phase2.md` | complete; visual handoff `briefs/shots/README.md` |
| 4 | Claude | review build, screenshots at 1440x900 and phone width, fix, commit; report to Neo | pending |

Rules for everyone: work only in this worktree (or your own worktree cut from this branch); commit often, messages
ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` for Claude and `Co-Authored-By: Astra
(Codex)` for Astra; never push; never merge into main (pushing main publishes the site; Neo decides); use /bin/rm
and /bin/mv -f. Modal: `uvx modal run research/modal_run.py::main --grid <name>`. Local JAX: `uv run --no-project
--with "jax[cpu]" --with optax --with numpy python ...`.

## Publishing

Neo, 20 October 2026: "yes I want it live." Claude merges `claude/story-wrapup` into main and pushes after
phase 4's review passes (build, check, tests, screenshots). Astra never pushes.

## Log

- Phase 1 launched; Astra's final message goes to `briefs/astra-phase1.out.md`, transcript id in `briefs/astra-phase1.log`.
- Phase 1 A started (Astra/Codex): audit the implemented symmetry, prove qualified separation and sufficiency results, and build numerical checks.
- Phase 1 B started (Astra/Codex): verified prior-art audit and novelty boundary, especially discrete signatures and matrix development.
- Phase 1 C started (Astra/Codex): select and test a second composition benchmark, run a pilot, and commit predictions before the three-seed grid.
- Phase 1 B finished (`bf3d0ef`, Astra/Codex): 36 arXiv citations verified by fetched abstract pages; Seq2Tens is the closest generating-map predecessor and path development the closest group-product predecessor. Novelty is narrowed to the matrix/marked-arity realization and task-specific separation; two thesis/workshop leads remain explicitly UNVERIFIED.
- Phase 1 C checkpoint (`5d5ddd2`, Astra/Codex): brute-force tests and eight-arm seed-0 pilot complete; numerical predictions committed before the 24-run confirmation grid. The short swap-program pilot is solved by positional softmax and the matrix RNN as well as noncommuting holonomy.
- Phase 1 C finished (`e92e4a5`, Astra/Codex): all four registered criteria hold. Commuting arms average approximately the exact 62.037% ceiling; holonomy d=3/4 and the matrix RNN reach 100%, positional softmax 1L reaches 98.95% and 2L/3L reach 100%. All 32 L4 runs used 0.432 subprocess-hours ($0.35 GPU-only estimate; $3.09 generous resource allowance); both apps are stopped.
- Phase 1 A finished (Astra/Codex): sharp Bayes bound; exact A4 83.054698% and A5 77.228752% ceilings; constructive token-only Match-3 and positional Match-k proofs; joint commutativity-reflection criterion and counterexample to faithful-dimension necessity. Hand-built A4/A5 heads pass raw and normalized checks on 64 sequences each; all A4 posterior classes and 86,400 A5 reorderings independently verify the exact ceiling method.

- **Phase 1 done (Astra/Codex).** Commits: `5d5ddd2` (C tests/pilot/preregistration), `bf3d0ef` (B verified prior art), `e92e4a5` (C confirmation/results), `f289075` (A proofs/constructions/exact ceilings). Handoff: `briefs/astra-phase1.out.md`. All work remains on `claude/story-wrapup`; no push, merge, or `src/` edit.

1. Exact order-blind ceilings are A4 **83.0546984493%** and A5 **77.2287515874%**, from a proved conditional-ordering formula and exact integer counting.
2. Faithful representations suffice for position-free Match-3 with explicit finite gates; the separate arbitrary-Match-k theorem requires positional gates, and every hand-built A4/A5 check passes.
3. Faithful dimension is not necessary: joint preservation of noncommuting pairs is the exact homomorphic Match-3 criterion with sufficient token gates; fixed-length softmax expressivity is explicitly proved.
4. **36 arXiv citations verified**; Seq2Tens already supplies ordered-subsequence sums, so novelty is narrowed to the marked matrix realization, task-specific theorems, and measured learning behavior.
5. Three-seed swap programs: commuting models ≈**62.04%**, holo d=3/4 and matrix RNN **100%**, positional softmax 1L **98.95%**, 2L/3L **100%**; all predictions hold, no superiority claim, **$0.35** GPU-only estimate.

- **Phase 3 done (Astra/Codex).** The app now tells the progression from higher-order synthetic wins, through the language-model limits, to composition and learned group representations. Title used: **Learning to compose**, with the report subtitle **From higher-order attention to group representations**. Alternative title: **Attention as composition**.
  - `e0aa26b`: shared, sourced group results and the accuracy-ladder / supplied-character figures.
  - `24aff05`: reproducible A5 d=3 seed-0 training and `static/recorded/a5-irrep.json`; all 60 learned matrices, computed ideal matrices, alignment and provenance.
  - `92b42ed`: Holonomy Explore lab, ideal/recorded switch, all 60 rotations, order demo and mathematical tests.
  - `259823c`: restructured report, exact result tables, qualified theorems, second benchmark and bibliography.
  - `be953f7`: Learn group prerequisites and composition chapters, definitions, provenance and interactive figures.
  - `62f0e63`: landing narrative and rotation tile, recorded-only Groups comparison and clearer shared typography.
  - `0bc00e1`: mobile lab layouts and controls, caption clearance and local stacking for graph labels.
  - `6a58054`: updated browser tests, portable static-server/capture scripts and 260 reviewed production screenshots.
- The fresh A5 recording reaches **99.17%** held-out balanced accuracy, with mean homomorphism error **0.101096** across all 3,600 pairs for the selected head. It is labelled as a fresh run, distinct from the original three-seed benchmark. The training app is stopped.
- The theory keeps its conditions: faithful is sufficient, not necessary; the token-only Match-3 and positional Match-k constructions are separate; softmax failure is measured learning behavior, not an expressivity impossibility. Seq2Tens and path development are the closest predecessors. Swap programs show the order distinction and **no advantage over the order-aware baselines**.
- Validation passed: `pnpm check` (0 errors, 0 warnings), `pnpm test` (39 unit tests and 4 browser tests), default `pnpm build`, and `BASE_PATH=/polyformer pnpm build`. A static production smoke check loaded all eight prefixed routes and the A5 recording without failures. A real WASM baseline trained ten steps and paused without browser errors. Edited Svelte files pass the autofixer without issues or suggestions.
- Visual handoff: `briefs/shots/README.md`, 1440×900 and 390×844, light/dark browser preferences, with second animation frames about one second apart. The existing fixed dark palette is intentional in both preferences. Repeated image inspection corrected mobile tables, labels, captions, controls, plot contrast and figure spacing; final runtime/geometry audits are clean.
- Only the requested **WORD-PROBLEMS** placeholders remain pending: one short report subsection and one Learn sentence, both marked for Claude. Work is committed on `claude/story-wrapup`; nothing was pushed or merged. Claude's review and publication remain Phase 4.
- Phase 4 (Claude): reviewed shots (landing, holonomy lab, report); check/39 unit tests/build pass (e2e needs a live preview server; Astra ran them green). Fast-forwarded main to dc75812 and pushed; Pages deploy succeeded, site title "Learning to compose". Remaining: fill the two `<!-- WORD-PROBLEMS -->` placeholders when claude/group-word-problems finishes, then push again.
- **Phase 3b done (Astra/Codex).** Merge `85430bd` retains both experiments: word problems remain GROUPS §7, swap programs move to §8, and both Python research suites pass. Replaced both word-problem placeholders with audited results, Table 7, registered successes and failures, the 20,000-step amendments, recurrence comparisons, length generalisation and limits; updated the abstract, conclusion, source references and e2e handoff check. Holonomy reaches 100.0% on A5 and 99.8%/98.4% on S5 classes at lengths 16/64; short-product sectors improve learning speed/reliability at the main budget, with no demonstrated capacity advantage over recurrence. The binary prediction fails, and Householder recurrence is faster on S5 classes. `pnpm check` (0 errors, 0 warnings), 39 unit tests, `pnpm build`, and all 4 e2e tests against a fresh preview pass; all edited Svelte pages pass the autofixer. Reviewed 32 final Playwright screenshots at 1440×900 and 390×844, light/dark preferences: [visual handoff](briefs/shots/phase3b/README.md), with no browser errors or overflow. Work is committed on `claude/story-wrapup`; nothing pushed. Claude reviews and publishes this final update.
- Phase 3b/4 final (Claude): merged claude/group-word-problems (Astra resolved, 85430bd/49d2425), placeholders filled, main at 06d481a pushed, deploy succeeded. Overnight wrap-up complete.
