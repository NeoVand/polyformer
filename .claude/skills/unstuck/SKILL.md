---
name: unstuck
description: Make a stuck or narrow research/engineering effort produce genuinely new, cross-field ideas by forced distant mappings, decomposition, recombination, an in-round adversary, scoring and hill-climbing. Use when ideas keep coming back narrow, when a result disappoints and the only moves on the table are variants of the last one, when prior-art gates keep returning "narrow", or when someone says "think bigger". General purpose; no project assumptions.
---

# unstuck: a harness for integrating what the model already knows

Models recall what the recent context cues. A context full of one topic cues more of that topic; the theorem from a
distant field that would solve the problem never fires because nothing points at it. This skill forces the pointing.
Run it as written; the discipline is the point. Output is many short lines, not one careful paragraph.

## 0. Ground and decompose (10 minutes)

- Write the goal in one sentence. Read the primary source for it (the benchmark rules, the spec, the failing log) for
  ten minutes before anything else; note three facts you did not know.
- Decompose the goal into 5–8 sub-problems P1..Pn (perception, induction, search, memory, execution, evaluation... whatever
  fits). Mapping to sub-problems is sharper than mapping to the whole.
- **Constraint sweep.** List every constraint: the ones you were given and the ones you inherited by habit ("must use
  model X", "must be certified", "no external tools"). For each, write one line of what becomes possible if it is dropped.
  Keep the list visible; history is lessons, not a prison.
- Read the **dead-framings list** (section 5) if one exists. No variant of a dead framing may run without a stated change
  of level (phenomenon → mechanism → theorem → architecture → experiment).

## 1. Draw eight fields by dice, not by taste

**Sampling frame (principled).** Do not hand-write the field list; a hand-written list is the author's taste wearing a
dice costume. Use a published taxonomy of human knowledge and practice as the frame and sample its leaves:
- academic fields: the UNESCO nomenclature for fields of science and technology (1988; ~2,000 six-digit leaves), or
  Wikipedia's "Outline of academic disciplines" (several hundred subfields), or arXiv + MeSH + JEL codes together;
- practices, crafts and trades: O*NET occupation titles (~1,000) or Wikipedia's lists of hobbies, sports and crafts.
Stratify by top-level branch (natural sciences, engineering, medicine, agriculture, social sciences, humanities, arts,
trades/crafts, sports/games) so no branch dominates, then draw leaves uniformly within branches with a fixed random
source (digits of π, a seeded RNG) and record the seed and the draw. Skip leaves used in the last two rounds. Optionally
bias half the draws toward leaves far from the problem's own field (embedding distance) and half toward mid-distance;
pure relevance is the failure mode this skill exists to break. Do not swap a field because it "obviously" does not apply.

**Offline fallback.** If no taxonomy is at hand, the 40-item list below is an unprincipled stand-in (one author's attempt
at breadth across sciences, crafts, arts and professions); say so in the round log. Map digit pairs to indices.

1 accounting · 2 ethology (animal behaviour) · 3 archaeology · 4 architecture (pattern language) · 5 astronomy ·
6 cartography / SLAM · 7 chess and game design · 8 child development (core knowledge) · 9 cooking · 10 cryptanalysis ·
11 detective fiction (abduction) · 12 ecology · 13 epidemiology · 14 experimental design · 15 forensics · 16 geology ·
17 improv theatre · 18 jazz · 19 jurisprudence (precedent) · 20 field linguistics · 21 martial arts · 22 medicine
(differential diagnosis) · 23 metrology · 24 military doctrine · 25 mountaineering · 26 navigation · 27 operations
(Toyota, queues) · 28 ornithology · 29 philosophy of science · 30 poker · 31 puzzle design · 32 reverse engineering ·
33 sailing · 34 sign language · 35 sports coaching · 36 surgery · 37 typography · 38 urban planning · 39 wine tasting ·
40 zoology. Academic cores to add when you need theorems: symbolic dynamics, coding theory, control theory, statistical
physics, category theory, PL/compilers, learning theory, cognitive science, cryptography, operations research, topology.

## 1b. Then draw a **subfield** by dice (depth beats breadth)

Fields are too broad; crazy ideas come from a deep lookup, not from smeared attention. For each drawn field, list 8
subfields (specific practices, theories or techniques: "SIR compartmental models", not "epidemiology"), then take the next
digit of the random source and pick subfield (digit mod 8) + 1. The subfield is what gets mapped. Write the subfield
lists down so the draw is auditable.

## 1c. One isolated agent per subfield (no mixing before ideas exist)

Hand each subfield to a separate agent with a fresh context. Each agent receives: the goal in one sentence, the primary
facts from step 0, the sub-problem list, its own subfield, and the mapping protocol below. It receives **nothing** about
the other subfields, the other agents, or any candidate system already on the table; shared context produces correlated
ideas. Agents write short reports (≤ 500 words) to separate files. Mixing (step 3) starts only when all reports are in.

## 2. Force the mapping (per subfield, by the isolated agent, minimum effort enforced)

For each subfield, before you may write "nothing":
- Name **3 objects** in that field and **3 techniques or theorems** it uses.
- Map **to** the problem: for each sub-problem Pi, what in this field plays the role of our state, our rule, our check,
  our search? Which technique transfers, verbatim or by analogy?
- Map **from** the problem: what does our problem say about that field? (Bidirectional mapping surfaces structure.)
- Grade the yield: **HIT** (imports a theorem or mechanism we did not have), **TOOL** (a known technique we were not
  using), **FRAME** (a better description, no new mechanism), **LOW**, **nothing**. Be stingy with HIT.

## 3. Recombine and attack (15 minutes)

- Combine 2–3 HITs/TOOLs into **one or two candidate systems**, each with: the mechanism in three sentences, the
  sub-problems it addresses, and **one experiment** with a number that would kill it.
- **Adversary, immediately:** for each candidate, the strongest objection and the closest prior art you can recall, with
  years. If you cannot name the closest prior art, you do not yet understand the idea.
- **Score** each candidate 1–5 on novelty, feasibility, cost, impact. Write the weakest sub-problem of the best candidate.

## 4. Hill-climb

The next round keeps the best candidate and spends six of its eight fields on that candidate's weakest sub-problem, plus
two fields drawn fresh as random restarts. Repeat until two consecutive rounds add no HIT, then stop and gate the best
candidate against live prior art before building anything.

## 5. Keep the memory

Maintain, in the project, (a) a **dead-framings list**: framings tried and why they died, read at the start of every
round; (b) a **glossary** of every method or term you used, one line each, so the humans deciding can follow;
(c) the round logs themselves. The yield of the harness (HITs per round that survive a prior-art gate) is a number;
track it.

## Rules of conduct

- Many short lines beat one careful paragraph; generate first, judge after.
- Say which constraint an idea breaks and what it buys; never silently respect a constraint nobody confirmed.
- Name the field a problem belongs to before inventing a trick; most problems are old somewhere.
- Prior art kills a *claim*, not an idea; take the gate's "what remains open" as the seed of the repair.
- Never answer a disappointing result with a same-level variant.
