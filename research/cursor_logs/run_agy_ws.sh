#!/usr/bin/env bash
# usage: run_agy_ws.sh <name> <workspace> <model> <prompt>   (Antigravity agent, auto-approved tools)
set -u
name="$1"; ws="$2"; model="$3"; prompt="$4"
log="/Users/neo/repos/polyformer/research/cursor_logs/agy_${name}.log"
cd "$ws" || exit 1
nohup /Applications/Gemini.app/Contents/Helpers/agy -p "$prompt" --model "$model" --dangerously-skip-permissions --print-timeout 0 > "$log" 2>&1 < /dev/null &
echo "$name pid $! log $log"
