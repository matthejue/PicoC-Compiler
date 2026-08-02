#!/usr/bin/env bash

NOT_PASSED_TESTS_FILE="${NOT_PASSED_TESTS_FILE:-./opts/not_passed_tests.txt}"
use_not_passed_tests=false
direct_compile=false

usage() {
  cat <<EOF
Usage:
  $0 [OPTIONS] COLUMNS [TEST_PATTERN] [EXTRA_CPL_ARGS] [EXTRA_EMU_ARGS]

Options:
  --not-passed
      Run only the whitespace-separated test paths listed in:
      ${NOT_PASSED_TESTS_FILE}

      TEST_PATTERN is ignored when this option is active.

  --direct
      Compile each test and its .picoc dependencies directly into the final
      .reti file. The default compiles .reti_blocks and .st files first.

  -h, --help
      Show this help message.

Examples:
  $0 120 all
  $0 120 basic
  $0 --direct 120 basic
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
    --direct)
      direct_compile=true
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

SECONDS=0

paths=()
verify_paths=()

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

if [[ "$use_not_passed_tests" == true ]]; then
  verify_paths=("${paths[@]}")
elif [[ "$test_pattern" == "all" ]]; then
  verify_paths=(./sys_tests/{basic,advanced,example,hard,thesis,tobias,hidden}*.picoc)
else
  verify_paths=("${paths[@]}")
fi

for test in "${paths[@]}"; do
  sed -n '1p' "$test" | sed -e 's/^\/\/ in://' > "${test%.picoc}.input"
  expected="$(sed -n '2p' "$test" | sed -e 's/^\/\/ expected://')"
  printf '%s' "$expected" > "${test%.picoc}.expected_output"
done

result_dir="$(mktemp -d)"
cleanup_result_dir() {
  rm -r "$result_dir"
}
trap cleanup_result_dir EXIT

test_sources="${paths[*]}"
verify_sources="${verify_paths[*]}"
if [[ "$direct_compile" == true ]]; then
  test_build_mode=direct
else
  test_build_mode=staged
fi

export TEST_CPL_OPTIONS
export TEST_EMU_OPTIONS
export EXTRA_CPL_ARGS="$extra_cpl_args"
export EXTRA_EMU_ARGS="$extra_emu_args"
TEST_CPL_OPTIONS="$(< ./opts/test_cpl_opts.txt)"
TEST_EMU_OPTIONS="$(< ./opts/test_emu_opts.txt)"

test_jobs="${TEST_JOBS:-$(nproc)}"
make_status=0
COLUMNS="$columns" make \
  --no-print-directory \
  --output-sync=target \
  --keep-going \
  --jobs "$test_jobs" \
  -f ./sys_tests/Makefile \
  TEST_BUILD_MODE="$test_build_mode" \
  TEST_SOURCES="$test_sources" \
  VERIFY_SOURCES="$verify_sources" \
  RESULT_DIR="$result_dir" \
  all || make_status=$?

num_tests=${#paths[@]}
failing=()
not_passed=()
timed_out=()

for test in "${paths[@]}"; do
  status_file="$result_dir/test/$(basename "${test%.picoc}").status"
  if [[ ! -f "$status_file" ]]; then
    failing+=("$test")
    not_passed+=("$test")
    continue
  fi

  read -r compile_status output_status timeout_status < "$status_file"
  if [[ $compile_status -ne 0 ]]; then
    failing+=("$test")
  fi
  if [[ $output_status -ne 0 ]]; then
    not_passed+=("$test")
  fi
  if [[ $timeout_status -ne 0 ]]; then
    timed_out+=("$test")
  fi
done

not_verified=()
for test in "${verify_paths[@]}"; do
  status_file="$result_dir/verify/$(basename "${test%.picoc}").status"
  if [[ ! -f "$status_file" ]] || [[ "$(< "$status_file")" -ne 0 ]]; then
    not_verified+=("$test")
  fi
done

verification_res="Verified: $((${#verify_paths[@]} - ${#not_verified[@]})) / ${#verify_paths[@]}
Not verified: ${not_verified[*]}"

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

printf 'Runtime: %02d:%02d\n' "$((SECONDS / 60))" "$((SECONDS % 60))" |
  tee -a ./sys_tests/tests.res

echo "Updated test list: $NOT_PASSED_TESTS_FILE"

./space_inserter.py

if [[ $make_status -ne 0 || ${#not_passed[@]} -ne 0 ]]; then
  exit 1
fi
