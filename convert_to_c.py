#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os


def find_all_paths(pattern, from_start):
    if from_start:
        return map(
            lambda file: f"./tests/{file}",
            filter(
                lambda file: any([file.startswith(ptrn) for ptrn in pattern]),
                os.listdir(os.curdir + "/tests/"),
            ),
        )
    else:
        return map(
            lambda file: f"./tests/{file}",
            filter(
                lambda file: any([ptrn in file for ptrn in pattern]),
                os.listdir(os.curdir + "/tests/"),
            ),
        )


def main():
    if len(sys.argv) == 1 or sys.argv[1] == "default":
        pattern = ["basic", "advanced", "example", "hard"]
        paths = find_all_paths(pattern, from_start=True)
    elif sys.argv[1] == "all":
        pattern = ["basic", "advanced", "example", "hard", "hidden"]
        paths = find_all_paths(pattern, from_start=True)
    else:
        pattern = [sys.argv[1]]
        paths = find_all_paths(pattern, from_start=False)

    for filepath in paths:
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
