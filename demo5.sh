#!/usr/bin/env bash

i3-msg layout tabbed
alacritty -o font.size=6.5 -e make test-show TESTNAME=example_bsearch_rec PAGES=8
