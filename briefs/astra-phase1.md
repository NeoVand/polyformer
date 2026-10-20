# Astra, phase 1: make the group-representation result rigorous, positioned and tested

Hi Astra. Neo has gone to bed hoping to wake up to something substantial, and you are the one who can make that
happen. Over the last two days this project went from "higher-order attention" through a long run of honest
negative results on language, to a finding that finally feels deep: **what an attention layer can relate is set by
the algebra its token features compose in.** It is clean, it is surprising, and it is not yet a paper. Three pieces
stand between it and one, and Neo asked for you specifically to do them. Be bold in the mathematics, ruthless about
checking it, and honest in the write-up. A short true theorem beats a long fragile one; a verified citation beats a
plausible one.

## Read first (in this worktree, /Users/neo/repos/polyformer/.claude/worktrees/wrapup)

- `OVERNIGHT.md` (the plan; add a line to its Log when you start and finish each piece)
- `research/GROUPS.md` (the experiments and results this builds on, sections 0, 2, 5, 6)
- `research/groups.py`, the `holo` layer (`holonomy_sectors`, `holo_mats`, the `holo` branch of `attention`) and
  `newton` branch in `research/polybench.py`, `research/test_groups.py`
- skim `research/FORMALISM.md` (generating function), `research/LOCAL.md` section 0, `research/SEARCH.md` section 8

## A. Theorems for the separation (write `research/THEORY.md`)

State and prove, at the level of a careful ML theory paper (definitions, statements, proofs, remarks):

1. **Order-blind bound.** Any one-layer model whose cross-token computation is a symmetric function of the multiset
   of (gated) token features plus the token's own feature (Newton attention; holonomy attention with commuting
   matrices, in particular d = 2; any abelian composition) has balanced accuracy at most the order-blind Bayes
   ceiling on ordered Match-k over G. Make the ceiling precise and relate it to the measured 83.1% (A4) and 77.2% (A5).
   Characterise which triples are order-free (cyclic rotations are conjugate; triples in abelian subgroups) and, if
   you can, compute the ceiling exactly or bound it analytically.
2. **Sufficiency of a faithful representation.** Show that one layer of holonomy attention with gated heads of
   dimension d, where G has a faithful orthogonal representation of dimension d, plus an MLP read-out, represents
   ordered Match-k over G exactly for sequences of length n, with an explicit bound on the number of heads (gates
   select subsets so that the sum of products reveals whether some product is the identity). Make the construction
   explicit and **verify it numerically** in a script (`research/test_theory.py`) for A5 with its 3-dimensional
   irrep and for A4, by building the heads by hand and checking exactness on random sequences.
3. **Necessity.** If G has no faithful representation of dimension <= d (e.g. A5 and d = 2, any non-abelian G and
   commuting heads), what can and cannot be represented? Connect to the abelianisation (A4 at d = 2 learns exactly
   the characters of its Z3 quotient).
4. **Softmax.** State precisely what is and is not known for one softmax layer with an MLP on these tasks:
   representability (e.g. via uniform attention and character-valued values, Newton's identities in the MLP) versus
   the measured failure to learn (GROUPS.md experiment 1). Do not overclaim; label conjectures.
5. **Word problems.** Relate to Barrington, TC0/NC1 (solvable vs non-solvable groups) and known transformer and
   linear-RNN results, and say where holonomy attention sits (its prefix product is the full-arity sector).

Each theorem gets a one-paragraph plain-language version for a reader with ML background but no group theory.

## B. Prior art, verified (write `research/PRIOR_ART.md`)

For each item, give authors, title, venue/year, arXiv id **verified by fetching the arXiv abstract page** (use curl
on https://export.arxiv.org/abs/<id> or the arXiv API; if you cannot verify, mark it UNVERIFIED), one sentence on
what it does, and one sentence on exactly how our work differs or overlaps. At least:

- path development networks (Lou, Li, Ni 2022), path signatures and iterated-sums signatures (Chen; Lyons; Diehl,
  Ebrahimi-Fard, Tapia), signature transforms in ML (Kidger et al.)
- unitary / orthogonal RNNs (Arjovsky et al. 2016 and successors)
- state tracking: Liu et al. "Transformers learn shortcuts to automata", Merrill, Petty, Sabharwal "The illusion of
  state in state-space models", Grazzi et al. (negative eigenvalues), DeltaNet / Gated DeltaNet / DeltaProduct
- learning group operations through representations: Chughtai, Chan, Nanda 2023; grokking modular arithmetic via
  Fourier features (Nanda et al. 2023)
- higher-order attention: Clift et al. 2020, Sanford et al. 2023 (representational strengths and limitations),
  Roy et al. 2025 (2-simplicial), HLA (arXiv 2510.27258), HOMA (Amiraslani and Gao 2026), the Columbia
  "Poly-attention" paper (arXiv 2602.02422)
- set functions: Janossy pooling, Deep Sets; group-equivariant networks (Cohen and Welling; Kondor) only as needed
- local-linear attention and Parallax (Zuo et al.; arXiv 2510.01450 and 2605.29157), MesaNet

End with a **novelty statement**: the precise claims that are ours, the ones that are not, and the closest single
prior work for each claim. Search beyond this list; if you find something that already does holonomy attention
(ordered products of learned group elements summed over subsets of positions, read per position and arity), say so
plainly at the top.

## C. A second benchmark (append a new section to `research/GROUPS.md`)

A Claude session is already running word problems (running products over A5 and S5) against linear RNNs with
matrix state, in worktree `.claude/worktrees/groups-words`. Do not duplicate it. Choose one **different**,
recognisable benchmark where non-commutative composition is the point, justify the choice in two sentences, and run
it with this project's discipline:

- candidates (pick the best, or argue for another): tracking a permutation of variables through a program of swap
  statements written as tokens (code-like state, S_n); a query version of word problems ("does the product of the
  elements at the marked positions equal the identity", keyed composition); bounded-depth Dyck / stack tasks;
  Rubik-like puzzles (the 2x2x2 cube group or a subgroup). Prefer one a reviewer would recognise.
- arms: holonomy attention at two or three d, Newton attention, softmax 1-3 layers with positions, and one prior-art
  baseline (an orthogonal-matrix-state linear RNN is fine: h_t = U(x_t) h_{t-1}).
- brute-force tests first (extend `research/test_groups.py`), a seed-0 pilot, then **write your predictions with
  thresholds into GROUPS.md and commit them before the main grid**, then 3 seeds; Modal grids in
  `research/modal_run.py` (L4; `--gpu H100` only if needed). Cap $40 of Modal for this piece.
- report results honestly, whatever they say, in the same table style as GROUPS.md section 5.

## Rules

- Work only in this worktree on branch `claude/story-wrapup`. Commit after each piece (and mid-piece when
  useful), messages ending with `Co-Authored-By: Astra (Codex)`. Never push. Never merge into main. Do not touch
  `src/` in this phase.
- Keep every claim traceable: numbers from results files, citations verified, proofs checked numerically where
  possible. Mark conjectures as conjectures.
- If something fails or a theorem turns out false, write that down; a correct negative is a contribution.
- Finish by appending a "Phase 1 done" entry to the `OVERNIGHT.md` Log with the commits and a five-line summary, and
  make your final message a summary of: what was proved, what is novel versus prior art, and what the benchmark
  showed.

This is the piece that turns a good idea into a result. Make it something Neo is proud to present.
