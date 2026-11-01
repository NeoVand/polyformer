# Round 8 (1 Nov 2026): what in Nerode and higher-order attention we failed to carry over

**Neo's words:** "I think there is something in nerode and higher order attention that we failed to carry over."

**Goal.** Find a mechanism or theorem that joins two of our threads and gives neural sequence models a significant
new capability, testable by one person in weeks. The threads:
- **Nerode's state theory.** A state is the class of pasts that have the same futures. Other parts of it: the minimal
  automaton, the bisimulation (Nerode) metric, and Moore's finite distinguishing experiments.
- **Higher-order attention.** A logit with a k-way term binds k items in one step, as in cubic and Newton attention.

## Step 0: three facts from the primary notes

1. **Higher order: the win was exact and narrow.**
   - A cubic logit ⟨q_i, k_j ⊙ k_k⟩ solves SET at 100%; pairwise attention reaches about 57%. SET is a three-card
     match over Z_3^4.
   - **Why.** Per attribute, the SET rule contains an "all three equal" term, and no sum of pairwise logits contains it.
     For every degree-2 form, the double-centred (j, k) logit matrix does not depend on the query (the coupling
     barrier).
   - **Order-k blindness.** Match-k needs a k-way logit term.
   - **Newton attention** (power sums with Newton's identities) made Match-4 exact. The characters law: a run is exact
     exactly when its channels carry all 40 characters of Z_3^4.
   - **Language models.** None of this gave a gain: the S0–S2 runs were null, and S6 was −0.4% at equal FLOPs.
2. **Nerode: the network finds the minimal automaton, and a Nerode loss trains it.**
   - On certified rewrite chains, the exact recurrent state is the minimal automaton: 960 of 960 classes, held in a
     ~20-dimensional code that is affine in the string but not systematic.
   - A loss that trains the readout's distance toward the bisimulation metric,
     d(u, v) = ‖o(u) − o(v)‖ + γ E_x d(ux, vx), makes the recurrence exact at 1,024 steps on its own.
   - Under dilution (long irrelevant narrative), the state learns a "first owner" heuristic instead.
3. **The two threads never met.**
   - **Higher order went one way.** We moved on to "higher order is composition": products of group or matrix
     elements (holonomy attention, a matrix-state recurrence that DeltaProduct-style models already cover).
   - **Nerode went another way.** It survived only as Moore's finite test, inside a certified bounded-view computer
     (Sketchpad).
   - **What was never studied.** No experiment asked what a k-way term means in Nerode terms, or what attention
     keyed by Nerode classes would do.

## Sub-problems

- **P1 representation:** what does a k-way term compute, in terms of classes of futures, that pairwise terms cannot?
- **P2 learning:** how does a network find Nerode classes without a certificate (where dilution defeated us)?
- **P3 memory:** a KV cache stores every past token, while a minimal state stores one class. What lies between
  (compression)?
- **P4 retrieval and binding:** retrieving by equivalence of futures rather than by similarity of content.
- **P5 language:** where natural text has k-way dependencies or a Nerode structure that matters.
- **P6 verification:** what certificate either thread gives.
- **P7 capability:** what a user would see that current models cannot do.
- **P8 test:** a small experiment, with a number that kills the idea.

## Constraint sweep

Each line names a constraint and what dropping it opens.

- **Attention reads tokens.** Drop it and attention can read states, spans or futures.
- **Softmax normalisation.** Drop it and the normalisations of Newton arities or of subsets (the free-field
  generating function) become available.
- **A fixed arity k.** Drop it and the arity can be learned, or summed over all subsets.
- **Next-token loss only.** Drop it and future-equivalence (Nerode) losses become available.
- **A state vector.** Drop it and the state can be a partition, a monoid element or a matrix.
- **The goal is perplexity.** Drop it and the goals can be exactness, length extrapolation, sample efficiency,
  in-context learning of rules, compression or editing.
- **A causal left-to-right model.** Drop it and two-sided contexts (infilling, editing) open up.
- **A pretrained model.** Drop it and small from-scratch models become candidates.

## Dead framings

A variant of any of these needs a stated change of level.

- Higher-order or Newton heads as a perplexity gain for language models (null, or below 1%).
- A new matrix-state recurrence against DeltaNet and DeltaProduct (they already cover it).
- Revisable memory, mixture-of-depths routing or selective attention (null at 2k).
- Self-predictive state objectives (trivial minima).
- Latent recurrence inside a pretrained model (it collapsed).
- Loops that converge; long arithmetic for its own sake; a universal interpreter as the claim.
- Certified CLRS-style algorithms (DNAR owns these); certified retrieval.

## The draw

The fields come from the unstuck skill's 40-item offline list, which is unprincipled (one author's stand-in), plus
its list of academic cores. Draw: seeded RNG 20261102, six fields from the list and two academic cores. Skipped: the
fields of rounds 6 and 7. Subfields: the next eight digits, with index = (digit mod 8) + 1.

