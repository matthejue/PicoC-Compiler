#!/usr/bin/env bash

if [[ $1 == "all" ]]; then
  paths=(./sys_tests/*.picoc)
elif [[ -n "$1" ]]; then
  paths=(./sys_tests/*$1*.picoc)
else
  paths=(./sys_tests/{basic,advanced,example,error,exclude,hard,thesis,tobias}*.picoc)
fi

for test in "${paths[@]}"; do
  sed -n '1p' "$test" | sed -e 's/^\/\/ in://' > "${test%.picoc}.input"
  if [[ $(sed -n "1p" "$test") =~ ^//\ expected: ]]; then
    sed -n '1p' "$test" | sed -e 's/^\/\/ expected://' | tr '\n' ' ' > "${test%.picoc}.expected_output"
  elif [[ $(sed -n "2p" "$test") =~ ^//\ expected: ]]; then
    sed -n '2p' "$test" | sed -e 's/^\/\/ expected://' | tr '\n' ' ' > "${test%.picoc}.expected_output"
  elif [[ $(sed -n "3p" "$test") =~ ^//\ expected: ]]; then
    sed -n '3p' "$test" | sed -e 's/^\/\/ expected://' | tr '\n' ' ' > "${test%.picoc}.expected_output"
  fi
done
