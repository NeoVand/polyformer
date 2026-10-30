# L2 prior art: exact arithmetic, length generalisation and state tracking

Literature agent L2 of six, 28 October 2026. Scope: arithmetic length generalisation; how pretrained
language models do arithmetic; error compounding with length; state tracking in transformers, SSMs,
RNNs and LLMs; long-context state-tracking benchmarks; recurrent and looped architectures that claim
exact extrapolation. Read with `research/LITERATURE.md` (85 works, cited below as LIT #n),
`research/NOVELTY.md` and the jewel `refs.bib`. This file adds what they lack and updates what has
changed; it does not re-annotate what LIT already covers.

**Verification.** Every arXiv entry was fetched on 28 Oct 2026 from the arXiv API by id
(`export.arxiv.org/api/query?id_list=…`: title, authors, first-version date, comment, journal_ref,
abstract). Titles were checked against the intended paper; four wrong ids were caught and dropped. The
183 raw records, each with its URL and access date, are in `L2_verified_arxiv.json` beside this file.
Entries marked **[read]** were read in the body (arXiv HTML, or the PDF text for Cai et al. 2017); all
others rest on the abstract. Non-arXiv items name the page fetched. Venues come from the arXiv comment or
journal_ref unless the entry says otherwise. All URLs were accessed on 2026-10-28.

**Closeness.** 3: pre-empts part of a claim and must be engaged in the text. 2: overlaps a claim; cite
it and say how ours differs. 1: relevant context or a baseline. 0: background.

---

## 1. The five most dangerous papers

### 1.1 Cai, Shin & Song 2017: a finite verification set proves correctness at any length (C5, C6, C10)

Jonathon Cai, Richard Shin, Dawn Song. *Making Neural Programming Architectures Generalize via
Recursion.* ICLR 2017. https://arxiv.org/abs/1704.06611 **[read: §3.3, §4.2]**

**What it shows.** A Neural Programmer-Interpreter is trained on recursive execution traces. Each
recursive call runs a fixed number of steps over a bounded observation of the environment, so the set
of step-input sequences that can ever occur is finite. The authors build a verification set that
realises all of them (every base case and every reduction), run the trained model on it, and match the
reference traces. A match proves the model correct on inputs of any size. They do this for grade-school
addition, a bubble-sort variant, topological sort and quicksort; the addition training set holds
problems of at most 3 digits. They argue that the non-recursive model cannot be verified this way:
its core LSTM carries a hidden state across a length-dependent number of calls, so an unbounded number
of examples would be needed.

**Overlap.** This is the logic of the theorem pair behind the pinned clock (Theorem P and
`no_finite_test_suite`). Bound what each tick sees and a finite table of checks suffices at every length;
leave a history-dependent state and no finite check does. Cai et al. prove sufficiency by construction
and assert the impossibility informally. They do not prove necessity, nothing is machine-checked, and the
model is a small trace-supervised NPI rather than a KV-cache policy in a pretrained decoder.

**What to reword.** Do not call the per-row certificate "the first certificate of exactness at any
length." Write instead: "Theorem P turns the bounded-view verification argument of Cai et al. (2017)
into a machine-checked equivalence for a KV-cache policy of a pretrained decoder. The per-row certificate
is sufficient and also necessary; unpinned decoding admits no finite certificate." Cite Cai et al. where
the pin is introduced and again in the Savant section. Price, Zaremba & Sutskever (2016; entry A15) are
the cautionary companion: a Neural GPU near-perfect on 100-digit decimal multiplication still fails on
000…002 × 000…002. Testing does not certify.

**Test it suggests.** (a) Show that Savant's certificate rows are Cai's verification set for the same
program (addition) and report both sizes. (b) Show necessity in practice: corrupt one certified row that
random inputs rarely reach, such as a long carry chain; show that the certificate flags it and that a
4,096-digit run fails exactly when that row fires. (c) Report the cost of certifying against the cost of
testing at 4,096 digits.

### 1.2 Abbe et al. 2024: the inductive scratchpad is the pinned clock without a certificate (C5, C6, C8)

Emmanuel Abbe, Samy Bengio, Aryo Lotfi, Colin Sandon, Omid Saremi. *How Far Can Transformers Reason?
The Globality Barrier and Inductive Scratchpad.* NeurIPS 2024. https://arxiv.org/abs/2406.06467
**[read: the inductive-scratchpad section]**

**What it shows.** Besides the globality barrier for learning, it introduces an "inductive scratchpad."
To generate state s[i+1] the model sees only the question and the last state s[i]. A decoder-only
transformer gets this through attention masking and position-id re-indexing, or by deleting earlier
states, and training uses the same masking, so the model learns only the transition function. Trained
from scratch, parity trained up to 30 bits generalises to about 50–55, and addition trained up to 10
digits reaches 18 (26 with a shifted format). The paper gives no guarantee.

**Overlap.** In everything but name this is the pinned-clock KV-cache policy: the run history is removed
from what each step sees, so the step function is the same at every length. Abbe et al. apply it to
small models trained from scratch, with no certificate, and get about 2–6×. Savant applies it in a
pretrained Qwen3-4B with literal tables in context and a certificate, and is exact at 4,096 digits.

**What to reword.** Present the pin as an instance of the inductive scratchpad, of PENCIL's erasure
(entry K5) and of Markovian thinking (LIT #51). Claim novelty for the certificate theorem and its
necessity direction, for the pretrained setting and language retention, and for the measured
exactness; do not claim it for the KV policy.

**Test it suggests.** Use the same model with Abbe's mask but no certificate and no literal table, and
measure exactness at 1,024–8,192. If the mask alone is exact, the certificate is the guarantee and not
the cause. If it is not, find which ingredient carries the length: the table in context, the pointer, or
certificate-driven repair. Also check whether Abbe's 18-digit ceiling is a pointer failure (C8).

### 1.3 Wang et al. 2026 (PAR): latent recurrence in Qwen2.5-0.5B extrapolates S5 16× with norm anchoring (C4, C2)

Pan Wang, Yihao Hu, Guangyuan Dong, Yitong Lin, Hang Wang, Zimi Liu, Zhihao Wen, Jianshe Li, Jiang-Ming
Yang, Wei Wu, Yongqi Tong. *PAR: Progress-Aligned Recurrence for Length Generalization in State
Tracking.* arXiv, 20 Oct 2026. https://arxiv.org/abs/2610.27628 **[read]**

**What it shows.** Qwen2.5-0.5B is split into a prelude (layers 1–8), a weight-tied core (9–16) looped R
times, and a coda (17–24), following McLeish et al.'s retrofitted recurrence (entry B3). Loop k is trained
to output the state after k operations. After each loop, every token's state is rescaled to the RMS norm
of its first-loop state, with a stop-gradient on the reference ("norm anchoring"). On swap-S5 trained on
at most 32 moves, full-state accuracy is 99.5 ± 1.2% at 256 and 95.5 ± 11.0% at 512. That is 16×, the
largest factor the protocol can measure, against 55.7% for RLT (entry B2) and 0.8% for explicit chain of
thought on the same backbone. Single-query S5 trained on at most 16 steps scores 100, 100 and 99.3% at
32, 64 and 128.

Removing norm anchoring drops extrapolation below 2.2×, and supervising only the final answer caps it at
8×. A label-free variant, prefix self-distillation, uses a teacher that reads the prompt truncated after
k steps. It reaches 85% at 256 on single-query S5, and up to 99.7% at 16× on swap-S5 after a short
positional-stretch fine-tune. The method transfers to Qwen2.5 1.5–7B, where the best seed holds 100% at
256 but the means range from 58 to 81%, and to Qwen3 0.6–4B. There is no certificate, language ability is
not measured, and graph reachability fails.

**Overlap.** It is a latent state machine inside a pretrained LLM that extrapolates far past its training
length after a short fine-tune. It also reports our EXEC_D/LATENT-1 factorial: the per-step state signal
and a fixed norm together carry the length, and either alone fails. Prefix self-distillation is a cousin
of our Nerode pairs, since it uses the states of shorter prefixes as targets.

**What to reword.** C4 cannot claim to be the first latent executor in a pretrained LLM that
extrapolates. It can claim exactness (all-correct runs on every seed at 4,096), the certificate, the size
of the switch (30 steps or one 2,560-number vector) and that language is kept. Cite PAR as concurrent
work that independently replicates "signal plus norm."

**Test it suggests.** Run PAR's recipe (progress-aligned targets with RMS anchoring on a looped
Qwen2.5-0.5B) on our S5 and addition tasks at 1,024–4,096, with our seed count and all-correct-run rates.
Add our kick or certificate to PAR and see whether it closes PAR's ±11-point seed spread. Measure PAR's
language retention with our battery.

### 1.4 Brandoit et al. 2026 (NFSM): iff conditions for length independence; extracted tables certify every length (C3, C2, C5)

Julien Brandoit, Arthur Fyon, Thomas Braipson, Tom Clara, Florent De Geeter, Pierre Sacré, Damien Ernst,
Guillaume Drion. *Length-Independent State Tracking Under a Parallel Scan.* arXiv, 26 Sep 2026.
https://arxiv.org/abs/2609.32447 **[read: first 100k characters]**. Already in `refs.bib`
(`brandoit2026length`).

**What it shows.** Finite precision is modelled as a perturbation of at most η at each step. Tracking is
length-independent (correct at every length at fixed precision) iff three things hold: a decodable code,
a bounded region with restoration, and transitions that map each state's cell into its successor's cell
with margin η (Thms 3.1–3.2). Together these force contraction inside cells and separation between cells
(Thm 3.3). Affine recurrences, which cover SSMs and linear attention, have a single rate, so at finite
precision they realise at most definite automata, and depth does not help (Thm 4.1).

Their Neural Finite-State Machine (NFSM) puts a per-symbol logit table inside a hard argmax that acts as
a "restoring organ," and stays scan-compatible by composing tables. On all five seeds it learns the exact
transition tables of Z2, Z16, S3, S4, A5, M11 and two flip-flop monoids. The extracted tables match the
target, and with a logit-margin condition that certifies tracking at every length. Tracking stays perfect
to about 1M tokens. Affine baselines (Mamba with negative eigenvalues, AUSSM, PD-SSM) fail within a few
hundred steps on non-definite tasks.

**Overlap.** C3's robust Myhill–Nerode theorem (balls inside readout cells, contraction over k-blocks,
absorption of bounded perturbations) states the same realisation conditions. Certifying every length from
a table read off the weights overlaps C5's per-row certificate and C2's exact small trackers. Their
"restoring organ / executive organ" wording is the von Neumann analogy we had planned to claim (LIT #60).

**What to reword.** Present Theorem 2 as a k-block, history-perturbation form of the finite-precision
realisation conditions (Casey 1996 in refs; Brandoit et al. 2026; Bugaud 2026, entry A4). Then say what is
ours: blocks in which single steps may expand, the prefix exception, absorption of perturbations that
depend on the history, the Lean proof, and the theorem's use as a training target in soft trackers and
inside an LLM. Drop "robust Myhill–Nerode" as a headline name, which referee T5 already flagged, or
justify it.

**Test it suggests.** Run NFSM as a baseline on our S5, Lean-rewrite and addition tasks. Apply their table
extraction to our closed trackers and report the margin. Measure their conditions R1–R3, with η, on our
trackers. Compare at 1M tokens.

### 1.5 Bie et al. 2026 (AI-rithmetic): frontier addition fails by misalignment and by independent carry slips (C8; context for C6)

Alex Bie, Travis Dick, Alex Kulesza, Prabhakar Raghavan, Vinod Raman, Sergei Vassilvitskii.
*AI-rithmetic.* arXiv, 11 Feb 2026. https://arxiv.org/abs/2602.10416 **[read]**

**What it shows.** Claude Opus 4.1, GPT-4o, GPT-5, Gemini 2.5 Flash and Pro, and Gemma 3 27B are asked
"What is A + B?" for random d-digit operands, d = 1–100, with 100 prompts per length. Every model loses
accuracy with length except Gemini 2.5 Pro with code execution. Two error classes dominate:

- **Operand misalignment.** The answer matches a sum in which one operand is shifted by up to 10 places.
  It is tied to 3-digit tokenisation: the modal shift is 3 for GPT-4o and Claude.
- **Close-carry slips.** These roughly fit a geometric model of independent failures, (1−p)^n.

Together the two classes explain 87.9% of Claude Opus 4.1's errors, 62.9% of GPT-5's and 92.4% of Gemini
2.5 Pro's. The paper proposes no fix and calls for new designs, data and training.

**Overlap.** C8 says plain decoding fails first by misreading input events (the pointer), then by step
drift. That is their misalignment-plus-independent-carry decomposition, measured on frontier models. The
paper also fixes the frontier baseline for C6's addition headline.

**What to reword.** Say that our plain-decoding failures follow the decomposition of Bie et al. (2026),
then add what they could not measure: a controlled model in which the pointer can be pinned, the length
at which each failure takes over, and the curve from 96% exact at 1,024 events to 0% at 8,192.

**Test it suggests.** Classify our plain-decoding errors with their rules (six or more leading digits
match a sum with an operand shifted by ±10 places; close carry; runaway) so the two analyses are
comparable. Extend their protocol to 1,000–8,000 digits on current frontier models, with and without
thinking, as the Fig. 1 baseline.

### 1.6 The next tier (read before submission)

- **Bugaud 2026a, 2026b (entries A4, A5).** A certificate computed from RNN weights, with no false
  positives at H ≥ 4k, 100% accuracy at L = 1,000,000 (66,667× the training length), and a training recipe
  obtained by inverting the certificate. There is also an iff: certified length generalisation ⇔ a
  forward-invariant positive-margin set, which confines it to languages with an absorbing accept state.
  Both are ICML 2026 workshop posters that touch C3, C5 and C2. Cite them, and test our trackers on a
  non-absorbing language such as mod-k counting, where their recipe fails.
- **Howe 2026 (entry B11).** A pre-registered ablation: deleting the additive input path of a Householder
  linear RNN gives the exact automaton (1.00 at 16× on parity, S4, A5 and S5). Adam, started at a hand-built
  exact solution, regrows the additive path and leaves the exact solution, without harming in-domain fit.
  It touches C1, since the loss moves the model along directions it cannot see in-domain, and C2. Cite it
  as an independent instance of blindness and run the "−b" ablation in our trackers.
- **Yang et al. 2026 and Chen, Ma & Li 2025 (entries A6, A7).** No computable length-generalisation bound
  exists for C-RASP or for transformers, already at depth 2. DFAs have length complexity 2n − 2. This is a
  learning-theory version of "no finite test certifies plain decoding" (C5); cite it as the theoretical
  companion and state the difference (theirs concerns identification from data, ours the verification of
  a given decoder).
- **Lee 2026; Wei 2026a, 2026b; Patriota 2024 (entries A10–A13).** Exactness at 10⁵–10⁶ steps from tiny
  trained models: a hard-projected recurrent model on S3×S3 is exact to 1,048,576 tokens from length 8; a
  neural cellular automaton adds to a million digits from 16; a tiny transformer with a right-to-left loop
  adds to 1,000 digits from two-digit cases. Very long exactness is therefore not new by itself; ours has
  to be distinguished by the model (a pretrained LLM), the certificate and the breadth of tasks.
- **Dai & Fan 2026; Wen et al. 2026 (entries G2, G3).** All 126 models tested have a finite,
  syntax-sensitive counting capacity, with abrupt failure that thinking and tools do not fix. Frontier
  models (GPT-5.5, Gemini 3.1 Pro, Claude Opus 4.7) fail to copy long strings exactly, and the authors
  blame a positional shortcut. Both support C8 (the pointer) and the frontier-failure framing.
- **Lai et al. 2024 (CAEF); Hu et al. 2024, 2025 (RFFT, Meta-RFFT) (entries D1–D3).** Pretrained LLMs
  taught to execute Turing-machine steps or explicit rules: LLaMA-3.1-8B is about 98–99% at 100 digits,
  inside its training range, and a 32B model reaches 95% on 30-digit addition. These are the closest
  "LLM executes an algorithm" baselines for C6; Savant must beat them on length and exactness and keep
  language (which they do not measure).
- **Block et al. 2023; Sharma & Vu 2026 (entries F5, B7).** In the first, SGD noise is benign for the
  one-step loss but catastrophic over long rollouts (behaviour cloning and autoregressive LMs). In the
  second, cross-entropy through an RMSNorm readout cannot see radial scale, so looped LMs grow hidden
  norms in the tens of thousands. Both are instances of C1 that predate our proof; cite them.
- **Lindsey et al. 2025; Nikankin et al. 2024; Gurnee et al. 2026 (entries E1, E2, E10).** "Lookup table"
  features and parallel pathways in Claude 3.5 Haiku's addition; arithmetic as a "bag of heuristics"
  neurons; character counts on place-cell-like manifolds. Our "lookup committee" (C7) needs to be placed
  against these descriptions.
- **Meyerson et al. 2025 (MAKER); Pai & Xian 2026 (entries F3, F19).** A million LLM steps with zero
  errors (Towers of Hanoi, gpt-4.1-mini), with the state carried outside the model and first-to-ahead-by-k
  voting. In the second, gpt-oss-120b carries MD5 state through 196 dependent tool calls. These answer
  "frontier models fail at 1,000–4,096 steps" (C2, C8) by externalising the state, so the paper must say
  that our claim concerns state held by the model.

---

## 2. Annotated list

Format: citation, URL, tag, then 2–3 sentences, then closeness (claim) and what it means for us. LIT #n
marks works already in `LITERATURE.md`; for those, only the update is given.

### A. Certified and provable length generalisation; exactness at extreme lengths

**A1. Cai, Shin & Song 2017.** See §1.1. https://arxiv.org/abs/1704.06611 [read]. **3 (C5, C6, C10).**

**A2. Abbe, Bengio, Lotfi, Sandon & Saremi 2024. How Far Can Transformers Reason? The Globality Barrier
and Inductive Scratchpad.** NeurIPS 2024. https://arxiv.org/abs/2406.06467 [read]. See §1.2.
**3 (C5, C6).**

**A3. Brandoit et al. 2026. Length-Independent State Tracking Under a Parallel Scan.** arXiv.
https://arxiv.org/abs/2609.32447 [read]. See §1.4. **3 (C3, C2, C5).**

**A4. Bugaud 2026a. Combining Theory and Benchmarks for Length Generalisation: Formal Certificates Meet
Large-Scale Evaluation.** ICML 2026 workshop poster ("Combining Theory and Benchmarks").
Page: https://icml.cc/virtual/2026/68270; OpenReview https://openreview.net/forum?id=shPakbYAoQ (blocked
by a bot check; abstract read on icml.cc). From switched-systems analysis, a gap-suppression mechanism
and a margin condition certify RNN length generalisation from the weights alone. The certificate has no
false positives at H ≥ 4k (100/100 models), and certified models are 100% accurate at L = 1,000,000 on 10
seeds. Inverting the certificate gives a training recipe that succeeds ≥99/100 for k = 3–10 and 12, and
349 of 350 absorbing-state regex patterns are certified. It fails on non-absorbing DFAs (0% against
80–100% for the baseline) and on GRU/LSTM. **3 (C3, C5, C2).** It is the closest "certificate → recipe"
precedent for v1's certified exactness. Ours must handle non-absorbing automata (S5, counters), which
their theory excludes, so state this as a difference and show it.

