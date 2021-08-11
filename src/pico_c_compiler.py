#!/usr/bin/env python

# from sys import exit
import argparse
from src.lexer import Lexer, TT
from src.grammar import Grammar
from src import globals


def main():
    cli_args_parser = argparse.ArgumentParser(
        description="Compiles Pico-C Code into RETI Code.")
    cli_args_parser.add_argument("infile", nargs='?',
                                 help="Input file with Pico-C Code")
    cli_args_parser.add_argument("outfile", nargs='?',
                                 help="Output file with RETI Code")
    cli_args_parser.add_argument('-p', '--print', action='store_true',
                                 help="Also output the file output to \
                                 the terminal")
    cli_args_parser.add_argument('-a', '--ast', action='store_true',
                                 help="Output the Abstract Syntax Tree \
                                 instead of RETI Code")
    cli_args_parser.add_argument('-t', '--tokens', action='store_true',
                                 help="Output the Tokenlist instead of \
                                 RETI Code")
    cli_args_parser.add_argument('-v', '--verbose', action='store_true',
                                 help="Create verbose output for the ast")

    globals.args = cli_args_parser.parse_args()

    if not globals.args.infile:
        _shell()

    if globals.args.infile:
        infile = globals.args.infile

    if globals.args.outfile:
        outfile = globals.args.outfile
    else:
        outfile = _basename(infile) + ".reti"

    try:
        _read_file(infile, outfile)
    except FileNotFoundError:
        print("File does not exist")
    else:
        print("Compiled successfully")


def _basename(fname):
    """stips of the file extension
    :fname: filename
    :returns: basename of the file

    """
    index_of_extension = fname.index(".")
    return fname[0:index_of_extension]


def _shell():
    """reads pico_c input and prints corresponding reti assembler code
    :returns: None (terminal output of reti assembler code)

    """
    # shell is always executed with print
    globals.args.print = True

    while True:
        pico_c_in = input('pico_c > ')

        if pico_c_in in ['quit()', 'exit()']:
            exit(0)
        elif pico_c_in == '':
            continue

        # compile('<stdin>', pico_c_in.split('\n'))
        _compile('<stdin>', [pico_c_in])


def _read_file(infile, outfile):
    """reads a pico_c file and compiles it
    :returns: pico_c Code compiled in RETI Assembler

    """
    with open(infile, encoding="utf-8") as fin, \
            open(outfile, 'w', encoding="utf-8") as fout:
        pico_c_in = fin.readlines()[0]
        # TODO: remove temporary solution to only read first line

        output = _compile(infile, [pico_c_in])

        fout.writelines(str(output))


def _compile(fname, code):
    # remove all \n from the code
    code_without_cr = list(map(lambda line: line.strip(), code))[0]
    # TODO: remove temporary solution to only read first line

    lexer = Lexer(fname, code_without_cr)

    # Deal with --tokens option
    if globals.args.tokens:
        tokens = []
        t = lexer.next_token()
        while t.type != TT.EOF:
            tokens += [t]
            t = lexer.next_token()

        if globals.args.print:
            print(tokens)

        return tokens

    # Generate ast
    grammar = Grammar(lexer)
    # Assignment grammar needs 2 num_lts for <va>
    grammar.start_parse()

    # Deal with --ast option
    if globals.args.ast:
        if globals.args.print:
            print(grammar.reveal_ast())
        return grammar.reveal_ast()

    # TODO: CodeGenerator belongs here

    # Deal with print option
    if globals.args.print:
        print("Placeholder for RETI Code")

    return "Placeholder for RETI Code", None


if __name__ == '__main__':
    main()
