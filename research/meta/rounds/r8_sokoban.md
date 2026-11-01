# Round 8: Puzzle Design — Sokoban

## Subfield Primitives
**Objects:**
1. **Canonical Pusher-Component State:** A board representation that quotients out exact player coordinates, storing box positions plus the connected component of empty squares reachable via zero-push walks.
2. **$k$-Box Freeze Deadlock:** A configuration of $k$ boxes and walls mutually blocking each other along both axes—an absorbing zero-future sink ($L(u)=\emptyset$).
3. **PI-Corral (Player-Inaccessible Corral):** An unreachable empty region bounded by $k$ boxes where only pushes on the corral boundary can alter internal reachability.

**Techniques / Theorems:**
1. **Nondeterministic Constraint Logic (NCL) Reduction (Culberson 1997; Hearn & Demaine 2005):** Proves Sokoban PSPACE-complete via 3-way AND gadgets (pushing box $A$ requires both boxes $B$ and $C$ displaced first).
2. **$k$-Box Deadlock Pattern Databases & Hall’s Marriage Bound (Junghanns & Schaeffer 1998):** Detects when $k$ boxes jointly freeze or violate bipartite goal-matching capacity, even when every $(k-1)$-subset remains solvable.
3. **PI-Corral Pruning (Junghanns & Schaeffer 1999; Shoham 2020):** Collapses commuting non-corral move sequences into a single canonical macro-transition on the corral boundary.

## Bidirectional Mapping
**To the Problem:**
- **Roles:** *State* = Canonical Pusher-Component + Boxes; *Rule* = NCL 3-way push gate; *Check* = $k$-box deadlock / Hall condition ($L(u)=\emptyset$); *Search* = PI-corral boundary pruning.
- **P1 (Representation):** A $k$-box freeze deadlock (e.g., 3 boxes + 1 wall in a $2\times 2$ block, or an NCL AND-gate) is a pure $k$-way predicate over the Nerode sink: every $(k-1)$-subset has winning futures ($L\neq\emptyset$), while the $k$-tuple forces $L=\emptyset$. Pairwise attention suffers order-$k$ blindness, seeing every box pair as movable.
- **P2 (Learning & Dilution):** Dilution is "pusher wandering"—reversible walks ($L(ua)=L(u)$) and commuting pushes in disjoint rooms ($L(uab)=L(uba)$). Quotienting by local reversibility and commutation recovers Nerode classes without certificates.
- **P3 (Memory):** PI-corral compression stores only the $k$ active boundary tokens of the current sub-problem, discarding solved interior items and walk history.
- **P4 (Retrieval/Binding):** Bind states by shared *push-affordance futures* rather than coordinate similarity.
- **P5–P7 (Language, Verification, Capability):** Multi-clause logical contradictions or resource locks where $k$ constraints jointly annihilate valid continuations; the mutually blocking $k$-tuple is an explicit deadlock certificate.

**From the Problem:**
- **Nerode classes** formalize Sokoban's canonical board equivalence: the minimal automaton has a single absorbing deadlock sink $\bot$ and quotients out Mazurkiewicz traces (commuting room pushes and zero-push walks).
- **$k$-way terms** measure a puzzle's *insight depth*: the minimum arity $k$ needed to recognize a nonlocal corral deadlock or NCL gate in one step without search.

**Yield Grade:** **TOOL** (imports PI-corral trace quotienting for P2 dilution and $k$-way sink detection for P1/P6).

## Concrete Proposals

### 1. Order-$k$ Deadlock-Sink Newton Attention
**Mechanism:** Instead of applying higher-order attention to raw token embeddings for perplexity, each state slot emits a vector of future transition affordances, and a Newton power-sum head computes $k$-way conjunctions that detect when $k$ items jointly annihilate all valid futures (entering the absorbing Nerode sink $\bot$). We train with a sink-Nerode objective that drives the state readout to zero ($o(u)=\mathbf{0}$) whenever a $k$-tuple closes a mutual-blocking cycle while keeping $(k-1)$-subsets non-zero. This turns $k$-way attention into a one-step detector of order-$k$ absorbing classes in the minimal automaton (P1, P6, P8).
**Experiment & Kill Number:** Train a 2-layer model with pairwise vs. order-4 Newton attention on serialized Sokoban/NCL traces (length 256) containing 4-way freeze deadlocks whose 3-subsets are all solvable. **Kill:** Order-4 Newton fails to beat pairwise deadlock accuracy by $\ge 25$ percentage points (or stays $<85\%$).
**Prior Art:** Junghanns & Schaeffer, *Rolling Stone* (1998); Hearn & Demaine, *NCL* (2005); Guez et al., *DRC on Boxoban* (2019).

### 2. PI-Corral Commutation Quotient Loss
**Mechanism:** Dilution defeats Nerode state tracking because irrelevant narrative steps drift the hidden state—identical to pusher wandering and outside-corral moves in Sokoban. We add an unsupervised trace-quotient regularizer gated by 3-way interaction footprints: when token $a$ has zero net binding with active boundary slots (reversible walk), enforce $\|s(ua)-s(u)\|_2^2 = 0$; when $a, b$ bind disjoint slot subsets (disjoint corrals), enforce $\|s(uab)-s(uba)\|_2^2 = 0$. This forces the recurrence onto the canonical pusher-component automaton without rewrite certificates (P2, P3).
**Experiment & Kill Number:** Run the diluted 960-class rewrite-chain benchmark at length 1,024 with $10\times$ narrative dilution plus the commutation/reversibility loss. **Kill:** State recovery falls below 90% of the minimal automaton (864/960 classes).
**Prior Art:** Mazurkiewicz, *Trace Theory* (1977); Junghanns & Schaeffer, *PI-Corrals* (1999); Shoham, *Festival* (2020).
