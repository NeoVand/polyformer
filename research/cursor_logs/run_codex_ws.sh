#!/usr/bin/env bash
# usage: run_codex_ws.sh <name> <workspace> <prompt>   (Codex agent with full access, high effort)
set -u
name="$1"; ws="$2"; prompt="$3"
log="/Users/neo/repos/polyformer/research/cursor_logs/codex_${name}.log"
out="/Users/neo/repos/polyformer/research/cursor_logs/codex_${name}.md"
cd "$ws" || exit 1
nohup /Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex exec --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check -C "$ws" -c model_reasoning_effort="high" -o "$out" "$prompt" > "$log" 2>&1 < /dev/null &
echo "$name pid $! log $log"
