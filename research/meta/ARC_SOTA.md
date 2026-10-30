# ARC-AGI: state of the art, and what the ideal model looks like (30 Oct 2026)

Read-only survey for Neo from live primary pages, 30 Oct 2026. Every number has a link and a date ("read 30 Oct" marks
an undated live page). Inferences are labelled INTERPRETATION; terms are defined in section 8.

**Headline.** The map changed in 2026. Frontier models score in the 90s on ARC-AGI-1 and -2 for $0.25–$1.12 per task;
offline Kaggle entries (12 h, no internet) show 88% on the public half of the hidden ARC-AGI-2 set. ARC-AGI-3, launched
in March 2026 with frontier AI below 1%, reached 99.9% in September (GPT-6 Astra in its provider's harness). The
organisers are now working out what the next benchmark should test.

---

## 1. Leaderboards now

### 1.1 Verified leaderboard

[arcprize.org/leaderboard](https://arcprize.org/leaderboard), read 30 Oct. Verified scores come from the **semi-private**
set, are priced at retail API rates, and are one run, not averaged ([testing policy](https://arcprize.org/policy), read
30 Oct). ARC-AGI-1 and ARC-AGI-2 are scored pass@2. The page does not say which models are open-weight.

| System | Date | ARC-AGI-2 | $/task | ARC-AGI-1 |
|---|---|---|---|---|
| GPT-6 Astra (Max), OpenAI | 2026-09-02 | **95.0%** | $1.12 | 97.5% |
| GPT-6.1 Sol (Max), OpenAI | 2026-09-29 | 94.2% | $0.254 | 96.5% |
| Claude Opus 5.5 (High), Anthropic | 2026-09-22 | 93.3% | $0.408 | 98.5% |
| Gemini 4 Argon (High), Google | 2026-10-13 | 91.3% | $0.325 | 98.5% |
| DeepSeek V4.1 Flash 1017 (Max) | 2026-10-17 | 78.1% | $0.163 | 93.5% |
| Gemini 3 Pro + Poetiq refinement | 2025-12-04 | 54.0% | $30.57 | n/a |
| Opus 4.5 (Thinking 64K) | 2025-11-24 | 37.6% | $2.40 | 80.0% |
| NVARC (Kaggle 2025 winner; page lists 2024-11-03) | 2025 | 27.6% | $0.20 | n/a |
| TRM, 7M parameters | 2025-10-07 | 6.3% | $2.10 | 40.0% |
| HRM, 27M parameters | 2025-08-07 | 2.0% | $1.68 | 32.0% |
| o3-preview (Low) | 2024-12-20 | 4.0% (footnoted estimate) | $200 | 75.7% |
| ARChitects (Kaggle 2024 winner) | 2024 | 2.5% | $0.20 | 56.0% |
| Icecuber (2020 DSL search) | 2020 | 1.6% | $0.13 | 17.0% |
| Human panel | — | 100% | $17 | 98.0% |

ARC-AGI-1 tops out at **98.5%**, shared by several 2026 models, against a human panel at 98.0%. In Dec 2024, o3-preview
scored 75.7% on the semi-private set at $26/task with 6 samples, and 87.5% at $4,560/task with 1,024 samples
([Chollet, 20 Dec 2024](https://arcprize.org/blog/oai-o3-pub-breakthrough)).

**ARC-AGI-3** (55 semi-private environments; costs are per run, not per task):

| System | Date | Standard harness | Provider Adapter harness |
|---|---|---|---|
| GPT-6 Astra (Max / High) | 2026-09-02 | **62.7%** ($26.1K) / 54.8% | 98.6% ($17.3K) / **99.9%** ($18.8K) |
| Gemini 4 Argon (Low) | 2026-10-13 | 49.8% ($5.8K) | 97.5% ($4.8K) |
| GPT-6.1 Sol (Max) | 2026-09-29 | 52.7% ($7.6K) | 96.2% ($3.8K) |
| Claude Sonnet 5.5 (XHigh) | 2026-09-28 | 24.3% ($7.4K) | 72.4% ($8.2K) |
| Claude Opus 5 (High) | 2026-07-24 | 30.2% ($20.7K) | n/a |
| Frontier AI at launch | 2026-03-25 | 0.51% | n/a |

Sources: [leaderboard](https://arcprize.org/leaderboard), read 30 Oct; [Astra, 3 Sep 2026](https://arcprize.org/blog/astra)
(semi-private split; Astra "used fewer actions than the human baseline on 96.0% of levels");
[launch, 25 Mar 2026](https://arcprize.org/blog/arc-agi-3-launch). Standard harness: "a minimal, provider-neutral
interface", the model keeps only notes it chooses; Provider Adapter: "provider-designed context-management features"
([policy](https://arcprize.org/policy)).

### 1.2 Community leaderboard (self-reported unless semi-private)

[arcprize.org/leaderboard/community](https://arcprize.org/leaderboard/community), read 30 Oct. Costs are per run.

| System | Split | Score | Cost | Date |
|---|---|---|---|---|
| Tycho: LLM plus a "falsification-tested executable world model" | ARC-AGI-3 public demo | 100.0% | $2,986 | 2026-07-29 |
| Retrodict: hypotheses must "retrodict recorded history" | ARC-AGI-3 public demo | 99.9% | $654 | 2026-07-19 |
| baseline1: coding agent "builds and verifies an executable Python world model" | ARC-AGI-3 public demo | 99.0% | $400 | 2026-07-15 |
| Berman: evolved English instructions | ARC-AGI-2 semi-private | 29.4% | $3,648 | 2025-09-16 |
| Pang: evolved Python program library | ARC-AGI-2 semi-private | 26.0% | $476 | 2025-09-01 |

### 1.3 Kaggle (offline, open-source)

| Year, benchmark | Top scores | Split | Source |
|---|---|---|---|
| 2020, ARC-AGI-1 | ≈20%, Icecuber | private | [ARC-AGI-3 report §1.2, 22 Apr 2026](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf) |
| 2024, ARC-AGI-1 | 53.5% ARChitects; 55.5% MindsAI (ineligible, closed) | private | [2024 report, v2 8 Jan 2025](https://arxiv.org/html/2412.04604v2) |
| 2025, ARC-AGI-2 | 24.03% NVARC; 16.53% ARChitects; 12.64% MindsAI | private | [2025 results, 5 Dec 2025](https://arcprize.org/blog/arc-prize-2025-results-analysis) |
| 2026, ARC-AGI-2 | 88.06 Tufa Labs; 87.22 Yi-Chia Chen @ Fields Model; 83.89 nvbanana | public board, ~50% of hidden data | [Kaggle](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-2/leaderboard), read 30 Oct |
| 2026, ARC-AGI-3 | 75.56 Yi-Chia Chen @ Fields Model; 70.02 Tufa Labs; 49.54 NVARC3; 41.03 ARChitects | public board, ~50% | [Kaggle](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/leaderboard), read 30 Oct |

The 2026 boards are provisional: "The final results will be based on the other 50%". Submissions close 2 Nov 2026 and
results come out 4 Dec ([ARC Prize 2026](https://arcprize.org/competitions/2026)).

### 1.4 Rules and formats

**ARC Prize 2025** ([24 Mar 2025](https://arcprize.org/blog/announcing-arc-agi-2-and-arc-prize-2025)): about "$50
worth" of L4x4 compute per submission, internet off; 85% grand prize, unclaimed; 1,000 training tasks and 120 each in
public eval, semi-private and private.

**ARC Prize 2026** ([overview](https://arcprize.org/competitions/2026)):
- $2M across three tracks.
- Code must be released under CC0 or MIT-0 before private scores are returned.
- "no API-based systems like GPT/Claude/etc."
- **ARC-AGI-2 track:** $700K; notebooks of 12 h or less on L4x4 (96 GB GPU memory); public pre-trained models allowed;
  a $150K bonus for 85% or more on the private set
  ([Kaggle](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-2/overview)).
- **ARC-AGI-3 track:** $850K, of which $700K goes to "the first eligible agent that scores 100%"
  ([track page](https://arcprize.org/competitions/2026/arc-agi-3)); 9 h or less on RTX 6000; per-game scores "capped at
  100%" ([Kaggle](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview)).

**ARC-AGI-3 format** ([technical report, 22 Apr 2026](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)):
turn-based games on a 64×64 grid of 16 colours; actions are five keys, Undo and clicking a cell; at least six levels per
game; 25 public-demo, 55 semi-private and 55 private environments. The agent is "never told the objective nor provided
instructions"; its internal reasoning is "not counted as actions".

**RHAE scoring** (§4.1): per level min(1.15, (human actions ÷ AI actions)²); per game a level-weighted average capped
by levels completed; overall the mean over games. The human baseline moved "from 2nd-best player to median player per
level", from 458 tested people ([14 Apr 2026](https://arcprize.org/blog/arc-agi-3-human-dataset)).

"Learning by exploration" here means finding out what actions do and what winning looks like by acting, while being
charged for every action: the metric "penalizes brute-forcing" (report §2.2).

---

## 2. The idea families, each with its best representative and its ceiling

| Family | Best representative | Best ARC-AGI-2 | Cost | Ceiling, Oct 2026 |
|---|---|---|---|---|
| (a) Hand-written DSL search | Icecuber 2020 | 1.6% semi-private | $0.13/task | ARC-AGI-2 was built to resist it |
| (b) LLM-sampled or evolved programs | Poetiq on Gemini 3 Pro | 54.0% semi-private (verified) | $30.57/task | bounded by the base model |
| (c) Test-time training of small LMs | NVARC (Qwen3 4B) | 24.03% private (2025) | $0.20/task | about a quarter of the set (2025) |
| (d) Small looped models from scratch | TRM (verified); URM, LoopViT (self-reported) | 6.3% semi-private; 14–16% public | $2.10/task | about 10–16%, mostly self-reported |
| (e) Frontier models, heavy test-time compute | GPT-6 Astra | 95.0% semi-private | $1.12/task | ARC-AGI-1 and -2 saturated |
| Unknown: 2026 Kaggle leaders | Tufa Labs; Yi-Chia Chen @ Fields Model | 88.06 / 87.22, public board | Kaggle limits | methods unpublished |
| (f) 2026 hybrids: LLM plus executable world model | Tycho, Retrodict, baseline1 | — (ARC-AGI-3: 99–100% public demo) | $400–$3,000 per run | the ARC-AGI-3 pattern |

### (a) Hand-written DSL search

**What it does.** Enumerate compositions of hand-written grid functions, keep the first one that reproduces every demo
pair, and apply it to the test input. Icecuber searched compositions of "142 handcrafted unary functions on grids"
([Bober-Irizar & Banerjee, 5 Feb 2024](https://arxiv.org/html/2402.03507)), to depth 2 by default and 3 optionally
([README](https://github.com/top-quarks/ARC-solution)).

**Results.** All 2020 entries ensembled: 49% on ARC-AGI-1 ([2024 report](https://arxiv.org/html/2412.04604v2)).
ARC-AGI-2 was built to "minimize susceptibility to naive or computationally intensive brute-force program search"
([v2 15 Jan 2026](https://arxiv.org/html/2505.11831)).

**What it cannot do.** It cannot express anything outside the DSL, and deep compositions explode. Icecuber, quoted on a
secondary page: "functions taking more than 1 argument were growing my search space super-exponentially"
([ironbar summary](https://ironbar.github.io/arc24/03_State_of_the_art); the primary write-up would not render).

### (b) LLM-sampled program synthesis and refinement

**What it does.** An LLM writes candidate programs, in Python or in plain-English instructions. Each candidate is run on
the demos, the best are revised, and the survivors vote.

| System | Date | How it works | Result | Cost |
|---|---|---|---|---|
| [Greenblatt](https://blog.redwoodresearch.org/p/getting-50-sota-on-arc-agi-with-gpt), GPT-4o | 17 Jun 2024 | about 8,000 programs per task | 43.0% ARC-AGI-1 semi-private | $40,000 per run |
| [CodeIt](https://arxiv.org/abs/2402.04858) | 2024 | 220M model, Hodel's DSL, hindsight relabelling | 15% of ARC-AGI-1 eval | — |
| [Berman](https://jeremyberman.substack.com/p/how-i-got-a-record-536-on-arc-agi) | 6 Dec 2024 | up to 500 Python programs per task | 53.6% ARC-AGI-1 semi-private | — |
| [Berman](https://jeremyberman.substack.com/p/how-i-got-the-highest-score-on-arc-agi-again) | 16 Sep 2025 | evolved English instructions on Grok 4 | 29.4% ARC-AGI-2 semi-private | $30.40/task |
| [Pang](https://ctpang.substack.com/p/arc-agi-2-sota-efficient-evolutionary) | Sep 2025 | evolving library of Python programs | 26.0% ARC-AGI-2 semi-private | $3.97/task |
| [SOAR](https://arxiv.org/html/2507.14172v2) | ICML 2025 | 6,000 attempts per task per iteration; fine-tunes on its own search traces | 52% ARC-AGI-1 public eval | — |
| [Poetiq](https://arcprize.org/blog/arc-prize-2025-results-analysis), Gemini 3 Pro | Nov–Dec 2025 | refinement harness; base model alone scored 31% at $0.81 | **54.0% ARC-AGI-2 semi-private, verified** | $30.57/task |
| [Imbue](https://imbue.com/blog/2026-02-27-arc-agi-2-evolution), Gemini 3.1 Pro | 27 Feb 2026 | code evolution | 88.1% → 95.1% ARC-AGI-2 public eval, self-reported | $8.71/task |

Per-task costs are from the leaderboards; Greenblatt's is per run (about $400 per task, my arithmetic).

Public-eval scores run high: Gemini 3.1 Pro is 88.1% there but 77.1% semi-private ([leaderboard](https://arcprize.org/leaderboard)).

**What it cannot do.** It can only find what the base model can propose: performance "remains fundamentally constrained
to knowledge coverage" ([2025 report, 15 Jan 2026](https://arxiv.org/abs/2601.10904)). Failure modes the authors report:
- "GPT-4o's vision is terrible on grids" (Greenblatt).
- Models "confidently claim an object is symmetrical when it obviously isn't" (Berman 2025).
- "ARC-AGI tasks are heavily under-constrained" (Imbue).

### (c) Test-time training of small language models

**What it does.** Pre-train a small LM on ARC and synthetic grids. At test time, fine-tune it on each task's augmented
demos, score candidate outputs across augmentations, and write the grid directly, with no program.

**Representatives:**
- **ARChitects 2024** (NeMo-Minitron-8B): 53.5% private on ARC-AGI-1. Their follow-up, Product of Experts, scored 71.6%
  on ARC-AGI-1 public eval at about $0.02/task ([May 2025](https://arxiv.org/abs/2505.07859)).
- **Akyürek et al.:** an 8B model with TTT scored 53.0% public and 61.9% when ensembled with program synthesis
  ([Nov 2024](https://arxiv.org/html/2411.07279v2)).
- **NVARC**, 1st in 2025: 103k synthetic puzzles plus 3.2M augmented ones from "staged puzzle generation" with
  open-weight models; an ARChitects-style TTT model on Qwen3 4B plus a TRM component; 24.03% private at $0.20/task
  ([NVIDIA blog, 5 Dec 2025](https://developer.nvidia.com/blog/?p=109968)).
- **ARChitects 2025:** an 8B masked-diffusion model, 16.53% private
  ([write-up](https://lambdalabsml.github.io/ARC2025_Solution_by_the_ARChitects/)).

**What it cannot do.** It needs heavy ARC-like pre-training and gives no explicit program. Chain-of-thought and agent
methods "couldn't fit within Kaggle's tight runtime" (NVIDIA blog). Quotes on its limits:
- "substantial pre-training on ARC riddles remains indispensable" (MindsAI, [Jun 2025](https://arxiv.org/html/2506.14276v2)).
- "Fine-tuning a model on ARC tasks is not enough to do well on the private test set"
  ([Barbadillo, 3 Nov 2025](https://ironbar.github.io/arc25/05_Solution_Summary)).

### (d) Small recurrent or looped models trained from scratch

**What it does.** A tiny network, looped, refines an answer; trained only on ARC with heavy augmentation. HRM, TRM and
Looped Flows learn a per-puzzle embedding, so evaluation demos are in training; VARC and LoopViT train per task at test
time.

| System | Date | Params | ARC-AGI-1 | ARC-AGI-2 | Source |
|---|---|---|---|---|---|
| HRM | Jun 2025 | 27M | 32% semi-private | 2% semi-private | [ARC Prize, 15 Aug 2025](https://arcprize.org/blog/hrm-analysis) |
| TRM (1st paper award 2025) | 6 Oct 2025 | 7M | 40.0% semi-private | 6.3% semi-private | [leaderboard](https://arcprize.org/leaderboard); [paper](https://arxiv.org/abs/2510.04871) |
| CompressARC (3rd paper award) | 2025 | ~76K, no pre-training | 20–34% | 4% | [2025 report](https://arxiv.org/html/2601.10904) |
| VARC (ViT, MIT) | 18 Nov 2025 | 18M (73M ensemble) | 54.5% (60.4%), public | 8.3% (11.1%) | [arXiv](https://arxiv.org/html/2511.14761) |
| URM | Dec 2025 | not reported | 53.8% pass@1, public | 16.0% pass@1 | [arXiv](https://arxiv.org/html/2512.14693) |
| LoopViT | 2 Feb 2026 | 3.8–18M | 65.8%, public | 14.2% | [arXiv](https://arxiv.org/html/2602.02156) |
| Looped Flows | 10 Sep 2026 | 5–7M | 58.8% | 12.2% | [arXiv](https://arxiv.org/abs/2609.11801) |
| BDH-CQ | — | — | not located | not located | — |

**What it cannot do.** It cannot handle tasks whose embedding was never trained: replacing the puzzle ID gives "zero
accuracy" ([Dec 2025](https://arxiv.org/abs/2512.11847)). Other reported limits:
- ARC Prize on HRM: "most of the performance comes from memorizing solutions to the specific tasks used at evaluation
  time". The outer refinement loop, not the hierarchy, drove the score.
- TRM's author: these are "supervised learning methods rather than generative models".

### (e) Frontier models with heavy test-time compute

Large reasoning models with long hidden reasoning, sometimes many samples. ARC-AGI-2 semi-private
([leaderboard](https://arcprize.org/leaderboard)):

| Model | Date | ARC-AGI-2 | $/task |
|---|---|---|---|
| o3-preview | Dec 2024 | 4.0% (estimate) | — |
| Opus 4.5 | Nov 2025 | 37.6% | $2.40 |
| Gemini 3 Deep Think | Feb 2026 | 84.6% | $13.62 |
| GPT-5.5 XHigh | Apr 2026 | 85.0% | $1.87 |
| GPT-6 Astra | Sep 2026 | 95.0% | $1.12 |

On ARC-AGI-3 the harness matters: Astra scores 62.7% with the minimal one, 99.9% with its provider's
([3 Sep 2026](https://arcprize.org/blog/astra)).

### (f) Hybrids and 2026 work that fits nowhere else

- **ARC-AGI-3 agents that write an executable world model and test it against what they observed:** Tycho, Retrodict,
  baseline1, and OPINE-World, which runs a CEGIS-style loop and scores 78.4%
  ([community board](https://arcprize.org/leaderboard/community)). Astra did the same in a sandbox, writing
  `maze_solver.py`, `patrol_solver.py`, and `sync_state.py` "to check its predictions against observations".
- **Small open models under Kaggle limits** ([Milestone 1, 6 Jul 2026](https://arcprize.org/blog/arc-prize-2026-milestone-1)):
  - Tufa Labs ran Qwen 3.6 27B locally, writing and running Python in a REPL; "hand-crafted tools actually hurt the model".
  - 2nd and 3rd place feed rendered frames to Gemma-4-31B, which returns one JSON action per step.

---

## 3. What the organisers say the ideal model looks like

**The definition.** Chollet defines intelligence as "skill-acquisition efficiency", "highlighting the concepts of scope,
generalization difficulty, priors, and experience" ([On the Measure of Intelligence, Nov 2019](https://arxiv.org/abs/1911.01547)).
The 2026 wording: AGI is "a system's ability to acquire any skill a human can, as efficiently as a human can"
([3 Sep 2026](https://arcprize.org/blog/astra)). Efficiency is counted in cost per task on ARC-AGI-1 and -2, in
actions on ARC-AGI-3.

**On o3, Dec 2024.** "o3's core mechanism appears to be natural language program search and execution within token
space". It "still fails on some very easy tasks". "Passing ARC-AGI does not equate to achieving AGI"
([20 Dec 2024](https://arcprize.org/blog/oai-o3-pub-breakthrough)).

**Why LLMs failed ARC-AGI-2** ([24 Mar 2025](https://arcprize.org/blog/announcing-arc-agi-2-and-arc-prize-2025)):
- **Symbolic interpretation:** systems "failed to assign semantic significance to the symbols themselves".
- **Compositional reasoning:** "application of multiple rules that interact with each other".
- **Contextual rule application:** "rules must be applied differently based on context". "Systems tend to fixate on
  superficial patterns rather than understanding the underlying selection principles."

**The 2025 lesson.** "The defining theme of 2025 is the emergence of the refinement loop -- a per-task iterative program
optimization loop guided by a feedback signal". The loop appears in evolutionary program synthesis, in commercial
harnesses, and in weight space, in "zero-pretraining deep learning methods" with "7M parameters"
([2025 report, 15 Jan 2026](https://arxiv.org/abs/2601.10904)). "From an information theory perspective, refinement is
intelligence" ([5 Dec 2025](https://arcprize.org/blog/arc-prize-2025-results-analysis)).

**Contamination.** Frontier reasoning "remains fundamentally constrained to knowledge coverage, giving rise to new forms
of benchmark contamination" (2025 report). The evidence: Gemini 3 Deep Think used ARC's colour mapping unprompted, which
"strongly suggests that ARC-AGI data is well represented in the underlying model". "We believe this has happened to
ARC-AGI-1 and ARC-AGI-2 with frontier LRMs" ([ARC-AGI-3 report §1.3.3](https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)).
"We still need new ideas, like how to separate knowledge and reasoning" (5 Dec 2025).

**What ARC-AGI-3 requires** (ARC-AGI-3 report §2.1–3.4):
- Exploration.
- Modelling: "turn raw observations into a generalizable world model".
- Goal-setting without instructions.
- Planning that corrects course.
- Constraints: core-knowledge priors only, no language or cultural symbols, and "Difficulty through composition".

Before Astra, the organisers found that models "fail to translate the effect into a global rule": "Opus had the wrong
compression, GPT-5.5 failed to compress". What is needed is "forming a working theory, testing it, updating it when the
evidence disagrees, and carrying forward what was learned"
([1 May 2026](https://arcprize.org/blog/arc-agi-3-gpt-5-5-opus-4-7-analysis)).

**After Astra.** Astra built "compact symbolic world models"; "Astra clears this bar", but the environments "have
deterministic, closed-ended mechanics and goals". Next the organisers are exploring "how to evaluate recursive self-improvement and
open-ended innovation" ([3 Sep 2026](https://arcprize.org/blog/astra)). An ARC-AGI-4 job listing appeared in Apr 2026
([secondary repost](https://dev.to/yuravolontir/arc-prize-foundation-yc-w26-is-hiring-a-platform-engineer-for-arc-agi-4-286i));
I found no announcement.

INTERPRETATION. The organisers' ideal builds a small, checkable model of a new situation from little experience, tests
it against what it has seen, and revises it, cheaply and without prior exposure to ARC-like data; they suspect high
static-set scores now partly reflect such exposure.

---

## 4. Program synthesis for ARC specifically

| DSL | Style | Size | Best result | Source |
|---|---|---|---|---|
| Icecuber | whole-grid transforms, brute force | 142 functions, depth 2–3 | 20% private (2020); README "129 / 419" public eval | see 2(a) |
| Hodel arc-dsl + RE-ARC | grid, object and patch primitives | "only few primitives" | hand-written solvers and generators for the 400 training tasks | [arc-dsl](https://github.com/michaelhodel/arc-dsl); [RE-ARC, 10 Apr 2024](https://arxiv.org/html/2404.07353) |
| ARGA | object graph | "4 base filters and 11 transformations" | 57 of 160 object-centric tasks vs the Kaggle winner's 64 | [Dec 2022](https://ar5iv.labs.arxiv.org/html/2210.09880) |
| Ferré MDL / MADIL | object-centric, picks the shortest description | no conditionals or recursion | 7% at ARC Prize 2024; 59 public-eval tasks vs Icecuber's 117 | [2023](https://arxiv.org/abs/2311.00545); [2 May 2025](https://arxiv.org/html/2505.01081v1) |
| PeARL + DreamCoder | library learning | "77 unique primitives" | 70 train / 18 eval tasks; 57% / 40% in an ensemble | [5 Feb 2024](https://arxiv.org/html/2402.03507) |
| BARC (Li et al.) | Python + LLM-written generators | 160 seed programs → 400k tasks | induction 38.0%, transduction 43.0%, both 56.75% (ARC-AGI-1 eval) | [v4 2 Dec 2024](https://arxiv.org/html/2411.02272v4) |
| Neuro-symbolic "Unit Patterns" | object DSL + LLM | 22 patterns | ARC-AGI-2 public: 16% → 24.4% (30.8% with a meta-classifier) | [2 Apr 2026](https://arxiv.org/html/2604.02434v1) |
| Cellular / local-rule DSL | — | — | not located | — |

**Verification.** Every system checks candidates the same way: the program must reproduce every demo output exactly.
Survivors vote. Measured false positives, meaning programs that pass every demo but fail the test:
- BARC: "about 9% of samples that fit the training examples".
- DreamCoder: 1.25%.
- MADIL: 12 of 69 demo-consistent models fail.
- SOAR: its vote falls 9.5% short of an oracle that picks a correct candidate when one exists.

**Program length.** For RE-ARC, "The median generator consists of 40 lines of code and uses 22 DSL primitive calls" and
"The median verifier program consists of 18 DSL primitive calls" (ARC-AGI-1 training tasks). For ARC-AGI-2: not located.

**What fraction of ARC-AGI-2 is a short local or object-level program?** Not located; nobody has measured it. The
closest evidence points the other way:
- The ARC-AGI-2 paper notes "nearly half of the ARC-AGI-1 Private Evaluation tasks might be vulnerable" to brute-force
  search, and ARC-AGI-2 was designed against that.
- BARC's induction model "only solves 0.8% of the ARC-AGI-2 evaluation tasks"
  ([Barbadillo, 3 Nov 2025](https://ironbar.github.io/arc25/05_Solution_Summary)).
- Berman found ARC-AGI-2 rules "too complex to express elegantly in Python" and switched to English programs.

**Induction vs transduction.** "most problems solved by induction are not solved by transduction, and vice versa".
Problems involving "counting are best solved with symbolic code", while "transduction better handles perceptual
processes" (Li et al.).

---

## 5. Where a canvas executor could fit (as questions)

**Q1. Where do systems lose: synthesis, execution, perception, verification or budget?**
- **Search.** Not in the search space, not found, or found but not generalising
  ([Bober-Irizar & Banerjee 2024](https://arxiv.org/html/2402.03507)).
- **Generation vs selection.** On 130 ARC-AGI-2 public instances, 21 failures had no correct candidate and 17 had one
  but did not pick it ([Land, 30 Jun 2026](https://arxiv.org/html/2606.31543)).
- **Perception.** "approximately 80 percent of model failures stem from perception errors", pooled over Mini-ARC and two
  other benchmarks ([Wang et al., Jan 2026](https://arxiv.org/abs/2512.21329)). An object representation gave GPT-4
  "nearly doubling the performance" ([Xu et al., 2024](https://arxiv.org/abs/2305.18354)).
- **Execution errors** as a separate category in an ARC-AGI-2 breakdown: not located.

**Q2. Do LLMs mis-execute rules they got right?** Yes, and it has been measured. On 480 ConceptARC tasks, how often each
model stated the intended rule but produced a wrong grid ([Beger, Mitchell et al., v4 2 Feb 2026](https://arxiv.org/html/2510.02125v4),
Table 7):

| Model | Text input | Image input |
|---|---|---|
| o3 | 2.3% | 19.6% |
| Gemini 2.5 Pro | 2.3% | 19.0% |
| Claude Sonnet 4 | 13.3% | 10.4% |

The reverse also happens: o3 on text got 15.8% of grids right from an unintended rule, so "accuracy alone ... can
substantially overestimate AI capabilities in textual modalities".

Older results agree:
- When GPT-4V's own rules were applied on MiniARC, a symbolic interpreter scored 8.5 task accuracy and GPT-4V as the
  interpreter scored 0.8, a "consistent performance drop when using the LM interpreter"
  ([Qiu et al., ICLR 2024](https://arxiv.org/html/2310.08559v4)).
- Turning GPT-4's natural-language hypotheses into Python took it from 12.5% to 47.5%
  ([Wang/Zelikman, 12 Sep 2023](https://threadreaderapp.com/thread/1701405044610851230)).

For 2026 frontier models: not located.

**Q3. Does seeing intermediate results help?** Execution feedback does: Greenblatt's "Revision seems to fix around 20%
of the remaining incorrect solutions"; Poetiq 31% → 54% on ARC-AGI-2; SOAR 29.67% → 34.83%; Barbadillo, with the BARC
model, saw no significant gain. Images instead of text hurt: GPT-4V on images 0.23 vs text-only GPT-4 0.69
([Mitchell et al., Dec 2023](https://arxiv.org/html/2311.09247)); o3 (medium effort) on images 5.6%, 29.2% with Python tools, vs 77.1% on
text (Beger et al., Table 1); rendering grids causes "a dramatic 20.5% performance drop due to imprecise element-wise
manipulation" ([Zhang et al., Nov 2025](https://arxiv.org/html/2511.15703v2)). A visual check of a finished answer
helps a little (section 6).

**Q4. Does anyone combine TTT with exact execution?** Yes, with Python executing: SOAR fine-tunes on its own search
traces ("an extra 3-5% tasks"); CodeIt relabels programs by their actual outputs; Barbadillo's search-and-learn went
23.3% → 28.3% on ARC-AGI-1 but "does not yet solve any of the private test tasks from ARC-AGI-2".

**INTERPRETATION: open questions for us.**
1. Program-synthesis systems already execute in Python, exactly; the measured 2–20% execution errors belong to models
   applying rules in tokens or images. What does an internal certified executor add beyond one small on-device loop?
2. Measured losses are mostly hypothesis generation, selection and perception. Does a cheap exact executor help
   there, for example by checking many more hypotheses?
3. Image input costs LLMs up to about 20 points on rule application. Does a vision-tower readback of a canvas inherit
   that, or does a certified local view avoid it?
4. On ARC-AGI-3 the winners write an executable world model and test it against the logged history. Can a 0.8B–4B model
   write those hypotheses?
5. With ARC-AGI-1 and -2 saturated, and offline entries at 88% (ARC-AGI-2) and 75.56 (ARC-AGI-3) on public boards, which
   benchmark and which constraint (cost, size, on-device, certificate) would make a result legible?

---

## 6. Prior art for our specific combination

| Item | Verdict | Closest work |
|---|---|---|
| Model executes its own grid programs internally on ARC | **Partial** | See below. |
| Certified or formally verified execution on ARC | **Not located** | CellARC ([11 Nov 2025](https://arxiv.org/abs/2511.07908)): an ARC-style benchmark from 1D cellular automata with known rules. The exactness is in the ground truth, not the learner. |
| Visual revision loop on ARC | **Found** | Modality-Switch Self-Correction ([Zhang et al., Nov 2025](https://arxiv.org/html/2511.15703v2)): render the predicted grid, have a VLM critic check it, up to 3 rounds. o4-mini went 42.25 → 44.75, GPT-4o 8.25 → 12.0. Its principle: "route each sub-task to its optimal modality", meaning vision induces the rule and text applies it. Also Land ([30 Jun 2026](https://arxiv.org/html/2606.31543)): text, image and code candidates with a judge, 72.9% ARC-AGI-2 semi-private at $38.99/task. |
| Small VLMs on ARC | **Found** | VARC: an 18M ViT trained on grid images. RoSeViT: 62.6% on ARC-AGI-1 ([Jan 2026](https://arxiv.org/abs/2601.13562)). Qwen3-VL-8B plus Qwen3-8B fine-tuned: 13.25% vs 9.75% text-only (Zhang et al.). Gemma-4-31B on rendered frames: 2nd and 3rd at ARC-AGI-3 Milestone 1. A Qwen 0.8B/4B VLM with LoRA on images: not located. |
| Browser or on-device solver | **Not located** | Closest are consumer GPUs: CompressARC "about 20 minutes per puzzle on one RTX 4070" ([5 Dec 2025](https://arcprize.org/blog/arc-prize-2025-results-analysis)); Product of Experts at about $0.02/task on an RTX 4090 ([v2](https://arxiv.org/html/2505.07859v2)). |
| A model that writes a program and runs it on a grid it can see; TTT plus execution; a looped net with a canvas | **Partial** | See below. |

**Internal execution:**
- **LPN** ([Bonnet & Macfarlane, v3 Nov 2025](https://arxiv.org/html/2411.08706v3)): a latent program vector is searched
  by gradient and executed by a neural decoder. 178M parameters, 15.50% on ARC-AGI-1 eval.
- **Per-task neural cellular automata** ([Xu & Miikkulainen, Dec 2025](https://arxiv.org/html/2506.15746v3)): 23 of 172
  feasible training tasks.
- **ARC-NCA** ([Guichard et al., May 2025](https://arxiv.org/html/2505.08778v1)): 12.9% of the 262 eval tasks that need
  no resizing.
- A network trained to emulate an ARC DSL interpreter: not located.

**Combinations, closest work:** Tufa Labs (REPL, image and ASCII on a 27B model); SOAR and CodeIt (TTT plus Python
execution); ARChitects 2025 (masked diffusion refining the output grid); TRM and LoopViT (looped answer refinement).
Internal execution plus vision readback plus a certificate, together: not located.

INTERPRETATION. Every component has a precedent. The exhaustive local certificate has none on ARC that I could find.
Whether ARC rewards that component is the open question in section 5.

---

## 7. Costs and timelines

**Per-task cost now.** ARC-AGI-2 semi-private at retail prices ([leaderboard](https://arcprize.org/leaderboard), read
30 Oct). The 120-task column is my arithmetic.

| System | Score | $/task | ≈ 120 tasks |
|---|---|---|---|
| GPT-6 Astra (Max) | 95.0% | $1.12 | $134 |
| Claude Opus 5.5 (High) | 93.3% | $0.408 | $49 |
| GPT-6.1 Sol (Max) | 94.2% | $0.254 | $30 |
| DeepSeek V4.1 Flash 1017 (Max) | 78.1% | $0.163 | $20 |
| Poetiq on Gemini 3 Pro (Dec 2025) | 54.0% | $30.57 | $3,668 |
| NVARC, Kaggle (2025) | 24.03% private | $0.20 | $24 |

**Kaggle budgets.**
- 2025: "$50 worth" per submission ([24 Mar 2025](https://arcprize.org/blog/announcing-arc-agi-2-and-arc-prize-2025)),
  described as "240 tasks within 12 hours using 4×L4" ([4 Feb 2026](https://arxiv.org/html/2603.06590v1)). That is
  about $0.21 per task by my arithmetic.
- 2026: 12 h on L4x4 for ARC-AGI-2, 9 h on RTX 6000 for ARC-AGI-3.

**Offline build compute.** ARChitects 2024: 98 H100-hours to fine-tune ([v2](https://arxiv.org/html/2505.07859v2)).
ARChitects 2025: pre-training "39 hours on an 8×H100 cluster" (312 H100-hours, my arithmetic), then two weeks on 16
H100s (at most ≈5,400 H100-hours) and one to three GH200 machines throughout
([write-up](https://lambdalabsml.github.io/ARC2025_Solution_by_the_ARChitects/)). NVARC: GPU-hours not located. TRM:
"around 3 days with 4 H100" ([arXiv](https://arxiv.org/html/2510.04871v1)). VARC: 8×H100 for 4.8 h. LPN: 2 days on a
TPU v4-32. Cognizant's 75M transformer from scratch: about 76% ARC-AGI-1 public eval and about 17% ARC-AGI-2 in "a
little over four hours" on one H100, self-reported ([21 Sep 2026](https://www.cognizant.com/us/en/ai-lab/blog/efficient-ai-reasoning-arc-agi)).

**Build time.** ARChitects 2025: three people across the March–November competition; the key trick came "only 5 days
before the competition ended". NVARC: two people ([NVIDIA, 5 Dec 2025](https://developer.nvidia.com/blog/nvidia-kaggle-grandmasters-win-artificial-general-intelligence-competition/)),
duration not located. MindsAI: on ARC since at least the 2023 ARCathon ([Jun 2025](https://arxiv.org/abs/2506.14276)).
The 2026 entry deadline passed on 26 Oct ([Kaggle](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-2/overview)).

---

## 8. Glossary (plain words)

- **ARC-AGI-1** (Chollet, 2019). A few input→output grid pairs (up to 30×30, 10 colours), then a test input; produce the
  exact output. Learning a rule from a handful of examples.
- **ARC-AGI-2** (2025). Same format, harder: several interacting rules per task; each solved by two people in two tries.
- **ARC-AGI-3** (2026). Instruction-free turn-based games on a 64×64 grid, scored by actions used relative to people.
- **Public / semi-private / private sets.** Visible to all; used for API models (small leak risk); offline Kaggle only.
  Public scores are the least trustworthy.
- **pass@2.** Two guesses per test output; either exactly right counts.
- **RHAE** (2026). ARC-AGI-3's score: (human actions ÷ AI actions)² per level, capped, averaged. Waste costs quadratically.
- **Standard vs Provider Adapter harness.** The model keeps only its own notes, or also its vendor's hidden reasoning
  state. Astra: 62.7% vs 99.9%.
- **Kaggle limits.** No internet, 12 h (ARC-AGI-2) or 9 h (ARC-AGI-3) on fixed GPUs; forces small open models.
- **Skill-acquisition efficiency** (Chollet, 2019). Intelligence as skill gained per unit of prior knowledge and
  experience; why ARC counts cost and actions.
- **Core-knowledge priors.** What a young child has: objects, basic geometry and physics, agents with goals.
- **DSL.** A small language of grid operations; solving means finding a short program in it that fits every demo.
- **Program synthesis / search.** Finding such a program by enumeration, LLM sampling or evolution.
- **Induction vs transduction** (Li et al., 2024). Infer a program and run it, or have a network output the grid
  directly. They solve different tasks.
- **Test-time training (TTT).** Fine-tune on each new task's own demos, augmented by rotations, flips and colour swaps
  that keep its rule, before answering.
- **LoRA.** A cheap fine-tune that trains small add-on matrices instead of the whole model.
- **Refinement loop** (ARC Prize, 2025). Propose, check against a signal, revise, repeat; what won in 2025.
- **Evolutionary program synthesis.** A population of programs scored on the demos and mutated by an LLM.
- **Hindsight relabelling** (CodeIt, 2024). A wrong program is a correct example for whatever it actually outputs.
- **HRM / TRM** (2025). 27M and 7M networks trained from scratch on ARC that loop the same layers to refine an answer.
- **Frontier model / LRM; test-time compute.** The largest commercial models, reasoning in a long hidden chain of
  thought; "test-time compute" is the extra computation spent per problem (longer reasoning, samples, search).
- **Knowledge contamination** (ARC Prize, 2025–26). Scoring by having seen much ARC-like data, not by learning efficiently.
- **MDL.** Prefer the shortest total description of the data (Ferré's ARC models).
- **Library learning / DreamCoder.** Turn recurring sub-programs into new primitives, so the DSL grows.
- **Object-centric representation.** A grid described as objects with properties, not pixels.
- **NCA.** Every cell runs the same small learned network on its neighbours, step after step: a learned local rule.
- **LPN** (2024). Search a vector space standing for programs; execute with a decoder network.
- **VLM; ViT.** A language model that also reads images; a vision transformer, which treats image patches as tokens.
- **Masked diffusion LM.** Writes by filling masked positions over several passes, so earlier output can be revised.
- **ConceptARC, MiniARC.** Smaller ARC-style task sets used in analysis papers.
- **REPL.** An interactive code prompt: run a line, see the result.
- **H100-hour.** One hour on one NVIDIA H100 GPU; the unit of training budgets.
- **World model (ARC-AGI-3).** A predictive model of how a game reacts to actions; the 2026 winners write it in Python.
- **CEGIS.** Propose a program, find an input where it fails, add it, repeat.
- **Retrodiction.** Check a hypothesis against what already happened before trusting it on new actions.

---

## What I could not verify

- The methods behind the 2026 Kaggle leaders (Tufa Labs 88.06; Yi-Chia Chen @ Fields Model 87.22 / 75.56); these are
  public-board scores on about half the hidden data. "Fields Model": not located.
- Open-weight status of the leaderboard's frontier rows; why ARC-AGI-3 runs above the policy's $10,000 cap are listed.
- ARC-AGI-4: only a secondary job-listing repost.
- Icecuber's primary write-up; any measured share of ARC-AGI-2 expressible as short local or object programs;
  right-rule-wrong-grid rates for 2026 frontier models.
- Conflicts: MindsAI 2025 at 12.64% vs 15.42% on the same page; TRM 44.6% public vs 40.0% verified; HRM 2.4% (URM's
  figure) vs 2%.
- NVARC's GPU-hours, generator models and TRM component's share (its paper did not render); BDH-CQ on ARC (none found).
- Self-reported public-eval only: URM, LoopViT, Looped Flows, Imbue's 95.1%.
- Quotes in sections 2, 4 and 5 came through a summarising fetch tool. I re-checked directly the Mitchell table, the HRM
  analysis, Looped Flows, Imbue, the Modality-Switch paper, Cognizant, and every arcprize.org and Kaggle page in
  section 1. The fetch tool cached some PDFs outside the repo; I read only the ARC-AGI-3 report and deleted them all.
