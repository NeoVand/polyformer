# SKETCHPAD3: one model, a calculator and algebra on its own sheet

Orchestrator and Fable, 30 Oct 2026, for Neo. This is the plan; Fable's design detail, demo script and registered tests
are in `SKETCHPAD3_FABLE.md`, the numbers in `research/sketch/calc_dryrun.md` and `compile_baseline.json`. Nothing has
been trained; everything below cost $0.

Neo asked for a sheet that does everything a calculator does, solves algebraic equations, and is used by one model that
decides for itself when to open it, keeping both its language and its page reliable ("the progressive kind").

## The answer in five lines

1. **Calculator.** Every key is a pen-and-paper procedure over a few small digit tables. We have addition and
   multiplication; subtraction, a quotient-digit guess and a decrement are new, about 650 new table rows. One retrain,
   about $5.
2. **Algebra.** The sheet never moves symbols. It evaluates what you typed at a few numbers, reads the polynomial off the
   values, solves, and checks by substituting back. Every digit is certified. What language still does shrinks to copying
   the equation with x replaced by a number.
3. **One model decides.** It writes a short work order inside its reply, the sheet runs it, and the results come back
   into the reply. We train it on synthetic dialogues, in one LoRA with a hard on/off gate in the graph. Gate off is stock
   Qwen bit for bit; that is the useful part of "progressive".
4. **Speed is the main risk.** At about 37 ms per step, demo problems stay under about 300 steps (12 s or less). Leaving
   the layer states on the GPU when nothing reads them already made each step 1.4–2× cheaper.
5. **Order.**
   1. Dry runs (done).
   2. Retrain with the new tables.
   3. Check end to end on the device.
   4. Algebra on the page.
   5. Chat fine-tune.
   6. The gate.

   About a week and $10–25.

## 1. What we measured today ($0)

**Cost of a step on the M4** (E6 page, batches of 1 to 32 rows):

| | Per call | Per batch row |
|---|---|---|
| Inside view capturing every layer, every step | 0.15 s | 0.05 s |
| States left on the GPU | 0.065 s | 0.037 s |

- The cost is flat in batch size, so the step count is the cost. Clever parallel schedules (carry-lookahead and the
  like) save calls, not rows, and buy almost nothing.
- Copying all 25 layers' states off the GPU was a third to half of every step. The worker now skips the copy when
  nothing reads it. That is uncommitted in the sketchpad worktree; it also speeds up the certificate check.
- Slicing the graph's state output to the one row the panel shows would make the inside view nearly free.

**Dry runs with the reference tables in place of the model** (`calc_dryrun.py`). Every procedure is exact using only
local views:
- division: 200/200 per size;
- square root: 300/300 random;
- every algebra case listed below.

Seconds are with states on the GPU.

| Problem | Steps | Seconds |
|---|---|---|
| 40-digit sum or difference | 40 | 4 |
| 1,000-digit sum | 1,001 | 102 |
| 6 × 6, 12 × 12 product (measured live) | 96, 336 | 5, 19 |
| 12-digit ÷ 4-digit to 10 places | 245 | 20 |
| 1/7 to 100 places | 500 | 44 |
| integer √ of a 20-digit number | 193 | 15 |
| √2 to 20 places | 787 | 63 |
| 2^256 by squaring | 7,638 | 343 |
| gcd of a 13- and a 16-digit number (13 divisions) | 641 | 47 |
| 3(x − 2) + 5 = 2x + 14, with the check | 44 | 4 |
| 2x + 3y = 7, x − y = 1 | 57 | 5 |
| (x + 2)^5 expanded (as 1002^5) | 336 | 23 |
| (2x − 3)(x + 5) = x² − 15, or x² − x − 6 = 0, with checks | about 300 | 29 |

So on stage: products to about 10 digits, divisions to about 10 places, √ to about 6 places, and every algebra example
above. The 1,000-digit sum, 100 places of 1/7 and 2^256 are background pieces that run while the chat continues.

**The language half** (`compile_baseline.py` on Modal; Qwen3.5-0.8B, few-shot in the chat format, greedy; scored by
running what the model writes; outputs in `modal/out/compile_baseline_1214/files/compile_samples.jsonl`):

| Task | Untouched 0.8B | With the E6 adapter |
|---|---|---|
| Expression → work order (one operation per line) | 15/60 | 0/60 |
| Equation → its two sides at x = 0 and x = 1 | 0/60 | 0/60 |
| Word problem → one expression | 44/60 | 1/60 |

What the outputs show:
- **Work orders: real mistakes.** The untouched model gets operator precedence wrong: `41 − 7 × (…)` becomes
  `t1 = 41 − 7`.
- **Equations: format failures.** The untouched model answers in LaTeX with headings and often substitutes into the
  example's equation instead of the asked one. The task itself is copying, which fine-tuning on the format should fix.
- **Word problems: wrong operations.** The misses use + for −, or the wrong grouping.
- **The adapter damaged instruction-following**, although text perplexity moved only 0.7%. It rambles, copies the
  few-shot examples, and claims the question has a typo.

