#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import global_vars

with open(global_vars.outbase + ".tokens", "r", encoding="utf-8") as fin:
    picoc_input = fin.read()
