#!/usr/bin/env bash
# usage: run_cursor_ws.sh <name> <workspace> <model> <prompt>
set -u
name="$1"; ws="$2"; model="$3"; prompt="$4"
log="/private/tmp/claude-501/-Users-neo-repos-polyformer/c0f48f9a-a2fb-4297-be2d-a48e0a64c3d9/scratchpad/cursor_${name}.json"
cd "$ws" || exit 1
nohup ~/.local/bin/cursor-agent -p --output-format json --model "$model" --force --trust --workspace "$ws" "$prompt" > "$log" 2>&1 &
echo "$name pid $! log $log"
