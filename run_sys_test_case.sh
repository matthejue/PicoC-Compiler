#!/usr/bin/env bash

mode="$1"
status_file="$2"
test="$3"
shift 3

MAX_EMULATOR_DURATION_SECONDS=5
reti="${test%.picoc}.reti"
output="${test%.picoc}.output"
expected="${test%.picoc}.expected_output"
# Creates isolated peripheral storage for each emulator process
peripherals_root="/tmp/reti_emulator"
mkdir -p "$peripherals_root" || exit 1
peripherals_dir="$(mktemp -d "$peripherals_root/sys_test.XXXXXX")" || exit 1

cleanup() {
  rm -r -- "$peripherals_dir"
}
trap cleanup EXIT

./heading_subheadings.py "heading" "$test" "${COLUMNS:-120}" "="

rm -f \
  "$reti" \
  "${test%.picoc}.sections" \
  "$output" \
  "${test%.picoc}.error"

compile_status=0

if [[ "$mode" == direct ]]; then
  # The intentional unquoted expansions permit multiple compiler options
  # shellcheck disable=SC2086
  if ! ./run.py $TEST_CPL_OPTIONS $EXTRA_CPL_ARGS --show-input-files \
    --direct-source-link "$test" "$@" -o "$reti"; then
    compile_status=1
  fi
else
  # shellcheck disable=SC2086
  if ! ./run.py $TEST_CPL_OPTIONS $EXTRA_CPL_ARGS --show-input-files \
    "$@" -o "$reti"; then
    compile_status=1
  else
    metadata_file="$(mktemp)"
    sed -nE \
      -e 's@^[[:space:]]*//[[:space:]]*(input|in)[[:space:]]*:[[:space:]]*(.*)$@# input:\2@p' \
      -e 's@^[[:space:]]*//[[:space:]]*(expected|exp)[[:space:]]*:[[:space:]]*(.*)$@# expected:\2@p' \
      -e 's@^[[:space:]]*//[[:space:]]*(datasegment|data)[[:space:]]*:[[:space:]]*(.*)$@# datasegment:\2@p' \
      "$test" > "$metadata_file"
    cat "$reti" >> "$metadata_file"
    mv "$metadata_file" "$reti"
  fi
fi

emulator_status="$compile_status"
timed_out=0

if [[ $compile_status -eq 0 && -f "$reti" ]]; then
  # The intentional unquoted expansion permits multiple emulator options
  # shellcheck disable=SC2086
  timeout \
    "${MAX_EMULATOR_DURATION_SECONDS}s" \
    reti_emulator \
    $TEST_EMU_OPTIONS \
    $EXTRA_EMU_ARGS \
    -f "$peripherals_dir" \
    "$reti"
  emulator_status=$?

  if [[ $emulator_status -eq 124 ]]; then
    timed_out=1
    echo "Test timed out after ${MAX_EMULATOR_DURATION_SECONDS}s: $test"
  fi
fi

output_status=1
if [[ $emulator_status -eq 0 ]]; then
  if diff "$expected" "$output"; then
    output_status=0
  fi
fi

printf '%d %d %d\n' "$compile_status" "$output_status" "$timed_out" > "$status_file"
