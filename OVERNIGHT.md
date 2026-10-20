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
| 3 | Astra | app, paper (report route), Learn, landing, visuals for the new story. Brief: `briefs/astra-phase2.md` | pending |
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
