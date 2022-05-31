#!/usr/bin/env bash

if [[ $1 == "all" ]]; then
  paths=(./tests/*.picoc)
elif [[ -n "$1" ]]; then
  paths=(./tests/*"$1"*.picoc)
else
  paths=(./tests/{basic,advanced,example,error,exclude}*.picoc)
fi

for test in "${paths[@]}"; do
  sed -n '1p' "$test" | sed -e 's/^\/\/ in://' > "${test%.picoc}.in"
  sed -n '2p' "$test" | sed -e 's/^\/\/ expected://' > "${test%.picoc}.out_expected"
done
