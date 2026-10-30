# Submission plan: Nature, arXiv and a release repository (24 Oct 2026, 05:50)

Neo's direction: aim for Nature; no rush while experiments run; the writing waits for the soft-checker (language)
results; when written, it must read like a major lab paper: a precise, authoritative voice, memorable prose, excellence
visible in every table and figure, a catchy title and a name for the method. Never an AI-generated mishmash.

## Order
1. Finish the science: soft checker on language (stage 2), Nerode self-distillation test, Figure 1 and 3 renders.
2. Decide the story from the results (with language working: the general principle plus programs, proofs and text;
   without: the principle plus programs and proofs, Nature Machine Intelligence first).
3. Write from scratch in one voice, not by patching the review drafts: a short brief fixing the narrative, then a
   single author pass, then hostile reading (a fresh model and at least one human expert), then a line-by-line pass
   for voice and precision.
4. Release repository and data, then arXiv, then the journal (Nature's policy permits preprints; transfer to Nature
   Machine Intelligence is the fallback).

## Release repository (its own repo, built from scratch, not a copy of this research tree)
- `exactstate/` (or the method's name): the core objective in a few hundred lines, framework-agnostic (JAX and
  PyTorch), with the three clauses, the readout criterion and the fixed norm as documented options.
- `domains/`: rewrite chains with Lean certificates, groups, programs, object stories; each a generator, a checker and a
  certified-partner sampler behind one interface.
- `experiments/`: one config per table row; one command reproduces a table or figure from scratch, another from the
  released run records.
- `results/`: every run record (JSON) behind every number, and `scripts/` that regenerate every table and figure.
- Data and certificates on Zenodo with a DOI; Lean toolchain pinned; tests and CI; a licence; a README that a reviewer
  can follow in ten minutes.
- The paper's LaTeX source in the journal template, figures built only from `results/`.

## Name and title (candidates; decide when the story is fixed)
Method name candidates: **Nerode training** (the loss: the Nerode loss); **loop closure** (from robotics, exact
image); **certified invariance**. Title candidates: "Exact state at any length from certified equivalences";
"Neural networks that never lose their place"; "Learning which paths lead to the same place".
