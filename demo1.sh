#!/usr/bin/env bash

i3-msg layout tabbed
alacritty -o font.size=7 -e make test-show TESTNAME=example_fib_efficient PAGES=7
