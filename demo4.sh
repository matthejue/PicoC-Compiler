#!/usr/bin/env bash

i3-msg layout tabbed
alacritty -o font.size=10 -e make test-show TESTNAME=example_faculty_rec PAGES=5
