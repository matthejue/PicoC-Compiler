#!/usr/bin/env bash

i3-msg layout tabbed
alacritty -o font.size=7 -e make test-show TESTNAME=example_bubble_sort PAGES=7
