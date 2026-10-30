# Builder A, round 2 response

## K4

**Guarantee (i)–(ii), contraction.** Conceded: F = H + B has Lipschitz constant up to 1 + Lip(B); spectral normalisation certifies nothing for a residual map, and 2609.26487's expanding Jacobian directions rule out a convex contraction domain. D^k is therefore withdrawn as a halting rule; halting is the step test ‖H^k − H^{k−1}‖ ≤ ε' (2502.05171), as the red team proposes.

**Fix to the flag (replaces (ii)–(iii)).** The ambiguity flag becomes *settled-and-apart*, with no λ:

```
settled_r = ‖H_r^{k} − H_r^{k−1}‖ ≤ ε'  for all r
flag      = settled_r ∀r  and  max_{r,s} ‖H_r^k − H_s^k‖ > ε
```

Statement: if the flag fires, F has at least two ε'-approximate fixed points at distance > ε. This is unconditional. The slow-convergence false alarm (λ ≈ 1, h = 16 chains) is excluded by construction: unsettled replicas do not flag. Cost fix: replace replicas from the start with a *kick test*, R − 1 perturbations σξ applied to the settled state and re-settled; extra compute is the re-settling steps only, not R× the loop.

**Fork blend.** Conceded: softmax returns the mean of two successors, a unique fixed point. Fix: the loop block's read-back is a dense-associative-memory update over the node table with learned β (2008.02217), whose fixed points lie exponentially close to stored patterns when patterns are separated and whose equal-distance mixture is a metastable state that noise leaves. That is K2's competitive nonlinearity; the red team's verdict that the flag belongs on a block with multiple attractors is accepted.

**C1.** Conceded for halting (withdrawn). For the flag, ε, ε' are calibrated from the 99th percentile of settled inter-replica distance on unique-answer training inputs: a calibration, not a learned gate.

**C2 (ambiguity untrained).** Fix: forks enter training with a per-replica min-over-valid-answers loss, `L_r = min_{y ∈ Y_valid} CE(y, W H_r^k)`; the blend scores worse than either committed answer, so commitment is rewarded and bistability is trained, while unique-answer inputs reduce to deep supervision. Held-out tests use longer chains and three-successor forks.

**C3.** Conceded; the kick test restores K0's iteration budget except after settlement.

**Prior art.** Conceded: 2211.09961 measures per-example path independence from different initialisations, 2601.19085 is an ensemble of TRMs with lowest-loss-winner training, 2607.11116 is a port-Hamiltonian DEQ. Added: PABEE 2006.04152 (halt when consecutive exits agree), self-consistency 2203.11171. Residual novelty: the settled-and-apart certificate, the kick test, and the min-over-valid-answers training of bistability.

**Kill test.** Accepted: report halting-step-vs-h slope (pass 1 ± 0.1), add the step-norm halting control, use three kicks (R = 4), add three-successor forks. Numeric: flag rate ≥ 80% on held-out forked chains and ≤ 5% on unforked chains at h = 16; two-successor and three-successor forks both flagged. Kill: flag rate difference < 30 points for every σ.

**Verdict.** Withdrawn as a block; retained as the interrupt flag for K2, K1 or K0 + H. P(beats K0) = 0.12, accepted.

## K5

**Marks in superposition.** Fix: stack frames carry an explicit child counter, iterative DFS:

```
frame = (w, id, c)           # latent state, discrete node id, next untried child index
push : S[π+1] ← (w, id(w'), 1); π ← π+1; w ← w'
pop  : (w, id, c) ← S[π]; S[π].c ← c+1; π ← π−1; exhausted if c+1 > b
w'   = T(w, c, E_c)          # proposes child c of the current node: a lookup with query (id, c)
```

No marks accumulate; state is (s+1)(d + log b) for every b; "never re-proposes an excluded sibling" is guaranteed because the proposal is a function of (id, c), a selection (A1), not a learned exclusion.

**Soft actions, exposure gap.** Fix: hard actions at train and test; the action head is trained by cross-entropy on the solver trace; push and pop are vector copies, piecewise differentiable in w, so no soft stack and no straight-through estimator. This is NPI's recipe (1511.06279), conceded below.

**DAgger decoder.** Fix: the frames' discrete (id, c) make the stack fully observable; the solver relabels from the discrete stack, no latent decoder.

**Positional generalisation.** Accepted: content group tokens, no absolute positions, cross-attention query (group id, c).

**C3.** Conceded: no scale evidence. Partial rebuttal of the token-space comparison: a cumulative trace costs N_DFS tokens of context per visited node and scatters the state across positions so the backtracking decision conditions on history rather than state (2605.22221); the stack holds O(s) frames and localises state by construction. That is a cost and locality claim, not a capability claim.

**C4.** Fix: phase one is teacher-forced over the trace with local per-tick losses; phase two (DAgger) runs own actions with a tick cap and the stack detached between ticks, so training never unrolls through the search. Inference in b^s worst case is DFS's price; the local dead-end test is what keeps visited nodes polynomial on structured instances.

**Prior art.** NPI 1511.06279 and recursive NPI 1704.06611: conceded, the recipe and the localisation condition are theirs. Residual novelty: the stack as K1's workspace discipline with broadcast into a token stream, the pop as a retraction with a training target, and the stated space separation from BFS superposition. NS-RNN 2010.04674: rebutted on cost, not on capability; the nondeterministic stack simulates the weighted PDA over all configurations at cost cubic in length, which is exactly the superposition price K5.1 trades time against; the dichotomy is a space-time trade-off, not a falsehood.

**Kill test.** Accepted and replaced: one-per-group with all chosen digits distinct and sum = T, b = 4, train s ≤ 3 with traces, test s = 8 (65,536 leaves, DP state above 80k, both ≫ C(64)). Pass: ≥ 90% exact solutions at s = 8, pop precision ≥ 80%, K0 at equal tick budget < 50%; a token-trace backtracker (2502.04404 style) at equal FLOPs is reported alongside. Kill: < 70% at s = 8.

P(beats K0) = 0.20, accepted.

## Ranking and combination

Reading H from the red team's description as a latent-prediction objective of the 2511.05963 / 2608.05806 kind: **H > K5 > C > K4.** H is the only candidate with precedents above 1B, zero inference cost, and a direct line to T3; its path-star result (2511.05963) is the capability-in-kind signature this project has never produced. K5 is second because it is the only candidate with a training target for retraction and a cheap, now DP-proof, kill test. C ranks above K4 because K4 is no longer a block; C has this project's strongest small-scale number (−0.79% at 22M), which is capacity, not kind, and that is why it is not first.

**K0 + H is accepted as the base pair, with two additions that cost almost nothing:**

1. **Apply H's loss at every loop iterate** (deep supervision with the belief-state target). This gives the loop a convergence target that is a sufficient statistic rather than a next-token shortcut, which is the condition the step-norm halting test needs to mean "finished" and not "stuck".
2. **The K4 kick test at settlement** as the interrupt: perturb the settled state, re-settle, flag when settled-and-apart. Extra compute is the re-settling steps only; the flag is a certificate of two approximate fixed points, trained by the min-over-valid-answers loss on ambiguous training inputs.

K5 is reserved for traced or RL search data, where a pop has a label, and is not proposed for prose.

The combination keeps the red team's reasons for K0 + H (no gates, no routers, no discrete actions in the base model, precedents above 1B) and adds the one thing the brief asked for that K0 + H does not have: a signal the model can raise when its own computation has not resolved.
