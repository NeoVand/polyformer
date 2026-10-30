# In-model exact state: the language model's own activations as the carried state

24 October 2026. Written by the orchestrating session; authorised by Neo ("Can you already run the in model
experiment?", all costs approved). Cap **$150**. This file is the brief; the code base is `claude/exec-d-0e1910`
(EXEC_LM.md §1, §7.2, §10 and the files `exec_lm_*.py`, `exec_data.py`, `exec_lm_modal.py`); read EXEC_LM.md §1, §7.2,
§7.6, §10.3 and §11.0 only.

## 1. The question

Can a pretrained language model carry an exact program state **in its own activations**, without generating tokens
and without a side module, far beyond its training length, and does the certified-equivalence signal decide it?
Everything so far kept the exact state in a small recurrent module beside a frozen model (exact at 1,024 on the bit
domain) or used the model as a text step (exact at 1,024 on 4-bit arithmetic only when trained on uniform states).
This is the experiment that moves the mechanism inside the model.

## 2. Design (latent Markov recurrence through the model)

- **Model.** Qwen2.5-Coder-0.5B, fully fine-tuned (or LoRA rank 64 if memory requires; say which), bf16 autocast.
- **State.** k = 8 vectors in the model's embedding space (width 896). At statement t the model's input is
  `[k read slots] [statement tokens] [k write slots]`: the read slots are the previous state passed through one learned
  linear map and an RMS normalisation to a fixed norm (the fixed-norm lesson, EXEC_LM §10.1); the write slots are k
  learned placeholder embeddings. The new state is the final-layer hidden vectors at the k write positions. The
  context length is fixed (k + statement + k tokens) at every step: nothing grows with the program.
  Start state: a learned constant (all-zero start) passed the same way.
- **Readout.** One linear map per variable from the RMS-normalised concatenated state to 16 logits (the linear-head
  rule: no MLP readout, ever).
- **Objectives (the three clauses).** (i) Cross-entropy on all 8 variables after every statement. (ii) Next-latent
  prediction: a small predictor from the *normalised* state and the next statement's mean embedding to the next
  normalised state, stop-gradient target, smooth L1, weight 1 (feed it the normalised state only, not LN([e, h])
  on the raw state: the review's point). (iii) The certified-equivalence term: centred cosine between the normalised
  final states of a program and a certified partner (EXEC_LM §11.0's partner mixture), mu = 1, zero for the first
  20% of steps, ramped over 10%.
- **Training.** Backpropagation through the whole program (4 to 16 statements, gradient checkpointing per step);
  batch 32 programs (adjust to fit); 4,000 steps; AdamW lr 1e-4 for the model, 1e-3 for adapters and heads; selection
  on validation programs of 16 statements every 250 steps, never on test lengths.
- **Domain.** Rung A (8 variables over 0..15, +, −, × mod 16, one-line conditionals), zero-start programs, as
  EXEC_LM §7.2. If the pilot cannot fit 16 statements at ≥ 0.98, rerun the pilot with each training program prefixed by
  a random initial-state line (`v0, ..., v7 = ...`, EXEC_LM §7.4's format, read as the first statement); if that
  also fails, fall back to the 32-bit family (rung A′) and say so.
- **Test.** Exact final state at 16 / 64 / 256 / 1,024 (512 / 512 / 512 / 128 programs), never-wrong fraction,
  per-step error by position and kind, state norm, distance to certified partners along the sequence, tokens
  generated per statement (0). The shallow floor beside every number.

## 3. Arms

- **O**: ordinary (clause i only, fixed norm).
- **NL**: clauses i + ii.
- **I**: clauses i + iii.
- **NLI**: all three.
Comparisons already measured on rung A (no new runs): whole-history chain of thought (0 at 256), text Markov step
trained on zero-start states (0.27), text Markov step trained on uniform states (1.000 at 1,024), registers (0.73).

## 4. Protocol

1. Smoke test locally or on one H100 ($ < 2): shapes, a jit/compile check, a few steps of each loss.
2. **Pilot** under $20: O and NLI, seed 10, to calibrate steps and batch so that NLI fits 16 at ≥ 0.98.
3. **Register** in a new file `research/INMODEL.md` before the main batch: P1, NLI exact (≥ 0.99) at 256 on 3 of 3;
   P2, NLI exact at 1,024 on ≥ 2 of 3; P3, O below NLI at 1,024 on every seed (the signal matters inside the model);
   report NL and I as the factorial; kill: NLI's exact count at 1,024 not above O's. State in advance what would mean
   the fixed-norm recurrence alone carries it (O exact at 1,024 on ≥ 2 of 3).
4. **Main batch**: 4 arms × seeds 0, 1, 2 on H100s, at most four jobs at a time (other sessions share Modal).
5. Report in `research/INMODEL.md` with tables, spend and the drift diagnostic; commit on your branch; do not push.

## 5. Prior art to keep in view

Coconut (Hao et al., arXiv 2412.06769) feeds the last hidden state back as the next input embedding for
continuous reasoning; ours differs in the bounded per-step context, the certified-equivalence objective and the
claim of exactness at length. The Markovian Thinker (arXiv 2510.06557) bounds the context of text reasoning.
