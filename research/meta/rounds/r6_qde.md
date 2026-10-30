# R6: Questioned-document examination → ARC-AGI-3

## 1. Objects and practices
- O1 Class vs individual characteristics: copybook features shared by a cohort vs idiosyncratic habits (Osborn 1910/1929).
- O2 Natural variation: no writer repeats exactly; identical signatures suggest tracing (Osborn).
- O3 Exemplars: requested (dictated, repeated) vs collected (course-of-business) standards.
- T1 Significant-difference principle: one fundamental difference beyond natural variation eliminates; identification needs many concurring features (Huber & Headrick 1999).
- T2 Nine-point conclusion scale with "no conclusion" (ASTM E1658, 2004).
- T3 Error rates: Kam et al. 1994/1997 (experts beat laypeople mostly by abstaining); NAS 2009; PCAST 2016; Hicklin et al. 2022 (~3% false "written by"). Bias control: linear sequential unmasking, LSU (Dror et al. 2015).

## 2. Map to ARC-3
- P1: class = sprite type, individual = instance pose/colour; variation range = animation frames as one object. Line quality (stroke order from crossings): weak.
- P2: hand = environment, habit = rule, exemplar = transition; T1 = one counterexample kills a rule, but only outside the measured variation range.
- P3: like-for-like: compare an action's effect only in matched local context; repeat once to expose hidden state (timers).
- P4: rare features weigh more (likelihood ratio vs a background population). LSU: register causes before the event, so hindsight cannot credit the last action.
- P5: none.
- P6: copybook = cross-game class features (walls, keys, counters); measure novelty against that population, not the episode.
- P7: T2 gating, only "identification"-grade rules enter the planner. Kam's gain is abstention, which efficiency punishes.
- P8: post-identification mismatch is within envelope (ignore) or fundamental (reopen): blocks drift and thrashing.

## 3. Map from ARC-3
- QDE cannot intervene. One designed probe settles what passive exemplars leave "probable"; part of the measured error rate is the price of passivity.
- QDE has no theory of exemplar cost; "how many signatures" is a rule of thumb. ARC-3 charges per exemplar.
- QDE verifies discriminatively; ARC-3 permits generative checks (predict the next frame = write as the suspect would).

## 4. Grades
- P1 class/individual: FRAME. Line quality: LOW.
- P2/P8 significant difference + envelope: TOOL.
- P3 like-for-like + repeat: TOOL.
- P4 rare-feature LR, LSU: TOOL.
- P6 copybook prior: FRAME.
- P7 scale/abstention: FRAME.
- P5: nothing. HIT: none.

## 5. Candidates
C1 Envelope falsifier (P2, P8, P7). Each induced rule tags every grid channel fixed or variable, from two matched-context exemplars. A miss in a fixed channel eliminates the rule at once; a miss in a variable channel is only logged. Rules reach the planner only at "identification" grade.
Kill: under 10% fewer actions-to-complete than a diff-masking baseline on the public games.

C2 Background-LR credit (P4, P6, P3). On a progress event, score candidate causes by likelihood ratio against feature frequencies from a cross-game corpus. Candidates must be registered before the event (LSU). The top cause seeds the next level's goal hypothesis.
Kill: top-1 cause fails to beat "last object touched" by 15 points at predicting level 2's win condition.

## 6. Adversary
- C1: ARC-3 is near-deterministic; "variation" is hidden state, and pixel masking already handles it. Prior art: DOORMAX (Diuk, Cohen & Littman 2008), one-counterexample elimination; version spaces (Mitchell 1982); status-bar masking in 2025 ARC-AGI-3 preview agents.
- C2: designers make goals salient, so salience is cheap; few public games give a noisy background. Prior art: forensic LR (Lindley 1977; Aitken & Taroni 2004); count-based novelty (Bellemare et al. 2016); hindsight credit assignment (Harutyunyan et al. 2019).

Verdict: nothing reaches HIT. The yield is vocabulary: a principled line between noise and counterexample.
