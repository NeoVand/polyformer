# Master ablation table (assembled 24 Oct ~10:50 from each domain's ABLATION_*.json)

Seeds exact (last-event full-state accuracy >= 0.99) at the long test length, out of 3. Long length = 64x training
(code, Lean, S5, stories) or 128x (addition, counting). Seed values in brackets where informative.

| arm | code execution | Lean chains | S5 words (mu 0.1, chosen on validation) | addition | counting | stories (certified) |
|---|---|---|---|---|---|---|
| O (output loss only) | 0 [.03 .03 .02] | 0 [.43 .00 .89] | 2 | 0 [0 0 0] | 0 [chance] | 0 [0 0 0] |
| O+N (+ fixed norm) | 0 [.76 .56 .48] | 3 | 1 | 3 | 1 | 0 [.59 .31 .67] |
| NS+N (+ next-state) | 0 [.97 .98 .87] | 3 | 3 | 3 | 2 | 0 [.96 .94 .96] |
| EQ+N (+ certified equivalence) | 3 | 3 | 1 (also 1 at mu 1) | 3 | 3 | 3 [1.0 .99 1.0] |
| **FULL+N** | **3** | **3** | **3** (1 at mu 1) | **3** | **2** [1.0 .984 1.0] | **3** |
| FULL (no closure) | 0 [.97 .84 .73] | 3 | 3 (2 at mu 1) | 0 [0 0 .74 at 32x] | 0 [chance] | 0 [0 .01 0] |

## Reading
- Ordinary training is exact nowhere except the easiest domain (S5, 2 of 3).
- Every partial recipe fails somewhere: O+N on code, S5, counting and stories; NS+N on code, counting and stories;
  EQ+N only on S5, where next-state is what it needs.
- Closure matters where the state can drift in scale: removing it breaks code, addition, counting and stories, but
  not Lean or S5.
- FULL+N is exact on 17 of 18 domain-seeds; the one miss is counting seed 1 at 0.984 (128x).
- The signal weight matters on S5 (mu 1 fails, mu 0.1 chosen on validation passes). Report both.

## Open cells
None in the ablation (the stories tracker always had the fixed norm, so its old 'none' and 'cert' arms are O+N and EQ+N). Language soft checker: soft 0.77-0.85, soft with wrong pairs
removed 0.78-0.83 (so the deficit is coverage, not wrong pairs, pending the write-up), consensus 0.18-0.23 (no bug: it fails because of
which stories the consensus accepts; STORIES §7).
