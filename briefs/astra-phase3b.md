# Astra, last step: fold in the word-problem results and finish the story

The A5/S5 word-problem experiment (GROUPS.md section 7, branch claude/group-word-problems, 294 runs, predictions
committed before results) is finished. Claude started `git merge claude/group-word-problems` in this worktree
(/Users/neo/repos/polyformer/.claude/worktrees/wrapup, branch claude/story-wrapup); it stopped with conflicts in
research/GROUPS.md, groups.py, modal_run.py, polybench.py, test_groups.py (7 hunks; both branches added code and
sections in the same places).

1. Resolve every conflict keeping **both** sides' functionality (your swap-program benchmark and its section, and the
   word-problem tasks, models, grids and section 7; renumber sections if needed so GROUPS.md reads in order). Run
   `uv run --no-project --with "jax[cpu]" --with optax --with numpy python research/test_groups.py` and
   `research/test_theory.py`; both must pass. Commit the merge.
2. Read GROUPS.md section 7 (and `research/wp_summary.py` output if useful). Replace the two `<!-- WORD-PROBLEMS -->`
   placeholders (src/routes/report/+page.svelte, src/routes/learn/+page.svelte) with the real results: a short
   honest subsection in the report (table in the paper's style, what was predicted, what held, the comparison with
   softmax, commuting layers and the matrix-state RNN, length generalisation if measured, limits), and a plain
   sentence or two in Learn. Update the e2e test that checks the pending handoff. If the results change any claim
   on the landing page or elsewhere in the report (abstract, conclusions), update those too. Numbers exactly from
   the results files.
3. `pnpm check`, unit tests, `pnpm build`, the e2e tests against a preview server, and Playwright screenshots of the
   changed sections (1440x900 and 390x844, light and dark); look at them and fix anything off.
4. Commit (messages end with `Co-Authored-By: Astra (Codex)`), append a "Phase 3b done" line to OVERNIGHT.md's Log.
   Never push; Claude publishes. Final message: what section 7 found in five lines, and what you changed.

This is the last piece before Neo wakes up. Make the ending land.
