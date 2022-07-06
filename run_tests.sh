#!/usr/bin/env bash

./space_replacer.sh
./extract_input_and_expected.sh $2
./convert_to_c.py $2
verification_res=$(./verify_tests.sh $1 $2)

num_tests=0;
not_running_through=();
not_passed=();

if [[ $2 == "all" ]]; then
  paths=(./tests/*.picoc)
elif [[ $2 == "default" ]]; then
  paths=(./tests/{basic,advanced,example,error,exclude,hard}*.picoc)
elif [[ -n "$2" ]]; then
  paths=(./tests/*$2*.picoc)
else
  paths=(./tests/{basic,advanced,example,error,exclude,hard}*.picoc)
fi

for test in "${paths[@]}"; do
  ./heading_subheadings.py "heading" "$test" "$1" "="
  ./src/main.py $(cat ./most_used_interpret_opts.txt) -c $3 $4 "$test";

  if [[ $? != 0 ]]; then
    not_running_through+=("$test");
  fi;

  diff "${test%.picoc}.out_expected" "${test%.picoc}.out"
  if [[ $? != 0 ]]; then
    not_passed+=("$test");
  fi
  ((num_tests++));
done;
echo "$verification_res" | tee ./tests/tests.res
echo Running through: $(($num_tests-${#not_running_through[@]})) / $num_tests | tee -a ./tests/tests.res
echo Not running through: ${not_running_through[*]} | tee -a ./tests/tests.res
echo Passed: $(($num_tests-${#not_passed[@]})) / $num_tests | tee -a ./tests/tests.res
echo Not passed: ${not_passed[*]} | tee -a ./tests/tests.res


./space_inserter.sh

if [[ ${#not_passed[@]} != 0 ]]; then
    exit 1
fi
