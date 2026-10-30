# In-model exact state: what went wrong, and the missing piece (whiteboard, 24 Oct 2026, 05:20)

Pilot stopped on Neo's decision. Facts (INMODEL.md §3–4): within ~40 steps every state collapsed to one point and the
readout predicted the all-zero state (validation equals the all-zero predictor); ordinary training never left it in
1,750 steps; with the full recipe the run began to leave it once the term ramped in (mean exact 0.27 at 1,250); the
first-step gradient norm was 2.1·10⁵; at initialisation the write-slot states carry 5.7–7.6% input-dependent energy and
a linear readout recovers nothing beyond the all-zero predictor.

## What we did wrong

1. **We asked the model to invent its state code from nothing, through the hardest gradient path.** Every recipe that
   works gives the step a clean, already-correct state to read during training: the side slot reads frozen features and
   learns a 128-wide code from scratch with a cheap transition; the text Markov step reads the *true* previous state
   line, uniformly sampled, so each step is trained as a function on correct inputs. The latent design had neither: no
   teacher-forced state and no cheap path; the only signal came from backpropagating through up to 16 unrolled passes of
   a 24-layer model, and it exploded. The term never got to act, because no representation formed (PROOFS A4: the
   constant state is the term's trivial minimum, which is why the term is delayed until one exists).
2. **We read the state where the model is least able to give it.** Final-layer hidden states of a causal model live in
   the output (unembedding) geometry, are dominated by a few massive coordinates, and at learned placeholder positions
   depend little on the input; feeding them back as input embeddings is a distribution shift. EXEC_LM already found the
   final layer a poor code (middle layer 12 learns; final layer does not fit 16 statements).
3. **We skipped the curriculum.** Continuous-thought work (Coconut) needed a curriculum from explicit text steps to
   latent ones; we went straight to latent.

## The missing piece

The model is an excellent *step function* when its state is in its native input space and the step is trained on
correct states (text Markov step: exact at 1,024 on 3/3). The missing piece is an **interface that keeps the latent
state in the model's input space and a training path that teaches the step before the loop is closed**. Three designs,
ranked by how likely each is to work and how much it says:

- **A. Soft-token state.** The state is 8 probability vectors over the 16 value tokens; the next step reads their
  expected embeddings (no sampling, no text emitted). At an exact state these are one-hot, so the system is the text
  Markov step at its fixed points and a continuous system near them; the certified-equivalence term acts on the
  distributions. Train the step teacher-forced on uniformly drawn states first, then close the loop. Most likely to
  work; the question it answers is whether a token-free, sampling-free state inside the model's own input space stays
  exact, and whether the signal lets it do so without uniform-state training.
- **B. Teacher-forced latent code.** Learn an encoder E from true states to 8 slot vectors jointly with the linear
  readout (an autoencoder of the state); train the step teacher-forced, from E(s_t) and the statement to E(s_{t+1}) on
  uniform states; then fine-tune free-running with the three clauses, with truncated backpropagation (1, 2, 4, 8, 16
  steps) and gradient clipping. The latent analogue of the recipe that worked; read and write at layer 12, centred and
  scaled per coordinate (not RMS over massive coordinates).
- **C. Repair the current design only** (middle layer, per-coordinate normalisation, truncated backpropagation
  curriculum, head warm-up). Cheapest to try, least principled; only worth it if the diagnostics show one dominant
  cause.

## What is deeper here

The theory already says the signal selects exactness among transitions the model can represent; this adds that it
also needs a representation the optimiser can *reach*. Consistency terms act on a code; something else must make the
code exist. In the side slot the frozen features plus a cheap transition made it; in the text step, teacher forcing
on true states made it. A general statement worth writing down: exactness at length needs (i) a reachable code (an
interface plus a path that teaches the step on correct states), (ii) closure (the fixed norm or a bounded input space),
and (iii) the certified signal. Our failures each removed one of the three: arithmetic in the flat slot removed (i),
the free norm removed (ii), ordinary training removed (iii).

## Next (after the flight)

Diagnostics first (massive activations at the write slots; gradient growth through the unroll; requested from the
lean-h session before 06:10). Then design A as a pilot under $20, registered first; B if A answers yes and we want the
fully latent version.

## Second pass (05:35): a more beautiful version, and what the first pass missed

Neo: "there might be a more beautiful way… maybe you are being shortsighted." He is right. The first pass kept
the slot-and-readout picture and tried to move the slot inside the model. The cleaner move is to apply Nerode's
definition to the model's *behaviour*, with the model itself as the teacher.

**Nerode self-distillation.** Two histories are equivalent when no continuation can tell them apart. So for a long
history u and its certified short equivalent v (the interpreter, kernel or group law supplies v; for programs, the
canonical program that sets each variable to its value), and any continuation w, require

    p_θ(· | u w)  =  sg p_θ(· | v w),

the model's own predictions after the long history must equal its predictions after the short one. The teacher is
the same model on the short context, where it is already competent; the stop-gradient keeps the teacher fixed.

Why this is the right object:
- **It is the definition, used as the loss.** No slot, no readout head, no fixed norm, no new architecture: it acts on
  any language model's own outputs, so "in-model" is automatic.
- **It is induction on length, as training.** If the model is exact on histories up to length n, certified pairs
  (2n, ≤ n) teach it to be exact at 2n; repeat. Theorem 3's proof is an induction over length through closure; this
  loss is that inductive step, executed by gradient descent. Competence propagates from short to long without labels
  at long lengths: the checker supplies the bridge, the model supplies the answer.
- **It targets the actual failure we measured.** Chain of thought fails at length because a long transcript is out of
  distribution (EXEC_LM §11.2: training on the states it will meet fixed it). Self-distillation teaches the full-context
  model to behave, on a long transcript, exactly as it does on the short equivalent: it learns to ignore the history
  that the state makes irrelevant, without cutting the context.
- **It carries to language.** The soft checker of SOFT_CHECKER_PLAN proposes equivalent prefixes; the noise test says
  near-miss errors are tolerated; the loss needs no labels.

**Its honest limit.** A fixed-depth transformer cannot compute a long sequential state in one forward pass (PROOFS2 T6;
the direct-answer model never fit 16 statements). So self-distillation makes a model exact at length wherever it
writes or predicts step by step (chain of thought, the Markov step, next-token prediction on traces); token-free
exactness still needs a carried state. For that, the second idea:

**The model's own reading of the canonical program is the state code.** The first pass's hardest problem was a
reachable code. But the model already has one: its hidden states after reading the canonical short program
(`v0 = 3; v1 = 12; …`, fixed length) represent the state, and computing them is trivial for it. So a latent recurrence
can be trained with free, exact teacher targets: after a statement, land on the hidden states the model would have
after reading the canonical program of the next state. Nothing is invented from scratch, no unrolled exploding
gradient is needed to discover the code, and the certified-equivalence signal holds the code fixed across routes.

**Prior work to separate from.** Self-Improving Transformers (Lee et al., ICML 2025, arXiv 2502.01612) extend length by
training on the model's own answers to slightly longer problems and need majority voting or length filtering to stop
error accumulation; here the checker maps a long problem to a certified short one, so the teacher signal comes from
the model's in-distribution regime and needs no filtering. Context distillation (distilling behaviour from a richer
context into a poorer one) is the nearest mechanism; here the direction is from a short certified context into a long
one.

