#!/usr/bin/env bash

i3-msg layout tabbed
alacritty -o font.size=6 -e make test-show TESTNAME=example_min_sort PAGES=8
