#!/usr/bin/env bash

shopt -s extglob

./heading_subheadings.py "heading" "Verification" "${1:-72}" "="
num_tests=0;
not_verified=();
tmp_c_file=""

cleanup() {
  if [[ -n "$tmp_c_file" && -f "$tmp_c_file" ]]; then
    rm -f "$tmp_c_file"
  fi
}

trap cleanup EXIT

if [[ $2 == "all" ]]; then
  paths+=(./sys_tests/{basic,advanced,example,hard,thesis,tobias,hidden}*.c)
elif [[ -n "$2" ]]; then
  paths=(./sys_tests/*$2*.c)
else
  paths+=(./sys_tests/{basic,advanced,example,hard,thesis,tobias}*.c)
fi

for test in "${paths[@]}"; do
  echo $test
  tmp_c_file=$(mktemp --suffix=.c)
  sed '/#include "\.\.\/\.\.\/Pico-OS\/lib\/stdio\/stdio\.header"/d' "$test" > "$tmp_c_file"
  sed -i '/^[[:space:]]*debug;[[:space:]]*$/d' "$tmp_c_file"
  gcc -Wno-incompatible-pointer-types "$tmp_c_file"
  input_file="${test%.c}.input"
  if [[ -f "$input_file" ]]; then
    ./a.out < "$input_file" | sed -e 's/^ *//' -e 's/ *$//' > "${test%.c}.c_output"
  else
    ./a.out | sed -e 's/^ *//' -e 's/ *$//' > "${test%.c}.c_output"
  fi
  diff <(sed -e 's/^ *//' -e 's/ *$//' "${test%.c}.expected_output") "${test%.c}.c_output"
  if [[ $? != 0 ]]; then
    not_verified+=("$test");
  fi
  ((num_tests++));
  rm ./a.out
done
./heading_subheadings.py "heading" "Results" "${1:-72}" "="
echo Verified: $(($num_tests-${#not_verified[@]})) / $num_tests;
echo Not verified: ${not_verified[*]};
