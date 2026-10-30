# B3. Theory lens: certainty as a capability

Language models can be confident, never certain. Under the pin, one forward pass per reachable row fixes what the
network does on a program at every length, so questions with no finite test for unpinned decoding (Moore 1956;
`no_finite_test_suite`) become finite checks. Three ways to use that, ranked:

## 1. Certified discovery: a world model that knows it is exact

**The demo.** A 4B model in a browser presses the buttons of a mystery machine it has never seen and writes its law
as a table. It announces "identified: 11 states, certain for any machine with at most 12", then predicts the next million
presses with zero errors.

**The belief it overturns.** That neural networks cannot induce exact rules (ARC; Gupta, Sanders & Solar-Lezama
2025), that learned world models drift (Dreamer, Genie), and that a model can never be certain. Moore's theorem
stands; the demo meets it by printing the state bound.

**The mechanism.** Three parts; only the first is new.
1. **Sound counterexamples** (Lean-able). With certified rows the model's predictions equal the hypothesis
   table's (Theorem P), so every disagreement with the box refutes the hypothesis, never the execution. An uncertified
   predictor's slips pose as counterexamples. Soundness is what L\*'s convergence needs.
2. **Counterexample processing** (Rivest & Schapire 1993). A binary search over prefixes finds a distinguishing suffix
   in O(log ℓ) queries. Each refinement adds a Nerode class, so an n-state box takes at most n rounds.
3. **Stopping** (Vasilevskii 1973; Chow 1978). For a declared bound m, the hypothesis's W-method suite is m-complete.
   Passing it, composed with Theorem P, gives box ≡ table ≡ network-under-clock on every input, for any box with at
   most m states.

The guarantee is classical; the learner is new, and its semantic priors ("a coin counter") should cut queries. Why
not call Python, as WorldCoder (Tang, Key & Ellis 2024) does? Then the law lives outside the network. Here it is the
network's own world model, provably drift-free.

**The team's assets.** Savant writes and certifies tables; Theorem P lets the suite's predictions be read off the
certified table. v1's exact trackers converge to the minimal automaton (960 clusters, 960 classes). WebGPU is ready.

**The smallest 48-hour experiment.** 40 hidden Mealy machines (3–16 states, 3–5 buttons, English labels): 20
random, 20 semantic (turnstile, combination lock, coin sums, mod-k counter, traffic light). Each round, Savant reads
20 random presses and writes a table, rows are certified, the harness runs the (n+1)-complete suite, and shortened
counterexamples go back; at most 8 rounds. Compare plain L\* (AALpy) on queries to the first correct hypothesis,
and count spurious counterexamples from base Qwen3-4B and a frontier model predicting by plain decoding.
Local, about $0.

**What kills it:**
- Savant identifies under half the semantic machines, or needs as many queries as L\* on them: the LLM adds
  nothing, and this is L\* with a slow executor.
- Any "identified" claim is wrong within its bound: a bug in the trusted base.

## 2. The ∀ badge: answers that carry a theorem about the network

**The demo.** Asked a new question ("is this 50,000-digit number divisible by 7?"), the model answers with a
kernel-checked Lean theorem: for every input of every length, this network on this code path answers correctly. The
proof is the model's own one-line account of what each of its states means.

**The belief it overturns.** That networks can be verified only locally on bounded inputs, that self-explanations
are post-hoc, and that hallucination is inevitable.

**The mechanism: a Nerode certificate** (new, generic). A table T computes a spec f at every length if and only if
its reachable states can be labelled with meanings (predicates on prefixes) so that the start meaning holds of the
empty input, every row preserves meaning, and every output is right under its meaning. Soundness is induction; for
completeness, label each state with the Nerode class of f its prefixes share (well defined because T is correct).
Templates proved once in Lean (positional carry a + b + c = o + 10c′; residue fold r′ = (br + d) mod k; bounded
counters) turn each row's obligation into a `decide`. With Theorem P: network ≡ table ≡ spec. Execution and meaning
become the same kind of certificate, one check per row; the explanation is the proof. Outside the proof stay
code-path determinism and the question-to-spec step, shown as one Lean line.

**The team's assets.** Lean, `adder_clock_correct` (the hand-made instance), Theorems P and P-M, Savant's tables.

**Prior art to separate from:** Lewandowski et al. 2026 (one fixed simulator) and, not in the map (verify),
self-proving models (Amit, Goldwasser, Paradise & Rothblum 2024; per-input proofs) and Clover and AlphaVerus
(programs run outside the model).

**The smallest 48-hour experiment.** In Lean, prove the generic theorem and three templates. Do no training: Savant
appends one meaning per state. Pose 30 held-out questions (arithmetic in bases 2–16, multiplication by a constant,
divisibility, Luhn and ISBN check digits, comparison). Count end-to-end theorems, rows right but meanings rejected,
and accepted theorems contradicted by a random 10,000-digit test (must be zero).

**What kills it:**
- Under 30% end to end where tables are at least 80% right: the model computes but cannot say what.
- Templates that need a human proof per task.

## 3. The ratchet: self-improvement that cannot forget

**The demo.** Overnight, the model writes programs for problems it failed on, keeps those that come with a for-all
theorem and trains its own compiler on them. By morning its ledger shows k new skills, each a theorem, and every old
skill re-proved on the new weights.

**The belief it overturns.** That self-improvement reward-hacks or collapses, and that no one can certify an update
broke nothing (for unpinned decoding, a theorem).

**The mechanism.** The overlooked half of Theorem P is necessity: under the pin the per-row certificate is a
*complete* regression suite, equivalent to every skill being exact at all lengths (Theorem C extends it to composed
calls). Accept an update only if the library recertifies, and certified capability can only grow. The reward is a
theorem, so Goodhart enters only at the displayed question-to-spec step. It targets REASON's measured weak point:
writing and reading programs.

**The team's assets.** WEIGHTS (rank-4 adapters certify 252/256 tables; 30 steps switch on the interpreter), GSM8K
retention, Theorem C, idea 2's checker.

**The smallest 48-hour experiment.** The model generates 500 questions. Train one STaR-style LoRA round on proved
triples, and one on triples whose execution is certified but whose meaning is unproved. Then recertify the whole
library (256 G1 tables, the adder, the register-machine rules, 2,079 Lag rules) and rerun GSM8K. About $30.

**What kills it:** the held-out proved rate rises by less than 5 points, proved data does not beat unproved data, or
no update passes recertification.

## If I could only pursue one

**Idea 1.** It alone shows *behaviour*, a model deciding on its own that it is done, rather than a badge. Nobody
expects a neural network to do exact science and know when it has finished. Build idea 2's checker the same week: it
is the fallback if idea 1 dies, and the reward for idea 3.
