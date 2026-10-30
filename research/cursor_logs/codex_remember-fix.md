Committed as `45fba394`. All jobs settled; working tree clean.

Unaudited fair-test results, exact runs out of 9 per cell:

| Model | Arm | Policy | 256 | 1024 | 4096 |
|---|---|---|---|---|---|
| Qwen3-1.7B | pin | pin | 9/9 | 9/9 | 9/9 |
| | pin | remember | 0/9 | 0/9 | 0/9 |
| | pin | tok | 9/9 | 9/9 | 9/9 |
| | pin | adv | 5/9 | 3/9 | 0/9 |
| | history | pin | 9/9 | 9/9 | 9/9 |
| | history | remember | 9/9 | 9/9 | 8/9 |
| | history | tok | 9/9 | 9/9 | 9/9 |
| | history | adv | 7/9 | 6/9 | 1/9 |
| Qwen3-4B | pin | pin | 9/9 | 9/9 | 9/9 |
| | pin | remember | 0/9 | 0/9 | 0/9 |
| | pin | tok | 9/9 | 9/9 | 9/9 |
| | pin | adv | 4/9 | 2/9 | 0/9 |
| | history | pin | 9/9 | 9/9 | 9/9 |
| | history | remember | 8/9 | 6/9 | 5/9 |
| | history | tok | 9/9 | 9/9 | 9/9 |
| | history | adv | 9/9 | 9/9 | 4/9 |

History is learnable under this recipe; exclusive pin learnability is unsupported. All 432 JSON/CSV cells agree.

Settled estimated spend: **$23.862331 / $35**, including smoke, timeout, and retry.

[Full report, first errors, and bitwise counts](/Users/neo/repos/polyformer-wt/remember/research/remember/REMEMBER2.md:342).