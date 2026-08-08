#!/usr/bin/env bash

status_file="$1"
test="$2"
tmp_c_file="$(mktemp --suffix=.c)"
tmp_exe_file="$(mktemp)"

cleanup() {
  rm -f "$tmp_c_file" "$tmp_exe_file"
}

trap cleanup EXIT

{
  printf '#include <stdio.h>\n'
  sed '/#include "\.\.\/\.\.\/Pico-OS\/library\/[^"]*\.header"/d' "$test"
} > "$tmp_c_file"
sed -i '/^[[:space:]]*debug;[[:space:]]*$/d' "$tmp_c_file"

verified=0
if ! gcc -iquote "$(dirname "$test")" -Wno-incompatible-pointer-types "$tmp_c_file" -o "$tmp_exe_file"; then
  verified=1
else
  input_file="${test%.picoc}.input"
  if [[ -f "$input_file" ]]; then
    "$tmp_exe_file" < "$input_file" |
      sed -e 's/^ *//' -e 's/ *$//' > "${test%.picoc}.c_output"
  else
    "$tmp_exe_file" |
      sed -e 's/^ *//' -e 's/ *$//' > "${test%.picoc}.c_output"
  fi

  if ! diff \
    <(sed -e 's/^ *//' -e 's/ *$//' "${test%.picoc}.expected_output") \
    "${test%.picoc}.c_output"; then
    verified=1
  fi
fi

printf '%d\n' "$verified" > "$status_file"
