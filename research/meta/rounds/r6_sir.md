# R6: SIR / compartmental epidemiology

## 1. Objects and techniques
- Object: compartment vector (S, I, R) with conserved sum N and flow rates β, γ (Kermack & McKendrick 1927).
- Object: R0, the spectral radius of the next-generation matrix FV⁻¹ (Diekmann, Heesterbeek & Metz 1990; van den Driessche & Watmough 2002).
- Object: incidence curve, a partial aggregated view.
- Theorem: threshold and final size. An outbreak happens iff R0·S0/N > 1, and z = 1 − e^(−R0 z) (KM 1927).
- Technique: structural identifiability (Bellman & Åström 1970; DAISY, Saccomani et al. 2003); profile likelihood (Raue et al. 2009).
- Practice: chain-binomial fitting (Reed–Frost 1928); iterated filtering (Ionides et al. 2006).

## 2. Map to ARC-3
- P1: compartments = colour or class counts; on-screen counters are compartments. Lumpability (Kemeny & Snell 1960) says when counting is exact.
- P2: an action's effect on the count vector = a stoichiometric column; contact flows (S next to I) = local rewrite rules.
- P3: identifiability as exploration: skip hypothesis pairs no sequence separates; target confounded pairs (rules that always fire together, like β vs N).
- P4: the absorbing compartment R is monotone (Lyapunov, Korobeinikov 2004), so a candidate goal is a count heading to an absorbing value.
- P5: optimal control on counts (Morton & Wickwire 1974); plan lumped, check on cells.
- P6: nested SIR → SEIR → SEIRS mirrors a level adding a mechanic; a nested-model test decides when to add one.
- P7: early growth fixes R0 from few points (Wallinga & Lipsitch 2007); fit only what an early window identifies.
- P8: the conservation law ΣX = N as a per-step check; a violation means a missed flow.

## 3. Map from ARC-3
- Epidemiology's hard part is partial observation without intervention. ARC-3 is fully observed, deterministic and intervenable, so identifiability is mostly easy.
- ARC-3 rules are spatial. Compartment models win by discarding geometry, exactly what ARC punishes (counters excepted).
- Lesson back: ARC is a lattice SIR, the regime where mean-field and pair approximations (Keeling 1999) fail.

## 4. Grades
- Stoichiometric ledger + conservation laws (P1, P2, P8): TOOL.
- Identifiability-driven exploration (P3, P7): TOOL (its discrete form is automaton distinguishability).
- Monotone absorbing count as goal (P4): FRAME.
- Nested expansion (P6): FRAME.
- Threshold, R0, control on counts (P4, P5): LOW.
- HIT: none.

## 5. Candidates
C1 Stoichiometric ledger. For each transition, log the change in a colour/class count vector, fit one integer column per (action, context), and take the left null space as conservation laws. The laws give exact step checks (P8), new-mechanic flags (P6) and a lumped planner for counter goals (P4, P5). Kill: if under 30% of level completions in the public games coincide with a linear count condition (a count hits 0 or a target), demote it to a checker.

C2 Identifiability-pruned probing. Keep a finite rule-hypothesis set, merge pairs no action sequence from the current state can separate, and act to split the most surviving pairs (P2, P3, P7). Kill: if actions-to-correct-model on the public games fall less than 20% against a count-based novelty baseline, kill it.

## 6. Adversary
- C1: most moves (sprite translation) conserve every count; the ledger reads zero while geometry carries the rule. Prior art: CRN stoichiometric subspace (Horn & Jackson 1972; Feinberg 1979); AI Poincaré (Liu & Tegmark 2021); colour counts in ARC-1 DSLs (Hodel 2022).
- C2: this is information-gain exploration over a bisimulation quotient; epidemiology adds only vocabulary. Prior art: Moore 1956; Angluin's L* 1987; Lindley 1956; Givan, Dean & Greig 2003; VIME (Houthooft et al. 2016).

Verdict: nothing ARC lacks. The ledger is a cheap checker, worth an afternoon at most.