Three consequences:
1. Perplexity on plain text is not a sufficient retention test.
2. The page's "Ask it" chat runs on these weights and is worse than stock Qwen at following instructions.
3. The chat fine-tune (T4) must hold the base's chat behaviour, not just its text statistics.

## 2. The calculator (Fable §1, with today's corrections)

The digit tables, each a view of three cells and an answer:

| Table | What it does | Rows |
|---|---|---|
| ADD | add a column with its carry | 242, have |
| MUL | multiply a digit by a digit, with carry | 1,100, have |
| SUB | subtract a column with its borrow | 242, new |
| EST | guess a quotient digit from three digits | 398 views met, new |
| DEC | lower the guess by one | 9, new |

Everything else is layout and the next-step token the model already writes. Comparison is free: the final borrow of a
subtraction says which number is bigger. Signs, decimal points and percent are layout.

**Division is Knuth's Algorithm D on paper**:
- Scale the divisor so its first digit is at least 5, which costs one multiply pass.
- Guess each quotient digit from three cells.
- Multiply and subtract in one pass, pipelined two rows per call.
- If the borrow comes out set, step the guess down and add the divisor back.

The guess was too high on about 1 quotient digit in 4. Trial subtraction (no EST table) is 2–3× slower; EST is worth its
398 rows.

**Square root, digit by digit**, uses the same trick:
- Scale the number by c² (c is 1, 2, 3 or 5) so the root starts with 25 to 49. Each digit's guess is then at most 2 too
  high, exactly as in division.
- Divide by c at the end.
- This is new today; exact on 300 random cases.

## 3. Algebra by evaluation (our addition to Fable §2)

