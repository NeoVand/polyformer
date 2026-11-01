# Round 8 status (orchestrator notes, written before mixing)

The agents run on Codex (algebraic attacks, L*, topological entropy, bundle adjustment) and on Gemini Argon (Sokoban,
OODA, loci, game balance), not on Claude: the weekly Claude limit was 91% used on 1 Nov. Each gets only R8_DRAW.md,
without the draw table.

## My own ideas before mixing (graded after)

**O1. Myhill, not Nerode: the k-way term is a two-sided congruence.**
- **The congruences.** Nerode's right congruence relates a past to its futures, a 2-way relation that a pairwise logit
  (query = now, key = then) can express. Myhill's syntactic congruence is u ≡ v iff xuy ∈ L ⇔ xvy ∈ L for all x, y,
  a 3-way relation (left context, middle, right context). Its classes form the syntactic monoid, which is the
  transition monoid: higher order is composition.
- **Claim to test.** Cubic attention is the natural form for span-level state: a logit scoring "the segment j..k
  maps the state at j to the state the query needs".
- **Capability.** Edit-stable and infill-stable state: change the middle of a document and recompute by composing
  the monoid elements of spans.
- **Prior art to check:**
  - associative scans for automata (Liu et al. 2023, "shortcuts to automata");
  - Krohn–Rhodes decomposition;
  - segment-tree incremental parsing;
  - fill-in-the-middle training.

**O2. Nerode-keyed attention, an induction head over states.**
- **Mechanism.** Key = the model's state at position j (an estimate of its Nerode class); value = what came after j.
  Query = the current state. The head retrieves "what happened next the last time I was in this state".
- **Relation to known heads.** Induction heads match by previous token, and infini-gram matches by longest suffix;
  both are Nerode classes of trivial automata.
- **Capability.** In-context learning of a new grammar or procedure from a few examples, beyond n-gram heads.
- **Training.** The Nerode metric loss supplies the keys.
- **Closest prior art:** Akyürek et al. 2024 (in-context language learning, n-gram heads, REGBENCH); induction heads
  (Olsson et al. 2022); infini-gram (Liu et al. 2024).
- **Kill.** No gain over n-gram-head transformers on REGBENCH at matched parameters.

**O3. Nerode–Fourier arity rule.**
- **Statement.** A task needs a k-way term exactly when the indicator of its futures has Fourier support of degree k
  over the item group. This joins the characters law (exact iff the channels hold all 40 characters) to Nerode
  classes.
