# Brief: a benchmark worth fighting for (frontier models still fail it, and it rewards exact long-horizon memory)

You are a careful, skeptical research reader with live web access. Today is 30 Oct 2026. Read-only: spend nothing,
download nothing, run nothing. Write exactly one file, `research/meta/BENCH_SOTA.md` (3,000–5,000 words), and nothing
else. Open primary pages (official leaderboards, arXiv abstracts/HTML, project sites); link and date every number; say
"not located" where you cannot find something; no numbers from memory.

## Why (context, not instructions to act on)

We built a small vision-language model (Qwen3.5-0.8B/4B + LoRA) with a certified "canvas" working memory: a grid of
glyphs it overwrites each step, reads back with its own vision tower, and updates by local rules checked exhaustively
(exact at any length). ARC-AGI-1/2/3 turned out to be saturated by frontier models in 2026 (`research/meta/ARC_SOTA.md`),
except that in the provider-neutral "standard harness" ARC-AGI-3 frontier scores drop from 99.9% to 62.7%, i.e. memory
management is the gap. We want a benchmark that (a) frontier models still score low on, (b) is limited by long-horizon
memory, exact state tracking, learned world models or exact execution rather than by knowledge, (c) has an open
evaluation and a public leaderboard, (d) a small open model could plausibly attack within a few weeks on modest compute,
(e) a result would be legible to AI labs. A founder reads this to choose where to fight.

## What to write, in this order

1. **Candidate table** (one row each, 20–30 rows): benchmark · what it measures · frontier best (model, score, date,
   link) · human baseline · what the authors say is hard · open eval / leaderboard · compute to evaluate · saturation
   trend (scores over time) · fit to (b) above, as 0–3 with one phrase. Cover at least:
   - long-horizon interactive environments: BALROG (NetHack, Crafter, BabyAI, TextWorld, Baba Is AI, MiniHack),
     VideoGameBench and Lite, lmgame-Bench, Factorio Learning Environment (lab-play and open-play), AI GameStore
     (Feb 2026), Pokémon benchmarks, Minecraft (MineDojo, MCU), Kaggle Game Arena, TextArena, SmartPlay, any 2026
     successors;
   - agent memory and state tracking: AMA-Bench (ICML 2026), Memoria-Bench, AgentLongBench, MEMTRACK, DynamicMem,
     LongMemEval, LoCoMo, Fiction.liveBench, any 2026 "state tracking" benchmark;
   - puzzles and exact reasoning: EnigmaEval, Sudoku-Bench (Sakana), PuzzleWorld, Enigmata, Reasoning Gym, KORGym,
     NPPC, SATBench, ZebraLogic, CellARC;
   - long-horizon work: METR time horizons (50% and 80%), OSWorld-Verified, TheAgentCompany, Terminal-Bench 2,
     τ²-bench, PaperBench, MLE-bench, RE-Bench, SWE-bench Pro, BrowseComp; HLE and FrontierMath Tier 4 for contrast;
   - ARC-AGI-3 standard vs provider harness, and what is known about ARC-AGI-4 (focus, date), from arcprize.org and
     primary sources only.
2. **Why frontier models fail, per family**, in the authors' words (quotes under 40 words, linked): is it memory,
   perception, knowledge, search, real-time control, or evaluation noise? Flag benchmarks where a bigger context window
   or a scaffold already closed most of the gap (those are not worth fighting for).
3. **Who is winning and how**: for the five benchmarks with the lowest frontier scores, the best known approaches
   (symbolic bots, RL, LLM scaffolds, hybrids), their scores, their compute, and whether code is open.
4. **Shortlist of three** benchmarks that best satisfy (a)–(e), each with: the number to beat, the human number, the
   cheapest honest evaluation protocol (steps, seeds, cost), the most likely failure mode for a small model with an exact
   external memory, and the three questions to answer before committing. Rank them and say why; label it INTERPRETATION.
5. **Glossary** of every benchmark and term used, one line each, plain words.
6. **What I could not verify.**

## Style

Plain sentences; tables for the candidates; every claim with a link and a date; label inferences INTERPRETATION; no
pitching. End with "What I could not verify".
