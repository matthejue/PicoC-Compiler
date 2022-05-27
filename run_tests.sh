#!/usr/bin/env bash

./extract_input_and_expected.sh
./convert_to_c.py
verification_res=$(./verify_tests.sh $1)

num_tests=0;
not_running_through=();
not_passed=();
  # for test in ./{old_,}tests/*$1*.picoc; do
  for test in ./tests/{basic,advanced}*$2*.picoc; do
    ./heading_subheadings.py "heading" "$test" "$1" "="
    ./src/main.py $(cat ./most_used_interpret_opts.txt) -c $3 "$test";

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
