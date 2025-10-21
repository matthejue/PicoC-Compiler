#!/home/areo/Documents/Studium/PicoC-Compiler/.virtualenv/bin/python

import sys
from option_handler import OptionHandler, _open_documentation
from util_funs import remove_filename, filename_without_ext, remove_ext


def main():
    if set(["-h", "--help"]).intersection(sys.argv):
        _open_documentation()
        return

    compiler = OptionHandler()
    compiler.build_all()
    print("\nCompilation successfull\n")


if __name__ == "__main__":
    main()