- **Grade.** Probably FRAME. It would give a design rule (measure the task's degree, then pick the arity), not a
  capability.

**O4. Hankel matrix versus Hankel tensor.**
- **The matrix side.** Spectral learning of weighted automata (Hsu, Kakade and Zhang 2009; Balle et al. 2014) is
  linear-algebraic Nerode: the rank of the past × future Hankel matrix is the minimal state dimension (Fliess).
  MECHANISM's affine ~20-dimensional code is that object.
- **The tensor side.** A past × middle × future Hankel tensor would be the Myhill analogue, and its tensor rank the
  size of a cubic layer.
- **Capability.** Unclear. It might give a sample-complexity result for learning span-composition from data.

**O5. Entity tracking as 3-way binding.**
- **Mechanism.** Discourse needs (entity, attribute, time) triples, and models fail box-tracking tasks (Kim and
  Schuster 2023). A cubic head binds entity and attribute under the time order in one step.
- **Objection.** Pairwise attention with recency solves many such tasks.
- **Status.** Dead unless the task needs a genuinely 3-way condition.

## Step 3: mixing (after all eight reports)

**Yield (my grading, stingier than the agents' own):** 0 HIT, 5 TOOL, 3 FRAME.
- TOOL: L* (counterexample repair of false merges), topological entropy (the entropy-minimality certificate), bundle
  adjustment (state = elimination message), Sokoban (trace quotient), loci (entity slots plus a neutral space).
- FRAME: algebraic attacks (state = the ideal of surviving assignments), game balance (Harsanyi dividends; its
  multiplicity diagnosis is new), OODA.

The agents' math checks out where we use it:
- radical Boolean ideals: equal varieties ⇔ equal ideals;
- the Schur message: equal messages ⇒ indistinguishable futures, with the converse when probes can clamp the boundary;
- entropy-minimality for irreducible sofic shifts (Lind–Marcus);
- parity records: every proper marginal is uniform.

Two rounds in a row now without a HIT, so the skill says: stop, and gate the best candidate against live prior art.

**Convergence 1: bind classes, not tokens.** Six of eight, from both model families: loci, game balance, OODA,
Sokoban, bundle adjustment, and algebraic attacks with its elimination step. Every higher-order run we made bound
*tokens*. In language a k-way relation holds between *entities or states*, each mentioned many times among filler.
Over tokens, k-tuples are dominated by spurious tuples. One entity mentioned three times is a "three equal cards"
SET. Newton's e_k counts k-subsets of positions, not of entities. That is a second reason for the null in language,
beside "no keys or values". It is the balance agent's diagnosis and is still a conjecture. Our Nerode work produced
exactly the quotient, mentions → classes (MECHANISM: 960/960), and never fed it to a k-way head.

**Convergence 2: quantify over futures, don't average.** Five of eight: L*, game balance, Sokoban, OODA, entropy.
- **What L_M does.** It averages the future distance over random shared continuations (an on-policy bisimulation).
  Nerode equivalence quantifies over *all* futures.
- **Why that failed under dilution.** The decisive future, the one question that separates two owners, is rare, so
  it gets almost no weight. A premise whose effect is purely k-way has zero lower-order (Harsanyi) signal under
  random continuations. Hence the first-owner heuristic.
- **The fix in its standard form.** L*'s counterexample processing, or Ferns' max-over-actions metric: train on
  distinguishing suffixes found by search, using the task's oracle (the dilution harness has an interpreter).

**The two failures are each other's missing piece.** The k-way head needs quotiented objects to bind. The quotient
needs ∀-future training, and the distinguishing future is often a k-way conjunction, which a k-way head can select.

## Candidate C1: class-level higher-order binding (from convergences 1 and 2)

**Mechanism:**
1. A slot memory where each slot holds one Nerode class (an entity or sub-state), written by gated pointer updates.
   Narrative that does not touch a slot takes a no-write path (the neutral space of loci; Sokoban's commuting walks).
2. The k-way (Newton or cubic) term runs over slots with unit weight per class, never over tokens.
3. The slots are trained with a ∀-future Nerode loss: distinguishing questions are found by an oracle or by search
   and weighted by the max, not the mean.

**Addresses:** P1, P2, P3, P5.

**Experiment:**
- **Task:** diluted multi-entity tracking with a k-way query. Entities change attributes over a narrative with 2,000
  filler tokens, each entity is mentioned 1–6 times, and the query is a SET-type condition over three entities'
  current states.
- **Arms, at matched parameters:**
  - (a) a softmax transformer;
  - (b) token-level cubic or Newton attention;
  - (c) the slot memory with pairwise attention;
  - (d) the slot memory with the k-way term;
  - (e) arm (d) with the averaged L_M in place of the ∀-future loss.
- **Kill:** (d) under 90%, or under 15 points above the best of (a)–(c).
- **Diagnosis kill:** if (b) scores as well on tokens with repeated mentions as on single mentions, the multiplicity
  conjecture is dead.

**Adversary:**
- Clift et al. 2020 already ran 2-simplicial (cubic) attention over *entities* (BoxWorld).
- Relational memory over slots: Santoro et al. 2018, and RIMs (Goyal et al. 2019), whose sparse updates are the
  neutral space.
- Entity memories: EntNet (Henaff et al. 2017).
- Frontier models with chain of thought solve entity tracking by writing a table.
- The new part is only the Nerode-trained quotient feeding the k-way term, plus the multiplicity diagnosis.

**Score (novelty / feasibility / cost / impact):** 2.5 / 4 / 4 / 3. **Weakest sub-problem:** P7, the capability. It
is a synthetic task until it is shown on real text.

## Candidate C2: the ∀-future Nerode loss (from convergence 2, cheap)

**Mechanism:** Replace the average over random continuations in L_M with the max over a searched set of
distinguishing questions. The search uses Rivest–Schapire binary search on a counterexample, with the interpreter as
the oracle.

**Test:** the dilution harness where L_M produced the first-owner heuristic (probe 0.452). **Kill:** probe < 0.5 again,
or no gain in exactness.

**Prior art:**
- Ferns et al. 2004: the bisimulation metric uses a max over actions.
- Castro 2020: neural bisimulation in deterministic MDPs.
- Weiss et al. 2018: L* extraction from RNNs.

**Score:** 2 / 5 / 5 / 2. It fixes our own failure; it matters only if dilution is the obstacle somewhere real.

## Kept from the agents, not in a candidate

- **Entropy-minimality as a certificate of generative support.** If a model's outputs never leave the target shift
  and their entropy equals the target's, the model generates all of it. This is a TOOL for Sketchpad-style
  certification of *generation* rather than computation.
- **The Nerode state as a boundary response function** (bundle adjustment), and as the ideal of surviving
  assignments (algebraic attacks). The state of a reasoning task is its solution set.

## My own ideas, graded

- O1 (Myhill/span): FRAME. The span query "a past segment (j, k) with net effect g" is a genuine 3-way query over
  prefix holonomies. Its trilinear form is tr(gᵀ P_k P_j⁻¹), which is new to us, but no need for it is in sight.
- O2 (Nerode-keyed retrieval): absorbed into C1.
- O3: FRAME. It is the subset-expansion theorem we already had.
- O4: TOOL. Hankel rank versus arity is the communication-complexity argument of Sanford et al. 2023, so it is
  owned.
- O5: absorbed into C1.

## Step 4: live prior-art gate (Codex with web search, 1 Nov; `r8_gate.md`)

Its 2026 arXiv citations have not been opened by me.

| Claim | Verdict | What remains open |
|---|---|---|
| C1a: k-way attention over slots or entities | PARTIAL | Clift et al. 2020 own the core: three-way attention over entity representations, with temporary "virtual entities". A persistent, deduplicated entity memory under long dilution is not covered. |
| C1b: tokens give spurious k-tuples (multiplicity) | OPEN | No paper found. Roy et al. 2025 report token-level trilinear gains on language benchmarks, so it is not a blanket failure. |
| C1c: training the state toward Nerode / bisimulation | OWNED | Zhang et al. 2019 (causal states); Hong, Dragan and Levine, ICLR 2024 (history representations with an on-policy bisimulation loss, including GPT-2 on Wordle); DBC; MICo. |
| C2: counterexample or max-over-futures state training against dilution | PARTIAL | Ferns 2004 defines the max metric; Weiss 2018 and Carr 2019 use counterexamples for extraction or retraining; no state loss fixing dilution was found. |
| C3: entropy-minimality as a generator certificate | PARTIAL | Polyvyanyy et al. (TOSEM 2020) use entropy measures for language coverage in process mining. A neural-generator certificate is open; it needs exact support containment and exact entropy. |

**Verdict.** No leap survives the gate.
- **What is ours.** Two small, testable pieces, both diagnoses of our own past nulls: C1b (multiplicity) and C2
  (averaged versus ∀ futures).
- **What C1 would have to show.** That tuple contamination causes the dilution failure, and that binding deduplicated
  entities fixes it beyond matched token-cubic and pairwise-slot baselines.
- **Cheapest test of both diagnoses.** About $5 and a day on Modal: (i) Newton or cubic heads on Match-3 with 1–6
  repeated mentions and filler, against single mentions; (ii) L_M with a max over the interpreter's questions on the
  dilution harness.

Harness yield: rounds 7 and 8 each produced 0 HITs that survived. By the skill's rule, rounds stop here.
