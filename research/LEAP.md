# The big picture, and the leap it asks for (23 October, morning)

## What the whole arc says, in five lines
1. Every block we built to add computation to attention (cubic, Newton, subset, local regression,
   holonomy, hybrids, revisable memory, energy descent, workspaces) was neutral on text and shrank with
   size. Attention plus MLP is already enough computation for prose at every scale we can run.
2. What moved anything was exactness: a hashed exact address in the input (−0.79% at 22M), a
   kernel-certified pair in the loss (exact state at 128× length), an exact oracle in search (one kernel
   call instead of 442). Soft approximations of these never paid; the exact versions always did.
3. The wall we hit from every direction is binding. Match-4 needed a curriculum to bind keys to cards;
   entity tracking sat at chance; the paraphrase test found the first-owner shortcut; fresh atoms read
   as noise; natural proofs cannot write the content a lemma introduces. Different names, one failure:
   the model cannot say "this symbol here is the same object as that one there, whatever it is called."
4. Our theory is about selection and it is right, but it lives downstream of binding: invariance can
   only make exact a state the model can represent, and a state over unbindable symbols is not one.
5. Neo's own thread through all of it is invariants: SkipNorm preserves a norm by construction, holonomy
   preserved a frame, orbits are what the symmetry preserves, Nerode is what the future preserves. The
   instances that worked were the ones where the invariant was certified by an oracle and imposed where
   the state is read; the ones that failed imposed it by architecture alone (SkipNorm's own finding:
   exact norm preservation does not imply identification).

## The leap: make identity exact, not learned
The simplest statement of the missing primitive is **alpha-equivalence by construction**: symbols should
enter the model as roles, not names. In proof assistants this is de Bruijn indexing; in our chains it is
"the first atom to appear, the second, …"; in a narrative it is "the first owner mentioned, the second".
Under this encoding a renamed chain is the *same input*, so invariance to renaming costs nothing, fresh
atoms are handled with zero machinery, and the term's job shrinks to what it is good at. The ESBN result
(Webb et al., ICLR 2021: an external key–value memory that separates roles from fillers generalises
near-perfectly to novel entities) is the architectural cousin; de Bruijn is the zero-parameter version.

Two consequences, each a one-afternoon test that should "just work" or fail cleanly:

**L1. Chains with role-indexed atoms.** Re-encode every chain by order of first appearance of its atoms;
the readout emits role indices, decoded back to names outside the model. Prediction: the existing R+I
tracker is exact on fresh atom names at 256 (yesterday: 0.000) with no new parameters; the fifth-atom
test becomes a question about a fifth role, which is honest extrapolation and may still fail.

**L2. Natural proofs as copying under substitution.** A tactic that introduces content (rw with a lemma,
have with a type) copies the lemma's statement with a substitution of roles for its variables. Give the
change readout a copy mechanism over the premise statement's tokens (the premise statements are already
in the data) with variables role-indexed on both sides, so the "content" the model must produce is a
pointer into the premise plus a substitution, never free generation. Prediction: the rewritten-target and
added-hypothesis components, exact on 0–6% yesterday, rise to the closure components' range on steps whose
premise is given; steps whose content is not in any premise remain the kernel's.

## Why this is the right kind of idea
It removes machinery rather than adding it; it explains four failures with one cause; it is the
practical form of the orbit insight (an address that does not depend on the name); and it is what the
field's successful provers already do by hand (LeanNavigator's templates replace variables with
placeholders; effect-grounded tactic embeddings supervise the delta, not the surface). If L1 fails, the
binding wall is not nominal and the leap is elsewhere; if L1 passes and L2 moves the content components,
the prover story is back on real proofs with the same small models.

## Sources for the leap
Webb, Sinha, Cohen, Emergent symbols through binding in external memory, ICLR 2021 (2012.14601).
LeanNavigator templates (2503.04772). Effect-grounded tactic representations (MathNLP 2025, paper 12).
Neural Rewriting System (2402.17407); RewriteNets (2601.07868); PANM pointers (TMLR 2024). SkipNorm
(Neo, TMLR submission): exact norm preservation by construction does not imply identification.
