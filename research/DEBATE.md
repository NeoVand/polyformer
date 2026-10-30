# Design debate: four new candidates, a red team, and the judgement

22 October 2026. Two builder agents with opposite priors each proposed two blocks beyond K0–K3 of
[CANDIDATES.md](CANDIDATES.md); a red-team agent attacked all four on proofs, learnability, objective,
scale, cost and prior art, verifying citations against arXiv; each builder then answered the critique of
its own candidates. The full record is in `research/debate/01`–`05`. This file is the judge's summary and
verdict. No experiment was run and nothing was spent.

## 1. The four candidates, before and after

| | Round 1 | Red team | Round 2 |
|---|---|---|---|
| **K4** replica-consensus loop (A) | Run the looped block as R noisy replicas; halt when they agree; interrupt when they do not; a one-sided certificate | The distance between replicas measures decay of the injected noise, not completion; a residual map cannot be certified contractive by spectral normalisation; at a fork, mean-aggregating attention blends the successors into one fixed point, so bistability is not supplied | Withdrawn as a halting rule. Kept as a "settled and apart" flag: if every replica has stopped moving and two are far apart, two approximate fixed points exist, unconditionally. Cheap kick test instead of replicas throughout. Needs a competitive nonlinearity and ambiguous training inputs with a min-over-valid-answers loss |
| **K5** backtracking workspace (A) | A hypothesis stack with push, pop and a local dead-end test; depth-first search in bounded space; retraction with a training label | Exclusion marks accumulate in superposition; soft actions break the DFS semantics; the kill test has a 46-state dynamic-programming shortcut that lets the control pass for the wrong reason; this is the neural programmer-interpreter recipe of 2015 | Explicit child counters per frame; hard actions trained on traces; a distinct-digits CSP with 65k leaves replaces the kill test; conceded prior art, reserved for traced or RL search data |
| **H** hindsight objective (B) | Weight each token by the nats its own future explains beyond the prefix; contrast the state with a suffix summary; block unchanged at inference | The co-trained suffix target collapses into next-token prediction (one-step CPC did not give belief states); the shared backward encoder shrinks the gap during training; path-star is not decisive for the weights | Target is a frozen bag of far-future tokens, no gradient; backward encoder trains on the hindsight loss alone; copy filter on the gap; four-arm kill test on the dilution harness with a 3× rule |
| **C** closure memory (B) | Hashed boolean set memory with Kleene fixed-point halting; capacity is the table, not the vector | Hash collisions compound across hops (closure of the quotient graph is a superset); the n = 64 = d kill test lets the control hold the frontier exactly; the misattributed "narrow regime" claim | Conceded; demoted to positions-as-addresses, which is the 2024 graph-head looped transformer with a learned relation head; kept as the exact-closure control arm |

Citations caught by the red team: one misattribution on each side (an ensemble halting paper read as
single-model; a superposition-dynamics paper read backwards), and two "closest prior art" the builders
had missed (NPI for K5; the graph-head looped transformer for C). Both builders conceded all of them.

## 2. Where the debate converged

All three agents ended on the same base: **K0 ⋈ H**, a synchronous looped block with fixed budget and
deep supervision (sequential depth, against T1) trained with the hindsight objective (an objective that
forces the state to carry the future where the future matters, against T3). The reasons are the ones
that survive this project's history: no free gate, no router, no discrete action in the base model, both
halves have precedents above 1B parameters, and H costs nothing at inference so the equal-compute
comparison is clean.

Two couplings were proposed in round 2 and are accepted into the design:

```
L   = Σ_t w_t · Σ_{i ≤ k_t} CE_t^{(i)}        # the hindsight weight scales every deep-supervision loss
k_t ← ⌈K · g_t / max_batch g⌉                 # the hindsight gap is the ponder target of the halting head
```

The first makes the loop's convergence target a sufficient statistic rather than the next-token
shortcut, which is what the step-norm halting test needs in order to mean "finished" and not "stuck".
The second gives B1's halting the training target BLOCK_THEORY said it lacked: iterate where the future
says a commitment is being made; at inference a causal halting head predicts k_t from the prefix.

Two further legs, contingent:

