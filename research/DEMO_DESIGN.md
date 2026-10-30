# DEMO_DESIGN: what it takes to build the demo, from first principles

Cursor agent (Opus 5.5), branch `demodesign`, 2026-10-27. Brief: `research/cursor/DEMO_DESIGN_BRIEF.md`; the demo is
`research/DEMO_SPEC.md`. No Modal spend; one local, read-only analysis of PROMPTBOX's saved gate texts
(`research/demodesign/table_vs_run.py`). Status: design. Nothing here is a counted result.

## 0. The answer to Neo's question, in plain words

Yes, we need to think deeper, but the deeper thought makes the build smaller, not larger.

The orchestrator's crux is half right. Certifying exactness on unseen programs is easiest when the execution step is
a fixed operation whose only program-dependence is the table it reads (pinning is a sufficient way to get that, not
the only conceivable one), and the written-out table is what makes the check mechanical: "did the step return the
destination of the row that starts with (state, event)?" needs no understanding of the program. But four things in
the first pass are wrong or missing, and each changes the build.

The honest headline, after both critiques: **the model computes every transition of a table it wrote, the
transition function is exhaustively verified, and an external clock of twenty lines invokes it once per event.** "An
LLM runs programs inside itself" needs that qualification on the page.

1. **The token is not enough of a snap.** In a transformer the state is not only the last state token. It is the
   whole context: every earlier run token, at every position. So emitting the state as a token does not by itself
   stop errors from building up, and Theorem 8(a) as written is false (§5.2). PROMPTBOX is consistent with this: in 13
   of the 51 first wrong steps we could place, the model's own check table had the right row and the run still wrote
   something else (§1.3), though those 13 do not by themselves separate drift from failed lookup (E0b does).
   The fix is to **pin the step**. The step may see only the program and a fresh two-token block, the current state
   and the current event, at fixed positions. Then the step is a fixed finite function of (state, event), and
   Theorem 1 holds exactly, by construction (§5.1).
2. **Once the step is pinned, the demo's certificate needs no weights-level bound.** Checking every (state, event)
   row of this program, one forward pass each, proves the run exact for an input of any length. That needs no role
   additivity, no N*, no balls and no size law. "48 of 48 steps checked, smallest margin 3.1" becomes a theorem about
   this prompt's run, and every step of the run reproduces one certified row's logits exactly. INTERP's weights-level
   certificate (one bound for all programs) is the natural route for the register computer, whose memory makes the
   state space too big to enumerate. That belongs in the second demo.
3. **Moving work to compile time moves the errors there.** In PROMPTBOX's gate runs, when the model's table had a row
   for the first wrong step, the run wrote the table's own wrong value in 38 of 51 cases (the same miscomputation in
   both, not necessarily copying). That is 51 placeable cases out of 125 classified responses in the saved texts; for those
   51, most errors begin when the model computes the rows (mostly modular arithmetic), not when it executes them. A
   perfect executor fixes only the rest. So the program language must keep arithmetic out of what the model computes: tables written as
   literal rules (about 50 rows at most), plus, if Neo allows, labelled library imports (remainders, counters) that
   are checked once, offline, and shown as imports.
4. **Reading the input is a second program-independent operation, and nothing yet certifies it.** Finding the next
   event in a 2,000-event prompt is where PROMPTBOX's runs fail at length (P0: reading errors become total at twice
   the training length;    the gates have 16–19 reading failures in 128 at 2,048 events). The design separates reading
   from stepping and pins reading too. For a list input the model quotes where the events are and the clock walks
   those tokens (exact). For sentence input, each clause is translated to an event name in its own pinned block, so
   translation does not degrade with length. §2.4 gives the options and their honesty costs.

**What the demo is, then.** One Qwen model with one adapter, used three ways:
- it writes a program as a table in the chat, in ordinary decoding;
- it names the input's events (a span quote for lists, a per-clause translation for sentences);
- the same weights then run the table in a pinned execution block, one tick per event.

Before the run, every row is checked by a forward pass. Afterwards, the final state is written back into the chat,
and the model answers in words. Everything is the model's own forward passes plus a clock. Plainly: the model is
the step (the combinational part of the machine); the clock is the latch and the tape head (the sequential part).
It is a loop of about twenty lines that keeps Π's cache, feeds the last state token and the next event token into a
fresh block, takes the argmax and discards the block. A single tick is just an ordinary causal forward of Π‖s‖e on
a reused, immutable prefix cache; no special mask is needed except to batch. The clock is part of the computer: it
stores the state, advances the pointer, routes registers and halts. It chooses no state. That is the one thing a
skeptic must accept, and the page shows it (§7).

**What we can drop.** For the first demo: the size law, the role-split bound, the noise law, the kick, the final loss,
the closure, robust Myhill–Nerode and REGS micro-steps. The blindness theorem stays, as the reason the step must be
pinned (§1.2).

## 1. Ingredients: what is needed and why

### 1.1 Table

