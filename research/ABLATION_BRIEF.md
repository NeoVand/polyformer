# ABLATION: one protocol, every domain (Nature list item 1; approved by Neo 24 Oct ~10:00, "get it done")

## Why
Reviewers will ask which ingredient does the work. Today the full factorial exists only for code execution. This
brief fixes one protocol so the paper has a single table, and Figure 1 is built on it.

## Arms (same names in every domain)
| arm | objective | closure |
|---|---|---|
| O | the domain's output loss only (next token / readout cross-entropy) | free |
| O+N | O | fixed norm (state RMS-projected to sqrt(d) after every step, or the domain's existing architectural equivalent; say which) |
| NS+N | O + next-state prediction | fixed norm |
| EQ+N | O + certified-equivalence term (no next-state) | fixed norm |
| FULL+N | O + next-state + certified-equivalence | fixed norm |
| FULL | O + next-state + certified-equivalence | free (shows closure is needed) |

Seeds 0, 1, 2 (or the domain's standard three; say which). Signal weight: the domain's registered default; S5 also
reports mu = 1 and mu = 0.1 and says which was chosen on validation, never on the test. Exact = last-event full-state
accuracy >= 0.99. Report exact at the training length and at 64x it (and 256x where it is cheap), plus the per-step
error p = 1 - E^(1/L) at the longest length.

## Reuse
Reuse every existing run whose configuration matches an arm exactly (cite the record). Run only the missing cells.

## Registration (before any spend, in your report, committed)
- A1. FULL+N is exact at 64x on 3 of 3 seeds in this domain.
- A2. O is not exact at 64x on at least 2 of 3 seeds.
- A3. FULL (no closure) is below FULL+N at 64x on the seed mean.
- Recorded, not verdicts: which of O+N, NS+N, EQ+N are exact. Across domains we expect each partial arm to fail
  somewhere and only FULL+N to hold everywhere; your domain's row is data for that claim, not a verdict on it.

## Output
A section in your domain's report, plus `ABLATION_<domain>.json` next to your results with one record per (arm, seed):
{domain, arm, seed, exact_train, exact_64x, exact_256x or null, p_longest, source_record}. Launch with modal deploy
+ spawn from a script that exits, results to a Modal volume, call ids committed. Cap $6 per domain. Commit, do not push.
