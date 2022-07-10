import global_vars
import cmd2
from error_handler import ErrorHandler
import symbol_table as st
import picoc_nodes as pn
import reti_nodes as rn
from colormanager import ColorManager as CM
import os
import sys
from help_message import generate_help_message
from lark.lark import Lark
from dt_visitor_picoc import DTVisitorPicoC, DTSimpleVisitorPicoC
from ast_transformer_picoc import ASTTransformerPicoC
from passes import Passes
from global_funs import remove_extension, subheading, throw_error
from interp_reti import RETIInterpreter


class OptionHandler(cmd2.Cmd):
    cli_args_parser = cmd2.Cmd2ArgumentParser(add_help=False)
    # ----------------------------- PicoC_Compiler ----------------------------
    cli_args_parser.add_argument("infile", nargs="?")
    # ------------------- PicoC_Compiler + RETI_Interpreter -------------------
    cli_args_parser.add_argument("-i", "--intermediate_stages", action="store_true")
    cli_args_parser.add_argument("-p", "--print", action="store_true")
    cli_args_parser.add_argument("-l", "--lines", type=int, default=2)
    cli_args_parser.add_argument("-v", "--verbose", action="store_true")
    cli_args_parser.add_argument("-vv", "--double_verbose", action="store_true")
    cli_args_parser.add_argument("-c", "--color", action="store_true")
    cli_args_parser.add_argument("-d", "--debug", action="store_true")
    cli_args_parser.add_argument("-t", "--traceback", action="store_true")
    cli_args_parser.add_argument("-e", "--example", action="store_true")
    # ---------------------------- RETI_Interpreter ---------------------------
    cli_args_parser.add_argument("-R", "--run", action="store_true")
    cli_args_parser.add_argument("-B", "--process_begin", type=int, default=3)
    cli_args_parser.add_argument("-D", "--datasegment_size", type=int, default=32)

    HISTORY_FILE = os.path.expanduser("~") + "/.config/pico_c_compiler/history.json"
    SETTINGS_FILE = os.path.expanduser("~") + "/.config/pico_c_compiler/settings.conf"
    PERSISTENT_HISTORY_LENGTH = 100

    def __init__(self):
        self.terminal_width = (
            os.get_terminal_size().columns if sys.stdin.isatty() else 79
        )
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

        self._compl(["void main() {"] + code.split("\n") + ["}"])
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

        self._compl(pico_c_in)

    def _compl(self, code):
        if global_vars.args.debug:
            __import__("pudb").set_trace()

        # add the filename to the start of the code
        code_with_file = (
            ("./" if not global_vars.args.infile.startswith("./") else "")
            + f"{global_vars.args.infile}\n"
            + code
        )

        if global_vars.args.intermediate_stages and global_vars.args.print:
            print(subheading("Code", self.terminal_width, "-"))
            print(f"// {global_vars.args.infile}:\n" + code)

        parser = Lark.open(
            f"{os.path.dirname(os.path.realpath(sys.argv[0]))}/concrete_syntax_picoc.lark",
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
            error_handler.handle(self._tokens_option, code_with_file, "Tokens")

        dt = error_handler.handle(parser.parse, code_with_file)

        dt_visitor_picoc = DTVisitorPicoC()
        error_handler.handle(dt_visitor_picoc.visit, dt)

        if global_vars.args.intermediate_stages:
            self._dt_option(dt, "Derivation Tree")

        dt_simple_visitor_picoc = DTSimpleVisitorPicoC()
        error_handler.handle(dt_simple_visitor_picoc.visit, dt)

        if global_vars.args.intermediate_stages:
            self._dt_option(dt, "Derivation Tree Simple")

        ast_transformer_picoc = ASTTransformerPicoC()
        ast = error_handler.handle(ast_transformer_picoc.transform, dt)

        if global_vars.args.intermediate_stages:
            self._ast_option(ast, "Abstract Syntax Tree")

        passes = Passes()

        picoc_shrink = error_handler.handle(passes.picoc_shrink, ast)

        if global_vars.args.intermediate_stages:
            self._output_pass(picoc_shrink, "PicoC Shrink")

        picoc_blocks = error_handler.handle(passes.picoc_blocks, picoc_shrink)

        if global_vars.args.intermediate_stages:
            self._output_pass(picoc_blocks, "PicoC Blocks")

        picoc_mon = error_handler.handle(passes.picoc_mon, picoc_blocks)

        if global_vars.args.intermediate_stages:
            self._output_pass(picoc_mon, "PicoC Mon")

        if global_vars.args.intermediate_stages:
            self._st_option(passes.symbol_table, "Symbol Table")

        reti_blocks = error_handler.handle(passes.reti_blocks, picoc_mon)

        if global_vars.args.intermediate_stages:
            self._output_pass(reti_blocks, "RETI Blocks")

        reti_patch = error_handler.handle(passes.reti_patch, reti_blocks)

        if global_vars.args.intermediate_stages:
            self._output_pass(reti_patch, "RETI Patch")

        reti = error_handler.handle(passes.reti, reti_patch)

        if global_vars.args.intermediate_stages:
            self._output_pass(reti, "RETI")

        if global_vars.args.run:
            if global_vars.args.print:
                print(subheading("RETI Run", self.terminal_width, "-"))
            reti_interp = RETIInterpreter()
            error_handler.handle(reti_interp.interp_reti, reti)

    def _tokens_option(self, code_with_file, heading):
        parser = Lark.open(
            f"{os.path.dirname(os.path.realpath(sys.argv[0]))}/concrete_syntax_picoc.lark",
            lexer="basic",
            priority="normal",
            parser="earley",
            start="file",
            maybe_placeholders=False,
            propagate_positions=True,
        )
        tokens = list(parser.lex(code_with_file))

        if global_vars.args.print:
            print(subheading(heading, self.terminal_width, "-"))
            print(tokens)

        if global_vars.path:
            with open(
                remove_extension(tokens[0].value) + ".tokens",
                "w",
                encoding="utf-8",
            ) as fout:
                fout.write(str(tokens))

    def _dt_option(self, dt, heading):
        if global_vars.args.print:
            print(subheading(heading, self.terminal_width, "-"))
            print(dt.pretty())

        if global_vars.path:
            with open(dt.children[0].value, "w", encoding="utf-8") as fout:
                fout.write(dt.pretty())

    def _ast_option(self, ast: pn.File, heading):
        if global_vars.args.print:
            print(subheading(heading, self.terminal_width, "-"))
            print(ast)

        if global_vars.path:
            match ast:
                case pn.File(pn.Name(val)):
                    with open(val, "w", encoding="utf-8") as fout:
                        fout.write(str(ast))

    def _output_pass(self, pass_ast, heading):
        if global_vars.args.print:
            print(subheading(heading, self.terminal_width, "-"))
            print(pass_ast)

        if global_vars.path:
            match pass_ast:
                case pn.File(pn.Name(val)):
                    with open(val, "w", encoding="utf-8") as fout:
                        fout.write(str(pass_ast))
                case rn.Program(rn.Name(val)):
                    with open(val, "w", encoding="utf-8") as fout:
                        fout.write(str(pass_ast))
                case _:
                    throw_error(pass_ast)

    def _st_option(self, symbol_table: st.SymbolTable, heading):
        if global_vars.args.print:
            print(subheading(heading, self.terminal_width, "-"))
            print(symbol_table)

        if global_vars.path:
            with open(
                global_vars.path + global_vars.basename + ".st",
                "w",
                encoding="utf-8",
            ) as fout:
                fout.write(str(symbol_table))