| result | needed for the demo? | why |
|---|---|---|
| INTERP Thm 1 (regeneration: snapped run exact iff every reachable one-step is exact) | **yes, core** | It turns a finite check into exactness at every length. It needs the step to be a function of (state, event) alone. Pinning is the simplest way to get that in a transformer (§5.1); a history-invariant decoder would also do, but nothing gives one for free |
| SI S5 (enumeration) / S6 (a certificate must read the readout) | **yes** | The demo's certificate is S5 in its plainest form: evaluate the argmax at every row. S6 is why a certificate has to look at logits and cannot rest on text the model writes about itself (§1.3) |
| INTERP Thm 2 (four situations, factorised bound), Thm 3 (size law), N*(A) | **not for demo 1**; needed for demo 2 (REGS) | Pinned enumeration is cheaper and exact for the small programs of demo 1. A bound for all programs is needed only when the state includes a memory too large to enumerate. In a host model it also needs a perturbed form (§5.3), and QINTERP2 found the host's scores far from role-additive (fit residual 0.66) |
| INTERP Thm 4 (identity path; overwrite vs residual tick) | design guidance only | With a token snap, exactness does not depend on contraction. Thm 4 explains why free (unsnapped) variants drift |
| INTERP Thm 5 / REGS R2 (noise law, one-factor form) | optional panel | A noise slider on the state slot whose survival follows the closed form would be a striking extra. It is not needed for any claim |
| INTERP Thm 7 (composition), REGS R1 | **yes, Thm 7**; R1 for demo 2 | Several registers run as one block per register, each seeing only its declared inputs. Each block is enumerated, and Thm 7 composes them (§5.1, Cor. P3) |
| INTERP Thm 8 (token is the snap) | **yes, corrected** | As stated, (a) and (b) fail (§5.2; THEOREMS.md's reader flagged the same). The corrected form is Theorem P |
| INTERP Prop 6 / footprint–view rule (MULTI) | **yes** | Training the executor on random tables with random names puts every row situation in the view, which is why it should run unseen programs. Pinning makes the test-time step context the same as the training context, which is the footprint–view rule satisfied by construction |
| Paper Thm 1(a) (blindness) | **yes, as the design reason** | Without pinning, a step at position 30,000 after 2,000 run steps lies outside any training view, and training cannot constrain it. That is the mechanism behind the 13 contradicted rows. Pinning removes the gap instead of trying to train across it |
| Robust Myhill–Nerode, centred closure, aimed tube, final loss F, kick | no | They train discrete state into weights. Here the state is a token and the program is data |
| THEORY4 push window, LEAP erasure | no | The snap is exact, so there is nothing for them to do |
| DIAG ten-skill model | no (contrast) | Skills in weights are exact on fixed tasks. Its weakest task was "programs" (364 of 512 at 4,096), the case the demo has to make general |
| QINTERP v1 (side head on input embeddings, everything passed) | evidence that the lookup is easy to learn | Rejected as "outside the model". The design here keeps Qwen's layers in the loop |
| PROMPTBOX: program language, families, phrasings, RL, scoreboards, audit | **yes: compile, reading, unprompted use** | Its interleaved run is replaced by the pinned table executor |
| An ordinary LLM's ability to write small programs | **yes, and it is the main risk** | §1.3: most step errors start at compile time |

### 1.2 Testing the crux: "separate a fixed, certified executor from the program; the expanded table is both the certificate and the executable"

- **Right:** certified exactness on unseen programs is cleanest with an executor whose only dependence on the
  program is the table it reads (sufficient, not logically necessary: Codex). A table makes the
  check syntactic: the step is right if it returns the destination of the row whose (state, event) match, and anyone
  can check that by string comparison. Without the table, checking a step means interpreting the rules, which means a
  second interpreter outside the model.
- **Wrong, 1: "the expanded table is the certificate."** The table is the *specification*, not the certificate. The
  certificate is a measurement of the model's step against that specification at every row, and it is sound only if
  the step that runs later is the same function that was measured. In a transformer it is not, unless pinned.
  INTERP's lookup ran in a clean context. A host decoding a long run does not.
- **Wrong, 2: "one certified lookup head, certified once from weights, does every step of every program."** It is not
  needed for small programs, and in a host it is hard: the score has cross-terms, context and position terms, and its
  readout passes through more layers. Demo 1's certificate is per prompt, exhaustive and exact. For demo 2 the
  weights-level form, with the perturbation lemma of §5.3, is the natural route, not a mathematical necessity.
- **Missing, 1:** reading. The executor needs an event per tick. Where that event comes from is the other half of a
  machine, and it is where long runs fail today.
- **Missing, 2:** compile errors dominate. A wrong table run perfectly is a wrong answer. The design has to shrink
  what the model computes at compile time.

### 1.3 Evidence from PROMPTBOX's gate texts (read-only, uncounted)

PROMPTBOX stage (a), gate G-a: held-out random programs at 2,048 events, n = 128 per checkpoint. The summary numbers
are from its rescored records. The table-versus-run split is from `table_vs_run.py`, run on the 64 saved texts per
checkpoint. It reuses PROMPTBOX's parser, and its run-token split is a regex approximation of the tokenizer's.

| checkpoint | exact runs | first errors: step / reading | wrote "certified" | check table right | certified and wrong |
|---|---|---|---|---|---|
| seed 1, step 500 | 21/128 | 64 / 19 | 128 | 86 | 72 |
| seed 2, step 500 | 31/128 | 55 / 30 | 128 | 83 | 64 |
| seed 1, step 1,000 | 62/128 | 42 / 19 | 128 | 100 | 40 |
| seed 2, step 1,000 | 55/128 | 50 / 16 | 128 | 97 | 48 |

First wrong step against the model's own table row for the same (register, dependencies, event), pooled over the four
checkpoints' saved texts:

| outcome | count |
|---|---|
| the run writes the table's own wrong value | 38 |
| the table row is right and the run contradicts it | 13 |
| no matching row (a big register with spot rows only, or my key lookup missed) | 29 |
| run value unreadable | 2 |
| not parsed (unclosed run or table, usually the token budget) | 43 |

Three readings, each with a design consequence:
1. **The model's self-check does not transfer to its own errors.** PROMPTBOX trains it: 15% of examples plant wrong
   rows and target `not certified`. Yet on its own tables it wrote "certified" on 128 of 128 at every checkpoint,
   including the 28 to 45 responses whose table was wrong. Whatever it learned from planted errors did not transfer
   to its own. The demo must never show model-written ✓ marks as the certificate; the certificate is computed from
   logits (§2.5).
2. **Of the errors we can place, most start in the rows.** In the 38, the table and the run carry the same wrong
   value: a shared miscomputation (which may be recomputed twice rather than copied). Many sit on `digits` programs
   with modular expressions, where the table was right in only 7 of 17 at step 1,000. A better executor does not fix
   these. Keeping arithmetic out of the model's compile step does. This is conditional on the 51 placeable cases of
   125; the other 74 cannot be attributed.
3. **Execution is not reliably the table's.** In 13 cases the run contradicts a correct row. Growing-context drift is
   one explanation, which pinning removes; failed lookup, a reading error or format confusion are others. E0b
   separates them. The 29 big-register cases are arithmetic computed on the fly with no row at all, which library tables
   remove.

## 2. The architecture (one model)

### 2.1 The flow

```
chat context (ordinary decoding, chat template, greedy)
  user: "Three cups, ball under the left one. Swaps: LM MR LR MR ... (500)"
  model: <program> states: left middle right · events: LM MR LR · start: left
           rows: left LM middle | left MR left | ... (9 rows) </program>
         <events from="Swaps:" to="(500)"/>               ← the model quotes the span (R2; sentences use R1p)
         <exec/>                                          ← model-emitted token; the clock takes over
execution context (same weights, pinned)
  prefix  Π = the table rows only, encoded in isolation (no chat, no input)
  certify: for every (s, e) ∈ S × B: one forward of the block [s][e] on Π → argmax, margin
  run:     s_0 = start; for e_i in tape: s_i = argmax M(Π; [s_{i−1}][e_i])
chat context again
  harness appends  <final> right </final>  (the last state token, a token the model itself emitted)
  model: "The ball is under the right cup."     · ran a 3-state program over 500 events · certified
```

### 2.2 Where each thing lives

| thing | where | visible to the visitor? |
|---|---|---|
| program (rows, optional rule text) | tokens in the chat context | collapsed ("show program") |
| tape | the user's own tokens in the quoted span (R2), or one event token per clause from pinned translation blocks (R1p) | collapsed ("show tape"), aligned to the prompt |
| state | one token per tick, emitted in the execution context; between ticks it exists only as that token id | panel 2, 3 |
| the step's working state | the residual stream at the block's event position (the second token), at every layer; the first position cannot see the event | panel 3 (projection) |
| the lookup | attention from the block onto Π's rows | panel 2 |
| certificate | logits of the \|S\|·\|B\| certification blocks | panel 4 |

"Inside the model" is about hidden scratch tokens and a pinned context. No hidden-state injection is involved. A
vector-quantised hidden state fed back inside the layers would be the same mathematics (Theorem 8's emission is a
snap), would cost the auditability of ordinary token decoding, and adds no evidence. QINTERP2 also showed it is
harder to train (0 of 32 at its gate). Recommendation: tokens in a pinned block, kept out of the visible chat,
shown in the panels, plus the causal tests of §3. That is convincing to a skeptic, and more so than a custom
latent loop, because every step is an ordinary forward pass that anyone can replay.

### 2.3 The step and the snap

- Π is the program's table rows, written by the model, re-encoded alone as a fresh context: positions 0…|Π|−1, no
  chat, no input. The harness copies the model's own row tokens byte for byte; it chooses no state.
- A tick is a two-token block, [s_{i−1}][e_i], at fixed positions |Π| and |Π|+1, attending to Π and within itself.
  The block is discarded after the argmax.
- The snap is the argmax of the language-model head at the block's last position (the event position; the state
  position cannot see the event). Recommended: argmax over the full vocabulary, so the certificate covers
  unconstrained output. An argmax restricted to the program's state names certifies constrained decoding only, and
  the page must say so. The emitted token id is the next tick's s_i.
