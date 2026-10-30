# Builder A: two blocks beyond K0–K3

Both keep the residual stream and token attention untouched, add no mixing layer, contain no free per-token gate, and are validated where the loss rewards the property.

## K4. Replica-Consensus Loop (RCL)

**Definition.** K0's weight-tied block B (attention + MLP on the residual) looped with input injection, run as R replicas that differ only in state noise. Halting and the interrupt come from inter-replica distance, not a gate.

```
H_r^0     = E(X) + σ ξ_r,   ξ_r ~ N(0,I),  r = 1..R        (R = 2 default)
H_r^{k+1} = H_r^k + B(H_r^k, E(X))                          (shared weights, k < K_max)
D_t^k     = max_{r,s} ‖H_{r,t}^k − H_{s,t}^k‖               (per position t)
halt_t    = min{k : D_t^k ≤ ε};  readout from mean_r H_{r,t}^k
interrupt_t = [D_t^{K_max} > ε]                              (ambiguity flag)
loss      = Σ_k Σ_r CE(y, W H_r^k) + λ_c Σ_k D^k             (deep supervision; consensus on training inputs)
```

**Properties.** Buys B1 with a halting rule whose target is geometry (respects "free gates collapse" and "routing hurts"); B2 (replicas are parallel hypotheses, the mean readout keeps them superposed until they agree); B5 in weak form (the interrupt is a condition that drives K1's broadcast or K3's retraction); and a free detector of lazy-identity collapse (2607.11116): a loop that computes nothing keeps D^k = D^0. Keeps A1, C1, C4. Risks: R× loop compute; σ is a hyperparameter; B3, B4 untouched.

**Guarantee K4.1 (one-sided-exact certificate).** Let F(H) = H + B(H, E(X)).
(i) If F is a λ-contraction (λ < 1) on a convex set containing the replica trajectories, then D^k ≤ λ^k D^0, every replica converges to the unique fixed point H* of that set, and the rule fires by k* = ⌈log(D^0/ε)/log(1/λ)⌉ with ‖H_r^{k*} − H*‖ ≤ λ^{k*}‖H_r^0 − H*‖. Proof: Banach; the distance between two trajectories contracts by λ per step.
(ii) If D^k > ε for some k ≥ k*, the replicas are not in the basin of a common λ-attractor: F has at least two attractors or a non-contracting region between them. Proof: contrapositive of (i).
(iii) With two attractors of basin masses p, 1−p under the start noise, the miss probability of (ii) is p^R + (1−p)^R (1/2 at R = 2, p = 1/2; 1/128 at R = 8); false alarms are impossible by (i). Proof: independence of the ξ_r.
Not guaranteed: that training makes F contractive on unique-answer inputs and bistable on ambiguous ones rather than contractive to one "undecided" point (that is the validation); λ near 1 makes k* large; nothing on scale.

**Validation V6 (forked pointer chains; CPU, ~15 min per σ).** Edge list of a chain in random order, a START node, answer = node after h hops; train h ≤ 8, test h ≤ 16 (loops implement iterated steps, 2502.17416). Test-only forks: one chain node with two outgoing edges, never seen in training, so two answers are valid. Model: 1-layer block, d = 64, K_max = 24, R = 2, σ ∈ {0.1, 0.3, 1}·RMS(H^0), ~60k parameters, 3 seeds, 500 chains per condition. Pass, for at least one σ: unforked accuracy ≥ 95% at h = 16 with halting by k = h + 2 in ≥ 90% of chains; forked median D^{K_max} ≥ 5× the unforked median; the first k with D^k > ε within ±1 of the fork hop in ≥ 80% of forked chains. Kill: ratio < 2 for every σ, or the single-trajectory KL exit of 2502.05171 separates forked from unforked chains as well as D does (then replicas buy nothing).

**Prior art.** Path independence as a global training-time property that predicts test-time extrapolation (2211.09961); Huginn starts the loop from N(0, σ²I) and exits one trajectory on KL < 5·10⁻⁴ (2502.05171); Ouro learns entropy-regularised exit gates (2510.25741); Equilibrium Reasoners run B restarts for majority vote or smallest-residual selection and still halt with a learned head q̂_k = f_φ(z_k) (2605.21488); halt-first ensembling keeps K = 4 latent states and takes the first to halt (2601.19085); SQUAD halts an ensemble of distinct early-exit learners on a quorum (2601.22711); single-trajectory convergence coexists with expanding Jacobian directions (2609.26487). New: inter-replica distance of one weight-tied loop, per input, as the halting rule and as a one-sided-exact certificate of non-contraction with the p^R bound; no learned exit; replicas differ only in noise, so agreement measures attractor geometry, not model diversity or trajectory selection.

