# Benchmarks frontier models still fail: a sourced survey (30 Oct 2026)

Read-only survey for Neo, written for the brief in `research/meta/BENCH_BRIEF.md`. Every number has a link and a date;
"read 30 Oct" marks a live page with no date of its own. Inferences are labelled INTERPRETATION. Terms are defined in
section 5.

**How it was gathered.** Four sub-agents read the primary pages for the games, memory, puzzle and work families on
30 Oct. I re-opened the pages behind the shortlist myself: the BALROG leaderboard, AutoMem, AMA-Bench, AI GameStore,
ARC Prize and Twin. Quotes came through a fetch tool that summarises pages with a small model; each was requested
verbatim, and the ones it could not confirm are marked (paraphrase). Abbreviations: **SR** self-reported, not
reproduced by the benchmark owner; **VR** vendor-reported; **AGG** third-party aggregator.

**Headline.** Most benchmarks with low 2026 frontier scores are low for one of three reasons that a small model with an
exact memory does not fix: knowledge (EnigmaEval, Agents' Last Exam), perception and real-time control
(VideoGameBench), or no maintained leaderboard. The memory-limited ones that labs know are either already closed by
scaffolds (LongMemEval, LoCoMo, Pencil Puzzle Bench, ARC-AGI-3) or still open but rising fast (BALROG-NetHack:
0.4% → 13.2% in 22 months).

---

## 1. Candidate table

Fit = fit to criterion (b), being limited by long-horizon memory, exact state, learned world models or exact
execution. It runs 0–3 and is INTERPRETATION throughout.

### 1a. Long-horizon interactive environments

| Benchmark | Measures | Frontier best | Human | Hard, per authors | Open / board | Eval cost | Trend | Fit |
|---|---|---|---|---|---|---|---|---|
| **BALROG-NetHack** ([paper](https://arxiv.org/abs/2411.13543), ICLR 2025) | NetHack progression %; text plus ASCII map; default history of 16 observations | GPT-6-Astra-Max **13.2 ± 2.7** (2026-09-18, SR); best checked Gemini-3-Pro **6.8 ± 3.2** (2026-02-03) ([board](https://balrogai.com), read 30 Oct) | no % located; the metric is built from human games | knowing-doing gap; a win takes "hundreds of thousands of steps" | code ([GitHub](https://github.com/balrog-ai/BALROG)); weekly board, ✔ = reproduced | 5 seeds (App. F); $ not located | 0.4 (Nov 2024) → 1.8 (Jul 2025) → 6.8 (Feb 2026) → 13.2 (Sep 2026) | **3**: long-horizon map and state, plus game knowledge |
| BALROG others | MiniHack, Crafter, TextWorld, BabyAI, Baba Is AI | Astra-Max MiniHack 65.0, Crafter 76.8; Opus-5-Max TextWorld 71.6 (Sep 2026, SR); BabyAI and Baba 100 | Crafter experts 50.5% on a different metric ([2021](https://ar5iv.labs.arxiv.org/html/2109.06780)) | as above | same | 5 seeds (MiniHack) | average 32.6 (Nov 2024) → 68.3 (Sep 2026) | MiniHack 2, Crafter 2, TextWorld 2, BabyAI and Baba 0 |
| VideoGameBench / Lite ([v3, 14 May 2026](https://arxiv.org/abs/2505.18134)) | 1990s console and DOS games from raw frames | Gemini 2.5 Pro and Claude 3.7 **0.48%**; Lite 1.6% (May 2025; no 2026 entries) | none numeric | latency, perception, scratchpad overwrite | code open; static board ([site](https://www.vgbench.com)) | ≤$30 per game run | no new models | 1: real-time play and pixels dominate |
| lmgame-Bench ([2505.15146](https://arxiv.org/abs/2505.15146)) | Sokoban, Tetris, 2048, Mario and others | o3 66.17 bare, 87.69 with harness ([board](https://lmgame-lmgame-bench.hf.space), "Latest Update June 07, 2025") | not located | perception, prompt sensitivity | open; stale | 3 runs per game | stale | 1: the harness closes much of it |
| Factorio (FLE) ([2503.09617](https://arxiv.org/abs/2503.09617)) | build factories by writing code; lab-play and open-play | Claude 3.5 Sonnet 7/24 lab tasks, open-play 293,206 (Mar 2025); 2026 entries not located | none | factory-layout "mental models" | open; board did not render | $1,318 for all paper runs | stale | 2: spatial state, but code and recipe knowledge |
| **AI GameStore** ([19 Feb 2026](https://arxiv.org/abs/2602.17594)) | 100 short games adapted from App Store and Steam, normalised to humans | GPT-5.2 **8.5% of human median** ([summary](https://www.emergentmind.com/papers/2602.17594)); abstract: best "<10% of the human average score on the majority of the games" | 106 online players, 120 s per game | "world-model learning, memory and planning" | MIT code ([GitHub](https://github.com/lance-ying/aigamestore)); 90 of 100 games private; board "Loading" (30 Oct) | not located | one time point | 2: memory named, but perception-heavy |
| Pokémon (PokeAgent) ([Mar 2026](https://arxiv.org/abs/2603.15563)) | Emerald speedrun to the first gym; battling | best baseline Gemini 3 Flash "~1.8× slower than the average human"; Opus 4.7 beat Red ([16 May 2026](https://www.lesswrong.com/posts/sehJYg5Yny9fvpbpt/a-year-late-claude-finally-beats-pokemon)) | average 1:22:05, top ~18 min | agents "wander aimlessly, repeat failed actions" | starter kit open; speedrun board empty (30 Oct) | Gemini 3 Flash $0.020 per battle | full games finished 2025–26 | 2: harnesses closed completion; speed gap remains |
| TextQuests ([v3, 13 Aug 2025](https://arxiv.org/abs/2507.23701)) | 25 Infocom text adventures, full history in context | GPT-5 **37.8%** without clues, 70.0% with clues (v3); 2026 not located | not located | models "hallucinate about prior interactions" | code open; board did not render, submissions by email | ~471M input tokens (o3) | not located | 3 in mechanism; Infocom puzzle knowledge too |
| Other suites: Minecraft (MineDojo, [MCU](https://arxiv.org/abs/2310.08367)), [Kaggle Game Arena](https://arxiv.org/abs/2609.31473), TextArena, SmartPlay | open-ended crafting; chess, poker, Werewolf; social text games | four Gemini 4 Argon agents killed the Ender Dragon in 27 h 14 m through a code API ([15 Oct 2026](https://arxiv.org/abs/2610.22319)); chess Elo led by Gemini 3 Pro Preview (25 Sep 2026); TextArena, SmartPlay not located | none | knowledge, search, social skill | mixed; boards did not render | not located | relative ratings or single runs | 0–1 |

### 1b. Agent memory and state tracking

| Benchmark | Measures | Frontier best | Human | Hard, per authors | Open / board | Eval cost | Trend | Fit |
|---|---|---|---|---|---|---|---|---|
| **AMA-Bench** ([v2, 4 Mar 2026](https://arxiv.org/html/2602.22769v2), ICML 2026) | questions about long agent trajectories: recall, causal, state updating (C), state abstraction (D); plus a synthetic BabyAI/TextWorld subset | GPT-5.2 **0.7226**; C 0.6563, D 0.6037 (Table 4) | not located | compression "fails to preserve dense state and causal information" | code, data, verified [board](https://huggingface.co/spaces/AMA-bench/AMA-bench-Leaderboard) | 2,496 + 1,200 questions; trajectories average 57.5K tokens | scaffolds on Qwen3-32B: 0.572 (Mar 2026) → ≈0.70 (Sep 2026, computed) | 2 real, 3 synthetic |
| Memoria-Bench | trajectory memory, including long-range state tracking | not located ([poster page](https://icml.cc/virtual/2026/poster/64414) returned 404) | — | — | not located | — | — | ? |
| AgentLongBench ([Jan 2026](https://arxiv.org/abs/2601.20730)) | entity-guessing rollouts of 32K–4M tokens; knowledge-free variant | Grok-4.1 >50 at 2M; knowledge-free "Intersection" "near zero for nearly all models" (2025-era models) | not located | "dynamic information synthesis" | code and data; no board | not located | stale models | 3 in mechanism |
| MEMTRACK ([Oct 2025](https://arxiv.org/abs/2510.01353)) and DynamicMem ([22 Jun 2026](https://arxiv.org/abs/2606.22877)) | Slack/Linear/Git timelines; 15-month app logs | GPT-5 0.601 (+Mem0 0.610); DynamicMem tested only gpt-5-mini | not located | Mem0 and Zep give "limited gains" | MEMTRACK data not located; DynamicMem open | 47 instances; 2.2M tokens per user | — | 2; 1–2 |
| LongMemEval (+V2) ([2410.10813](https://arxiv.org/abs/2410.10813); [V2, 12 May 2026](https://arxiv.org/html/2605.12493)) | chat memory (~115K tokens); V2 has web-agent histories up to 115M tokens | S: Mem0 94.4 ([26 Oct 2026](https://mem0.ai/research-3), VR); best independent re-run 86.5 ([Redis, 21 Sep 2026](https://redis.io/resources/agent-memory-benchmark-report/)); V2: 74.9 with a 9B reader | not located | V2: answer-bearing trajectories "remain sparse" | open; V2 board "coming soon" | ~57M tokens per full-context run | 60.2 (gpt-4o, 2024) → 94–96 (2026) | S 1 (saturated); V2 2 |
| LoCoMo, Fiction.liveBench, BEAM, MRCR v2 | dialogue memory; fiction comprehension to 192K; memory to 10M; multi-needle recall | LoCoMo >92 (VR, 2026); Fiction.liveBench gemini-3-flash 100.0 at 192K ([Apr 2026](https://fiction.live/stories/Fiction-liveBench-April-04-2026/oQdzQvKHw8JyXbN87)); BEAM-10M 68.0 (VR, [28 Jul 2026](https://www.webull.com/news/15304952493908992)) | LoCoMo F1 87.9 (2024) | LoCoMo audit: 6.4% of the key is wrong ([8 Apr 2026](https://penfieldlabs.substack.com/p/we-audited-locomo-64-of-the-answer)) | data mostly open | small to large | LoCoMo 37.8 F1 (2024) → >92; BEAM 0.27 → 0.68 in 9 months | 0–1: closed by context or scaffolds |
| MINTEval ([18 May 2026](https://arxiv.org/abs/2605.18565)) and StateMemBench ([20 Aug 2026](https://arxiv.org/abs/2608.19652)) | return the current value after many updates | MINTEval best **33.4** (MemAgent); StateMemBench best **0.363** (StateMem on DeepSeek-V4-Flash); **no GPT, Claude or Gemini-Pro answerer** | none | "not _retrieving_ the fact, but rather _tracking_ its relevance to current state" | MINTEval code and data; no boards | small | new | 3, but frontier not measured |

### 1c. Puzzles and exact reasoning

| Benchmark | Measures | Frontier best | Human | Hard, per authors | Open / board | Eval cost | Trend | Fit |
|---|---|---|---|---|---|---|---|---|
| EnigmaEval ([2502.08859](https://arxiv.org/abs/2502.08859)) and PuzzleWorld ([v2, Apr 2026](https://arxiv.org/html/2506.06211v2)) | puzzle-hunt puzzles | claude-fable-5-high **39.28%** ([Scale](https://labs.scale.com/leaderboard/enigma_eval), updated 23 Jul 2026); PuzzleWorld Gemini 3 Pro 18.00% | PuzzleWorld enthusiasts 44.44% | lateral thinking, OCR; spatial "sketching" | Enigma board and data; PuzzleWorld no board | 1,161 / 667 items | Enigma o1 7.0% (Feb 2025) → 39.28% | 0–1: knowledge and wordplay |
| Sudoku-Bench ([2505.16135](https://arxiv.org/abs/2505.16135)) | 100 variant sudokus, no tools | GPT-5 high **33%** ([Oct 2025](https://pub.sakana.ai/sudoku-gpt5/)) | none formal | "maintaining global consistency over long reasoning chains" | **discontinued**, code withdrawn ([GitHub](https://github.com/SakanaAI/Sudoku-Bench), read 30 Oct) | 100 puzzles | 14.0% (May 2025) → 33% | 2; a solver scaffold reaches 74.7% |
| Generator and search suites: Enigmata, Reasoning Gym, KORGym, NPPC, SATBench, ZebraLogic | procedural puzzles; NP-complete; SAT stories; logic grids | 2025 models: Enigmata 65.1, KORGym 82, SATBench 89.3; ZebraLogic 98.8 (AGG, Feb 2026); NPPC hardest levels "below 10%" ([v2, Feb 2026](https://arxiv.org/html/2504.11239v2)) | none | search; spatial and sequential tasks | code open; no maintained boards | NPPC $10–$522 per model | no 2026 entries | 1–2: training sources; solvers trivialise |
| CellARC ([2511.07908](https://arxiv.org/abs/2511.07908); [ICML 2026](https://icml.cc/virtual/2026/68262)) | few-shot 1D cellular-automaton rule induction | GPT-5 High 62.3 / 48.1 per-token (Nov 2025); a 10M-parameter transformer gets 58.0 / 32.4 | not located | unseen support windows are "information-theoretically ambiguous" | data and generator; board unreadable | small | — | 2: local-rule induction; single author |
| Pencil Puzzle Bench ([2 Mar 2026](https://arxiv.org/abs/2603.02119)) | pencil puzzles with checkable intermediate boards | claude-fable-5 **97.6%** with checker / 50.0% without ([ppbench.com](https://ppbench.com), read 30 Oct) | "No human performance baseline" | long-context use | open; board | ~$28k over 17,032 runs | 56.0 (Mar 2026) → 97.6 | 3 in mechanism; saturated with the checker |
| Long execution: LongReasonArena, Long-Horizon Execution | run given algorithms step by step | LongReasonArena L3 GPT-5 **27.8** ([board](https://github.com/LongReasonArena/LongReasonArena), undated); LHE: GPT-5 holds 80% for 2,176 steps ([v3, Mar 2026](https://arxiv.org/abs/2509.09677)) | not located | "failures are in execution" | open; README board | not located | — | 3; trivial with code; MAKER ran 1M steps without error |

### 1d. Long-horizon work, with knowledge benchmarks for contrast

| Benchmark | Measures | Frontier best | Human | Hard, per authors | Open / board | Eval cost | Trend | Fit |
|---|---|---|---|---|---|---|---|---|
| METR time horizons ([page](https://metr.org/time-horizons/), updated 8 Sep 2026) | task length finished at 50% / 80% reliability | Claude Mythos Preview p50 ≈17.4 h, p80 ≈3.1 h ([data](https://metr.org/assets/benchmark_results_1_1.yaml)) | defines the scale | "Measurements above 16 hrs are unreliable" | results public; no submissions | not located | doubling every 128.7 days since 2023 | 1: the ruler has hit its ceiling |
| OSWorld-Verified and OSWorld 2.0 ([2606.29537](https://arxiv.org/abs/2606.29537)) | desktop GUI tasks; 2.0: 108 workflows of ~1.6 h | V: 86.1% (VR, [steel.dev](https://leaderboard.steel.dev/leaderboards/osworld.md), 11 Oct 2026); 2.0: Claude Fable 5.1 **41.7%** binary (VR, [30 Sep 2026](https://leaderboard.steel.dev/leaderboards/osworld-2.md)) | V 72.36% | 2.0: "hidden state they must recover" | open; boards | 2.0: $25–72 per task on frontier models | 2.0: 20.6 (Jun) → 41.7 (Sep 2026) | V 0; 2.0 2, but GUI and cost |
| TheAgentCompany, Terminal-Bench 4.0, τ²/τ³ | office tasks; CLI tasks; tool-using service agents | TAC Gemini-2.5-Pro 30.3% (Sep 2025); TB4 Opus 5.5 + Claude Code **64.8%** ([Snorkel](https://snorkel.ai/leaderboard/terminal-bench/), 29 Sep 2026); τ² 87.9%, τ³-Banking 55.2% ([taubench](https://taubench.com), read 30 Oct) | not located | browsing; "Execution errors dominate"; retrieval | open; boards | TAC ~$735 per run; TB $1–100 | each refreshed when saturated | 1: skill, not state |
| PaperBench, MLE-bench, RE-Bench | replicate papers; Kaggle medals; ML research | PaperBench Code-Dev 93.0 (VR, Aug 2026); MLE-bench **64.44** (23 Feb 2026, board closed); RE-Bench 2026 not located | PhDs 41.4% (3-paper subset); experts 0.64 at 8 h | agents "failed to strategize"; "stubborn and incorrect assumptions" | code open; boards frozen or absent | MLE ~1,800 A10-hours per seed | MLE 16.9 → 64.4 | 1 |
| SWE-bench Pro, BrowseComp | repository tasks; hard-to-find web facts | Pro public 61.50 ([Scale](https://labs.scale.com/leaderboard/swe_bench_pro_public), read 30 Oct); BrowseComp 92.2% (AGG, 22 Aug 2026) | BrowseComp 29.2% | coding skill; persistence in search | open | not located | saturating | 0 |
| Vending-Bench 2 ([page](https://andonlabs.com/evals/vending-bench-2), read 30 Oct) | run a simulated business for a year | Gemini 4 Carbon $16,484 vs ~$63k for a "good" strategy | v1: one person $844 | "meltdown loops" (v1); lacks "analytical skills" | **closed**; Andon Labs runs it | 60–100M output tokens per run | $2,218 (v1, 2025) | 2; fails (c) and (d) |
| Agents' Last Exam ([2606.05405](https://arxiv.org/abs/2606.05405)) | expert workflows in professional software | hardest tier: "most agents score 0% pass rate"; overall ~38–40% (AGG, 19 Oct 2026) | n/a | "dominant bottleneck is domain knowledge" | open harness | $3–10 per task | — | 0 |
| HLE, FrontierMath Tier 4 (contrast) | expert questions; research mathematics | HLE-Diamond: Gemini 4 Carbon 69.1% ([AA](https://artificialanalysis.ai/evaluations/hle-diamond), read 30 Oct); FM-T4 GPT-6 Astra 97.6% (OpenAI via [36Kr](https://eu.36kr.com/en/p/3978639480617733), 11 Sep 2026) | not located | knowledge | HLE public; FM private | not located | FM-T4 19% (v1) → 97.6 | 0 |

### 1e. ARC-AGI-3 and ARC-AGI-4

| Benchmark | Measures | Frontier best | Human | Hard, per authors | Open / board | Eval cost | Trend | Fit |
|---|---|---|---|---|---|---|---|---|
| ARC-AGI-3, standard vs provider harness | instruction-free grid games, scored on action efficiency | Astra (Max) **62.7%** standard ($26K) vs Astra (High) **99.9%** with its provider's harness ($19K) ([3 Sep 2026](https://arcprize.org/blog/astra)); Kaggle public board 75.56 (read 30 Oct, via `ARC_SOTA.md`) | Astra "used fewer actions than the human baseline on 96.0% of levels" | the standard harness "leaves the model responsible for deciding what to preserve in its visible notes" | public games; verified and community boards; Kaggle closes 2 Nov | $5.8K–26.1K per frontier run | 0.51% (25 Mar 2026) → 62.7 / 99.9 (Sep 2026) | 2: memory management is the gap, but scaffolds close it |

**ARC-AGI-4.**
- **The only primary statement located.** An ARC Prize post on X says "ARC-AGI-4 will be a benchmark for autonomous open-ended innovation" ([post](https://x.com/arcprize/status/2098849962754978152)). X returned HTTP 402, so the text comes from the search result. I dated it 12 Sep 2026 from the post's ID.
- **Hiring.** The Apr 2026 hiring post lists "Own ARC-AGI-4" and "Lay the foundations for ARC-AGI-5" ([7 Apr 2026](https://x.com/arcprize/status/2041626929380626530)).
- **Continual learning.** A secondhand post (Psyho, [13 Sep 2026](https://x.com/FakePsyho/status/2099086728963207537)) quotes an earlier plan: ARC-4 would be "more focused on continual learning and curriculum learning at longer timescales". The same post says that idea was scrapped.
- **Release date.** "Early 2027" appears only in an AI-generated blog. Not verified.
- **What the Astra post says comes next:** "how to evaluate recursive self-improvement and open-ended innovation" ([3 Sep 2026](https://arcprize.org/blog/astra)).
- **INTERPRETATION.** The claim that ARC-AGI-4 will test continual learning, early 2027, has no primary source. The organisers' current wording is open-ended innovation.

---

## 2. Why frontier models fail, per family

**Interactive environments: memory and spatial state are named, but so are perception, latency and knowledge.**
- **BALROG.** "models execute undesirable actions during gameplay despite knowledge of their negative consequences"
  ([§4.1](https://arxiv.org/html/2411.13543v2)). The paper fixes a short memory: "we use a history length of 16
  observations" (§3.2).
- **VideoGameBench.** The model "overwrites its textual scratchpad memory after reaching a new zone, deleting
  information on where its been before". Separately: "A huge bottleneck in playing games with VLMs is the high
  inference time" ([paper](https://arxiv.org/html/2505.18134v3); [site](https://www.vgbench.com)). This is mainly
  latency and perception.
- **AI GameStore.** Models "especially struggled with games that challenge world-model learning, memory and planning"
  ([abstract](https://arxiv.org/abs/2602.17594)).
- **TextQuests.** "current models often hallucinate about prior interactions, such as believing they have already
  picked up an item" ([2507.23701](https://arxiv.org/abs/2507.23701)).
- **PokeAgent.** "Long-context autonomous embodied tasks appear to demand qualitatively different architectures"
  ([§5.2](https://arxiv.org/html/2603.15563)).
- **FLE.** "Agents also struggle to maintain consistent mental models of the factory layout"
  ([v0.3](https://jackhopkins.github.io/factorio-learning-environment/versions/0.3.0.html)).
- **A 2026 NetHack harness.** "By far the biggest roadblock was also the least surprising: spatial awareness"
  ([30 Jan 2026](https://kenforthewin.github.io/blog/posts/nethack-agent)).
- **Closed by scaffolds, so not worth fighting:**
  - lmgame-Bench: "40% of game runs without the harness fail to outperform a random-play baseline"
    ([2505.15146](https://arxiv.org/html/2505.15146v2)).
  - Finishing a Pokémon game: done with harnesses.
  - ARC-AGI-3: the same unnamed base model scores 7.8% playing directly, 61.1% with an off-the-shelf harness and 93.3%
    when it writes and tests an executable world model ([Twin, 14 Aug 2026](https://arxiv.org/abs/2608.14490)).

**Agent memory: the authors blame state, not length, and generic memory products don't help.**
- **AMA-Bench.** "compression tuned for redundant natural language fails to preserve dense state and causal information
  in agent memory" ([AMA-Bench](https://arxiv.org/html/2602.22769v2)).
- **StateMemBench.** "The obstacle is not _retrieving_ the fact, but rather _tracking_ its relevance to current state"
  ([StateMemBench](https://arxiv.org/abs/2608.19652)).
- **DynamicMem.** "In more than 93% of failures, the bottleneck is what the memory system could deliver, not what the
  answer model did with it" ([DynamicMem](https://arxiv.org/html/2606.22877v1)).
- **MEMTRACK.** "Memory components such as Mem0 and Zep provide limited gains"
  ([MEMTRACK](https://arxiv.org/html/2510.01353)).
- **Closed by context or scaffolds, so not worth fighting:**
  - LongMemEval-S: vendors report 94–96, independent re-runs 86.5.
  - LoCoMo: its grading model accepts 62.81% of deliberately wrong answers.
  - Fiction.liveBench: 100 at 192K.
  - BEAM: rose from 0.27 to 0.68 in 9 months.

**Puzzles: the low scores are knowledge, and the state-limited ones are closed by a checker or a solver.**
- **EnigmaEval.** "some frontier models are still constrained by OCR and parsing ability"
  ([2502.08859](https://arxiv.org/html/2502.08859v2)).
- **PuzzleWorld.** "53.33% of these bottleneck steps involved spatial reasoning or sketching-related capabilities"
  ([v2](https://arxiv.org/html/2506.06211v2)). That is a persistent-sketch failure, but answers also need wordplay.
- **Sudoku-Bench.** Models "frequently fail at maintaining global consistency over long reasoning chains"
  ([Sakana](https://pub.sakana.ai/sudoku-gpt5/)). An LLM that writes an Answer Set Programming encoding goes from 10.3%
  to 74.7% ([Apr 2026](https://arxiv.org/html/2604.27960)).
- **Long-Horizon Execution.** "We posit that the eventual failures are in execution"
  ([v3](https://arxiv.org/html/2509.09677v3)).
- **Closed by scaffolds, so not worth fighting:**
  - MAKER: "the first system that successfully solves a task with over one million LLM steps with zero errors"
    ([12 Nov 2025](https://arxiv.org/abs/2511.09030)).
  - Pencil Puzzle Bench: 97.6% with the checker.

**Long-horizon work: mostly skill and knowledge; state appears only in the newest suites.**
- **OSWorld 2.0.** Agents "lose track of constraints, miss information that arrives mid-task", worst "when a task
  hinges on hidden state they must recover" ([2606.29537](https://arxiv.org/abs/2606.29537)).
- **Agents' Last Exam.** "the dominant bottleneck is domain knowledge rather than execution capability"
  ([2606.05405](https://arxiv.org/abs/2606.05405)).
- **Vending-Bench (2025).** "We find no clear correlation between failures and the point at which the model's context
  window becomes full" ([2502.15840](https://arxiv.org/abs/2502.15840)).
- **Closed or saturated, so not worth fighting:**
  - OSWorld-Verified (above the human baseline).
  - BrowseComp (above humans).
  - τ² (87.9%).
  - MLE-bench: its scaffold dominates. With the same Gemini-2.5-Pro, one scaffold scores 59.56 and another 44.0.

---

## 3. Who is winning and how (the lowest frontier scores)

| Benchmark (frontier best) | Best known approaches | Score | Compute | Code |
|---|---|---|---|---|
| VideoGameBench (0.48% / 1.6%, May 2025) | only a ReAct loop plus a scratchpad tested; nearest analogue is Pokémon reinforcement learning: a policy under 10M parameters beat Pokémon Red ([Feb 2025](https://drubinstein.github.io/pokerl/)) | — | not stated | RL code [open](https://github.com/drubinstein/pokemonred_puffer) |
| Agents' Last Exam, hardest tier (~0%) | frontier models in their vendors' harnesses; Opus 5.5 + Claude Code 38.16% overall (AGG, 19 Oct 2026); swapping the harness moves scores 4.9–7.2 pp, swapping the model 16.8 pp | ~0% top tier | $3–10 per task | harness open |
| AI GameStore (8.5% of human) | only frontier VLMs prompted directly; no specialist agents reported | 8.5% | not located | MIT |
| BALROG-NetHack (13.2%, SR) | **Symbolic:** AutoAscend won NeurIPS 2021; median in-game score 4,918; "In over half a million evaluation games, no agent managed to ascend" ([report](https://nethackchallenge.com/report.html)) | 4,918 | — | open |
| | **Imitation plus RL:** HiHack ([2023](https://ar5iv.labs.arxiv.org/html/2305.19240)) | median 972 | 48 h on one GPU per seed | open |
| | **LLM plus code harness** ([Jan 2026](https://kenforthewin.github.io/blog/posts/nethack-agent)) | GPT-5.2 average 2.56%, maximum 12.56% over 37 runs | API | blog |
| | **Small model plus learned file memory:** AutoMem, Qwen2.5-32B + LoRA ([1 Jul 2026](https://arxiv.org/html/2607.01224)) | **1.85 ± 0.44**, up from 0.00 | LoRA on 2 GPUs | [released](https://github.com/autoLearnMem/AutoMem) |
| PuzzleWorld (18%) | fine-tuning InternVL3-8B on reasoning traces | final answers 0.76% (unchanged), stepwise 11.00% | not stated | open |
| Memory-update suites (MINTEval 33.4; StateMemBench 0.363; AgentLongBench knowledge-free ~0) | systems that **write and overwrite an explicit state**: MemAgent, a 14B model RL-trained to overwrite a fixed-length memory ([2507.02259](https://arxiv.org/abs/2507.02259)); StateMem, which tracks superseded facts and adds 32–67 points | 33.4; 0.363 | MemAgent training compute not located | MemAgent [open](https://github.com/ngaut/MemAgent) |

INTERPRETATION.
- Where scores are lowest and the authors blame memory, the winners keep an explicit, overwritten state: AutoMem's
  position-keyed map, MemAgent's fixed memory, StateMem's supersession tracking. That is our mechanism, so each is
  prior art to cite as well as a signal.
- On NetHack, frontier LLMs and AutoMem are scored on BALROG's progression metric, while AutoAscend and HiHack are
  scored on in-game score. The two metrics are not comparable.

---

## 4. Shortlist of three (INTERPRETATION)

**Assumptions check (what Neo did not ask for).**
- **A benchmark-specific LoRA is acceptable.** This breaks condition 1, no per-skill adapters
  (`NEO_CONDITIONS.md`).
- **An external canvas loop counts as "the model".** This breaks condition 2 ("The LLM itself computes") unless the
  canvas becomes native.
- **Matching frontier models at a hundredth of the size counts as a win.** Beating them outright is not assumed.
- **The field.** This problem belongs to memory for agents in partially observable environments (POMDPs). Its standard
  solutions are recurrent policies, external memory, map-building, and LLM scratchpads or file memories.
- **Alternatives at the level of the constraint:**
  - (i) Accept a per-benchmark adapter on a game benchmark. This breaks condition 1 and buys the fastest result.
  - (ii) Use a clean state benchmark with no frontier numbers (MINTEval, StateMemBench) and run the frontier baselines
    ourselves. This keeps all conditions but loses (e), legibility.
  - (iii) Enter ARC-AGI-3's community board. This is legible, but scaffolds already reach 93–100%.

### 1. BALROG-NetHack, with MiniHack and Crafter run in the same harness
- **Number to beat.**
  - Best entry: 13.2 ± 2.7 (GPT-6-Astra-Max, 2026-09-18, SR).
  - Best reproduced: 6.8 ± 3.2 (Gemini-3-Pro, 2026-02-03).
  - Same-protocol prior art: AutoMem 1.85 ± 0.44 (32B).
  - Small-model floor: Qwen2.5-7B 0.0 ([board](https://balrogai.com), read 30 Oct).
- **Human number.** No BALROG-progress score for humans was located. The progression metric itself is "the highest
  progression achieved between the dungeon level and experience level attained", derived from human games
  ([App. F](https://arxiv.org/html/2411.13543v2)).
- **Cheapest honest protocol.**
  - Official BALROG code, language mode (text plus ASCII map).
  - Keep the default history of 16 observations and add the canvas as the only extra memory.
  - Run 10 seeds (AutoMem's count; the paper uses 5) and report mean ± standard error.
  - Run MiniHack first (top 65.0) as a pilot.
  - Submit as an open entry and request the ✔ reproduction.
  - API cost $0 on a local GPU; step caps per episode not located.
- **Likely failure mode.** The canvas fixes "where have I been". But NetHack progress is gated by survival tactics and
  item and monster knowledge (the knowing-doing gap), where a 4B policy is weak. AutoMem found the bottleneck moved to
  "the model's parametric ability to navigate its memory".
- **Three questions before committing.**
  1. What share of frontier NetHack failures are map or state errors, as opposed to tactical deaths? Does the ASCII map
     already show the whole current level?
  2. Will BALROG reproduce (✔) an entry that brings its own learned memory module?
  3. Does a one-week MiniHack pilot lift a ≤4B model above Qwen2.5-72B's 5.0?

### 2. AMA-Bench, focusing on state updating and state abstraction plus the synthetic BabyAI/TextWorld subset
- **Number to beat.**
  - GPT-5.2: 0.7226 overall, 0.6563 on state updating, 0.6037 on state abstraction
    ([Table 4](https://arxiv.org/html/2602.22769v2), 4 Mar 2026).
  - Best scaffold on Qwen3-32B: ≈0.70 ("starhop", 9 Sep 2026). That figure was computed from the leaderboard file and
    is not published.
  - Qwen3-8B with long context: 0.4109.
- **Human number.** Not located.
- **Cheapest honest protocol.**
  - Released code and data: 2,496 real questions over 208 trajectories, plus 1,200 synthetic questions (240 at each of
    5 lengths, 8K–128K).
  - Use the paper's Qwen3-32B judge.
  - Build one canvas per trajectory and answer every question from it, which is 208 trajectory passes rather than 2,496.
  - Local GPU only.
- **Likely failure mode.** Real trajectories (web, SQL, software) carry state in natural language, not on a grid, so
  the canvas needs a learned policy for what to write. Judge noise blurs small gains. And 0.72 is not "low": a win
  reads as "4B plus exact memory matches GPT-5.2".
- **Three questions before committing.**
  1. Is the synthetic subset scored by rule or by the judge? Its per-length numbers appear only in a figure.
  2. Does the agent board accept a backbone other than Qwen3-32B?
  3. What do 2026 models score? The board stops at GPT-5.2.

### 3. AI GameStore
- **Number to beat.** GPT-5.2 at 8.5% of the human median (geometric mean, from a
  [summary](https://www.emergentmind.com/papers/2602.17594) of the 19 Feb 2026 paper). The abstract says best models
  scored "less than 10% of the human average score on the majority of the games".
- **Human number.** 106 online participants, 120 s per game (per the sub-agent's reading of the paper; not in the
  abstract).
- **Cheapest honest protocol.**
  - Develop on the 10 public games.
  - Score the 90 private games through [aigamestore.org](https://aigamestore.org)'s "Test Model" page.
  - The authors ask that nobody train on the games ([README](https://github.com/lance-ying/aigamestore)); this is a
    request, not a license condition.
  - Cost not located.
- **Likely failure mode.** Perception and control across 100 different visual games outweigh memory. A canvas layout
  designed per game would break generality.
- **Three questions before committing.**
  1. Is the game paused while the model acts?
  2. How are self-hosted models scored, and is the board maintained? It showed "Loading" on 30 Oct.
  3. What do 2026 frontier models score? There is only one data point.

**Why this order.**
- **NetHack** alone meets all five criteria:
  - a low frontier score;
  - a memory-shaped failure;
  - an open, reproducing leaderboard with Sep 2026 entries for GPT-6, Opus 5 and GPT-5.6 (who submitted them is not
    stated);
  - a local evaluation that costs $0;
  - a same-protocol small-model comparator (AutoMem).
  Its risks are that the frontier score is rising fast and that game knowledge matters.
- **AMA-Bench** fits criteria (b)–(d) best and is cheapest, but is weakest on (a).
- **AI GameStore** is strongest on (a) and (e), but weakest on (c) and (d).

**Not shortlisted.**
- ARC-AGI-3: scaffolds close it, and Kaggle ends 2 Nov.
- OSWorld 2.0: dominated by GUI perception, and $25–72 per task.
- Vending-Bench 2: closed evaluation.
- VideoGameBench: dominated by latency and perception.
- TextQuests: Infocom puzzle knowledge; submissions by email.
- MINTEval and StateMemBench: no frontier numbers, but cheap "unit tests" for the canvas.
- Pencil Puzzle Bench and LongReasonArena: saturated, or trivial with a checker or with code.

---

## 5. Glossary (plain words)

**Benchmarks.** What each measures is in its table row in section 1; these are only the ones that need more.
- **BALROG** (2024): six games in one harness. **NetHack / NLE**: a 1987 dungeon game and its RL interface; winning is
  called "ascending". **MiniHack**: small NetHack levels. **Crafter**: a 2D survival game. **Baba Is AI**: a
  rule-rewriting puzzle game.
- **VideoGameBench Lite**: pauses the game while the model thinks.
- **FLE lab-play / open-play**: fixed production targets / "build the biggest factory".
- **PokeAgent**: the NeurIPS 2025 Pokémon competition.
- **MineDojo / MCU**: Minecraft task suites.
- **Memoria-Bench**: an ICML 2026 memory benchmark; details not located.
- **MRCR**: find the i-th of several identical requests in a long chat.
- **METR time horizon**: the human task length an agent finishes 50% (or 80%) of the time.
- **PaperBench Code-Dev**: a variant that grades code only, without running it.
- **ARC-AGI-3**: grid games scored by actions used relative to humans. **ARC-AGI-4**: the next one; its organisers say
  "open-ended innovation".

**Methods and terms**
- **Progression metric** (BALROG): the deepest dungeon or experience level reached, mapped to human win odds.
- **Knowing-doing gap**: the model can state the right move but does another.
- **Harness / scaffold**: the code around a model (memory, tools, loops).
- **Standard vs provider harness**: ARC's notes-only interface vs the vendor's own context management.
- **Compaction**: shortening old context to fit.
- **ReAct**: alternate written reasoning and actions.
- **AutoAscend**: the hand-written NetHack bot that won in 2021.
- **HiHack**: a neural NetHack agent trained from AutoAscend's games.
- **Behaviour cloning**: imitate recorded play.
- **APPO**: an RL algorithm.
- **LSTM**: a recurrent network.
- **AutoMem**: learned file-system memory for a 32B agent.
- **MemAgent**: an RL-trained model that overwrites a fixed memory.
- **StateMem**: memory that tracks which facts are superseded.
- **Supersession**: a newer value replacing an older one.
- **Mem0, Zep**: commercial memory layers.
- **RAG**: retrieve text, then answer.
- **LLM judge**: a model grades answers, adding noise.
- **pass@k / pass^k**: any of k tries succeeds / all k tries succeed.
- **ASP**: Answer Set Programming, a logic solver language.
- **MAKER**: splits a task into tiny steps and votes on each.
- **TRM**: a tiny recursive network.
- **Twin**: writes a game simulator and repairs it from mismatches.
- **World model**: a predictive model of how an environment responds.
- **POMDP**: a decision problem where the agent sees only part of the state.
- **Elo, TrueSkill, GXE**: skill ratings.
- **Mineflayer, MCP**: a Minecraft code API; a standard tool protocol.
- **Geometric-mean human-normalised score**: per-game AI/human ratios, averaged multiplicatively.
- **SR / VR / AGG**: self-reported / vendor-reported / aggregator.
- **LoRA**: small trainable add-on matrices.
- **VLM**: a language model that reads images.

---

## What I could not verify

- **Numbers I could not confirm on the source page.**
  - The ARC Prize ARC-AGI-4 post: X returned 402, so its text and date come from search snippets and the post ID.
  - Any official ARC-AGI-4 date or format.
- **Self-reported or vendor-reported numbers.**
  - BALROG's 2026 top rows (unchecked).
  - OSWorld 2.0's 41.7%.
  - LongMemEval and LoCoMo scores above 90.
  - BEAM.
  - FrontierMath-T4 97.6% (OpenAI via press; not on epoch.ai).
  - BrowseComp 92.2% and ZebraLogic 98.8% (aggregators).
- **Leaderboards that did not render:** AI GameStore, TextQuests, TextArena, Kaggle Game Arena, FLE, TheAgentCompany,
  OSWorld-Verified, tbench.ai, FrontierMath.
- **AMA-Bench.** The ≈0.70 scaffold score is computed from the leaderboard file, not published. The meaning of the
  README's "judge accuracy" table is unclear. The synthetic subset's per-length numbers and scoring rule are unknown.
- **AI GameStore.** The 8.5% figure comes from a summary site, not the arXiv HTML, which returned 404. Whether the game
  pauses for the model, the human protocol details, and any 2026 model scores are all unknown.
- **NetHack.** Episode step caps and evaluation cost are unknown, as is whether the ASCII map shows the whole level.
  There is no human % on BALROG's metric, and AutoAscend's score on that metric was not located.
- **Not located at all:**
  - Memoria-Bench.
  - MEMTRACK's public data.
  - StateMem's code.
  - RE-Bench 2026 scores.
  - TextQuests 2026 scores.
  - METR horizons for GPT-6, Opus 5/5.5 or Gemini 4.
  - VideoGameBench entries after May 2025.
- **Unresolved conflicts:**
  - PuzzleWorld's best is 18% in one place and 14% in another.
  - FLE's lab-task count is 24, 8 or 33 depending on the source.
  - AI GameStore's headline is "<10% of the human average" in one place and "<30%" in another.
  - The OSWorld-Verified top is 86.1% or 90.19%.
- **Not verbatim-checked.** Every quote passed through a summarising fetch tool. The ones not confirmed verbatim are
  marked (paraphrase) in the sub-agent notes; I did not re-check each against raw HTML.
- **Glossary.** The brief allowed one file only, so `research/meta/GLOSSARY.md` was not updated; section 5 holds the
  new terms.
