# SKETCHPAD2: the layout is the program

Fable, 29 Oct 2026, after E2/E3 (242/242 rows, 1,000-digit sums, on-device re-certification, min margin 0.59). Two pages.
Nothing run.

## 1. Control: kill the Turing head, keep the canvas as the whole state

A 2-D Turing machine with its state drawn as a glyph is clean and its table is tiny (|Q|×|G| rows), but it is Savant
with a two-dimensional tape: one cell per view, O(n) head travel per digit, O(n³) ticks for an n×n product, and nothing
a picture gives you is used. What a picture gives you is that **operands sit where the step needs them**. So control is
position: the cursor's column is the loop index i, its row (the multiplier digit it is on) is j, and the end of a loop
is a boundary glyph the fovea sees, not a counter. The program Π shrinks to a layout plus a cycle of opcodes, and each
tick's output includes a *move/next-opcode token*, so the runtime applies moves blindly and holds no loop knowledge. The
runtime is still a cropper (template cells relative to the cursor and the row/column headers), a painter and a window.
Draw the cursor mark and the next opcode in a status row too: purely display plus a consistency assertion, but it makes
the picture the complete state, so a paused run can be resumed from its own screenshot. The honest sentence for the
paper: a tick is a certified lookup over a small view, as in Savant; what is new is that memory and control are
spatial, gathered by the eye, and the state is the picture you edit.

## 2. Long multiplication, first program

Interleave multiply and add per column. No stack of partial products: one scratch product glyph, two travelling carries,
one running result row. The 242-row adder is reused verbatim (its view is carry, top, bottom).

```
row 0  status:  ▲ under cursor column, next-opcode glyph        (display + assertion)
row 1  a        multiplicand, right-aligned, n digits
row 2  b        multiplier, right-aligned, m digits
row 3  cM       multiplication carry (one moving glyph)
row 4  p        product scratch (one moving glyph)
row 5  cA       addition carry (one moving glyph)
row 6  R        running result, n+m cells, blank = 0
```

Pass j (multiplier digit b_j), columns x = j … n+j from the right:
- **MUL** at x: view = [a_{x−j} (row 1), b_j (row 2, anchored by j), cM(x)] → write p(x), cM(x+1); next op A.
  Table 11 × 10 × 11 = **1,210 rows** (a and cM include blank). The blank a cell at x = n+j is the flush.
- **ADD** at x: view = [cA(x), p(x), R(x)] → write R(x), cA(x+1); next op M, or F when a_{x−j} was blank. The existing
  **242 rows**; cA ≤ 1 always because p + R + cA ≤ 19, and the MUL carry ≤ 9 rides inside p.
- **FLUSH** at n+j+1: view = [cA, R] → write R; next op N. A 22-row sub-table of ADD with p blank.
- **NEXT**: view = [b_{j+1}] → "continue to row j+1" or "H". **11 rows.**
Total about 1,480 rows, certified once per device; on the M4 at ~0.25 s per row that is six minutes in the background,
or server-side with a device spot check of every table's lowest-margin decile.

Ticks: 2n² + 3n for n×n (44 for 4×4, 90 for 6×6, 230 for 10×10). At the §4 tick cost that is 11 s, 23 s, 1 min. The
demo shows 4×4 and 6×6 live; 100×100 is 20,000 ticks and is not a live demo, say so on the page.

## 3. Where the glance helps without touching exactness

The glance is a separate call with the whole canvas at low resolution; it never enters a certified tick's context.
It does four things. (i) **Layout and program choice**: from the typed or photographed problem it emits the header
(program name, n, m, where a, b, R go); the runtime draws the operands from text exactly, from a photo through
perception, which is the labelled boundary. (ii) **Readout for chat**: do not let it read R; whole-row reading is 98.5%
per digit (PROBES). The answer is read cell by cell with a 12-row READ table, or not read at all, since the canvas is
the answer. (iii) **Recovery**: after a user edit it may re-plan (which pass to redo); the certified rows then run.
(iv) **Halting** stays certified (NEXT); the glance may only propose stopping. Test for leakage: blank or shuffle the
glance image (the Wang 2608.06270 control) and confirm every certified tick is bitwise unchanged.

## 4. Prompt and tokens per tick

Prefix cached once per run: system line, program header, glyph legend. Per tick, uncached: one opcode token, the fovea
strip (three cells, three vision tokens, plus image delimiters), the assistant start; about 12 tokens. Output: two glyph
tokens and one move/next-op token, from a closed set of ~8 (left, next-row, halt, with the next opcode folded in).
Cost from the measured numbers: 12 × 3.5 ms + 80 ms + 2 × 60 ms ≈ **0.25 s per tick**, so about four ticks a second;
the call overhead and the extra decode tokens dominate, not the prompt. One *call* per tick, three decode forwards; a
single-forward tick would need the glyph pair and the move in one token, and Qwen tokenises digits singly, so do not
chase it. The move token is part of the certified output string, so a wrong move is a failed row, not a runtime bug.

## 5. Failure modes and kill tests

| Failure | How it shows | Kill test, and the fix if it fails |
|---|---|---|
| MUL strip roles confused (a, b, cM from three rows) | rows < 1,210 or min margin < 1 | full-domain hinge every step (O3); kill if not 1,210/1,210 by step 600; if margin only, hinge 4 |
| On-device drift | server rows pass, device rows flip (E3: 3.56 → 0.59) | re-certify all tables on the device after every export; kill if any row flips; fix: fp16 decoder or hinge 4 |
| Runtime, not model (offsets, anchors, sweep) | long products wrong with all rows certified | **table dry run**: drive the same runtime with the reference tables in place of the model; must reproduce the truth before any model run |
| Sprite or preprocessing change (the do_normalize gotcha) | rows flip after a UI change | pixel-hash sprites and the preprocessor config into the certificate's header |
| Retention with 1,480 rows | perplexity ratio > 1.05 (242 rows gave 1.007) | predicted ≤ 1.03; kill at 1.05; raise text fraction, lower LoRA rank |
| Glance leakage | certified ticks change when the glance is blanked | §3 control; fix: separate calls, separate cache |
| Wrong layout header | exact arithmetic on the wrong problem | report compile accuracy separately from executor exactness; show the parsed problem before running |
| Photo misread | wrong operands | labelled boundary; UI confirms the digits it read |
| Stale glyphs | cluttered canvas, no effect on rows | clear cM, p, cA behind the cursor with a blank write; costs nothing certified |
| Speed | 10×10 feels slow | cache the prefix, drop the status row redraw to every 5 ticks; never fake a tick |

Predictions to register before E4: MUL 1,210/1,210 by step 400 with min margin ≥ 2 on the server and ≥ 0.5 on device;
4×4, 6×6 and 10×10 products exact 20/20 each through the runtime; retention ≤ 1.03; mid-run edit of an unread a-digit
followed exactly; ~0.25 s per tick in the browser.
