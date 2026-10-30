#!/bin/zsh
# usage: wait_any.sh <name> <pid> <log>  — wait for pid, then print the log tail
while kill -0 "$2" 2>/dev/null; do sleep 120; done; echo "$1 exited $(date +%H:%M)"; tail -c 3000 "$3"
