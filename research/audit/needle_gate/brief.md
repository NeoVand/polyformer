You are the kill gate for a set of research hypotheses. Use live web search. For each hypothesis do two things:

**(1) Prior art.** Search adversarially (arXiv, OpenReview, ACL Anthology, PMLR, Google Scholar if reachable; 2015–Oct
2026, with extra care for 2025–2026). Give each close paper: citation with link, date, a short verbatim quote of the
decisive statement, and a verdict (STATES / IMPLIES / PARTIAL / UNRELATED).

**(2) Triviality.** As a hostile referee, say whether the core is an immediate consequence of a classical result (name
it), and what exactly would make it a real contribution.

Finish each with a verdict: **KILL** (published or trivial), **NARROW** (survives only in a stated narrower form; give
that form), or **PASS** (new as far as searched, non-trivial). Finish the whole report with a ranked table.

Context: a 4B chat LLM (Qwen3-4B, LoRA) executes finite-state programs written as tables Π in its context, under a
"pinned" KV-cache policy: keep Π's cache, evict history, show only (current state, current event), restart positions.
A per-row certificate (each table row's argmax with margin) is proved necessary and sufficient for exactness at every
length (Lean). Known prior art for that: Cai, Shin & Song 2017 (recursion and bounded-view verification for neural
programs); Schuurmans 2024; Lewandowski, Machado & Schuurmans 2026 (fresh-call harness executes Lag U(15,2));
Abbe et al. 2024 (inductive scratchpad); PENCIL (ICML 2025); Xu, Yang, Li & McAllester 2026 (universal computer
trained from scratch); MAKER 2025 (voting over bounded calls); Xiang 2026 (arXiv 2610.24133, prompt forgetting
O(P(log t)^{L−1}/t)).

Hypotheses:

**C1. Certified pushdown execution via a KV stack policy.** Extend the pin to visibly pushdown programs. On a call or
push symbol the policy keeps the model's current state frame's KV as a stack entry; on a return or pop it evicts the
closed scope and re-exposes the parent frame. At every step attention sees only Π, the top frame, and (state,
event), at fixed restarted positions. Claim: exactness on every input of every length and every stack depth holds
if and only if each reachable row (q, top, a) certifies (|Q|·|Γ|·|Σ| forward checks), in exact arithmetic, with a
margin version. Demo: Dyck-k, nested Boolean formulas and nested arithmetic at depth 500+ in a browser, where the same
model scores 2.4% on Dyck and 22% on BBH boolean expressions today. Check especially: Cai et al. 2017, PENCIL,
Pushdown Layers (Murty et al. 2023), stack attention (DuSell & Chiang 2024), StackTrans, neural stacks
(Grefenstette 2015; Joulin & Mikolov 2015), recursive LLM calls (RLM, Thread, recursive language models), Alur &
Madhusudan visibly pushdown automata, and any "certified" or "provable" recursion in LLM agents.

**C2. A predictive horizon law for plain decoding: collisions, not decay.** A content-addressed read fails when its
query admits a second referent within the margin. Two forms:
- (a) The address form. P(run exact to T) = E[∏_t (1 − q·1{the k-suffix before t occurred earlier followed by a
  different event})]. This gives a birthday horizon T₅₀ ≈ a^{k/2}·√(2 ln 2 / q).
- (b) The key form. Rows with a near-duplicate competitor lose about 1 logit per doubling of context once background
  mass exceeds 1, while the bulk margin stays flat.

A variant: the horizon t₀ = exp(Δ − σ²/2), from the target logit gap Δ and the background logit variance σ² (a
random-energy-model argument), with a correction that subtracts the mean key-value "bath". Check: Jelassi et al.
2024 (copying and n-gram matching), induction-head failure on repeated substrings, lost-in-the-middle theory,
attention dilution theorems, Barbero et al. over-squashing, random energy model analyses of attention, "context rot",
and needle-in-a-haystack theory.

**C3. A symmetrised restoring organ: a threshold theorem for neural executors.** Run k randomly re-encoded copies of
the program (consistent renaming of states and events from a large name pool, shuffled rows, varied separators)
under the pin, and take a plurality vote per step after mapping answers back. Claims:
- Enumerating all classes (program, state, event) across the k copies certifies the voted executor exact at every
  length if every class wins by margin 2m+1, and it tolerates m corrupted copies.
- If every class has a positive vote bias μ_c over the encoding group, a random pool fails class c with probability
  ≤ (|S|−1)exp(−kμ_c²/2).
- Certification is cheap enough to rerun on device at load time, so runtime numeric differences are absorbed.

Check: von Neumann's restoring organs, N-version programming, MAKER, self-consistency, randomised smoothing
(Cohen et al. 2019) and certified robustness by voting, permutation or renaming ensembles for LLMs.

**C4. Pinned stochastic execution with a time-uniform bound.** Under the pin, an LLM that samples its tokens is
exactly a finite Markov chain on rows, and its kernel is read off with one forward pass per row. If every row is
within ε TV of the spec and the spec chain mixes (‖P^t − π‖ ≤ Cρ^t), then sup_t TV(model_t, spec_t) ≤
(t̂ + Cρ^{t̂}/(1−ρ))·ε (Mitrophanov 2005). Conjectured converse: for history-keeping decoders no finite set of
per-context checks bounds sup_t TV. Check: Mitrophanov 2005, "LLMs as Markov chains" (Zekri et al. 2024), and
perturbation bounds for Markov chains applied to LLM generation.

**C5. Faults heal iff the program has a synchronising word.** For an executor with independent per-step fault
probability p, the error at step T converges to a limit ≤ p·E[τ_sync] if the transition monoid contains a constant
map. Otherwise it tends to a constant bounded away from 0 (horizon about 1/p). Check: synchronising automata (Černý),
fault-tolerant and self-stabilising automata, error-resilient finite-state machines, Casey and Maass–Orponen (noise
implies definite).

**C6. Tree-parallel certified execution of Dyck and Boolean evaluation via the bicyclic monoid.** A block-diagonal pair
mask runs log₂T rounds of pinned lookups with a certificate of size |M|². Check: parallel bracket matching with the
bicyclic monoid, Mytkowicz 2014 (data-parallel FSMs), and Blelloch scans for parsing.

**C7. Semantically neutral words that restore a learned continuous state.** A small LLM with a rank-4 adapter and a
32-d continuous recurrent carrier learns an identity word in S₅ (for example (s_i s_{i+1})³) whose execution
contracts perturbations around all 120 state centres, while ordinary generators expand them slightly. Periodically
inserting the word makes a continuous group computation certifiable without emitting intermediate states. Check:
pause tokens, PAR, denoising, error-correcting recurrent dynamics, Brandoit 2026, Omlin & Giles.

**C8. One enumeration certifies the model for all programs.** On a frozen executor, one enumeration of the view space
(page size ≤ 512, per-state degree ≤ 8, no gap) certifies the argmax of every row of every program built from those
views, including programs never assembled. Check: weight-level verification of neural programs, compositional
certification, and universal certificates for interpreters.
