#!/usr/bin/env bash

cleanup() {
  echo "Termination signal received. Cleaning up..."
  ./space_inserter.py
  exit 1
}

trap cleanup SIGINT

./space_replacer.py
./extract_input_and_expected.sh $2
./convert_to_c.py $2
verification_res=$(./verify_tests.sh $1 $2)

num_tests=0;
not_running_through=();
not_passed=();

if [[ $2 == "all" ]]; then
  paths=(./sys_tests/*.picoc)
elif [[ -n "$2" ]]; then
  paths=(./sys_tests/*$2*.picoc)
else
  paths=(./sys_tests/{basic,advanced,example,error,exclude,hard,thesis,tobias}*.picoc)
fi

if [ ! -f "${paths[0]}" ]; then
  exit 1
fi

for test in "${paths[@]}"; do
  ./heading_subheadings.py "heading" "$test" "$1" "="
  ./src/main.py $(cat ./run/most_used_compile_opts.txt) $3 $4 "$test";
  if [ -f "${test%.picoc}.reti" ]; then
    reti_interpreter $(cat ./run/most_used_interpret_opts.txt) $3 $4 "${test%.picoc}.reti";
  fi

  if [[ $? != 0 ]]; then
    not_running_through+=("$test");
  fi

  diff "${test%.picoc}.expected_output" "${test%.picoc}.output"
  if [[ $? != 0 ]]; then
    not_passed+=("$test");
  fi
  ((num_tests++));
done;
echo "$verification_res" | tee ./sys_tests/tests.res
echo Running through: $(($num_tests-${#not_running_through[@]})) / $num_tests | tee -a ./sys_tests/tests.res
echo Not running through: ${not_running_through[*]} | tee -a ./sys_tests/tests.res
echo Passed: $(($num_tests-${#not_passed[@]})) / $num_tests | tee -a ./sys_tests/tests.res
echo Not passed: ${not_passed[*]} | tee -a ./sys_tests/tests.res

./space_inserter.py

if [[ ${#not_passed[@]} != 0 ]]; then
    exit 1
fi
