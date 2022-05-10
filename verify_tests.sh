#!/usr/bin/env bash

./convert_to_c.py

shopt -s extglob

./heading_subheadings.py "heading" "Verification" "$1" "="
num_tests=0;
not_verified=();
  for test in ./tests/!(error*|exclude*).c; do
  echo $test
  gcc -Wno-incompatible-pointer-types $test
  ./a.out | sed -e 's/^ //' | sed 's/$/\n/' > "${test%.c}.c_out"
  diff "${test%.c}.out_expected" "${test%.c}.c_out"
  if [[ $? != 0 ]]; then
    not_verified+=("$test");
  fi
  ((num_tests++));
done
./heading_subheadings.py "heading" "Results" "$1" "="
echo Verified: $(($num_tests-${#not_verified[@]})) / $num_tests;
echo Not verified: ${not_verified[*]};
rm ./a.out
