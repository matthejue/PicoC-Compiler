#!/usr/bin/env python

import sys
import global_vars
from compiler import Compiler, remove_extension
from colorama import init

# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL


def main():
    if len(sys.argv) > 1:
        global_vars.shell_on = False

    compiler = Compiler()

    if global_vars.args.color:
        init(strip=False)
    else:
        init(strip=True)

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
