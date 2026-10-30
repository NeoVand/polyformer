# R6: status games in improvisation (Johnstone)

## 1. Objects and techniques
- O1 Status: something you *do*, not *are*; relational and momentary (Impro, 1979).
- O2 The offer: any partner act, accepted or blocked (Impro, 1979).
- O3 Platform and tilt: the routine a scene sets up, and the event that breaks it (Impro for Storytellers, 1999).
- T1 See-saw: one party rises as the other falls; status is read from tiny cues (a still head, an "er").
- T2 Accept vs block: accepting builds the scene; blocking kills it.
- T3 Reincorporation: endings satisfy by bringing back earlier elements; look back at what is established, not ahead.

## 2. Map to problem
- P1 State = pairwise status: a role (wall, pushable, hazard) is set by who yields when objects meet. Avatar = what follows my actions.
- P2 Rule = a type×type→outcome table. See-saw: find quantities moving oppositely in one transition (a bar shrinks as a count grows).
- P3 Search = offers. No change is a block: prune it. Changes I did not cause are offers: accept them first.
- P4 Check = legibility: the designer made the scene readable, so anything shown twice (HUD and board pattern, key and lock) is a constraint the goal reincorporates.
- P5 "Walk backwards" = regress from that target; standard.
- P6 Memory = platform; new level = platform + tilt. Replaying the old routine, the first failure locates the tilt.
- P7 "Be obvious": generic Occam.
- P8 Hold status until contradicted. Nothing new.

## 3. Map from problem
- ARC-3 is an improv scene whose partner only accepts or blocks; the player is the audience.
- Human efficiency supports Johnstone's claim that roles are read instantly; an agent lacking that layer pays actions for it.
- ARC-3 measures legibility: how often is the obvious move right?

## 4. Grades
- Pairwise status as role (P1, P2): FRAME; VGDL (Schaul 2013) and EMPA (Tsividis et al. 2021) learn type-pair interactions.
- See-saw pairing (P2): TOOL; conserved-quantity search (Schmidt & Lipson 2009), likely unused here.
- Accept/block (P3): FRAME; no-op pruning is standard.
- Platform/tilt replay (P3, P6, P7) and reincorporation goal prior (P4): TOOL.
- P5, P7, P8: LOW. HIT: none.

## 5. Candidates
C1 Tilt localiser (P3, P6, P7). On level k, diff sprite types against earlier levels and replay the previous solution as object-level subgoals. Record the first mispredicted step and every new type. Explore only those spots before generic curiosity.
Kill: on public levels ≥2, neither the first replay failure nor a new type touches the new mechanic in at least 60% of levels.

C2 Reincorporation goal prior (P4, P5, P2). List region pairs matching up to colour, shift or rotation, and see-saw counter pairs. Hypothesise "make A equal B" or "drive the counter to its extreme", ranked by how many elements each brings back; plan to the top one, switch on a block.
Kill: the top hypothesis is the true win condition in under 40% of solved public levels (scored from winning traces).

## 6. Adversary
- C1: old sprites can gain new behaviour, leaving the diff empty; prediction-error curiosity already chases surprises. Prior art: kishōtenketsu level design (Nintendo, Hayashida, ~2012); options (Sutton, Precup & Singh 1999); ICM (Pathak et al. 2017).
- C2: many goals are reach-or-clear, not match; repeated colours make false pairs; LLM agents already guess "match". Prior art: goal recognition as planning (Ramírez & Geffner 2009); Gestalt similarity (Wertheimer 1923); Chollet's goal-directedness prior (2019). No exact ARC-3 precedent known to me.

Verdict: framing and two TOOLs. No HIT.
