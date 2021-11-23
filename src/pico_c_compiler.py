#!/usr/bin/env python

# from sys import exit
import argparse
from lexer import Lexer, TT
from grammar import Grammar
from error_handler import ErrorHandler
from symbol_table import SymbolTable
from tabulate import tabulate
import global_vars


def main():
    cli_args_parser = argparse.ArgumentParser(
        description="Compiles Pico-C Code into RETI Code.")
    cli_args_parser.add_argument("infile", nargs='?',
                                 help="input file with Pico-C Code")
    cli_args_parser.add_argument("outfile", nargs='?',
                                 help="output file with RETI Code")
    cli_args_parser.add_argument('-p', '--print', action='store_true',
                                 help="output the file output to the terminal"
                                 " and if --symbol_table is active output the"
                                 " symbol table beneath")
    cli_args_parser.add_argument('-a', '--ast', action='store_true',
                                 help="output the Abstract Syntax Tree "
                                 "instead of RETI Code")
    cli_args_parser.add_argument('-t', '--tokens', action='store_true',
                                 help="output the Tokenlist instead of "
                                 "RETI Code")
    cli_args_parser.add_argument('-s', '--start_data_segment',
                                 help="where the allocation of variables "
                                 "starts (default 100)", type=int, default=100)
    cli_args_parser.add_argument('-e', '--end_data_segment', help="where the "
                                 "stackpointer starts (default 200)", type=int, default=200)
    cli_args_parser.add_argument('-m', '--python_stracktrace_error_message',
                                 action='store_true', help="show python error "
                                 "messages with stacktrace")
    cli_args_parser.add_argument('-S', '--symbol_table', action='store_true',
                                 help="output the final symbol table into "
                                 "a CSV file after the whole Abstract Syntax "
                                 "Tree was visited")
    cli_args_parser.add_argument('-O', '--optimization-level',
                                 help="set the optimiziation level of the "
                                 "compiler (0=save all variables on the "
                                 "stack, 1=use graph coloring to find the "
                                 "best assignment of variables to registers, "
                                 "2=partially interpret expressions) [NOT IMPLEMENTED YET]", type=int, default=0)
    cli_args_parser.add_argument('-b', '--binary', action='store_true',
                                 help="produce binary encoded RETI code [NOT IMPLEMENTED YET]")
    cli_args_parser.add_argument('-P', '--prefix-notation', action='store_true',
                                 help="write Abstract Syntax Tree in prefix notation [NOT IMPLEMENTED YET]")
    cli_args_parser.add_argument('-v', '--verbose', action='store_true',
                                 help="also show tokentypes in the ast, add "
                                 "comments to the RETI Code and show more "
                                 "context around error messages [NOT IMPLEMENTED YET]")
    global_vars.args = cli_args_parser.parse_args()

    if not global_vars.args.infile:
        _shell()

    if global_vars.args.infile:
        infile = global_vars.args.infile

    if global_vars.args.outfile:
        outfile = global_vars.args.outfile
    else:
        outfile = _basename(infile) + ".reti"

    try:
        _read_and_write_file(infile, outfile)
    except FileNotFoundError:
        print("File does not exist")
    else:
        print("Compiled successfully")


def _basename(fname):
    """stips of the file extension
    :fname: filename
    :returns: basename of the file

    """
    index_of_extension = fname.rindex('.')
    return fname[0:index_of_extension]


def _shell():
    """reads pico_c input and prints corresponding reti assembler code
    :returns: None (terminal output of reti assembler code)

    """
    # shell is always executed with print
    global_vars.args.print = True

    while True:
        pico_c_in = input('pico_c > ')

        if pico_c_in in ['quit()', 'exit()']:
            exit(0)
        elif pico_c_in == '':
            continue

        # compile('<stdin>', pico_c_in.split('\n'))
        _compile('<stdin>', [pico_c_in])


def _read_and_write_file(infile, outfile):
    """reads a pico_c file and compiles it
    :returns: pico_c Code compiled in RETI Assembler

    """
    with open(infile, encoding="utf-8") as fin, \
            open(outfile, 'w', encoding="utf-8") as fout:
        pico_c_in = fin.readlines()

        output = _compile(infile, pico_c_in)

        fout.writelines(str(output))

    if global_vars.args.symbol_table:
        outfile = _basename(outfile) + '.csv'
        output = "name,type,position,value\n"
        symbols = SymbolTable().symbols
        for name in symbols.keys():
            if symbols[name].position:
                output += f"{name},{symbols[name].type},"\
                    f"{symbols[name].position[0]}:"\
                    f"{symbols[name].position[1]},"\
                    f"{symbols[name].value}\n"
            else:  # if it is None
                output += f"{name},{symbols[name].type},"\
                    f"{symbols[name].position},{symbols[name].value}\n"
        with open(outfile, 'w', encoding="utf-8") as csv_out:
            csv_out.writelines(output)


def _compile(fname, code):
    # remove all \n from the code
    code_without_cr = list(map(lambda line: line.strip(), code))

    lexer = Lexer(fname, code_without_cr)

    # Deal with --tokens option
    if global_vars.args.tokens:
        tokens = []
        t = lexer.next_token()
        while t.type != TT.EOF:
            tokens += [t]
            t = lexer.next_token()

        if global_vars.args.print:
            print(tokens)

        return tokens

    # Generate ast
    grammar = Grammar(lexer)
    # Handle errors
    error_handler = ErrorHandler(grammar)
    # Assignment grammar needs 2 num_lts for <va>
    error_handler.handle(grammar.start_parse)

    # Deal with --ast option
    if global_vars.args.ast:
        if global_vars.args.print:
            print(grammar.reveal_ast())
        return grammar.reveal_ast()

    abstract_syntax_tree = grammar.reveal_ast()
    error_handler.handle(abstract_syntax_tree.visit)

    # Deal with --print and --symbol_table options
    if global_vars.args.print:
        print(abstract_syntax_tree.show_generated_code())
    if global_vars.args.symbol_table:
        header = ["name", "type", "position", "value"]
        symbols = SymbolTable().symbols
        print(tabulate([(k, str(v.type), str(v.position), str(v.value))
              for k, v in symbols.items()], headers=header))

    return abstract_syntax_tree.show_generated_code()


if __name__ == '__main__':
    main()
