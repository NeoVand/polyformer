# CALC3: the calculator on the sheet (SKETCHPAD3 T1–T3)

Log of the CALC stream (brief: `research/meta/sketchpad3/CALC.md`, contract `CONTRACT.md`). Newest results at the top
once they exist; the registration below was written before any spend.

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

## Spend and Modal calls

| Job | Call id | What | Cost |
|---|---|---|---|