- The adapter must be active on the whole execution context, Π and the block. The first draft gated it to the two
  block positions only, which freezes Π's keys and values at the base model's: the lookup could then only learn a
  query against whatever base Qwen happens to put at the row tokens (Gemini). E1 tests both arms.
- One adapter, trained on chat, compile, tape and execution examples, active everywhere. "One base model, one
  low-rank adapter" is then literally true, and its language cost is measured by PROMPTBOX's P13 bar. The first
  draft's "chat logits are bitwise the compile model's" claim needed two adapters switched by a tag, which reads as
  two models orchestrated by a script, so it is dropped. Fallback if one adapter cannot hold both: two adapters,
  stated on the page.

Information flow (proof in §5.1): the block's residual at every layer depends only on Π, s_{i−1}, e_i and the fixed
positions. So tick i computes F_Π(s_{i−1}, e_i) for one fixed function F_Π. The run cannot drift, because nothing
carries over between ticks but a token.

### 2.4 Reading: three tiers, chosen per prompt family

| tier | who finds event i | exact by construction? | skeptic cost |
|---|---|---|---|
| R0, plain decoding (PROMPTBOX today) | the model, in an interleaved run | no; fails at length (P0, gates) | none |
| R1, the model writes a contiguous tape; the clock walks it | the model, while writing the tape (a contiguous copy or translation) | no, but a contiguous copy is the task LLMs do best, and it is checkable against the prompt | the clock walks the model's tape |
| R1p, sentence inputs: the clock splits the input on clause delimiters; each clause is translated to an event name in its own pinned block (program header, clause) | the model, one clause at a time | no, but length-free: each clause sees the same context at every length, by the argument of Theorem P | the clock splits on punctuation; translation is measured, not certified |
| R2, list inputs: the clock walks the prompt's own event tokens from a span the model names | the clock | yes, given that the model chose the right span and every token in it is in B (the clock rejects any that is not) | the clock walks the user's text, from a marker the model quoted |

Recommendation (revised after Gemini): **R2 for list inputs** ("swaps: LM MR LR …", bit strings, moves), **R1p for
sentence inputs** ("First, Alice and Bob swap balls. Then, …"), and a contiguous tape (R1) only for short inputs.
The first draft made R1 the default; that was wrong twice. Rewriting a 2,000-event list costs more decoding than the
run itself and cannot reach 10⁴ events within an output budget. And its supporting argument, that an induction head
copies a contiguous tape better than an interleaved one, fails on these alphabets: with 3 event names, every 5-gram
recurs about 8 times in 2,048 events, so matching the preceding tokens does not locate the next event. Copying needs
positional indexing either way, which fits PROMPTBOX's chunked format doing *worse* than interleaved (P0f). The
argument is withdrawn. Turning a sentence into an event name is reading comprehension, the model's job, so R1p keeps
it with the model while removing length. Translation accuracy per clause is gated (G2) and shown: the tape panel
aligns each event with its source span, and a translation error is shown as one, not hidden in the run.

### 2.5 The certificate

For a program with state set S and alphabet B (the tape's event names, a finite set by construction), compute
F_Π(s, e) and its margin for all |S|·|B| pairs: one batch-1 forward each over the cached Π, on the run's code path
(Cor. P2).
- **Pass** if, at **every** row of S × B (not only the reachable ones, so the harness needs no graph search), the
  argmax token id equals the destination token id written in that row of Π, and every margin is strictly positive.
  The comparison is a disclosed string match of row text; it is the referee, like a unit test's expected value, and
  the answer is never taken from it. Report "|S|·|B| rows checked, smallest margin m".
- By Theorem P, the run on this prompt is then exact for a tape of any length. Panel 3 shows each tick's logits equal
  to its row's certified logits (equality on the same host and code path, not a tolerance).
- Scope, stated on the page: the certificate covers execution of this table. It does not cover the table's fidelity
  to the question (compile) or the tape's fidelity to the prompt (reading). Both are shown and scored separately.
- Cost: 9 rows for the shell game, 100 for the 5 × 5 robot, 70 for divisibility by 7 (a library table), 62 for one
  bracket type to depth 30 (a counter). Unbatched on a cached prefix, a few seconds on a server GPU; tens of seconds
  in a browser. Tables are capped at 256 rows, the size the executor is trained and gated on (G1).
- "Brackets" means one bracket type, a bounded counter. Several bracket types need a stack, whose states cannot be
  enumerated (k^depth); that is a REGS program, demo 2. The page says which.

### 2.6 Arithmetic and several registers

- **Literal tables, at compile time, up to about 50 rows.** The model writes rows that need no arithmetic:
  permutations ("left LM middle"), mode switches, and ±1 on small ranges written out. Writing 200 counting rows in a
  chat is not something a sensible assistant does, so larger or arithmetic tables, such as (10r + d) mod 7, come from
  **library tables**: constant, generated and checked once offline, named in the program (`use remainder 7`).
- **Library tables are imports, and the page says so.** A skeptic will rightly call `use remainder 7` a tool call:
  the model chose a table that a person wrote. Its rows still run on the model's executor and are certified the same
  way, but "the model wrote this program" is then false for those rows. The page labels imported rows, and whether
  demo 1 uses imports at all is Neo's decision (§7). Without them, demo 1 is the literal families only. In
  PROMPTBOX's language, `digits` and big-register programs are exactly where the rows are wrong today (§1.3).
- **Several registers:** independent registers only in demo 1 (Cor. P3, narrowed). The 7 ball registers of BBH
  tracking with one shared `each` table cost 7 × 21 = 147 certified rows in all. A small product (the 5 × 5 robot) runs
  as one register of 25 states.
- **Streaming arithmetic with an output tape** (adding two 200-digit numbers) is dropped from demo 1 (Cor. P4).
  Divisibility, a DFA whose answer is the last state, stays.
- **REGS micro-steps** are for programs with memory (multiply, sort, GCD), whose state cannot be enumerated. They need
  the weights-level certificate in the host (§5.3, QINTERP3). That makes them demo 2, not demo 1.

### 2.7 Unprompted use and language cost

- The model decides by emitting `<program>`. After it emits `<exec/>`, the clock runs. Training: PROMPTBOX's bare
  questions (supervised) for the families, then GRPO with a verifiable reward. Nothing changes except the target
  format.
- Language cost: one adapter (§2.3), held to PROMPTBOX's registered bar (P13: perplexity ratio under 1.2, MMLU
  within 3 points, GSM8K within 5), measured with the execution data in the mix.

