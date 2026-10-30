# The energy form: spec and the first three tests

22 October 2026. After [DEBATE.md](DEBATE.md) section 7. One principle instead of an assembly:

> A context is the minimiser of one energy over the states of all its positions. Thinking is descent
> with tied weights. Reading a token adds a variable. The readout at a position is taken at the current
> minimum. The transformer is the special case of L untied descent steps with earlier positions frozen.

```
E(h_1..h_t ; x_1..x_t) = Σ_s [ ½‖h_s‖²  −  Σ_{r≤s} F(⟨k(h_r), h_s⟩)  +  Σ_u ψ(⟨a_u, h_s⟩) ]  + readout terms
descent : h ← h − η ∇E   (all positions, every step)      halt : ‖∇E‖ ≤ ε or E stops falling
```

Context enters only through the memory term (keys of earlier states). No additive tilt, no gate, no
router, no halting head. Three terms per position: a quadratic (boundedness), a Hopfield memory over
earlier positions (F = exp gives exponential capacity), and the MLP as an energy with convex ψ.

What follows without being added: iteration with a Lyapunov halting rule; several minima, each a
hypothesis; revision of earlier states by later tokens; asynchrony, since positions converge at different
rates and the background descent continues while tokens arrive; compute rising near a basin boundary,
which is the "no, wait" signature and a theorem about descent near a saddle.

Known obstacles: re-descending earlier positions is sequential over positions under teacher forcing,
which needs a chunked rule or a non-autoregressive objective; training through descent is second-order.

## The tests, each pre-registered, each under $10 on Modal

**E0. Tilt-free basin switch** (the V4 rerun; the form's own signature). Same ambiguous-cue task and K2
block as V4 in the validation worktree, with the additive tilt W c removed so context enters only through
the keys. Prediction: the switch at the decisive cue must now cross the memory barrier, so the step
count at the cue is at least 2× the baseline on 3/3 seeds, and the spike grows with the barrier height
(sweep the memory temperature β). Kill: ratio under 1.5 on every β. Cost: tens of CPU-minutes; under $3.

**E1. The joint form, non-autoregressive** (revision and asynchrony, the brave one). All positions,
including the answer positions, are variables of one energy; generation is descent from a blank or noisy
answer; there is no teacher forcing and no causal mask on the energy. This is the energy-based
iterative-refinement family (energy-based diffusion language models; discrete diffusion solves Sudoku and
path planning where autoregression fails, Ye et al. 2024, arXiv 2410.14157) with a tied-weight descent and
a Hopfield memory term. Tasks: (a) the late-evidence task of V1, where the answer position must flip after
later evidence, measured as the fraction of answers that change after the decisive event and the step at
which they change; (b) path-star (Bachmann & Nagarajan 2403.06963, d = 5, ℓ = 5), where next-token
training provably fails. Arms: the joint energy model; the one-slot event-clocked loop (K1); an
autoregressive transformer at equal FLOPs. Predictions: joint model ≥ 90% on path-star where the AR model
sits at 20%; on late evidence the joint model's answer flips after the decisive event in ≥ 80% of
overturned cases, with the flip concentrated within three descent steps of that event. Kill: joint model
below 50% on path-star, or flips uncorrelated with the decisive event. Cost: under $10 on one H100.

**E2. The carried state on a manifold** (exactness; the fix V2 needs). The one-slot loop was exact at 256
events on one seed of three and drifted on the others because nothing holds the state on the set it
represents. Make the carried state an orthogonal matrix updated by a learned rotation per event (the
holonomy state space, used here as the loop's state and not as a position code), with the readout a
linear probe of the matrix. Prediction: exact at e = 256 on 3/3 seeds (≥ 99%), and the Euclidean-state
loop drifts as before. Kill: orthogonal state below 95% on any seed. Cost: under $3.

Decision rule: E0 passing makes the form's signature real; E1 passing gives revision and the lookahead
property in one model; E2 passing gives the loop an exact state. Any two of three passing earns the
first language-shaped run of the pure form (reasoning text with hidden intermediates), still under $10.
