# Builder B: two candidates beyond K0–K3

**Position.** The block already has A1, C1, C4. Every block we added returned under 1% and shrank; the one objective change we made moved a decision task from under 1% to 18–35%. So the budget goes where the gradient is: one objective (B3, and the precondition for B4) and one memory (B2 with certified B1 halting). Both keep the standard block at inference.

## Candidate H: HINDSIGHT, a lookahead-gap weighted belief objective

**Definition.** Block unchanged. Training adds a 2-layer backward encoder `B` over the suffix, a hindsight head and a contrastive head; all three are discarded at inference.

```
s_t   = forward state at t (standard block)
b_t   = B(x_{>t})                                        # suffix summary, 2 layers, tied embeddings
CE_f  = -log p_f(x_{t+1} | s_t)                          # the ordinary loss
CE_b  = -log p_b(x_{t+1} | s_t, b_{t+1})                 # hindsight head: prefix + suffix after x_{t+1}
g_t   = max(0, CE_f - CE_b)              [stop-grad]     # lookahead gap: nats the future explains
w_t   = 1 + α·g_t / mean_batch(g)                        # α ramps 0→4 over the first 10% of steps
NCE_t = -log  exp(⟨P s_t, Q b_t⟩/τ) / Σ_{t'∈batch} exp(⟨P s_t, Q b_{t'}⟩/τ)
L     = Σ_t w_t·(CE_f + λ·NCE_t) + Σ_t CE_b
```

`g_t` is T3 measured per token: the excess of teacher forcing over hindsight. Tokens with large `g_t` are commitments whose correctness only the future reveals (the first branch token of a path-star, 2403.06963), which is where the ~100× dilution lives. The NCE term scores the state against a summary of the whole suffix, not the next token.

**Properties.** Buys B3 (the state is trained to be sufficient for the suffix summary at exactly the positions where the suffix matters) and C2 (the loss asks for lookahead). It is the precondition for B4: a state that carries the live alternative at a commitment is what a retraction needs; it does not supply the retract action. Risks: nothing in group A or T1 changes, so a sufficient statistic that needs more depth than the block has stays unrepresented; early in training `g_t` is noise, hence the α ramp.

**Guarantee (sufficiency at the optimum).** Let `z_t = Q b_t` be the suffix summary with critic `⟨P s_t, z⟩`. For any state map `s_t = f(x_{≤t})`, `I(s_t; z_t) ≥ log N − NCE_t` (1807.03748; 1905.06922), and `I(s_t; z_t) ≤ I(x_{≤t}; z_t)` by data processing. The minimiser over `f` with `N → ∞` therefore attains `I(x_{≤t}; z_t | s_t) = 0`: `s_t` is a sufficient statistic of the prefix for the suffix summary, the Myhill–Nerode condition T3 says next-token loss never imposes. Not guaranteed: sufficiency is for `z_t` at the resolution of `Q`, not for the full suffix; at finite `N` the bound saturates at `log N` nats (1811.04251), so batch 256 certifies only 5.5 nats of future; and that `g_t` locates decisions rather than free choices is an empirical claim, which is what the validation tests.

**Kill test (CPU, under 1 h, under 1M params).** The project's dilution harness, where hand-labelled reweighting lifted the decision task from under 1% to 18–35%. Three arms, three seeds: unweighted; hand-labelled weights; HINDSIGHT with self-derived `g_t`. Pass: HINDSIGHT reaches at least half the hand-labelled lift (decision accuracy ≥ 9% where unweighted is under 1%) and the top-5% `g_t` tokens have precision ≥ 0.5 against the hand labels. Failure means the gap does not find decisions; dead. Secondary: path-star `d = 5, ℓ = 5` (2403.06963), pass ≥ 90% where next-token stays at 20%.

**Prior art.** BST 2410.23506: forward and backward encoders with next- and previous-token heads; proves belief-state learning; weights every token equally and scores the state by one token. LongCE 2410.23771 and Helm et al. 2503.09202: weights from a long-versus-short *prefix* gap. Rho-1 2404.07965: reference-model excess loss. Forking tokens 2506.01939: entropy alone, at RL time. cDPO 2411.19943: positive/negative model ratio. Trelawney 2504.11336: data rearrangement. New: the weight is the *suffix* gap, the T3 quantity itself, computed by the same backward encoder that supplies the contrastive target; and the belief term is a suffix summary rather than one token.

**P(beats K0 at equal compute on a reasoning benchmark): 0.30.** Puzzle benchmarks pay for depth, which K0 has and H does not add; H's win is on long-horizon decisions, and the fair test is K0+H against K0.

## Candidate C: CLOSURE, a hashed boolean set memory for latent search

