#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os


def main():
    filename = sys.argv[1]
    with open(remove_extension(filename) + ".picoc", "r", encoding="utf-8") as picoc_file:
        picoc_input = picoc_file.readlines()
        almost_c_input = picoc_input.replace("print(", 'printf(" %f", ')
        with open(remove_extension(filename) + ".picoc", "r", encoding="utf-8") as fin:



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
