# Candidate ideas to red-team (28 Oct 2026)

Sources: B1_visionary.md, B2_cognitive.md, B3_theory.md, B4_frontier_skeptic.md (same folder), and the orchestrator's
own list. Our assets are described in FACT_SHEET.md. The full prior-art map is in ../prior_art/L1–L6.

- **I1. Exact imagination.** A learned world model (pixels or text in, a snapped discrete state, a renderer out) that
  never drifts.
  - Hide a key, come back an hour later, and it's there.
  - Plan thousands of moves in imagination and execute them blind.
  - Object permanence over 10,000 occluded steps.
  - A "world-model Theorem P": check each local rule once and the rollout is exact. (B1#1, B4#2, orchestrator)
- **I2. Certified identification of rules or machines from experiments or examples.**
  - An LLM proposes transition tables; certified execution tests them exactly against observations or queries
    (L*-style, Rivest–Schapire counterexamples, a W-method stopping rule).
  - It declares "identified; certain for any machine with ≤ n states" and predicts a million steps.
  - Variant: "three examples, one question, forever". (B3#1, B2#1, B1#2, orchestrator)
- **I3. Self-predicted failures.**
  - Before running, the model prints the exact set of inputs or steps it will get wrong (from its uncertified rows),
    and a bounty finds only listed failures.
  - It repairs itself, for example by renaming confusable names, until it is certified. (B4#1, B2#2)
- **I4. The ∀ badge.** Every answer carries a Lean theorem, checked by the kernel, that the network on this code path
  is correct for all inputs of all lengths. A "Nerode certificate" maps table states to spec meanings, discharged
  per row by `decide`. (B3#2)
- **I5. The ratchet.** Self-improvement where an update is accepted only if the whole certified skill library
  recertifies, so certified skills can only grow. (B3#3)
- **I6. Practice makes it faster.** Certified multi-step shortcuts: one tick replaces two after agreement is
  certified, following a power law of practice with exactness kept. (B2#3)
- **I7. The glass mind.** Under the pinned clock, hidden or steganographic channels in the run are provably absent
  and caught. Edits to activations have long-run effects that are predicted before they happen. (B1#3)
- **I8. Certify the model, not the program.** A weights-level certificate N\*: a designated lookup head plus row-local
  attention, so every table up to N rows over a screened vocabulary runs exactly at any length. (orchestrator, bet A)
- **I9. Row-level credit assignment for program-writing RL.** Certified execution traces each wrong answer to the
  exact wrong row, giving a dense exact process reward. (orchestrator, bet B)
- **I10. Exact state over long messy documents.** Local semantic judgments, a certified control skeleton, and
  per-row semantic checks of the compiled table; cost per row, not per step. (orchestrator, bet C)
- **I11. Silent execution.** The model writes a program, then runs it in latent space inside a looped block of its own
  layers, snapped each step (v1's closure), with no tokens, emitting only the result. (orchestrator)
