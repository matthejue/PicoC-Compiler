#!/usr/bin/env python

import os


def remove_extension(fname):
    # if there's no '.' rindex raises a exception, rfind returns -1
    index_of_extension_start = fname.rfind(".")
    if index_of_extension_start == -1:
        return fname
    return fname[0:index_of_extension_start]


def _remove_path(fname):
    index_of_path_end = fname.rfind("/")
    if index_of_path_end == -1:
        return fname
    return fname[index_of_path_end + 1 :]


def basename(fname):
    fname = remove_extension(fname)
    return _remove_path(fname)


def only_keep_path(fname):
    index_of_path_end = fname.rfind("/")
    if index_of_path_end == -1:
        return "./"
    return fname[: index_of_path_end + 1]


filenames = [
    f for f in os.listdir("./tests") if f.endswith(".picoc") and f.find(" ") != -1
]

for filename in filenames:
    filename_copy = filename.replace(" ", "_")

    os.rename(
        "./tests/" + filename,
        "./tests/" + remove_extension(filename_copy) + "_no_spaces.picoc",
    )
