# Sign Language: Spatial Referencing (Loci)

## Objects & Techniques
**Objects:**
1. **R-loci (Referential Loci):** Discrete coordinates in signing space (`IX-a`, `IX-b`) serving as overt spatial variables for discourse referents.
2. **Polyadic Agreement & Classifier Predicates:** Single-syllable articulations (`a-GIVE-b`, two-handed classifiers) whose path, orientation, and handshape simultaneously bind $k$ loci.
3. **Role Shift (Constructed Action):** Torso/gaze rotations that apply a rigid coordinate transformation to the entire locus map, shifting perspective without re-indexing entities.

**Techniques / Theorems:**
1. **Deictic-Anaphoric Variable Isomorphism (Lillo-Martin & Klima 1990; Schlenker 2011):** Loci are overt spell-outs of Dynamic Predicate Logic indices; unlike closed-class spoken pronouns, signing space is an open geometric register file $s: \text{Loci} \to \text{Referents}$.
2. **Maximal Contrast Partitioning (Kuhn 2015; Steinbach & Onea 2016):** New loci split signing space (ipsilateral/contralateral and nested sub-loci) only when referents have distinct discourse futures, while background narrative executes in unindexed "neutral space."
3. **Simultaneous Multi-Locus Binding (Meir 2002):** Agreement verbs compute $k$-ary relations directly over established loci in one step, decoupling narrative length ($T$ tokens) from relational composition ($M \approx 4\text{--}8$ active loci).

## Bidirectional Mapping

**To the Problem:**
- *Roles:* **State** = active R-locus register map; **Rule** = directional verb path/classifier transition (`a-VERB-b`); **Check** = sortal agreement + relational invariance under Role Shift; **Search** = deictic pointing (`IX-a`) vs. spawning a contrasted locus.
- **P1 (Representation):** A $k$-way term is a polyadic classifier predicate: it computes whether $k$ loci jointly satisfy a configuration (e.g., ternary alignment/SET) that pairwise verb paths cannot factor.
- **P2 (Learning):** Neutral-space routing transfers—irrelevant narrative executes in neutral space without writing to peripheral R-loci, preventing dilution ("first owner" collapse).
- **P3 (Memory):** R-loci sit strictly between a token KV cache ($T$ tokens) and one monolithic state: a factorized bank of $M \ll T$ **entity-level Nerode slots**.
- **P4 (Retrieval):** Pointing (`IX-a`) retrieves a locus by its future argument-structure affordances, not surface token similarity.
- **P5 (Language):** Coreference across perspective shifts (Role Shift) and simultaneous multi-actor constraints require $k$-way locus binding.
- **P6 (Verification):** Geometric locus disjointness (maximal contrast) certifies non-collision of distinct Nerode classes.
- **P7 (Capability):** Exact multi-entity tracking and $k$-ary constraint solving across 100k tokens of distractor narrative.
- **P8 (Test):** Diluted state tracking coupled with online 3-way SET queries over tracked entity states.

**From the Problem:**
- **Nerode classes** explain why signing space needs only $M \approx 6$ loci: an R-locus is the factorized Nerode class of all past clauses governing one entity's future transitions.
- **$k$-way terms** explain why sign languages grammaticalize simultaneous two-handed classifiers for ternary spatial relations: sequential pairwise agreement hits the coupling barrier on symmetric multi-entity predicates.

**Yield Grade:** **TOOL** (imports the architectural separation between $O(T)$ neutral-space narrative and $O(M^k)$ higher-order binding over $M$ Nerode locus slots).

## Proposals

### 1. Locus-Indexed Cubic Attention (LICA)
**Mechanism:** Instead of computing cubic logits $\langle q_i, k_j \odot k_l \rangle$ over all $T$ past tokens, the layer maintains $M=16$ spatial locus slots updated via gated pointer writes plus a "neutral-space" no-op sink for narrative tokens. A factorized bisimulation loss trains each locus slot to hold the local Nerode class of one entity's future transitions. Cubic/Newton attention then operates exclusively over the $M$ locus slots in $O(M^3)$ time per step, binding 3-way entity relations without token-level dilution or $O(T^3)$ cost.
- **Experiment & Kill Number:** Train a 4-layer model on 960-class rewrite tracking with online 3-way SET queries over entity states across 2,000 distractor tokens; **kill if accuracy is $<90\%$ or $<15\%$ above pairwise slot attention**.
- **Closest Prior Art:** Henaff et al., *Tracking the World State with Recurrent Entity Networks* (2017); Csordás et al., *The Devil is in the Detail: Simple Tricks Improve Systematic Generalization of Transformers* (2021).

### 2. Role-Shift Gauge-Invariant Bisimulation
**Mechanism:** Model context/perspective switches as a shared orthogonal operator $R_t \in O(d)$ rotating all $M$ locus slots simultaneously, analogous to sign language Role Shift. Train the Nerode bisimulation metric on the $k$-way cubic invariants $\langle s_a, s_b \odot s_c \rangle$ across slots rather than raw slot coordinates, making state equivalence invariant to perspective shifts. A new locus is spawned only when Moore's finite distinguishing test via the cubic readout exceeds threshold $\epsilon$ against all existing loci.
- **Experiment & Kill Number:** 960-class rewrite chains with random perspective relabelings and 10x narrative dilution at length 1,024; **kill if exact automaton recovery falls below $95\%$ (912/960 classes)**.
- **Closest Prior Art:** Schlenker, *Iconicity and Indexicality* (2011); Zhang et al., *Learning Invariant Representations for Reinforcement Learning without Reconstruction* (2021).
