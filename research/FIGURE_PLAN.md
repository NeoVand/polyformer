# Figure plan for the paper (proposed 24 Oct ~13:00 for Neo's approval)

Five main figures, each telling one step of the argument. Panel names refer to gallery v5 (app-exact,
paper/nmi/figures/v5/gallery) or are marked NEW. Every number comes from build_master.py or a raw record.

**Figure 1. The result at a glance.**
(a) What the models read in each domain, and what 64x longer means (p1_six_inputs).
(b) Domains by ingredients: the ablation matrix (r1_matrix).
(c) Ordinary training falls, the full recipe stays exact, same architecture (r3_slopes).

**Figure 2. Why the training loss cannot see it.**
(a) The line through weight space: ordinary training sits in the deeper next-token valley, only the full recipe is
exact at length (pr1_blindness).
(b) The training loss ranks the trackers backwards across 24 checkpoints (s3_loss).
(c) NEW: stiffness, the equivalence term responds to drift at first order while next-token loss is damped by its floor.

**Figure 3. What the model learns: the minimal automaton, with error correction.**
(a) Tesseract globes: the state is the 4-cube and statements walk its edges (m1_tesseract).
(b) Exactly 960 clusters, one per Nerode class (m3_clusters).
(c) Kicked states return to their class within about ten steps (pr2_kicks), or the basins (c5).

**Figure 4. Closure, the error cocycle and proofs at every length.**
(a) Without closure the state winds outward on a scale clock (drift spiral).
(b) NEW: adversarial repeated cycles break trackers trained without closure; closure-trained ones survive.
(c) NEW: the snapped tracker is certified exact on every input at every length (the ball certificate).

**Figure 5. Toward language models.**
(a) NEW: the in-model ladder at 256 statements: chain of thought 0, self-distillation about 0.5, coverage alone 0,
coverage plus self-distillation about 0.9, oracle about 0.97.
(b) NEW: the teacher's error is 17 times higher on states short training never reaches (the coverage diagnosis).
(c) NEW: stories with an off-the-shelf embedding checker stay level with length; no signal collapses.

**Extended Data.** Architecture and compute graph (h1_architecture); the long-carry addition control and the last-8
floor; the counting control on fresh seeds; physics (closure stops blow-up, Lorenz held, pendulum phase lost); the
frontier-model comparison (reliability and tokens); noise tolerance of near and far false pairs; the soft checker's
coverage bias; the audit's reproduction table.
