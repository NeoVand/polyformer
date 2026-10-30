# Questions worth asking a strong mind (23 October 2026)

Context for the reader: `EXACTNESS.md` (the selection theorem, the invariance term, results, the two halves),
`INVARIANCE.md` (the group-task evidence), `LEAN_PLAN.md` (the program). The questions are grouped by what
an answer would change. Each one is phrased so that it can be pasted as a prompt.

## A. Proofs we want written properly (Argon first, then verified)

A1. **Blindness of a length-L loss.** State and prove: for a recurrent state h_{t+1} = T(h_t, x_t) with
readout r, and a transition T = T* + δ with per-step error ε = ‖δ‖ in the readout's metric, the
teacher-forced next-token loss over sequences of length L differs from the loss at T* by O(L ε²) in the
typical case (random drift) and O(L² ε²) in the worst case, while the error at length N is Ω(N ε) in the
worst case. Make the constants explicit for a linear readout with margin m. Conclude the condition on ε for
exactness at N against the resolution of the loss at L.

A2. **First-order sensitivity of the invariance term.** For equivalent histories u ~ v of lengths ℓ_u ≠ ℓ_v,
show that d(N h(u), N h(v)) is Θ(ε · |ℓ_u − ℓ_v|) for a drifting transition, to first order, where N is the
readout's normalisation. Identify exactly which normalisations make the "shared common-mode direction"
trivial minimum possible (the raw RMS case we observed) and which exclude it (centred cosine after LayerNorm).
Give a general criterion: the distance must be invariant to every direction the readout discards.

A3. **The floor.** Empirically the term settles at a pair distance of 0.002–0.004 rather than zero, and that
floor shrinks with training length. Derive the floor from the finite number of partner pairs per step and the
noise of SGD, or from a bias of the centred-cosine distance; predict how it scales with batch size, number of
partners, and L; say which lever lowers it fastest.

A4. **The identity minimum on structured state spaces.** On an orthogonal state updated by learned rotations,
the term switched on at initialisation selected the trivial representation (all rotations identity). Prove
that for any invariance term and any group representation, the trivial representation is a global minimiser
of the term alone, and characterise the schedule (delayed start, or a lower bound on the primary loss's
progress) under which the joint minimiser is a faithful representation instead.

A5. **Growth, not level.** Prove that under a drifting transition the expected growth rate of the pair
distance along the sequence is proportional to ε, while its level at the training length is dominated by a
transient that depends on the readout margin and not on ε. This justifies the diagnostic that predicted
drift at Spearman 0.86–0.91.

A6. **The minimiser is the minimal automaton.** Under what conditions (dense primary loss, exhaustive
equivalent pairs, capacity of h) is the joint minimiser of next-token loss plus compression term a bijection
onto the Nerode classes? Give a counterexample when the primary loss is diluted (section 7's Prop. A) and a
sufficient condition (Prop. B) with a proof rather than a sketch.

## B. Positioning questions (a literature-aware mind; verify every citation)

B1. **Bisimulation.** Nerode equivalence for MDPs is bisimulation. Deep bisimulation metrics (DBC, Zhang et
al. 2021) and MDP homomorphism learning train representations where behaviourally equivalent states
coincide. How exactly does the invariance term differ: certified versus learned equivalences, exactness and
length extrapolation versus control performance, a sequence model versus an MDP? Is there a prior result on
exactness or extrapolation from bisimulation objectives?

B2. **Path independence** (Anil et al. 2022) and **predictive state representations**: is "invariance across
different histories to the same state, as a loss" already in the literature under another name? Where is the
nearest prior claim of length extrapolation from such a loss?

B3. **Automata learning.** What does the theory of learning minimal automata from equivalence queries
(Angluin's L*) say about sample complexity when equivalences are given as random pairs rather than queried?
Is there a known rate?

B4. **Lean specifics.** Which equivalences of tactic scripts are decidable offline from LeanDojo traces
(alpha-renaming, independent reordering) and which need the kernel? Is there a canonical form of a proof
state that makes exact match well-defined across renaming and goal ordering? Has anyone used definitional
equality as a training signal?

## C. Design questions (a sceptical experimentalist)

C1. In stage one, what would make a pass unconvincing? (A transformer that also extrapolates because tier-1
rewrites are too easy; expression sizes where the finite state space is small enough to memorise; partners
that leak the answer.) Propose the control that catches each.

C2. What is the cheapest certified **distinction** term for natural text, given that paraphrase invariance
collapsed without it? Is there any public corpus where "two histories with different futures at an observed
position" comes with a certificate?

C3. How would a prover use an exact multi-step state tracker so that the gain shows as fewer kernel calls at
equal theorems proved, given the JEPA-for-Lean result that one-step ranking did not transfer?

## D. One question for a very smart generalist

D1. We have a learning rule that makes a carried state exact when the loss is dense in the state and the
equivalences are certified. Language gives neither for free. What is the most natural self-supervised
signal in ordinary text that is dense in the state, so that the same term would apply? Candidates we have
ruled out: predicting your own future state (collapses to a still state), suffix-gap weighting (finds the
end of the narrative, not decisions), paraphrase invariance alone (collapses). What have we missed?