**A5. Bugaud 2026b. Which Regular Languages Admit Provably Correct RNN Implementations? A
Lattice-Theoretic Characterisation via Forward-Invariant Sets.** ICML 2026 workshop poster ("AI for
Math"). Page: https://icml.cc/virtual/2026/82548; OpenReview https://openreview.net/forum?id=L4kh17ZuSa
(not readable). For Elman RNNs as switched systems, a forward-invariant certificate of length
generalisation exists iff there is a forward-invariant positive-margin set. Such languages fall inside
the class whose minimal DFA has an absorbing accept state; modular counting, last-k and alternating
patterns are excluded. The checks use Kleene iteration over boxes and LMIs. **3 (C3).** It is an iff
theorem of the same type as robust Myhill–Nerode; cite it, and explain why our theorem allows
non-absorbing automata: through k-block contraction, multiple balls per class, or a different readout.

**A6. Chen, Ma & Li 2025. Non-Asymptotic Length Generalization.** arXiv; listed as an ICML 2025 poster
(icml.cc listing seen in search, not fetched). https://arxiv.org/abs/2506.03085. A computable bound on
the training length that guarantees length generalisation exists iff language equivalence is decidable.
For n-state DFAs the bound is 2n − 2, under the minimum-complexity interpolator; context-free grammars
have no computable bound. **2 (C5, C3).** It gives a finite-test guarantee for an idealised learner on
DFAs. Contrast it with our claim that no finite test certifies a given unpinned decoder.

**A7. Yang, Bergsträßer, Zetzsche, Chiang & Lin 2026. Length Generalization Bounds for Transformers.**
arXiv. https://arxiv.org/abs/2603.02238 [read]. Two-layer C-RASP has undecidable emptiness, so no
computable length-generalisation bound exists for C-RASP or for (1, log n)-precision transformers.
Fixed-precision transformers (positive C-RASP) have bounds exponential in size, and the bounds are tight.
The paper does not address verifying a trained model. **3 (C5).** It is the published theoretical
cousin of `no_finite_test_suite`; cite it, and state that ours is about certifying a given decoder rather
than learning.

**A8. Ahuja & Mansouri 2024. On Provable Length and Compositional Generalization.** arXiv.
https://arxiv.org/abs/2402.04875. Limited-capacity deep sets, transformers, SSMs and RNNs trained to
minimise prediction error provably length-generalise when the training distribution is diverse enough,
and chain-of-thought supervision extends this to larger models. **1 (C1, C3).** These are sufficient
conditions from realisability and capacity limits; our blindness theorem says what happens without them.

**A9. Huang et al. 2024. A Formal Framework for Understanding Length Generalization in Transformers.**
ICLR 2025. https://arxiv.org/abs/2410.02140. Characterises functions identifiable in the limit from long
enough inputs by causal transformers with absolute positions under a norm-regularised idealised
learner, and predicts empirical success and failure. **1 (C5).** Idealised learning, not verification.

**A10. Lee 2026. A Held-Out Transition-Pair Falsifier for Long-Horizon Non-Abelian State Tracking.**
arXiv. https://arxiv.org/abs/2606.07254 [read]. Training forbids selected ordered generator pairs and
evaluation requires them. A "projected" recurrent model (hard argmin to the nearest group element at
readout) trained on length-8 S3×S3 sequences is error-free (250/250 per horizon over five seeds) up to
1,048,576 tokens, while GRU, SSM and bag baselines stay near chance. The carrier is undisclosed and there
is no all-length proof. **2 (C2).** It is a stronger extrapolation factor than ours on an easier group.
Borrow its held-out-pair split as a memorisation control for our trackers.

**A11. Wei 2026a. On the Spatiotemporal Dynamics of Generalization in Neural Networks (SEAD).** arXiv.
https://arxiv.org/abs/2602.01651 (already `wei2026sead`) [read v1]. A neural cellular automaton (local
convolutional rule, argmax projection, iterated to a fixed point) trained by single-step supervision
reports 100% on parity and addition from L = 16 to L = 1,000,000, and on Rule 110. There is no proof, the
addition layout is unspecified, and the longest lengths rest on 1–10 samples. **2 (C2, C6).** It is the
current record claim for exact addition length; we cannot say "longest exact addition", only "longest
inside a pretrained LLM".

