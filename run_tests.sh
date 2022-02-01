#!/usr/bin/env bash

num_tests=0;
not_passed=();
  # for testfile in $(basename --suffix=.picoc ./tests/*$1*.picoc); do
  for testfile in ./tests/*$1*.picoc; do
  echo -e "\n\033[1;37m===============================================================================";
  echo $testfile;
  echo -e "===============================================================================\033[0;0m";
  ./src/main.py -c -t -a -s -p -v -b 128 -e 256 -d 20 -S 2 -C $testfile;
  if [[ $? != 0 ]]; then
    not_passed+=($testfile);
  fi;
  ((num_tests++));
done;
echo Passed: $(($num_tests-${#not_passed[@]})) / $num_tests;
echo Not passed tests: ${not_passed[*]};
