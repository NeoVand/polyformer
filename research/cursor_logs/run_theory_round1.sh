#!/usr/bin/env bash
# Waits for the atlas (ATLAS_DONE or the atlas agent exiting), bundles it, then runs Codex, Gemini and Grok
# independently on ROUND1_BRIEF. Each gets a 120-minute watchdog.
set -u
WS=/Users/neo/repos/polyformer-wt/theory
T=$WS/research/theory
ATLAS_PID="$1"
while kill -0 "$ATLAS_PID" 2>/dev/null && [ ! -f "$T/ATLAS_DONE" ]; do sleep 120; done
for f in ATLAS.md ANOMALIES.md TENSIONS.md GRAVEYARD.md; do [ -s "$T/$f" ] || { echo "missing $f; round 1 not launched"; exit 1; }; done
B=$T/round1/BUNDLE.md
{ cat "$T/ROUND1_BRIEF.md"; for f in ATLAS ANOMALIES TENSIONS GRAVEYARD; do printf '\n\n---\n\n# %s\n\n' "$f"; cat "$T/$f.md"; done; } > "$B"
cd "$WS" || exit 1
( /Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex exec -s read-only --skip-git-repo-check -c model_reasoning_effort="high" -o "$T/round1/codex.md" - < "$B" > "$T/round1/codex.log" 2>&1 ) &
P1=$!
( /Applications/Gemini.app/Contents/Helpers/agy -p "$(cat "$B")" --model gemini-4-argon-high > "$T/round1/gemini.md" 2> "$T/round1/gemini.log" ) &
P2=$!
( ~/.local/bin/cursor-agent -p --output-format json --model grok-4.7-xhigh-fast --force --trust --workspace "$WS" "Read research/theory/round1/BUNDLE.md in full and follow its instructions exactly. Write your complete answer to research/theory/round1/grok.md. Do not edit any other file and do not commit." > "$T/round1/grok.log" 2>&1 ) &
P3=$!
deadline=$(( $(date +%s) + 7200 ))
for p in $P1 $P2 $P3; do
  while kill -0 $p 2>/dev/null; do
    if [ "$(date +%s)" -gt "$deadline" ]; then kill $p 2>/dev/null; echo "watchdog killed pid $p"; fi
    sleep 30
  done
done
cd "$WS" && git add research/theory/round1/*.md 2>/dev/null; git commit -q -m "Theory round 1: Codex, Gemini, Grok conjectures

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" 2>/dev/null
for f in codex gemini grok; do printf '%s: %s bytes\n' "$f" "$(wc -c < "$T/round1/$f.md" 2>/dev/null || echo 0)"; done
echo "theory round 1 finished"
