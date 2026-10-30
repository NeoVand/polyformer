# Why training finds near-exact states, and the term that selects exact ones

22 October 2026. The theory the last two weeks were missing. The constructions (a per-event recurrence,
an orthogonal carried state, an energy block) all work; training finds the exact version on some seeds
and a drifting one on others, with identical training loss, decided below the precision of the loss and
even by the machine's rounding (SELFSTATE S2). This note says why that is forced by the objective, and
what term removes it.

## 1. Selection is invisible to a length-L loss

Let the carried state be updated by a learned transition T, and let the exact transition T* be the one
that composes the generators faithfully. Suppose training finds T = T* + δ with per-step error ε = ‖δ‖ in
the relevant norm. Over a training sequence of length L the state error is at most of order L·ε (worst
case) and typically of order √L·ε (random drift), and the loss, which is smooth at its minimum, changes by
at most order L²·ε² (worst case) or L·ε² (typical). With L = 16 and the measured end-of-training loss of
5·10⁻⁴ (VALIDATION V2), any ε below about 5·10⁻³ is invisible: the exact and the near-exact transition are
the same minimiser to the precision of the loss. Extrapolation to N events needs the accumulated error
below the decision margin, i.e. ε of order 1/N or smaller, which at N = 256 is 4·10⁻³. So the exact
solution sits inside the flat set of minimisers, and which point of that set training reaches is set by
initialisation and rounding. This is the measured behaviour: exact on one seed of three, drifting at 82 to
85% at 256 on the others, with the same loss; and on the group manifold, exact on four of six, with the
drift now a mixing between equivalent copies of the representation (ENERGY E2), which is again a flat
direction of the length-16 loss.

The fix cannot be more data at the same length (the flat set does not move) and cannot be longer training
sequences alone (the flat set shrinks as 1/L, which buys a constant factor at a linear cost).

## 2. The term that selects: invariance over equivalent histories

Two histories u and v are equivalent, u ~ v, when they determine the same future: in the word problem,
when the words multiply to the same group element; in language, when the prefixes are paraphrases or
translations; in code, when two programs have the same trace. The Nerode theorem says the classes of ~
are the states of the minimal automaton of the data.

Add to the next-token loss an invariance term on equivalent pairs:

```
L  =  CE(x_{t+1} | h(u))   +   μ · d( h(u), h(v) )      for u ~ v
```

with d a distance after normalisation. Two properties, both provable:

- **Length-independent sensitivity.** For a drifting transition, d(h(u), h(v)) on a pair of equivalent
  words of lengths ℓ_u, ℓ_v grows with the drift accumulated along the longer word; choosing pairs whose
  lengths differ (a word and its reduced form, which has length at most the group's diameter) makes the
  term's gradient with respect to ε of order ε·ℓ, not ε²·ℓ, and independent of the training length L of
  the next-token loss. The flat set of section 1 is no longer flat: only T* makes the term zero on all
  pairs.
- **The minimiser is the minimal automaton.** If h is invariant on every equivalent pair and sufficient
  for the next token, then h factors through the Nerode classes and separates them, so h is a bijection
  onto the states of the minimal automaton. This is the address: the orbit, obtained as a consequence of
  the loss. The collapse that killed "predict your own future" (SELFSTATE S2) does not exist here: the pairs
  carry the input, so the invariant state cannot be the input-averaged state.

Where the pairs come from: for groups, any word and its reduced form, free; for language, paraphrase and
translation corpora, abundant, which is Lake and Baroni's orbit training stated as a loss on states
rather than as data augmentation; for code, programs with equal traces, free from an interpreter.

## 3. The test (event word problem, under $10)

Arms, three seeds, trained at e ≤ 16, tested at e = 64 and 256: the one-slot per-event recurrence of V2;
the same with the invariance term on pairs (word, reduced word) at μ ∈ {0.1, 1}; the orthogonal-state
version of E2 with and without the term. Registered prediction: with the term, exact (≥ 99%) at e = 256
on 3 of 3 seeds for the Euclidean state, and the drift of any non-exact seed below 1% at 256; without it,
1 or 2 of 3 as measured. Diagnostics: the invariance distance on held-out pairs against the per-event
drift, which the theorem says are proportional. Kill: no improvement in the exact-seed count.

If it passes, the language form is the next test: paraphrase pairs on the dilution harness (two
narratives with the same decisions and different wording) and then on a public paraphrase corpus at 22M,
where the prediction is a gain on far-repeat buckets at equal FLOPs, because invariance across wording is
what carrying an entity across a document requires.

## 4. First result (22 Oct, branch `claude/invariance-3e22f3`, INVARIANCE.md 5.1, $2.36)

The term works, with one correction to section 2 that the data forced. With the distance taken on the
raw state (RMS-normalised), the term found a trivial minimum: a shared component along the direction the
readout's LayerNorm removes made every state nearly parallel to every other (unrelated states 0.002
apart, norms growing from 9 to 2,800), paying the term while leaving the readout's view, and its drift,
untouched; exactness fell to 0 of 3. With the distance taken in the readout's own normalisation (centred
cosine), the recurrence is exact at e = 256 on 3 of 3 seeds (1.000 / 0.998 / 1.000, drift under 0.2
points) against the base's 2 of 3, and at e = 1,024, sixty-four times the training length, 1.000 / 0.912
/ 1.000 against the base's 0.533 on its drifting seed. "d a distance after normalisation" must mean the
readout's normalisation: the invariance has to hold where the state is read. The proportionality of
section 2 holds in its growth form: the growth of the centred-cosine distance between equivalent pairs
from e = 16 to e = 256 has Spearman +0.81 with the drift to 256 and +0.90 with the drift to 1,024 across
arms and seeds; its level at the training length does not predict drift, which is the transient the
readout's margin absorbs. Seeds 3-5 are running to separate selection from a one-seed flip.