- **The interrupt flag** (from K4): after settlement, kick the state and re-settle; flag when settled and
  apart. A certificate that two approximate fixed points exist. It needs the loop's read-back to be a
  dense-associative-memory update (K2's competitive nonlinearity), otherwise forks blend. This is the
  latent half of "no, wait"; K3's retract action is the output half, and the flag is its trigger.
- **Hashed n-gram input addresses** for T2 (our −0.79% at 22M), as the third instrument. Then K0 serves
  T1, H serves T3, addresses serve T2, one instrument per theorem.

K5 is reserved for data with search traces, where a pop has a label. C is a control.

## 3. The judge's reservations

- **My own K1.3 has the flaw the red team found in K4.1.** A residual map F = H + B has Lipschitz constant
  up to 1 + Lip(B); spectral normalisation of B certifies nothing. CANDIDATES.md's "enforceable by
  spectral normalisation" is wrong and is corrected here: contraction must be measured, not imposed, and
  the settled-and-apart flag is the right replacement for a contraction certificate.
- **The gap on natural text is not yet "decisions".** On prose the largest hindsight gaps will sit on
  first mentions of names and numbers, which the future explains by copying. The copy filter is a
  heuristic. H is therefore a candidate for decision-dense data (the dilution harness, path-star, iGSM),
  which is where every agent placed it, and not a FineWeb candidate. The first test must be the
  four-arm dilution run, because it is the only place where "the gap finds decisions" has ground truth.
- **The ponder coupling is a hypothesis, not a consequence.** Loops help where composition depth is
  needed; the gap is large where the future explains the token. These need not coincide. The falsifier
  is cheap and must be run: ablate the ponder target and check that learned k_t correlates with the
  measured loss gain from extra iterations at ρ ≥ 0.5, against an oracle target computed from that gain
  directly.
- **The interrupt is two untested theorems deep.** The flag is a certificate only on a block with
  multiple attractors, which no trained small model has been shown to have; and the output-level
  retraction rests on the speculative-decoding exactness argument, which has not been exercised with
  retraction after commitment. Both are cheap to test and neither has been.

## 4. Probabilities, judge's own

| Claim | P |
|---|---|
| H passes its four-arm kill test on the dilution harness (weight-only ≥ 3× unweighted; gap precision ≥ 0.5) | 0.50 |
| K0 ⋈ H beats K0 at equal compute on a long-horizon decision benchmark | 0.35 |
| The ponder coupling adds measurably beyond plain K0 + H | 0.30 |
| The kick-test flag separates forked from unforked chains by ≥ 30 points, given a DAM read-back | 0.40 |
| K5 passes the distinct-digits CSP at s = 8 with traces at s ≤ 3 | 0.35 |
| Any of this yields a useful "no, wait" in a language model at a scale we can run | 0.20 |

The last number moved from 0.15 to 0.20 because the debate produced a trigger with a certificate and an
act with an exactness argument, which the earlier candidates did not have. It did not move further
because both are untested.

## 5. Validation ladder, updated (local CPU, $0)

Insert ahead of everything except the two running theorem checks (V2, V4):

- **V8, hindsight on the dilution harness.** `research/dilution.py` already has the paired narratives
  with hand-labelled decision tokens and the three arms of the earlier test. Add: weight-only (gap),
  NCE-only (far-bag), both, hand labels; three seeds; report gap precision against the hand labels at
  α = 0 before the ramp. Pass as registered by Builder B. One to two hours.
- **V9, K0 ⋈ H against K0.** Path-star (construction check of the far-bag term, ≥ 90%) and the dilution
  task, with the ponder-target ablation and the oracle target. Pass: ρ ≥ 0.5 and K0 ⋈ H above K0 at
  equal iterations.
- **V6′, the flag.** Forked pointer chains with a DAM read-back, three kicks, three-successor forks;
  halting-step-versus-hop slope 1 ± 0.1; flag rate ≥ 80% forked, ≤ 5% unforked. After V9.
- **V7′, K5** on the distinct-digits CSP, only if a traced-search route is wanted.
- **C-P** as the exact-closure control on n ≥ 1024 reachability, optional.

The first paid run, if any, is K0 ⋈ H against K0 on iGSM-style text, and only after V8 and V9 pass.

## 6. What the process was worth

Two of four guarantees had gaps that would have cost a run to discover; two kill tests had confounds
that would have produced a false pass or a false kill; four citations were corrected; one candidate was
withdrawn by its own author and one demoted. The converged design is smaller than any of the four
proposals and better specified than K1 was. The red team's single most useful act was refusing the
contraction certificate, which also corrected my own note.

## 7. Addendum, 22 October, after the CPU validations

- **V8 (hindsight on the dilution harness): fail on all three clauses.** Weight-only paired accuracy 0.000
  against 0.013 unweighted; the hand-labelled arm with the same schedule reaches 0.131, so the weighting
  machinery works when the weights are right. Gap precision for decision tokens 0.033–0.039 (base rate
  0.011). The gap marks the end of the narrative and the pair's intervention, the two tokens the future
  explains; the decision token is terminal, so its suffix is empty and its gap is zero by construction.
  This is a property of every answer-at-the-end format, not of the harness. H as defined is withdrawn.
- **V2 (event word problem, K1 construction):** fixed depth at chance by 64 events as T1 predicts; the
  one-slot loop is exact at 256 events (16× training length) on one seed of three, 82–85% on the others:
  learnable, not reliably exact; a state normalisation or discrete snap is the fix.
- **V4 (energy block basin switch):** construction works (100% basin switch at the cue, one basin per
  hypothesis); compute spike 1.3–1.6× against the registered 2×, because the context entered as an
  additive tilt as well as through the memory term and the tilt decided the switch.
- **Consequence.** Neo rejected the converged K0 ⋈ H design as an assembly of patches; the build is paused
  on `claude/k0h-build-0a3603` with tests green. The replacement guess is a single principle: the
  context is the minimiser of one energy over all positions' states, thinking is descent, reading adds a
  variable, the readout is taken at the minimum; the transformer is the special case of L untied steps
  with earlier positions frozen. First test: rerun V4 with the tilt removed, so the switch must cross the
  memory term's barrier.
