#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os


def main():
    for filepath in map(
        lambda file: f"./tests/{file}", os.listdir(os.curdir + "/tests/")
    ):
        basename = remove_extension(filepath)
        with open(basename + ".picoc", "r", encoding="utf-8") as picoc_file:
            picoc_input = picoc_file.read()
        almost_c = picoc_input.replace("print(", 'printf(" %d", ')
        with open(basename + ".in", "r", encoding="utf-8") as input_file:
            inputs = input_file.read().replace("\n", "").split(" ")
        while inputs:
            almost_c = almost_c.replace("input()", inputs.pop(0), 1)
        finally_c = almost_c.split("\n")
        finally_c.insert(2, "#include<stdio.h>")
        with open(basename + ".c", "w", encoding="utf-8") as c_file:
            for line in finally_c:
                c_file.write(line + "\n")


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
