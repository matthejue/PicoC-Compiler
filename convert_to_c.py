#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os


def main():
    basename = remove_extension(sys.argv[1])
    with open(basename + ".picoc", "r", encoding="utf-8") as picoc_file:
        picoc_input = picoc_file.read()
    almost_c = picoc_input.replace("print(", 'printf(" %f", ')
    with open(basename + ".in", "r", encoding="utf-8") as input_file:
        inputs = reversed(input_file.read().split(" "))
    while inputs:
        almost_c = almost_c.replace("input()", next(inputs), 1)
    almost_c.split("\n").insert(2, "#include<stdio.h>\n")
    finally_c = almost_c
    with open(basename + ".c", "r", encoding="utf-8") as c_file:
        for line in finally_c:
            c_file.write(line)


def remove_extension(fname):
    """stips of the file extension
    :fname: filename
    :returns: basename of the file

    """
    # if there's no '.' rindex raises a exception, rfind returns -1
    index_of_extension_start = fname.rfind(".")
    if index_of_extension_start == -1:
        return fname
    return fname[0:index_of_extension_start]


if __name__ == "__main__":
    main()