### 2.8 Where it runs (Neo decides)

Each tick is a two-token forward on a cached prefix. Rough guide, not measured: on a laptop GPU through WebGPU, a
0.6B–1.7B model at about 4 bits should do tens of ticks per second, so 2,000 ticks would take about one to two
minutes. A server GPU does it in seconds. The browser version has the stronger story ("the weights are on your
machine"), and it lets the visitor's own machine recompute the certificate. Custom masks and fixed position ids are
simple on a server (Hugging Face 4D masks, `position_ids`). A browser runtime would need the block forward exposed,
which is a risk (§6).

## 3. Each panel: evidence, causal test, and what a skeptic still says

| panel | evidence | causal test (registered number, to be fixed by whoever runs it) | what a sharp skeptic still says | answer |
|---|---|---|---|---|
| 1 program | the rows and the diagram, from the model's text | **row edit**: change one row in Π (destination t → t′) and rerun; the run must follow t′ at every visit, ≥ 99% of 200 edits | "The program could be wrong." | Yes. Compile accuracy is reported per family, and the page says "certified execution of this program", not "certified answer" |
| 2 run, row arrow | the lookup head's attention from the block onto the row whose (s, e) match | **path patching**: swap the attended row's destination token's value → output follows; **head ablation** → first wrong tick within 3 ticks in ≥ 95% of runs, against controls (ablating a random head of the same layer; matched activation replacement), and **selectivity**: editing one row changes only ticks that visit it. Ablation alone shows necessity, not lookup | "Attention is not explanation." | That is why patching and ablation sit next to the arrow. If no single head carries the lookup, the panel shows attribution over heads and says so |
| 3 digital state | the event position's residual projected onto the span of the unembedding rows of the program's state tokens (what the readout can see of each state); the margin per tick, never below the certified minimum | **logit identity**: each tick's logit vector is equal to its certified row's (exact equality, 100% of ticks, same host and code path, Cor. P2; a tolerance such as 10⁻³ would be meaningless in bf16, where one unit in the last place at 16 is 0.125) | "Every classifier has a margin." | The point is that the margin is bounded below for every length by a finite check, and the identity shows the run is the certified function |
| 4 certificate | \|S\|·\|B\| forwards, min margin | soundness test: every certified run on fresh inputs at 10⁴ events is exact (a single failure is a bug, Thm P) | "Only as good as the pinning; it says nothing about compile or reading." | True, and the page says so. Those are scored separately (G2, G3) |
| 5 poke, ablation | force s at tick k; resume | **poke**: 200 of 200 runs follow the program from the forced state, *and the chat answer changes to the predicted one*, using only pokes whose trajectories end in a different final state (states can merge), and **conflict pokes** where the forced final state contradicts what the prompt implies, so a parallel route through the prompt would show; the certificate covers every state, so forced states are covered; **ablation**: executor adapter off, or Π removed → run fails | "Pokes are implied by the certificate." | For the run, yes. The poke's value is the last step: the answer depends on the machine and not on a parallel route through the input |
| clock | the 20-line loop, shown | audit: no network or subprocess; the loop never reads the program's rows (only the certifier's string match does); the run equals a bare-loop replay token for token | "Your loop is the interpreter: it owns all control flow, and your certifier already parsed the table, so why run the model at all?" | Half true, and the page says so: the clock is the sequential half (latch, tape head, halt), the model the step. The certifier's string match is the referee, not the source of the answer; the run's answer comes only from argmaxes. The demo's claim is that the model's own forward pass executes an unseen table exactly, and the string match is how a visitor checks it. A plain-decoding mode (R0) runs alongside |

## 4. Training plan

### 4.1 Cheapest decisive experiments first (for PROMPTBOX and QINTERP3 to run; no spend here)

| id | what | cost | decides |
|---|---|---|---|
| E−1 | **Systems check first, base model, hand-written tables** (Codex): implement certification and replay on the run's code path; then deliberately vary prior history, cache reuse, batch neighbours and invocation order, and confirm every tick's logits are unchanged | laptop-scale or ≪ $1 | That Theorem P's hypotheses hold in the actual runtime (no leakage, determinism), before any training is interpreted |
| E0a | **Row edit on PROMPTBOX's existing adapters** (step 1,000/1,500): in 64 gate prompts, change one row of the model's own check table in context and regenerate the run | inference only, ≪ $5 | Does today's run read its table (follows the edit) or recompute from the rules (ignores it)? It bears on how far R0 is from a certifiable executor; it cannot settle whether R0 could ever be certified |
| E0b | **Pinned evaluation of the same adapters, in PROMPTBOX's native format**: the context is the original prompt, program and check table, then `<run>` and only `s_{i−1} e_i` in PROMPTBOX's own token order, with no earlier run tokens; read the next state at each step's position | ≪ $5 | How much of the step error is accumulated run context (removing it fixes it) and how much is rows (it stays). A bare Π with an `[s][e]` block would be out of distribution for these adapters and would say nothing (Gemini). Even in native format, a run with no history is still a shift for these adapters, so a failure is weaker evidence than a success (Codex) |
| E0c | **Reading baselines, base model**: Qwen3-1.7B and 4B, no training, at 256/1,024/2,048 events, n = 64 per cell: R1 (contiguous tape), R1p (pinned per-clause translation) on sentence families, R2 (span quote) on list families | ≈ $3 | Which reading tier each family uses, and whether it needs training |
| E1 | **Pinned executor pilot**: first verify that every pool name is one token in both block and row context (H1). Then overfit one fixed table (teacher-forced one-step accuracy must reach 100%). Then one seed, two arms: LoRA on Π and the block (A), LoRA on the block only (B). Random tables (N 2–32, A 2–8, up to 256 rows, 288-token pool, 64 tables a batch with 16 blocks per table, block-diagonal mask), 1,000–2,000 steps; held-out tables with renamed symbols and shuffled row order | ≈ $5–8 | Can Qwen's layers learn the pinned lookup, and does Π need the adapter? Go if arm A has ≥ 95% of 128 held-out tables whole-table exact (every row), reported by size bin up to 256 rows; no-go below 50%. Whole-table, not per-row: 99.9% per row would be only about 77% of 256-row tables if rows failed independently (0.999²⁵⁶ ≈ 0.774) |

