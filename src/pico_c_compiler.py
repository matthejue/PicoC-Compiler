#!/usr/bin/env python

from sys import exit
import argparse
from lexer import Lexer, TT
from grammar import Grammar
from error_handler import ErrorHandler
from symbol_table import SymbolTable
from tabulate import tabulate
import global_vars


def main():
    description = """
    Compiles Pico-C Code into RETI Code.
    PicoC is a subset of C including while loops, if and else statements,
    assignments, arithmetic and logic expressions.
    Please keep in mind that all statements have to be enclosed in a

    void main() { /* your program */ }

    main function.

    If called without arguments, a shell is going to open up where you can type
    PicoC-Code in. The shell can be exited again by typing in exit() or quit().

    If you discover any bugs I would be very grateful if you could report it
    via email to juergmatth@gmail.com, attaching the malicious code to the
    email. ^_^
    """
    cli_args_parser = argparse.ArgumentParser(description=description)
    cli_args_parser.add_argument("infile",
                                 nargs='?',
                                 help="input file with pico-c code")
    cli_args_parser.add_argument('-p',
                                 '--print',
                                 action='store_true',
                                 help="print all file outputs to the terminal")
    cli_args_parser.add_argument(
        '-c',
        '--concrete-syntax',
        action='store_true',
        help="also print the concrete syntax(=content of input file)."
        "The --print option must be active")
    cli_args_parser.add_argument('-t',
                                 '--tokens',
                                 action='store_true',
                                 help="also write the tokenlist")
    cli_args_parser.add_argument('-a',
                                 '--abstract-syntax',
                                 action='store_true',
                                 help="also write the abstract syntax")
    cli_args_parser.add_argument(
        '-S',
        '--symbol_table',
        action='store_true',
        help="also write the final symbol table into a CSV file")
    cli_args_parser.add_argument(
        '-s',
        '--start_data_segment',
        help="where the datasegment starts (default 100)",
        type=int,
        default=100)
    cli_args_parser.add_argument(
        '-e',
        '--end_data_segment',
        help="where the "
        "datasegment ends and where the stackpointer starts (default 200)",
        type=int,
        default=200)
    cli_args_parser.add_argument(
        '-m',
        '--python_stracktrace_error_message',
        action='store_true',
        help="show python error messages with stacktrace")
    cli_args_parser.add_argument(
        '-O',
        '--optimization-level',
        help="set the optimiziation level of the "
        "compiler (0=save all variables on the "
        "stack, 1=use graph coloring to find the "
        "best assignment of variables to registers, "
        "2=partially interpret expressions) [NOT IMPLEMENTED YET]",
        type=int,
        default=0)
    cli_args_parser.add_argument(
        '-b',
        '--binary',
        action='store_true',
        help="produce binary encoded RETI code [NOT IMPLEMENTED YET]")
    cli_args_parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help="also show tokentype and position for tokens, write the nodetype "
        "in front of parenthesis in the abstract syntax tree [NOT IMPLEMENTED YET], add comments to "
        "the RETI Code and show more context around error messages "
        "[NOT IMPLEMENTED YET]")
    global_vars.args = cli_args_parser.parse_args()

    if not global_vars.args.infile:
        _shell()
    else:
        infile = global_vars.args.infile
        outbase = _basename(infile)

    try:
        _read_and_write_file(infile, outbase)
    except FileNotFoundError:
        print("File does not exist")
    else:
        print("Compiled successfully")


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

        _compile([pico_c_in], "stdin")


def _read_and_write_file(infile, outbase):
    """reads a pico_c file and compiles it
    :returns: pico_c Code compiled in RETI Assembler

    """
    with open(infile, encoding="utf-8") as fin:
        pico_c_in = fin.readlines()

    _compile(pico_c_in, infile, outbase)


def _compile(code, infile, outbase=None):
    # remove all empty lines and \n from the code lines in the list
    code_without_cr = [infile + " "] + list(
        filter(lambda line: line, map(lambda line: line.strip(), code)))

    if global_vars.args.concrete_syntax and global_vars.args.print:
        print(code_without_cr)

    lexer = Lexer(code_without_cr)

    if global_vars.args.tokens:
        _tokens_option(lexer, outbase)
        lexer.__init__(code_without_cr)

    # Generate ast
    grammar = Grammar(lexer)
    # Handle errors
    error_handler = ErrorHandler(grammar)
    error_handler.handle(grammar.start_parse)

    if global_vars.args.abstract_syntax:
        _abstract_syntax_option(grammar, outbase)

    abstract_syntax_tree = grammar.reveal_ast()
    error_handler.handle(abstract_syntax_tree.visit)

    if global_vars.args.symbol_table:
        _symbol_table_option(outbase)

    _reti_code(abstract_syntax_tree, outbase)


def _tokens_option(lexer, outbase):
    tokens = []
    t = lexer.next_token()
    while t.type != TT.EOF:
        tokens += [t]
        t = lexer.next_token()

    if global_vars.args.print:
        print('\n' + str(tokens))

    if outbase:
        with open(outbase + ".tokens", 'w', encoding="utf-8") as fout:
            fout.write(str(tokens))


def _abstract_syntax_option(grammar, outbase):
    if global_vars.args.print:
        print('\n' + str(grammar.reveal_ast()))

    if outbase:
        with open(outbase + ".ast", 'w', encoding="utf-8") as fout:
            fout.write(str(grammar.reveal_ast()))


def _symbol_table_option(outbase):
    if global_vars.args.print:
        header = ["name", "type", "datatype", "position", "value"]
        symbols = SymbolTable().symbols
        print('\n' + str(
            tabulate([(k, v.get_type(), str(v.datatype), str(v.position),
                       str(v.value)) for k, v in symbols.items()],
                     headers=header)))

    if outbase:
        _write_symbol_table(outbase)


def _write_symbol_table(outbase):
    output = "name,type,datatype,position,value\n"
    symbols = SymbolTable().symbols
    for name in symbols.keys():
        if symbols[name].position:
            output += f"{name},"\
                f"{symbols[name].get_type()},"\
                f"{symbols[name].datatype},"\
                f"{symbols[name].position[0]}:"\
                f"{symbols[name].position[1]},"\
                f"{symbols[name].value}\n"
        else:  # if it is None
            output += f"{name},{symbols[name].get_type()},"\
                f"{symbols[name].datatype},{symbols[name].position}, {symbols[name].value}\n"
    with open(outbase + ".csv", 'w', encoding="utf-8") as fout:
        fout.write(output)


def _reti_code(abstract_syntax_tree, outbase):
    if global_vars.args.print:
        print('\n' + str(abstract_syntax_tree.show_generated_code()))
    if outbase:
        with open(outbase + ".reti", 'w', encoding="utf-8") as fout:
            fout.write(str(abstract_syntax_tree.show_generated_code()))


def _basename(fname):
    """stips of the file extension
    :fname: filename
    :returns: basename of the file

    """
    index_of_extension = fname.rindex('.')
    return fname[0:index_of_extension]


if __name__ == '__main__':
    main()
