#!/usr/bin/env bash

for test in ./tests/*.picoc; do
  sed -n '1p' "$test" | sed -e 's/^\/\/ in://' > "${test%.picoc}.in"
  sed -n '2p' "$test" | sed -e 's/^\/\/ expected://' > "${test%.picoc}.out_expected"
done
