#!/bin/zsh
# usage: wait_all.sh name:pid:log ...  — prints each agent's tail as it exits; returns when all are done.
typeset -A left
for a in "$@"; do left[$a]=1; done
while (( ${#left} > 0 )); do
  for a in ${(k)left}; do
    pid=${${a#*:}%%:*}
    if ! kill -0 $pid 2>/dev/null; then echo "== ${a%%:*} done $(date +%H:%M)"; tail -c 1200 ${a##*:}; echo; unset "left[$a]"; fi
  done
  sleep 120
done
