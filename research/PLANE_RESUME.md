# Resume after the flight (written 24 Oct 2026, 04:58; updated as sessions report before 06:30)

Neo closes the laptop at 06:30 and reconnects from the plane. Every thread was told to commit by 06:10, to make every
Modal job that will not finish by then run detached with its call_id in a ledger, and to write a resume note.

| thread | session | branch / worktree | state at 04:58 | resume note |
|---|---|---|---|---|
| Headline factorial, Markov control, reruns, registers (EXEC_LM §11); globe retrainings for Fig. 3 | exec-d (local_41febb64) | claude/exec-d-0e1910 | 13 of 15 factorial runs done; RIr seeds 1, 2 running on Modal | research/EXEC_D_RESUME.md |
| In-model exact state (INMODEL_BRIEF.md) | lean-h (local_27ff932b) | claude/lean-h-26e3bd | pilot O and NLI training on Modal H100 | research/INMODEL_RESUME.md |
| Soft-checker noise test (SOFT_CHECKER_PLAN.md stage 1, MECHANISM §8) | mechanism (local_766f1add) | claude/intelligent-solomon-11ea28 | registered; 12 Modal + 8 Mac runs | research/MECHANISM_RESUME.md |
| Soft-checker theory (PROOFS4.md) | proofs (local_1a46b8ec) | claude/gracious-panini-dde55f | writing | status line at the top of PROOFS4.md |
| Paper (paper/nmi, review round with [HOLD] markers) | proofs (local_1a46b8ec) | claude/gracious-panini-dde55f | committed dc85244 | HOLD markers list pending numbers |
| Language soft checker, stage 2 build (object stories, simulator, soft checker harness; no spend) | lean-n-data (local_c9c973e3) | claude/lean-n-data-34a2d2 | building from 05:40 | README and resume note in its worktree |
| Figures v4 (FIGURES_V4_BRIEF.md): Fig. 1 landscape slice | app-exact (local_ea0f1613) | claude/app-exact-state-e29a3b | computing grid on the Mac | in that worktree's figures folder |

Factorial so far (exact at 1,024, seeds 0 / 1 / 2): ordinary + fixed norm 0.76 / 0.56 / 0.48; next-state + fixed norm
0.97 / 0.98 / 0.87; next-state, no norm 0.15 / 0.01 / 0.09; signal, no norm 0.92 / 0.18 / 0.00; signal + fixed norm
1.000 / pending / pending; full recipe + fixed norm 1.000 / 1.000 / 1.000. The norm alone does not carry the headline.

On reconnecting: open this session; run each thread's fetch command from its resume note (they are idempotent and
fetch finished detached jobs by call_id); then continue: in-model main batch, noise-test verdict and stage 2,
factorial verdict into the paper's [HOLD] markers, Figure 1 Blender render, Figure 3 globes once weights land.

Update 05:40: in-model pilot shut down on Neo's decision ($9.95; whiteboard INMODEL_WHITEBOARD.md: Nerode self-distillation is the next in-model test). Factorial complete: signal + fixed norm exact at 1,024 on 3 of 3. Noise test: near-miss wrong pairs tolerated to 20%, far errors hurt from 1% (PROOFS4 §7); stage 2 is a go.
Update 05:45: app-exact is pushing a dated priority section to the live /paper page (factorial, controls, soft checkers, three ingredients, in-model negative, Nerode self-distillation idea, landscape draft) by 06:15. Full polish of the page from the plane.

## Final state at 06:06 (all clear)
- Every worktree committed (exec-d 6d9e005 + logs, lean-h bd53867, mechanism 436bf64, proofs e2b7689, app-exact 49c66e4, lean-n-data 727cfe1).
- Still running on Modal, detached: Figure 3 retrainings R and RNLIr (exec-d; call ids and fetch commands in EXEC_D_RESUME.md). Rr and RNLr are in with weights.
- Live page: §52 '24 October 2026: what the review round established' at https://neovand.github.io/polyformer/paper#review-round (9d13b52).
- Next on reconnecting: fetch Figure 3 jobs; stage 2 language pilot (STORIES_RESUME.md: summariser model to download, embedder to fix); Nerode self-distillation test; Blender render of Figure 1; then the writing per SUBMISSION_PLAN.md.

