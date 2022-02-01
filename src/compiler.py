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
from enum import Enum
from colormanager import ColorManager as CM
import os
from string import ascii_letters


class Compiler(cmd2.Cmd):
    description = """
    Compiles PicoC-Code into RETI-Code.
    PicoC is a subset of C including while loops, if and else statements,
    assignments, arithmetic and logic expressions.
    Please keep in mind that all statements have to be enclosed in a

    void main() { /* your program */ }

    main function.

    If called without arguments, a shell is going to open up where you can
    compile PicoC-Code into RETI-Code with the `compile <cli-options>
    "<code>";` command (shortcut 'cpl'). The cli-options are the same as for
    calling the compiler from outside, except for the 'infile' argument which
    is interpreted as string with PiooC-Code and which will be compiled as if
    it was enclosed in a main function.

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
    cli_args_parser = cmd2.Cmd2ArgumentParser(description=description)
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
        help="distance of the comments from the instructions for the --verbose "
        "option. The passed value gets added to the minimum distance of 2 spaces",
        type=int,
        default=0)
    cli_args_parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help="also show tokentype and position for tokens, write the nodetype "
        "in front of parenthesis in the abstract syntax tree, add comments to "
        "the RETI Code")
    cli_args_parser.add_argument('-S',
                                 '--sight',
                                 help="sets the number of lines visible around"
                                 " a error message",
                                 type=int,
                                 default=0)
    cli_args_parser.add_argument('-C',
                                 '--color',
                                 action='store_true',
                                 help="colorizes the terminal output."
                                 " Gets ignored in the shell. Instead in the "
                                 "shell colors can be toggled via the "
                                 "'color_toggle' command (shortcut 'ct')")
    #  cli_args_parser.add_argument(
    #      '-O',
    #      '--optimization_level',
    #      help="set the optimiziation level of the "
    #      "compiler (0=save all variables on the "
    #      "stack, 1=use graph coloring to find the "
    #      "best assignment of variables to registers, "
    #      "2=partially interpret expressions) [NOT IMPLEMENTED YET]",
    #      type=int,
    #      default=0)

    HISTORY_FILE = os.path.expanduser(
        '~') + "/.config/pico_c_compiler/history.json"
    SETTINGS_FILE = os.path.expanduser(
        '~') + "/.config/pico_c_compiler/settings.conf"
    PERSISTENT_HISTORY_LENGTH = 100

    def __init__(self, ):
        global_vars.args = self.cli_args_parser.parse_args()
        if not global_vars.args.infile:
            self._shell__init__()

    def _shell__init__(self, ):
        super().__init__()

        shortcuts = dict(cmd2.DEFAULT_SHORTCUTS)
        shortcuts.update({
            'cpl': 'compile',
            'ct': 'color_toggle',
            'mu': 'most_used'
        })
        cmd2.Cmd.__init__(self,
                          shortcuts=shortcuts,
                          multiline_commands=['compile'])

        # save history hook
        self.register_postcmd_hook(self.save_history)

        self._deal_with_history_and_settings()

        self._colorprompt()

    def _deal_with_history_and_settings(self, ):
        # load history
        if os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE) as fin:
                self.history = self.history.from_json(fin.read())

        # for the tc command
        if os.path.exists(self.SETTINGS_FILE):
            with open(self.SETTINGS_FILE) as fin:
                lines = fin.read().split('\n')
                for line in lines:
                    if "colorprompt" in line:
                        if "True" in line:
                            global_vars.args.color = True
                        else:  # "False" in line:
                            global_vars.args.color = False
        else:
            self.colorprompt = False

    def save_history(
            self,
            _: cmd2.plugin.PostcommandData) -> cmd2.plugin.PostcommandData:
        if len(self.history) > self.PERSISTENT_HISTORY_LENGTH:
            del self.history[0]
        with open(self.HISTORY_FILE, 'w', encoding="utf-8") as fout:
            fout.write(self.history.to_json())
        return _

    def _colorprompt(self, ):
        if global_vars.args.color:
            CM().color_on()
        else:
            CM().color_off()
        self.prompt = (
            f"{CM().BRIGHT}{CM().GREEN}P{CM().CYAN}ico{CM().MAGENTA}C{CM().WHITE}>{CM().RESET}{CM().RESET_ALL} "
            if global_vars.args.color else "PicoC> ")
        self.continuation_prompt = (
            f"{CM().BRIGHT}{CM().WHITE}>{CM().RESET}{CM().RESET_ALL} "
            if global_vars.args.color else "> ")

    def do_color_toggle(self, _=None):
        global_vars.args.color = False if global_vars.args.color else True
        if os.path.exists(self.SETTINGS_FILE):
            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as fout:
                fout.write(f"colorprompt: {global_vars.args.color}")
        self._colorprompt()

    @cmd2.with_argparser(cli_args_parser)
    def do_most_used(self, args):
        args = global_vars.Args(args.infile)
        self._do_compile(args)

    @cmd2.with_argparser(cli_args_parser)
    def do_compile(self, args):
        # don't chang anything about the color setting
        self._do_compile(args)

    def _do_compile(self, args):
        color = global_vars.args.color
        global_vars.args = args
        global_vars.args.color = color

        # printing is always on in shell
        global_vars.args.print = True

        if global_vars.args.color:
            CM().color_on()
        else:
            CM().color_off()

        try:
            self._compile(["void main() {"] + args.infile.split('\n') + ["}"],
                          "stdin")
        except:
            print(
                f"{CM().BRIGHT}{CM().WHITE}Compilation unsuccessfull{CM().RESET}{CM().RESET_ALL}\n"
            )
        else:
            print(
                f"{CM().BRIGHT}{CM().WHITE}Compilation successfull{CM().RESET}{CM().RESET_ALL}\n"
            )

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
            code_without_cr_str = Colorizer(
                str(code_without_cr)).colorize_conrete_syntax()
            print(code_without_cr_str)

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
            tokens_str = Colorizer(str(tokens)).colorize_tokens()
            print('\n' + tokens_str)

        if outbase:
            with open(outbase + ".tokens", 'w', encoding="utf-8") as fout:
                fout.write(str(tokens))

    def _abstract_syntax_option(self, grammar: Grammar, outbase):
        if global_vars.args.print:
            ast = str(grammar.reveal_ast())
            ast = Colorizer(ast).colorize_abstract_syntax()
            print('\n' + ast)

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

        output = str(
            tabulate([(k, v.get_type(), str(v.datatype), str(
                v.position), str(v.value)) for k, v in symbols.items()],
                     headers=header))

        output = (Colorizer(output).colorize_symbol_table()
                  if global_vars.args.color else output)
        print('\n' + output)

    def _write_symbol_table(self, outbase):
        output = "name,type,datatype,position,value\n"
        symbols = SymbolTable().symbols
        for name in symbols.keys():
            position = (
                f"({symbols[name].position[0]}:{symbols[name].position[1]})"
                if symbols[name].position != '-' else '-')
            output += f"{name},"
            f"{symbols[name].get_type()},"
            f"{symbols[name].datatype},"
            f"{position},"
            f"{symbols[name].value}\n"
        with open(outbase + ".csv", 'w', encoding="utf-8") as fout:
            fout.write(output)

    def _reti_code(self, abstract_syntax_tree, outbase):
        if global_vars.args.print:
            code = Colorizer(str(abstract_syntax_tree.show_generated_code(
            ))).colorize_reti_code() if global_vars.args.color else str(
                abstract_syntax_tree.show_generated_code())
            print('\n' + code)
        if outbase:
            with open(outbase + ".reti", 'w', encoding="utf-8") as fout:
                fout.write(str(abstract_syntax_tree.show_generated_code()))


class Colorizer:
    EOF_CHAR = 'EOF'

    class States(Enum):
        # to reti code
        COMMAND = 0
        SPACE = 1
        PARAMETER = 2
        REGISTER = 3
        SEMICOLON = 4
        COMMENT = 5
        # for symbol table
        TABLE = 6
        HEADING = 7
        WORD_CELL = 8
        NUMBER_CELL = 9
        # for abstract syntax
        PARENTHESIS = 10
        OPERATOR = 11
        NUMBER = 12
        WORD = 13
        # for tokens
        STRUCTURE = 14
        TOKEN = 15
        TOKENTYPE = 16
        STRING = 17
        POSITION = 18

    def __init__(self, cinput):
        """
        :lc: lookahead character
        :c: character
        """
        self.cinput = cinput
        self.idx = 0
        self.c = cinput[self.idx]

        # position variable to be available between methods
        self.state = None

        # so that the color ansi escape sequence won't get inserted several times
        self.color_not_inserted = True

    def colorize_reti_code(self, ):
        self.state = self.States.COMMAND
        while self.c != self.EOF_CHAR:
            if self.c == ' ' and self.state != self.States.COMMENT:
                self.state = self.States.SPACE
                self.color_not_inserted = True
            elif (self.c in ascii_letters + '_'
                  and self.state == self.States.SPACE
                  and self.state != self.States.COMMENT):
                self.state = self.States.REGISTER
                self.color_not_inserted = True
            elif (self.c in '-1234567890' and self.state == self.States.SPACE
                  and self.state != self.States.COMMENT):
                self.state = self.States.PARAMETER
                self.color_not_inserted = True
            elif self.c == ';':
                self.state = self.States.SEMICOLON
                self.color_not_inserted = True
            elif self.c == '#':
                self.state = self.States.COMMENT
                self.color_not_inserted = True
            elif self.c == '\n':
                self.state = self.States.COMMAND
                self.color_not_inserted = True

            if self.state == self.States.COMMAND and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().BLUE)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.REGISTER and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().RED)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.PARAMETER and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().GREEN)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.SEMICOLON and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().WHITE)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.COMMENT and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().MAGENTA)
                self.color_not_inserted = False
                self.next_char()
            else:
                self.next_char()
        return self.cinput + CM().RESET

    def colorize_symbol_table(self, ):
        self.state = self.States.HEADING
        while self.c != self.EOF_CHAR:
            if (self.c in ascii_letters + '_' and self.state
                    in [self.States.TABLE, self.States.NUMBER_CELL]):
                self.state = self.States.WORD_CELL
                self.color_not_inserted = True
            elif (self.c in '1234567890'
                  and self.state != self.States.WORD_CELL):
                self.state = self.States.NUMBER_CELL
                self.color_not_inserted = True
            elif self.c == '-' and self.state in [
                    self.States.HEADING, self.States.WORD_CELL
            ]:
                self.state = self.States.TABLE
                self.color_not_inserted = True
            elif self.c in '(),':
                self.state = self.States.TABLE
                self.color_not_inserted = True

            if self.state == self.States.HEADING and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().BLUE)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.WORD_CELL and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().RED)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.NUMBER_CELL and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().GREEN)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.TABLE and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().WHITE)
                self.color_not_inserted = False
                self.next_char()
            else:
                self.next_char()
        return self.cinput + CM().RESET

    def colorize_abstract_syntax(self, ):
        self.state = self.States.PARENTHESIS
        while self.c != self.EOF_CHAR:
            if (self.c in ascii_letters + '_' and self.state
                    in [self.States.PARENTHESIS, self.States.OPERATOR]):
                self.state = self.States.WORD
                self.color_not_inserted = True
            elif self.c in '1234567890' and self.state != self.States.WORD:
                self.state = self.States.NUMBER
                self.color_not_inserted = True
            elif self.c in '()':
                self.state = self.States.PARENTHESIS
                self.color_not_inserted = True
            elif self.c in '+~-*%/&|!^<>=' and self.state != self.States.OPERATOR:
                self.state = self.States.OPERATOR
                self.color_not_inserted = True

            if self.state == self.States.WORD and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().RED)
                self.color_not_inserted = False
                self.next_char()
            if self.state == self.States.NUMBER and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().GREEN)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.PARENTHESIS and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().WHITE)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.OPERATOR and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().BLUE)
                self.color_not_inserted = False
                self.next_char()
            else:
                self.next_char()
        return self.cinput + CM().RESET

    def colorize_tokens(self, ):
        self.state = self.States.STRUCTURE
        while self.c != self.EOF_CHAR:
            if self.c in '()[],':
                self.state = self.States.STRUCTURE
                self.color_not_inserted = True
            elif self.c in '<>':
                self.state = self.States.TOKEN
                self.color_not_inserted = True
            elif self.c == 'T' and self.state == self.States.TOKEN:
                self.state = self.States.TOKENTYPE
                self.color_not_inserted = True
            elif self.c in "'":
                self.state = self.States.STRING
                self.color_not_inserted = True
            elif (self.c in "1234567890"
                  and self.state == self.States.STRUCTURE):
                self.state = self.States.POSITION
                self.color_not_inserted = True

            if self.state == self.States.STRUCTURE and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().WHITE)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.TOKEN and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().MAGENTA)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.TOKENTYPE and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().BLUE)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.STRING and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().RED)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.POSITION and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().GREEN)
                self.color_not_inserted = False
                self.next_char()
            else:
                self.next_char()
        return self.cinput + CM().RESET

    def colorize_conrete_syntax(self, ):
        self.state = self.States.STRUCTURE
        while self.c != self.EOF_CHAR:
            if self.c in '[],':
                self.state = self.States.STRUCTURE
                self.color_not_inserted = True
            elif self.c in "\"'":
                self.state = self.States.STRING
                self.color_not_inserted = True

            if self.state == self.States.STRUCTURE and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().WHITE)
                self.color_not_inserted = False
                self.next_char()
            elif self.state == self.States.STRING and self.color_not_inserted:
                self.insert_colorcode(self.idx, CM().RED)
                self.color_not_inserted = False
                self.next_char()
            else:
                self.next_char()
        return self.cinput + CM().RESET

    def insert_colorcode(self, idx, color):
        self.cinput = self.cinput[:idx] + color + self.cinput[idx:]
        self.idx += len(color)

    def next_char(self):
        """go to the next character, detect if "end of file" is reached

        :returns: None
        """
        # next index
        self.idx += 1

        # next character
        if self.idx == len(self.cinput):
            self.c = self.EOF_CHAR
        else:
            self.c = self.cinput[self.idx]


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
