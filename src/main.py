#!/usr/bin/env python

from sys import exit
import global_vars
from compiler import Compiler, remove_extension


def main():
    compiler = Compiler()

    if not global_vars.args.infile:
        global_vars.args.print = True
        exit(compiler.cmdloop())
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
