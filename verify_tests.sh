#!/usr/bin/env bash

shopt -s extglob nullglob

./heading_subheadings.py "heading" "Verification" "${1:-72}" "="
num_tests=0;
not_verified=();
tmp_c_file=""
tmp_exe_file=""

cleanup() {
  if [[ -n "$tmp_c_file" && -f "$tmp_c_file" ]]; then
    rm -f "$tmp_c_file"
  fi
  if [[ -n "$tmp_exe_file" && -f "$tmp_exe_file" ]]; then
    rm -f "$tmp_exe_file"
  fi
}

trap cleanup EXIT

if [[ $2 == "all" ]]; then
  paths+=(./test/{basic,advanced,example,hard,thesis,tobias,hidden}*.picoc)
elif [[ -n "$2" ]]; then
  paths=(./test/*$2*.picoc)
else
  paths+=(./test/{basic,advanced,example,hard,thesis,tobias}*.picoc)
fi

for test in "${paths[@]}"; do
  echo $test
  tmp_c_file=$(mktemp --suffix=.c)
  tmp_exe_file=$(mktemp)
  {
    printf '#include <stdio.h>\n'
    sed '/#include "\.\.\/\.\.\/Pico-OS\/library\/[^"]*\.header"/d' "$test"
  } > "$tmp_c_file"
  sed -i '/^[[:space:]]*debug;[[:space:]]*$/d' "$tmp_c_file"
  if ! gcc -iquote "$(dirname "$test")" -Wno-incompatible-pointer-types "$tmp_c_file" -o "$tmp_exe_file"; then
    not_verified+=("$test");
    ((num_tests++));
    rm -f "$tmp_c_file" "$tmp_exe_file"
    tmp_c_file=""
    tmp_exe_file=""
    continue
  fi
  input_file="${test%.picoc}.input"
  if [[ -f "$input_file" ]]; then
    "$tmp_exe_file" < "$input_file" | sed -e 's/^ *//' -e 's/ *$//' > "${test%.picoc}.c_output"
  else
    "$tmp_exe_file" | sed -e 's/^ *//' -e 's/ *$//' > "${test%.picoc}.c_output"
  fi
  diff <(sed -e 's/^ *//' -e 's/ *$//' "${test%.picoc}.expected_output") "${test%.picoc}.c_output"
  if [[ $? != 0 ]]; then
    not_verified+=("$test");
  fi
  ((num_tests++));
  rm -f "$tmp_c_file" "$tmp_exe_file"
  tmp_c_file=""
  tmp_exe_file=""
done
./heading_subheadings.py "heading" "Results" "${1:-72}" "="
echo Verified: $(($num_tests-${#not_verified[@]})) / $num_tests;
echo Not verified: ${not_verified[*]};
