#!/usr/bin/env bash

num_tests=0;
not_passed=();
for testfile in ./tests/*.picoc; do
  echo -e \\n===============================================================================;
  echo $testfile;
  echo ===============================================================================;
  ./src/pico_c_compiler.py -c -t -a -S -p -v -s 100 -e 200 -d 20 -m $testfile;
  if [[ $? != 0 ]]; then
    not_passed+=($testfile);
  fi;
  ((num_tests++));
done;
echo Passed: $(($num_tests-${#not_passed[@]})) / $num_tests;
echo Not passed tests: ${not_passed[*]};
