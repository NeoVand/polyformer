# SKETCHPAD3: a calculator-complete, algebra-capable page that one model decides to use (Fable, 30 Oct 2026)

Grounded in REPORT.md "Inside" and "E6" (one union LoRA r16, language layers only; 1,795 rows, min margin 3.35,
perplexity ×1.007; one forward pass per step with the prompt ending `=??`; M4 fp16: 6×6 in 5 s, 10×10 in 11 s, 12×12 in
19 s; device margins add 5.58, multiply 3.53; retrain $2–5). Estimates below use a cost model fitted to those three
times: **wall time ≈ 0.1 s × batched calls + 0.035–0.043 s × certified steps**; the decoder is compute bound, so batching
saves only the 0.1 s per call and the step count is what matters. The orchestrator's table dry runs (calc_dryrun.md)
should replace my step counts where they differ. "Progressive kind" I read as Neo did in this session: progressive
networks (Rusu 2016, frozen columns plus gated lateral connections); §3 says where that reading helps and where it is
unnecessary.

## 1. The factorisation: four digit tables, three tiny control tables, everything else is layout

Field: computer arithmetic (Knuth, TAOCP vol. 2 §4.3). Every calculator operation is a pen-and-paper algorithm whose
steps are digit-local once the operands are laid out; the non-local steps (quotient digit, root digit) become local by
trial or by a bounded estimate. The step format stays `op view =??` for every table, so the whole calculator is one
executor over one prompt shape (condition 7).

| Table | View → write | Rows | Status |
|---|---|---|---|
| SUM | carry, top, bottom → digit, carry | 242 | have |
| MUL step | a digit, b digit, carry → product digit, carry | 1,100 (+ADD/ADZ 440, FLS 2, NXT 11) | have |
| **SUB** | borrow, top, bottom → digit, borrow | 242 | new |
| **Q̂** (optional, speed) | two leading remainder digits, leading divisor digit → trial quotient digit | 900 | new |
| **SIGN** | sign a, sign b, op → which program, result sign | 8 | new |
| **HALF** (optional) | remainder in, digit → quotient digit, remainder out | 20 | new |
| **READ** | one cell → one token for chat | 12 | new |

