#!/usr/bin/env bash
# usage: wait_pids.sh <name> <pid> <log>
while kill -0 "$2" 2>/dev/null; do sleep 300; done
echo "$1 cursor agent exited"; tail -c 2500 "$3"
