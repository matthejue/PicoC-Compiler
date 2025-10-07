#!/home/areo/Documents/Studium/PicoC-Compiler/.virtualenv/bin/python

import sys
import global_vars
from option_handler import OptionHandler, _open_documentation
from util_funs import only_keep_path, basename
import traceback


def main():
    if set(["-h", "--help"]).intersection(sys.argv):
        _open_documentation()
        return

    compiler = OptionHandler()

    global_vars.path = only_keep_path(global_vars.args.infile)
    global_vars.basename = basename(global_vars.args.infile)

    try:
        compiler.read_and_write_file()
    except FileNotFoundError:
        print("File does not exist")
        if global_vars.args.traceback:
            traceback.print_exc()
    else:
        print("\nCompilation successfull\n")


if __name__ == "__main__":
    main()