Union without the optionals: **2,057 rows** (one retrain, $2–5); with both: 2,977. Comparison is free: SUB's final
borrow is "a < b", so CMP needs no table. Decimal points and signs are glyphs the layout aligns; SUM and SUB get two
pass-through rows each for `.` if we want the point inside the certified strip, otherwise the runtime places it from the
header (a calculator's display logic, not a learned step; labelled as such).

**How each operation reduces, with demo-size cost (steps; seconds from the model above):**

| Operation | Program over the tables | Steps for a demo instance | Est. time |
|---|---|---|---|
| a + b, a − b (signed) | SIGN once; SUM or SUB pass; if SUB borrows out, one complement pass (SUB from zeros) and flip the sign | 12-digit: 13 (+13) | 2 s (4 s) |
| a × b | have; MUL/ADD wave | 8×8: 2·64+24 = 152 | 6 s |
| a ÷ b, k decimals | long division; each quotient digit by **trial subtraction** (SUB passes until borrow out, then one SUM pass back) or by **Q̂ + one MUL pass + one SUB pass** (Knuth's Algorithm D after normalising the divisor's lead digit ≥ 5, correction ≤ 2) | 8÷3 digits to 4 places, m = 3: trial ≈ 9·(4·4.5)·4 = 650 worst, ~330 typical; Q̂ path ≈ 9·(2·4+3) = 100 | 12 s / 4 s |
| x % of y, +x %, −x % | MUL then point shift; SUM or SUB | 6×3 digits: 54 + 10 | 3 s |
| a^k | square-and-multiply: ≤ 2·log₂k products, sizes growing | 7^20 (17 digits): 5 squarings + 2 products ≈ 400 | 15 s |
| √N to k places | digit-by-digit root: bring down a pair; find the largest x with (20P + x)·x ≤ remainder by estimate (Q̂-style) plus ≤ 2 corrections; each trial is a one-digit MUL pass and a SUB pass | √2 to 6 places: 6 digits × ≈ 4·(m+1), m ≤ 7 ≈ 190 | 8 s |
| p/q ± r/s, ×, ÷ | three MUL passes and one SUM/SUB, then reduce by gcd | 4-digit terms: 3·(2·16+12) + 9 ≈ 140 + gcd | 6 s + gcd |
| gcd(a, b) | Euclid by division (above), or Stein's binary gcd with HALF and SUB only (no estimate, no multiply) | 4-digit pair: Euclid ≈ 4 divisions ≈ 120; Stein ≈ 20 rounds × 5 ≈ 100 | 5 s |

Two honest limits. **Live size:** at 35–43 ms per certified step, anything under about 300 steps runs in ≤ 12 s: × and ÷
stay at ≤ 10–12 digits on stage, + and − can go to 100 digits (4 s), 1,000-digit sums are a background piece. **The lever
is tokens per step, not batching:** the fovea costs 3 vision tokens and about 7 text tokens; cutting the text to 3 is a
30–40% speedup for free. Base 100 (two digits per cell, 20k SUM rows certified server-side, spot-checked on device)
halves every step count later. Carry-lookahead (Kogge–Stone) cuts calls, not rows, and the decoder is compute bound:
it buys nothing here.

## 2. Algebra: canonical forms first, rewriting second

Field: computer algebra. Every CAS keeps polynomials in a canonical form (a vector of coefficients) and uses term
rewriting only for the expression tree above that. We should do the same, because the canonical form needs **no new
tables**: it is arithmetic laid out in two dimensions.

- **Coefficient grid.** A polynomial in x is a row of columns, one per degree; each coefficient is a signed number written
  vertically in its column. Addition is SUM per column. Multiplication is "polynomials as numbers without carries"
  (Kronecker substitution undone): the long-multiplication wave with the carry between columns switched off, which is a
  layout flag, not a table. (x + 2)(x − 3) is a 2×2 wave of one-digit products plus two SUM passes: ≈ 12 steps.
  Derivatives of polynomials: MUL of each coefficient by its degree and a shift: layout plus one MUL pass per column.
- **Linear equations and systems.** ax + b = c is SUB then DIV, two lines on the page (PENPAPER §2). Systems: Gaussian
  elimination as row operations, each "multiply row i by a number and subtract from row j" is one MUL pass and one SUB
  pass per column; fraction-free (Bareiss) keeps everything integer until one final division per unknown. 2×2 and 3×3 in
  under 300 steps.
- **Quadratics.** b² − 4ac (two MUL, one SUB), √ by §1, then two SUB/SUM and two DIV passes. Exact when the discriminant
  is a perfect square (√ terminates with zero remainder, a certified halt); otherwise k decimals, labelled as such.
- **Factoring and "guess, then prove".** Integer roots of a monic polynomial lie among the divisors of the constant term
  (rational root theorem). The model proposes candidates; each is checked by **Horner evaluation on the page** (MUL and
  SUM passes), which is certified. The strategy is uncertified and cannot hurt the answer: a candidate is a root only if
  the certified check says zero. This is the one safe place for the LM's judgement, and it is the demo's cleverest beat:
  a small model guessing like a student and the page proving or refusing each guess.
- **Check by substitution** closes every algebra problem: substitute the solution into the page's own copy of the
  equation and run the arithmetic. Certified. It does **not** certify transcription (is the drawn grid the equation the
  user typed?); that stays visible and uncertified: the drawn problem is shown before the run and READ reads it back.

**Certified:** every digit written in +, −, ×, ÷, √, gcd, polynomial arithmetic, elimination and Horner checks, and
every halt decided by a boundary glyph. **Not certified:** which procedure runs, the transcription, and any candidate
before its check. **Term rewriting on a record heap (PENPAPER §5)** stays the route to general expressions (nested
fractions, trig identities, derivatives of compositions); its pointer-following interpreter over a ~60-glyph alphabet is
of unknown learnability at 0.8B, so it is the second milestone, and the interaction-net reducer (§6) is the architecture
note, not the demo.

## 3. One model that decides to use the page

Field: tool-use training (Toolformer 2023: insert tool calls into text, keep the ones that lower loss; function-calling
SFT), and continual learning for the "do not forget language" half (progressive networks 2016, adapter gating 2024).
The mechanism is the same in every option: the assistant emits a page block, `⟦page op=mul a=48273916 b=7391048⟧`, the
runtime draws it, the certified steps run, the READ rows return the result into the turn, and the model continues in
words. Training data is synthetic dialogue generated by code: problems that need the page, problems that do not
(distractors, so it learns when **not** to), problems inside prose, and problems the user corrects on the page. The
score that matters is page-use precision and recall and transcription exactness on **held-out templates**.

| Option | Mechanism | Breaks | Buys | Verdict |
|---|---|---|---|---|
| **A. One always-on LoRA** (E6 plus chat-with-page SFT in the same adapter) | one set of weights for steps and for deciding; nothing to switch | risks 9 (language) and 5 (margins may move; re-certify) | simplest; one retrain $5–10; the ONNX graph unchanged | **first** |
| **B. Hard-gated column** (same LoRA, a 0/1 gate input scales its delta; gate 1 when a fovea prompt is present) | gate 0 is bit-identical stock Qwen; gate 1 is the certified machine; chat still has the gate on, so the decision is the model's | none in form; arguably 1 if a second "chat" adapter is ever added (do not) | zero language regression in stock mode by construction; the certificate has a fixed state; a stage beat ("switch the page off") | **add to A** ($0: one graph input, as `steer` was) |
| **B′. Learned soft gate / progressive columns** (Rusu's frozen columns with lateral connections) | router decides when to engage the column | 5 if the gate sits inside a certified step (soft gate, no finite certificate) | emergent engagement (condition 3) | not needed: new abilities arrive as certified programs, not new training, so there is nothing to forget; keep the gate hard |
| **C. Larger base** (4B) | better compiler and transcription | 11 at demo sizes (steps cost ~4×: 12×12 at ~75 s) | fewer transcription errors | only for the compiler if 0.8B fails T4; then page steps still on 0.8B = option D |
| **D. Two models** | a talker and a page model | 1 and 2 in spirit ("not that different from tool calling") | everything practical | rejected by Neo; listed for completeness |

Recommendation: A with B's gate, on the 0.8B. Progressive networks are the right name for what the gate does
(a frozen base plus a column you can switch), and the wrong tool for the forgetting problem we do not have: the
interpreter adds skills by certification. RL for "emergent unprompted use" (condition 3) comes after SFT, with the exact
answer as reward and page use unpenalised; on a 0.8B it is cheap and risky to language, so gate it on T4 passing.

## 4. The demo script (one page, one model, one chat box)

Every beat live on the laptop GPU, ≤ 12 s, labelled certified or not, nothing precomputed:

1. **A normal model.** A short poem. The stock-mode toggle is visible, off.
2. **It decides.** "What is 48,273,916 × 7,391,048?" The model writes the page block in its own turn; the wave runs
   (152 steps, ~6 s); the result returns cell by cell and the model says it. Caption: views checked on this device, min
   margin.
3. **The page is the state.** Mid-run the viewer changes a multiplier digit; the run follows. "Check it": division back.
4. **Money.** "$1,249.99, 15% off, then 8.25% tax?" Three chained operations, decimals and percent, 5 s.
5. **Algebra.** "Solve 3x + 7 = 2026." Two drawn lines, long division, x = 673, substitution check green.
6. **Guess and prove.** "Factor x² − x − 6." The model proposes ±1, ±2, ±3, ±6; Horner on the page refuses four and
   accepts 3 and −2.
7. **√2 to six places** (190 steps, ~8 s), squared check.
8. **Inside.** The lens and the layer-20 push, 80/80.
9. **Switch it off.** Beat 2 with the gate at 0: stock Qwen 0.8B is wrong. Gate 1: exact. Then the honest line: tools
   do this too; nobody has done it inside the forward passes with a certificate you re-run on your own GPU.

Covers for disappointment: sizes under 300 steps and the wave as the spectacle; the drawn problem shown and correctable
before the run; a labelled "use the page" button if the model fails to decide; beat 1 and the toggle for language;
captions that name what is certified.

## 5. Registered first tests, kill lines, dollars

| # | Test | Prediction | Kill | $ |
|---|---|---|---|---|
| T1 | Table-driven dry runs through the runtime: long division (both quotient methods), √, gcd (Euclid and Stein), coefficient-grid expansion, 2×2 elimination, Horner check; 1,000 random instances each | all exact; step counts within 20% of §1 | any program that cannot be made exact with reference tables ⇒ redesign its layout before training | 0 (orchestrator, in progress) |
| T2 | Union retrain with SUB, SIGN, READ (2,057 rows), recipe v2 | all rows, min margin ≥ 3, perplexity ≤ ×1.01 | < 2,057 rows at 4,000 steps or perplexity > ×1.02 | 2–5 |
| T3 | On-device end to end: 50 each of 8÷3-digit divisions to 4 places, √ to 6 places, 4-digit gcds, signed sums with complement | 50/50 each, ≤ 12 s | one wrong digit with all rows certified ⇒ a layout or runtime bug (Theorem P), fix before anything else | 0 |
| T4 | Chat-with-page SFT on the same adapter: 3,000 synthetic dialogues, 30% distractors, held-out templates | page-use precision and recall ≥ 0.95; transcription exact ≥ 0.9; perplexity ≤ ×1.02; GSM8K and MMLU within noise; all 2,057 rows re-certify at ≥ 3 | rows lost or perplexity > ×1.03 ⇒ the chat skill and the step skill fight; fall back to a separate decision adapter and report condition 1 as the cost | 5–10 |
| T5 | Gate input in the ONNX graph | gate 0 bit-identical to stock on 100 prompts; gate 1 certificate unchanged | any logit difference at gate 0 | 0 |
| T6 | Algebra on grids: 200 each of expansions, 2×2 systems, quadratics with square discriminants; 200 corrupted answers | all exact; the substitution check rejects 200/200 corruptions | a corruption that passes the check ⇒ the check layout is wrong | 0 |
| T7 | Q̂ and HALF tables (optional) | division 3× faster; rows certify | margins < 3 ⇒ stay with trial subtraction | 2–5 |

Total ≈ $10–25 plus the orchestrator's dry runs. Order: T1 → T2 → T3 → T6 → T4 → T5 → T7.

**Novelty claims for the live gate** (none said on the page before it survives): (1) a VLM runs calculator-complete
arithmetic, division, roots and gcd included, inside its own forward passes with a per-device certificate (search Goat
2023, MathGLM 2023, Abacus embeddings 2024, CAEF 2024, Giannou 2023, Nye 2021, Visual Sketchpad and Whiteboard-of-Thought
2024); (2) one model that decides mid-conversation to run its own certified program, not an external tool (Toolformer
2023, ToolRL and ReTool 2025, "internal tool" LMs); (3) guess-then-prove algebra with a certified checker in one model
(AlphaGeometry 2024, CAS-in-the-loop verification); (4) a hard gate giving bit-identical stock behaviour plus a certified
mode (X-LoRA 2024, adapter toggling, progressive networks 2016). (1) is the strong claim; (2) and (4) are engineering
firsts at best; (3) is a known pattern with a new checker.

## 6. Assumptions check

Assuming: the 0.8B is the model and the 4B is only a fallback compiler; ≤ 12 s per operation counts as not
disappointing; transcription and procedure choice may stay uncertified if visible and read back; "calculator" means
integers, decimals to k places and the operations listed, not repeating-decimal detection or scientific notation;
`.`, `−`, `/` and `√` may join the glyph alphabet; "progressive" means Rusu's networks; the orchestrator's dry-run step
counts override mine; nothing trains until Neo says go.
