# Soft checkers: how wrong can the referee be? (plan, 24 Oct 2026)

Authorised by Neo: "go for the cheap test and if it works out, then go for a soft checker attempt for language;
theoretical work in the background for soft checkers." Motivation: language has no kernel or interpreter; a strong
embedding model (or a model judging two texts) could propose equivalent pairs, but it will sometimes be wrong. The
certified-equivalence term copies its checker's mistakes, so the question is the tolerance.

## Stage 1: noise tolerance on a certified domain (mechanism session, local CPU, $0 to $5)

Tier-1 rewrite chains, R+NL+I at the registered configuration (the CPU trainer of MECHANISM §2), certified partners
replaced with probability f by a wrong partner:
- **random wrong partner:** a chain ending at a uniformly random different tree (the gross error);
- **near-miss wrong partner:** a chain ending at a tree that differs from the true end tree by one rewrite
  (the realistic error of a similarity-based checker: close, but not the same state).
Grid: random at f = 0, 0.01, 0.05, 0.20; near-miss at f = 0.05, 0.20; plus one remedy, a robust term that drops the
largest q = 2f of the pair distances in each batch (trimmed mean), at f = 0.05 and 0.20 for both error kinds. Seeds
0, 1 (three where a cell sits on a threshold). Report exact at 8 / 256 / 1,024 / 4,096, the equivalent-pair and
unrelated distances, and the collapse diagnostic. Register the predictions (the tolerated f, which error kind is worse,
whether trimming restores exactness) before the runs, in MECHANISM.md §8.

**Decision rule for stage 2.** Stage 2 goes ahead if R+NL+I (with or without trimming) stays exact at 1,024 on 2 of 2
seeds at f = 0.05 for near-miss errors. If it breaks at f = 0.01, soft checkers are not viable without exact
verification, and language goes through simulators (stories whose state a program certifies) instead.

## Stage 2: a soft checker on language (designed after stage 1)

Language on top, a hidden exact world underneath: short stories about objects moving between containers (the
entity-tracking setting where large models lose track over long texts), with varied wording. Training uses only a
soft checker on the text (an embedding model proposes pairs of story prefixes; a verifier, such as an entailment
model in both directions or a judging language model, accepts or rejects), never the simulator. The simulator is used
only to measure the checker's real error rate and to score exactness at length. The test: does exactness at length
track the checker's measured error rate as stage 1 and the theory predict?

## Stage 3: theory (proofs session, $0)

`PROOFS4.md`: tolerance bounds for noisy and graded checkers; see the brief sent to that session.

## Stage 2 design (24 Oct, 05:40; stage 1 gave GO: near-miss f = 0.05 exact at 1,024 on 2 of 2, PROOFS4 §7)

**Domain: object stories.** A hidden world of 6 objects and 5 containers; events move one object, swap two, empty a
container into another, or say nothing new (a distractor sentence). Each event is rendered in varied natural English
(several hundred templates: synonyms, active and passive voice, pronouns resolved within the sentence, clause order),
so the same event has many surface forms. A simulator holds the true state (the container of every object).
Training stories have 4 to 16 events; tests at 16 / 64 / 256 / 1,024.

**Tracker.** The side slot that is exact on programs: frozen Qwen2.5-Coder-0.5B is replaced by a general model of the
same size if one is already cached (Qwen2.5-0.5B), middle-layer features per sentence, slot d = 128 with fixed norm,
linear readout of each object's container, next-state prediction; the certified-equivalence term with partners from
one of three checkers:
- **certified:** the simulator's equivalence (upper bound);
- **soft:** candidate pairs of training-length story prefixes, accepted when a soft judgment says they describe the
  same world: a small language model writes a one-line state summary of each prefix ("the key is in the drawer, …"),
  and an embedding model's cosine between the two summaries passes a threshold; the simulator is used only to measure
  this checker's false-positive rate, split into near (one object misplaced) and far errors;
- **none:** ordinary training.
Partners come only from training-length prefixes, where summaries are reliable; that is the theory's point: the checker
never has to be right at length.

**Registered question.** Does the soft checker make the story tracker exact at length, and does its effect follow its
measured far-error rate as PROOFS4 predicts?

**Now (before 06:10):** build the generator, simulator, renderer, the soft checker harness and its error measurement
on a sample, with tests; no training, no spend. After the flight: pilot, registration, main batch.
