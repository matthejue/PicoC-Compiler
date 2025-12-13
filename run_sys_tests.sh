#!/usr/bin/env bash

cleanup() {
  echo "Termination signal received. Cleaning up..."
  ./space_inserter.py
  exit 1
}

trap cleanup SIGINT

MAX_EMULATOR_DURATION_SECONDS=5

./space_replacer.py
./extract_input_and_expected.sh $2
./convert_to_c.py $2

verification_res=$(./verify_tests.sh $1 $2)

num_tests=0;
failing=();
not_passed=();

if [[ $2 == "all" ]]; then
  paths=(./sys_tests/*.picoc)
elif [[ -n "$2" ]]; then
  paths=(./sys_tests/*$2*.picoc)
else
  paths=(./sys_tests/{basic,advanced,example,hard,thesis,tobias}*.picoc)
fi

if [ ! -f "${paths[0]}" ]; then
  exit 1
fi

for test in "${paths[@]}"; do
  ./heading_subheadings.py "heading" "$test" "$1" "="
  ./run.py $(cat ./opts/test_cpl_opts.txt) $3 "$test" -o "${test%.picoc}.reti";

  compile_status=$?
  if [[ $compile_status != 0 ]]; then
    failing+=("$test");
  fi

  emulator_status=0
  if [ -f "${test%.picoc}.reti" ]; then
    timeout --preserve-status "${MAX_EMULATOR_DURATION_SECONDS}s" reti_emulator $(cat ./opts/test_emu_opts.txt) $4 "${test%.picoc}.reti";
    emulator_status=$?
    if [[ $emulator_status == 124 ]]; then
      echo "Emulator timed out after ${MAX_EMULATOR_DURATION_SECONDS}s for $test"
    fi
  fi

  output_status=0
  if [[ $emulator_status == 0 ]]; then
    diff "${test%.picoc}.expected_output" "${test%.picoc}.output"
    output_status=$?
  else
    output_status=1
  fi

  if [[ $output_status != 0 ]]; then
    not_passed+=("$test");
  fi
  ((num_tests++));
done;
echo "$verification_res" | tee ./sys_tests/tests.res
echo Not failing: $(($num_tests-${#failing[@]})) / $num_tests | tee -a ./sys_tests/tests.res
echo Failing: ${failing[*]} | tee -a ./sys_tests/tests.res
echo Passed: $(($num_tests-${#not_passed[@]})) / $num_tests | tee -a ./sys_tests/tests.res
echo Not passed: ${not_passed[*]} | tee -a ./sys_tests/tests.res

./space_inserter.py

if [[ ${#not_passed[@]} != 0 ]]; then
    exit 1
fi
