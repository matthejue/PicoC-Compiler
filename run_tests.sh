#!/usr/bin/env bash

num_tests=0;
not_passed=();
  # for testfile in $(basename --suffix=.picoc ./tests/*$1*.picoc); do
  for testfile in ./tests/*$1*.picoc; do
  echo -e \\n===============================================================================;
  echo $testfile;
  echo ===============================================================================;
  ./src/main.py -c -t -a -s -p -v -b 100 -e 200 -d 20 -S 20 $testfile;
  if [[ $? != 0 ]]; then
    not_passed+=($testfile);
  fi;
  ((num_tests++));
done;
echo Passed: $(($num_tests-${#not_passed[@]})) / $num_tests;
echo Not passed tests: ${not_passed[*]};
