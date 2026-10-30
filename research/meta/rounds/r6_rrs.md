# R6 · Racing Rules of Sailing → ARC-AGI-3

## 1. Objects, techniques
- O1 Definitions (RRS 2025–28): Overlap, Keep Clear, Zone (3 hull lengths since 2009), Mark-Room, Proper Course. Glance-checkable relations.
- O2 Part 2 Section A, rules 10–13: four exhaustive pair cases decide who keeps clear; Sections B–C limit and override.
- O3 Protest hearing (Part 5): facts found → conclusions → rules → decision, on a time-step diagram; Case Book as precedent.
- T1 Zone-entry latch (rule 18.2): overlap when the first boat reaches the zone fixes mark-room until a release event.
- T2 Reasonable-doubt presumption (rule 18.2): an unprovable overlap change is presumed not to have happened.
- T3 Exoneration (rule 43), Two-Turns Penalty (44.2); facts are final, appeal only on rules (70.1).

## 2. Map TO
- P1: state = O1 relations between object pairs; "overlap" = projection overlap on an axis, "zone" = k-cell radius.
- P2: rule = O2 decision list: few relations → exhaustive cases → explicit overrides; T1 latches for non-Markov parts.
- P3: none; hails probe intentions, which ARC objects lack.
- P4: Proper Course is defined counterfactually ("in the absence of the other boat"); rule 28's string = goal as ordered mark sides.
- P5: Keep Clear = plan so the other party needs no action. LOW.
- P6: Case Book: cases keyed by relational configuration; a new level adds an overriding Section, older Sections still apply.
- P7: rules switch on only when boats meet; gate compute on proximity events.
- P8: T3: perception frozen, revision targets rules only; exonerate (upstream rule fired) before revising; T2 gives ambiguity a fixed default.

## 3. Map FROM
- ARC-3 is RRS with no rulebook and no jury: the agent is sailor, protest committee and rule-writer.
- Revisions (1997, 2009) pushed RRS toward glance predicates; instruction-free games should share that shape: few relations, exhaustive cases, explicit overrides, rare latches.
- Sailors learn from verdicts; ARC-3 has none, so the hearing must be internal.

## 4. Grades
- T1 latch: TOOL. O2 decision-list prior: TOOL. Meeting-gated compute: TOOL.
- T3 facts-final, exonerate-first: FRAME. T2: FRAME. Sailor + committee + rulebook: FRAME.
- P3, P4, P5: LOW.
- HIT: nothing.

## 5. Candidates
C1 Hearing-gated rule learner (P2, P6, P8).
Hypotheses are precedence-ordered decision lists over pairwise relations (touch, row/column overlap, within k, same colour), plus latches snapshotted when an object enters a region and held until it exits.
A mispredicted transition opens a hearing: frames are frozen as facts, then try exoneration (another rule fired first), a latch, and finally a new overriding rule.
New levels append overriding Sections instead of rewriting old ones.
Kill: latches repair under 10% of a Markov relational model's residual mispredictions on the public games.

C2 Meeting-gated exploration (P3, P7).
Learn free motion once per object class; spend induction and actions only on meetings (pairs within a zone).
Choose actions that produce an unseen class-pair × relation case.
Induction cost scales with meeting types, not frames.
Kill: over 30% of state changes occur with no pair within 2 cells (counters, global toggles), or actions-to-first-level drops under 20% against count-based novelty.

## 6. Adversary
- C1: designed puzzles rarely hide hysteresis beyond inventory, which a count feature covers. Prior art: AutumnSynth (Das et al., POPL 2023), event-triggered latent state; Utile Suffix Memory (McCallum 1995); default logic (Reiter 1980).
- C2: it is EMPA (Tsividis et al. 2021, theory-based RL in VGDL games); also OO-MDPs (Diuk, Cohen, Littman 2008), Schema Networks (Kansky et al. 2017).

Verdict: a clean frame and a rule-shape prior; no mechanism new to ARC.