## Airport hour (06:50 to 07:40)
- exec-d: fetch Figure 3 R and RNLIr; build, register (EXEC_LM §12) and launch detached the Nerode self-distillation pilot (rung A; SD vs ORACLE; seeds 0, 1; cap $30).
- lean-n-data: soft checker measurement on Modal (summaries + embeddings, f near / far) and the story tracker pilot (certified and none arms), detached; registration in research/STORIES.md (cap $25).
- app-exact: Figure 3 globes and basins data and drafts from the retrained weights.
- Deadline: everything committed and detached by 07:40; fetch commands in each resume note.

## Flight batch (launching 07:10 to 07:40, all detached)
- exec-d EXEC_LM §13: headline at frozen Qwen2.5-Coder-1.5B and 7B (full recipe + norm, ordinary + norm, 3 seeds); seeds 3 and 4 for the four headline rows (cap $70).
- lean-s (local_ad23c403) LEAN_S new section: combined objective on the 5k / 20k / 80k data grid, 3 seeds; third seeds for the old two-seed entries (cap $25).
- invariance (local_6a643510) INVARIANCE new section: next-state alone and signal + next-state on S5, 3 seeds (cap $10).
- Already running: EXEC_LM §12 self-distillation (4 jobs); STORIES checker and tracker pilot (3 jobs).
- Palette 'Ink and Cinnabar' in research/figstyle (notes branch 06b36c1); figure session told to adopt it.

## Launch confirmations (07:15)
- exec-d §13: 20 jobs detached (1.5B and 7B headline; seeds 3 and 4), reserved $68.1 of $70; call ids in EXEC_D_RESUME.md (a220899).
- lean-s §2.9: 5 jobs detached (combined objective on 5k / 20k / 80k; third seeds), b6d228a.
- invariance §6: 6 jobs detached (next-state alone and combined on S5, 3 seeds), INVARIANCE_RESUME.md (6e79b84).
- app-exact: Figures 1 and 3 drafts in the palette (7e2f3d3); 8 Modal jobs (seeds 1, 2) and local Figure 1 planes for seeds 1 to 5 (resumable) in progress.

