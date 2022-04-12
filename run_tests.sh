#!/usr/bin/env bash

./extract_input_and_expected.sh

num_tests=0;
not_running_through=();
not_passed=();
  for test in ./tests/*$1*.picoc; do
    echo -e "\n\033[1;37m===============================================================================";
    echo $test;
    echo -e "===============================================================================\033[0;0m";
    ./src/main.py -ctas -p -d 20 -S 2 -C -m $2 $test;
    # ./RETI-Interpreter/src/main.py -ctaor -p -b 8 -d 32 -D 20 -s 2 -E 8 -U 4 -S 0 -C -m ${test%.picoc}.reti

    if [[ $? != 0 ]]; then
      not_running_through+=($test);
    fi;

    diff ${test%.picoc}.out_expected ${test%.picoc}.out
    if [[ $? != 0 ]]; then
      not_passed+=($test);
    fi
    ((num_tests++));
done;
echo Running through: $(($num_tests-${#not_running_through[@]})) / $num_tests;
echo Passed: $(($num_tests-${#not_passed[@]})) / $num_tests;
echo Not running through tests: ${not_running_through[*]};
echo Not passed tests: ${not_passed[*]};

if [[ ${#not_passed[@]} != 0 ]]; then
    exit 1
fi
