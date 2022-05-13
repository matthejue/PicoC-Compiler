#!/usr/bin/env bash

./extract_input_and_expected.sh
verification_res=$(./verify_tests.sh $1)

num_tests=0;
not_running_through=();
not_passed=();
  # for test in ./{old_,}tests/*$1*.picoc; do
  for test in ./tests/*$2*.picoc; do
    ./heading_subheadings.py "heading" "$test" "$1" "="
    ./src/main.py -ctdambs -p -D 20 -S 2 -M -C $3 "$test";
    # ./RETI-Interpreter/src/main.py -ctaor -p -b 8 -d 32 -D 20 -s 2 -E 8 -U 4 -S 0 -m -v -C ${test%.picoc}.reti

    if [[ $? != 0 ]]; then
      not_running_through+=("$test");
    fi;

    diff "${test%.picoc}.out_expected" "${test%.picoc}.out"
    if [[ $? != 0 ]]; then
      not_passed+=("$test");
    fi
    ((num_tests++));
done;
echo "$verification_res"
echo Running through: $(($num_tests-${#not_running_through[@]})) / $num_tests;
echo Not running through: ${not_running_through[*]};
echo Passed: $(($num_tests-${#not_passed[@]})) / $num_tests;
echo Not passed: ${not_passed[*]};

if [[ ${#not_passed[@]} != 0 ]]; then
    exit 1
fi
