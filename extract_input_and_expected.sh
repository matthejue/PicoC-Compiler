#!/usr/bin/env bash

if [[ $1 == "all" ]]; then
  paths=(./tests/*.picoc)
elif [[ $1 == "default" ]]; then
  paths=(./tests/{basic,advanced,example,error,exclude,hard}*.picoc)
elif [[ -n "$1" ]]; then
  paths=(./tests/*$1*.picoc)
else
  paths=(./tests/{basic,advanced,example,error,exclude,hard}*.picoc)
fi

for test in "${paths[@]}"; do
  sed -n '1p' "$test" | sed -e 's/^\/\/ in://' > "${test%.picoc}.in"
  sed -n '2p' "$test" | sed -e 's/^\/\/ expected://' > "${test%.picoc}.out_expected"
  line3=$(sed -n '3p' "$test")
  if [[ "$line3" == *datasegment* ]]; then
    sed -n '3p' "$test" | sed -e 's/^\/\/ datasegment://' > "${test%.picoc}.datasegment_size"
  fi
done