## 5. Final result of the group test (INVARIANCE.md, 75 runs, $3.89)

- Over six seeds, the base recurrence is exact at e = 256 on 3 of 6; with the term in the readout's view
  and reduced-word partners, 5 of 6 (p ≈ 0.11 under a 50% rate: evidence, not proof). With random
  equivalent partners of every length, 3 of 3 exact to e = 1,024 with a pair distance that does not grow
  along the sequence at all: that is what exactness looks like. Trained at only 8 events, the base is at
  chance by 256 on every seed; the random-partner arm is exact on 3 of 3.
- The mechanism is invariance across paths: pairs that share the path and differ only in distractors
  leave drift at the base's value (control, 2 of 3), so nothing here is a generic consistency regulariser.
- The orthogonal state collapses to the identity if the term is on from the start (0 of 9) and is exact
  to 1,024 on 3 of 3 if the term is held at zero until a representation exists (delayed term). Order of
  supervision matters: first represent, then make the representation invariant.
- Corrections to section 2: (i) d must be measured where the state is read; (ii) the proportionality
  is between the *growth* of d along the sequence and the drift (Spearman +0.86 to 256, +0.91 to 1,024
  over 42 runs), not its level at the training length; (iii) length-independence holds in the weak form:
  the term's floor shrinks with training length rather than vanishing, so its sensitivity is first order
  in the drift but not independent of L. The term is a regulariser with a floor, not a projection onto
  the exact point; the floor is lowest with random-length partners.

## 6. The language form, first attempt (PARA_INVARIANCE.md, 39 runs, $4.77): fail, and why

Paraphrase invariance on the dilution harness collapses: every invariance arm drives the distance between
*unrelated* narratives to 0.001 along with the paraphrase distance, the state becomes constant in the
readout's view, paired accuracy stays at 0 (hand labels 0.066, the decision objective 0.135), and the
control with unrelated partners is indistinguishable from the paraphrase arm, so the kill fires. The
reason is the regime, not the term: on this harness the base model's states already barely depend on the
narrative (unrelated distance 0.02, against 1.1–1.5 for the group recurrence), because the next-token
loss is diluted and rarely needs the owner. Invariance can only select among states the primary loss
already forces to carry the input; it cannot create that need. On the group task every event changes
the answer, so the need was there. The Nerode condition has two halves, compression (equivalent
histories agree) and distinction (inequivalent histories differ); the group loss supplied distinction
for free and language does not. The hinge that pushes intervention pairs apart supplies it, but alone it
is paid by the first-owner shortcut (paired 0.14 = the heuristic), and with paraphrase invariance added
it reaches the heuristic on one seed of three. The language form therefore needs both halves at once and
a primary loss that is not diluted at the state, which is the open design problem; it is the same
problem the dilution study named, now stated as a condition on the objective rather than a weight.