B2 is better obtained by a memory than by a block. Evidence: superposition in one vector holds `C(d) = Θ(d / log n)` hypotheses before cross-talk breaks the frontier expansion (2505.12514), and it emerges only in a narrow logit regime (2509.23365); K1.2 buys a factor `m`. A set in a hashed bit memory holds `S` hypotheses with zero interference, and hashed addresses are the one lever that paid in this project (−0.79% at 22M) and in the field (L³ 2601.21461; Engram 2601.07372).

**Definition.** Block unchanged. A per-sequence memory of `S` bits for the hypothesis set and an `S×S` bit relation, filled by the fast stream, iterated by boolean algebra.

```
h(u) ∈ {1..S}^κ        # κ learned LSH hashes: sign(W u) buckets; κ = 2, S = 4096
ingest: for each relation pair (u → v) found by one thresholded attention head:  E[h(u), h(v)] := 1
seed:   F_0 := onehot(h(q))                              # q = the query item
step:   F_k := F_{k-1} ∨ (F_{k-1} E)                     # boolean matrix-vector product
halt:   F_k = F_{k-1}                                    # exact test, k ≤ K
readout: y = Dec(F_K ; s_T)                              # the fast stream reads F_K by cross-attention
```

Gradients reach the hash projection and the relation head through straight-through estimators; deep supervision on `F_k` against the true frontier when the task gives it (CLRS-style, 2205.15659), otherwise on `y` alone.

**Properties.** Buys B2 (the frontier is a set, never a vector), B1 with certified halting, A1 exact for the closure (lookup by address, no T2 term), and A3 for monotone relations. Risks: B4 is lost in the monotone form (no deletions); the relation head is a gate and our gates collapse (REVISE, EVENTS); prose contains no closures, so on FineWeb this is dead weight (C2) and is gated off by task.

**Guarantee (Kleene halting with capacity S).** `Φ(F) = F ∨ FE` is monotone and inflationary on the finite lattice `2^[S]`, so the chain `F_0 ⊆ F_1 ⊆ …` stabilises at the least fixed point above `F_0` in at most `diam + 1 ≤ S` steps, and `F_k = F_{k−1}` certifies it exactly. By induction on path length, `F_k` is the k-step reachable set of the hashed relation. With `n` items and a uniform hash, all addresses are distinct with probability `≥ 1 − n²/2S`; with `κ` hashes the false-positive rate for a frontier of size `F` is `(1 − e^{−κF/S})^κ` (the Bloom bound), so soundness holds with `S = O(F log 1/ε)`. Contrast with K1.3 and K2.1: no contraction, no convexity, no uniqueness; the certificate coexists with `S` simultaneous hypotheses. Not guaranteed: that the relation head extracts the right edges (A1 and C1 in the fast stream are untouched); anything non-monotone; anything on prose.

**Kill test (CPU, under 1 h, under 1M params).** Directed reachability with the graph as edge tokens in context: `n = 64`, diameter `D ≤ 8`, frontier up to 32, `d = 64`, where single-vector capacity `C(64) < 32`. Arms: 2-layer block plus CLOSURE; the same block looped `D` times with a continuous thought (K0 at matched depth). Pass: CLOSURE ≥ 95% at `F = 32` with halting step equal to the true BFS depth on ≥ 90% of inputs, and ≥ 90% at `n = 256, D = 16` without retraining. Failure means the hash and relation head are not learnable through STE at this scale; dead. If K0 also reaches 95% at `F = 32`, the capacity argument is void and C dies with it.

**Prior art.** Neural Bloom Filters 1906.04304: hashed additive set memory, one-shot membership, trained without BPTT. Neural execution of graph algorithms 1910.10593 and CLRS 2205.15659: GNNs imitate BFS steps with a learned termination network; algorithmic alignment 1905.13211. Continuous-thought BFS 2505.12514 and its dynamics 2509.23365. Fixed-point halting in looped models: FPRM 2606.18206, RSM 2603.15641. Titans 2501.00663: test-time memory, dense, no set semantics. New: the frontier is a boolean set in hashed address space inside a language-model block, with the relation stored by address rather than read by attention, so halting is a lattice certificate and capacity is `S`, not `C(d)` or `m·C(d)`.

**P(beats K0 at equal compute on a reasoning benchmark): 0.35.** It wins where the benchmark is a closure (mazes, reachability, Sudoku's candidate elimination, the same lattice argument downward) and K0 spends depth re-deriving a set it cannot hold; it loses on everything non-monotone, and its one learnable part is a gate.

## What I concede to the loop camp

Depth is real and K0 has it. Both candidates compose with K0; neither needs it. Decision rule: run H's kill test first (one afternoon, existing harness), C's second, and take the survivor into K0's V1 as a fourth arm.
