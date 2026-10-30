#!/usr/bin/env bash
# Round 2: bundle the brief, the bulletin, the prior-art verdicts, the four round-1 sets and the atlas, then run four
# minds independently (Gemini and Opus via agy with no tools; Codex read-only; Grok via Cursor). 150-minute watchdog.
set -u
WS=/Users/neo/repos/polyformer-wt/theory
T=$WS/research/theory
R=$T/round2; mkdir -p "$R"
B=$R/BUNDLE.md
{ cat "$T/ROUND2_BRIEF.md"
  for f in BULLETIN_1 ROUND1_PRIORART; do printf '\n\n---\n\n# %s\n\n' "$f"; cat "$T/$f.md"; done
  for m in codex grok gemini opus; do printf '\n\n---\n\n# ROUND 1: %s\n\n' "$m"; cat "$T/round1/$m.md"; done
  for f in ATLAS ANOMALIES TENSIONS GRAVEYARD; do printf '\n\n---\n\n# %s\n\n' "$f"; cat "$T/$f.md"; done
} > "$B"
NOTOOLS="IMPORTANT: do not call any tools, read any files or run any commands. Everything you need is in this message. Write your complete answer directly as your reply text, in Markdown.

"
E=/private/tmp/claude-501/-Users-neo-repos-polyformer/c0f48f9a-a2fb-4297-be2d-a48e0a64c3d9/scratchpad/agy_empty
( cd "$WS" && /Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex exec -s read-only --skip-git-repo-check -c model_reasoning_effort="high" -o "$R/codex.md" - < "$B" > "$R/codex.log" 2>&1 ) & P1=$!
( cd "$E" && /Applications/Gemini.app/Contents/Helpers/agy -p "${NOTOOLS}$(cat "$B")" --model gemini-4-argon-high --sandbox > "$R/gemini.md" 2> "$R/gemini.log" ) & P2=$!
( cd "$E" && /Applications/Gemini.app/Contents/Helpers/agy -p "${NOTOOLS}$(cat "$B")" --model claude-opus-5-5-high --sandbox > "$R/opus.md" 2> "$R/opus.log" ) & P3=$!
( ~/.local/bin/cursor-agent -p --output-format json --model grok-4.7-xhigh-fast --force --trust --workspace "$WS" "Read research/theory/round2/BUNDLE.md in full and follow its instructions exactly. Write your complete answer to research/theory/round2/grok.md. Do not edit any other file and do not commit. Never run a blocking long-lived command." > "$R/grok.log" 2>&1 ) & P4=$!
deadline=$(( $(date +%s) + 9000 ))
for p in $P1 $P2 $P3 $P4; do
  while kill -0 $p 2>/dev/null; do
    if [ "$(date +%s)" -gt "$deadline" ]; then kill $p 2>/dev/null; echo "watchdog killed pid $p"; fi
    sleep 30
  done
done
cd "$WS" && git add research/theory/ROUND2_BRIEF.md research/theory/round2/*.md 2>/dev/null; git commit -q -m "Theory round 2: Codex, Gemini, Grok, Opus

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" 2>/dev/null
for f in codex gemini grok opus; do printf '%s: %s bytes\n' "$f" "$(wc -c < "$R/$f.md" 2>/dev/null || echo 0)"; done
echo "theory round 2 finished"
