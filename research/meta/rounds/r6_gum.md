# r6: GUM uncertainty budgets → ARC-AGI-3

## 1. Objects and techniques
- Measurement model Y = f(X1..XN) (GUM, JCGM 100:2008).
- Uncertainty budget: u(xi), sensitivity ci = ∂f/∂xi, contribution |ci|u(xi).
- Definitional uncertainty: the floor set by how well the measurand is specified (VIM3, JCGM 200:2012).
- Type A (repeat statistics) vs Type B (certificates, priors), combined on equal footing.
- Propagation law (first order); Welch–Satterthwaite → coverage factor k; Monte Carlo (JCGM 101:2008).
- Decision rules: guard bands, specific risk (JCGM 106:2012; ISO/IEC 17025:2017 §7.8.6; TUR 4:1); check standards (NBS measurement assurance).

## 2. Map TO
- P1: segmentation = defining the measurand. Its ambiguity is definitional uncertainty, which more data never removes.
- P2: rule = measurement model; transitions = Type A; earlier-level rules and priors = Type B. No noise, so all uncertainty is about the model's form, which GUM assumes away.
- P3: probe the component that dominates the decision, weighted by sensitivity.
- P4: a counter is an uncalibrated indicator; fit its response to actions first. Weak.
- P5: committing to a plan = a conformity decision, with the guard band set by the cost of a false accept (wasted actions, reset) vs a false reject (an extra probe).
- P6: a traceability chain across levels; inherited rules stay Type B until re-verified.
- P7: TUR-style sufficiency: never resolve finer than the decision needs; drop components below ~1/10 of the dominant one.
- P8: check standards: re-run a known transition as a control point. An error that does not fall with repetition is systematic: the representation is wrong.

## 3. Map FROM
- ARC-3 is metrology's blind corner: zero noise, discrete structural uncertainty. Propagation, k and νeff do nothing there; only the decision-rule layer survives.
- GUM-6:2020 discusses choosing a model but gives no budget term for that choice. ARC-3 needs a "Type C".

## 4. Grades
- P1, P2, P6: FRAME
- P3 dominance: TOOL (it is value of information)
- P5 cost-based guard band: TOOL
- P7 sufficiency: TOOL
- P8 non-shrinking residual → re-segment: TOOL
- P4: LOW
- Propagation, coverage factors, Welch–Satterthwaite, Monte Carlo: nothing.
- HIT: none.

## 5. Candidates
C1 Guard-banded commit (P3, P5, P7). Score each unresolved rule component of the best plan as P(wrong) × the fraction of plan steps that depend on it × the cost of failure. Execute when the summed risk is below the cost of the cheapest probe that resolves the dominant component; otherwise probe that component only.
Kill: with the same learner, if median actions-to-complete is not ≥10% below the best tuned "explore k, then plan" schedule, kill.

C2 Provenance ledger plus a systematic-error trigger (P1, P6, P8). Each rule records whether it was inherited or verified here; goal-directed actions double as checks, and a mismatch demotes an inherited rule. If the rate of unexplained transitions stays flat as observations grow, re-segment objects instead of gathering more.
Kill: on levels ≥2, if under 5% of wasted actions trace to stale inherited rules or wrong segmentation, kill.

## 6. Adversary
C1: value of information with a linear decomposition, which breaks when discrete components interact; P(wrong) is uncalibrated. Prior art: Howard 1966; Lindley 1956; Russo & Van Roy 2014 (information-directed sampling, the closest); Williams & Hawkins 1993 (guard-band economics).
C2: model-based agents already check every prediction; this adds bookkeeping, not capability. Prior art: Schmidhuber 1991; Friston et al. 2015 (epistemic value); OIML D10:2007. I know of no ARC-specific prior art.

Verdict: no HIT. GUM assumes a known model with small noise, the opposite of ARC-3; only its decision rules transfer.
