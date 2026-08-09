#!/usr/bin/env bash
git tag -d $1
git push github --delete $1
git tag -a $1 -m "$2"
git push github $1
