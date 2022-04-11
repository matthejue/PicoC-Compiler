#!/usr/bin/env bash

for test in ./tests/*.picoc; do
  sed -n '1p' $test | sed -e 's/^// in://' > ./tests/$(basename --suffix=.picoc $test).in
  sed -n '2p' $test | sed -e 's/^// except://' > ./tests/$(basename --suffix=.picoc $test).out_except
done
