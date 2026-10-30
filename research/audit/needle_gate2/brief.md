You are the kill gate for round-2 research hypotheses. Use live web search. Same protocol as before. For each:
- **(1) Prior art.** Citation with link, date, a short verbatim quote, and STATES / IMPLIES / PARTIAL / UNRELATED.
- **(2) Triviality and correctness.** As a hostile referee: is the core a classical theorem (name it)? Is anything
  mathematically wrong?
- **(3) Verdict.** KILL / NARROW (give the surviving form) / PASS.

Finish with a ranked table.

Context: a 4B chat LLM executes finite-state table programs under a "pinned" KV-cache policy (keep the program's
cache, evict history, restart positions). A per-row certificate is proved necessary and sufficient (Lean). Also in
Lean: for history-keeping decoders no finite test suite certifies exactness (an explicit decoder passes every finite
suite with strict margins and fails later), and the W-method with ε ∈ W. Separately, small recurrent "trackers"
(width 128) trained on S₅ word problems are exact on random words but fail on some periodic words (8 of 10 seeds).

**G1. Training sees the Lyapunov exponent, not the joint spectral radius.** Next-token or readout training on random
words constrains a trained tracker's average contraction: the top Lyapunov exponent of the random product of
Jacobians along reached states (Furstenberg–Kesten). Exactness on every word needs the worst case, the joint
spectral radius of the cell-to-cell Jacobians under the automaton's constrained switching, and by Berger–Wang the
worst case is approached on periodic words. Claims:
- (a) This explains why trained trackers are exact on random words and fail on periodic ones.
- (b) A computable certificate for trained trackers on group automata is an upper bound on the constrained JSR over
  the reached cells (SOS or ellipsoidal norms, Parrilo–Jadbabaie), applied to neighbourhoods. That would address
  the open problem of per-state certificates for trained weights on non-absorbing automata (Bugaud 2026: a single
  forward-invariant set exists only for absorbing languages).
- (c) It predicts which periodic words fail: those whose monodromy spectral radius exceeds 1.

Check: JSR and RNN or neural-network stability; constrained switching systems and the JSR (Dai; Philippe, Essick,
Dullerud & Jungers 2016); Berger–Wang; Lyapunov exponents of trained RNNs (Engelken, Wolf & Abbott 2023;
Vogt et al.); Bugaud 2026a, b (CQLF, forward-invariant sets); Brandoit 2026; certified RNN state tracking with
switched-system tools.

**G2. Faithful-rank theorem.** Any stabiliser that changes the Jacobian at a state centre by an operator of rank r <
d_faithful(G) (the minimal faithful real representation dimension, 4 for S₅) cannot contract all group-tangential
directions (Weyl and Eckart–Young). Hence radial norm rescaling (PAR, Wang et al. 2026, arXiv 2610.27628) cannot
certify S₅, and rank 4 is sharp. A word such as (s₁s₂)³ can contract although each generator expands its own axis,
by 120° cone rotation. Check the mathematics carefully: a restoring word is a composition of several steps, each
with its own rank-r change.

**G3. Exact semantic entropy of a program compiler, and a length-uniform guarantee.** A model compiles a question x
into a table T. The behavioural class [T] is the minimised transducer up to renaming, so equivalence is decidable
and the exact semantic entropy H([T]|x) is computable. Procedure:
- sample k tables;
- ask the person short distinguishing questions, each a word of length ≤ n_i+n_j−1 (Moore), chosen by generalised
  binary search, until one class remains.

Claims:
- (b) A Fano lower bound: P(wrong machine) ≥ (H − q·log|O| − 1)/log|C|. A calibrated compiler is an optimal
  questioner.
- (c) With split-conformal calibration of the stopping rule, the pinned certified executor satisfies P(wrong answer
  at length L) ≤ α + 1/(N+1) **for every L simultaneously**. For history-keeping decoders no finite-length
  calibration transfers across lengths. This is a separation.
- (d) Any proof of correctness needs a state bound and at least n|Σ| atomic checks.
- (e) An equivalence-marginalised likelihood −log Σ_{T∈[M*]} p(T|x) lowers H at equal training steps.

Check: semantic entropy (Farquhar et al. 2024), conformal prediction for LLM code or programs, active automata
learning and minimally adequate teachers (Angluin; L*; TTT), interactive program synthesis with distinguishing
inputs (ExReg, Nguena Timo 2026, SemRegex, Ji et al. "question selection for interactive program synthesis" PLDI
2020), query-by-committee, generalised binary search, and equivalence-aware or permutation-invariant losses.

**G4. Switching on as conflict resolution.** Where a constant steering vector fails to switch on an executor and a
rank-1 weight edit succeeds, the reason is a small, certifiable set of mutually incompatible row requirements on the
vector. The input-dependent gate b^T h of a rank-1 edit resolves them, and the gate can be predicted from the frozen
model before fine-tuning. Check: steering-vector failure and geometry papers (2024–2026), ROME, function vectors,
linearised fine-tuning theory, and "why LoRA rank-1 works".

**G5. Canonical frames by cold prefill.** In a stack policy for a pretrained LLM, a frame's write-time KV (computed in
context) carries ancestor information even when the read-time mask hides the ancestors. Recomputing the frame cold
(prefilling its symbol alone at fixed positions after the program) makes it history-free at every layer, which is
what a finite certificate needs. Check: KV-cache reuse and position-independent caching (CacheBlend, EPIC, Prompt
Cache), "information leakage in KV caches", and recomputation for context compression.
