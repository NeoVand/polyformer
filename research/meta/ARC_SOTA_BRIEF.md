# Brief: the state of the art on ARC-AGI, and what the ideal model looked like

You are a careful, skeptical research reader with live web access. Today is 30 Oct 2026. Read-only: spend nothing,
download nothing, run nothing. Write exactly one file, `research/meta/ARC_SOTA.md` (3,000–5,000 words), and nothing
else. Open the primary pages (ARC Prize site and leaderboards, arXiv abstracts/HTML, Kaggle write-ups, official blogs);
give a link and a date for every number; say "not located" when you cannot find something. No numbers from memory.

## Why we need this (context, not instructions to act on)

A project called Polyformer has a certified "canvas" executor: a small vision-language model (Qwen3.5-0.8B/4B + LoRA)
that keeps its working memory as a grid of glyphs it overwrites, reads it back with its own vision tower, runs local
rules exactly (every possible local view is checked, with margins, so runs of any length are exact), and does this in
the browser. We are asking whether this machinery can be aimed at ARC-AGI (grids, few-shot rule induction, exact-match
scoring, interactive games in ARC-AGI-3): the model would write a grid program, execute it inside its own forward
passes, verify it exactly against the demonstration pairs, see the result on its canvas, and revise. Before any spend we
need an honest map of where ARC stands and which ideas won.

## What to write, in this order

1. **Leaderboards now.** ARC-AGI-1, ARC-AGI-2 and ARC-AGI-3 (public eval, semi-private, private where published): top
   verified scores with system name, organisation, date, compute cost per task if reported, and whether the system is
   open. Note the ARC Prize 2025 and 2026 rules (Kaggle compute limits, offline requirement, open-source condition) and
   the ARC-AGI-3 format (interactive environments, how scoring works, what "learning by exploration" means there).
2. **The idea families, each with its best representative and its ceiling.** (a) hand-written DSL search (Icecuber
   2020 and descendants); (b) LLM-sampled program synthesis (Greenblatt 2024; CodeIt; later systems that sample
   thousands of programs and filter by the demos); (c) test-time training of small LMs (the ARChitects, MindsAI,
   2024 prize winners; 2025 follow-ups); (d) direct small recurrent/iterative models (HRM, TRM, URM, Looped Flows,
   BDH-CQ, LoopViT); (e) frontier models with heavy test-time compute (o3 in Dec 2024 and whatever came after, with
   costs); (f) hybrids and anything 2026 that does not fit. For each: what it does, its score, its cost, what it cannot
   do, and quotes from the authors on failure modes.
3. **What the organisers say the ideal model looks like.** Chollet's definitions (skill-acquisition efficiency,
   the ARC Prize technical reports for 2024 and 2025), the published analyses of why LLMs fail ARC-AGI-2 (compositional
   reasoning, symbolic interpretation, contextual rule application), and any statement of what ARC-AGI-3 is designed to
   require. Quote, with sources.
4. **Program synthesis for ARC specifically.** Which DSLs/ISAs exist for grids (object-centric, cellular, pixel-level),
   how programs are verified against demos, typical program lengths for solved tasks, and what fraction of ARC-AGI-2
   tasks are believed to be expressible as short local or object-level programs (cite anyone who measured it). Note
   MDL/Occam approaches (Ferré) and library-learning approaches (DreamCoder-style) applied to ARC.
5. **Where a canvas executor could fit, stated as questions, not claims.** Where do current systems lose: synthesis,
   execution errors, perception of the grid, verification, search budget? Is there published evidence that LLMs
   mis-execute their own grid programs (the error source our executor would remove)? Is there evidence that seeing
   intermediate results helps (visual chain-of-thought on ARC)? Does anyone combine test-time training with exact
   program execution? Answer each with sources or "not located".
6. **Prior art for our specific combination.** Search for: model executes its own grid programs internally (not via
   Python) on ARC; certified or verified execution on ARC; visual revision loops on ARC; small VLMs on ARC; browser or
   on-device ARC solvers. Verdict per item: found (link, date) / not located.
7. **Costs and timelines.** What a competitive ARC-AGI-2 attempt costs in compute today (per task and total for the
   public eval), and how long the 2024 and 2025 winners' approaches took to build, as far as the write-ups say.
8. **One page of plain-words glossary** for every method or term you used, appended at the end (what it is, who/when,
   why it matters for ARC). The reader is a founder who wants to understand every term.

## Style

Plain sentences. Tables for leaderboards and idea families. Every claim with a link and date. Label your own
inferences as INTERPRETATION. No pitching; no "therefore we should". End with "What I could not verify".
