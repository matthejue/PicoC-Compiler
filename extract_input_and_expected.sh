#!/usr/bin/env bash

if [[ $1 == "all" ]]; then
  paths=(./test/*.picoc)
elif [[ -n "$1" ]]; then
  paths=(./test/*$1*.picoc)
else
  paths=(./test/{basic,advanced,example,error,exclude,hard,thesis,tobias}*.picoc)
fi

for test in "${paths[@]}"; do
  sed -n '1p' "$test" | sed -e 's/^\/\/ in://' > "${test%.picoc}.input"

  expected=$(sed -n '2p' "$test" | sed -e 's/^\/\/ expected://')
  printf '%s' "$expected" > "${test%.picoc}.expected_output"
done
