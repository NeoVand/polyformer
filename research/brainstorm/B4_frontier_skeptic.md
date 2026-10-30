# B4: the frontier skeptic

## 1. What a frontier lab would shrug at

Any demo whose punchline is "exact on symbols" has a tool-call twin that is faster, cheaper and just as exact, and
that twin is what a lab sees.
- **Long runs are simulators.** The 8,000-digit adder, the 10,000-event tracker, the ghost cube, the robot and Hanoi-20
  are each a 30-line simulator. A neural cellular automaton has added million-digit numbers (Wei 2026a), and MAKER ran
  10⁶ steps without an error.
- **Universality is settled** (Schuurmans 2024; Lewandowski 2026; Percepta's MicroPython).
- **REASON is o3's shipped format.** On our own numbers (43% on new templates), a frontier model without tools wins.
  Our failures are in writing and reading programs, which is where frontier models are strongest.
- **The inside views look familiar.** Poke-the-brain reads as a debugger on a lookup table. "Browser" is WebLLM. "A
  head that finds the row" is a retrieval head until we show otherwise.
- **"Certified" means "matches the table the model wrote".** Python gives that guarantee for free, and 64–88 certified
  gate answers had the wrong table.
- **A prompt-injection-proof agent is CaMeL** (DeepMind 2025; not in L5, check), built on Python.

The inside of the model is worth something only where the proof, or the inside itself, is the product.

## 2. Three ideas, ranked

### Idea 1. "Here is exactly what I will get wrong"

**The demo.**
1. Before seeing any input, the model prints a regular expression for the exact set of inputs, of any length, on which
   its run will go wrong.
2. The internet attacks it. Every failure found is already in the set, and everything outside the set comes out right.
3. The model repairs itself until the set is empty and prints Q.E.D.

**Why a lab can't or won't.**
- **It follows from our iff theorem.** Under the pin, every step is bitwise one of finitely many rows, so a run fails
  exactly when it reaches a failing (state, event) row. The failure set ("runs that reach row r") is regular and costs
  one forward pass per row.
- **No-finite-test says no finite probing determines it under ordinary decoding.**
- **Labs think of self-knowledge as calibration,** a probability. Nobody believes a network can print an exact, finite
  description of its own infinite error set.
- **"Trivial, it's just row r"** holds only because of the theorem; without the pin it is false.

**The jaw drop.** A bounty page: "Find an input we got wrong that is not in our printed set." Hunters find failures, and
every one of them is already listed. The model then retrains its own switch vector live (rank-1 LoRA reached 128/128 by
step 100). The set shrinks to ∅, it prints Q.E.D., and the bounty stands.

**Assets.**
- Theorem P and no-finite-test, proved in Lean.
- Per-row certificates from the model's own forward passes.
- A latent executor, so the repair takes about 30 steps.
- The browser: the visitor's own GPU recomputes the certificate, which handles host-dependent code paths.

**The smallest 48-hour experiment (no training).**
1. Take the one-vector model's 25 uncertified G1 tables (99.74% of rows right).
2. Build each table's failure automaton.
3. Run 10,000 pinned inputs of length 10–10,000, half from inside the predicted set and half from outside it.
4. Pass: the prediction is 100% right in both directions, on two hosts.

**What kills it.** One misprediction on the reference host: the state is not truly regenerated, or the pin leaks.
Design rule: the specification must come from outside the model, either a table the user gives or a black box probed
by Chow's W-method (complete under a stated bound on the number of states).

### Idea 2. Certified object permanence: a world that never melts

**The demo.** A world model trained on 32-step pixel clips runs in the browser for an hour with every object exactly
in place. Beside it, an unsnapped twin melts within a few hundred steps, and a frontier video model loses a Rubik's
cube within five twists (test this first).

**Why a lab can't or won't.**
- **Labs (Genie, video models, xAI's games) treat drift as a compute and memory problem.** The blindness theorem says
  it is not: no loss on reached states sees drift grow.
- **Discreteness is not enough:** Genie's tokens are discrete and still drift.
- **Their state cannot be certified.** A whole frame of tokens cannot be enumerated row by row, and their end-to-end
  bet keeps them from factoring it.

**The jaw drop.** Cover the scene for 10,000 steps and keep acting. When you uncover it, every object is where it
should be: object permanence, proved for a neural simulator.

**Assets.**
- The v1 snap: exact at 16–250× training length on the cube, S5 and programs.
- The blindness theorem.
- Certificates over factored (object slot, action) rows.
- jax-js.

**The smallest 48-hour experiment.** A gridworld with 3–5 objects and an occluder, pixels in and out. The model is an
encoder, snapped slots, a factored transition and a renderer. Train at 32 steps and test at 4,096 against the twin
trained with scheduled sampling.

**What kills it.**
- Pixel-to-slot errors above 10⁻⁵ per frame.
- Collision rows that make the table too large to certify.
- The twin also holding to 4,096.

### Idea 3. The universal key: every LLM is one vector away from an exact computer

**The demo.** A gallery of nine open model families, each with its own key of 2,560 numbers. Each base model loses
Hanoi-20 within a few hundred moves. With the key, the same frozen model runs all 1,048,575 moves exactly. Stretch: the
S5 automaton read from Qwen-0.5B's latent state runs as a certified program inside Llama.

**Why a lab can't or won't.** Labs don't care about execution without tools. The public believes models cannot
execute algorithms (Shojaee et al. 2025); our mechanism says they lose their place.

**The jaw drop.** "Your Llama already contains a computer; here is the switch."

**Assets.**
- The lookup head in all nine families.
- The Qwen key.
- MECHANISM: the latent state is the minimal automaton (960/960 clusters).

**The smallest 48-hour experiment.** Train keys for Llama-3.2-3B and Gemma-3-4B on G1 and certify held-out tables.
Compare with a mean-activation function vector (Todd et al.).

**What kills it.** Fewer than 90% of tables certified, or the function vector doing as well.

**Verdict:** viral, but it will not impress a lab.

## 3. If I could only pursue one

Idea 1.
- **No tool call reproduces it.** It is the only demo whose product is the theorem, and our own no-finite-test theorem
  says ordinary decoding never will.
- **It answers the best attack.** The objection that the model is certified only against its own table becomes the
  headline, because the error set is measured against a specification from outside the model.
- **It is cheap and decisive:** no new training, a pass-or-fail result.
- **It changes the story.** We move from "exact calculator", which every lab shrugs at, to a model that knows exactly
  which inputs it will get wrong before it sees them, and proves when there are none left.
