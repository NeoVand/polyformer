# The dream: what Neo asked the model to do

This file collects Neo's own words, from 26 to 29 Oct 2026, gathered by the orchestrator on 29 Oct after Neo asked
"What did I ask you that the model should do? What was the dream?". Every condition below cites the moment Neo set it.
Use this file as the acceptance test for any proposal.

## The dream in one sentence

One new kind of language model that thinks with exact internal computation. You ask it a normal question. It writes
its own compact program and runs that program inside its own forward passes, without chain of thought and without a
tool. It does this unprompted, as part of its own reasoning. The computation is provably exact and checkable. The
model is still a normal LLM. The demo makes ML-researcher investors see that, scaled, this eats Python, Lean and the
calculator.

## The conditions (Neo's words in quotes)

1. **One model, many abilities, with no per-skill adapters.**
   - "In reality you're not going to want an adapter for each of the different scenarios. That's not that different
     from tool calling." (26 Oct, after FIVE's joint model failed)
   - "Failure in training simultaneous automatons is a sign of our weakness."
2. **The LLM itself computes.**
   - Not a module bolted on: "The separate lookup head is cool, but that's not what we want." (27 Oct, QINTERP)
   - Not an external host either: the clock is "fine but not ideal", so "keep shrinking the clock". (27 Oct)
3. **The model turns a normal prompt into a program and runs it inside.**
   - "maximum effort on interpreter inside LLM ... normal prompting, the model turns it into a program and runs it
     inside ... a user with a prompt box can check." (27 Oct, PROMPTBOX)
   - "Emergent unprompted use is the breakthrough."
   - RL should let it discover how to use its interpreter: "system 2 thinking, not just a lot more of system 1."
4. **No chain of thought.** The working title for v2 is "Neural Networks That Run Programs Without Chain of Thought"
   (27 Oct). State lives in the model, not in thousands of written tokens.
5. **Exact, certified, and nothing a skeptic can poke holes in.** "Not something a skeptic would immediately poke holes
   in." (27 Oct) Novelty claims must be verified: Neo would unsubscribe over a false "doesn't exist yet".
6. **Compact code, not tables.** "Imagine if it wrote something like python or bff or even just assembly code or even a
   language invented exactly for writing and running code in the brain of the model." (29 Oct) A program is not 200
   rows.
7. **One executor, many programs.** "I really like the interpreter idea." (26 Oct) One interpreter is certified once,
   and every program inherits exactness. The thesis to beat: "automata are programs; many automata = one".
8. **It generalises.** New task families and new wording, not only the trained ones. "It might generalize ... don't
   give up ... good RL." (27 Oct)
9. **Language stays intact.** It must still be a normal model: GSM8K, MMLU and perplexity held.
10. **A new model, pointing at a new architecture.**
    - "Main goal = ONE great model served behind the demo page; the page is the vehicle, not the goal." (27 Oct)
    - With funding, a model trained from scratch, "in which the clock, state slot and certified lookup become native
      architecture".
    - 29 Oct: "We need to make a new kind of model that satisfies my conditions."
11. **The demo freaks out ML-researcher investors, and nothing in it disappoints.** (28 Oct) It runs live, on a laptop
    GPU, in the browser.
    - Demos Neo chose: a huge-number calculator inside the LLM, the ghost Rubik's cube, poke-the-brain, a
      dead-reckoning robot.
    - "Demos that obviously make LLMs smarter and hint at eating Python / Lean / a calculator when scaled."
12. **Budget and pace (via Fable, 29 Oct):** about one week, $1–2k.

## Where the work stands against these (orchestrator, honest)

- **Savant / PROMPTBOX (27–28 Oct):**
  - Meets 1 partly, 3 partly, 5, 9, and 11 partly.
  - Misses 2 (an external clock runs the program), 6 (programs are tables), 7 (each program is its own table) and
    8 (held-out families 2–77%).
- **WEFT as built on 29 Oct:**
  - Meets 5, 6 (on paper), 9 (an untouched model), and fast exact arithmetic.
  - Misses 2 badly: the host runs the algorithm and the model is a certified digit table, which is close to tool
    calling.
  - Also misses 3 (P4 compile KILL: base zero-shot 20/88), 10 (no new model) and 8.
  - The orchestrator let the "no training this week" plan shrink the dream. That was a mistake to own.

## Meta-goals (Neo, 30 Oct 2026, added by Fable)

- "it is not a breakthrough. it becomes one once it is amazing at generalization. like it has intelligence."
- "certified compute when cleverly mixed and interleaved with chain of thoughts and visual reasoning is something smart
  things do." Tool calls and agent harnesses "are not brain-like"; the brain has multiple memory systems, fewer layers,
  is asynchronous, handles multiple streams.
- "I want to work on something that matters. That is beautiful and theory driven and at the same time becomes the
  foundation of my startup ... a successful M&A with a major AI lab."
- "I need to get a few great publications under my belt soon."
Acceptance test for proposals from here on: generality (model writes and certifies its own procedures, decides when to
use the page, grounded in perception), a theory behind it (certifiability; memory systems by certifiability), a checkable
paper soon, and a plausible small-beats-big result.

## Goal reset (Neo, 30 Oct 2026)

"let's set the goal on beating arc, i suppose arc 3 is the most rewarding one. but we are not going to be stuck in a
loop, we will do whatever it takes to beat it. i mean we will be open to try wildly new things. our history is lessons we
have learned and not our prison. i think beating arc is what i can do to survive."
Working method from here: the `unstuck` skill (`.claude/skills/unstuck/SKILL.md`) with ground-truth from
`research/meta/ARC_SOTA.md`; candidates and rounds in `research/meta/INTEGRATE.md`.
