#!/usr/bin/env bash
# Outsider round: fresh minds see only the north star, the fact sheet, TAKEN and the graveyard. 120-minute watchdog.
set -u
WS=/Users/neo/repos/polyformer-wt/theory; R=$WS/research/theory/outsiders; B=$R/BUNDLE.md
NOTOOLS="IMPORTANT: do not call any tools, read any files or run any commands. Everything you need is in this message. Write your complete answer directly as your reply text, in Markdown.

"
E=/private/tmp/claude-501/-Users-neo-repos-polyformer/c0f48f9a-a2fb-4297-be2d-a48e0a64c3d9/scratchpad/agy_empty
( cd "$E" && /Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex exec -s read-only --skip-git-repo-check -c model_reasoning_effort="high" -o "$R/codex.md" - < "$B" > "$R/codex.log" 2>&1 ) & P1=$!
( cd "$E" && /Applications/Gemini.app/Contents/Helpers/agy -p "${NOTOOLS}$(cat "$B")" --model gemini-4-argon-high --sandbox > "$R/gemini.md" 2> "$R/gemini.log" ) & P2=$!
( cd "$E" && /Applications/Gemini.app/Contents/Helpers/agy -p "${NOTOOLS}$(cat "$B")" --model claude-opus-5-5-high --sandbox > "$R/opus.md" 2> "$R/opus.log" ) & P3=$!
( cd "$E" && ~/.local/bin/cursor-agent -p --output-format text --model grok-4.7-xhigh-fast --trust --workspace "$E" "${NOTOOLS}$(cat "$B")" > "$R/grok.md" 2> "$R/grok.log" ) & P4=$!
deadline=$(( $(date +%s) + 7200 ))
for p in $P1 $P2 $P3 $P4; do
  while kill -0 $p 2>/dev/null; do
    if [ "$(date +%s)" -gt "$deadline" ]; then kill $p 2>/dev/null; echo "watchdog killed pid $p"; fi
    sleep 30
  done
done
cd "$WS" && git add research/theory/DEMO_NORTH_STAR.md research/theory/TAKEN.md research/theory/OUTSIDER_BRIEF.md research/theory/outsiders/*.md 2>/dev/null; git commit -q -m "Theory: outsider round (demo-first, fresh context)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" 2>/dev/null
for f in codex gemini grok opus; do printf '%s: %s bytes\n' "$f" "$(wc -c < "$R/$f.md" 2>/dev/null || echo 0)"; done
echo "outsider round finished"
