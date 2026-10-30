# BEAST: where a far-more-intelligent result could come from (Fable, 30 Oct 2026)

Neo: "does the hyperbolic framing give us something to do practically that leads to a model that is far more intelligent
... or is it just putting fancy names on things? i'm happy to pay for compute if it unlocks a new beast."

## 1. The hyperbolic framing, honestly

A theory of **reliability**, not intelligence. Buys: (a) a principled training term (enforce stable/unstable splitting
instead of a margin hinge; the aimed tube was this by accident and took S5 from 15/20 to 20/20 seeds); (b) deployment
bounds from shadowing (why margin 3 survived a 2.5 quantisation shift); (c) a classification of architectures that can
host exact computation. Likely partly known (Casey 1996; Tiňo et al., RNNs as symbolic dynamical systems) — gate it.
Spend: thought and Lean, $0. Not a beast.

## 2. Where intelligence lives in this stack: induction, measured on ARC

Everything built so far is execution. Intelligence as Neo means it is **induction**: learn a procedure from a few examples,
apply it exactly to new cases. The benchmark the field accepts for that is ARC-AGI (1, 2, and the interactive 3), with a
prize and a history of small models beating large ones (HRM/TRM at tens of millions of parameters; the 2024 prize winners
with test-time training on small LMs).

Our machinery maps onto ARC more directly than onto anything else: grids are canvases; rules are local programs over
cells; scoring is exact match; perception of the grid is native to the VLM; verification against the demonstration pairs
is a finite exact check. **Nobody has a system where the model writes a grid program, executes it inside its own forward
passes, verifies it exactly against the examples, sees the result on its own canvas, and revises.** That is "visual
program synthesis with exact in-model verification": Neo's dream, measured where everyone looks.

Risks: crowded and hard. Python-in-the-loop synthesis (sample many programs with a frontier LM, keep those that fit) is
a strong baseline that already executes exactly, so exactness is not our edge. The edge must be (i) a visual working
memory during search (the model sees each hypothesis applied before deciding), (ii) small-model efficiency (browser, not
thousands of frontier samples), (iii) long exact state tracking for ARC-AGI-2's harder half and ARC-AGI-3's interactive
games. Conviction: high that the machinery fits; about one in three that it beats the leaderboard in a way that gets
attention. Still the best odds of anything on our table that could be called intelligence.

## 3. The sprint, with kills (about $1k–2k H100, two weeks)

- **Stage 1, no training (~$200):** Qwen3.5-4B writes canvas-ISA programs for ARC-AGI-1 public tasks; our executor runs
  them on the demonstration inputs; exact match filters; apply to test inputs. Compare against (a) published numbers and
  (b) the *same model* calling Python for execution. **Kill** if in-model execution is not better than Python-in-the-loop
  on the same model: then the executor adds nothing here and we say so.
- **Stage 2, test-time training (~$500):** per-task LoRA adaptation (the 2024 winners' trick) with the certified executor
  as the adapted component; measure gain over stage 1.
- **Stage 3, the visual loop (~$800):** the model sees its program applied on the canvas and revises before answering;
  trained with exact reward (RL with a reward that cannot be hacked). **Kill** if ARC-AGI-2 public-eval accuracy does not
  exceed published small-model results (TRM ~8%, URM ~16%). Bar for "in the game": the 2024 winners' ARC-AGI-1 level
  (~55%). The orchestrator must check the live leaderboard first; these numbers are months old.

## 4. Fallback that is a business, not a beast

A certified ledger as an agent's working memory: a 1,000-step workflow whose state never corrupts. Enterprises pay;
labs less so. The floor under the company, not the pitch.

## 5. Decision for Neo

Spend thought on the hyperbolic theory (paper, $0) and compute on ARC (sprint, $1–2k, kills above). Do not spend
compute on the theory; do not spend thought pretending the arithmetic demo is the beast.
