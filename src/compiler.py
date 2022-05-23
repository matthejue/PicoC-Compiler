import global_vars
import cmd2
from error_handler import ErrorHandler
from symbol_table import ST
from picoc_nodes import N as PN
from reti_nodes import N as RN
from colormanager import ColorManager as CM
import os
import sys
from help_message import generate_help_message
from lark.lark import Lark
from dt_visitor_picoc import DTVisitorPicoC
from ast_transformer_picoc import ASTTransformerPicoC
from passes import Passes
from global_funs import basename, subheading, bug_in_compiler_error


class Compiler(cmd2.Cmd):
    cli_args_parser = cmd2.Cmd2ArgumentParser(add_help=False)
    cli_args_parser.add_argument("infile", nargs="?")
    cli_args_parser.add_argument("-i", "--intermediate_stages", action="store_true")
    cli_args_parser.add_argument("-e", "--execute", action="store_true")
    cli_args_parser.add_argument("-p", "--print", action="store_true")
    cli_args_parser.add_argument("-g", "--gap", type=int, default=20)
    cli_args_parser.add_argument("-l", "--lines", type=int, default=2)
    cli_args_parser.add_argument("-m", "--show_error_message", action="store_true")
    cli_args_parser.add_argument("-v", "--verbose", action="store_true")
    cli_args_parser.add_argument("-c", "--color", action="store_true")
    cli_args_parser.add_argument("-d", "--debug", action="store_true")

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

        terminal_width = os.get_terminal_size().columns if sys.stdin.isatty() else 79

        # add the filename to the start of the code
        code_with_file = (
            f"{basename(global_vars.args.infile.replace(' ', '_'))}\n" + code
        )

        if global_vars.args.intermediate_stages and global_vars.args.print:
            print(subheading("Code", terminal_width, "-"))
            print(
                f"// {basename(global_vars.args.infile.replace(' ', '_'))}.picoc:\n"
                + code
            )

        parser = Lark.open(
            "./src/concrete_syntax_picoc.lark",
            lexer="basic",
            priority="normal",
            parser="earley",
            start="file",
            maybe_placeholders=False,
            propagate_positions=True,
        )

        # handle errors
        error_handler = ErrorHandler(code_with_file)

        if global_vars.args.intermediate_stages:
            print(subheading("Tokens", terminal_width, "-"))
            error_handler.handle(self._tokens_option, code_with_file)

        dt = error_handler.handle(parser.parse, code_with_file)

        if global_vars.args.intermediate_stages:
            print(subheading("Derivation Tree", terminal_width, "-"))
            self._derivation_tree_option(dt)

        dt_visitor_picoc = DTVisitorPicoC()
        error_handler.handle(dt_visitor_picoc.visit, dt)

        if global_vars.args.intermediate_stages:
            print(subheading("Derivation Tree Simple", terminal_width, "-"))
            self._derivation_tree_simplified_option(dt)

        ast_transformer_picoc = ASTTransformerPicoC()
        ast = error_handler.handle(ast_transformer_picoc.transform, dt)

        if global_vars.args.intermediate_stages:
            print(subheading("Abstract Syntax Tree", terminal_width, "-"))
            self._abstract_syntax_tree_option(ast)

        passes = Passes()

        picoc_blocks = error_handler.handle(passes.picoc_blocks, ast)

        if global_vars.args.intermediate_stages:
            print(subheading("PicoC Shrink", terminal_width, "-"))

        if global_vars.args.intermediate_stages:
            print(subheading("PicoC Blocks", terminal_width, "-"))
            self._picoc_blocks_option(picoc_blocks)

        picoc_mon = error_handler.handle(passes.picoc_mon, picoc_blocks)

        if global_vars.args.intermediate_stages:
            print(subheading("PicoC Mon", terminal_width, "-"))
            self._picoc_mon_option(picoc_mon)

        if global_vars.args.intermediate_stages:
            print(subheading("Symbol Table", terminal_width, "-"))
            self._symbol_table_option(passes.symbol_table)

        reti_blocks = error_handler.handle(passes.reti_blocks, picoc_mon)

        if global_vars.args.intermediate_stages:
            print(subheading("RETI Blocks", terminal_width, "-"))
            self._reti_blocks_option(reti_blocks)

        if global_vars.args.intermediate_stages:
            print(subheading("RETI Patch", terminal_width, "-"))

        reti = error_handler.handle(passes.reti, reti_blocks)

        if global_vars.args.intermediate_stages:
            print(subheading("RETI", terminal_width, "-"))
            self._reti_option(reti)

    def _tokens_option(self, code_with_file):
        parser = Lark.open(
            "./src/concrete_syntax_picoc.lark",
            lexer="basic",
            priority="normal",
            parser="earley",
            start="file",
            maybe_placeholders=False,
            propagate_positions=True,
        )
        tokens = list(parser.lex(code_with_file))

        if global_vars.args.print:
            print(tokens)

        if global_vars.path:
            with open(
                global_vars.path + global_vars.basename + ".tokens",
                "w",
                encoding="utf-8",
            ) as fout:
                fout.write(str(tokens))

    def _derivation_tree_option(self, dt):
        if global_vars.args.print:
            print(dt.pretty())

        if global_vars.path:
            with open(
                global_vars.path + global_vars.basename + ".dt", "w", encoding="utf-8"
            ) as fout:
                fout.write(dt.pretty())

    def _derivation_tree_simplified_option(self, dt_simplified):
        if global_vars.args.print:
            print(dt_simplified.pretty())

        if global_vars.path:
            with open(
                global_vars.path + global_vars.basename + ".dt_simple",
                "w",
                encoding="utf-8",
            ) as fout:
                fout.write(dt_simplified.pretty())

    def _abstract_syntax_tree_option(self, ast: PN.File):
        if global_vars.args.print:
            print(ast)

        if global_vars.path:
            match ast:
                case PN.File(PN.Name(val)):
                    with open(val, "w", encoding="utf-8") as fout:
                        fout.write(str(ast))

    def _picoc_blocks_option(self, picoc_blocks: PN.File):
        if global_vars.args.print:
            print(picoc_blocks)

        if global_vars.path:
            match picoc_blocks:
                case PN.File(PN.Name(val)):
                    with open(val, "w", encoding="utf-8") as fout:
                        fout.write(str(picoc_blocks))
                case _:
                    bug_in_compiler_error(picoc_blocks)

    def _picoc_mon_option(self, picoc_mon: PN.File):
        if global_vars.args.print:
            print(picoc_mon)

        if global_vars.path:
            match picoc_mon:
                case PN.File(PN.Name(val)):
                    with open(val, "w", encoding="utf-8") as fout:
                        fout.write(str(picoc_mon))
                case _:
                    bug_in_compiler_error(picoc_mon)

    def _symbol_table_mon_option(self, symbol_table: ST.SymbolTable):
        if global_vars.args.print:
            print(symbol_table)

        if global_vars.path:
            with open(
                global_vars.path + global_vars.basename + ".st_mon",
                "w",
                encoding="utf-8",
            ) as fout:
                fout.write(str(symbol_table))

    def _reti_blocks_option(self, reti_blocks: RN.Program):
        if global_vars.args.print:
            print(reti_blocks)

        if global_vars.path:
            match reti_blocks:
                case PN.File(PN.Name(val)):
                    with open(val, "w", encoding="utf-8") as fout:
                        fout.write(str(reti_blocks))
                case _:
                    bug_in_compiler_error(reti_blocks)

    def _symbol_table_option(self, symbol_table: ST.SymbolTable):
        if global_vars.args.print:
            print(symbol_table)

        if global_vars.path:
            with open(
                global_vars.path + global_vars.basename + ".st", "w", encoding="utf-8"
            ) as fout:
                fout.write(str(symbol_table))

    def _reti_patch_option(self, reti_patch: RN.Program):
        if global_vars.args.print:
            print(reti_patch)

        if global_vars.path:
            match reti_patch:
                case RN.Program(RN.Name(val)):
                    with open(val, "w", encoding="utf-8") as fout:
                        fout.write(str(reti_patch))
                case _:
                    bug_in_compiler_error(reti_patch)

    def _reti_option(self, reti: RN.Program):
        if global_vars.args.print:
            print(reti)

        if global_vars.path:
            match reti:
                case RN.Program(RN.Name(val)):
                    with open(val, "w", encoding="utf-8") as fout:
                        fout.write(str(reti))
                case _:
                    bug_in_compiler_error(reti)

    # from tabulate import tabulate
    #  def _print_symbol_table(self):
    #      header = ["name", "type", "datatype", "position", "value"]
    #      symbols = ST.SymbolTable().symbols
    #
    #      output = str(
    #          tabulate(
    #              [
    #                  (k, v.get_type(), str(v.datatype), str(v.position), str(v.value))
    #                  for k, v in symbols.items()
    #              ],
    #              headers=header,
    #          )
    #      )
    #      print(output)
    #
    #  def _write_symbol_table(self):
    #      output = "name,type,datatype,position,value\n"
    #      symbols = ST.SymbolTable().symbols
    #      for name in symbols.keys():
    #          position = (
    #              f"({symbols[name].position[0]}:{symbols[name].position[1]})"
    #              if symbols[name].position != "/"
    #              else "/"
    #          )
    #          output += (
    #              f"{name},"
    #              f"{symbols[name].get_type()},"
    #              f"{symbols[name].datatype},"
    #              f"{position},"
    #              f"{symbols[name].value}\n"
    #          )
    #      with open(global_vars.outbase + ".csv", "w", encoding="utf-8") as fout:
    #          fout.write(output)