The field is computer algebra. Its two standard ways to solve an equation are:
- **rewriting** the expression tree, step by step (what a student and Mathematica's step mode do);
- **evaluating** at numbers and interpolating (black-box polynomials, Kaltofen and Trager 1990).

The second needs nothing but arithmetic, which is exactly what our sheet certifies.

- **Equations in one unknown.** The model copies each side with x replaced by a number: L(0), L(1), R(0), R(1) for a
  linear equation, and four points for a quadratic (the fourth confirms the degree). The sheet computes the values, and
  the coefficients fall out by subtraction and one halving. It then solves:
  - linear: one division;
  - quadratic: the discriminant, a √ that halts with remainder 0 when the roots are rational, and two divisions.

  It checks every root by substituting it back, with Horner's rule.
  - Brackets, nesting and x on both sides cost nothing extra.
  - The model never expands anything in words.
- **Expansion.** (x + 2)^5 is 1002^5 on the sheet (Kronecker substitution, 1882): 1 010 040 080 080 032, read in groups
  of three as 1, 10, 40, 80, 80, 32. No new table: it is the multiplier we ship. This is the beat for ML researchers.
- **Systems.** Cramer's rule for 2×2, or fraction-free elimination (Bareiss) for 3×3; products, differences and one
  division per unknown.
- **Factoring.** Guess, then prove (Fable): the model proposes the divisors of the constant term, and the sheet's Horner
  check accepts or refuses each one.
- **Display.** Fable's coefficient grid is how the answer is drawn: one column per power of x, like a student's working.

**Certified:** every digit, every halt, and every check. **Not certified, and shown on the page:**
- the work order: which values to compute, and that x was replaced correctly;
- the degree claimed, which the extra point catches if it is wrong;
- which procedure runs.

**Out of scope for this round:**
- trig;
- general fractions of polynomials (rational functions);
- calculus beyond polynomials;
- simplification that is not polynomial.

Those need term rewriting (PENPAPER §5) and are the second milestone.

Why evaluation over the grid as the engine:
- In the grid route someone must expand 3(x − 2) + 5 into 3x − 1 first. In words that is uncertified algebra; on the
  sheet it is carry-free multiplication with multi-digit coefficients per column, a new nested layout.
- Evaluation keeps the sheet to procedures it already has.

## 4. One model that decides (Fable §3, agreed)

The field is tool-use training (Toolformer 2023: put candidate calls into text and keep those that help; PAL, ToRA)
together with continual learning (progressive networks 2016, gated adapters). The mechanism:
1. The model writes a work order in its reply, which the runtime draws.
2. The certified steps run.
3. The answers come back into the reply.
4. The model goes on talking.

The training data is synthetic dialogue: problems that need the sheet, distractors that do not, and problems inside
prose. Scores on held-out templates:
- precision and recall of opening the sheet;
- exact transcription;
- perplexity, GSM8K and MMLU.

| Option | Breaks | Buys |
|---|---|---|
| **A. One always-on LoRA**, steps and chat in one adapter | risks 9 (language) and 5 (margins may move) | simplest; one retrain |
| **B. A + a hard gate input** (0: stock Qwen bit for bit; 1: the sheet machine) | nothing | language exactly intact whenever the sheet is not needed; a stage beat (switch it off, the model gets it wrong) |
| B′. Learned soft gate or progressive columns | 5, if a soft gate sits inside a certified step | emergent engagement; not needed, since new abilities arrive as certified procedures |
| C. A larger base (Qwen3.5-4B) | 11: every step about 4× slower | a better compiler, if the 0.8B fails |
| D. A talker plus a sheet model | 1 and 2 | everything practical; Neo rejected it |

**Recommended: B** (A with the gate). The decision to open the sheet must live in weights that are on during chat, so the
gate is on for the whole conversation. The gate's value is the guarantee and the demonstration, not the deciding. If the
0.8B cannot write work orders after fine-tuning, C is the fallback for the language half only.

**What the baseline changes.** Today's adapter is on during chat and hurts it (§1). Forgetting under fine-tuning is
continual learning, and its standard fix is to distil the old model's behaviour into the new one: Learning without
Forgetting (Li and Hoiem 2016), here self-distillation on the base's own chat answers. Concretely:
- T4 adds a KL term to the base's chat answers on instruction prompts, next to today's plain-text term.
- T4 reports instruction-following (IFEval-style), GSM8K and MMLU against stock, not perplexity alone.
- Until T4 passes, the page's chat should run with the gate at 0 (stock Qwen), and the page sentence "The same weights
  still chat" should say the chat is stock.

The compile itself needs a fine-tune either way:
- The untouched 0.8B misses precedence 3 times in 4.
- It cannot follow the equation format at all.
- Algebra by evaluation keeps that job to copying, the easiest kind of language task.

## 5. The demo

Fable §4 is the script: a poem, a product the model decides to do on the sheet, a live edit, money with percent and tax,
an equation, factoring by guess and prove, √2 to six places, the inside view, then the gate switched off.

Three changes from today's numbers:
- Add the 1002^5 beat.
- Make the inside view capture only the shown row, so it costs nothing.
- Keep every beat under 300 steps.

## 6. Plan, money, kill lines

1. **Runtime (T1, $0, 1 day).** The new layouts (SUB, division, √, evaluation) go into the page's TypeScript runtime.
   With reference tables in place of the model, it must be exact on 1,000 random instances per procedure.
2. **Retrain (T2, about $5).** E7, from E6, recipe v2, with SUB, EST, DEC and the division and √ control steps, about
   2,500 rows.
   - Kill: not every row certified by 4,000 steps, or perplexity above ×1.02.
3. **On device (T3, $0).** 50 each of division, √, gcd and signed sums, all exact, each under 12 s.
4. **Algebra (T6, $0).** 200 each of linear equations, quadratics, expansions and 2×2 systems, plus 200 corrupted answers
   the check must refuse.
5. **Chat fine-tune (T4, $5–10).** 3,000 synthetic dialogues, 30% distractors, held-out templates, plus self-distillation
   on the base's chat answers.
   - Registered against the baseline (§1):
     - work orders above 0.95, from 0.25 untouched;
     - equation substitution above 0.95, from 0;
     - word problems above 0.9 on held-out templates, from 0.73;
     - instruction-following within 2 points of stock.
   - Kill: rows lost, perplexity above ×1.03, or instruction-following more than 5 points below stock.
6. **Gate (T5, $0).** One graph input; gate 0 bit-identical to stock on 100 prompts.
7. **Prior-art gate (done today, `research/audit/sketchpad3_gate/out.md`, 50 abstracts checked).** All three claims
   came back NARROW. The pieces exist apart from each other:
   - exact arithmetic at any length: Neural GPU, Wei's cellular automaton, DFST;
   - proving a learned program correct by testing a finite set of inputs: Cai et al. 2017;
   - a pretrained LLM stepping through procedures, division included, near-exact but uncertified: CAEF;
   - algebra by learned models: Lample and Charton, Minerva;
   - choosing when to call a tool: Toolformer, ToRA, ReTool;
   - switching adapters on and off: X-LoRA.

   Not found anywhere: a pretrained VLM whose only state is a rendered sheet, with every view certified and the check
   re-run on the user's GPU. Nor a learned certified long division, square root or gcd, nor algebra by evaluation or
   Kronecker substitution on a learned executor.

   Sentences we may say, each only once its piece has passed:
   - "the first pretrained VLM to do exact addition and long multiplication at any length with a rendered sheet as its
     only state, certified on all 1,795 views and re-checked on your GPU" (true today);
   - "polynomial expansion and equation solving in which every arithmetic step is done by a learned, certified
     executor";
   - "a small VLM that writes a work order mid-conversation and carries it out itself on its own sheet".

   Rules from the gate:
   - Never say "inside its forward passes" without "one step per forward pass; a fixed runtime paints and moves".
   - The algebra algorithms are classical. Only their certified execution is ours.
   - A substitution check confirms the roots found, not that all were found.

## 7. Assumptions check (what Neo did not ask for)

- The 0.8B stays the model, for step speed. The 4B is only a fallback for the language half.
- 12 s or less per beat counts as not disappointing.
- Typed problems only; photos are a later beat.
- "Calculator" means integers and decimals to a stated number of places: no repeating-decimal detection, no scientific
  notation.
- Algebra means polynomial equations in one or two unknowns of small degree.
- The work order may stay uncertified as long as it is shown.
- "Progressive" means Rusu's networks; we use only their hard gate.
- This competes for the week with the ARC/NetHack track, whose benchmark choice is still waiting on Neo.
- Nothing trains until Neo says go.
