# R6: jazz comping and ARC-AGI-3

## 1. Subfield
Objects
- The form: a cyclic chorus (blues, AABA, rhythm changes from 1930). It is a shared clock with landmarks.
- The rootless voicing (Evans, Kelly, late 1950s): the 3rd and 7th fix the chord, and the bass carries the root.
- The contrafact: a new melody over old changes (Parker, Anthropology, 1946).

Practices
- Dynamic attending (Large & Jones 1999) and phase correction (Vorberg & Wing 1996).
- Schematic vs veridical expectation (Bharucha 1987; Huron 2006).
- Finding the changes by ear; laying out (Berliner 1994).

## 2. Map to problem
- P1: guide tones mean keeping only the features that fix a transition class. LOW.
- P2: hearing the changes is matching against a small vocabulary of cadences. TOOL.
- P3: a player sitting in tells a blues from rhythm changes by bar 5. Exploration is a probe that splits library hypotheses. TOOL.
- P4: a dominant implies its tonic. The goal is the state that removes a visible asymmetry. FRAME.
- P5: voice leading is the minimal-motion path through ordered subgoals. LOW.
- P6: contrafacts index mechanics by transition skeleton, not by sprite. A new level is old A sections plus a new bridge: explore only where predictions fail. FRAME.
- P7: laying out means no action without information or progress. FRAME.
- P8: the drummer keeps time whatever the soloist does. Split each frame delta into clock and action channels; a mismatch flags a rule. TOOL.

## 3. Map from problem
- Comping is easy because the lead sheet is given. ARC-3 is the jam session where nobody calls the tune.
- Players learning by ear find the form fast only because the repertoire of forms is tiny. Human speed on ARC-3 likely has the same cause: a few dozen game forms (push, key-door, toggle, paint, gravity), each recognised from 1–3 events.
- The ARC-3 score is "bars until the sitter-in finds the changes", which jazz never measures.

## 4. Grades
- HIT: none.
- TOOL: P2, P3, P8.
- FRAME: P4, P6, P7.
- LOW: P1, P5.

## 5. Candidates
C1, the sitter-in probe (P2, P3, P6, P7)
- Keep a library of game forms, each a rule template that predicts every action's effect.
- Act where the predicted outcomes best split the surviving forms, and break ties by goal progress. On a new level, replay the old forms first and open new hypotheses only at the first failed prediction.
- Kill: it needs ≥80% of the actions random diff-exploration needs to reach a correct one-step model, or the right form is in the library on <50% of public levels.

C2, the drummer split (P1, P2, P8)
- Fit period detectors to changes that occur under every action, giving a clock model.
- Credit only the leftover change to the chosen action, with a null action (bumping into a wall) as the control.
- Kill: <10% of public transitions contain any change that does not depend on the action.

## 6. Adversary
C1
- Objection: ARC-3 is built for novelty, so a hand library misses the mechanics that matter. Information gain over wrong hypotheses is confidently wrong.
- Prior art: EMPA (Tsividis et al. 2021); Lindley 1956; DreamCoder (Ellis et al. 2021).

C2
- Objection: turn-based worlds move when you move, and timers are visible. This is a frame diff with extra steps.
- Prior art: contingency awareness (Bellemare et al. 2012); Choi et al. 2019; Thomas et al. 2017.

## Verdict
Frames and one diagnosis (a small repertoire of forms), no new mechanism.
