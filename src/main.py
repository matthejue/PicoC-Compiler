#!/usr/bin/env python

import sys
import global_vars
from option_handler import OptionHandler, _open_documentation
from global_funs import only_keep_path, basename
import global_vars
from colorama import init
from colormanager import ColorManager as CM
import traceback


def main():
    if set(["-h", "--help"]).intersection(sys.argv):
        _open_documentation()
        return

    init(strip=False)

    compiler = OptionHandler()

    if not global_vars.args.infile:
        sys.exit(compiler.cmdloop())

    if global_vars.args.color:
        CM().color_on()
    else:
        CM().color_off()

    global_vars.path = only_keep_path(global_vars.args.infile)
    global_vars.basename = basename(global_vars.args.infile)

    try:
        compiler.read_and_write_file()
    except FileNotFoundError:
        print("File does not exist")
        if global_vars.args.traceback:
            traceback.print_exc()
    else:
        if global_vars.args.run:
            match global_vars.extension:
                case "reti":
                    print(
                        f"\n{CM().BRIGHT}{CM().WHITE}Interpretation successfull{CM().RESET}{CM().RESET_ALL}\n"
                    )
                case _:
                    print(
                        f"\n{CM().BRIGHT}{CM().WHITE}Compilation and Interpretation successfull{CM().RESET}{CM().RESET_ALL}\n"
                    )
        else:
            match global_vars.extension:
                case "picoc":
                    print(
                        f"\n{CM().BRIGHT}{CM().WHITE}Compilation successfull{CM().RESET}{CM().RESET_ALL}\n"
                    )
                case "reti":
                    print(
                        f"\n{CM().BRIGHT}{CM().WHITE}Interpretation successfull{CM().RESET}{CM().RESET_ALL}\n"
                    )


if __name__ == "__main__":
    main()
