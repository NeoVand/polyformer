# Figures v4: show the mechanism, from real data (brief, 24 Oct 2026, 04:55)

Neo: replace the schematic loops with figures that make the mechanism visible: how the loss landscape and the state
space change under each ingredient (next-token loss, certified-equivalence signal, next-state prediction, fixed norm),
something striking, ideally three-dimensional. Everything drawn must be computed from trained models; captions state
projections and variance kept.

## Figure 1 (replaces the conceptual figure): "The training loss cannot see the cliff"
Data: the saved rewrite-chain checkpoints in `/Users/neo/repos/polyformer/.claude/worktrees/intelligent-solomon-11ea28/
research/results/mechanism/*.params.npz` (R, R+I, R+NL, R+NL+I, seeds 0-5) and that worktree's model code
(`mechanism.py`, `lean_run.py`; read only what loads a checkpoint and runs the tracker). Take the plane through three
checkpoints of one seed (R+NL+I = exact, R = drifting, R+NL), parameter-space interpolation on a grid of about 25 x 25
(Li et al. 2018 style; with the usual filter normalisation if the architectures' scales differ). At each grid point:
(a) next-token loss on training-length chains (a few hundred), (b) the certified-equivalence term and the next-state
loss on the same batch, (c) exactness at 1,024 rewrites on 128 held-out chains. Panel a: surface of (a), coloured by
(c). Panel b: surface of (a) + (b), coloured by (c). Save the grid as JSON; render a 3D surface draft (matplotlib)
now; the final hero render in Blender later.

## Figure 3 (replaces the mechanism figure): "Four globes" and the basins
Data: program-domain (4 bit variables, 16 states) trackers with weights saved, retrained by the exec-d session
(arms: ordinary; ordinary + fixed norm; next-state + fixed norm; full recipe + fixed norm; seed 0). States along
512 programs of 1,024 statements projected to 3D by PCA of the 16 class means (report the variance explained);
for the fixed-norm arms, show the states on the unit sphere of that projection. One 1,024-statement trajectory traced
on each globe. Basins panel: a 2D slice through three class centres of the full-recipe model; colour each start point
by the class the dynamics carry it to after a cycle of statements that returns to the same class (e.g. a statement
and its inverse, or `x = x`), brightness by steps to converge; the same slice for ordinary training.

## Deadline
Neo leaves at 06:30. By 06:10: grid data for Figure 1 computed and committed (or the script committed with a
resume note if the grid is not done), drafts committed. Render after Neo is back online.
