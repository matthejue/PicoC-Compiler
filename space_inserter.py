#!/usr/bin/env python

import os


def remove_ext(fname):
    # if there's no '.' rindex raises a exception, rfind returns -1
    index_of_extension_start = fname.rfind(" no spaces.")
    if index_of_extension_start == -1:
        return fname
    return fname[0:index_of_extension_start]


def _remove_path(fname):
    index_of_path_end = fname.rfind("/")
    if index_of_path_end == -1:
        return fname
    return fname[index_of_path_end + 1 :]


def filename_without_ext(fname):
    fname = remove_ext(fname)
    return _remove_path(fname)


def only_keep_path(fname):
    index_of_path_end = fname.rfind("/")
    if index_of_path_end == -1:
        return "./"
    return fname[: index_of_path_end + 1]


PATTERN = r"_no_spaces.picoc"

filenames = [f for f in os.listdir("./test") if f.endswith(PATTERN)]

for filename in filenames:
    filename_copy = filename.replace("_", " ")


    os.rename(
        "./test/" + filename, "./test/" + remove_ext(filename_copy) + ".picoc"
    )