**A12. Wei 2026b. On the Mirage of Long-Range Dependency, with an Application to Integer
Multiplication.** arXiv. https://arxiv.org/abs/2603.29069. On a 2D outer-product layout, each step of
binary long multiplication is a 3×3 local rule. A 321-parameter cellular automaton then generalises
perfectly to 683× the training range, while transformer and Mamba baselines fail on the same layout.
**1 (C6, C10).** Our planned multiplication programs should cite this as a strong layout-based
baseline.

**A13. Patriota 2024. Arbitrary-Length Generalization for Addition in a Tiny Transformer.** arXiv.
https://arxiv.org/abs/2406.00075 [read]. A small transformer trained only on single- and two-digit cases
with a carry prefix is run right to left. Each step sees the previous output and the next aligned digit
pair, and the carry is fed back as text. It reports 100% on every test up to 1,000 digits, with some runs
to about 300,000, and no proof. **2 (C5, C6).** An externally pinned, Markov decoding loop with a
finite case table makes exact long addition easy. A reviewer will ask what the pin adds beyond this; the
answer is a pretrained LLM, programs given as tables, the certificate, and language kept.

**A14. Kaiser & Sutskever 2016 (LIT #17), update.** https://arxiv.org/abs/1511.08228. The abstract says
binary addition and multiplication trained to 20 bits showed "no errors whatsoever" on much longer
numbers. **2 (C2, C6).**

**A15. Price, Zaremba & Sutskever 2016. Extensions and Limitations of the Neural GPU.** arXiv.
https://arxiv.org/abs/1611.00736. With a curriculum and larger models, the Neural GPU learns all
arithmetic operations in decimal and generalises to arbitrarily long numbers. Yet a model near-perfect on
100-digit decimal multiplication fails on highly symmetric inputs such as 000…002 × 000…002. **2 (C5).**
It is the classic example that random testing at length does not certify; use it to motivate the
certificate.

**A16. Freivalds & Liepins 2017. Improving the Neural GPU Architecture for Algorithm Learning.** NAMPI
workshop. https://arxiv.org/abs/1702.08727. Diagonal gates and saturating hard nonlinearities; the first
architecture to learn decimal multiplication end to end. **1 (C6).**

**A17. Yan, Swersky, Koutra, Ranganathan & Hashemi 2020. Neural Execution Engines: Learning to Execute
Subroutines.** NeurIPS 2020. https://arxiv.org/abs/2006.08084. Transformers executing subroutines lose
attention fidelity as lists grow; learned conditional masking gives near-perfect strong generalisation,
and binary number encodings help arithmetic. **1 (C8, C5).** An early "masking fixes the pointer"
result.

**A18. Wang, Zhang, Liu & Giles 2018. Verification of Recurrent Neural Networks Through Rule
Extraction.** arXiv. https://arxiv.org/abs/1811.06029. Uses DFAs as oracles to verify RNNs against
adversarial strings. **0 (C5).** Background on verifying RNNs through automata.

### B. Recurrent, looped and length-robust architectures

**B1. Wang et al. 2026 (PAR).** See §1.3. https://arxiv.org/abs/2610.27628 [read]. **3 (C4, C2).**

**B2. Zhang, Feng, Qin, Kung & Wang 2026. Recurrent Looped Transformer.** arXiv.
https://arxiv.org/abs/2610.07591. A parallel causal encoder plus a recurrent decoder that feeds each
token's final decoder state to the next token. Parity trained on 40 bits generalises to 256 at 100%;
swap-S5 is 97% at 8× against under 1% for a transformer; removing the feedback drops both to chance.
**2 (C2, C4).** Per-token recurrence across positions is our tracker's shape. Use it as a baseline.

**B3. McLeish et al. 2025. Teaching Pretrained Language Models to Think Deeper with Retrofitted
Recurrence.** arXiv (a NeurIPS 2025 listing appeared in search; not fetched).
https://arxiv.org/abs/2511.07384. Converts pretrained non-recurrent LMs (TinyLlama, OLMo, Llama) into
depth-recurrent ones through a curriculum of recurrences; this beats plain post-training on maths at
equal compute. **2 (C4).** PAR builds on it. It is evidence that recurrence can be retrofitted into
pretrained weights.

**B4. Zhu et al. 2025. Scaling Latent Reasoning via Looped Language Models (Ouro).** arXiv.
https://arxiv.org/abs/2510.25741. Looped LMs pretrained on 7.7T tokens with learned depth allocation;
1.4B and 2.6B models match up to 12B baselines. **1 (C4).**

**B5. Zhang, Hu, Peng & Xie 2026. When Does Recurrence Become an Algorithm? Convergence Selection in
Weight-Tied Looped Transformers.** arXiv. https://arxiv.org/abs/2607.20594. On group word problems,
training installs a "computation frontier" whose speed is priced by the training contract,
v ≈ n_train/T_train. Weight tying selects a serial algorithm over a parallel scan. A5 generalises fully,
while S5's 120×120 operator deadlocks learning until an operator-first curriculum dissolves the wall.
Standard metrics saturate at the fixed points trained loops reach. **2 (C2).** A rival account of when
extrapolation appears; S5's operator wall is directly relevant to our S5 results.

**B6. Kuo, Chayti, Reizinger, Brendel & Jaggi 2026. Stabilizing Extrapolation in Looped Transformers via
Learned Stochastic Stopping.** NeurIPS 2026. https://arxiv.org/abs/2606.29983. Out-of-distribution
variance of looped transformers comes from the training correlation between length and loop count;
random or learned stopping reduces it on binary addition, Dyck-1 and copy. **1 (C2).**

**B7. Sharma & Vu 2026. Dense Supervision Is Not Enough: The Readout Blind Spot in Looped Language
Models.** arXiv. https://arxiv.org/abs/2606.24898 [read]. Through a scale-invariant readout
(RMSNorm/LayerNorm), cross-entropy has zero radial gradient, ⟨∇_H L, H⟩ = 0, while pre-norm residual
recurrence keeps updating scale. Final-loop norms in 44M and 129M looped LMs reach about 39,000 and
56,000. Scale-visible readouts or a norm penalty fix it; the paper studies depth, not length. **2 (C1,
C4).** It is a concrete, published instance of a loss blind to a state direction, and it explains why
norm anchoring (PAR) and our fixed-norm slot matter. Cite it in the blindness section.

**B8. Ibrahimli, Lee & Wermter 2026. Adaptive Recurrence as Algorithmic Time for Length Generalization
in Addition.** ICML 2026 workshop poster (Compositional Learning). Page:
https://icml.cc/virtual/2026/69322 (no arXiv found). Small looped transformers with adaptive halting
extrapolate decimal addition without positional information, and later answer positions resolve at
later recurrent phases. The page gives no numbers. **1 (C2).**

**B9. Fan, Du, Ramchandran & Lee 2024. Looped Transformers for Length Generalization.** ICLR 2025.
https://arxiv.org/abs/2409.15647. Looped transformers with adaptive step counts learn length-generalising
solutions to tasks with iterative RASP-L solutions. **1 (C2).**

**B10. Bansal et al. 2022; Schwarzschild et al. 2021.** End-to-end Algorithm Synthesis with Recurrent
Networks: Logical Extrapolation Without Overthinking (https://arxiv.org/abs/2202.05826) and Can You Learn
an Algorithm? Generalizing from Easy to Hard Problems with Recurrent Networks
(https://arxiv.org/abs/2106.04537). Recurrent networks run longer at test time to solve bigger problems;
"overthinking" degenerates over many iterations and a recall architecture fixes it. **1 (C2).** An
early account of drift over many iterations.

**B11. Howe 2026. The Automaton Underneath: The Additive Input Pathway Is a Parasitic Attractor for State
Tracking in Householder Linear RNN.** arXiv. https://arxiv.org/abs/2609.18966 [read].

- **Main result.** In one Householder-product linear RNN layer (d = 112), deleting the additive input
  b_t = W_b e_t turns shortcut solutions into the exact automaton: median 1.00 at position 512 (16× the
  training length) on parity, S4, A5 and S5, at the minimal number of factors set by a stated
  representation law. With b_t, S5 scores 0.20 at 512.
- **The loss moves an exact model off its solution.** Started at a hand-built exact solution, Adam grows
  W_b and pulls the model off it: position-512 accuracy falls to 0.50 on parity and 0.23 on S5.
- **The exact automaton is concealed, not missing.** Zeroing W_b at inference restores exactness in 18 of
  20 seeds.
- **Protocol.** All 202 runs were pre-registered in the author's own repository; mod-3 still drifts.

**2–3 (C1, C2).** It shows the training loss moving an exact solution along a direction that is harmless
in-domain and fatal at length, which is the phenomenon C1 explains. Cite it and run the ablation.

**B12. Chung, Choi & Kim 2026. Rethinking State Tracking in Recurrent Models Through Error Control
Dynamics.** NeurIPS 2026. https://arxiv.org/abs/2605.07755 (already `chung2026error`) [read]. An exact
affine tracker must act as the identity on the subspace that separates states, so it cannot contract
errors along it (Thm 1). A distinguishability ratio q(t) predicts the failure horizon (r = 0.87). tanh
and state-gated RNNs reach 1,000, the longest length tested, while Mamba, Mamba-3 and the linear RNNs
fail early. No training fix is proposed and the loss is not analysed. **2 (C1, C2, C3).** It covers the
"affine cannot correct drift" half of our closure argument; cite it there and do not re-derive it as new.

**B13. Ebrahimi & Memisevic 2025. Revisiting Bi-Linear State Transitions in Recurrent Neural Networks.**
NeurIPS 2025 (proceedings listing seen in search). https://arxiv.org/abs/2505.21749. Bilinear state
transitions without additive terms learn parity even with a frozen recurrence, and form a hierarchy for
state tracking with Mamba at the bottom. **1 (C2).** Agrees with Howe on removing additive terms.

**B14. Mishra, Tan, Stoica, Gonzalez & Dao 2026. M²RNN: Non-Linear RNNs with Matrix-Valued States for
Scalable Language Modeling.** arXiv. https://arxiv.org/abs/2603.14360. Non-linear matrix-state RNN
layers report "perfect state tracking generalization" at unseen lengths and improve hybrids at 7B MoE
scale. **1 (C2, C4).** A non-linear recurrent layer inside an LM at scale; the lengths were not read.

**B15. Karuvally et al. 2025. Bridging Expressivity and Scalability with Adaptive Unitary SSMs (AUSSM).**
arXiv (a NeurIPS 2025 listing appeared in search). https://arxiv.org/abs/2507.05238. Skew-symmetric,
input-dependent unitary recurrence performs modulo counting and simulates solvable-group automata at
precision logarithmic in length. **1 (C2).** Brandoit and Chung use it as a baseline that fails at
length.

**B16. Lahoti et al. 2026. Mamba-3: Improved Sequence Modeling using State Space Principles.** ICLR 2026.
https://arxiv.org/abs/2603.15569. Complex-valued (rotational) transitions add state tracking such as
parity; in Chung et al. Mamba-3's longest passing length is 200–300 on parity, 100 on C6 and 60 on S3.
**1 (C2).**

**B17. Shakerinava, Khavari, Ravanbakhsh & Chandar 2026. The Expressive Limits of Diagonal SSMs for
State-Tracking.** ICLR 2026. https://arxiv.org/abs/2603.01959. A single-layer complex diagonal SSM
tracks no non-Abelian group at finite precision; k layers track a group iff it has a subnormal series of
length k with Abelian factors; multi-layer models often fail to learn it. **1 (C2).**

**B18. Movahedi et al. 2025, Fixed-Point RNNs; Schöne et al. 2025, Implicit Language Models are RNNs.**
https://arxiv.org/abs/2503.10799 (NeurIPS 2025 spotlight) and https://arxiv.org/abs/2502.07827.
Iterating a diagonal recurrence to a fixed point recovers dense or non-linear transitions and state
tracking (A5, S5). **1 (C2).**

**B19. Siems et al. 2026. Learning State-Tracking from Code Using Linear RNNs.** arXiv.
https://arxiv.org/abs/2602.14814. Permutation composition is recast as REPL traces with sparse state
reveals. Linear RNNs with extended eigenvalues track it and transformers fail; when actions are not
fully observed, linear RNNs can be worse than non-linear ones. **1 (C2, C9).** A code-format tracking
benchmark close to our code-execution domain.

**B20. Yang et al. 2025. PaTH Attention: Position Encoding via Accumulating Householder
Transformations.** NeurIPS 2025. https://arxiv.org/abs/2505.16381. Data-dependent Householder position
encodings give transformers state tracking. **1 (C8).** A pointer and state fix inside attention.

**B21. Peng et al. 2025, RWKV-7 "Goose"; Beck et al. 2024, xLSTM.** https://arxiv.org/abs/2503.14456 and
https://arxiv.org/abs/2405.04517. Recurrent LMs that claim state tracking and the recognition of all
regular languages (RWKV-7) or of parity (sLSTM). **1 (C2).**

**B22. Jiang 2026. Learning Length-Extrapolatable Recurrent Models (CST).** arXiv.
https://arxiv.org/abs/2609.09157. Rescales the backward "state credit" to stabilise its norm, which
improves extrapolation up to 128× on synthetic tasks and on LM. **1 (C1).** A gradient-side fix,
complementary to blindness.

**B23. Yau et al. 2025. Sequential-Parallel Duality in Prefix Scannable Models.** arXiv.
https://arxiv.org/abs/2506.10918. Prefix-scannable models with non-associative aggregators; some
length-generalise better than SSMs or transformers. **0.**

**B24. Csordás, Irie & Schmidhuber 2021. The Neural Data Router.** ICLR 2022.
https://arxiv.org/abs/2110.07732. Copy gates and geometric attention give 100% length generalisation on
compositional table lookup. **2 (C4, C6).** "Execute a lookup table in a transformer at length" is old in
from-scratch models; cite it with the table-executor claim.

**B25. Reed & de Freitas 2015. Neural Programmer-Interpreters.** ICLR 2016.
https://arxiv.org/abs/1511.06279. The NPI that Cai et al. made recursive. **1 (C10).**

**B26. Geiping et al. 2025 (Huginn; LIT #54), update; Lu et al. 2025, Latent Chain-of-Thought? Decoding
the Depth-Recurrent Transformer.** https://arxiv.org/abs/2507.02199. Probing Huginn-3.5B on arithmetic
finds little interpretable latent chain of thought, and more recurrence helps GSM8K only marginally.
**1 (C4).** A large depth-recurrent model does not by itself give exact latent execution.

**B27. Ebrahimi, Defferrard, Panchal & Memisevic 2026. On the "Induction Bias" in Sequence Models.**
ICML 2026. https://arxiv.org/abs/2602.18333 (in NOVELTY). In distribution, transformers need far more
data than RNNs for state tracking and learn length-specific solutions without sharing across lengths.
**1 (C1, C2).**

**Known architectural entries (LIT #4–7, #10), update.** Grazzi 2025, DeltaProduct, PD-SSM, Sarrof 2024
and Buitrago Ruiz & Gu 2025 are now standard baselines. Brandoit (Mamba with negative eigenvalues,
AUSSM, PD-SSM) and Chung report them failing within a few hundred steps on non-definite tasks. Howe
reports that DeltaProduct-class models are exact once the additive input path is removed. Our E4 should
quote these numbers.

### C. Arithmetic length generalisation in transformers trained from scratch

**C1. McLeish et al. 2024 (Abacus; LIT #11), update.** https://arxiv.org/abs/2405.17399. Abstract: up to
99% on 100-digit addition from 20-digit training; the authors locate the failure in "keep track of the
exact position of each digit". **2 (C8, C6).** It is the pointer diagnosis, in their own words.

**C2. Cho et al. 2024 (Position Coupling; LIT #12).** https://arxiv.org/abs/2405.20671. NeurIPS 2024;
from 30 to 200 digits. **2 (C8).**

**C3. Cho, Cha, Bhojanapalli & Yun 2025. Arithmetic Transformers Can Length-Generalize in Both Operand
Length and Count.** ICLR 2025. https://arxiv.org/abs/2410.15787. Task-specific scratchpads that attend
to a fixed number of tokens per step, plus multi-level position coupling, give about 2–3× generalisation
for multi-operand addition and for multiplication. **2 (C5, C8).** "A fixed number of tokens per step"
is a pin in data format.

**C4. Zhou et al. 2024 (LIT #13); Zhou et al. 2023 RASP-L (LIT #14); Lee et al. 2023 (LIT #15); Lee et al.
2025 self-improving (LIT #16); Kazemnejad et al. 2023 (LIT #9).** No change. Lee 2025's abstract
reports 10- to 100-digit addition "without apparent saturation".

**C5. Jelassi et al. 2023. Length Generalization in Arithmetic Transformers.** arXiv.
https://arxiv.org/abs/2306.15400. Relative position embeddings take addition from 5 to 15 digits but
fail for multiplication. Priming with 10–50 long examples reaches 35×3 multiplication. **1 (C6).**

**C6. Shen et al. 2023. Positional Description Matters for Transformers Arithmetic.** arXiv.
https://arxiv.org/abs/2311.14737. Modified positional encoding gives direct 15-digit multiplication and
10-to-12-digit addition extrapolation. **1.**

**C7. Duan, Shi & Xu 2023. From Interpolation to Extrapolation: Complete Length Generalization for
Arithmetic Transformers.** arXiv. https://arxiv.org/abs/2310.11984. Attention Bias Calibration
reports near-perfect length generalisation on some arithmetic tasks and parity. **1 (C2).**

**C8. Ruoss et al. 2023. Randomized Positional Encodings Boost Length Generalization of Transformers.**
ACL 2023 (venue not on the arXiv record). https://arxiv.org/abs/2305.16843. Out-of-distribution positions
cause failure; random position subsets fix part of it. **1 (C8).**

**C9. Sabbaghi, Pappas, Hassani & Goel 2024. Explicitly Encoding Structural Symmetry is Key to Length
Generalization in Arithmetic Tasks.** arXiv. https://arxiv.org/abs/2406.01895. Custom formats and
positional encodings take addition and multiplication from 5 to 50 digits. **1 (C6).**

**C10. Cai, Lee, Schwarzschild et al. 2025. Extrapolation by Association: Length Generalization Transfer
in Transformers.** arXiv. https://arxiv.org/abs/2506.09251. Length generalisation transfers from a
related, longer auxiliary task, including in pretrained models. **1 (C4).**

**C11. Golowich et al. 2025. The Role of Sparsity for Length Generalization in Transformers.** arXiv.
https://arxiv.org/abs/2502.16792. Length generalisation follows sparse token dependence; Predictive
Position Coupling learns the coupling ids. **1 (C8).**

**C12. Back de Luca et al. 2024. Positional Attention.** ICML 2025.
https://arxiv.org/abs/2410.01686. **0.**

**C13. Shaw, Cohan, Eisenstein & Lee 2024. ALTA: Compiler-Based Analysis of Transformers.** TMLR 2025.
https://arxiv.org/abs/2410.18077. Compiles programs with loops into (universal) transformer weights,
shows length-invariant parity and addition constructions, and trains from execution traces. **1 (C10,
C1).** It separates expressibility from learnability, our framing too.

**C14. Hou et al. 2024 (Turing Programs; LIT #72).** No change. **1 (C5).**

**C15. Deng, Choi & Shieber 2024 (ICoT; LIT #53), update.** https://arxiv.org/abs/2405.14838. GPT-2
Small reaches 9×9 multiplication at up to 99% by internalising chain of thought, where standard training
stops at 4×4. **1 (C6).**

**C16. Bai et al. 2025. Why Can't Transformers Learn Multiplication? Reverse-Engineering Reveals
Long-Range Dependency Pitfalls.** arXiv. https://arxiv.org/abs/2510.00184. A model trained with implicit
chain of thought caches pairwise partial products through an attention DAG over Fourier digit codes,
while standard fine-tuning converges to a local optimum without those dependencies. An auxiliary
"running sum" probe loss fixes it. **1 (C1, C6).** An auxiliary intermediate-state loss as the remedy
is the kind of signal our kick provides.

**C17. Shintani 2026. Arithmetic OOD Failure Unfolds in Stages in Minimal GPTs.** arXiv.
https://arxiv.org/abs/2603.26828. Out-of-distribution failure of a GPT trained on 2-digit addition
decomposes into stages: a layout barrier, carry semantics, recomposition and a tens residual. **1 (C8).**
A staged failure account like ours, at toy scale.

**C18. Quirke & Barez 2023 (ICLR 2024), https://arxiv.org/abs/2310.13121; Quirke, Neo & Barez 2024,
https://arxiv.org/abs/2402.02619; Kruthoff 2024, https://arxiv.org/abs/2401.07993.** Mechanisms of
addition and carry in small transformers: per-digit parallel streams, and a shared circuit skeleton
across 46 models. **0 (C7).**

### D. Arithmetic in pretrained LLMs: fine-tuning, formats and calculators

**D1. Lai et al. 2024. Executing Arithmetic: Fine-Tuning Large Language Models as Turing Machines
(CAEF).** arXiv. https://arxiv.org/abs/2410.07896 [read]. LLaMA-3.1-8B with one LoRA adapter per
operator learns Turing-machine steps (state and command in, next state and command out), with aligners
in and out and reversed operands. It scores about 98–99% at 5–100 digits (addition 98.6% at 100) and
99.3% on 1–10-digit multiplication and division. Test lengths lie inside the training range; GPT-4o gets
43% on 100-digit addition. Language ability is not measured. **3 (C6).** It is the closest "pretrained
LLM executes a state machine for arithmetic" baseline. Savant differs by length (4,096+), exactness,
certificate, a single model with tables in context, and language kept; say so.

**D2. Hu, Tang, Yang & Zhang 2024. Case-Based or Rule-Based: How Do Transformers Do the Math?** arXiv
(listed at ICML 2024 per search; not fetched). https://arxiv.org/abs/2402.17709. Transformers lean on
case-based reasoning. Rule-Following Fine-Tuning, which recites and applies explicit rules step by step,
takes 1–5-digit training to over 95% at 12 digits. **2 (C6).** "Give the model the rule and train it to
apply it" is RFFT; Savant's literal tables are a sharper form.

**D3. Hu, Kang, Yang, Xu & Zhang 2025. Beyond Single-Task: Robust Multi-Task Length Generalization for
LLMs (Meta-RFFT).** arXiv. https://arxiv.org/abs/2502.11525. After RF-pretraining on 86 tasks, a 32B
model fine-tuned on 1–5-digit addition reaches 95% at 30 digits, against 72% for DeepSeek-R1-671B. **2
(C6, C10).** The multi-task rule-following baseline for a general executor.

**D4. Zhou H. et al. 2022. Teaching Algorithmic Reasoning via In-context Learning.** arXiv.
https://arxiv.org/abs/2211.09066. Algorithmic prompting cuts errors on long parity, addition,
multiplication and subtraction by about 10×, 9×, 5× and 2×. **1 (C6).** The prompting-only baseline.

**D5. Dietz & Klakow 2025. IGC: Integrating a Gated Calculator into an LLM.** arXiv.
https://arxiv.org/abs/2501.00684. A module reads operands from a frozen Llama's hidden states, computes
exactly on the GPU and writes back through gates. It reaches 98–99% on BigBench Arithmetic in one pass.
**2 (C4).** A calculator bolted into the forward pass; our executor is learned and table-driven.
Distinguish them.

**D6. Dugan et al. 2024. OccamLLM: Fast and Exact Language Model Arithmetic in a Single Step.** arXiv (a
NeurIPS 2024 proceedings listing appeared in search). https://arxiv.org/abs/2406.06576. LLM hidden
states steer a symbolic OccamNet; it is 100% on single operations with Llama 3 8B. **1 (C4).**

**D7. Number encodings.** FoNE (Zhou et al. 2025, https://arxiv.org/abs/2502.09741), BitTokens
(Kreitner et al. 2025, https://arxiv.org/abs/2510.06824), xVal (Golkar et al. 2023,
https://arxiv.org/abs/2310.02989), NumeroLogic (Schwartz et al. 2024,
https://arxiv.org/abs/2404.00459), and *Tokenization counts* (Singh & Strouse 2024,
https://arxiv.org/abs/2402.14903), where right-to-left tokenisation fixes many GPT-3.5/4 errors that
follow stereotyped patterns. **1 (C8).** Tokenisation drives the misalignment errors of §1.5.

### E. How pretrained LLMs compute arithmetic and counts internally

**E1. Lindsey et al. 2025. On the Biology of a Large Language Model.** Transformer Circuits Thread,
27 Mar 2025. https://transformer-circuits.pub/2025/attribution-graphs/biology.html [read: addition
section]. Claude 3.5 Haiku adds 36 + 59 through parallel pathways: a low-precision magnitude path and an
exact ones-digit path. "Lookup table" features map input properties to output properties (operands
ending in 6 and 9 give a sum ending in 5), and the model's own explanation (carry the 1) does not match
the computation. **2 (C7).** Our "lookup committee" must be set against these lookup-table features and
parallel paths.

**E2. Nikankin, Reusch, Mueller & Belinkov 2024. Arithmetic Without Algorithms: Language Models Solve
Math With a Bag of Heuristics.** arXiv. https://arxiv.org/abs/2410.21272. A sparse set of MLP neurons
each fire on a numeric input pattern and promote answers; their union explains most arithmetic accuracy.
**2 (C7).** "Committee of heuristic neurons" is close to "lookup committee"; run their neuron-type
classifier on Savant's tick neurons.

**E3. Zhou T., Fu, Sharan & Jia 2024. Pre-trained Large Language Models Use Fourier Features to Compute
Addition.** arXiv. https://arxiv.org/abs/2406.03445. MLPs compute magnitude with low-frequency features
and attention computes modular parts with high-frequency ones; pretraining is necessary. **1 (C7).**

**E4. Kantamneni & Tegmark 2025. Language Models Use Trigonometry to Do Addition.** arXiv.
https://arxiv.org/abs/2502.00873. Numbers lie on a generalised helix, and addition uses a "Clock"
algorithm in three mid-sized LLMs. **1 (C7).**

**E5. Levy & Geva 2024. Language Models Encode Numbers Using Digit Representations in Base 10.** NAACL
2025. https://arxiv.org/abs/2410.11781. Per-digit circular representations explain digit-wise error
patterns. **1 (C7, C8).**

**E6. Baeumel et al. 2025. Modular Arithmetic: Language Models Solve Math Digit by Digit.** arXiv.
https://arxiv.org/abs/2508.02513. Digit-position-specific MLP circuits are causally validated. **1
(C7).**

**E7. Naganna, Sijan & Kalita 2026. Are Arithmetic Heuristic Neurons Form-Invariant?** arXiv.
https://arxiv.org/abs/2607.16693. A compact set of heuristic neurons is shared across symbols, word
problems and code in Llama-3, and is necessary and sufficient. Transferring their activations repairs
over 97% of cross-format addition and subtraction failures. **1 (C7).**

**E8. Stolfo, Belinkov & Sachan 2023 (EMNLP), https://arxiv.org/abs/2305.15054; Zhang W. et al. 2024
(ICML 2024 oral), https://arxiv.org/abs/2409.01659.** Attention moves operands to the last token and
MLPs compute; fewer than 5% of heads matter, and tuning them helps. **0 (C7).**

**E9. Gurnee et al. 2026. When Models Manipulate Manifolds: The Geometry of a Counting Task.** arXiv.
https://arxiv.org/abs/2601.04480. Claude 3.5 Haiku represents character counts on low-dimensional curved
manifolds tiled by sparse, place-cell-like feature families, and adversarial "illusions" hijack the
counter. **2 (C7, C8).** Discretised "cells" on a counting manifold relate to our robust cells; the
illusions are pointer-type failures.

**E10. Nanda et al. 2023. Progress Measures for Grokking via Mechanistic Interpretability.** ICLR 2023
(not on the arXiv record). https://arxiv.org/abs/2301.05217. Fourier "clock" modular addition. **0.**

### F. Error compounding with length

**F1. Dziri et al. 2023 (LIT #76).** No change.

**F2. Sinha, Arun, Goel, Staab & Geiping 2025. The Illusion of Diminishing Returns: Measuring Long
Horizon Execution in LLMs.** ICLR 2026. https://arxiv.org/abs/2509.09677 (already `sinha2025horizon`)
[read]. With plan and knowledge supplied (a running sum over looked-up values), small gains in per-step
accuracy compound into large horizon gains. Models also self-condition on their own past errors, which
scale does not fix but thinking does. Single-turn horizon at 80% accuracy: GPT-5 thinking about 2,176
steps, Claude-4 Sonnet 432, Grok 4 384, Gemini 2.5 Pro 120; non-thinking models fail beyond about six
steps. **2 (C8, C2).** The quantitative frontier number our "1,000–4,096 steps" claim must quote.

**F3. Meyerson et al. 2025. Solving a Million-Step LLM Task with Zero Errors (MAKER).** arXiv.
https://arxiv.org/abs/2511.09030 [read]. Towers of Hanoi with 20 disks (2²⁰ − 1 steps) is solved with
zero errors by gpt-4.1-mini microagents, at a per-step error of about 0.22%. It uses first-to-ahead-by-3
voting and red-flagging, with cost Θ(s ln s), and the state is passed outside the model in every prompt.
**2 (C8, C9, C5).** Externalised state plus error correction beats any single model's horizon; we must
say our exactness is of model-held state, and note that the pin is a minimal form of their
decomposition.

**F4. Shojaee et al. 2025. The Illusion of Thinking.** NeurIPS 2025. https://arxiv.org/abs/2506.06941.
Reasoning models collapse completely beyond a complexity threshold on puzzles. **Lawsen 2025. Comment
on The Illusion of Thinking.** https://arxiv.org/abs/2506.09250. Part of the collapse is output-token
limits and unsolvable instances. **1 (C8).** The comment is a warning: our frontier failure curves must
rule out output limits.

**F5. Block, Foster, Krishnamurthy, Simchowitz & Zhang 2023. Butterfly Effects of SGD Noise: Error
Amplification in Behavior Cloning and Autoregression.** arXiv. https://arxiv.org/abs/2310.11428.
Minibatch noise barely changes the one-step loss but causes sharp oscillations in long-horizon reward
("gradient variance amplification") in control and autoregressive LMs; an exponential moving average of
the iterates mitigates it. **2 (C1).** An empirical precursor of "the one-step loss cannot see what
makes errors grow"; cite it.

**F6. Foster, Block & Misra 2024. Is Behavior Cloning All You Need? Understanding Horizon in Imitation
Learning.** NeurIPS 2024. https://arxiv.org/abs/2407.15007. Behaviour cloning with log-loss has
horizon-independent sample complexity under realisability and controlled payoff ranges. **2 (C1).** The
main counterpoint to blindness: state the boundary, namely realisability and evaluation lengths inside
the training distribution, against exactness at unseen lengths.

**F7. Simchowitz, Pfrommer & Jadbabaie 2025. The Pitfalls of Imitation Learning when Actions are
Continuous.** arXiv. https://arxiv.org/abs/2503.09722. Even in exponentially stable systems, any smooth
deterministic imitator learned from expert data suffers error exponentially larger in the horizon than
on the training distribution. **2 (C1).** A lower bound in the continuous setting; cite it beside T1.

**F8. Zhang T. et al. 2025. Action Chunking and Exploratory Data Collection Yield Exponential
Improvements in Behavior Cloning for Continuous Control.** arXiv (an ICLR 2026 version appeared in
search). https://arxiv.org/abs/2507.09061. Chunking adds closed-loop stability that offsets compounding.
**1 (C1, C2).**

**F9. Liu, Ash, Goel, Krishnamurthy & Zhang 2023. Exposing Attention Glitches with Flip-Flop Language
Modeling.** NeurIPS 2023. https://arxiv.org/abs/2306.00946. Transformers make sporadic long-range errors
copying one bit across distractors, and recurrent models do not. **2 (C8).** A pointer-type failure in
its simplest form; cite it with C8.

**F10. Barbero et al. 2024. Transformers need glasses! Information over-squashing in language tasks.**
arXiv. https://arxiv.org/abs/2406.04267. Distinct long sequences collapse to near-identical final
representations at low precision, so counting and copying fail. **2 (C8).**

**F11. Jelassi, Brandfonbrener, Kakade & Malach 2024. Repeat After Me: Transformers are Better than
State Space Models at Copying.** arXiv. https://arxiv.org/abs/2402.01032. Fixed-state models cannot
copy long strings; transformers can. **1 (C8, C2).** The reason our tracker keeps the input in the
cache.

**F12. Guo, Wu & Yiu 2026. The Deterministic Horizon.** arXiv. https://arxiv.org/abs/2606.00376 (already
`dethorizon2026`). Unaided state tracking crosses 50% accuracy at depth 19–31. Tool-integrated reasoning
reaches 76–94% against 17–42% for chain of thought, and fine-tuning helps by less than 3 points. **2 (C9,
C8).**

**F13. Motwani et al. 2026. LongCoT: Benchmarking Long-Horizon Chain-of-Thought Reasoning.** arXiv.
https://arxiv.org/abs/2604.14140. 2,500 problems whose steps are each easy but which need tens to
hundreds of thousands of reasoning tokens; the best scores are GPT 5.2 at 9.8% and Gemini 3 Pro at 6.1%.
**1 (C9).** A candidate showcase for certified program calls mid-thought.

**F14. Chapra, Kumar, Mandal & Sinha 2026. The Complexity Ceiling Benchmark.** CTB workshop at ICML 2026.
https://arxiv.org/abs/2606.29278. Sequential tasks of depth 5–50 decay geometrically per step. 14.5% of
correct answers come from wrong reasoning, and forced verbose state tracking does not move the ceiling.
**1 (C8).**

**F15. Samiei, Mansouri & Soleymani Baghshah 2025. The Illusion of Procedural Reasoning: Measuring
Long-Horizon FSM Execution in LLMs.** arXiv. https://arxiv.org/abs/2511.14777. LLMs given an explicit
FSM degrade with horizon and branching factor. Rule retrieval with many branches is harder than a long
memory span. **2 (C6, C8).** Savant writes and runs tables, so this benchmark fits it directly.

**F16. Zhou Y. et al. 2025. GSM-Infinite.** arXiv. https://arxiv.org/abs/2502.05252. Accuracy declines
along a sigmoid in reasoning complexity, and exponential inference compute buys linear gains. **1.**

**F17. Gema et al. 2025. Inverse Scaling in Test-Time Compute.** TMLR. https://arxiv.org/abs/2507.14417.
Longer reasoning can lower accuracy, including on deduction tasks that need sustained focus. **1 (C9).**

**F18. Malek, Ge, Lazic & Jin 2025. Frontier LLMs Still Struggle with Simple Reasoning Tasks.** arXiv.
https://arxiv.org/abs/2507.07313. Procedurally scaled easy tasks, counting among them, break thinking
models through shortcuts, intermediate errors and long contexts. **1 (C8).**

**F19. Pai & Xian 2026. Long-Horizon State Tracking in LLMs: Executing MD5 through a Deep Sequence of
Dependent Tool Calls.** arXiv. https://arxiv.org/abs/2609.00012. gpt-oss-120b carries four 32-bit
words through 196 dependent tool calls and returns the right digest on most runs. Keeping its own
reasoning in context and voting over a thinking worker are what decide success. **1 (C9, C8).**

**F20. Schnabel et al. 2025. Lost in Transmission: When and Why LLMs Fail to Reason Globally.** NeurIPS
2025. https://arxiv.org/abs/2505.08140. Bandwidth-limited attention makes some problems BAPO-hard, and
chain of thought makes them easy. **1 (C8).**

**F21. Amiri, Huang, Rofin & Hahn 2025. Lower Bounds for Chain-of-Thought Reasoning in Hard-Attention
Transformers.** ICML 2025. https://arxiv.org/abs/2502.02393. **Li, Liu, Zhou & Ma 2024. Chain of Thought
Empowers Transformers to Solve Inherently Serial Problems.** ICLR 2024. https://arxiv.org/abs/2402.12875.
**0 (C8).** Theory for why plain decoding needs many steps.

### G. Frontier-model failures at length: arithmetic, counting, copying

**G1. Bie et al. 2026 (AI-rithmetic).** See §1.5. https://arxiv.org/abs/2602.10416 [read]. **3 (C8).**

**G2. Dai & Fan 2026. Language models fail at extended rule following.** arXiv (v1 was titled
"Counting as a minimal probe of language model reliability"). https://arxiv.org/abs/2605.02028 [read].
The study queries 126 model variants on an adaptive ladder of identical repeated items. Each has a
finite, syntax-sensitive "counting capacity"; failure is abrupt, with outputs jumping to salient numbers
(500, 1,000, 2,000), and reasoning variants and tools do not help. In Gemma 3 27B a linearly readable
count direction tracks the true count until it collapses, and the first error comes at 27 items in the
probed setting. The paper concludes that models use a finite set of count-like states. **2 (C8, C7,
C2).** This is the strongest 2026 frontier evidence for our "frontier models fail" framing. Run its
assay on Savant, plain and pinned. Per-model capacities are in its Table S1, which was not read.

**G3. Wen, Zhang, Chen & Lyu 2026. Frontier Language Models Struggle to Copy: Text Can Be Better Viewed
in 2D.** arXiv (ICML 2026 listings appeared in search). https://arxiv.org/abs/2607.16072. GPT-5.5, Gemini
3.1 Pro and Claude Opus 4.7 fail to copy long in-context strings exactly. The authors blame positional
encodings that copy by matching local context instead of locating positions; with 2D-RoPE, shallow
transformers copy perfectly at hundreds of times the training length. **2 (C8).** Independent evidence
for the pointer failure; our pin is the decoding-side fix where theirs is architectural.

**G4. Patil, Kumar, Sinha & Mandal 2026. Beyond Accuracy: Diagnosing Algebraic Reasoning Failures in LLMs
Across Nine Complexity Dimensions.** arXiv. https://arxiv.org/abs/2604.06799. Working memory is the
scale-invariant bottleneck; every model collapses between 20 and 30 parallel branches. **1 (C8).**

**G5. Zhang X., Cao & You 2024. Counting Ability of Large Language Models and Impact of Tokenization.**
arXiv. https://arxiv.org/abs/2410.19730; **Bueno, Lotufo & Nogueira 2024. Lissard.** arXiv.
https://arxiv.org/abs/2402.07859. Tokenisation changes counting accuracy; LLMs find common items in
lists of 20 but fail at 80. **1 (C8).** Chang & Bisk and Yehudai et al. (LIT #78, #79) are unchanged.

### H. State-tracking theory

**H1. Merrill & Sabharwal 2023. The Parallelism Tradeoff: Limitations of Log-Precision Transformers.**
TACL. https://arxiv.org/abs/2207.00729 (already `merrill2023parallelism`). **0.**

**H2. Merrill & Sabharwal 2025. A Little Depth Goes a Long Way (log-depth transformers),
https://arxiv.org/abs/2503.03961, NeurIPS 2025; Exact Expressive Power of Transformers with Padding,
https://arxiv.org/abs/2505.18948, NeurIPS 2025.** Depth Θ(log n) suffices for regular languages, so
state tracking over n steps needs depth growing with n. **1 (C8).** A reason fixed-depth plain decoding
must spend tokens.

**H3. Butoi et al. 2024. Training Neural Networks as Recognizers of Formal Languages.** ICLR 2025.
https://arxiv.org/abs/2411.07107. **0.**

**H4. Zhang & Li 2026. Tracking States or Tracking Cosets?** arXiv. https://arxiv.org/abs/2609.29951
(already `zhang2026cosets`). Partial accuracy reflects quotient (coset) solutions; transformers recover
only normal-subgroup cosets, while RNNs also pass through non-normal ones. **1 (C7, C2).** A diagnostic
for our partial-accuracy plateaus.

**H5. Dhayalkar 2025. Neural Networks as Universal Finite-State Machines.** arXiv.
https://arxiv.org/abs/2505.11694. Feed-forward networks unrolled in depth simulate DFAs up to a fixed
length and embed Myhill–Nerode classes separably. **1 (C3).** It uses the Myhill–Nerode name for a
finite-length representation result, so pick our theorem's name with that in mind.

**H6. Park & Choi 2026. Lifted State Hypothesis in Large Language Models.** arXiv.
https://arxiv.org/abs/2607.19360. Inputs indistinguishable in computation-relevant behaviour form a
"type" that shares a latent state; later revision of a subtype fails to localise. **1 (C3, C4).**

### I. State and entity tracking inside LLMs

**I1. Li, Guo & Andreas 2025. (How) Do Language Models Track State?** arXiv (a PMLR v267 / ICML 2025
listing appeared in search). https://arxiv.org/abs/2503.02854 (in NOVELTY) [read]. Pythia-160M and GPT-2
fine-tuned on S3/S5 composition learn either an associative scan or a parity-then-scan algorithm,
identified by prefix patching, probes and parity heads. Both are near perfect up to the training length
(100) and drop steeply past a cutoff; the mechanism can be steered by intermediate tasks. **2 (C7, C4).**
Fine-tuned pretrained LMs learn parallel scans, not step-by-step simulation. Our latent executor is
sequential and exact, so show that mechanism difference explicitly.

**I2. Zhang Y., Du, Jin & Fu 2025. Finite State Automata Inside Transformers with Chain-of-Thought.**
arXiv. https://arxiv.org/abs/2502.20129. Late-layer MLP neuron sets encode each automaton state (about
100% compression and distinction) in Transformer+CoT trained on state tracking. **2 (C7).** "An implicit
FSA in MLP neurons" is close to our robust-cell mechanism.

**I3. Kim & Schuster 2023 (LIT #81); Kim, Schuster & Toshniwal 2024. Code Pretraining Improves Entity
Tracking Abilities of Language Models.** https://arxiv.org/abs/2405.21068. Extra code training helps
entity tracking; extra maths training does not, consistently. **1.**

**I4. Prakash et al. 2024. Fine-Tuning Enhances Existing Mechanisms: A Case Study on Entity Tracking.**
ICLR 2024. https://arxiv.org/abs/2402.14811. Fine-tuning improves entity tracking through the same
circuit the base model already uses. **2 (C4).** It is precedent for "a short fine-tune switches on an
existing mechanism." Test whether the 30-step switch reuses a pre-existing circuit.

**I5. Prakash et al. 2025. Language Models use Lookbacks to Track Beliefs.** arXiv.
https://arxiv.org/abs/2505.14685; **Feng & Steinhardt 2023. How do Language Models Bind Entities in
Context?** https://arxiv.org/abs/2310.17191; **Gur-Arieh, Geva & Geiger 2025. Mixing Mechanisms.** ICLR
2026. https://arxiv.org/abs/2510.06182. These describe binding IDs, ordering IDs with lookback
retrieval, and a mix of positional, lexical and reflexive retrieval. **1 (C7, C8).** Our "pointer" is
a positional retrieval mechanism in their vocabulary.

**I6. Tang et al. 2026. Do Language Models Track Entities Across State Changes?** ICML 2026.
https://arxiv.org/abs/2605.30233. LMs do not track world state step by step: they aggregate relevant
facts in parallel at the query, and implement REMOVE with a fragile global suppression tag that predicts
failures. **2 (C8, C7).** Plain decoding with a non-incremental strategy is exactly what our pinned
clock replaces. Cite it as the mechanistic reason plain models fail on long event streams.

**I7. Oh & Demberg 2026. A Retrieval Conditioned Rebinding Circuit for Dynamic Entity Tracking.** arXiv.
https://arxiv.org/abs/2606.08644; **Li, Nye & Andreas 2021. Implicit Representations of Meaning in
Neural Language Models.** ACL 2021. https://arxiv.org/abs/2106.00737. **1.**

### J. Long-context and state-tracking benchmarks

**J1. Kuratov et al. 2024. BABILong.** NeurIPS 2024 Datasets & Benchmarks.
https://arxiv.org/abs/2406.10149. LLMs use 10–20% of their context effectively; recurrent memory
transformers reach 50M tokens. **1.**

**J2. Hsieh et al. 2024. RULER.** COLM 2024. https://arxiv.org/abs/2404.06654. It includes multi-hop
tracing (variable tracking); half of the models fail at 32K. **1.**

**J3. Michelangelo (LIT #82); Ye et al. 2025. LongProc,** COLM 2025, https://arxiv.org/abs/2501.05414,
where models falter on 2K–8K-token procedural outputs. **Suzgun et al. 2022. BIG-Bench Hard**
(tracking shuffled objects), https://arxiv.org/abs/2210.09261. **Kazemi et al. 2025. BIG-Bench Extra
Hard**, https://arxiv.org/abs/2502.19187. **Liu et al. 2023. Lost in the Middle**, TACL,
https://arxiv.org/abs/2307.03172. **Modarressi et al. 2025. NoLiMa**, ICML 2025,
https://arxiv.org/abs/2502.05167. **1.**

**J4. Yen, Mani, Renda & Hardin 2026. LEAPS.** arXiv. https://arxiv.org/abs/2610.25919 (already
`yen2026leaps`). Its state-tracking tasks degrade far faster than recall up to 512K, and thinking models
often do worse. **1 (C8).**

**J5. Cohen & Mooney 2025. MET-Bench.** ICML 2026. https://arxiv.org/abs/2502.10886. **0.**

**J6. La Malfa et al. 2024. Code Simulation Challenges for Large Language Models.** arXiv.
https://arxiv.org/abs/2401.09074. LLM simulation of straight-line programs, loops and sorting is fragile
and degrades with complexity. **1 (C6, C9).**

**J7. Wu et al. 2025. Computational Reasoning of Large Language Models (TMBench).** arXiv.
https://arxiv.org/abs/2504.20771. Turing-machine execution from a supplied transition table, with
step-wise accuracy curves. **2 (C6).** A ready-made public benchmark for Savant's "run literal tables";
report on it.

**J8. Markeeva et al. 2024. The CLRS-Text Algorithmic Reasoning Language Benchmark.** arXiv.
https://arxiv.org/abs/2406.04229. **1 (C10).**

**J9. Zou & Tang 2026. Trace as State.** arXiv. https://arxiv.org/abs/2609.02702. Placing a reasoning
trace before the long context, as a state proxy, lifts GraphWalks exact match (GLM-5.2 to 100%). **1
(C9).**

### K. Programs executed inside transformers (C10)

**K1. Tzamos and colleagues at Percepta 2026. Can LLMs Be Computers?** Blog, 11 Mar 2026.
https://www.percepta.ai/blog/can-llms-be-computers. The page title, date and author were verified, but
the body did not render. Its content was read through a third-party mirror
(https://code.nym.sh/kennethnym/percepta-computer-as-llm/raw/branch/main/article.md). According to the
mirror, a 7-layer, d = 36, 18-head transformer runs a WebAssembly interpreter for millions of steps.
2D-key hard-max attention gives O(log t) convex-hull lookups, and the post claims 100% on Sudoku. It is
standalone, not a pretrained LLM, with no error-rate benchmark. **2 (C10, C4).** It is the
interpreter-in-weights showcase reviewers will name. Our register interpreter is learned or switched on
inside a pretrained model; say so.

**K2. Turkcan 2026. Loom: A Scalable Analytical Neural Computer Architecture.** arXiv.
https://arxiv.org/abs/2604.08816. A looped 8-layer transformer with analytically derived weights
executes a 22-opcode instruction set compiled from C, with programs in the state tensor. **1 (C10).**

**K3. Giannou et al. 2023. Looped Transformers as Programmable Computers.**
https://arxiv.org/abs/2301.13196; **Weiss, Goldberg & Yahav 2021. Thinking Like Transformers (RASP).**
ICML 2021. https://arxiv.org/abs/2106.06981. **1 (C10).**

**K4. Yang C., Srebro, McAllester & Li 2025. PENCIL: Long Thoughts with Short Memory.** ICML 2025.
https://arxiv.org/abs/2503.14337. Learned erasure of intermediate thoughts simulates any Turing machine
with optimal time and space; a 25M model solves Einstein's puzzle. **2 (C5, C10).** A learned KV-memory
policy for long exact computation; cite it with the pin.

**K5. Schuurmans 2023, 2024 (LIT #70, #71).** No change.

### L. Certified or tool calls in mid-reasoning (C9), for context

**L1. Feng et al. 2025. ReTool** (https://arxiv.org/abs/2504.11536) and **Li, Zou & Liu 2025. ToRL**
(https://arxiv.org/abs/2503.23383). RL-trained code-interpreter calls interleaved with reasoning (AIME
67% and 43.3%). **1 (C9).** Our calls differ in being certified programs run by the model itself, not
by an external interpreter; say so. The Deterministic Horizon (F12) and MD5 (F19) are the closest
evaluations.

---

## 3. The frontier in 2026

**Exact arithmetic at length** comes from small or specially built models, not from frontier language
models:

- **Cellular automata and tiny loops.** A neural cellular automaton reports 100% addition from 16 to
  1,000,000 digits (Wei 2026a). Another learns binary multiplication to 683× its training range (Wei
  2026b). A tiny transformer with a right-to-left loop adds to 1,000 digits, with some runs to about
  300,000 (Patriota 2024). All are preprints with few samples at the top lengths.
- **Transformers trained from scratch.** They reach 99% at 100 digits (Abacus, from 20), above 95% at
  200 (position coupling, from 30), 100+ digits by self-improvement, 50-digit multiplication from 5, and
  2–3× on multi-operand tasks.
- **Pretrained LLMs taught an algorithm.** They reach about 98–99% at 100 digits within the training
  range (CAEF) and 95% at 30 digits (Meta-RFFT).
- **Frontier models without tools.** They lose addition accuracy well before 100 digits, mostly by
  operand misalignment and independent carry slips (Bie et al. 2026). In CAEF's comparison GPT-4o scores
  43% on 100-digit addition.

No published exact addition at 1,000+ digits inside a pretrained LLM turned up in the searches run.
Savant's 4,096 (and 8,000) is then a claim of exactness inside an LLM with language kept, not a
length record.

**Long-horizon execution.**

- **GPT-5 thinking** sustains about 2,176 steps at 80% accuracy on a supplied-plan running sum, against
  432 for Claude-4 Sonnet and 120 for Gemini 2.5 Pro (Sinha et al.).
- **Counting.** Every one of 126 models has a finite counting capacity, which thinking and tools do not
  lift (Dai & Fan 2026).
- **Copying.** GPT-5.5, Gemini 3.1 Pro and Claude Opus 4.7 fail to copy long strings exactly (Wen et al.
  2026).
- **Long reasoning and long context.** The best LongCoT score is under 10%, and state-tracking tasks in
  LEAPS degrade far faster than recall.
- **The exception.** A million-step task is solved with zero errors only by holding the state outside
  the model and voting at every step (MAKER).

**State tracking.** Affine recurrences (SSMs, linear attention) are now proved unable to correct drift
along state-separating directions or to track non-definite automata at finite precision (Chung et al.;
Brandoit et al.). Non-affine trackers with hard projection, argmax restoration or a weight-level
certificate are exact to about 10⁶ tokens:

- NFSM on S3–M11 (Brandoit et al.);
- a projected model on S3×S3, from length 8 (Lee);
- certified absorbing-state RNNs at L = 10⁶ (Bugaud);
- Householder RNNs without the additive path, 1.00 at 16× (Howe).

Inside pretrained LLMs the best published result is PAR: a looped Qwen2.5-0.5B at 95.5 ± 11% full-state
accuracy on swap-S5 at 16×, against 0.8% for explicit chain of thought. It has no certificate and no
language evaluation. On the theory side, transformers admit no computable length-generalisation bound
(Yang et al. 2026), and DFAs have length complexity 2n − 2 for an idealised learner (Chen et al. 2025).

---

## 4. Ideas: baselines, benchmarks and tests

**Baselines to add.** Rows 1–6 are the minimum set.

| # | Baseline | Purpose | Code |
|---|---|---|---|
| 1 | NFSM (A3) | the architectural route to exactness | project page in its arXiv comment |
| 2 | PAR (B1) on Qwen2.5-0.5B | the in-LLM latent rival; report all-correct-run rates at 1,024–4,096 and language retention | — |
| 3 | Inductive-scratchpad mask without a certificate (A2) | separates the pin from the certificate | — |
| 4 | CAEF-style Turing-machine LoRA (D1) on the Savant base | the "LLM taught to execute" rival | — |
| 5 | Howe's "−b" Householder RNN (B11) | an exact small tracker with no special loss | — |
| 6 | RLT (B2) | per-token recurrence | — |
| 7 | Lee's projected model (A10) | hard projection | optional |
| 8 | SEAD (A11) for addition | the length-record holder | optional |

**Benchmarks to report.**

- **Frontier addition.** Extend Bie et al.'s protocol to 1,000–8,000 digits, using their error
  classifier on both frontier models and our plain decoding.
- **Counting.** Run Dai & Fan's counting-capacity assay on plain, pinned and Savant decoding.
- **Copying.** Run Wen et al.'s Binary Copy.
- **Execution horizon.** Run Sinha et al.'s supplied-plan running sum against GPT-5 thinking's 2,176
  steps.
- **Table execution.** FSM Execution (F15) and TMBench (J7) are natural fits, since Savant runs literal
  tables.
- **State-tracking suites.** Shuffled objects from BBH and BBEH, RULER variable tracking, the LEAPS
  state-tracking subsets and Michelangelo Latent List, for the language-kept and state-tracking claims.
- **Splits and diagnostics.** Lee's held-out transition-pair split as a memorisation control for the
  trackers, and Zhang & Li's coset diagnostics for partial accuracy.

**Tests for the claims.**

1. **C5, necessity.** Corrupt one certified row that training rarely reaches and show the certificate
   catches it before a long run fails on it (Cai et al. give only sufficiency). Report certificate size
   against Cai's verification set for addition.
2. **C5, pin vs certificate.** Run Abbe's mask alone vs mask plus certificate at 1,024–8,192. Run Price
   et al.'s symmetric adversarial inputs (000…002 × 000…002 style) through plain and pinned decoding: the
   certificate should cover them, and testing alone may not.
3. **C1, instances.** Show that blindness covers the radial-scale case of Sharma & Vu (cross-entropy
   through RMSNorm), Howe's additive-path pull-off and Block et al.'s gradient variance amplification.
   State where Foster et al.'s horizon-independence holds (realisable, in-distribution) and why exactness
   at unseen lengths falls outside it.
4. **C2, C4 against PAR.** Replicate PAR's norm-anchoring ablation and our own signal × norm factorial
   side by side on the same backbone; add our kick to PAR's loop.
5. **C3 against Brandoit and Bugaud.** Measure their R1–R3 conditions and margin on our trackers, extract
   transition tables, and show a non-absorbing automaton (mod-k counting or S5) certified by our theorem
   but outside Bugaud's class.
6. **C7.** Run Nikankin's heuristic-neuron typing and Lindsey-style lookup-table attribution on Savant's
   tick, and check Zhang Y. et al.'s per-state neuron-set metrics. Report whether the "committee" is a
   bag of heuristics or a table.
7. **C8.** Fit Bie's geometric carry model to our step-drift errors and the misalignment classifier to
   our pointer errors. Test whether Tang et al.'s non-incremental aggregation explains where plain
   decoding first misreads.

---

## 5. Partly verified items and gaps

**Partly verified.**

- **Percepta (K1).** The primary page's title, date and author were verified; the body came from a
  third-party mirror.
- **Bugaud 2026a, b (A4, A5).** Read from icml.cc listings. OpenReview showed a bot check, and no arXiv
  version was found.
- **Ibrahimli et al. (B8).** icml.cc listing only.
- **Lindsey et al. (E1).** Read on transformer-circuits.pub.
- **Venues taken from search-result listings, not from fetched pages:** Chen et al. 2025 (ICML 2025),
  Hu et al. 2024 (ICML 2024), Li et al. 2025 (ICML 2025), McLeish et al. 2025 (NeurIPS 2025), OccamLLM
  (NeurIPS 2024), AUSSM and Ebrahimi & Memisevic (NeurIPS 2025), Zhang T. et al. 2025 (ICLR 2026) and
  Wen et al. 2026 (ICML 2026). Ruoss et al. (ACL 2023) and Nanda et al. (ICLR 2023) are given from
  memory and are not on their arXiv records. Check all of these before citing.

**Gaps.** The web-search budget, shared across the agents in this run, ran out before three searches:
(i) frontier reasoning models on 1,000+-digit addition, (ii) M²RNN's tested lengths, and (iii) the
per-model counting capacities in Dai & Fan's supplementary table. None of the searches run found a paper
that combines all of: exact multi-thousand-step execution inside a pretrained LLM, a necessary-and-
sufficient certificate, and measured language retention. That combination is where our claim stands, and
each component has the precedents listed above.
