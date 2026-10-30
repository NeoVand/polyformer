# PAPER v2 plan: open with a banger, close with one

28 Oct 2026, orchestrator. v1 ("Neural Networks That Don't Lose Track: Exact Digital State Without Chain of
Thought") is final apart from the author details and an endorser. v2 is the same paper extended by the language-model
half, posted as an arXiv update. This plan fixes the arc, the claims and the figures. The numbers come from the reports
named in INSIGHTS.md. Results still pending are marked as such.

## The arc in five sentences

1. **Open.** Frontier reasoning models lose track on long state tracking: S5 words, 4,096-digit additions, a cube
   turned 1,000 times. We prove why a trained network will too: a loss evaluated on the states training reaches
   cannot see how errors grow away from them (blindness).
2. **v1.** Robustness must therefore be built in (a closure that regenerates the state each step) or probed (an aimed
   kick). With both, small trackers keep an exact digital state far past their training length.
3. **Pivot.** An off-the-shelf LLM already contains the lookup a finite-state step needs. About 30 optimizer steps
   switch it on, and a fixed-window clock that gives each step only the program and a fresh block is a regenerating
   architecture.
   - Theorem P: if the program's rows are certified, every run is exact at any length.
   - The theorem pair, proved in Lean: no finite test certifies unpinned decoding, while for the pinned step a finite
     per-row certificate is necessary and sufficient. This is blindness, again, inside the LLM.
   - In the measured runs, every tick is bitwise equal to a checked row.
4. **The model.** Savant, a 4B chat model, turns a question into a small program, certifies it and runs it inside its
   own forward passes. It keeps its language. It runs in a browser.
5. **Close.** Savant reasons in words, calls its interpreter mid-thought, reads the result and keeps reasoning. On
   composite problems with long computations inside, it stays exact where its own base model and frontier models
   fail. (REASON; pending.)

## Opening banger (candidates; pick one)

- **A.** The frontier failure panel (Fig. 1a as is) plus the blindness theorem in one sentence. Proven, measured,
  and already in v1.
- **B.** A single picture: the same question answered by a frontier model (wrong at 4,096 digits) and by a 4B model in
  a browser (exact, every tick certified). Strongest hook for v2, but the arithmetic must be live (r3) first.

Recommendation: keep A as Fig. 1, and put B's picture in the abstract figure / teaser.

## Closing banger (in order of preference; the first that holds)

1. **Mid-reasoning execution (REASON).** Accuracy against the length of the embedded computation (64 → 4,096 events,
   10 → 1,000 digits) on held-out composite templates, for:
   - Savant with the clock (flat);
   - Savant writing its runs itself;
   - base Qwen3-4B thinking at 32k tokens;
   - frontier models (n = 16–32 per cell).

   Shown with a transcript replay: reasoning, then a program, the certificate, the run and the result, and more
   reasoning. Plus the model's probability of opening `<program>` along the transcript: the moment it decides to
   compute.
2. **No clock (BRIDGE part 2).** If the aimed kick in context makes plain decoding length-flat, the model runs
   programs with no clock at all. This closes the loop with v1: the kick replaces the architecture.
3. **Fallback.** Certified addition at 10–4,096 digits inside the LLM: every output digit right, every tick bitwise
   equal to its certified row, against frontier models (FIVE's FRONTIER2: 2/3, 2/3, 0/3 at 4,096).

## Claims we make, and the ones we refuse

**Make:**
- Theorem P and its converse; the Mealy version; no finite test certifies unpinned decoding; Lemma Q with the softmax denominator over all positions (all in Lean, lean-p af8809ad).
- The Mealy version.
- Token emission is not a full snap in context (counterexample).
- Composition: certified calls make the execution term of the error exactly zero (INSIGHTS C).
- The executor is latent and switched on cheaply (CIRCUITS §2, WEIGHTS §2).
- Plain decoding drifts and the pin does not (BRIDGE, pending).
- Language kept (Stage 2r numbers).

**Refuse:**
- "Certified" never means "the answer is right": the certificate checks the run against the written table, not the
  table against the question. Report the 64–88 certified-but-wrong answers (of 1,280 pinned responses).
- No weights-level certificate: the per-program certificate is the guarantee (CIRCUITS §1).
- Bitwise claims hold for one host and code path.
- Do not say "never", "forever" or "general computation". Use "programs of this kind, at the lengths tested, exact".
- Do not hide the clock. It is a few dozen lines that copy one token per tick and compute nothing about the state.
  Show it in Methods, line counts and all. Where the arithmetic clock pads digits, say so.

**Answer "is it a tool call?" with BIGIDEA H2.** The pinned tick is the LLM's ordinary decoding under a KV-cache
policy:
- keep Π as a sink;
- evict each block;
- restart positions after Π.

Under that policy, token-by-token decoding is bitwise equal to its own certificate, on 24,336/24,336 ticks. StreamingLLM
windows and full attention fail. The clock adds only the cache policy and the event stream (the pointer).

**Answer the "is it trivial?" referee in the text.** The executor is cheap because it is latent. What is new:
- the regeneration theorem, with a certificate that is necessary and sufficient;
- the measured fact that this turns a 35%-accurate latent lookup into an exact computer at any length;
- a model that decides for itself when to compute.

Plain fine-tuning without the pin drifts beyond the training range (BRIDGE quantifies this).

## Figures (code-generated, white background, Cobalt and Rose; no AI-generated pixels)

| fig | content | source | status |
|---|---|---|---|
| 1 | v1 Fig. 1 (frontier failure, blindness, kick, digital codes) | paper | done |
| v2-1 | **The clock is a closure.** Left: plain decoding, where the run so far sits between Π and each new step. Right: the pinned step, Π plus one fresh block with the history evicted. Below: the certificate grid and a run whose ticks light up their rows. | DEMO_DESIGN, page components | to draw |
| v2-2 | **Inside Savant's head.** (a) The lookup committee, the head map on one table. (b) Formation: base 37% → 30 steps 100% of rows, and the head-map correlation over training. (c) Logit lens: first among the states (layer ≈ 24), then over the vocabulary (≈ 30). (d) Sharp decision steps between two states (robust cells inside an LLM). | CIRCUITS figs 1, 4, 6, 8; WEIGHTS executor fig | data done; restyle |
| v2-3 | **Blindness inside an LLM.** Plain vs pinned error against length; the sensitivity of the next state to earlier run tokens (plain > 0, pinned = 0); the kick arm. | BRIDGE | pending |
| v2-4 | **Closing.** Composite accuracy against computation length, Savant against base thinking and frontier models, plus one transcript replay. | REASON | pending |
| ED | Size (needles to 4,096 rows; 8,192 pending); the gap contract; rank-4 executor; failure anatomy; language table; arithmetic gates | CIRCUITS, WEIGHTS, PROMPTBOX, ARITH | data done |

## Cross-field paragraph (Discussion, short)

- **Theoretical CS.** The pinned step is Turing's split of finite control from tape. The certificate is translation
  validation of one program on one machine. Regeneration below the program is von Neumann's restoring organ.
- **Neuroscience** (analogy, flagged as such):
  - plain decoding drifts like a bump attractor, whose error grows with delay;
  - the pinned step recomputes the state from a discrete token, like activity-silent working memory;
  - the executor is recycled induction circuitry, like reading's use of visual cortex.

  Only BRIDGE's drift curve makes any of this a measurement.

## Decisions for Neo (morning)

1. v2's title.
   - Keep v1's title and add "and Run Programs"?
   - Or the proposed "Neural Networks That Run Programs Without Chain of Thought"?
2. Opening teaser: B, the browser-vs-frontier picture, once r3 is live.
3. Which closing banger, once REASON and BRIDGE report.
4. Whether the page gets a plain-mode toggle (no clock), so a skeptic can watch the drift for themselves.