**First test (after the flight, under $20, registered first).** Rung A, the whole-history chain-of-thought model (0 at
256). Add self-distillation: long transcripts (64 to 256 statements, no labels used beyond 16) paired with the short
canonical transcript of the same state; loss = KL of the next state line's predictions. Controls: the same model trained
on long transcripts with true labels (the oracle upper bound), and plain chain of thought. Prediction: self-distillation
reaches the oracle's exactness at 256 and 1,024 with full context, where plain chain of thought is 0.

## Third pass (24 Oct 08:15, after EXEC_LM §12): why self-distillation stopped at half, and the consensus teacher

**§12 numbers.** At 256: ORACLE 0.941 / 1.000, SD 0.508 / 0.422, plain chain of thought 0.000 / 0.000.

**Diagnosis: self-distillation cannot beat its teacher's per-step error.** Per-statement error p = 1 - E^(1/L):
SD at 16 is 0.0010 / 0.0018 (this is the teacher: the model on short contexts); SD at 256 is 0.0026 / 0.0034, about
twice the teacher's. ORACLE at 256 is 0.0002. Exact at 256 (0.95) needs p <= 0.0002, five to ten times below what
the teacher achieves at short length. A teacher at p = 0.0015 caps the student near exp(-256 x 0.0015) = 0.68 at 256,
and inheriting it with some loss gives the observed 0.42-0.51. The bridge worked: length no longer kills the model
(0.000 to about 0.5). What is missing is error correction in the teacher.

**Idea: the consensus teacher (a restoring organ built from certified equivalence).** Certified equivalence gives
more than one short context per state: permutations of the canonical `v = c` lines, and different short programs the
interpreter certifies reach the same state (`x = 5` versus `x = 2; x = x + 3`). Query the teacher on K of them,
take the product of their distributions (or the majority), use the argmax as a hard label, and keep only positions
where all K agree. If the contexts' errors are close to independent, a majority of three drops p from 0.0015 to about
3p^2 = 7e-6. Filtering also removes wrong targets, which PROOFS4 says hurt most (far errors).
- Prior art: Self-Improving Transformers (Lee et al. 2025) vote across independently trained models and grow the
  length slowly. Here the vote is across certified-equivalent contexts inside one model, at full length at once.
- It is von Neumann's restoring organ, and the repair-model equilibrium says why it should work: exactness at length
  holds once repairs outpace fresh errors.

**Free check first.** Measure the teacher's per-statement accuracy on canonical contexts and the agreement rate across
K = 3 equivalent contexts on a trained checkpoint. Prediction: single-context error 0.001-0.002; three-way-agreed
error at least 10x lower. If agreement does not cut the error, the contexts' errors are correlated and the idea fails
cheaply.

**Then the run** (same as §12, two seeds, about $4 each): SD-consensus with K = 3, hard labels, agreement filter.
Prediction to register: within 0.05 of ORACLE at 256 on both seeds.
