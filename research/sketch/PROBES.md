# Sketchpad probes, 29 Oct 2026 ($0, M4, Qwen3.5-0.8B untouched) — qwen35_reader.py / qwen35_reader.json

A written sum (two right-aligned numbers over a rule, Menlo font) rendered as an image; 20 examples per setting;
teacher-forced exactness; no thinking. Vision tokens from image_grid_thw (one token = 32x32 px; minimum ~64/image).

| digits | font | vision tokens | per digit | read both exact | per-digit read | direct sum | text read | text sum |
|---|---|---|---|---|---|---|---|---|
| 8 | 16-32px | 70 | 4.4 | 1.00 | 1.000 | 0.00 | 1.00 | 0.05 |
| 16 | 16-32px | 72-78 | 2.3-2.4 | 0.80-0.90 | 0.994-0.997 | 0.00 | 0.90 | 0.00 |
| 32 | 16/24/32px | 68/64/132 | 1.1/1.0/2.1 | 0.05/0.15/0.00 | 0.981-0.986 | 0.00 | 0.70 | 0.00 |
| 64 | 16/24/32px | 66/120/246 | 0.5/0.9/1.9 | 0.00 | 0.987-0.991 | 0.00 | 0.60 | 0.00 |

Reading: short canvases exact, long ones ~98.5-99% per digit (one slip per pair); copying long numbers from TEXT also
fails (0.60 at 64), so part of the limit is the 0.8B model's copying, not its eyes. Direct sums: zero from image and
text alike. A 64-digit pair fits in 66 vision tokens at 16px (0.52 tokens/digit, about 2x denser than text digits).
Implication: the reader must be local (a few cells per read) and trained to margin; whole-canvas reading is not exact.
