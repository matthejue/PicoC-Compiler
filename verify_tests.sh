#!/usr/bin/env bash

shopt -s extglob

./heading_subheadings.py "heading" "Verification" "$1" "="
num_tests=0;
not_verified=();

if [[ $2 == "all" ]]; then
  paths+=(./sys_tests/{basic,advanced,example,hard,thesis,tobias,hidden}*.c)
elif [[ -n "$2" ]]; then
  paths=(./sys_tests/*$2*.c)
else
  paths+=(./sys_tests/{basic,advanced,example,hard,thesis,tobias}*.c)
fi

for test in "${paths[@]}"; do
  echo $test
  gcc -Wno-incompatible-pointer-types $test
  # ./a.out | sed -e 's/^ //' | sed 's/$/\n/' > "${test%.c}.c_output"
  ./a.out | sed -e 's/^ //' | sed 's/$/ /' > "${test%.c}.c_output"
  diff "${test%.c}.expected_output" "${test%.c}.c_output"
  if [[ $? != 0 ]]; then
    not_verified+=("$test");
  fi
  ((num_tests++));
  rm ./a.out
done
./heading_subheadings.py "heading" "Results" "$1" "="
echo Verified: $(($num_tests-${#not_verified[@]})) / $num_tests;
echo Not verified: ${not_verified[*]};
