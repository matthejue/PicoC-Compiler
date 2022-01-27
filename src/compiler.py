#!/usr/bin/python
# -*- coding: utf-8 -*-
import global_vars
import cmd2
from lexer import Lexer, TT
from grammar import Grammar
from error_handler import ErrorHandler
from warning_handler import WarningHandler
from symbol_table import SymbolTable
from code_generator import CodeGenerator
from warning_handler import WarningHandler
from tabulate import tabulate
import argparse


class Compiler(cmd2.Cmd):
    description = """
    Compiles PicoC-Code into RETI-Code.
    PicoC is a subset of C including while loops, if and else statements,
    assignments, arithmetic and logic expressions.
    Please keep in mind that all statements have to be enclosed in a

    void main() { /* your program */ }

    main function.

    If called without arguments, a shell is going to open up where you can
    compile PicoC-Code into RETI-Code with the 'compile <cli-options>;' command.
    The cli-options are the same as for calling the compiler from outside,
    except for the 'infile' argument, which is interpreted as string with
    PiooC-Code which will be compiled as if it was enclosed in a main function.

    The 'compile <cli-options>;' command can also be written over multiple
    lines and thus has to end with a ';'.
    All multiline_commands have to end with a ';'.

    In the shell the cursor can be moved with the <left> and <right> arrow key.
    Previous and next commands can be retrieved with the <up> and <down> arrow key.
    A command can be completed with <tab>.

    The shell can be exited again by typing 'quit'.

    If you discover any bugs I would be very grateful if you could report it
    via email to juergmatth@gmail.com, attaching the malicious code to the
    email. ^_^
    """
    cli_args_parser = (cmd2.Cmd2ArgumentParser(description=description)
                       if global_vars.shell_on else argparse.ArgumentParser(
                           description=description))
    cli_args_parser.add_argument(
        "infile",
        nargs='?',
        help="input file with PicoC-code. In the shell this is interpreted as"
        " string with PicoC-Code")
    cli_args_parser.add_argument(
        '-c',
        '--concrete_syntax',
        action='store_true',
        help=
        "also print the concrete syntax (= content of input file). Only works"
        " if --print option is active")
    cli_args_parser.add_argument('-t',
                                 '--tokens',
                                 action='store_true',
                                 help="also write the tokenlist")
    cli_args_parser.add_argument('-a',
                                 '--abstract-syntax',
                                 action='store_true',
                                 help="also write the abstract syntax")
    cli_args_parser.add_argument(
        '-s',
        '--symbol_table',
        action='store_true',
        help="also write the final symbol table into a .csv file")
    cli_args_parser.add_argument('-p',
                                 '--print',
                                 action='store_true',
                                 help="print all file outputs to the terminal")
    cli_args_parser.add_argument(
        '-b',
        '--begin_data_segment',
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
        '-d',
        '--distance',
        help="distance of the comments from the instructions for the --verbose"
        "option. The passed value gets added to the minimum distance of 2 spaces",
        type=int,
        default=0)
    cli_args_parser.add_argument('-S',
                                 '--sight',
                                 help="sets the number of lines visible around"
                                 " a error message",
                                 type=int,
                                 default=0)
    cli_args_parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help="also show tokentype and position for tokens, write the nodetype "
        "in front of parenthesis in the abstract syntax tree, add comments to "
        "the RETI Code")
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

    def __init__(self, ):
        if global_vars.shell_on:
            super().__init__()

        shortcuts = cmd2.DEFAULT_SHORTCUTS
        shortcuts.update({'c': 'compile'})

        # shell is always executed with print
        cmd2.Cmd.prompt = "PicoC> "
        cmd2.Cmd.continuation_prompt = "> "
        cmd2.Cmd.persistent_history_file = "~/.config/pico_c_compiler/history.txt"
        cmd2.Cmd.persistent_history_length = 100
        cmd2.Cmd.multiline_commands = ['compile']
        global_vars.args = self.cli_args_parser.parse_args()

    @cmd2.with_argparser(cli_args_parser)
    def do_compile(self, args):
        global_vars.args = args
        # printing is always on in shell

        global_vars.args.print = True
        try:
            self._compile(["void main() {"] + args.infile.split('\n') + ["}"],
                          "stdin")
        except:
            print("Compilation unsuccessfull\n")
        else:
            print("Compilation successfull\n")

    def read_and_write_file(self, infile, outbase):
        """reads a pico_c file and compiles it
        :returns: pico_c Code compiled in RETI Assembler

        """
        with open(infile, encoding="utf-8") as fin:
            pico_c_in = fin.readlines()

        self._compile(pico_c_in, infile, outbase)

    def _reset(self, fname, finput):
        # Singletons have to be reset manually for the shell
        SymbolTable().__init__()
        CodeGenerator().__init__()
        if not WarningHandler(fname, finput)._instance:
            WarningHandler(fname, finput)
        else:
            WarningHandler().__init__(fname, finput)

    def _compile(self, code, infile, outbase=None):
        # remove all empty lines and \n from the code lines in the list
        code_without_cr = [basename(infile) + " "] + list(
            filter(lambda line: line, map(lambda line: line.strip('\n'),
                                          code)))

        # reset everything to defaults
        self._reset(infile, code_without_cr)

        if global_vars.args.concrete_syntax and global_vars.args.print:
            print(code_without_cr)

        lexer = Lexer(code_without_cr)

        # Handle errors and warnings
        error_handler = ErrorHandler(infile, code_without_cr)
        warning_handler = WarningHandler(
            infile, code_without_cr)  # initialise singleton

        if global_vars.args.tokens:
            error_handler.handle(self._tokens_option, lexer, outbase)
            lexer.__init__(code_without_cr)

        # Generate ast
        grammar = Grammar(lexer)
        error_handler.handle(grammar.start_parse)

        if global_vars.args.abstract_syntax:
            self._abstract_syntax_option(grammar, outbase)

        abstract_syntax_tree = grammar.reveal_ast()
        error_handler.handle(abstract_syntax_tree.visit)

        if global_vars.args.symbol_table:
            self._symbol_table_option(outbase)

        # show warnings before reti code gets output
        warning_handler.show_warnings()

        self._reti_code(abstract_syntax_tree, outbase)

    def _tokens_option(self, lexer, outbase):
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

    def _abstract_syntax_option(self, grammar: Grammar, outbase):
        if global_vars.args.print:
            print('\n' + str(grammar.reveal_ast()))

        if outbase:
            with open(outbase + ".ast", 'w', encoding="utf-8") as fout:
                fout.write(str(grammar.reveal_ast()))

    def _symbol_table_option(self, outbase):
        if global_vars.args.print:
            self._print_symbol_table()

        if outbase:
            self._write_symbol_table(outbase)

    def _print_symbol_table(self, ):
        header = ["name", "type", "datatype", "position", "value"]
        symbols = SymbolTable().symbols
        print('\n' + str(
            tabulate([(k, v.get_type(), str(v.datatype), str(v.position),
                       str(v.value)) for k, v in symbols.items()],
                     headers=header)))

    def _write_symbol_table(self, outbase):
        output = "name,type,datatype,position,value\n"
        symbols = SymbolTable().symbols
        for name in symbols.keys():
            position = f"({symbols[name].position[0]}:{symbols[name].position[1]})"\
                if symbols[name].position != '-' else '-'
            output += f"{name},"\
                f"{symbols[name].get_type()},"\
                f"{symbols[name].datatype},"\
                f"{position},"\
                f"{symbols[name].value}\n"
        with open(outbase + ".csv", 'w', encoding="utf-8") as fout:
            fout.write(output)

    def _reti_code(self, abstract_syntax_tree, outbase):
        if global_vars.args.print:
            print('\n' + str(abstract_syntax_tree.show_generated_code()))
        if outbase:
            with open(outbase + ".reti", 'w', encoding="utf-8") as fout:
                fout.write(str(abstract_syntax_tree.show_generated_code()))


def remove_extension(fname):
    """stips of the file extension
    :fname: filename
    :returns: basename of the file

    """
    # if there's no '.' rindex raises a exception, rfind returns -1
    index_of_extension_start = fname.rfind('.')
    if index_of_extension_start == -1:
        return fname
    return fname[0:index_of_extension_start]


def _remove_path(fname):
    index_of_path_end = fname.rfind('/')
    if index_of_path_end == -1:
        return fname
    return fname[index_of_path_end + 1:]


def basename(fname):
    fname = remove_extension(fname)
    return _remove_path(fname)
