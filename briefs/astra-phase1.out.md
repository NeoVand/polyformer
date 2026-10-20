# Phase 1 complete

All work is committed on `claude/story-wrapup`; no push, merge, or `src/` change.

**What was proved.** [THEORY.md](../research/THEORY.md) gives the sharp order-blind
balanced-accuracy bound and an exact conditional-ordering formula for Match-3.
An integer dynamic program yields **A4 83.0546984493%** and **A5 77.2287515874%**,
confirming the historical rounded estimates. Every A4 observation posterior agrees
with exhaustive enumeration of 2,985,984 sequences; 86,400 A5 reorderings independently
check the formula.

The constructive position-free Match-3 theorem uses faithful orthogonal
representations and explicit finite token gates: 182 heads for A4 and 3,782 for A5
are sufficient, deliberately loose bounds. Hand-built three-dimensional irreps
produce zero label errors on 64 sequences per group, including repeated-token
cases, before and after the implemented normalization. The arbitrary-Match-k
construction uses positional gates and binom(n,k) heads; the corresponding
position-free theorem for k≥4 remains open.

The necessity claim was strengthened and corrected: with a fixed collection of
homomorphic matrix channels and sufficiently many scalar-gated copies, exact
Match-3 is possible precisely when those channels jointly distinguish every
noncommuting pair. Faithfulness is sufficient but not necessary; A5×Z3 projected
onto A5 is an explicit counterexample to a universal minimum-faithful-dimension
claim. Softmax with an MLP has fixed-length constructions both for abelian
Match-k from uniform character values and for arbitrary sequence labels with
positions. The original Match-4 failure is a measured learning failure.

**What is novel.** [PRIOR_ART.md](../research/PRIOR_ART.md) and its reproducible
manifest verify **36 arXiv abstract pages**. Seq2Tens already constructs ordered
subsequence sums; Path Development Networks already learns Lie-group products.
The defensible contribution is the particular gated matrix realization with
marked-position, arity-specific readouts, its exact task-specific theory, and its
empirical representation learning. The general composition-algebra principle and
ordered subset generating map are not inventions of this project. Two inaccessible
thesis comparisons remain explicitly unverified; no exhaustive priority claim is made.

**What the second benchmark showed.** [GROUPS.md §7](../research/GROUPS.md)
reports interleaved keyed swap programs, different from the running A5/S5 word
problems. Tests preceded the eight-arm seed-0 pilot; numerical predictions were
committed before the 24-run main grid.

| Arm | Three-seed mean balanced accuracy |
|---|---|
| Holonomy d=2 | 62.02% |
| Newton | 62.05% |
| Holonomy d=3 / d=4 | 100% / 100% |
| Orthogonal matrix-state RNN | 100% |
| Positional softmax 1L / 2L / 3L | 98.95% / 100% / 100% |
| Exact order-blind ceiling | 62.037037…% |

All four preregistered criteria hold. This transfers the symmetry barrier to
short program execution; it does **not** show superiority over softmax or recurrence,
algorithmic length generalization, or a language-model gain. Evaluation draws are
independent but not deduplicated against training. Source and result fingerprints,
app chronology, full seed rows, and cost assumptions are retained.

The 32 L4 calls used 1,556.2 subprocess-wall seconds: **$0.35 GPU-only estimate**;
a generous full-resource accounting allowance is $3.09, not an invoice. Both Modal
apps are stopped; no further GPU jobs were launched.

Commits:

- `5d5ddd2` — benchmark implementation, tests, pilot, and preregistration.
- `bf3d0ef` — verified prior art and novelty boundaries.
- `e92e4a5` — three-seed benchmark results and provenance.
- `f289075` — theorems, constructive tests, exact ceilings, and integrated qualifications.

Reproduction commands are in THEORY.md, PRIOR_ART.md, and GROUPS.md. Independent
mathematical and benchmark reviews found no remaining blocking issue. The phase-2
update should replace the old absolute phrases “softmax composes nothing” and
“minimum faithful dimension is the capacity threshold” with these qualified results.
