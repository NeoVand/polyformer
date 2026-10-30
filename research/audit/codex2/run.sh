#!/bin/zsh
# Run the four Codex audits in parallel, one per experiment directory; wait for all.
CODEX=/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex
A=/Users/neo/repos/polyformer/research/audit/codex2
run() { (cd "$2" && nice -n 19 $CODEX exec -s read-only --skip-git-repo-check -c model_reasoning_effort="high" -o "$A/out_$1.md" - < "$A/$1.md" > "$A/log_$1.txt" 2>&1; echo "$1 exit $?") & }
run remember /Users/neo/repos/polyformer-wt/remember/research/remember
run headpin /Users/neo/repos/polyformer-wt/headpin/research/headpin
run scan /Users/neo/repos/polyformer-wt/scan/research/scan
run e3e4 /Users/neo/repos/polyformer-wt/theory/research/theory
wait
