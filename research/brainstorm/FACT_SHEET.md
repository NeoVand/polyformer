# What we can do today (facts only; numbers are measured)

**v1: small networks, theory.**
- **A blindness theorem.** A network trained only on the states its training data reaches cannot see how its errors
  grow, so it drifts at length.
- **The fix is to "snap" the state to a finite code every step.** With it, small recurrent trackers keep an exact
  state at 16–250× their training length:
  - group words (S5);
  - Lean proof rewriting;
  - 4,096-digit addition;
  - a Rubik's cube;
  - programs.

  Frontier LLMs fail on the same tasks at 1,000–4,096 steps.
- **Robust Myhill–Nerode theorem**, Lean-proved.
- **In-model, latent:** Qwen-0.5B kept an exact state in its residual stream, with no tokens emitted, for 4,096 steps.

**v2: Savant, a Qwen3-4B fine-tune that runs in a browser on WebGPU.**
- **What it does with a question.** It writes a small program (a transition table), checks every row of the table
  with its own forward passes (a per-row "certificate"), then runs it.
- **How the run works.** Each step is the model's own decoding under a fixed attention/cache rule: keep the program,
  show only the current (state, event) pair, restart positions.
- **Theorems (Lean):**
  - the per-row certificate is necessary and sufficient for exactness at any length;
  - no finite test certifies ordinary decoding;
  - composition of calls;
  - the adder table is correct.
- **Measured:**
  - addition exact at 10, 100, 1,000, 4,096 and 8,000 digits; language kept (GSM8K 92%);
  - state tracking exact to 10,000 events;
  - every executed step bitwise equal to its certified row.
- **With no extra training**, it executes a register machine exactly (multiply, gcd, sort, factorial, primes), and
  2,079 of the 2,081 rules of a universal Turing-machine (Lag-system) encoding.
- **Reasoning with calls.** It reasons in words, calls programs mid-thought and reads their results. On new problem
  templates it is 43% right, against 9% for base Qwen thinking at 32k tokens. A frontier model without tools beats
  it. The failures are always in writing or reading the program, never in executing it.
- **Inside the model:**
  - every one of 9 LLM families tested already has a head that finds the right table row;
  - in Qwen, one learned 2,560-number vector switches on reading out the answer (99% of rows);
  - near-duplicate names cause most errors;
  - plain decoding (the model writing its own run with all history in context) fails first by losing its place in
    the input, then by drift.

**The world (prior art, 2024–2026).**
- **Prompted Gemini and Llama-4 simulate a universal machine,** with each rule checked once and a fresh call per step
  (Schuurmans; Lewandowski et al. 2026). It is very slow, one fixed hand-built program, and the model writes nothing.
- **Percepta compiled a WebAssembly/Python interpreter into a tiny transformer** (not an LLM).
- **MAKER ran a million Towers-of-Hanoi moves error-free** with an LLM, by voting at every step.
- **Small trained interpreters run long traces** (Xu & McAllester 2026).
- **Tool use mid-reasoning** is a shipped product (o3, Claude).
- **Chain of Code** has the LLM emulate code it can't run.
- **"LLMs can't plan"** (Kambhampati et al.).
- **World models drift** (Dreamer, Genie).
- **ARC-AGI is unsolved by pure LLMs.**

Full map: /Users/neo/repos/polyformer/research/prior_art/L1–L6 (read these to avoid re-proposing known work).