## 7. The two halves, stated (23 October 2026)

**Setting.** Histories u ∈ Σ*, a state map h: Σ* → ℝ^d read through a fixed normalisation N (the readout's),
and a primary per-token loss ℓ(x_{t+1} | h(x_{≤t})). Nerode equivalence: u ~ v iff for every continuation w
the future is the same, i.e. P(· | uw) = P(· | vw). The minimal automaton's states are the classes of ~.

**Definition (Nerode objective).** For sampled equivalent pairs (u, v) with u ~ v and inequivalent pairs
(u, v') with a continuation w on which their futures differ,
```
L_N = E_{u~v} d(N h(u), N h(v))        (compression)
    + E_{u≁v'} max(0, m − d(N h(u), N h(v')))   (distinction)
```
added to the primary loss. Compression needs known equivalents (reduced words, alpha-renamed programs,
paraphrases). Distinction needs known inequivalents whose futures differ *at observed positions*.

**Proposition A (compression alone selects only within the need).** Let S be the set of state maps that
minimise the primary loss to within its resolution at the training length L. The compression term
restricted to S selects the maps whose per-step error ε is smallest in the readout's view, with first-order
sensitivity in ε (section 2, corrected by section 5). If the primary loss does not force the state to
depend on the input (its dependence on h(x_{≤t}) is below resolution at most positions), then the constant
map is in S, the compression term is zero on it, and the minimiser collapses. This is the paraphrase
failure of section 6: compression cannot create the need the primary loss leaves out.

**Proposition B (distinction is supplied by a dense primary loss).** If for every pair of inequivalent
histories the primary loss differs at a position within the training window with probability bounded
below (every event changes the answer, or every statement changes the trace), then the constant map is
not in S, S contains only input-dependent maps, and compression on S selects the exact one. This is the
group task and the execution task. On language the probability is of order the decision density, about
1/p ≈ 1/100 (the dilution measurement), so distinction must be added as a term or the data must be chosen
to make consequences dense.

**Corollary (where the objective applies as is).** Any domain with (i) free, provable equivalences and
(ii) a trace that depends on the state at every step: group words, program execution, games with full
state, simulations. Natural text has (i) only approximately (paraphrase) and (ii) only at the decision
density, which is why the language form is the open problem and execution is the next test.

**What would make the language form work.** Either a contrastive distinction term whose inequivalent
pairs are chosen by a future that actually differs at observed positions (the intervention pairs of the
dilution harness are such pairs, but their difference is one terminal token, which the shortcut absorbs),
or a primary loss that is dense in the state, which on language means predicting something the state
determines at every position: the trace of an execution, a running summary, a game's state. The second
is the running-state supervision that made the transformer exact on late evidence, and the question of
whether it can be self-supervised on prose is open; "predict your own future" (SELFSTATE) is not it.

## 8. One equation: the Nerode metric (23 October, night)

**Observation.** The arms of LEAN_H implement the three clauses of the Myhill–Nerode theorem separately. The
cross-entropy makes the state consistent with the output; NextLat (predict the next state from the current
state and the next input) makes the state a *right congruence*, the Markov property; the invariance term
makes the congruence the *coarsest*. The minimal automaton is the coarsest right congruence consistent
with the output, so the combination is the theorem written as a loss, and each single term leaves open the
flat direction the others close. Prediction P8.1: on tier 2 and on natural proofs, where sampled
equivalences cannot cover the state space, the single terms separate from the combination and the
combination is the only arm that holds.

**Definition (Nerode metric).** For histories u, v with outputs o(u), o(v) (next-token distributions) and
next inputs x, the bisimulation metric d* is the unique fixed point of
```
d(u, v) = ‖o(u) − o(v)‖  +  γ · E_x d(ux, vx)         (0 < γ < 1)
```
(Ferns, Panangaden, Precup 2004 for MDPs; for a deterministic automaton with outputs the kernel of d* is
exactly the Nerode equivalence: d*(u, v) = 0 iff u ~ v). The **Nerode metric loss** trains the state so that
the readout distance equals d*:
```
L_M = E_{(u,v,x)} [ d_N(h(u), h(v)) − ‖o(u) − o(v)‖ − γ · sg d_N(h(ux), h(vx)) ]²
```
with d_N the centred-cosine distance in the readout's view and sg a stop-gradient on the successor term
(as in deep bisimulation for control, Zhang et al. 2021). Certified equivalent pairs enter with target 0;
inequivalent pairs need no certificate: their target is positive from the outputs along their futures.

**Claims to prove (P8.2–P8.4).** (i) The zero set of L_M at its optimum is the Nerode partition; (ii) the
constant map is not a minimiser whenever two sampled histories have different outputs, so the collapse of
PARA_INVARIANCE cannot occur; (iii) L_M contains the three clauses: output consistency (the first term),
dynamics consistency (the successor term, NextLat's content), and coarseness (the zero target on
equivalent pairs, the invariance term's content).

**Registered tests (tonight).** T8.1 tier 1 parity: L_M alone exact at 256 on 3/3. T8.2 tier 2 separation:
R+I, R+NL below exactness; R+NL+I and L_M exact at 256 on ≥ 2/3. T8.3 language-shaped (the dilution
harness, where paraphrase invariance collapsed): L_M does not collapse (unrelated distance stays above
0.3), the running-state probe rises from 0.27 (chance 0.25) to ≥ 0.5, and paired decision accuracy exceeds
the unweighted 0.01 by 3×; kill: collapse or no probe gain. T8.4 the dream's mechanism, on certified chains:
a search for a target tree with and without the tracker's imagination; kernel calls to solve at equal
success rate fall by ≥ 30% with the exact tracker.

### 8.1 Corrections from review (same night, before the runs registered)

- **Scale.** Both sides of the recursion must live in [0, 1]: d_N = (1 − cos)/2, output difference as total
  variation (or normalised Hamming distance between target trees), and
  `d(u, v) = (1 − γ)·‖o(u) − o(v)‖_TV + γ·sg d(ux, vx)`. Without the (1 − γ) the target can exceed the
  distance's range and the regression saturates at antipodal states, which is not the fixed point.
- **Same input to both.** The recursion is a bisimulation metric only when the same next input is fed to
  both histories. On chains, inequivalent pairs take the next rewrite from the intersection of the
  rewrites applicable to both trees, else the output term alone. On language, the recursion runs on
  matched-template pairs (paraphrases at event boundaries; intervention pairs, which share their
  continuation); unrelated pairs enter through the output term only. A recursion over each history's own
  continuation is a trajectory distance whose kernel is not Nerode.
- **max versus expectation.** With max over inputs the kernel of d* is Nerode equivalence outright; with an
  expectation it is Nerode equivalence when every input has positive probability. We use the expectation
  (sampled inputs) and state the full-support condition.
- **What the chain task does and does not test.** On rewrite chains the supervised target is the state
  itself, so the output term already separates inequivalent histories and the metric's distinction half
  is redundant there; T8.1 and T8.2 test the compression and successor halves. The test of "distinction for
  free" is T8.3, where the output (the next token) does not reveal the state and the recursion must carry
  the decision's difference back to earlier positions: the target for an intervention pair k events before
  the decision is γ^k (1 − γ), so γ must be high (0.9–0.95) and the floor (0.0002) must stay below it.
- **Clause (ii) stated precisely.** The successor term constrains distances between successors, not the
  successor states themselves: it is dynamics consistency in the metric sense, weaker than NextLat's
  prediction of the next state vector, and sufficient for the fixed point.

### 8.2 Proofs of the metric's two properties (written 23 Oct, night)

**Setting.** Deterministic system: histories u ∈ Σ*, outputs o(u) in a bounded metric space with distance
‖·‖_TV ∈ [0, 1], inputs x drawn from a distribution π with full support on Σ, discount 0 < γ < 1.

**Lemma (existence, uniqueness).** The operator (F d)(u, v) = (1 − γ)‖o(u) − o(v)‖_TV + γ E_{x∼π} d(ux, vx)
maps bounded functions on Σ*×Σ* with values in [0, 1] to themselves and is a γ-contraction in the sup norm:
|F d − F d'|_∞ ≤ γ |d − d'|_∞. By Banach it has a unique fixed point d* with values in [0, 1].

**Proposition P8.2 (zero set = Nerode partition).** d*(u, v) = 0 ⟺ u ∼ v.
(⇐) If u ∼ v then o(uw) = o(vw) for every w, so the function d₀(u, v) := 0 on equivalent pairs, and d*
elsewhere, satisfies the fixed-point equation on equivalent pairs (both terms vanish because ux ∼ vx for
every x); by uniqueness d* = d₀ there, i.e. d*(u, v) = 0.
(⇒) Suppose d*(u, v) = 0. Then (1 − γ)‖o(u) − o(v)‖_TV = 0, so o(u) = o(v), and E_x d*(ux, vx) = 0 with
d* ≥ 0 and π of full support, so d*(ux, vx) = 0 for every x ∈ Σ. By induction on |w|, d*(uw, vw) = 0 and
o(uw) = o(vw) for every w, which is u ∼ v. ∎
*Remark.* With max_x in place of E_x the same proof holds without the full-support assumption. With a
sampled expectation the zero set is exact; the positive values differ between the two definitions.

**Proposition P8.3 (no collapse).** Let h_c be any constant state map. Then d_N(h_c(u), h_c(v)) = 0 for all
pairs, and the metric loss on a pair (u, v) with o(u) ≠ o(v) equals ((1 − γ)‖o(u) − o(v)‖_TV + γ·sg(0))² > 0.
If the training distribution puts positive mass on pairs with different outputs, every constant map has
loss bounded away from zero, while the map h* with d_N(h*(u), h*(v)) = d*(u, v) (which exists whenever the
readout view has enough dimensions to isometrically embed the finite sample of d*, and approximately
otherwise) has loss zero on the fixed point. Hence no constant map is a minimiser. ∎
*Remark.* This is exactly what paraphrase invariance lacked: its term is zero on the constant map.

**Proposition P8.4 (the three clauses).** At a zero of the metric loss on all pairs and inputs:
(i) output consistency: o(u) ≠ o(v) ⇒ d_N(h(u), h(v)) ≥ (1 − γ)‖o(u) − o(v)‖_TV > 0, so different outputs
have different states; (ii) dynamics consistency: d_N(h(ux), h(vx)) = (d_N(h(u), h(v)) − (1 − γ)‖o(u) −
o(v)‖_TV)/γ averaged over x, so the distance of successors is determined by the distance of predecessors
and their outputs (a metric-level right congruence; weaker than NextLat's vector-level prediction);
(iii) coarseness: u ∼ v ⇒ d_N(h(u), h(v)) = d*(u, v) = 0 by P8.2, so equivalent histories share a state in
the readout's view. Conversely (i) and (iii) together say the readout-view partition of Σ* equals the
Nerode partition, i.e. the states are the minimal automaton's. ∎

**What is not proved.** That gradient descent on the sampled loss reaches the fixed point; that the floor
under finite sampling is below the smallest target that matters (γ^k (1 − γ) at distance k from a
differing output); and anything about tier 2, where the metric arm was the weakest term, which the
pending diagnosis addresses.

### 8.3 Verdicts of the night (23 Oct, ~04:30)

- **Metric alone, tier 1 (T8.1): pass.** L_M with no other term is exact at 256 and 1,024 on 3/3.
- **Tier 2 was under-training, not size (METRIC §5).** At 24k steps R+NL+I is exact at 256 on 2/2; the
  metric arm gains 0.10 but its floor still grows along the sequence, so on size-changing rewrites the
  metric is the weakest of the three clauses' incarnations and the combination of the two separate terms
  is the strongest. P8.1 (separation) holds in the direction "combination first", with the single terms
  and the metric below it.
- **The 80k-chain loss of exactness was drift from a diluted term (LEAN_S).** On the lost seeds the pair
  distance grew 25–28× from 8 to 256 while the floor level stayed where exact runs have it; four times the
  partners per step, or μ = 3, restores exactness on 2/2. The term's strength must scale with the data per
  step, as PROOFS A3's floor says; a fixed pair budget is a bug in the registered scale axis, now
  explained and fixed.
- **Language-shaped, corrected (T8.3′): not killed, not a win.** With matched pairs and γ = 0.9 the
  state moves: the running-state probe rises from 0.27 to 0.45–0.48, paired decision accuracy from 0.000 to
  0.07 (the decision objective with labels reaches 0.10–0.15), the ordering paraphrase < intervention <
  unrelated holds at the decision on 3/3 seeds with paraphrases. But what the state carries is the first
  owner: the model answers the first owner on 69–86% of decisions on two seeds and is near chance where
  that heuristic fails. The distinction half now exists without labels; what it distinguishes is the
  cheapest feature that separates the pairs, which is the shortcut. Section 7's condition stands: for
  language the recursion must be driven by futures that differ because of the state, and at this density
  the shortcut explains most of the difference. Open.
- **Natural proofs, stage two as designed (LEAN_N, $38.46): fail, for the predicted reason.** Every arm
  memorises the training proofs and is exact on held-out natural states only where the state is `no
  goals`; the MLP position-wise head over 256 padded state tokens breaks length extrapolation even on
  rewrite chains (stage one's linear-probe head is exact at 256 there; the MLP head is not), and the
  collapse diagnostic flags the invariance arms. The bottleneck is the readout, re-emitting a long
  structured state token by token, not the objective. The prepared fallback (DESIGN_NEXT A, a change
  readout: goals closed, hypotheses added, reconstruct the state) is launched as LEAN_N §7.
- **What the exact state is (MECHANISM, $1.79).** Under the term (alone or with NextLat; 12 of 12
  checkpoints) the readout-view states form exactly 960 tight clusters for 960 trees at purity 1.000, in a
  roughly 20-dimensional code that is 95–97% an affine image of the tree's one-hot Polish string; each
  rewrite acts on it as the linear map of the string permutation it induces (residual 1–4%, composing to
  2–5%), not as one map per lemma and path and not orthogonally (singular values 0.2–1.6). The plain
  recurrence uses 76–98 dimensions, is nonlinear from the first steps, and never forms pure clusters.
  NextLat alone also reaches one state per tree on its exact seeds, so the "unminimised automaton"
  hypothesis for NextLat is refuted: on this space both clauses lead to the minimal automaton.
- **Beyond length: nothing (MECHANISM item 3).** No arm reads unseen atom names or a fifth atom (exact at
  step 0: 0.000), and a held-out (lemma, address) event is applied correctly on first occurrence 18–51% of
  the time. The objectives buy length generalisation within the training distribution of events and
  nothing outside it. The fix is structural, not an objective: atom identities must be unlearnable
  (fresh embeddings per chain) and the readout must point at the chain's atoms rather than name them; a
  registered test of that is running. For a prover this is the real axis: new symbols every theorem.
- **Natural proofs with the change readout (LEAN_N §10, $42.05 total): the gate fails, and the reason
  is now exact.** The readout learns what kind of step a tactic is, closing a goal, adding a hypothesis,
  or other, at 0.90–0.94 in distribution, and keeps closures exact on longer proofs (0.93–1.00); it never
  produces the tokens a step introduces: the rewritten target is exact on 0–2% of rewrite steps and an added
  hypothesis on 6%, so free-running reconstruction is 0.000 for every arm, and all arms including the
  transformer sit within 0.03 of each other. On natural proofs the obstacle is content generation, not
  state tracking: a quarter to a third of tactic steps introduce new mathematical expressions that the
  tracker must write out, which at this size and with 2,850 training proofs no objective supplies. The
  invariance machinery is orthogonal to that bottleneck. Consequence for the dream: a tracker can imagine
  exactly the steps whose effect is determined by the state (closures, structural changes) and must call
  the kernel, or a larger generator with retrieval, on steps that introduce content; the prover proxy's
  saving applies to the first class. Stage two is a negative result with its reason, not a dead end.