### 4.2 Stages and gates (n = 512 per length unless stated; Clopper–Pearson intervals)

| stage | data | gate |
|---|---|---|
| 1 executor | pinned blocks on random tables up to 256 rows, rows in PROMPTBOX's row format and the pipe format; names from a single-token pool, train and test pools disjoint; adapter on Π and block | **G1**: on 512 held-out tables with N ≤ 32, A ≤ 8: certificate acceptance (whole table exact, all margins > 0) ≥ 99% (lower bound ≥ 98%), reported by size bin; smallest margins reported as a distribution, not gated (a raw logit margin has no universal scale); zero inexact 10⁴-event runs on accepted tables (a bug otherwise) |
| 2 compile | PROMPTBOX families with the program written as literal rows (≤ 50), plus imports if Neo allows them; held-out phrasings and families | **G3**: table correct (every row) ≥ 95% on training phrasings, ≥ 85% on held-out phrasings, per family; held-out families reported |
| 3 reading | R2 span quotes for list families; R1p per-clause translation for sentence families, to 2,048 events | **G2**: span exact ≥ 99.5% (R2); clause translation such that the whole tape is exact ≥ 99% at 1,024 and ≥ 97% at 2,048 (R1p), per family; families that miss are dropped from the suggested prompts |
| 4 loop | end to end, on a **fresh** test set drawn after families were dropped at G2 and G3 | **G4**: answer ≥ 95% at the demo's lengths per suggested prompt, measured directly (the stage gates do not imply it: 0.95 × 0.97 × 0.99 ≈ 0.91 even if independent, and the verbal answer is one more failure point); the §3 causal tests at their numbers; logit identity 100% |
| 5 RL | PROMPTBOX's GRPO, executor frozen | unprompted use and held-out families as PROMPTBOX registered; G1 re-run after RL |

Rough cost: E0–E1 ≈ $10; stage 1 at 3 seeds ≈ $30; stages 2–3 are PROMPTBOX's stage (b+c) with a new target format;
evaluation ≈ $30.

### 4.3 What PROMPTBOX and QINTERP3 should change (they keep running; I edit nothing of theirs)

