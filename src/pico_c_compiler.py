#!/usr/bin/env python

from sys import exit
from lexer import Lexer, TT
from arithmetic_expression_grammer import ArithmeticExpressionGrammer
import argparse

###############################################################################
#                              Gloabel Variables                              #
###############################################################################

args = None

###############################################################################
#                                    Main                                     #
###############################################################################


# def basename(fname):
# """stips of the file extension
# :fname: filename
# :returns: basename of the file

# """
# index_of_extension = fname.index(".")
# return fname[0:index_of_extension]


def main():
    cli_args_parser = argparse.ArgumentParser(
        description="Compiles Pico-C Code into RETI Code.")
    cli_args_parser.add_argument("infile", nargs='?',
                                 help="Input file with Pico-C Code")
    cli_args_parser.add_argument("outfile", nargs='?',
                                 help="Output file with RETI Code")
    cli_args_parser.add_argument('-p', '--print', action='store_true',
                                 help="Print the file output also out \
                                 to the terminal")
    cli_args_parser.add_argument('-a', '--ast', action='store_true',
                                 help="Output the Abstract Syntax Tree \
                                 instead of RETI Code")
    cli_args_parser.add_argument('-t', '--tokens', action='store_true',
                                 help="Output the Tokenlist instead of \
                                 RETI Code")

    global args
    args = cli_args_parser.parse_args()

    if not args.infile:
        shell()

    # if args.infile:
        # infile = args.infile

    # if args.outfile:
        # outfile = args.outfile
    # else:
        # outfile = basename(infile) + ".reti"

    # try:
        # read_file(infile, outfile)
    # except FileNotFoundError:
        # print("File does not exist")
    # else:
        # print("Compiled successfully")

###############################################################################
#                                    Shell                                    #
###############################################################################


def shell():
    """reads pico_c input and prints corresponding reti assembler code
    :returns: None (terminal output of reti assembler code)

    """
    # shell is always executed with print
    global args
    args.print = True

    while True:
        pico_c_in = input('pico_c > ')

        if pico_c_in in ['quit()', 'exit()']:
            exit(0)
        elif pico_c_in == '':
            continue

        # compile('<stdin>', pico_c_in.split('\n'))
        compile('<stdin>', pico_c_in)

###############################################################################
#                                  Read File                                  #
###############################################################################


# def read_file(infile, outfile):
    # """reads a pico_c file and compiles it
    # :returns: pico_c Code compiled in RETI Assembler

    # """
    # with open(infile, encoding="utf-8") as fin, \
        # open(outfile, 'w', encoding="utf-8") as fout:
        # pico_c_in = fin.readlines()

        # output, error = compile(infile, pico_c_in)

        # if error:
        # exit(1)

        # fout.writelines(str(output))

###############################################################################
#                                   Compile                                   #
###############################################################################


def compile(fname, code):
    # remove any \n from the code
    # code_without_cr = list(map(lambda line: line.strip(), code))

    # Generate tokens
    # lexer = Lexer(fname, code_without_cr)
    lexer = Lexer(fname, code)

    # Deal with --tokens option
    global args
    if args.tokens:
        tokens = []
        t = lexer.next_token()
        while t.type != TT.EOF:
            tokens += [t]
            t = lexer.next_token()

        if args.print:
            print(tokens)

        return tokens

    # Generate ast
    parser = ArithmeticExpressionGrammer(lexer, 1)
    parser.code_ae()

    # # Deal with --ast option
    # if args.ast:
    # if args.print:
    # print(syntax_tree_rootnode)
    # return syntax_tree_rootnode, None

    # # TODO: CodeGenerator belongs here

    # # Deal with print option
    # if args.print:
    # print("Placeholder for RETI Code")

    # return "Placeholder for RETI Code", None


if __name__ == '__main__':
    main()
