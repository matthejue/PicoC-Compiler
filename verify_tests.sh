#!/usr/bin/env bash

shopt -s extglob

./heading_subheadings.py "heading" "Verification" "$1" "="
num_tests=0;
not_verified=();

if [[ $2 == "all" ]]; then
  # paths=(./tests/!(error*|exclude*).c)
  paths+=(./tests/{basic,advanced,example,hard,thesis,tobias,hidden}*.c)
elif [[ -n "$2" ]]; then
  paths=(./tests/*$2*.c)
elif [[ $2 == "default" ]]; then
  paths+=(./tests/{basic,advanced,example,hard,thesis,tobias}*.c)
else
  paths+=(./tests/{basic,advanced,example,hard,thesis,tobias}*.c)
fi

for test in "${paths[@]}"; do
  echo $test
  gcc -Wno-incompatible-pointer-types $test
  ./a.out | sed -e 's/^ //' | sed 's/$/\n/' > "${test%.c}.c_out"
  diff "${test%.c}.out_expected" "${test%.c}.c_out"
  if [[ $? != 0 ]]; then
    not_verified+=("$test");
  fi
  ((num_tests++));
  rm ./a.out
done
./heading_subheadings.py "heading" "Results" "$1" "="
echo Verified: $(($num_tests-${#not_verified[@]})) / $num_tests;
echo Not verified: ${not_verified[*]};