**P(beats K0 at equal compute on a reasoning benchmark) = 0.30.** R = 2 halves the iteration budget, so RCL wins only where the benchmark credits abstention or where compute saved on early-halting inputs is reallocated to interrupted ones.

## K5. Backtracking workspace (K1 with a stack)

**Definition.** K1's fast stream unchanged. The slow stream is a hypothesis vector w, a stack S ∈ R^{s×d} with pointer π, and a verifier V with a local dead-end test. Per tick:

```
w' = T(w, S[π], E_c)                         # one block: cross-attention to the current event's tokens, MLP
a  = argmax V(w', E_c) ∈ {push, pop, stay}   # soft in training: a ∈ Δ³, Joulin–Mikolov stack update
push: S[π+1] ← w; π ← π+1; w ← w'            # commit the hypothesis
pop : w ← S[π] + u(w'); π ← π−1              # retract: return to the last commitment, mark the rejected branch
stay: w ← w'
halt: g(w) > τ (goal test)  or  pop at π = 0 (search exhausted); broadcast on halt as in K1
loss = CE over the solver's action trace + goal loss; own-action rollouts relabelled by the solver (DAgger, as 2306.05426)
```

Per tick O(d² + n_e d); memory (s+1)d.

**Properties.** Buys B4 in latent form with a training target (the pop is a retraction labelled by the trace, so C2 holds by construction); B1 with a halting rule that is a goal test, not a gate; B2 in depth-first form; A3 (the stack is non-commutative state of depth ≤ s). Keeps everything K1 keeps. Risks: discrete actions (C1); exposure bias at test; worst-case time b^s; on prose nothing asks for a pop, so the block is for traced or RL data.

**Guarantee K5.1 (DFS simulation and space separation).** Tree search with branching b, depth s, goal at a leaf, dead-end test local to (w, E_c). With hard actions and an exact verifier, the ticks visit DFS's node sequence and halt at the goal within 2N ticks, N ≤ (b^{s+1} − 1)/(b − 1), with state (s+1)d independent of the frontier. The superposed-frontier construction (2505.12514; K1.2 with m slots) requires |frontier| ≤ m·C(d), and the frontier reaches b^s; above m·C(d) its expansion step is corrupted by cross-talk (2505.12514's capacity argument) while the stack's space is unchanged. Proof: induction on ticks; after each tick the stack equals DFS's path of commitments and u(w') excludes the rejected sibling, so the next proposal is DFS's next node. Not guaranteed: that soft actions sharpen; learnability without traces; any time bound better than DFS's.

**Validation V7 (one-per-group sum; CPU, ~30 min).** s groups of b integers in [0, 9]; choose one per group with sum T; "partial sum > T" is the local dead-end test. Train b = 3, s = 3 with solver traces; test s = 5 (243 leaves), never trained. Model: 1-layer tick block, d = 64, stack depth 8, ~80k parameters, 3 seeds. Pass: ≥ 90% exact solutions at s = 5 and pop precision ≥ 80% against the oracle's pop positions, while K0 and a K1 slot workspace (m = 4) at the same tick budget score < 50%. Kill: < 70% at s = 5 with traces at s = 3.

**Prior art.** Stack-RNN (1503.01007), unbounded-memory transducers (1506.02516), stack attention for CFLs (2310.01749), StackTrans's hidden-state stacks between layers at 360M–7B with ≥ 30 points on DCFG tasks (2507.15343): all per-token syntactic memories on the fast stream, never a hypothesis stack with a dead-end test. Backtracking emerges in a latent reasoner without a mechanism in 32% of instances, +34 points when it does (2602.08100); token-trace backtracking fails verification because the state is scattered across positions, fixed by a state-only attention mask (2605.22221). Latent lookahead rolls hidden states forward before committing a token, with no retraction (2603.20219). New: the stack is the workspace's control discipline (push = commit, pop = retract) with DFS semantics, the state localised by construction, a stated space separation from BFS superposition, and a training target for the retraction.

**P(beats K0 at equal compute on a reasoning benchmark) = 0.25.** It wins only on instances whose frontier exceeds superposition capacity and only with traced or RL data; elsewhere it is K1 with extra machinery.

## One line

K4 gives the interrupt a certificate ("two answers survive"), K5 gives it a label ("that path is dead"); both are computation, neither is capacity, and each dies in under an hour on a laptop if wrong.
