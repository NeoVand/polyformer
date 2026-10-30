#!/usr/bin/env bash
# Needle round: six independent minds, each with its own lens and bundle. 150-minute watchdog.
set -u
WS=/Users/neo/repos/polyformer-wt/theory
N=$WS/research/theory/needle
R=$N/round; mkdir -p "$R"
NOTOOLS="IMPORTANT: do not call any tools, read any files or run any commands. Everything you need is in this message. Write your complete answer directly as your reply text, in Markdown.

"
E=/private/tmp/claude-501/-Users-neo-repos-polyformer/c0f48f9a-a2fb-4297-be2d-a48e0a64c3d9/scratchpad/agy_empty; mkdir -p "$E"
CODEX=/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex
AGY=/Applications/Gemini.app/Contents/Helpers/agy
( cd "$WS" && $CODEX --search exec -s read-only --skip-git-repo-check -c model_reasoning_effort="high" -o "$R/codex.md" - < "$N/BUNDLE_codex.md" > "$R/codex.log" 2>&1 ) & P1=$!
( cd "$E" && $AGY -p "${NOTOOLS}$(cat "$N/BUNDLE_gemini.md")" --model gemini-4-argon-high --sandbox > "$R/gemini.md" 2> "$R/gemini.log" ) & P2=$!
( cd "$E" && $AGY -p "${NOTOOLS}$(cat "$N/BUNDLE_opus.md")" --model claude-opus-5-5-high --sandbox > "$R/opus.md" 2> "$R/opus.log" ) & P3=$!
( ~/.local/bin/cursor-agent -p --output-format json --model grok-4.7-xhigh-fast --force --trust --workspace "$WS" "Read research/theory/needle/BUNDLE_grok.md in full and follow its instructions exactly. Write your complete answer to research/theory/needle/round/grok.md. Do not edit any other file and do not commit. Never run a blocking long-lived command." > "$R/grok.log" 2>&1 ) & P4=$!
( cd "$E" && $AGY -p "${NOTOOLS}$(cat "$N/BUNDLE_outsider_a.md")" --model gemini-4-argon-high --sandbox > "$R/outsider_a.md" 2> "$R/outsider_a.log" ) & P5=$!
( cd "$E" && $AGY -p "${NOTOOLS}$(cat "$N/BUNDLE_outsider_b.md")" --model claude-opus-5-5-high --sandbox > "$R/outsider_b.md" 2> "$R/outsider_b.log" ) & P6=$!
deadline=$(( $(date +%s) + 9000 ))
for p in $P1 $P2 $P3 $P4 $P5 $P6; do
  while kill -0 $p 2>/dev/null; do
    if [ "$(date +%s)" -gt "$deadline" ]; then kill $p 2>/dev/null; echo "watchdog killed pid $p"; fi
    sleep 30
  done
done
cd "$WS" && git add research/theory/needle 2>/dev/null; git commit -q -m "Needle round: six minds

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" 2>/dev/null
for f in codex gemini opus grok outsider_a outsider_b; do printf '%s: %s bytes\n' "$f" "$(wc -c < "$R/$f.md" 2>/dev/null || echo 0)"; done
echo "needle round finished"
