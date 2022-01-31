#!/usr/bin/env python

import sys
import global_vars
from compiler import Compiler, remove_extension
from colorama import init
from colormanager import ColorManager as CM


def main():
    compiler = Compiler()

    init(strip=False)

    if not global_vars.args.infile:
        sys.exit(compiler.cmdloop())

    if global_vars.args.color:
        CM().color_on()
    else:
        CM().color_off()

    infile = global_vars.args.infile
    outbase = remove_extension(infile)

    try:
        compiler.read_and_write_file(infile, outbase)
    except FileNotFoundError:
        print("File does not exist\n")
    except:
        print("Compilation unsuccessfull\n")
    else:
        print("Compilation successfull\n")


if __name__ == '__main__':
    main()
