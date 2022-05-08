import global_vars
import cmd2
from error_handler import ErrorHandler
from symbol_table import SymbolTable
from tabulate import tabulate
from colormanager import ColorManager as CM
import os
from help_message import generate_help_message
from ast_node import ASTNode
from lark import Lark, Token
from transformer import ASTTransformer


class Compiler(cmd2.Cmd):
    cli_args_parser = cmd2.Cmd2ArgumentParser(add_help=False)
    cli_args_parser.add_argument("infile", nargs="?")
    cli_args_parser.add_argument("-c", "--code", action="store_true")
    cli_args_parser.add_argument("-t", "--tokens", action="store_true")
    cli_args_parser.add_argument("-d", "--derivation_tree", action="store_true")
    cli_args_parser.add_argument("-a", "--abstract_syntax_tree", action="store_true")
    cli_args_parser.add_argument("-s", "--symbol_table", action="store_true")
    cli_args_parser.add_argument("-p", "--print", action="store_true")
    cli_args_parser.add_argument("-D", "--distance", type=int, default=0)
    cli_args_parser.add_argument("-S", "--sight", type=int, default=0)
    cli_args_parser.add_argument("-C", "--color", action="store_true")
    cli_args_parser.add_argument("-v", "--verbose", action="store_true")
    cli_args_parser.add_argument("-g", "--debug", action="store_true")
    cli_args_parser.add_argument("-m", "--show_error_message", action="store_true")

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

        self._deal_with_history_and_color_settings()

        self._color_for_prompt_and_intro()

    def _deal_with_history_and_color_settings(self):
        # load history
        if os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE) as fin:
                self.history = self.history.from_json(fin.read())

        # color on or off
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
        while len(self.history) > self.PERSISTENT_HISTORY_LENGTH:
            del self.history[0]
        if os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, "w", encoding="utf-8") as fout:
                fout.write(self.history.to_json())
        return _

    def _color_for_prompt_and_intro(self):
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
        self._color_for_prompt_and_intro()

    @cmd2.with_argparser(cli_args_parser)
    def do_most_used(self, args):
        # the 'infile' attribute is used as a storage for the code
        code = args.infile
        # color should never be effected by the '-C' option, because it's
        # determined before via 'settings.conf' before and this should be kept
        color = global_vars.args.color
        global_vars.args = global_vars.Args()
        global_vars.args.color = color
        self._do_compile_shell(code)

    @cmd2.with_argparser(cli_args_parser)
    def do_compile(self, args):
        # shell is only going to open, if there're no options from outside, so
        # shell is anyways always starting with everything turned off in
        # global_vars.args besides color being set from settings.conf before
        code = args.infile
        color = global_vars.args.color
        global_vars.args = args
        # is important to give this attribute a filename as value again,
        # because it's needed later
        global_vars.args.infile = "stdin"
        global_vars.args.color = color
        self._do_compile_shell(code)

    def _do_compile_shell(self, code):
        # printing is always turned on in shell
        global_vars.args.print = True

        try:
            self._compile(["void main() {"] + code.split("\n") + ["}"])
        except Exception as e:
            print(
                f"{CM().BRIGHT}{CM().WHITE}Compilation unsuccessfull{CM().RESET}{CM().RESET_ALL}\n"
            )
            if global_vars.args.show_error_message:
                raise e
        else:
            print(
                f"{CM().BRIGHT}{CM().WHITE}Compilation successfull{CM().RESET}{CM().RESET_ALL}\n"
            )

    def do_help(self, _):
        print(generate_help_message())

    def read_and_write_file(self):
        """reads a pico_c file and compiles it
        :returns: pico_c Code compiled in RETI Assembler
        """
        with open(global_vars.args.infile, encoding="utf-8") as fin:
            pico_c_in = fin.read()

        self._compile(pico_c_in)

    def _compile(self, code):
        if global_vars.args.debug:
            __import__("pudb").set_trace()

        terminal_width = os.get_terminal_size().columns

        # add the filename to the start of the code
        code_with_file = f"{basename(global_vars.args.infile)}\n" + code

        if global_vars.args.code and global_vars.args.print:
            print(subheading("Code", terminal_width, "-"))
            print(code)

        parser = Lark.open(
            "./src/concrete_syntax.lark",
            lexer="dynamic",
            parser="earley",
            start="file",
            maybe_placeholders=False,
            propagate_positions=True,
        )

        # handle errors
        error_handler = ErrorHandler(code_with_file)

        dt = error_handler.handle(parser.parse, code_with_file)

        if global_vars.args.tokens:
            print(subheading("Tokens", terminal_width, "-"))
            error_handler.handle(self._tokens_option, dt, code_with_file)

        if global_vars.args.derivation_tree:
            print(subheading("Derivation Tree", terminal_width, "-"))
            self._derivation_tree_option(dt)

        ast_transformer = ASTTransformer()
        ast = error_handler.handle(ast_transformer.transform, dt)

        if global_vars.args.abstract_syntax_tree:
            print(subheading("Abstract Syntax Tree", terminal_width, "-"))
            self._abstract_syntax_tree_option(ast)

        if global_vars.args.symbol_table:
            print(subheading("Symbol Table", terminal_width, "-"))
            self._symbol_table_option()

        print(subheading("RETI Code", terminal_width, "-"))
        self._reti_code(ast)

    def _tokens_option(self, dt, code):
        if global_vars.args.verbose:
            parser = Lark.open(
                "./src/concrete_syntax.lark",
                lexer="dynamic",
                keep_all_tokens=True,
                parser="earley",
                start="file",
                maybe_placeholders=False,
                propagate_positions=True,
            )
            dt = parser.parse(code)

        tokens = list(dt.scan_values(lambda v: isinstance(v, Token)))

        if global_vars.args.print:
            print(tokens)

        if global_vars.outbase:
            with open(global_vars.outbase + ".tokens", "w", encoding="utf-8") as fout:
                fout.write(str(tokens))

    def _derivation_tree_option(self, dt):
        if global_vars.args.print:
            print(dt.pretty())

        if global_vars.outbase:
            with open(global_vars.outbase + ".dt", "w", encoding="utf-8") as fout:
                fout.write(str(dt))

    def _abstract_syntax_tree_option(self, ast):
        if global_vars.args.print:
            print(ast)

        if global_vars.outbase:
            with open(global_vars.outbase + ".ast", "w", encoding="utf-8") as fout:
                fout.write(str(ast))

    def _symbol_table_option(self):
        if global_vars.args.print:
            self._print_symbol_table()

        if global_vars.outbase:
            self._write_symbol_table()

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
        print(output)

    def _write_symbol_table(self):
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
        with open(global_vars.outbase + ".csv", "w", encoding="utf-8") as fout:
            fout.write(output)

    def _reti_code(self, root: ASTNode):
        if global_vars.args.print:
            pass
        if global_vars.outbase:
            with open(global_vars.outbase + ".reti", "w", encoding="utf-8") as fout:
                pass


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


def subheading(heading, terminal_width, symbol):
    return f"{symbol * ((terminal_width - len(heading) - 2) // 2 + (1 if (terminal_width - len(heading)) % 2 else 0))} {heading} {symbol * ((terminal_width - len(heading) - 2) // 2)}"
