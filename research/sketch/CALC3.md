# CALC3: the calculator on the sheet (SKETCHPAD3 T1–T3)

Log of the CALC stream (brief: `research/meta/sketchpad3/CALC.md`, contract `CONTRACT.md`). Registrations were written
before the runs they register.

## Report: E7 with the gate, published (30 Oct 2026, evening)

**Published:** `mohsenvand/sketchpad-0.8b-preview` revision `2df871728a9d24d1e102a327d1f1475457c53962` (parent
`ca527a6d`), pinned in `models.ts` (`HF_REVISION`). `arithmetic/` is now the gated E7 program: graph, lens, inside data,
certificate, adapter; README updated. Every uploaded file checked by sha256 against the staged copy (9 changed), the
other 17 files unchanged (`hf_publish_e7.py`).
- **Identity (ONNX Runtime 1.31.1 CPU, Modal, 8 shards):** gate 1 = ungated E7 and gate 0 = stock, bit for bit on every
  logit, hidden state and present state: 2,500/2,500 chat calls (100 prompts) and 2,688/2,688 rows (all 2,446 rows plus
  the 242 SUM rows in the page's padded form) for each pair; greedy text identical 100/100.
- **Certificate on the M4 (WebGPU):** 2,446/2,446; min margins addition 3.016, multiplication 6.516, calculator 4.609.
  All 2,446 margins equal the ungated E7's, to the stored 1/1000.
- **T3 again, all 200 problems:** 200/200 exact (also checked against a Python oracle), each step for step the same as
  the ungated T3 (steps, views, answers). Wall times are not comparable: the machine was busy and the browser reset the
  GPU three times (see below); the cost model gives the same seconds as before (√ to 6 places median 10.7 s, 13/50 over
  12 s).
- **Prod build** (`BASE_PATH=/polyformer pnpm run build`, `vite preview`, a fresh browser profile): the page loads all
  1,913 MB from the pinned revision and accepts the shipped certificate; the weakest tenth of each table passes again on
  the M4 (addition 25 rows, lowest 3.02; calculator 66, lowest 4.61; multiplication too, since Calculate reads all three
  tables and reports its run certified). Calculate: 22 ÷ 7 to 10 places = 3.1428571428…, exact, 45 steps, 4.6 s.
  The page's prose still describes only addition and multiplication (left for the port).
- **Device-loss recovery (step 6):** dropped by the orchestrator (it moves to NeoVand/sketchpad). The code was written and
  ran during this T3: it recovered from all three real GPU resets (Chrome: "A valid external Instance reference no longer
  exists"), reloading from the cache in 13.5 s and redoing the step in flight, with every answer exact. It is reverted
  here and kept as `calc-device-loss-recovery.patch` in the orchestrator's notes folder; the forced-loss test
  (`device.destroy()`) was not run.
- **Spend:** about $0.44 (Modal CPU, identity test); the stream's total is about $2.8 of $15.
- **D3 (refined guess) now or at the final retrain:** wait for the final retrain (below, "D3").

## Report (30 Oct 2026)

**Passed.**
- **T1:** subtraction (signed sums and differences), Knuth long division and the digit-by-digit square root run on the
  sheet as model steps, each on a three-cell view of a certified table. `SheetCalc` implements seam 2, plus waves
  (`Calc.wave`: steps of different operations share forward passes). Exact on 1,000 random cases per procedure with the
  reference tables; no view outside the tables, ever. Calculate mode is on the dev page.
- **T2:** E7 (E6 seed 3 + SUB 242, EST 400, DEC 9 rows) passed both kill lines. 2,446/2,446 rows certified on the
  server, minimum margin 3.96; perplexity ×1.0048 of stock; stopped at step 1,600. Every row was first certified at step
  1,200 (predicted). Compile baseline: plan 0/60, equation 0/60, word 2/60 (E6 0, 0, 1; stock 15, 0, 44), so E7 hurts
  chat no more than E6. Program folder built into `static/sketchpad/models/arithmetic-e7/`.
- **T3, exactness and certificate:** on the M4 page, the full certificate in the browser, **2,446/2,446**, every margin
  positive (minimum 3.02 SUM, 4.61 calculator, 6.52 multiplier). **200/200 problems exact** (50 each of division to 10
  places, √ to 6 places, gcd, signed ± up to 20 digits). Every run certified, no unchecked view. All 200 answers were
  checked again in Python.

**Failed.**
- **T3, the 12 s bar: 184/200 met it.** Medians: division 7.0 s, √ 9.8 s, gcd 7.0 s, ± 2.0 s. Over 12 s: √ 11/50
  (max 16.5 s), gcd 4/50 (max 13.4 s), division 1/50 (13.3 s), ± 0/50. Measured wall times track the cost model
  (median ratio 1.02). The over-bar cases are roots of 3-digit numbers with several lowered guesses, and gcds with many
  division steps.
- **The browser dropped the WebGPU device 3 times** in about 45 minutes, with the Browser pane hidden
  (`mapAsync … A valid external Instance reference no longer exists`). The tab was also reloaded once. Each time the
  driver reloaded the model (certificate recalled from this device's cache) and redid the interrupted problem.
  No wrong digit came of it; the page itself does not yet recover from a lost device.

**Spend:** about $2.5 of $15 (37 min of H100 in four Modal jobs, table below). **Commits** on `sketchpad`: listed at the
end. Optional item (slicing `hidden_states`) not done: T3 missed the 12 s bar, and the calculator already leaves the
states on the GPU unless the run is slowed down.

**For the orchestrator.**
- `main` merged in (the `lora_gate` wiring kept).
- E7 is built without the gate.
- `HAS_CALC` turns Calculate on for the dev page only.
- PROGRAM can use `sqrtFloor` and `divFloor` for "to k places".
- Hand-over note: `calc3-handover.md` in the shared notes folder.

## T2 registration (30 Oct 2026, before launch)

**What runs.** E7 = E6 seed 3 (`e6_adapter_s3_h4_v2_cont`, the shipped adapter) trained on with recipe v2 (LoRA r16,
alpha 32, language layers only; hinge 4, cosine lr 2e-4 → 2e-5, KL to the base on plain text, certificate every 100
steps with replay of the rows below hinge/2, stop when every row is certified with minimum margin ≥ 3.0), on 2,446 rows:
the 1,795 E6 rows (SUM 242; MUL 1,100, ADD 220, ADZ 220, FLS 2, NXT 11) plus the new tables of `calc_tables.py`:

| Table | View (three cells) | Answers (`=`, `?`, `?`) | Rows |
|---|---|---|---|
| SUB | borrow (blank, 1), top, bottom (blank, 0–9) | digit, borrow 0/1, `S`; both blank: `-`, `-`, `H` (no borrow out) or `B` (borrow out) | 242 |
| EST | r_hi, r_lo, d_hi with d_hi 5–9, r_hi ≤ d_hi | min(9, (10 r_hi + r_lo) // d_hi), `-`, `M` (multiply-subtract) or `N` (guess 0) | 400 |
| DEC | q (1–9), blank, blank | q − 1, `-`, `C` (correct the remainder) | 9 |

Prompts: `SUB<image>=??`, `EST<image>=??`, `DEC<image>=??` (each word one token, like ADD and SUM; the page pads every
slotted prompt to the longest word's length, as for the multiplier). Strata per step: E6's (MUL 20, ADD 4, ADZ 4, FLS 1,
NXT 2, SUM 6) plus SUB 8, EST 12, DEC 2. Seed 3, up to 4,000 steps, H100 on Modal (`launch.py e7 3`).

**Kill lines (from the brief):** not every one of the 2,446 rows certified by 4,000 steps, **or** plain-text perplexity
above ×1.02 of stock at the end. Either one: stop, build nothing, report.

**Predictions:**
- every row certified by step 1,200; the stop rule (all rows, minimum margin ≥ 3.0) fires by step 2,000;
- minimum margin at the stop 3.0–3.6 (E6 stopped at 3.35), the weakest rows in EST or MUL;
- perplexity ×1.000–1.012 of stock (E6: ×1.007);
- spend: smoke about $0.3, training $2–4, the compile job about $1; cap $15.

**Then:** certify every row on the server (`evaluate`), build `static/sketchpad/models/arithmetic-e7/` with
`build_program.sh`, run the `compile` job on E7 (E6: plan 0/60, equation 0/60, word 1/60; stock 15, 0, 44).

## T2: E7 result (30 Oct)

Passed both kill lines. Training log (`modal/out/e7_s3_4000_h4.0_stop3.0_fast/run.log`), certificate every 100 steps:

| Step | Rows certified (of 2,446) | Weakest table, margin | Perplexity × stock |
|---|---|---|---|
| 100 | 2,305 | EST −13.9 | 1.011 |
| 500 | 2,425 | SUB −10.5 | 1.008 |
| 900 | 2,443 | EST −7.2 | 1.010 |
| 1,200 | **2,446** (first time) | EST 0.54 | 1.004 |
| 1,300–1,400 | 2,443, 2,439 (replay churn) | SUM −14.1 at 1,400 | 1.000–1.002 |
| 1,500 | 2,446 | EST 1.13 | 1.007 |
| **1,600 (stop)** | **2,446** | **SUM 3.96** (EST 4.51, MUL 6.39, SUB 8.36, DEC 10.0) | **1.0048** |

Server evaluation of the saved adapter (`evaluate`, the same margin test as E6): **2,446 / 2,446**, minimum margin 3.96
(SUM; EST 4.51, MUL 6.39, ADZ 8.41, SUB 8.36, ADD 9.37, DEC 10.0, NXT 10.48, FLS 12.93), text perplexity 18.55 (E6:
18.58).

Against the registration: every row certified by step 1,200 (predicted by 1,200: right); the stop at 1,600 (predicted
by 2,000: right); minimum margin at the stop 3.96 (predicted 3.0–3.6: higher than predicted), the weakest row in SUM,
not EST or MUL as predicted; perplexity ×1.0048 (predicted 1.000–1.012: right).

Server end-to-end runs with the model (`eval.json`): products 4 × 4 20/20, 6 × 6 10/10, 10 × 10 5/5; sums of 10 digits
20/20, 100 digits 5/5, 1,000 digits 2/2.

**SUM rows in the padded form** (`e7_padcheck.py`, server, fp32): 242/242, minimum margin 3.9600 padded vs 3.9598
unpadded, largest change of any row's margin 0.0018 (mean 0.0004): float rounding, as causality says.

**Program folder.** `build_program.sh` → `static/sketchpad/models/arithmetic-e7/` (not committed, not uploaded; no
gate input, as the brief asks): LoRA into the fp16 decoder (21 MB graph), the inside window, atlas and map data; the
layer-20 push still lands (SUM 79/80, MUL 80/80, as for E6). `models.ts` points the dev page at it.

**On the M4, the full certificate in the browser** (WebGPU, fp16 decoder, the padded form for SUM): **2,446 / 2,446**,
every margin positive: SUM 242/242 (minimum 3.02, 22 s), the calculator's 651/651 (minimum 4.61, 62 s), the
multiplier's 1,553/1,553 (minimum 6.52, 151 s).

## Waves across operations (orchestrator, 30 Oct, after E7 trained)

PROGRAM's algebra is many small, independent `Calc` calls; `Calc` gains `wave(jobs)`, and the sheet must put the
steps of different operations in one batch.

**Decision: one prompt form for every table.** The slotted ops (MUL ADD ADZ FLS NXT SUB EST DEC) already share one: the
word, the image, `=`, two `?` slots, and `?`s up to the longest word's length (two tokens), answers at `=` and the
slots. The adder's SUM rows were the exception (`SUM<image>=`, one token at `=`). Now, for the E7 program
(`MODELS.add.padded`), the adder's prompt is padded the same way (`SUM<image>=???`), its one answer still read at `=`.
Any mix of steps is then one batch. The certificate checks the SUM rows in exactly this form (`CERT_FORMAT`
`add=padded-fast-242`); E6 on the live page keeps its unpadded form and shipped certificate.

**Training form.** E7 had already trained (SUM rows unpadded) when this arrived. Every layer of Qwen3.5 is causal
(attention and Gated DeltaNet, including its causal convolution), so tokens after `=` cannot change the logits at `=`:
the padded form equals the trained one up to float rounding. Measured rather than assumed: `e7_padcheck.py` on the
server compares all 242 SUM rows in both forms (result below), and the device certificate is taken in the padded form.

**Runtime.** `SheetCalc` sends every procedure's steps through a multiplexer (`Mux` in `calc-sheet.ts`): a step waits
until every procedure under way has asked for its next step (or ended), then all their views go in one call. `wave(jobs)`
is `Promise.all` over the jobs; any `Calc` calls that run at the same time share calls this way. Tests: 20 mixed jobs
(divmod, mul, isqrt, signed sums of four pairs) give the same answers as one at a time, the same views, under a third of
the calls, with SUM, SUB and MUL rows in one batch; a failing job does not hold the others.

## T1: the runtime (30 Oct, $0)

**Files.** `src/lib/sketchpad/calc-tables.ts` (the 651 rows, cross-checked row by row against `calc_tables.json` from
the Python), `calc-sheet.ts` (the procedures on a `Grid` sheet, driven by a `Policy`: the model, or the reference
tables in tests), `sheet-calc.ts` (`SheetCalc implements Calc`, seam 2, with the interface copied from PROGRAM's
`program/calc.ts`), `calc-task.ts` (one calculator line: parse, solve on the sheet, the page's own BigInt answer),
`calc.spec.ts`. Page: a third mode, *Calculate* (dev page only until E7 is published: `HAS_CALC` in `models.ts`).

**How each procedure uses the tables.**

- **Signed sum and difference.** Same signs: the adder (SUM, one token per column, as shipped). Opposite signs: SUB
  column by column; the column past both numbers is the halt row, `H` (no borrow out) or `B` (the top was smaller);
  on `B` the same subtraction runs the other way round and the sign flips. Signs are layout.
- **Long division (Knuth's algorithm D).** Scale both numbers by f = 10 // (d + 1) (d the divisor's first digit) in
  one multiply pass each, side by side (MUL steps; the dividend's trailing zeros are skipped, so `to k places` costs
  nothing extra to scale). Then per digit brought down: EST on the remainder's top two digits and the divisor's
  first; `N` (guess 0) moves on; otherwise one multiply-subtract pass, MUL a column ahead of SUB, two views per call.
  The borrow the model writes out of the top column is the branch: 1 means the guess was too high, so DEC lowers it
  and the adder adds the divisor back; the carry the adder writes out of the top column says whether the sum crossed
  zero again (else DEC again). The remainder of the scaled numbers is f × the true one: × (10 / f) and the last digit
  (a zero) dropped for f = 2, 5; a short division by 3 (the same procedure) for f = 3.
- **Square root, digit by digit.** Scale a by c² so the root starts with 25–49 (then twice the root so far starts with
  5–9, so EST's views stay in the table and each guess is at most 2 too high). Per pair brought down: a guess (the
  first digit 4, which the scale makes the largest possible; the second 9 when the trial divisor starts with 4, that
  is when the root starts with 2; every later one from EST); the trial divisor T = (twice the root so far, then y) times
  y subtracted from the remainder into a new row; a borrow out lowers y (DEC) and the pass runs again from the old
  remainder. The next trial divisor is T + y: the multiplier's ADD on its last digit (and on the one before when that
  carries; that one rides in the next pass's first call), read in the same call as the next guess once T has three
  digits. Then root = R / c (× 10 / c or 100 / c, last digits dropped). Perfect square ⟺ the scaled remainder is 0.

**Deviations from the brief and the dry run, and why.**

1. **c ∈ {1, 2, 4, 5} instead of {1, 2, 3, 5}.** c = 4 covers the range 3 covered (mantissas 1 to 1.5625), and makes
   "divide by c at the end" a multiplication by 10 / c or 100 / c with the last digits dropped, instead of a short
   division (about 6 views per digit). The c rule is exhaustively tested: for every a from 1 to 999,999 the scaled
   root starts with 25–49.
2. **The dry run's √ met EST views with d_hi = 4** (whenever the root starts with 2: twice the first digit is 4), which
   are outside the 400-row table; it also left the doubling of the root and the first digit (`SQ1`, a 100-row table
   not in seam 1) off the sheet. Here the first digit starts at 4 and is lowered by DEC, the second starts at 9 when
   twice the root is 4, and the doubling is ADD steps on the sheet. No view outside ADD/MUL/SUB/EST/DEC is ever read
   (checked in every test).
3. **The branch inside a multiply-subtract is the model's own borrow out of the top column**, not a separate halt
   view: the halt column would cost one call and one view per digit and say the same thing. The SUB halt rows
   (`H`/`B`) are still what a signed subtraction ends on. Likewise the add-back's branch is the carry out of its top
   column.
4. **Remainders.** `Calc.isqrt` returns the exact remainder (from the scaled one: 10^(2k) rem = c'² rs + e (2 root 10^k
   + e), c' = 10^k / c, e the dropped digits; a few passes). PROGRAM only ever tests `rem === 0n`, which is free (the
   scaled remainder is 0 exactly when the true one is), so `SheetCalc` also offers `sqrtFloor(a) → {root, exact}` and
   `divFloor(a, b) → {q, exact}`, which skip the remainder's value; the page's ÷ and √ "to k places" use them.
   **Suggestion for the orchestrator:** PROGRAM's √ to k places and ÷ to k places could call these when present.
5. **The runtime chooses, from the digits it lays out, the scales f and c and the first two root guesses.** None can
   change a digit: every guess is at least the true digit (EST is never too low, and the starting guesses are the
   largest the scale allows), each is checked by a certified multiply-subtract and lowered only by DEC. A wrong choice
   could only cost steps or read a view outside the table, which the page reports. (Checked by mutation: forcing the
   wrong c for small mantissas left every answer exact and only the scale test failed.)
6. Zero: `isqrt(0)` and `0 × b` need no step for the root (`isqrt(0)` returns at once); division of 0 runs on the sheet.

**Tests (`calc.spec.ts`, reference tables in place of the model; all pass, 33 in the sketchpad suite):**

| Procedure | Cases | Exact | Views off the table |
|---|---|---|---|
| tables vs `calc_tables.py` | 651 rows | all equal | – |
| signed sum and difference (`add`, `sub`) | 1,000 (up to 40 digits, signs, zeros, equal operands) | 1,000 | 0 |
| `divmod` | 1,000 (up to 40 digits, divisor longer than dividend, 0, 1, equal) | 1,000 | 0 |
| `divFloor` (to k places) | 1,000 | 1,000 | 0 |
| `isqrt` with remainder | 1,000 (up to 40 digits, squares and their neighbours, 0) | 1,000 | 0 |
| `sqrtFloor` to six places | 1,000 | 1,000 | 0 |
| `mul` signed | 200 | 200 | 0 |
| gcd by repeated `divmod` | 100 (up to 16 digits) | 100 | 0 |
| scale rules | f for every leading digit; c for every a ≤ 999,999 | all | – |

**Cost on the M4, by the page's cost model** (0.065 s per call + 0.037 s per view, states left on the GPU; 50 random
cases each, reference tables). The calculator turns the inside view's state capture off unless the run is slowed down.

| Problem | Calls | Views | Seconds, median | Seconds, max |
|---|---|---|---|---|
| 2-digit ÷ 1-digit to 10 places | 31 | 38 | 2.6 | 6.0 |
| 3-digit ÷ 2-digit to 10 places | 74 | 97 | 8.3 | 13.0 |
| 6-digit ÷ 2-digit to 10 places | 83 | 108 | 9.5 | 14.6 |
| √ of a 1-digit number to 6 places | 72 | 110 | 10.1 | 12.8 |
| √ of a 3-digit number to 6 places | 87 | 139 | 11.0 | 15.3 |
| gcd of two 3-digit numbers | 68 | 96 | 8.3 | 13.0 |
| gcd of two 4-digit numbers | 112 | 159 | 13.7 | 21.6 |
| signed ± of 20-digit numbers | 26 | 26 | 2.1 | 4.3 |
| 22 ÷ 7 to 10 places / √2 to 6 / gcd(1071, 462) | 45 / 105 / 41 | 56 / 162 / 60 | 5.0 / 12.8 / 4.9 | |

(Before pipelining the next guess with the doubling and dropping the halt column: √2 to 6 places 14.6 s, 4-digit ÷
2-digit to 10 places median 9.9 s.) So by the model the 12 s bar holds for demo-sized problems and fails in the tail
of 3-digit operands; T3 measures the real times.

## T3 registration (before any device run)

On the M4 dev page with E7 (`arithmetic-e7`), *Calculate* mode, Fast (no pause; the inside view's states stay on the
GPU), one problem after another through `sketchpad.runCalc(line)`, wall time from the call to the answer. Problem sets
from a fixed generator (LCG seed 12345, in the order below):

| Set | 50 lines |
|---|---|
| division | `a ÷ b to 10 places`, a uniform in 1–999, b in 2–99 |
| square root | `√a to 6 places`, a uniform in 2–999 |
| gcd | `gcd(a, b)`, a and b uniform in 10–999 (Euclid by `divmod`, remainders on the sheet) |
| signed sums and differences | ± numbers of 1–20 digits (length uniform), random signs, + and − alternating |

Bar (from the brief): every answer exact, each under 12 s; then the full certificate in the browser (all 2,446 rows,
every margin positive). Prediction from the cost model above: all exact; the medians 8, 10, 8 and 2 s; the 12 s bar
fails for a few divisions, roots and gcds in the tail (the model's maxima are 13–15 s for these sizes).

## T3: result (30 Oct, M4)

Dev page with E7 (`arithmetic-e7`), Calculate mode, Fast, Apple M4 (WebGPU "Apple metal-3", fp16 decoder), the
registered sets in order, one problem after another through `sketchpad.runCalc`, 19:45–20:12 UTC. Per-problem record:
`calc3_t3.json` (line, exact, wall seconds, calls, views, cost-model seconds, certified, unchecked views, answer).

**Certificate in the browser first:** 2,446/2,446, every margin positive (SUM 242/242 min 3.02 in 22 s; calculator
651/651 min 4.61 in 62 s; multiplier 1,553/1,553 min 6.52 in 151 s). The T3 runs reused it (same files, device and
runtime: the page's certificate cache).

| Set (50 each) | Exact | Median s | Max s | Over 12 s | Median calls / views | Cost model median s |
|---|---|---|---|---|---|---|
| a ÷ b to 10 places (a ≤ 999, b ≤ 99) | **50** | 7.0 | 13.3 | 1 | 65 / 90 | 7.6 |
| √a to 6 places (a ≤ 999) | **50** | 9.8 | 16.5 | 11 | 86 / 137 | 10.7 |
| gcd(a, b) (a, b ≤ 999) | **50** | 7.0 | 13.4 | 4 | 61 / 84 | 7.1 |
| signed ± up to 20 digits | **50** | 2.0 | 4.7 | 0 | 19 / 19 | 1.9 |

- Every answer equals the page's own BigInt answer, and Python's (checked again from the record).
- Every run's views were all certified rows (0 unchecked).
- Wall time over the cost model's estimate: median 1.02, range 0.76–1.38. The 1.38 is √356, the first problem after a
  device loss, on a freshly loaded model.

**Against the registration.** Predicted: all exact (right); medians 8, 10, 8, 2 s (measured 7.0, 9.8, 7.0, 2.0); the
12 s bar failing for a few divisions, roots and gcds in the tail (right: 1, 11 and 4).

**Over the bar:**
- division 803 ÷ 48 (13.3 s);
- √573, √693, √88, √860, √489, √656, √214, √322, √356, √377, √120 (12.0–16.5 s);
- gcd(362, 983), gcd(232, 257), gcd(261, 734), gcd(232, 909) (12.1–13.4 s).

The roots cost because each digit's multiply-subtract runs over the whole trial divisor, which grows a digit per root
digit, and a guess that is one too high costs a whole extra pass. These roots have 7–8 digits.

**What would bring the tail under 12 s** (not done, for the orchestrator):
- Knuth's refined guess (step D3: a second divisor digit, so the guess is rarely too high), which needs one more small
  table;
- or showing √ to 5 places on stage;
- gcd could stop dividing by 3 for the remainder (scale by 25 instead of 3, a second multiply pass).

**Interruptions.** The first attempt lost its page after five divisions (the tab reloaded while the Browser pane was
hidden). The run was restarted with every result kept in `localStorage`. During it the WebGPU device was lost three
times:
- during √89 (the 46 problems after it failed at once);
- at 20:01:49 during √356;
- at 20:09:12 during gcd(34, 659).

Each time the driver started a new worker and loaded the model again; the certificate came from this device's cache. It
then redid the problem from the start. The table counts only completed runs; no run finished with a wrong digit.

## E7 with the gate, published (30 Oct, evening)

Task from the orchestrator (Neo's OK of 30 Oct for the upload, relayed): build E7 with CHAT's gate, check it on ONNX
Runtime CPU, certify it in the browser, publish it to Hugging Face as a new pinned revision, switch the page to it, and
make the page recover from a WebGPU device loss.

**Build ($0, local graph surgery).** `main` merged into `sketchpad` (fast-forward). `patch_onnx_lora.py` (gated by
default since CHAT's T5) then `patch_onnx_inside.py` on the E7 seed-3 adapter, the graph steps of `build_program.sh`;
the atlas and lens data do not depend on the gate and are E7's (`inside.*` copied, `lens.*` rebuilt byte-identical).
`--no-gate` reproduces the ungated `arithmetic-e7/` graph byte for byte (sha256 `a463b426…`), so the gated graph
(`5f83a661…`) differs from it only by the gate.

**Identity test (Modal CPU, ONNX Runtime 1.31.1 CPUExecutionProvider; `e7_gate_identity.py`, CHAT's
`chat/gate_identity.py` with E7's graphs and rows; 8 shards, summary `e7_gate_identity_summary.json`).** Three graphs
on the same external weights (sha256 of `decoder_model_merged_fp16.onnx_data` checked in the job: `5866a207…`, the
published file): stock (base + inside patch), E7 ungated, E7 gated. Every call compares logits, `hidden_states` and every
present state (conv, recurrent, key/value) bit for bit.

| pair | chat calls (100 no_robots prompts × 25) | table rows (2,446 + 242 SUM rows in the page's padded form) | max diff |
|---|---|---|---|
| stock vs gate 0 | 2,500 / 2,500 bit-identical | 2,688 / 2,688 bit-identical | 0 |
| ungated E7 vs gate 1 | 2,500 / 2,500 bit-identical | 2,688 / 2,688 bit-identical | 0 |

Greedy continuations identical on 100/100 prompts for both pairs. On the captured row inputs gate 1 answers every
row right at every answer place (2,446/2,446 and 242/242 padded); stock 12/2,446 and 12/242 (the inputs are real).

**Certificate in the browser (M4, WebGPU, transformers.js 4.2.0, dev page from `static/sketchpad/models/arithmetic/`
= the gated graph).** 2,446/2,446: addition 242/242 (min margin 3.016, 20 s), multiplication 1,553/1,553 (6.516,
133 s), calculator 651/651 (4.609, 55 s). Every one of the 2,446 margins equals the ungated E7's T3 certificate on this
M4 (as stored, to 1/1000; max difference 0), so the WebGPU provider does not fold the gate into the matmuls either.
The Browser pane could not be shown (this session is open in no window); no device loss during the certificate.
Exported with `sketchpad.exportCertificate()` as `arithmetic/certificate.json`.

**T3 again, all 200 problems (same seed and lines as T3), gated E7.** Record `calc3_t3_gated.json`. The certificate came from the browser's store after a Vite reload of the dev page (my own
file write) at problem 16; three GPU resets during the √ and gcd sets were recovered by the page (device-loss code,
below).

| set (50 each) | exact | same steps, views and answer as ungated T3 | wall median / max | over 12 s (wall) | cost model median / max / over 12 s | ungated T3 wall median |
|---|---|---|---|---|---|---|
| division to 10 places | 50 | 50 | 6.7 / 11.1 s | 0 | 7.6 / 12.1 s / 1 | 7.0 s |
| square root to 6 places | 50 | 50 | 14.9 / 39.9 s | 38 | 10.7 / 17.8 s / 13 | 9.8 s |
| gcd | 50 | 50 | 10.3 / 37.3 s | 19 | 7.1 / 12.0 s / 0 | 7.0 s |
| signed sums and differences | 50 | 50 | 2.2 / 4.9 s | 0 | 1.9 / 4.1 s / 0 | 2.0 s |

The model does exactly what the ungated model did (every step's answers are the same, as the identical margins
promise), so its cost is the same; the wall times are not a measurement of the gate. During the division set the page
ran at the cost model (wall/model 0.88, faster than T3's 1.02); from the fifth √ on, the M4 was shared with other
processes (Claude helpers at 40–85% CPU, the ANE compiler) and the three resets each added a reload of about 13.5 s,
so the √ set ran at 1.24× and gcd at 1.46× the model. The 12-second bar is judged on T3 (184/200) and the cost model.

**Published.** Revision `2df871728a9d24d1e102a327d1f1475457c53962` of `mohsenvand/sketchpad-0.8b-preview` (one commit on
`ca527a6d`, by `hf_publish_e7.py`), checked file by file against the staged copy:

| file | sha256 | |
|---|---|---|
| `arithmetic/onnx/decoder_model_merged_fp16.onnx` | `5f83a661…` | the gated E7 graph |
| `arithmetic/onnx/lens.bin`, `lens.json` | `6ec9da10…`, `bc8a2d3c…` | E7's lens (the letters S, B, C added) |
| `arithmetic/inside.bin`, `inside.json` | `dee3f6d5…`, `e72030c2…` | E7's maps and push means |
| `arithmetic/certificate.json` | `73fbcf44…` | the M4 certificate above |
| `arithmetic/adapter/adapter_model.safetensors`, `adapter_config.json` | `453ae613…`, `f7c23b47…` | the E7 adapter (config as E6's, base path `Qwen/Qwen3.5-0.8B`) |
| `README.md` | | the calculator's rows and margins, prompts, timings |

The adapter is not in the orchestrator's list (graph, certificate, README) but `arithmetic/adapter/` is documented as
the adapter the graph was built from, so leaving E6's there would have made the folder wrong. `base/`,
`arithmetic/sprites.png` and the licences are unchanged. `models.ts`: `HF_REVISION` pinned; `arithmetic` was already
the program's folder, and `HAS_CALC` and the adder's `padded` are now true in every build (the certificate checks the
padded adder and the calculator's table, so a build without them would not accept it).

**Device loss.** Dropped from this task by the orchestrator (the demo moves to NeoVand/sketchpad, where it will be added). What was
written and ran before that: the worker watches the GPU device ONNX Runtime made (`env.webgpu.device`) and reports
`device.lost`, or a failed call whose error is a loss; the page then terminates the worker, starts a fresh one, loads
the same program again (from the browser cache; the certificate from its store) and sends the steps that were in flight
again, up to three times each. A step is a function of its views, so the redone step is the step. It recovered all three
real resets of this T3. Reverted here; patch in the orchestrator's notes folder (`calc-device-loss-recovery.patch`,
untested against a forced loss).

### D3: the refined guess, now or at the final retrain? (no spend)

Measured on T3's own problems with the reference tables ($0, `calc3_d3probe.json`): the guess is corrected on 176 of
619 quotient digits in division (28%) and 192 of 329 root digits (58%); every correction is a wasted multiply-subtract
pass plus an add-back, about 0.6 s in a division and 1.2 s in a square root (regression on the cost model). A base-10
simulation of the same problems says Knuth's D3 test makes the guess exact for T3's divisors (two digits at most) and
cuts the square root's too-high guesses from 45% to 7%; 90% fewer corrections would bring the modelled √ maximum from
17.8 s to under 10 s. But D3 reads five digits (two of the divisor, three of the remainder) and a view holds three, so it
is a new table and a new step in both procedures: a retrain (E7's training run was $1.3 of H100, its smoke run $0.3),
the server certificate, a rebuild, the CPU identity test ($0.44), the M4 certificate and another Hugging Face revision,
about $2–3 and half a day, for 16 of 200 problems that are exact and only slow. A runtime-only D3 from the certified MUL
and SUB rows is possible at $0, but it adds about two calls per digit: it gains nothing in division and about 3 s on the
√ tail. Recommendation: fold D3 into the final retrain, after a dry run of the new table in the reference runtime; until
then the √ tail stays.

## Spend and Modal calls

| Job | Call id | What | Cost |
|---|---|---|---|
| `e7smoke_20_1401` | `fc-01M672ZV9KK296RQJ3EEVTX0N6` | 20 steps from E6 s3 and one certificate: the wiring (2,446 rows; 1,877 certified at step 20) | 4.1 min H100, about $0.27 |
| `e7_s3_4000_h4.0_stop3.0_fast` | `fc-01M673S1J9D0G42QCNBHE8RFS9` | E7: 1,600 steps (stop rule), certificate, end-to-end runs | 19.8 min H100, about $1.30 |
| `compile_baseline_1435` | `fc-01M674Y4EY2AXDY80AMHJJS18G` | compile baseline, stock then E7 | 11.5 min H100, about $0.76 |
| `e7pad_1437` | `fc-01M67526PSNKA5JHY1F68BN9WF` | SUM rows padded vs unpadded | 1.2 min H100, about $0.08 |
| `e7gate_1852_100_0` | `fc-01M67KN62ZZ9HGXZCRXV8EST3K` | gate identity smoke (1 prompt, 27 rows), CPU | 51 s × 8 CPU, about $0.01 |
| `e7gate_1854_8_0…7` | `fc-01M67KRHGCMJSS1CSJ319VVG7S` … `fc-01M67KRJKJF911XVM0RZFPBCNH` | gate identity, 8 CPU shards | 46 min × 8 CPU in all, about $0.43 |
| **total** | | | **about 37 min of H100 and 47 min of 8-CPU containers, about $2.8** (H100 at $3.95/h; CPU at 8 cores and 24 GiB) |

## Glossary candidates

- **Knuth's algorithm D** (Knuth, *The Art of Computer Programming* vol. 2, §4.3.1, 1969): long division of
  multi-digit numbers where each quotient digit is guessed from the top two digits of the remainder and the top digit
  of the divisor, after scaling the divisor so its top digit is at least half the base; the guess is then never too
  low and at most 2 too high, so a short correction loop makes it exact. Why it matters to us: it turns division into
  three small certified tables (EST, SUB, DEC) on top of the multiplier.
- **Normalisation (of a divisor)**: multiplying dividend and divisor by the same small factor so the divisor's first
  digit is 5 or more; the quotient is unchanged and the remainder is scaled by the factor. Why: it is what makes the
  three-digit guess table (EST) enough.
- **Digit-by-digit square root** (the schoolbook method, known since antiquity, in Europe from the 16th century):
  bring the number down two digits at a time; the next root digit y is the largest with (20 p + y) y ≤ remainder,
  p the root so far. Why: with the same scaling trick (here c² with c ∈ {1, 2, 4, 5}) its guess is division's guess.
- **Speculative vs dependent steps**: a view may share a decoder call with another only when it does not read a cell
  the other writes; the calculator rides a guess along with the last step of the trial divisor, never with a step
  whose outcome could make the guess's view meaningless. Why: calls are a third to a half of the cost on the M4.
- **Wave (on the sheet)**: several independent procedures run at once, each step of all of them read by the model in one
  batched forward pass; a step waits until every procedure under way has asked for its next one. Why: PROGRAM's algebra
  is many small independent calls, and on the M4 a call's fixed cost is about two views' worth.
- **WebGPU device loss**: the browser can withdraw the GPU from a page (driver reset, background tab, memory); every
  later call fails until the page asks for a new device and loads the model again. Why: it stopped T3 three times with
  the Browser pane hidden, and the page should recover from it by itself.

## Commits on `sketchpad` (CALC stream)

`8217fb02` E7 registration and tables · `ed05b216` the calculator runtime and tests · `da26e7b9` Calculate mode and worker ·
`4a1f974f` E7 result · `efd750bb` merge of `main` (gate wiring) · `9dc90ca3` waves and the padded prompt form ·
`4450ea06` E7 build artefacts and logs · `768cb9a2` taller calculator sheet · `d19a41e6` compile baseline and job logs ·
`27cfbf80` T3 and the report · `b244012a` this list · merge of `main` (fast-forward to `d5eb4d79`) · the gated E7 published (this section's commit).
