#!/usr/bin/env bash
# Overnight "chew": round A (diverge, 5 lenses) -> round B (cross-critique + live prior art, 3 critics) -> round C (synthesis memo).
set -u
R=/Users/neo/repos/polyformer
D=$R/research/meta/chew
CODEX=/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex
AGY=/Applications/Gemini.app/Contents/Helpers/agy
COMMON="Read $D/CHEW_CONTEXT.md first (and any local file it names that you need; you may read files under $R and /Users/neo/repos/sketchpad, but change nothing). Search the live web thoroughly; cite every paper with authors, year, venue/arXiv id and one line on what it did; never invent citations (write 'unverified' when unsure). Your final message IS your report: markdown, no preamble."
cx() { # name, prompt  (codex with web search, read-only)
  "$CODEX" --search exec -s read-only --skip-git-repo-check -C "$R" -c model_reasoning_effort="high" -o "$D/$1.md" "$2" > "$D/logs/$1.log" 2>&1 < /dev/null
}
ag() { # name, model, prompt
  (cd "$R" && "$AGY" -p "$3" --model "$2" --dangerously-skip-permissions --print-timeout 0 > "$D/$1.md" 2> "$D/logs/$1.log" < /dev/null)
}
mkdir -p "$D/logs"
echo "A start $(date)" >> "$D/logs/progress.txt"
cx A1_nature_anatomy "$COMMON
Your lens: THE ANATOMY OF RECENT NATURE-LEVEL AI PAPERS. List 15-25 papers from 2022-2026 in Nature, Science, Nature Human Behaviour, Nature Machine Intelligence (flagship articles) and PNAS that are AI/LLM-driven and drew wide attention, especially ones by small teams (1-4 authors) or with modest compute. For each: the headline, the old question it settled or the discovery, compute/team size, and why editors took it. Then extract the recurring recipe(s) a solo researcher with LLM fine-tuning skills could follow in 4-10 weeks. Then propose 4 concrete directions for Neo following those recipes, each with a draft Nature-style title, the one decisive experiment, and the closest prior art. At most 1,400 words." &
cx A2_language "$COMMON
Your lens: LANGUAGE AND MIND. Go beyond the gate report (research/meta/survive/chomsky_gate_report.md). Map the 2024-2026 frontier where LLMs meet linguistics, psycholinguistics, language acquisition and the neuroscience of language (brain-LM alignment, impossible languages, poverty of the stimulus, BabyLM, emergent syntax, LLM informants, universals, typology). Identify the open questions whose answer would be front-page (e.g. a decades-old debate an experiment could settle). Propose 4 concrete directions for Neo, each with a draft Nature-style title, the decisive experiment with open models, a kill criterion, cost, and the most dangerous prior paper. Say plainly which could plausibly reach Nature or Nature Human Behaviour. At most 1,400 words." &
ag A3_assets gemini-4-argon-high "$COMMON
Your lens: OUR OWN ASSETS. Read research/meta/META_REPORT.md, research/meta/rounds/r8_status.md, research/FORMALISM.md and the Sketchpad paper abstract and introduction. Which of our results or capabilities (Sketchpad certification, Nerode minimal automata inside networks, higher-order/Newton/Feynman attention, holonomy, the characters law) could, extended or recombined, become a Nature-level result? Be brutally honest about which cannot. For the 3 best, give a draft title, the missing experiment, the risk, and a live prior-art check. At most 1,200 words." &
ag A4_wildcard claude-opus-5-5-high "$COMMON
Your lens: WILD CARD / EDITOR'S EYE. Imagine you are a Nature editor scanning 2027 submissions: what AI result by a single researcher would make you stop scrolling? Think across sciences (language, cognition, mathematics, biology, physics, social science, music, history) where an LLM fine-tuner with formal-methods skills could produce a genuine discovery or settle a debate in 4-10 weeks. Generate 12 headline ideas in one line each, then kill 8 with reasons and prior art, and develop the surviving 4: title, decisive experiment, kill criterion, why Nature, closest prior art (verify live). At most 1,400 words." &
cx A5_skeptic "$COMMON
Your lens: THE SKEPTIC. Find AI/LLM papers in Nature/Science/high-profile venues (2022-2026) that were hammered after publication or retracted, and claims of 'LLMs reveal X about language/mind/science' that failed to replicate or were judged overclaimed (e.g. debates around emergent abilities, brain-alignment confounds, impossible-languages confounds, theory-of-mind claims). Extract the failure modes and the review bar: what a Nature-bound claim by a solo researcher must do (pre-registration, human data, replication, controls) to survive. Also: how presubmission enquiries work at Nature and Nature Human Behaviour and how solo researchers have succeeded. At most 1,000 words." &
wait
echo "B start $(date)" >> "$D/logs/progress.txt"
BREF="Read all round-A reports: $D/A1_nature_anatomy.md, A2_language.md, A3_assets.md, A4_wildcard.md, A5_skeptic.md (and research/meta/survive/AUDIT.md if it exists)."
cx B1_gate "$COMMON
$BREF
Your role: PRIOR-ART GATE AND RANKER. Pool every direction proposed in round A, merge duplicates, and pick the 6 strongest. For each, run a thorough live prior-art search (2023-Nov 2026; arXiv, ACL, NeurIPS/ICLR/ICML, Nature family, PNAS, bioRxiv/PsyArXiv/LingBuzz) and give OWNED / PARTIAL (what remains) / OPEN, the most dangerous paper, and scores 1-5 on: headline strength, Nature fit, novelty, feasibility for one person in <=10 weeks, cost, robustness of the claim under hostile review, fit to Neo's goals. At most 1,600 words." &
ag B2_critic claude-opus-5-5-high "$COMMON
$BREF
Your role: HOSTILE REVIEWER AND IMPROVER. For the 6 most promising directions across round A, write the review a hostile Nature referee would write, then say how to change each direction (scope, controls, human data, theory) so it survives, or kill it. Then propose 2 new hybrids that combine the best parts. At most 1,400 words." &
ag B3_theory gemini-4-argon-high "$COMMON
$BREF
Your role: THEORY. Which directions have a real theorem or mechanism at their core (not just an empirical finding)? Where can our Nerode / Myhill / higher-order attention / certification theory give a direction an explanatory spine that makes it more than a benchmark result? Check the math carefully. At most 1,200 words." &
wait
echo "C start $(date)" >> "$D/logs/progress.txt"
cx C_memo "$COMMON
Read every report in $D (A1-A5, B1-B3) and research/meta/survive/AUDIT.md if present. Write the morning memo for Neo: CHEW_MEMO content. Structure: (1) the 3 best directions, ranked, each with a draft Nature-style title, a 120-word abstract of the result we would hope to show, the decisive experiment and kill criterion, prior-art status with the most dangerous paper (re-verify live), time and cost, what could go wrong, and why Nature would care; (2) directions considered and rejected, one line each with the reason; (3) the decisions Neo must make. Plain words: define every term on first use in one sentence. Be honest about odds. At most 1,800 words."
echo "done $(date)" >> "$D/logs/progress.txt"
