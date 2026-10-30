# THEORY_DEEP: is there a deeper, more elegant framework? (Neo, 24 Oct ~11:10; exploratory, optimistic, no spend)

You consolidated THEORY.md. Now go looking for the framework underneath it. Be optimistic and ambitious; be strict
about what you claim at the end.

## The puzzle the data pose (research/master/master_table.md, built from raw records)
| arm | code | Lean | S5 | add | count | stories |
|---|---|---|---|---|---|---|
| O | 0/3 | 0/3 | 2/3 | 0/3 | 0/3 | 0/3 |
| O+N | 0/3 | 3/3 | 1/3 | 3/3 | 1/3 | 0/3 |
| NS+N | 0/3 | 3/3 | 3/3 | 3/3 | 2/3 | 0/3 |
| EQ+N | 3/3 | 3/3 | 1/3 | 3/3 | 3/3 | 3/3 |
| FULL+N | 3/3 | 3/3 | 3/3 | 3/3 | (fresh seeds pending) | 3/3 |
| FULL (no closure) | 0/3 | 3/3 | 3/3 | 0/3 | 0/3 | 0/3 |
Plus: physics (closure onto the invariant set holds the orbit; the signal adds nothing; phase is never repaired);
the soft checker (stable at length, constant deficit, caused by which pairs are accepted, not by wrong pairs);
in-model self-distillation (inherits the teacher's per-step error; the teacher's errors are correlated across
equivalent contexts, likely because long-reached states are outside the short-program coverage).

## Questions
1. **Do we need all clauses?** Give a criterion, computable from the task and the architecture before training,
   that predicts which arms are exact in each domain. Candidates to test against the table: whether the per-step
   output reveals the state (observability per step; PROOFS2 T4), the size and structure of the state space, the
   contraction of the learned map in the readout's null space, whether the transition reads the discarded scale
   (Cor 3.1), the spectrum of the task's transition monoid, supervision density.
2. **Why does O+N suffice on Lean and addition but not on code and stories?** Why does closure not matter on Lean
   and S5? Why does the signal at mu = 1 hurt S5 while helping elsewhere?
3. **One object.** Is there a single quantity (a curvature, a holonomy, a Lyapunov spectrum on the quotient, a
   spectral gap of the pair graph, an information-theoretic margin) whose sign or size decides exactness, with the
   three ingredients as three ways to control it?
4. **Certified exactness at every length.** Theorem 4 says block contraction onto class centres bounds the error
   forever. Can it be turned into a finite computational certificate for a trained network (for example, interval
   bounds showing every class ball maps into its successor's ball under every event), proving exactness at all
   lengths rather than testing to 4,096? What would it take on the Lean tier-1 tracker (960 classes)?
5. **Coverage.** Formalise "the teacher is wrong on states outside short-program coverage" and what it implies for
   self-distillation and for language.

## Method
Use Astra and Argon (research/../memory: Brainstorm CLIs) for ideas, verify every step yourself, and test any
criterion against the table and the raw records before believing it. Write research/THEORY_DEEP.md: what is proved,
what is conjectured with evidence, what failed. Commit on your branch, no push.
