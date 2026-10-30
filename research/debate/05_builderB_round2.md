# Builder B, round 2 response

## H: fix (b) on every named gap; concede two points

**Gap 1, co-trained target collapses to next token** (1811.06407 confirmed: multi-step targets are critical). Fix: the NCE target is a frozen far-suffix bag, nothing co-trained.

```
z_t   = R · bag(x_{t+k+1 .. t+k+W})      # R fixed random d_z×V, k = 8, W = 128; no gradient anywhere
NCE_t = -log exp(⟨P s_t, z_t⟩/τ) / Σ_{t'} exp(⟨P s_t, z_{t'}⟩/τ)     # P learned, one-sided critic
```

The guarantee is now sufficiency of `s_t` for a fixed statistic of the far future, with no subspace to collapse into. Independent support: a bag-of-future-words target is one of the supervision changes that make path-star learnable in 2503.10542.

**Gap 2, shared B shrinks g_t.** Resolved by the same change: `B` receives no NCE gradient because it is no longer the target; `B` trains on `CE_b` alone, and `g_t` keeps its meaning.

**C2 on prose** (first mentions of names and numbers). Conceded: H is not a FineWeb candidate, and I expect ≤ 1% there. One deterministic filter removes the copy case at zero cost and with no gate:

```
g_t := g_t · 1[x_{t+1} ∉ x_{t+2 .. t+W}]     # a decision is a token the future depends on, not one it repeats
```

**"Backward encoder discarded at inference is not new"**: conceded; it was not among the two claimed novelties.

**Kill test.** Accepted as tightened: four arms (weight-only, NCE-only, both, hand labels), three seeds, `g_t` precision against hand labels reported at α = 0 before the ramp. Path-star conceded as not decisive for the weights: 2403.06963 Prop. 3 stands and none of the fixes in 2503.10542 is weight-only; path-star becomes the construction check of the NCE-only arm (pass ≥ 90%). Added kill rule: if weight-only does not beat unweighted by 3× on the dilution task, the gap is withdrawn and H reduces to the far-bag objective.

Prior art added: 1811.06407, 2503.10542. Probability: 0.35 on long-horizon decisions, 0.05 on depth-bound puzzles; the red team's split is right.

## C: concede the hashed version; fix (b) to positions as addresses, demoted

**Guarantee.** Conceded in full: Kleene holds for the quotient graph, whose closure is a superset of the truth; one collision imports a descendant set; the Bloom bound is for membership, not closure; κ hashes in one array mix under propagation. The 0.39 collision probability at n = 64 and the failure of the 90% criterion at n = 256 follow. Fix: addresses are context positions, so there is no quotient.

```
F ∈ {0,1}^T,  E[i,j] = 1 iff position j holds the head of a relation whose tail is the item at position i
E = Rel ∧ Id      # Rel: one learned, thresholded relation head; Id: same-item test, exact token equality for discrete ids
F_k = F_{k-1} ∨ F_{k-1}E ;  halt when F_k = F_{k-1}     # exact least fixed point in ≤ diam+1 steps, capacity T
```

This is 2402.01107's address space with a learned relation extractor and a convergence halt in place of a fixed loop count. Cost `T²` bits per sequence (2 MB at T = 4096) and one boolean mat-vec per step.

**C1.** Conceded to one STE map, the relation head; the identity test is a fixed rule for discrete ids. **C2.** Conceded: frontier supervision would make it a programmed BFS, so the kill test drops it; the only loss is on `y`. **C3.** Rebutted as glossed: 2405.09220 shows the standard model stores adjacency and partial reachability in weights and cannot derive reachability by transitivity; that is a failure of the block, not a niche that scale closes, and token-space closure costs Ω(F·D) tokens against D boolean steps. Conceded: closure-shaped tasks are a narrow slice of reasoning, and B4 is lost in the monotone form. **2509.23365** misattribution conceded; the word "narrow" is withdrawn, and the capacity argument stands only when n ≫ d, which is why the red team's n = 64 = d objection to the kill test is right.

**Kill test, as tightened:** n ≥ 1024 ≫ d = 64, no frontier supervision, relations stated in several indirect phrasings, arms = block + CLOSURE-P, 2402.01107's graph-head looped transformer, K0 at equal FLOPs. Pass: ≥ 90% at n = 1024, D = 16, and ≥ 85% at n = 4096 without retraining, with halting step equal to BFS depth on ≥ 90% of inputs. Failure means the relation head is not learnable from `y` through K ORs; dead.

Prior art added: 2402.01107 (closest), 2405.09220, 2408.10369 (BMLP, the same boolean recursion, not differentiable), 1711.04574 (∂ILP, soft forward chaining, which loses the exact halt). Probability of beating K0: 0.15 on closure-shaped benchmarks only. Its remaining use is as the exact-closure control arm that measures how much of K0's depth is spent re-deriving a set.

## Ranking and the pair

**Ranking: H first.** It targets T3, which no loop touches; its inference cost is zero; it has no gates, routers or discrete actions, so it passes C1 where every block we built failed; its signal is the project's one positive result, and reweighting has precedents at 1–7B (2404.07965, 2410.23771). I have not seen K4 and K5's definitions; if they are loop or energy blocks they buy T1 depth and a halting rule, which H does not, and they pay k× compute, unrolled-descent gradients (K2's defect) or a gate; on C1 and C4 I rank them below H and above C, and I accept the red team's order between them until I read the notes. C last, as a control.

**The pair:** I accept K0 + H and propose a coupling rather than a sum.

```
L   = Σ_t w_t · Σ_{i≤k_t} CE^{(i)}_t            # the gap weights every deep-supervision loss of the loop
k_t ← ⌈K · g_t / max_batch g⌉                  # the gap is the ponder target for K0's halting head
```

The second line gives B1's halting the training target BLOCK_THEORY says it lacks: iterate where the future says a commitment is being made. Falsifier, free in the same run: ablate the ponder target; pass when learned `k_t` correlates with the loss gain from extra iterations at ρ ≥ 0.5. Third leg if the budget allows: hashed n-gram input addresses (2601.07372; our −0.79% at 22M) for T2. Then K0 serves T1, H serves T3, addresses serve T2, one instrument per theorem, and the paired run is K0 against K0 ⋈ H on the dilution task and iGSM (2407.20311), never on FineWeb.
