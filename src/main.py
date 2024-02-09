#!/home/areo/Documents/Studium/PicoC-Compiler/.virtualenv/bin/python

import sys
import global_vars
from option_handler import OptionHandler, _open_documentation
from util_funs import only_keep_path, basename
from colorama import init
from colormanager import ColorManager as CM
import traceback


def main():
    if set(["-h", "--help"]).intersection(sys.argv):
        _open_documentation()
        return

    init(strip=False)

    compiler = OptionHandler()

    if not global_vars.args.infile and sys.stdin.isatty():
        sys.exit(compiler.cmdloop())

    if global_vars.args.color:
        CM().color_on()
    else:
        CM().color_off()

    if not sys.stdin.isatty():
        sys.exit(compiler.read_stdin())

    global_vars.path = only_keep_path(global_vars.args.infile)
    global_vars.basename = basename(global_vars.args.infile)

    try:
        compiler.read_and_write_file()
    except FileNotFoundError:
        print("File does not exist")
        if global_vars.args.traceback:
            traceback.print_exc()
    else:
        compiler._success_message()


if __name__ == "__main__":
    main()
