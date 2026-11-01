# Subfield: Chess and Game Design — Game Balance (Cost Curves)

## Objects and Theorems
* **Objects:**
  1. **Hedonic Mana/Material Cost Curve $C(S)$:** Non-linear valuation mapping stat/keyword bundles to scalar cost (e.g., chess piece values plus the non-linear Bishop-pair bonus; CCG mana curves).
  2. **Combo Payoff Tensor:** $k$-piece/card subsets whose joint value jumps superadditively across a phase boundary (mating nets, 3-card infinite combos).
  3. **Iso-Cost Role Class:** Distinct board/hand histories inducing identical tempo and win-probability trajectories across opponent responses.
* **Techniques / Theorems:**
  1. **Harsanyi Dividends / Möbius Subset Inversion (Harsanyi, 1963):** $\Delta_S(v) = \sum_{T \subseteq S} (-1)^{|S|-|T|} v(T)$, isolating pure $k$-way synergy from lower-order marginals.
  2. **Conway Thermography (Berlekamp, Conway & Guy, 1982):** Decomposing a combinatorial game state into *mean value* (baseline material) and *temperature* $t(G)$ (tactical volatility / branching urgency).
  3. **Strict Dominance Pruning:** Eliminating states/cards whose cost exceeds and continuation outcomes are dominated by a simpler state.

## Bidirectional Mapping
* **To the Problem** (*State* = equivalence class of board/hand histories; *Rule* = transition/payoff table; *Check* = tactical probe; *Search* = combo discovery):
  * **P1 (Representation):** A $k$-way logit computes the **order-$k$ Harsanyi dividend** $\Delta_S$ of the Nerode future-value functional. Pairwise attention sees only degree-2 marginals; in SET, $\Delta_T = 0$ for $|T|<3$ while $\Delta_{\{i,j,k\}} \neq 0$ (a pure 3-card combo with zero 2-card marginal).
  * **P2 (Learning):** Under dilution, 1-step bisimulation collapses because uncompleted combo pieces have zero 1-step marginal value under random continuations. Transfer **$k$-tuple Moore probing**: evaluate candidate states alongside $(k-1)$ cached partner states.
  * **P3 (Memory):** **Thermographic dominance pruning**: zero-temperature filler tokens ($d(u, ux) \approx 0$) and resolved ("spent") pieces merge into the baseline state vector; only high-temperature, unspent combo pieces stay in an active KV hand.
  * **P4 (Retrieval):** Retrieve by **role equivalence** (shared transition operator $\tau_x: Q \to Q$ on futures) rather than surface token similarity.
  * **P5 (Language):** Multi-clause contracts, mysteries, and diluted state tracking where $k$ scattered spans jointly trigger a rule, while individual spans repeat or drown in filler.
  * **P6 (Verification):** Finite **probe-by-state payoff matrix** certifying class rank and $k$-way character coverage.
  * **P7 (Capability):** Exact $k$-premise rule execution and state tracking across 10k+ tokens of narrative dilution.
  * **P8 (Test):** Diluted Span-SET and Diluted $k$-Premise Rewrite (below).
* **From the Problem:**
  * Nerode equivalence formalizes **functional card/position redundancy** (detecting disguised reprints across deck futures). The 40-character law of $\mathbb{Z}_3^4$ gives the exact algebraic dimension needed for a stat/cost system to represent $k$-way counter-play without degenerate meta-cycles.

## Yield: **HIT**
Imports **Harsanyi subset inversion** and **thermographic quotienting** to explain both failures at once: Newton power sums $p_r = \sum_t k_t^r$ failed in language because summing over raw tokens counts variable-length spans and filler with arbitrary multiplicity $m_c$, corrupting elementary symmetric polynomials $e_k$; Nerode failed under dilution because 1-step bisimulation assigns zero value to latent combo pieces with zero lower-order Harsanyi dividend.

## Proposals

### 1. Nerode-Quotiented Newton Attention (NQNA)
* **Mechanism:** Compress local spans into Nerode transition keys trained via bisimulation, and prune zero-temperature filler tokens that induce the identity transition ($d(u, ux) < \epsilon$). Quotient surviving keys by kernel density in Nerode metric space so each unique equivalence class $c$ enters with unit weight $w_c = 1/\text{count}(c)$ instead of raw token multiplicity. Compute Newton power sums $p_r = \sum_c w_c k_c^r$ over the deduplicated Nerode classes to recover exact $k$-way symmetric polynomials $e_k$ invariant to narrative dilution.
* **Experiment & Kill Number:** On **Diluted Span-SET** (12 cards phrased as 10-token clauses buried in 2,048 distractor tokens), kill if accuracy is $<90\%$ (where raw Newton and pairwise attention score $<60\%$).
* **Prior Art:** Harsanyi (1963, synergy dividends); Berlekamp, Conway & Guy (1982, thermography); Ferns et al. (2004, bisimulation metrics).

### 2. Harsanyi-Dividend Bisimulation Loss
* **Mechanism:** Augment the Nerode bisimulation loss with an order-$k$ Harsanyi contrast over tuples of cached past spans. Train the state representation so the inclusion-exclusion dividend $\Delta_{\{u_1,\dots,u_k\}} o = \sum_{T \subseteq [k]} (-1)^{k-|T|} o(\text{compose}(T, x))$ matches the future outcome jump under probe $x$. This forces the state to preserve latent combo premises whose 1-step marginal predictability is zero during long dilution stretches.
* **Experiment & Kill Number:** On 1,024-step rewrite chains with 85% narrative dilution and 3-way conjunctive transitions, kill if recovered minimal automaton classes fall below $850 / 960$ (vs. $<200$ under "first owner" collapse).
* **Prior Art:** Moore (1956, distinguishing experiments); Grabisch & Roubens (1999, Shapley interaction index); Castro (2020, deep bisimulation).
