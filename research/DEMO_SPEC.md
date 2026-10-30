# The demo: an LLM that programs itself and runs the program inside

Neo, 27 Oct: "a website where on the left side there is a simple chatbot UI where you write a prompt (you can also
select one of the suggested prompts and modify them before sending) and on the right side you see what can be
visualized from the guts or activations etc of the model that proves the interpreter gets programmed and is running
inside the model, and it eventually answers correctly inside the chatbot. The prompt can be implicit and the model
automatically uses its interpreter capability where it needs to."

## 1. What the visitor sees

**Left, the chat.** A plain chat box with a row of suggested prompts that drop into the box for editing before sending.
The prompts are ordinary questions with long inputs: a 500-swap shell game, a 2,000-move robot on a wrapping grid, "is
this 300-digit number divisible by 7?", a 1,000-character bracket string, two 200-digit numbers to add, a vending
machine story with 800 events, BBH-style items made long. The model answers in words. Under the answer, one quiet line:
"ran a 6-state program over 2,000 events · certified". The base model's answer to the same prompt can be revealed.

**Right, the inside of the model,** replayed in step with the answer:
1. **The program it wrote.** The rules as text and as a small machine diagram (states, arrows labelled by events).
2. **The run.** The input tape with the current event highlighted; an arrow from the executing attention head to the
   program row it is reading at this step; the current state lit in the diagram. Scrubbable.
3. **The state is digital.** The working state, read from the hidden layer, lands exactly on one of the program's
   state codes at every step (a 3-D view of the codes with the state snapping between them, and a margin trace that
   never touches zero).
4. **The certificate.** Before running, every (state, event) step of the program was checked: "48 of 48 steps checked,
   smallest margin 3.1". This is what makes the answer exact for any input length, not just the tested ones.
5. **Poke the brain.** Click any step and force a different state. The model resumes from it and its answer changes to
   exactly what the program predicts from the forced state. Then switch off the executing head: the run breaks. These
   two controls are the proof that the computation happens in the model, not in a picture of it.

## 2. What must exist inside the model for each panel

| panel | needs | evidence type | who delivers today |
|---|---|---|---|
| program | the model compiles a question into a program | output | PROMPTBOX (training) |
| run, row arrow | one head whose attention picks the executed row | mechanism | QINTERP3 (starting) |
| digital state | a snapped state with a fixed codebook | readout, exact | INTERP, REGS (standalone); token-as-snap (Thm 8) |
| certificate | the step factored into a program-independent lookup with a margin | proof | INTERP/REGS certificate |
| poke, ablation | the state is causal; the head is necessary | intervention | to build (QINTERP3 registers it) |
| unprompted use | the model chooses to compile and run | behaviour | PROMPTBOX RL stage (not started) |

## 3. Do we need every ingredient? (orchestrator's first pass, for the design agent to test)

**Needed:** the snap (regeneration onto a finite codebook: INTERP Thm 1, token-as-snap Thm 8), the lookup certificate
(INTERP Thm 2-3, size N*), composition (INTERP Thm 7, REGS R1) for anything bigger than one table, Prop 12 / the
footprint-view rule for training the executor on diverse programs, and an ordinary LLM's ability to write small
programs.

**Not needed for the demo (they belong to the paper's story or to skills trained into weights):** the blindness theorem
(it explains why naive training fails, not how the demo works), the kick and the final loss F (needed when the program
is in the weights; with the program in context the snap does the work), the closure, robust Myhill-Nerode.

**The idea we have not yet applied, and probably the crux:** exactness on programs the model has never seen requires
the executor to be a fixed, program-independent operation with a certifiable margin. A network that "understands" each
program cannot be certified over all programs. So:
- **separate the executor from the program** (the digital abstraction: a fixed machine, programs as data);
- **the expanded table is both the certificate and the executable.** The model writes readable rules, expands them into
  every (state, event) row (PROMPTBOX already writes this as its check table), and each run step is then one lookup:
  find the row that starts with (state, event), copy its result. Nothing is computed per step except the lookup;
- **one certified lookup head does every step of every program**, so the certificate is computed once, from weights;
- **anything with arithmetic or several registers compiles into REGS-style micro-steps** over small fixed tables (digit
  add with carry is 200 rows), so tables never explode.

PROMPTBOX today trains the language model to compute each step from the rules (expressions, conditions), which is a
program-dependent computation; its errors are mostly wrong steps (64 of 128 failures at step 500). QINTERP2 asked
generic adapters to find the lookup and they did not. Both are consistent with the crux above.

**What may need deeper thought:** whether a pretrained transformer can host a certified lookup head with negligible
language cost (QINTERP3 tests 1-2); context drift of the name tokens' representations (certify on balls); whether a
hidden-state run (no tokens appended, cache eviction) is needed for "inside the model", or whether hidden scratch tokens
plus the poke test are convincing; how compile errors are shown honestly (a wrong program run perfectly is a wrong
answer, and the panel shows the program); how the model learns when to compile (supervised implicit prompts, then RL).

## 4. Trace format (what every line of work should emit so the page can replay it)

```json
{
  "schema": "polyformer.trace/0",
  "source": "regs | qinterp3 | promptbox | mock",
  "model": {"name": "...", "adapter": "...", "commit": "..."},
  "host": {"gpu": "...", "cpu": "..."},
  "prompt": "...", "answer": "...", "truth": "...", "base_answer": "...",
  "program": {
    "text": "...", "states": ["left", "middle", "right"], "events": ["LM", "MR", "LR"],
    "start": "left",
    "rows": [{"s": "left", "b": "LM", "t": "middle", "token_pos": [12, 13, 14]}]
  },
  "certificate": {"pairs_checked": 9, "all_ok": true, "min_margin": 3.1, "N_star": 256, "A": 32},
  "input": {"events": ["LM", "LR"], "char_spans": [[120, 122], [123, 125]]},
  "codebook": {"names": ["left", "middle", "right"], "xyz": [[0.1, 0.2, 0.3]]},
  "steps": [
    {"i": 0, "event": "LM", "s": "left", "row": 0, "attn": [[0, 0.98], [4, 0.01]],
     "t": "middle", "margin": 3.4, "xyz": [0.1, 0.2, 0.3]}
  ],
  "pokes": [{"step": 40, "forced": "right", "answer_after": "...", "predicted": "...", "match": true}],
  "ablation": {"head": "L14.H3", "answer": "...", "first_wrong_step": 3}
}
```
A REGS trace adds `pc`, the instruction, and the memory per step. Fields a source cannot fill are omitted, never faked;
the page labels each panel with its source, and mock data is marked as mock on the page.

## 5. Where it runs (Neo decides before anything is public)
A GPU server streaming activations, or the whole model in the visitor's browser on WebGPU (a ~0.5-1.7B model may fit;
"the weights are on your machine and nothing else runs" is itself the strongest no-tool argument). Nothing is published
or deployed without Neo.
