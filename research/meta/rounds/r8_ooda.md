# Military Doctrine: The OODA Loop

## Objects and Techniques
- **Objects:**
  1. **Orientation ($O_2$):** Boyd’s synthesis state (genetic heritage, cultural tradition, previous experience, new information) filtering observations into action repertoires.
  2. **Implicit Guidance & Control (IG&C) Links:** Direct $O_2 \to \text{Observe}$ and $O_2 \to \text{Act}$ pathways in Boyd’s 1995 diagram bypassing explicit *Decide* ($D$).
  3. **Auftrag / Schwerpunkt:** Commander’s intent defined as an equivalence class of acceptable future end-states rather than a sequence of orders.
- **Techniques / Theorems:**
  1. **Destructive Deduction & Creative Induction (Boyd, 1976):** Unstructuring domain sequences into atomic parts and re-binding $k$ cross-domain constituents to escape Gödel/Heisenberg/entropy lock-in.
  2. **Tempo-Induced Orientation Collapse (Boyd, 1986; Richards, 2004):** Generating fast transients so an adversary’s state merges pasts with divergent futures, inducing bisimulation failure and paralysis.
  3. **Fingerspitzengefühl:** Executing $O_2 \to \text{Act}$ via simultaneous $k$-way conjunctions of fleeting tactical cues without serial deliberation.

## Mapping to the Problem
- **Roles:** *State* = **Orientation ($O_2$)**; *Rule* = **IG&C link**; *Check* = **Reconnaissance-in-force (active Moore probe)**; *Search* = **Destruction-and-Creation ($D\&C$) rebinding**.
- **P1 (Representation):** A $k$-way term is **Fingerspitzengefühl**—binding $k$ concurrent tactical conditions in one step along the IG&C link, bypassing serial *Decide* steps.
- **P2 (Learning):** **Reconnaissance-in-force** overcomes dilution (fog of war) by injecting fast transients that force the environment to expose future-equivalence classes.
- **P3 (Memory):** **Auftragstaktik** compresses raw battle logs (KV cache) into *Schwerpunkt* (minimal Nerode state).
- **P4 (Retrieval/Binding):** **Destructive deduction** strips surface chronology to bind past states by *Auftrag* (future-outcome equivalence).
- **P5 (Language):** Rules of engagement and legal clauses where $k$ dispersed conditions jointly trigger an immediate operative obligation.
- **P6 (Verification):** **Red-team transient probing** acts as Moore’s distinguishing experiment across candidate orientations.
- **P7 (Capability):** Zero-latency state re-orientation under mid-context rule flips without "first-owner" inertia.
- **P8 (Test):** Diluted rewrite chains where 3 dispersed sub-chain states must satisfy a joint SET trigger.

## Mapping from the Problem
- **Nerode classes** formalize *Orientation ($O_2$)*: two histories share an Orientation iff all subsequent maneuver sequences yield identical outcomes. "Operating inside the adversary’s OODA loop" means refining the true Nerode partition faster than the adversary splits their state space.
- **$k$-way terms** formalize *Creative Induction*: pairwise attention models linear attrition, whereas $k$-way logits capture simultaneous multi-axis synergy (*cheng/ch'i*) that collapses an adversary's state in one step.

## Yield: **FRAME**
OODA cleanly separates serial *Decide* (pairwise chain-of-thought) from parallel *IG&C* ($k$-way binding over Nerode states), though it imports no formal theorem beyond bisimulation and multilinear algebra.

## Concrete Proposals

### 1. IG&C State-Character Attention
**Mechanism:** Project recurrent states into a Nerode bisimulation space ("Orientation states" $s_j$) trained via future-equivalence distance. Compute cubic/Newton $k$-way logits $\langle q_i, s_j \odot s_k \rangle$ over past *states* rather than raw token embeddings ("Creative Induction"). Route high-confidence $k$-way state matches through a direct residual bypass ("IG&C link") that updates the recurrent state in one step.
- **Experiment & Kill Number:** On diluted Hierarchical-SET (each card is the terminal Nerode state of a 32-token rewrite chain with 80% filler; 3 cards must match), kill if accuracy fails to beat pairwise state-attention + Nerode loss by $\ge 25$ points ($<80\%$ vs. $\sim 55\%$).
- **Prior Art:** Boyd, *Destruction and Creation* (1976); Zhang et al., DBC bisimulation (2021); Newton Attention (2026).

### 2. Fast-Transient Moore Contrastive Loss
**Mechanism:** Combat narrative dilution without certificates by branching sequences at random steps with shared synthetic continuation probes ("reconnaissance transients"). Use a $k$-way multilinear head across a prefix pair $(u, v)$ and $k-2$ probe rollouts to estimate future-equivalence distance directly from uncertified trajectories. Train the recurrent state distance toward this empirical $k$-way bisimulation metric.
- **Experiment & Kill Number:** On uncertified 1,024-step diluted rewrite chains (960 classes, 90% filler), kill if linear probing recovers $<800/960$ classes or $<85\%$ exactness.
- **Prior Art:** Moore, *Gedanken-experiments* (1956); Boyd, *Patterns of Conflict* (1986); Castro, scalable bisimulation (2020).
