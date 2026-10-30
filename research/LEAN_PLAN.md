# Lean program: certified invariance makes state trackers exact

23 October 2026. Decision: the Nerode objective moves to formal mathematics. The feasibility pass
(`LEAN_FEASIBILITY.md`, branch `claude/fervent-gagarin-ef7e03`) and the theory (`EXACTNESS.md` §1–7) set the
design; this file is the plan, the claim ladder, and the rules that make each stage likely to succeed.

## 0. The claim, in one sentence

A state tracker trained with an invariance loss over kernel-certified equivalent histories stays exact far
past its training length, where the same tracker without the loss drifts and a transformer collapses; the
kernel is the Nerode oracle, certifying both halves of the objective (equivalent histories agree,
inequivalent ones differ), which no other domain supplies.

## 1. Why this can succeed where language did not

The term selects exactness only where the primary loss is dense in the state (EXACTNESS §7, Prop. B). A
rewrite chain or a tactic script changes the state at every step, so distinction is supplied by the trace
itself; equivalences are exact and certified; and the S5 result already shows the mechanism at 64× the
training length. Nothing in the plan asks the model to learn something the loss does not pay for.

## 2. Stage one: certified rewrite chains (the group word problem with Lean as referee)

**Domain.** Expressions over natural numbers with a fixed multiset of leaves (6–8 atoms) and the operations
`+` and `*`; rewrite steps are single applications of core Lean lemmas at explicit instances
(`Nat.add_comm a b`, `Nat.add_assoc a b c`, `Nat.mul_comm`, `Nat.mul_assoc`, `Nat.left_distrib` and
`Nat.right_distrib` in a second tier). Lean 4 **core only**, no mathlib: the toolchain is a 300 MB elan
install and every certificate is `example : e_k = e_{k+1} := by rw [lemma args]`, batch-checked. The
commutativity and associativity tier keeps expression size constant, so the state space is finite (all
trees over the multiset) and exact match at 256 steps is well-posed; the distributivity tier changes size
and is the harder second cell.

**Generation.** Python owns the rewrite engine (explicit positions, deterministic), Lean owns the
certificate: every step is emitted as a Lean example and compiled; a step that fails to certify is
discarded. Equivalent partners (compression pairs): a different chain that ends at the *same* tree
(detours such as `comm; comm`, permutations of rewrites at disjoint positions, random re-derivations),
certified by syntactic equality of the final canonical expression, plus alpha-renaming of atoms applied
to both script and states. Inequivalent pairs: different final trees, certified by syntactic inequality.
Chains of 4–8 steps for training; test at 8, 64, 256, with fresh start expressions.

**State and metric.** The state after each step is the expression in a canonical linearisation
(Lean's own pretty-printing with fixed parenthesisation, or an S-expression); the model decodes it with a
small autoregressive head conditioned on the slot; the metric is exact match per step and at the last
step, plus first divergent step, teacher-forced and free-running.

**Models.** (T) transformer with trace supervision at every step, 4 layers, d = 128, equal per-token
FLOPs; (R) the per-step recurrence from INVARIANCE (one slot, cross-attention from the slot to the step's
tokens, MLP transition, readout through LayerNorm); (R+I) R plus the invariance term in the readout's
view with random equivalent partners, μ = 1, delayed for the first 20% of steps; (R+ctrl) the term on
unrelated pairs. Three seeds each.

**Registration rule.** Pilots first (two seeds, base and R+I, 2k scripts) to calibrate the expression
size so that the base is near-exact at training length and drifts by 256; thresholds are then written
from the pilot and committed before the main batch. Predictions: R+I exact (≥ 99%) at 256 on 3/3 seeds;
R drifts on at least one seed; T below 50% at 256; the growth of the pair distance predicts drift
(Spearman ≥ 0.7); the control does not raise the exact count. Kill: R+I's exact count does not exceed R's.

**Budget.** Toolchain and certification on CPU under $1; training on CPU containers or one H100, under
$10 in all.

## 3. Stage two: natural mathlib proofs

LeanDojo Benchmark 4 traces (states before and after every tactic), the Data/ slice with states under 256
tokens, canonical renaming of hypotheses, the tree recovered by re-tracing with positions (~$2). Train on
proofs of ≤ 4 tactics, test at 8–15 and ≥ 16 under the novel-premises split. Equivalences: alpha-renaming
(free), reordering of independent tactics (certified by re-running the swapped pair in the REPL), different
scripts reaching syntactically equal canonical states (free). Claim: exact multi-step state tracking that
extrapolates 2–4× in proof length against a transformer with the same supervision; metric exact match per
step and first divergent step. Budget $20–40.

## 4. Stage three: the prover in the loop (the headline, if stages one and two pass)

The tracker as kernel-free imagination inside a best-first prover (ReProver's search): roll out k steps
of imagined states to filter tactic candidates before the kernel sees them. Metric: theorems proved at
equal kernel calls, and kernel calls per proof, on the novel-premises test. The JEPA-for-Lean result
(better one-step ranking, fewer theorems solved) is the warning: one-step ranking does not transfer; the
claim is that exact multi-step imagination does. Budget $100–200.

## 5. Rules that protect the result

- Lean certifies every training pair; nothing enters the invariance term uncertified.
- The distance lives in the readout's normalisation; the term is delayed until a representation exists;
  partners are random equivalent chains of every length (INVARIANCE §5).
- Pilots calibrate, registration precedes spend, three seeds, the drift-versus-growth diagnostic reported.
- A transformer with identical supervision at equal FLOPs is in every table.
- Stage one must pass before stage two is built; stage two before three.

## 6. Publication ladder

Stage one: a workshop paper (MathAI / AITP) and the core of a main-track submission once stage two lands.
Stage two: AI-for-math main track. Stage three: a result provers would adopt. The theory section exists
(EXACTNESS §1–7); the prior-art position is clear (no kernel-free proof-state prediction task with an
exact-match, length-extrapolating metric exists; certified invariances have never been a loss term).