| Field | Subfield list (8) | Digit → pick |
|---|---|---|
| 31 puzzle design | 1 nonograms · 2 sliding-block puzzles · 3 crossword construction · 4 Sokoban · 5 uniqueness in constraint puzzles · 6 disentanglement puzzles · 7 puzzle-hunt metapuzzles · 8 cryptic crosswords | 3 → **4 Sokoban** |
| 6 cartography / SLAM | 1 map projections · 2 loop closure · 3 map generalisation · 4 triangulation surveys · 5 occupancy grids · 6 topological maps · 7 bundle adjustment · 8 place recognition | 6 → **7 bundle adjustment** |
| 24 military doctrine | 1 OODA loop · 2 mission command · 3 centre of gravity · 4 combined arms · 5 deception operations · 6 lines of communication · 7 manoeuvre warfare · 8 wargaming (Kriegsspiel) | 8 → **1 OODA loop** |
| 34 sign language | 1 classifier predicates · 2 spatial referencing (loci) · 3 non-manual markers · 4 fingerspelling · 5 iconicity · 6 emergence of home sign · 7 role shift · 8 phonological parameters | 9 → **2 spatial referencing (loci)** |
| 10 cryptanalysis | 1 frequency analysis · 2 differential cryptanalysis · 3 linear cryptanalysis · 4 cribs and the bombe · 5 index of coincidence · 6 side channels · 7 meet-in-the-middle · 8 algebraic attacks (linearisation, XL, Gröbner bases) | 7 → **8 algebraic attacks** |
| 7 chess and game design | 1 endgame tablebases · 2 opening books · 3 combinatorial game theory · 4 game balance (cost curves) · 5 procedural generation · 6 hidden-information design · 7 Elo rating · 8 retrograde chess problems | 3 → **4 game balance** |
| core: learning theory | 1 VC dimension · 2 query learning of automata (Angluin's L*) · 3 mistake bounds · 4 Rademacher complexity · 5 identification in the limit · 6 compression schemes · 7 statistical-query lower bounds · 8 teaching dimension | 9 → **2 Angluin's L*** |
| core: symbolic dynamics | 1 shifts of finite type · 2 sofic shifts · 3 topological entropy · 4 Markov partitions · 5 state splitting · 6 cellular automata · 7 zeta functions · 8 sliding block codes | 2 → **3 topological entropy** |

## Mapping protocol (each agent, alone)

Name 3 objects and 3 techniques or theorems of your subfield. Then map in both directions:
- **To the problem:** for each Pi, what in the subfield plays the role of the state, the rule, the check and the
  search? Which technique transfers?
- **From the problem:** what do Nerode classes and k-way terms say about the subfield?

Grade the yield HIT, TOOL, FRAME, LOW or nothing. HIT means it imports a theorem or mechanism we did not have; be
stingy with it. End with at most two concrete proposals. Each proposal gets its mechanism in three sentences, a small
experiment with a number that would kill it, and the closest prior art you know, with years.

Each report is at most 500 words and goes to `rounds/r8_<slug>.md`.
