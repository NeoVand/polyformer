# CALC brief: the calculator on the sheet (T1–T3)

Read first: `research/meta/sketchpad3/CONTRACT.md` (rules, seams, your files), then `research/meta/SKETCHPAD3.md` §2 and
§6 items 1–3, then `research/sketch/calc_dryrun.py` (the procedures and tables you implement, already exact with
reference tables). Your worktree: `/Users/neo/repos/polyformer-wt/sketchpad`, branch `sketchpad`. Log:
`research/sketch/CALC3.md`. Modal spend cap: **$15**.

## What exists

- The page runtime: `src/lib/sketchpad/` (`adder.ts`, `multiplier.ts` with `reference()`, `pad.svelte.ts` drives
  procedures and waves, `worker.ts` runs the ONNX model, `protocol.ts`, `models.ts`, `runtime.spec.ts`). Two tables are
  learned and certified on all 1,795 views: ADD (242) and MUL (1,100), one adapter, E6 seed 3
  (`research/sketch/e6_slots.py`, recipe v2; Modal app `research/sketch/modal/`, `launch.py` job types).
- The program folder build: `research/sketch/build_program.sh` (adapter → ONNX program graph, inside assets,
  certificate); local model files in `static/sketchpad/models/` (never committed); `pnpm dev` serves them.

## T1: runtime ($0)

1. New layouts in the TypeScript runtime, following the existing adder/multiplier pattern (each step is one model call on
   a three-cell view; the model also writes the next-step token where the procedure branches):
   - **SUB**: column subtraction with borrow; signed add and subtract on top (the final borrow says which magnitude is
     larger; swap and set the sign, layout only).
   - **Division**: Knuth's Algorithm D as in `calc_dryrun.divide`: normalise the divisor (first digit ≥ 5) with one
     multiply pass, guess each quotient digit with EST, multiply-and-subtract, and when the borrow comes out set, DEC
     the guess and add the divisor back.
   - **√**: digit by digit as in `calc_dryrun.sqrt_digits`, with c² normalisation (c ∈ {1, 2, 3, 5}) so a guess is at
     most 2 too high; divide by c at the end.
2. A sheet-backed implementation of `Calc` (CONTRACT seam 2) that the PROGRAM stream's parser will call. Put it in
   `src/lib/sketchpad/sheet-calc.ts`; copy the interface into it with a comment that the canonical copy lives in
   `program/calc.ts` (PROGRAM's branch), so the two compile apart until the orchestrator merges.
3. With reference tables in place of the model: exact on 1,000 random instances per procedure (vitest), including
   signs, zeros, equal operands, divisors longer than the dividend, and 40-digit operands.
4. A minimal way on the page to type `a − b`, `a ÷ b` (to k places) and `√a` and watch it run. Keep the page's design
   rules: dark monochrome, compact, no boxes or chips, aligned. The full demo page comes later; do not redesign.

## T2: retrain E7 (about $5)

- Rows: the SUB (242), EST (the views met with normalised divisors, about 400; enumerate them all), DEC (9) tables plus
  any control-step views the new procedures add, on top of ADD and MUL: about 2,500 rows in all. E7 starts from E6
  seed 3 with recipe v2 (same LoRA: r16, alpha 32, language layers only).
- Register in `CALC3.md` before launching: the kill line is *not every row certified by 4,000 steps, or plain-text
  perplexity above ×1.02 of stock*. Predict the step at which all rows certify and the minimum margin.
- Certify every row of every table on the server (the same margin test as E6), then build the program folder with
  `build_program.sh` into `static/sketchpad/models/arithmetic-e7/` (do not overwrite `arithmetic/`, which the live
  page mirrors) and point the dev page at it.
- Also run the `compile` job on E7 (the language baseline in `research/sketch/compile_baseline.py`, about $1) so the
  record shows whether E7 hurts chat more than E6 did (E6: plan 0/60, equation 0/60, word 1/60; stock 15, 0, 44).

## T3: on device ($0)

On the M4 page (`pnpm dev`, run in the background; or the `sketchpad` entry in `.claude/launch.json`), with E7: 50 each
of division to 10 places, √ to 6 places, gcd (repeated division), and signed sums and differences, all exact, each under
12 s; and the full certificate re-run in the browser (all rows, every margin positive). Record each time and failure in
`CALC3.md`.

## Optional, only after T3 passes

`patch_onnx_inside.py`: slice the graph's `hidden_states` output to the one row the inside view shows, so capture costs
almost nothing (today 50 ms per call plus 12 ms per row when on; `b80727e4` already skips it when off).

## Notes

- The CHAT stream will add a gate input to `patch_onnx_lora.py` (stock Qwen at gate 0). Build E7 without it; the
  orchestrator rebuilds with the gate after merging.
- Done = T1, T2, T3 pass (or a kill line fires and you stop and report), committed on `sketchpad`, with the final report.
