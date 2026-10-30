# SKETCHPAD3 contract: what the three work streams share

Neo said go on 30 Oct 2026 for the calculator and algebra (T1–T3, T6), the chat fine-tune and gate (T4–T5), and the
page fix. The plan is `research/meta/SKETCHPAD3.md` (read §2–§6 only); this file fixes the seams between the streams.
The orchestrator (the parent Claude session) merges the branches, edits `GLOSSARY.md`, uploads to Hugging Face and
pushes. **No stream pushes, uploads to Hugging Face, touches `main`, or edits another stream's files.**

## Streams, owners, files

| Stream | Worktree (branch) | Owns | Brief |
|---|---|---|---|
| CALC (T1–T3) | `/Users/neo/repos/polyformer-wt/sketchpad` (`sketchpad`) | `src/lib/sketchpad/**` except `program/`; `src/routes/sketchpad/**`; `research/sketch/**` except `chat/` and `patch_onnx_lora.py`; Modal app `polyformer-sketch` | `CALC.md` |
| PROGRAM (T6 + parser) | `/Users/neo/repos/polyformer-wt/program` (`program`) | `src/lib/sketchpad/program/**` (new) | `PROGRAM.md` |
| CHAT (T4–T5) | `/Users/neo/repos/polyformer-wt/chat` (`chat`) | `research/sketch/chat/**` (new), `research/sketch/patch_onnx_lora.py`; Modal app `polyformer-chat` (may read the `polyformer-sketch` volume, writes only its own) | `CHAT.md` |

Each stream keeps a log in its own folder (`research/sketch/CALC3.md`, `src/lib/sketchpad/program/NOTES.md`,
`research/sketch/chat/CHAT3.md`): decisions, numbers, Modal call ids and spend, and a section **Glossary candidates**
(term: what it is, who/when, why it matters to us) that the orchestrator lifts into `research/meta/GLOSSARY.md`.

## Seam 1: the digit tables (CALC trains them; everyone else may assume them)

Exactly the functions in `research/sketch/calc_dryrun.py`: `t_add`, `t_mul` (shipped), and new `t_sub(w, t, b) -> (digit,
borrow)`, `t_est(r_hi, r_lo, d_hi) -> min(9, (10 r_hi + r_lo) // d_hi)` with `d_hi >= 5` (normalised divisor), and
`t_dec(q) -> q - 1`. CALC records how each view is drawn and prompted (word, cells, answer tokens) in `CALC3.md`.

## Seam 2: `Calc`, the sheet as an arithmetic unit (CALC implements on the sheet; PROGRAM builds on it)

```ts
// src/lib/sketchpad/program/calc.ts (PROGRAM writes this file; CALC implements the interface elsewhere)
export interface Calc {
	add(a: bigint, b: bigint): Promise<bigint>; // signed
	sub(a: bigint, b: bigint): Promise<bigint>; // signed
	mul(a: bigint, b: bigint): Promise<bigint>; // signed
	divmod(a: bigint, b: bigint): Promise<{ q: bigint; r: bigint }>; // a >= 0, b > 0, 0 <= r < b
	isqrt(a: bigint): Promise<{ root: bigint; rem: bigint }>; // a >= 0, root = floor(sqrt(a)), rem = a - root^2
}
```

- Integers only. Decimals, signs of quotients, scaling for "to k places" and decimal points are layout, done by PROGRAM
  on top of `Calc` (division to k places is `divmod(a·10^k, b)`; √ to k places is `isqrt(a·10^(2k))`).
- Every `Calc` call on the sheet is certified step by step (the model writes every digit). Anything above `Calc` is the
  fixed runtime and must be shown on the page as such.
- PROGRAM ships a reference `Calc` (BigInt) that also counts sheet rows and calls with the costs in `calc_dryrun.py`, so
  its tests report the seconds a procedure would take on the M4.

## Seam 3: the work order (CHAT trains the model to write it; PROGRAM parses and runs it)

The model writes a fenced block in its reply. The runtime stops generation at the closing fence, runs the block on the
sheet, appends one result line, and lets the model continue.

````
```sheet
1234 × 5678 − 99
```
= 7006553
````

Statements, one per line:
- an expression: integers and decimals; `+ − × ÷ ^` (integer exponent ≤ 12), brackets, unary minus, `√(…)`,
  `gcd(a, b)`; an optional trailing `to k places` sets the decimals of every `÷` and `√` in the line (default: exact
  if the division ends within 12 places, else 12 places, marked `…`);
- `name = expression`, then `name` may be used in later lines;
- `solve <equation>` in one unknown (`x`), polynomial of degree ≤ 2, `x` on either side, brackets allowed;
- `solve <eq1>, <eq2>[, <eq3>]`, a linear system in `x, y[, z]`;
- `expand <polynomial in x>` (powers up to 12, integer coefficients);
- `factor <polynomial in x>` (integer roots by guess-then-prove; what is left stays unfactored).

ASCII spellings are accepted and normalised: `* / - sqrt( )`. The result line is `= <value>` for one line, else one
`= ` line per statement; for `solve`, `x = …` (exact fractions in lowest terms, plus a decimal to 6 places when not an
integer); a refused check prints `check failed` and the model must not claim an answer.

**Who does what.** The model's job is the translation: decide to open the sheet, and write the line (the expression from
the words, or the equation as typed). The fixed runtime substitutes evaluation points, applies precedence and schedules
the `Calc` calls; it never computes a digit. This is a decision of 30 Oct (orchestrator): it replaces the plan's
"one operation per line" and "substitution by the model" with a parser, because algebra by evaluation needs the
scheduler anyway. CHAT keeps a flag in its data generator for the older format (one binary operation per line,
`t1 = a op b`), so that format is one retrain away if Neo prefers it.

## Rules for every stream

- Model runs go on Modal, not the M4 (Neo, 30 Oct). The M4 is for the browser page and pure dry runs.
- Register predictions and kill lines in your log before spending; spend caps are in each brief.
- `nice -n 19` for local CPU work; `/bin/rm`, never `rm`; never commit model files (`*.onnx*`, `*.safetensors`, `*.pt`).
- Never print or commit keys (`~/.polyformer_keys`, `~/.cache/huggingface/token`).
- Never run a blocking long-lived command (dev servers, `modal run` without `--detach`, waits): background them and
  poll with short calls. Modal: `modal deploy` then `.spawn()`; collect with `modal.FunctionCall.from_id(id).get(timeout=…)`
  and `modal volume get`. A warm container may serve old code after a deploy: `modal container list`, stop stale ones.
- Commit to your own branch only, in small commits, with the attribution line
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` (Claude streams).
- Before you claim a result, re-check it (rerun the test, reread the number at its source). Report failures plainly.
- Finish with a short plain report (what passed, what failed, numbers, spend, commits) as your final message, and the
  same at the top of your log. No interim messages unless blocked.
