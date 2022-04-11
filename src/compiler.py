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
from colormanager import ColorManager as CM
import os
from colorizer import Colorizer
from help_message import generate_help_message


class Compiler(cmd2.Cmd):
    cli_args_parser = cmd2.Cmd2ArgumentParser(add_help=False)
    cli_args_parser.add_argument("infile", nargs="?")
    cli_args_parser.add_argument("-c", "--concrete_syntax", action="store_true")
    cli_args_parser.add_argument("-t", "--tokens", action="store_true")
    cli_args_parser.add_argument("-a", "--abstract-syntax", action="store_true")
    cli_args_parser.add_argument("-s", "--symbol_table", action="store_true")
    cli_args_parser.add_argument("-p", "--print", action="store_true")
    cli_args_parser.add_argument("-d", "--distance", type=int, default=0)
    cli_args_parser.add_argument("-v", "--verbose", action="store_true")
    cli_args_parser.add_argument("-S", "--sight", type=int, default=0)
    cli_args_parser.add_argument("-C", "--color", action="store_true")

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

    HISTORY_FILE = os.path.expanduser("~") + "/.config/pico_c_compiler/history.json"
    SETTINGS_FILE = os.path.expanduser("~") + "/.config/pico_c_compiler/settings.conf"
    PERSISTENT_HISTORY_LENGTH = 100

    def __init__(self):
        global_vars.args = self.cli_args_parser.parse_args()
        if not global_vars.args.infile:
            self._shell__init__()

    def _shell__init__(self):
        super().__init__()

        shortcuts = dict(cmd2.DEFAULT_SHORTCUTS)
        shortcuts.update(
            {
                "cpl": "compile",
                "mu": "most_used",
                "ct": "color_toggle",
            }
        )
        cmd2.Cmd.__init__(
            self, shortcuts=shortcuts, multiline_commands=["compile", "most_used"]
        )
        del cmd2.Cmd.do_help

        # save history hook
        self.register_postcmd_hook(self.save_history)

        self._deal_with_history_and_settings()

        self._colorprompt_and_intro()

    def _deal_with_history_and_settings(self):
        # load history
        if os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE) as fin:
                self.history = self.history.from_json(fin.read())

        # for the tc command
        if os.path.exists(self.SETTINGS_FILE):
            with open(self.SETTINGS_FILE) as fin:
                lines = fin.read().split("\n")
                for line in lines:
                    if "color_on" in line:
                        if "True" in line:
                            global_vars.args.color = True
                        else:  # "False" in line:
                            global_vars.args.color = False
        else:
            self.colorprompt = False

    def save_history(
        self, _: cmd2.plugin.PostcommandData
    ) -> cmd2.plugin.PostcommandData:
        if len(self.history) > self.PERSISTENT_HISTORY_LENGTH:
            del self.history[0]
        if os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, "w", encoding="utf-8") as fout:
                fout.write(self.history.to_json())
        return _

    def _colorprompt_and_intro(self):
        if global_vars.args.color:
            CM().color_on()
        else:
            CM().color_off()

        # prompts
        self.prompt = (
            f"{CM().BRIGHT}{CM().GREEN}P{CM().CYAN}ico{CM().MAGENTA}C{CM().WHITE}>{CM().RESET}{CM().RESET_ALL} "
            if global_vars.args.color
            else "PicoC> "
        )
        self.continuation_prompt = (
            f"{CM().BRIGHT}{CM().WHITE}>{CM().RESET}{CM().RESET_ALL} "
            if global_vars.args.color
            else "> "
        )

        # intro
        self.intro = (
            f"{CM().BLUE}PicoC Shell ready. Enter {CM().RED + CM().BRIGHT}`help`{CM().BLUE + CM().NORMAL} (shortcut {CM().RED + CM().BRIGHT}`?`{CM().BLUE + CM().NORMAL}) to see the manual."
            if global_vars.args.color
            else "PicoC Shell. Enter `help` (shortcut `?`) to see the manual."
        )

    def do_color_toggle(self, _):
        global_vars.args.color = False if global_vars.args.color else True
        if os.path.exists(self.SETTINGS_FILE):
            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as fout:
                fout.write(f"color_on: {global_vars.args.color}")
        self._colorprompt_and_intro()

    @cmd2.with_argparser(cli_args_parser)
    def do_most_used(self, args):
        args = global_vars.Args(args.infile)
        self._do_compile(args)

    @cmd2.with_argparser(cli_args_parser)
    def do_compile(self, args):
        # don't change anything about the color setting
        self._do_compile(args)

    def _do_compile(self, args):
        color = global_vars.args.color
        global_vars.args = args
        global_vars.args.color = color

        # printing is always on in shell
        global_vars.args.print = True

        try:
            self._compile(["void main() {"] + args.infile.split("\n") + ["}"], "stdin")
        except:
            print(
                f"{CM().BRIGHT}{CM().WHITE}Compilation unsuccessfull{CM().RESET}{CM().RESET_ALL}\n"
            )
        else:
            print(
                f"{CM().BRIGHT}{CM().WHITE}Compilation successfull{CM().RESET}{CM().RESET_ALL}\n"
            )

    def do_help(self, _):
        print(generate_help_message())

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
            filter(lambda line: line, map(lambda line: line.strip("\n"), code))
        )
        # reset everything to defaults
        self._reset(infile, code_without_cr)

        if global_vars.args.concrete_syntax and global_vars.args.print:
            code_without_cr_str = Colorizer(
                str(code_without_cr)
            ).colorize_conrete_syntax()
            print(code_without_cr_str)

        lexer = Lexer(code_without_cr)

        # Handle errors and warnings
        error_handler = ErrorHandler(infile, code_without_cr)
        warning_handler = WarningHandler()  # get singleton

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
            print("\n" + tokens_str)

        if outbase:
            with open(outbase + ".tokens", "w", encoding="utf-8") as fout:
                fout.write(str(tokens))

    def _abstract_syntax_option(self, grammar: Grammar, outbase):
        if global_vars.args.print:
            ast = str(grammar.reveal_ast())
            ast = Colorizer(ast).colorize_abstract_syntax()
            print("\n" + ast)

        if outbase:
            with open(outbase + ".ast", "w", encoding="utf-8") as fout:
                fout.write(str(grammar.reveal_ast()))

    def _symbol_table_option(self, outbase):
        if global_vars.args.print:
            self._print_symbol_table()

        if outbase:
            self._write_symbol_table(outbase)

    def _print_symbol_table(self):
        header = ["name", "type", "datatype", "position", "value"]
        symbols = SymbolTable().symbols

        output = str(
            tabulate(
                [
                    (k, v.get_type(), str(v.datatype), str(v.position), str(v.value))
                    for k, v in symbols.items()
                ],
                headers=header,
            )
        )

        output = (
            Colorizer(output).colorize_symbol_table()
            if global_vars.args.color
            else output
        )
        print("\n" + output)

    def _write_symbol_table(self, outbase):
        output = "name,type,datatype,position,value\n"
        symbols = SymbolTable().symbols
        for name in symbols.keys():
            position = (
                f"({symbols[name].position[0]}:{symbols[name].position[1]})"
                if symbols[name].position != "/"
                else "/"
            )
            output += (
                f"{name},"
                f"{symbols[name].get_type()},"
                f"{symbols[name].datatype},"
                f"{position},"
                f"{symbols[name].value}\n"
            )
        with open(outbase + ".csv", "w", encoding="utf-8") as fout:
            fout.write(output)

    def _reti_code(self, abstract_syntax_tree, outbase):
        if global_vars.args.print:
            code = (
                Colorizer(
                    str(abstract_syntax_tree.show_generated_code())
                ).colorize_reti_code()
                if global_vars.args.color
                else str(abstract_syntax_tree.show_generated_code())
            )
            print("\n" + code)
        if outbase:
            with open(outbase + ".reti", "w", encoding="utf-8") as fout:
                fout.write(str(abstract_syntax_tree.show_generated_code()))


def remove_extension(fname):
    """stips of the file extension
    :fname: filename
    :returns: basename of the file

    """
    # if there's no '.' rindex raises a exception, rfind returns -1
    index_of_extension_start = fname.rfind(".")
    if index_of_extension_start == -1:
        return fname
    return fname[0:index_of_extension_start]


def _remove_path(fname):
    index_of_path_end = fname.rfind("/")
    if index_of_path_end == -1:
        return fname
    return fname[index_of_path_end + 1 :]


def basename(fname):
    fname = remove_extension(fname)
    return _remove_path(fname)
