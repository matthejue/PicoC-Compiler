#!/usr/bin/env bash

NOT_PASSED_TESTS_FILE="./opts/not_passed_tests.txt"
use_not_passed_tests=false

usage() {
  cat <<EOF
Usage:
  $0 [OPTIONS] COLUMNS [TEST_PATTERN] [EXTRA_CPL_ARGS] [EXTRA_EMU_ARGS]

Options:
  --not-passed
      Run only the whitespace-separated test paths listed in:
      ${NOT_PASSED_TESTS_FILE}

      TEST_PATTERN is ignored when this option is active.

  -h, --help
      Show this help message.

Examples:
  $0 120 all
  $0 120 basic
  $0 --not-passed 120

After the test run, all tests that did not pass are written as
whitespace-separated paths to:
  ${NOT_PASSED_TESTS_FILE}
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --not-passed)
      use_not_passed_tests=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    *)
      break
      ;;
  esac
done

if [[ $# -lt 1 ]]; then
  echo "Error: COLUMNS argument is required." >&2
  usage >&2
  exit 2
fi

columns="$1"
test_pattern="${2:-}"
extra_cpl_args="${3:-}"
extra_emu_args="${4:-}"

cleanup() {
  echo "Termination signal received. Cleaning up..."
  ./space_inserter.py
  exit 1
}

trap cleanup SIGINT

MAX_EMULATOR_DURATION_SECONDS=5

paths=()

if [[ "$use_not_passed_tests" == true ]]; then
  if [[ ! -f "$NOT_PASSED_TESTS_FILE" ]]; then
    echo "Test list file not found: $NOT_PASSED_TESTS_FILE" >&2
    exit 1
  fi

  mapfile -t paths < <(
    tr -s '[:space:]' '\n' < "$NOT_PASSED_TESTS_FILE" |
      sed '/^[[:space:]]*$/d'
  )
elif [[ "$test_pattern" == "all" ]]; then
  paths=(./sys_tests/*.picoc)
elif [[ -n "$test_pattern" ]]; then
  paths=(./sys_tests/*"$test_pattern"*.picoc)
else
  paths=(./sys_tests/{basic,advanced,example,hard,thesis,tobias}*.picoc)
fi

if [[ ${#paths[@]} -eq 0 ]]; then
  echo "No test paths were found." >&2
  exit 1
fi

for test in "${paths[@]}"; do
  if [[ ! -f "$test" ]]; then
    echo "Test file not found: $test" >&2
    exit 1
  fi
done

./space_replacer.py

verification_results=()

if [[ "$use_not_passed_tests" == true ]]; then
  # The helper scripts accept a test pattern rather than a list of paths.
  # Run them once per listed test using the exact filename without .picoc.
  for test in "${paths[@]}"; do
    exact_test_pattern="$(basename "${test%.picoc}")"

    ./extract_input_and_expected.sh "$exact_test_pattern"
    verification_results+=(
      "$(./verify_tests.sh "$columns" "$exact_test_pattern")"
    )
  done

  verification_res="$(printf '%s\n' "${verification_results[@]}")"
else
  ./extract_input_and_expected.sh "$test_pattern"
  verification_res="$(./verify_tests.sh "$columns" "$test_pattern")"
fi

num_tests=0
failing=()
not_passed=()
timed_out=()

for test in "${paths[@]}"; do
  ./heading_subheadings.py "heading" "$test" "$columns" "="

  # The intentional unquoted expansion permits multiple options in the
  # option files and EXTRA_CPL_ARGS.
  # shellcheck disable=SC2046,SC2086
  ./run.py $(cat ./opts/test_cpl_opts.txt) $extra_cpl_args \
    "$test" -o "${test%.picoc}.reti"

  compile_status=$?

  if [[ $compile_status -ne 0 ]]; then
    failing+=("$test")
  fi

  emulator_status=0

  if [[ -f "${test%.picoc}.reti" ]]; then
    # shellcheck disable=SC2046,SC2086
    timeout \
      "${MAX_EMULATOR_DURATION_SECONDS}s" \
      reti_emulator \
      $(cat ./opts/test_emu_opts.txt) \
      $extra_emu_args \
      "${test%.picoc}.reti"

    emulator_status=$?

    if [[ $emulator_status -eq 124 ]]; then
      timed_out+=("$test")
      echo "Test timed out after ${MAX_EMULATOR_DURATION_SECONDS}s: $test"
    fi
  fi

  output_status=0

  if [[ $emulator_status -eq 0 ]]; then
    diff \
      "${test%.picoc}.expected_output" \
      "${test%.picoc}.output"

    output_status=$?
  else
    output_status=1
  fi

  if [[ $output_status -ne 0 ]]; then
    not_passed+=("$test")
  fi

  ((num_tests++))
done

# Overwrite the test list with the tests that failed during this run.
# The paths are written on one line and separated by spaces.
if [[ ${#not_passed[@]} -eq 0 ]]; then
  : > "$NOT_PASSED_TESTS_FILE"
else
  (
    IFS=' '
    printf '%s\n' "${not_passed[*]}"
  ) > "$NOT_PASSED_TESTS_FILE"
fi

echo "$verification_res" |
  tee ./sys_tests/tests.res

echo "Not failing: $((num_tests - ${#failing[@]})) / $num_tests" |
  tee -a ./sys_tests/tests.res

echo "Failing: ${failing[*]}" |
  tee -a ./sys_tests/tests.res

echo "Passed: $((num_tests - ${#not_passed[@]})) / $num_tests" |
  tee -a ./sys_tests/tests.res

echo "Not passed: ${not_passed[*]}" |
  tee -a ./sys_tests/tests.res

echo "Timed out: ${#timed_out[@]} / $num_tests" |
  tee -a ./sys_tests/tests.res

echo "Timed-out tests: ${timed_out[*]}" |
  tee -a ./sys_tests/tests.res

echo "Updated test list: $NOT_PASSED_TESTS_FILE"

./space_inserter.py

if [[ ${#not_passed[@]} -ne 0 ]]; then
  exit 1
fi
