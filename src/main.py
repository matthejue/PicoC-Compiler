#!/usr/bin/env python

import sys
import global_vars
from compiler import Compiler, remove_extension


def main():
    if len(sys.argv) > 0:
        global_vars.shell_on = False

    compiler = Compiler()

    if not global_vars.args.infile:
        sys.exit(compiler.cmdloop())
    else:
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
