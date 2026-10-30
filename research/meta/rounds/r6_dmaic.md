# R6: DMAIC applied to ARC-AGI-3

## 1. Objects and techniques
- Transfer function Y = f(X), with the "vital few" X (Juran, 1951).
- Shewhart control chart (1924; 1931): ±3σ limits, common vs special cause.
- Cp = (USL−LSL)/6σ; Cpk = min(USL−μ, μ−LSL)/3σ.
- Fractional factorials 2^(k−p) (Box & Hunter, 1961): resolution, alias tables.
- Shainin Red X (Bhote, 1988): multi-vari, component swap, B vs C (3+3 runs, p = 1/20). A cause counts only if you can "make the defect come and go at will".
- Gage R&R (AIAG, 1990): repeatability, reproducibility, ndc ≥ 5. Nelson rules (1984).

Understood means: X's confirmed, defect on/off at will, confirmation run matches.

## 2. Map to the problem
- P1: Gage R&R on the parser: same state gives the same objects, across levels too. The parser must separate every state the dynamics separate. FRAME.
- P2: Y = next-state diff, X = object attributes × action. Multi-vari splits change into positional (per object), cyclical (per step) and temporal (per level). FRAME.
- P3: DOE with zero noise: replication is worthless, aliasing is everything. Choose the action that breaks the largest alias set. TOOL.
- P4: CTQ assumes a customer states Y; nothing infers it. LOW.
- P5: Improve = optimise X given f; confirmation run = execute and check. FRAME.
- P6: Control plan: each mechanic gets a detection signature and a reaction plan. FRAME.
- P7: Once determinism is verified, one on/off pair suffices. Budget per mechanic = alias-breaking moves + 2. TOOL. Cpk: nothing.
- P8: Chart the per-step residual. Nelson patterns give the type of the missing hidden variable. TOOL.

## 3. Map from the problem
- DMAIC has no phase that discovers Y. ARC-3 lives in that gap.
- Zero noise turns SPC into combinatorics: aliasing, not σ, sets the sample size.
- Factors are reachable only along paths. That is a split-plot regime (hard-to-change state, easy-to-change action), central here and a nuisance in DMAIC.

## 4. Grades
- HIT: none.
- TOOL: on/off gate, alias-breaking probes, residual typing.
- FRAME: MSA, multi-vari families, control plan.
- LOW: CTQ. Nothing: Cp/Cpk.

## 5. Candidates
C1, Red-X tollgate. A mechanic enters the model only after the agent predicts it on a fresh state and both produces and suppresses it by its own choice of action. One replicate each is enough once one repeated sequence confirms determinism. Probes split the alias table (cause pairs no transition separates); exploration stops at the gate. Addresses P2, P3, P7, P8.
Kill: across 20 environments, it saves under 20% of the actions before the first win, compared with exploring until 10 consecutive zero-residual steps.

C2, residual chart. Chart mispredicted cells per step. Each pattern maps to a typed hidden variable: trend → counter, period-k → timer, alternation → parity toggle, shift → new mechanic, spike → an object the model lacks. The type seeds the rule inducer. Addresses P8, P2, P6.
Kill: on 50 transcripts with labelled latents, typing accuracy is below 60% (chance is 20%).

## 6. Adversary
- C1: A Bayesian hypothesis posterior already gives the two-sided test, and the bottleneck is the hypothesis generator. Reaching "off" may cost more than the gate saves.
  Prior art: Bhote 1988; Lindley 1956; Mitchell 1982 (version spaces); Seung et al. 1992 (query by committee); Tsividis et al. 2021 (EMPA).
- C2: Counters are usually drawn on screen, and patterns need 6–9 points, which means wasted actions.
  Prior art: Rivest & Schapire 1993; Das et al. 2023 (AutumnSynth); Page 1954 (CUSUM).

Verdict: DMAIC brings discipline, not a mechanism.
