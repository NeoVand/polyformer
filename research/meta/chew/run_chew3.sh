#!/usr/bin/env bash
set -u
R=/Users/neo/repos/polyformer; D=$R/research/meta/chew
CODEX=/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex
COMMON="Read $D/CHEW_CONTEXT.md, $D/C_memo.md and $R/research/meta/survive/AUDIT.md. You may read any file under $R and /Users/neo/repos/sketchpad but change nothing. Search the live web thoroughly and slowly; depth beats speed. Cite every paper with authors, year, venue/arXiv id and one line on what it did; open each paper you rely on; never invent citations (write 'unverified'). Your final message IS your report: markdown, no preamble."
cx() { "$CODEX" --search exec -s read-only --skip-git-repo-check -C "$R" -c model_reasoning_effort="xhigh" -o "$D/$1.md" "$2" > "$D/logs/$1.log" 2>&1 < /dev/null; }
echo "G start $(date)" >> "$D/logs/progress3.txt"
cx D3_grammar "$COMMON
Your role: THE DISCOVERY MACHINE FOR GRAMMAR (direction 2 of the memo; Neo's favourite theme, 'young Chomsky with LLMs'). Design it seriously.
- How would an LLM-informant procedure surface a NEW, true grammatical generalisation? Consider Harris's distributional analysis, Clark's learners, and meaning-matched minimal pairs, which avoid the Hu et al. 2026 TACL confound.
- Which languages or constructions are under-described yet well covered by open multilingual models? Check Qwen3.5's language coverage.
- Which public human-judgment datasets allow validation without running new participants? For example: Sprouse et al. 2013, BLiMP, CLiMP, SyntaxGym, multilingual acceptability sets, and Grambank/WALS for typology.
- What would a linguist collaborator need to see?
- Give a concrete 2-week pilot with numbers and a kill.
- Verify prior art live: Yu et al. 2026 (arXiv:2604.07189), Goertzel 2020, and LLM-for-linguistic-discovery papers.
At most 1,600 words." &
cx E1_referee "$COMMON
Also read $D/D1_citations.md, D2_arity.md, D4_nohumans.md, E2_feasibility.md and F_memo2.md.
Your role: SENIOR NATURE EDITOR AND HOSTILE REFEREE.
- Rank every direction on the table by expected value for Neo: P(top venue) × impact, with P(solid specialist paper) as the floor.
- Assume a 10-week, one-person budget of at most \$5k, preferably with no new human data.
- Drop anything that rests on a citation D1 flagged as fabricated or misdescribed.
- For the top 3, write the referee report and the fix.
At most 1,500 words." &
wait
cx F_memo3 "$COMMON
Also read every file in $D (A1-A5, B1-B3, D1-D4, E1-E2, F_memo2). Revise F_memo2 into the FINAL memo for Neo, integrating D3_grammar and E1_referee (which were missing when F_memo2 was written). Keep its structure and word limit (at most 2,000 words), plain words, verified citations only. Add at the top a 5-line summary of where you land and why."
echo "done $(date)" >> "$D/logs/progress3.txt"