**PROMPTBOX**
1. Report P7 as measured: "certified" was written on 128 of 128 at every gate, while the table was right in 83 to
   100. Score a logit-based certificate instead (E0b's pinned row check) and never present the text mark as a
   certificate.
2. Run E0a and E0b on the existing adapters before stage (b+c) ends. Both are inference only.
3. In stage (b+c) and after: keep arithmetic out of rows the model computes. Big registers and `digits` expressions
   are where the tables are wrong. Replace them with library tables, or restrict the suggested demo prompts to
   families whose rows are literal.
4. Measure reading on the families as a separate suite (E0c: span quote, per-clause translation, contiguous tape):
   the interleaved copy is the length bottleneck.
5. Fix one leading-space convention for names and check that every name is a single token in every context (H1).

**QINTERP3**
1. Post-mortem hint from QINTERP2's record: it trained 800 steps on batches of 8 sequences (6,400 in all, 110 s),
   against INTERP's 384,000 tables. Cross-entropy ended at 2.0, close to the 2.04 of uniform guessing among a
   table's names (the mean of ln N over N = 2…16). That is consistent with no learned lookup, though not proof of it,
   and it suggests the run says little about the architecture. First check that one-step teacher-forced accuracy rises
   on a single fixed table, then scale to INTERP's batch.
2. Add the token-emission pinned block (E1) as an arm beside the layer-12 injection. It is the demo's mechanism, it
   needs no custom latent loop, and its certificate is exhaustive per program.
3. For a weights-level certificate (one route for REGS, not the only one), the cleanest host placement is a lookup
   head after the last block, before the final RMSNorm. The norm divides by a positive scalar that depends on the
   head's output and multiplies by a learned gain γ. So the sign of each gap is that of (U_t − U_m)·D_γ·x, and §5.3's
   bound applies to that unnormalised numerator with γ absorbed into the readout. The normalised gap itself is not
   additive (Codex). Measured ε and η over sampled contexts are evidence, not a certificate over all contexts.

## 5. Theory

New theory is needed, but it is small: Theorem 8 has to be replaced by a statement that is true in a transformer.

### 5.1 Theorem P (pinned regeneration)

**Setting.** A decoder M with causal attention. A prefix Π (token sequence). A tick is a block of two tokens
(s, e) at fixed position ids (|Π|, |Π|+1), in which the first may attend to Π and itself, and the second to Π, the
first and itself. Let F_Π(s, e) be the argmax of M's logits at the second position, and μ_Π(s, e) the gap between the
largest and second-largest logit. A run on a tape e_1 … e_T from s_0 sets s_i = F_Π(s_{i−1}, e_i), each tick in a
fresh block.

**Hypotheses** (the first draft left them implicit; Gemini's critique, §8).
- (H1) Every state name in S and event name in B is a single token, and it is the same token id in the block as in
  Π's rows. In Qwen's byte-level BPE, `left`, ` left` and `|left` are different ids, and `r3c4` is several tokens.
  So the program language fixes one leading-space convention and draws names from a pool of verified single tokens.
  The page states it.
  Distinct names have distinct ids (the encoding is injective), and δ: S × B → S is total and well formed: exactly
  one row per pair, every destination in S. The certifier rejects duplicate or missing rows, invalid destinations,
  ambiguous names and tape symbols outside B.
- (H2) The margin is strict, μ_Π(s, e) > 0, at every pair checked, so F_Π is single-valued. A tie fails
  certification.
- (H3) The forward pass is a deterministic function of its inputs with no other mutable state: fixed weights and
  adapter, fixed mask and position ids, an immutable prefix cache, and certification and run on the same kernels,
  dtype, quantisation and batch shape (Cor. P2). Causal attention alone does not supply this; the runtime must, and
  E−1 tests it.

**Statement.**
1. Tick i's logits are a function of (Π, s_{i−1}, e_i) only. They do not depend on i, T, earlier ticks, or anything
   outside Π.
2. Let δ be the table Π encodes. The run equals δ's run on every tape of every length over B, from s_0, if and only if
   F_Π(s, e) = δ(s, e) for every (s, e) reachable from s_0 under δ over B. Checking all of S × B suffices.
3. Each tick's logit vector equals that of its row's certification block, exactly in exact arithmetic.

**Proof.** (1) Write h_ℓ(p) for the residual at layer ℓ and position p. By induction on ℓ, h_ℓ(p) is a function of
the tokens and position ids of the positions p can attend to, and of their residuals at layer ℓ − 1. Π's positions
attend only within Π, so their residuals are fixed by Π. The block's first position attends to Π and itself, so its
residuals are functions of (Π, s). The second attends to Π, the first and itself, so it is a function of (Π, s, e).
The position ids are the same in every tick. Nothing else is visible. (2) Induction on i, as INTERP Thm 1(i): if
s_{i−1} is right, then s_i = F_Π(s_{i−1}, e_i) = δ(s_{i−1}, e_i), and every pair the induction visits is reachable.
Conversely, take a reachable pair with F ≠ δ and a tape that reaches it under δ, then applies its event: either the
run has already diverged on that prefix, or it diverges at that pair. (3) The same function on the same inputs. ∎

The statement holds at every finite length, as long as the clock keeps operating correctly. It is a theorem about a
program-conditioned executor F_Π; it does not say the executor is program-independent, only that its dependence on
the program is through Π alone.

**The certificate's contract.** A certificate is bound to: the exact token ids of Π, the weights and adapter (hashes),
the tokenizer, the output set of the argmax (full vocabulary or constrained), the mask, the position ids, the cache
policy and the runtime configuration. Any edit to Π invalidates it. The page reports both how often certification
accepts and how often accepted runs are correct (the latter must be 100%, or something is a bug).

**Corollary P2 (floating point).** Floating-point evaluation is a deterministic function of the inputs *and* the
code path (kernel choice, tile sizes and reduction order depend on batch shape). So the theorem holds bit for bit
only if certification evaluates each row exactly as a tick does: one block of batch 1 over the same cached Π, the
same kernels and dtype. Then each tick's logits are *equal* to its row's certified logits, and the check of panel 3
is equality, not a tolerance. Certifying in one big batch is faster but is a different function; its agreement with
the run would need an ℓ∞ bound τ on per-logit differences (argmax agreement where μ > 2τ, since each of the two
logits in the gap can move by τ), and τ can only be measured by running both paths on every row, which is the
unbatched certification anyway. So certify unbatched: about 300 two-token forwards on a cached prefix, a few seconds
on a server GPU. Never claim agreement across hosts or code paths (COMMON).

**Corollary P3 (registers), narrowed.** With one block per register per tick, each seeing Π, its own previous value,
the event and the declared values of the registers it reads (all as fresh tokens), each register's step is a fixed
function of those inputs. If the wiring is a cascade (register j reads only registers < j, as the new values of that
tick, or any registers as the previous values), then enumerating each register's own (inputs, event) set certifies
the whole machine at every length (induct over ticks, then over the cascade order within a tick). This is INTERP
Thm 7, with exact routing supplied by the clock, which is real controller work: old and new values, fixed input
order. The certification cost is Σ_j |B|·|S_j|·Π_{k∈D_j}|S_k| over registers j with read sets D_j, not the sum of
register sizes. Two costs the first draft hid: a register that reads d others needs a block of d + 2 tokens (plus a register-name token if registers share a
vocabulary), so the executor must be trained on that arity; and its table has N^{d+1}·A literal rows. **Demo 1
therefore uses only d = 0:** independent registers (the 7 balls of BBH tracking, each a 2-token block over the
same `each` table), or a small product run as one register (the 5 × 5 robot, 25 states). Cascades are demo 2.

**Corollary P4 (outputs per tick).** Theorem P(2) makes the whole trace s_1 … s_T equal δ's trace, not only s_T. So a
Mealy machine can be run as a Moore machine whose states are (state, output) pairs, and its output tape is a
projection of the certified trace. For add-with-carry that is 20 composite states over 100 digit-pair events, 2,000
rows, too many to write or certify cheaply, and the operand alignment is a reading problem. **Addition is dropped
from demo 1.** Divisibility (remainder mod 7, a DFA whose answer is s_T) stays.

**Remark (what P does not say).** It says nothing about Π matching the question, or the tape matching the prompt.
It is a theorem about the executor on the program the model wrote.

### 5.2 Theorem 8 as stated is false, and why

INTERP Thm 8(a) says that emitting the state token makes Theorem 1 hold: "errors cannot accumulate". **Counterexample.**
- Machine: two names u, v, one letter a, δ(u, a) = u, δ(v, a) = v, start u. The right run writes `a u a u …`.
- Decoder: the logits at a run position are L(s, e) plus one attention head's write. L is the correct lookup, with
  L_u − L_v = R > 0 at (u, a).
- The head: score c on a sink token at position 0 and score 0 on every other earlier position. Its value is β on v's
  logit for an `a` token and 0 otherwise.
- After n run tokens, half of them `a`, the head's weight off the sink is n/(n + e^c). So it adds
  β(n/2)/(n + e^c) to v's logit.
- With β = 4R, that push is below R for n < e^c and above it for n > e^c.

So the run is exact up to about e^c tokens and wrong after, although every emitted state is an exact name. The token
snapped the state but not the context. The context is a second state, unsnapped and growing, and Theorem 1 does not
cover it. In a pinned block the head sees no run tokens. Its push need not be 0, since Π's rows contain `a` tokens
too, but it is the same at every tick for a given (s, e), so it is part of F_Π and the enumeration either passes
with it or fails (Codex corrected the first draft's "the push is 0"). The construction is idealised: real prefix
tokens and the block's self-attention change the counts, not the conclusion.

Thm 8(b), that the host's lookup is role-additive, is an empirical property of a head. QINTERP2 measured a fit
residual of 0.66 at layer 15. So it has to be engineered or bounded (§5.3); it cannot be assumed.

### 5.3 Lemma Q (the factorised bound under perturbation), for demo 2

Setting as INTERP Thm 2, with the readout linear in the attention output (for example a head after the last block,
before the final RMSNorm, which does not change the argmax). Suppose every row score is σ_r = σ⁰_r + ε_r with σ⁰
role-additive and |ε_r| ≤ ε, and every push is P_r = P⁰_r + u_r with |u_r| ≤ η, where ε and η absorb cross-terms,
context and position terms. Let XY = Σ_r e^{σ⁰_r − σ⁰_{r₀}} over the table, R₀ = P⁰_{r₀} the matching row's unperturbed push, and
Ω ≥ −min P⁰ over every non-matching position the head attends to, row or not. Let Z₀ ≥ Σ_{p ∉ rows}
e^{σ_p − σ_{r₀}} bound the attention mass on positions that are not row destinations (keys, delimiters, the sink,
the block itself), measured over contexts, or Z₀ = 0 if the head is hard-masked to destination positions. Let g_I be
a lower bound, over the contexts considered, on the logit gap that the residual stream contributes without the head.
If R₀ + Ω ≥ 0, then

  ℓ_t − ℓ_m ≥ g_I + w·(R₀ + Ω) − Ω − η, with w = 1/(1 + e^{2ε}(XY − 1) + Z₀).

**Proof.** For rows, w_r/w_{r₀} = e^{σ_r − σ_{r₀}} ≤ e^{2ε} e^{σ⁰_r − σ⁰_{r₀}}; for other positions the ratios sum to at
most Z₀. So 1/w_{r₀} ≤ 1/w, i.e. w_{r₀} ≥ w. The margin is g_I + Σ_p w_p P_p ≥ g_I + w_{r₀}(R₀ − η) − (1 − w_{r₀})(Ω + η)
= g_I + w_{r₀}(R₀ + Ω) − Ω − η. This is non-decreasing in w_{r₀} because R₀ + Ω ≥ 0, so w_{r₀} may be replaced by
w. ∎ (The first draft omitted Z₀, which made the bound false for an unmasked head, and kept η inside the slope,
where it cancels; both from Gemini, checked.)

**Caveat on g_I.** Before the final RMSNorm the residual has a large norm and strong token preferences (closing tags,
punctuation), so g_I over all m ≠ t can be large and negative. A host certificate then needs either a readout
restricted to the program's state tokens (stated on the page), or an executor trained to suppress the residual's
own preference at block positions, with g_I measured.

The bound must hold for every competing output m (R₀, Ω, η and g_I are per pair (t, m)). With
XY ≤ (1 + X⁺_{N−1})(1 + Y⁺_{A−1}) as in INTERP, this gives a certified size under bounded non-additivity, with the
leak entering exactly as 1 + e^{2ε}(XY − 1) + Z₀. Inflating the two factorised terms separately would change the
cross-term and give a different, looser bound. The quantities to measure in a host are ε, η and Z₀ over the contexts
the head meets; measured over samples they are evidence, and a certificate over all contexts is the open problem
demo 2 still has to solve.

### 5.4 What carries the demo's claims

| claim on the page | carried by |
|---|---|
| "this run is exact, at any length" | Theorem P (2) + the certificate (S5 enumeration) |
| "48 of 48 steps checked, smallest margin 3.1" | Theorem P (2), Cor. P2 |
| "each step reproduces a certified row" | Theorem P (3) |
| several registers | Cor. P3 (INTERP Thm 7) |
| "it runs programs it never saw" | measured (G1). Prop 6 and the footprint–view rule are the reason to expect it |
| "every transition is the model's; the clock only latches and advances" | §3's causal tests, plus the clock's audit. Causal tests cannot turn external control into autonomous internal execution, and the page does not claim that |
| demo 2, register computer | Lemma Q + REGS R0/R1 |

## 6. Risks, ranked

| # | risk | mitigation | kill criterion |
|---|---|---|---|
| 1 | Compile errors: the table is wrong | literal rows and library tables; small programs; row-by-row display; self-check is shown, never counted | G3 below 90% on a family after stage 2: drop that family from the suggested prompts. Below 90% on all of them: the demo becomes "certified execution of programs you write", with compile as a stretch goal |
| 2 | Reading at length | R2 for list inputs (exact by construction); R1p for sentences (length-free); cap demo lengths where G2 holds | R1p below 98% whole-tape exact at 1,024 on every sentence family: sentence families are capped at what passes, or demo 1 ships list inputs only |
| 3 | The pinned executor does not learn in Qwen's layers (QINTERP2's fate) | E−1 and E1 first; LoRA on all layers over Π and the block; INTERP's batch scale; attention supervision on one head if needed | E1 below 50% row-exact after 1,000 steps and a second, larger try below 80%: fall back to R0 with an empirical certificate only, and say so |
| 4 | No single identifiable lookup head (panel 2) | causal attribution; supervise one head's attention | ablating the supervised head breaks fewer than 95% of runs: panel 2 shows attribution, not an arrow |
| 5 | The clock is read as a hidden interpreter | show the loop; audit; plain-decoding mode (R0) side by side; R1 so the model, not the clock, reads the prompt | Neo's judgement (§7) |
| 6 | Numerical mismatch between certification and run | certify on the run's code path, batch 1 (Cor. P2) | any tick whose logits differ at all from its row's on the same host and path: a bug, stop |
| 7 | Browser runtime cannot do pinned blocks | server first; browser later with a custom block forward | no browser path by the time the server demo works: ship the server |
| 8 | Language damage from the one adapter | PROMPTBOX's P13 bar, measured with execution data in the mix | P13 fails: reduce rank or mix more chat, as PROMPTBOX registered; last resort two adapters, stated on the page |

## 7. Decisions that are Neo's

1. **The clock.** Pinning needs about twenty lines of loop that feed two token ids into a fresh block, with a fixed
   mask and fixed positions. It is what makes the certificate a theorem. Plain decoding (R0) needs no loop beyond
   standard generation, but its certificate can only be empirical, because the step depends on the whole context
   (§5.2). Is the clock acceptable on the public page, shown and audited, with R0 as a comparison toggle? And with
   it, the headline: "the model computes every transition of the table it wrote, exhaustively verified, invoked by
   an external clock", not "an LLM runs programs inside itself" (§0, §8.4).
2. **Reading tier per family:** R2 (the clock walks the user's tokens from a span the model quotes) for list inputs
   and R1p (pinned per-clause translation, clauses split on punctuation by the clock) for sentences, which is my
   recommendation; or the model reads everything itself (R1/R0), which caps lengths.
3. **Library tables:** allow labelled imports (`use remainder 7`) in demo 1, or literal tables only. Imports widen the
   families but make "the model wrote this program" false for those rows.
4. **Server or browser** (DEMO_SPEC §5).
5. **Demo 1 scope:** small enumerable programs only (≤ 256 rows, independent registers, no output tapes), with REGS
   (multiply, sort, cascades, several bracket types) as demo 2.

## 8. Outside critiques

Two referees read the whole first draft (no keys, no private paths): Gemini (`agy`, gemini-4-argon-high) and Codex
(`codex exec`, high reasoning, read-only). Their full texts are in `research/demodesign/critiques/`. I checked each
mathematical claim before taking it. Both agree that the core construction (pinning, exhaustive per-program
certification, the Theorem 8(a) counterexample) is right. Both say the draft overstated what the clock does and what
the evidence shows.

### 8.1 Math checked

| claim | referee | check | verdict |
|---|---|---|---|
| §5.2 counterexample: push 2Rn/(n + e^c) crosses R exactly at n = e^c | both | β(n/2)/(n + e^c) with β = 4R; 2Rn = R(n + e^c) iff n = e^c; equality is a tie | correct; the draft's conclusion stands |
| "in a pinned block the push is 0" does not follow: Π's rows contain `a` tokens | Codex | true: the push is constant per (s, e), not zero | taken (§5.2) |
| P2: argmax survives if margin > 2τ with τ an ℓ∞ per-logit bound | both | ẑ_t − ẑ_j ≥ z_t − z_j − 2τ | correct; the draft also said "> τ" in §2.5, inconsistent |
| P2: measuring τ over the rows needs both paths on every row, so it is no cheaper than unbatched certification | Gemini | true | taken: certify on the run's path; the check is equality |
| bf16 unit in the last place at 16 is 0.125, so a 10⁻³ tolerance is meaningless | Gemini | bf16 has 8 significand bits: 2⁴ × 2⁻⁷ = 2⁻³ | correct; taken |
| Lemma Q: non-row positions must enter the softmax denominator | both | 1/w_{r₀} = 1 + Σ_{rows} + Σ_{non-rows}; the draft dropped the second sum | correct; the draft's bound was false for an unmasked head; Z₀ added |
| Lemma Q: η cancels in the slope; bound = g_I + w(R₀ + Ω) − Ω − η | both | w(R₀ − η) − (1 − w)(Ω + η) = w(R₀ + Ω) − Ω − η | correct; taken |
| Lemma Q: inflate the joint leak, 1 + e^{2ε}(XY − 1), not each factor | Codex | e^{2ε} multiplies (XY − 1); multiplying both factors by it changes the cross-term | correct; taken |
| final RMSNorm: gain γ and a head-dependent denominator make the normalised gap non-additive; the sign is that of (U_t − U_m)D_γ x | Codex | RMSNorm(x) = γ ⊙ x / rms(x), and rms depends on x = h + o | correct; the draft's "only rescales" was wrong; taken (§4.3, §5.3) |
| whole-table vs per-row: 0.999²⁵⁶ ≈ 0.774 | Codex | ln = 256 × (−0.0010005) = −0.256 | correct; G1 is whole-table |
| stage gates imply end-to-end ≈ 0.95 × 0.97 × 0.99 ≈ 0.912 at best under independence | Codex | 0.95 × 0.9603 = 0.9123 | correct; G4 measured directly |
| P3 certification cost Σ_j \|B\|·\|S_j\|·Π_{k∈D_j}\|S_k\| | Codex | counts each register's local input combinations | correct; taken |
| QINTERP2's cross-entropy 2.0 is "not automatically chance" | Codex | uniform over a table's names gives mean ln N = ln(16!)/15 ≈ 2.04 for N = 2…16, so 2.0 is near it but does not prove it | taken as a softening |
| the block's first position cannot see the event | Codex | causal mask: position |Π| attends to Π and itself | correct, and a real bug in panel 3 and §2.2; fixed |

### 8.2 Taken (design changes)

- **Theorem P's hypotheses made explicit** (both): single-token, injective names with one spacing convention; total,
  well-formed δ; strict margins; a deterministic runtime with no other mutable state; the converse's proof sentence;
  a certificate contract binding the exact token ids, weights, tokenizer, output set, mask, positions and runtime.
- **The executor adapter must be active on Π as well as the block** (Gemini). Gating it to the block froze Π's keys
  and values at the base model's. E1 now tests both arms.
- **One adapter** (Gemini; Codex adds that a position-gated adapter cannot in general be merged into static weights).
  The "chat logits bitwise unchanged" and "language cost zero" claims are withdrawn; P13 is measured.
- **Reading redesigned** (Gemini): R2 span quotes for list inputs, R1p pinned per-clause translation for sentences.
  The induction-head argument is withdrawn (both: low-entropy alphabets make matches ambiguous). R2's exactness is
  stated as conditional on the span (Codex).
- **Narrowed scope** (Gemini): demo 1 has independent registers only, no output tapes (addition dropped; Cor. P4
  explains how outputs would be certified), one bracket type, and at most 256 rows, the size E1 and G1 train and test.
  Literal tables stay at about 50 rows.
- **Library tables labelled as imports** (Gemini), and whether to use them at all is now Neo's decision (§7).
- **E0b in PROMPTBOX's native format** (Gemini), with the caveat that it remains a shift (Codex).
- **E−1, a systems check before any training** (Codex), and an overfit-one-table step in E1.
- **Honest clock language** (both): it latches, advances, routes and halts; it chooses no state. A single tick is an
  ordinary causal forward on a reused prefix cache (Codex). The headline now says "an external clock invokes it".
  The certifier checks every row of S × B by token-id match, so it needs no graph search, and pokes to any state are
  covered (Codex: reachable-only certification would not cover pokes).
- **Causal tests tightened** (Codex): ablation controls and selectivity; pokes chosen so that final states differ,
  plus conflict pokes against the prompt.
- **Evidence softened** (Codex): the 38 of 51 is conditional on 51 placeable cases of 125; matching wrong values may
  be shared recomputation; the 13 contradictions do not isolate drift.
- **Full-vocabulary argmax recommended** (Codex: a restricted argmax certifies constrained decoding only), and
  "pinning is necessary" softened to "sufficient" (Codex).
- **Gates**: margins reported, not gated on a raw value of 3; acceptance rate and correctness given acceptance
  reported separately; G4 on a fresh test set after families are dropped (Codex).

### 8.3 Rejected or partly rejected

- **"`certified` was a constant string in every SFT target, so 128 of 128 is a trivial artifact"** (Gemini).
  Rejected as stated: PROMPTBOX mixes 15% verification examples whose target is `not certified` (PROMPTBOX.md §mix;
  `pb_data.py`). The point that the mark is not evidence stands, so §1.3 now says the trained self-check did not
  transfer to the model's own errors.
- **"Never parse the program in the harness; certify by margins and attention concentration alone"** (Gemini).
  Rejected: a margin-only check certifies determinism, not that the run follows the table the visitor reads, which is
  the whole claim. Taken in part: the certifier is a disclosed token-id match over all rows, with no graph search,
  and the answer never comes from it.
- **"Reframe the clock as KV-cache eviction"** (Gemini). Partly taken as a description, but Codex is right that the
  relabelling does not change its role, so the page calls it the clock and lists what it does.
- **"Drop multi-digit addition, or define a trace readout"** (Gemini). Both taken: dropped from demo 1, and Cor. P4
  is the trace readout for later.

### 8.4 What both critiques leave for Neo

The honest headline ("the model computes every transition; an external clock invokes it") is weaker than "an LLM
runs programs inside itself". Whether the weaker headline is the demo Neo wants is the first decision of §7.

## 9. What I read

COMMON.md and DEMO_DESIGN_BRIEF.md (orchestrator worktree); `research/DEMO_SPEC.md`, `research/cursor/PROMPTBOX_BRIEF.md`
and `QINTERP3_BRIEF.md` (this branch); INTERP.md and REGS.md (`interp` worktree); PROMPTBOX.md, `pb_lang.py`, the
scoring part of `pb_eval.py`, and every stage (a) gate record and saved text (`promptbox` worktree); QINTERP.md and
QINTERP2.md (`latent1` worktree); DIAG.md (`five` worktree); THEOREMS.md (summary, INTERP sections, Part V) in the
main repository. BLINDNESS_EXPLAINED.md was not needed beyond THEOREMS' statement of the blindness theorem. For the
critiques: Gemini's and Codex's full replies (`research/demodesign/critiques/`), and, to check Gemini's "constant
string" claim, PROMPTBOX's training mix (PROMPTBOX.md) and `pb_data.py`'s verification targets. The referees were
sent `critiques/prompt.md` (referee instructions plus the whole first draft).
