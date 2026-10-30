#!/bin/zsh
cd /Users/neo/repos/polyformer/research/audit/leap2_gate && nice -n 19 /Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex --search exec -s read-only --skip-git-repo-check -c model_reasoning_effort="high" -o out.md - < brief.md > log.txt 2>&1; echo "exit $?"
