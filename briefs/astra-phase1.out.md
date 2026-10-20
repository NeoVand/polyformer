Phase 1 is complete and committed on `claude/story-wrapup`.

**Proved:** [THEORY.md](/Users/neo/repos/polyformer/.claude/worktrees/wrapup/research/THEORY.md) establishes exact order-blind ceilings—**83.054698% for A4, 77.228752% for A5**—and a constructive, position-free Match-3 theorem verified with hand-built representations. Faithfulness is sufficient but **not necessary**; preserving noncommutativity is the sharper criterion. General Match-k sufficiency is proved with positional gates; the position-free extension remains open.

**Positioned:** [PRIOR_ART.md](/Users/neo/repos/polyformer/.claude/worktrees/wrapup/research/PRIOR_ART.md) verifies **36 arXiv records**. Seq2Tens already supplies ordered-subsequence sums. The defensible contribution is the marked matrix readout, task-specific theory, and measured learning behavior.

**Tested:** The three-seed swap-program benchmark confirms the symmetry barrier:

| Arm | Mean accuracy |
|---|---:|
| Commuting holonomy / Newton | 62.02% / 62.05% |
| Holonomy d=3 / d=4 | 100% / 100% |
| Matrix RNN | 100% |
| Positional softmax 1L / 2L / 3L | 98.95% / 100% / 100% |

All registered predictions hold. This benchmark establishes **no advantage over the order-aware baselines**. Recorded GPU-time cost is approximately **$0.35**, excluding overhead.

The [handoff](/Users/neo/repos/polyformer/.claude/worktrees/wrapup/briefs/astra-phase1.out.md) contains evidence, limitations, and commit references. `OVERNIGHT.md` records completion. Nothing was pushed or merged; `src/` was untouched.