## Boarding state (07:20)
- Cancelled as not needed: EXEC_LM §13 scale-up and extra seeds ($4.88 settled); figure seeds 1 and 2 ($1.68 settled).
- Running detached (one app per job, call ids in each resume note): EXEC_LM §12 self-distillation (4 jobs, exec-d); STORIES checker and tracker pilot (3 jobs, lean-n-data); LEAN_S §2.9 data grid (5 jobs); INVARIANCE §6 group-word factorial (6 jobs).
- Neo's six priorities (memory feedback-paper-priorities): reviewer points, text, in-model, theory, literature, banger figure and abstract. Plane work: theory consolidation pass and a systematic literature review (laptop sessions), then fetch and read results; figures redrawn in Cobalt and Rose (research/figstyle).
- 07:25: figure gallery commissioned (app-exact): tesseract globe (the exact tracker's 16 states are a projected 4D hypercube, trajectories walk its edges), ingredient cube (2x2x2 factorial), drift spiral, error-correction streams, basins redone, landscape surfaces; Blender if available; contact sheet gallery.png.

## Boarding state, 24 Oct 07:35
- Running detached on Modal: EXEC_LM §12 self-distillation (2 apps left, exec-d, verdict about 08:00); STORIES 7B/3B checker re-measure (1 app left, lean-n-data).
- Finished: INVARIANCE R2 (S5 + fixed norm). Prediction failed: combined exact at 1,024 on 1/3 (0.855 / 0.916 / 1.000); next-state + norm 0.994 / 1.000 / 0.998. Sent to the invariance session [e4efcd] to write up and diagnose, no new spend.
- Figure gallery (app-exact, 7bda745, not pushed) sent to Neo. Verdicts: tesseract globes = Figure 1 contender; ingredient cube and basins = strong supporting ideas; drift spiral b is a good Methods panel; kick globe and 3D landscape are weak as drawn.
- REACH.md (notes b8c7338): Neo's question "what big problem does this solve". Missing citations to add: Angluin L*, Bachmann & Nagarajan, Othello-GPT, McLeish Abacus, Cho position coupling, Snell context distillation. One proposed counting/addition test, not launched.
- 07:36: INVARIANCE diagnosis (1741268): reduced-word partners constrain only two lengths; EXEC used partners of every length. Follow-up F1-F3 approved and sent to the invariance session (9 jobs, cap $3): random all-length partners, mu = 0.1, seeds 3-5.
- 07:42: ARITH approved by Neo and sent to exec-d (ARITH_BRIEF.md in its worktree, cap $10). REACH.md gained 'Beyond language models' with two proposed cross-domain tests.
- 07:54: PHYSICS (notes a1d05f5, research/physics/) launched: 8 detached Modal apps, results on volume polyformer-physics as {system}_{arm}_s{seed}.json; fetch with: uvx modal volume get polyformer-physics / research/physics/results
- 08:08: all Modal apps with a live local client were cancelled at 07:57 (physics x8, exec-lm x3). PHYSICS relaunched as a DEPLOYED app (polyformer-physics) with 8 spawned calls (call ids in research/physics/calls.json); results to volume polyformer-physics. Self-distillation §12 verdict: ORACLE 0.941/1.000, SD 0.508/0.422, plain CoT 0.000/0.000 at 256 -> S1 fails, S2 fails on seed 1; exec-d told to write it up and use deploy+spawn.
- 08:16: Neo approved the SD-consensus run (cap $12). Queued to exec-d in order: ARITH launch, §12 write-up (done, 5cb6cda), free agreement check, register + launch SD-consensus. Physics: 3 of 8 calls still running at 08:15.

## Nature list dispatched (24 Oct ~10:00, Neo: "get it done")
- Item 1 ablation (ABLATION_BRIEF.md): code + arithmetic -> exec-d; Lean -> lean-s; S5 -> invariance; stories -> lean-n-data. Cap $6 per domain.
- Item 2 in-model: consensus teacher (EXEC_LM §15) running on the deployed app, 2 seeds.
- Item 3 language: consensus checker approved -> lean-n-data (cap $5).
- Item 4 theory: THEORY.md consolidation + free-readout proof of Thm 1.4 -> proofs session.
- Item 5 literature: LITERATURE.md, verified citations -> "Methods gaps raised by the external review" session.
- Figures: polish c1/c2/c5 -> app-exact; Figure 1 waits for the ablation table.
- Assembly (orchestrator): collect ABLATION_<domain>.json from each worktree into one table.

## 24 Oct ~11:15 (Neo: "go")
- Coverage teacher approved -> exec-d (arms COV and COV+SD, 2 seeds, cap $16), after the §17 fresh counting seeds.
- Independent audit approved -> "Methods gaps raised by the external review" (local_b842e034), AUDIT_BRIEF.md, cap $15, report research/AUDIT.md.
- THEORY_DEEP -> proofs session; VIZ_EXPLORE (gallery v5) -> app-exact. No spend.
- Master table is generated by research/master/build_master.py (notes branch); never type numbers.

## 24 Oct ~11:40, before landing
- Live on Modal: only the §18 coverage check job (deployed app polyformer-exec-lm, results on volume polyformer-exec-lm-results). exec-d asked to move the §18 gate and the four arms into a server-side driver.
- Audit: reruns must be deploy + spawn with results on a volume; queued note sent.
- Counting fresh seeds 3-5: exact 1.000 at 32 / 256 / 1,024 / 4,096, never wrong, n = 128 per length, selected at step 750 (> onset 600).
- After landing: Neo runs `sudo pmset -a disablesleep 0`.
