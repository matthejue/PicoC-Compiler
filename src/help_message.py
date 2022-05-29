import os
import sys
import global_vars
from colorizer import colorize_help_page
from global_funs import (
    strip_multiline_string,
    get_most_used_compile_opts,
    get_most_used_interpret_opts,
)


def heading(heading, terminal_width, symbol):
    return f"""{symbol * terminal_width}
    {symbol + ' ' + ' ' * ((terminal_width - len(heading) - 6) // 2 +
    (1 if (terminal_width - len(heading) - 6) % 2 else 0))}`{heading}`{' ' *
    ((terminal_width - len(heading) - 6) // 2) + ' ' + symbol}
    {symbol * terminal_width}
    """


def wrap_text(text, terminal_width):
    lines = text.split("\n")
    for l_idx, line in enumerate(lines):
        if len(line) > terminal_width:
            for idx in range(terminal_width, -1, -1):
                if line[idx] == " ":
                    lines.insert(l_idx + 1, line[idx + 1 :])
                    lines[l_idx] = line[:idx]
                    break
    return "\n".join(lines)


def generate_help_message():
    try:
        terminal_width = os.get_terminal_size().columns if sys.stdin.isatty() else 79
    except OSError:
        terminal_width = 79
    description = wrap_text(
        strip_multiline_string(
            f"""
    {heading("Synopsis", terminal_width, '=')}
    Usage: picoc_compiler / compile [-i] [-p] [-l LINES] [-v] [-c] [-d] [-h] [-R] [-B PROCESS_BEGIN] [-D DATASEGMENT_SIZE] [-U UART_SIZE] [-S SRAM_SIZE] [infile]

    Compiles PicoC Code into RETI Code.

    {heading("Positional arguments", terminal_width, '~')}
    infile
    > input file with PicoC Code. In the shell this is interpreted as string with PicoC Code

    {heading("Main optional arguments", terminal_width, '~')}
    -i, --intermediate-stages
    >  shows intermediate stages of compilation, inter alia tokens, derivation trees, abstract syntax trees which implies the abstract syntax trees after the different passes. If the --verbose option is activated, the nodes of the abstract syntax trees get extra parenthesis
    -p, --print
    >  prints all file outputs to the terminal. Is always activated in the shell
    -l, --lines LINES
    >  sets the number of lines visible around a error message
    -v, --verbose
    >  inserts comments before RETI instructions that contain the PicoC statement or expression that has the same meaning as the following RETI instructions. If the --intermediate-stages option is activated, the nodes of the abstract syntax trees get extra parenthesis. If the --run option is activated, it shows the state of the RETI after each RETI instruction. Shows more expected tokens in error messages
    -c, --color
    >  colorizes the terminal output. Gets ignored in the shell. Instead in the shell colors can be toggled via the `color_toggle` command (shortcut `ct`)
    -d, --debug
    >  starts the pudb debugger at a point before the derivation tree and abstract syntax tree generation and before all passes
    -h, --help
    >  show this help message and exit. With the -c option it can be colorized

    {heading("Interpreter specific optional arguments", terminal_width, '~')}
    -R, --run
    > executes the RETI Instructions after generating them. If the --verbose option is activated, the state of the RETI can be watched after every instruction
    -B, --process_begin
    >  sets the address where the process and the codesegment begin, respectively
    -D, --datasegment_size
    >  sets the size of the the datasegment. This has to be set carefully, because if the value is set to low, the section for global static data and the stack might collide
    -U, --uart_size
    >  sets the size of the uart
    -S, --sram_size
    >  sets the size of the sram. If the generated RETI-instructions and --datasegment_size take up more space in the sram then given by the --sram-size option, then the sram size will be set to --process-begin + #RETI-instructions + --datasegment-size

    {heading("PicoC", terminal_width, '=')}
    PicoC is a subset of C including the primitive datatypes int, char and void, the derived datatypes array, struct and pointer, if / else statements (including the combination of if and else, if else), while and do while statements, arithmetic expressions, build with the help of the binary operators `+`, `-`, `*`, `/`, `%`, `&`, `|`, `^` and unary operators `-`, `~`, logic expressions, build with the help of comparison relations `==`, `!=`, `<`, `>`, `<=`, `>=` and logical connectives `!`, `&&`, `||` and assignments build with the assignment operator `=`.

    Statements have to be enclosed within functions that can call eath other and among this functions, there has to be a 'main' function that marks the start of the execution of the sequence of statements within the functions or rather the execution of RETI instructions that get compiled out of this RETI statements. Statements can contain other statements like e.g. if / else and while / do while or expressions like e.g. assignments have on their right handside.

    The code can be commented with single line (`//`) and multiline comments (`/*` and `*/`).

    {heading("Shell", terminal_width, '=')}
    If called without arguments, a shell is going to open.

    In the shell the cursor can be moved with the <left> and <right> arrow key. Previous and next commands can be retrieved with the <up> and <down> arrow key. A command can be completed with <tab>.

    In the shell "commands" like `compile`, `most_used`, `color_toggle`, `history` etc. can be executed.

    The shell can be exited again by typing `quit`.

    {heading("compile command", terminal_width, '~')}
    PicoC Code can be compiled into RETI Code with the `compile <cli options> "<code>";` command (shortcut `cpl`).
    The cli options are the same as for calling the compiler from outside, except for the `infile` argument which is interpreted as string with PicoC Code and which will be compiled as if it was enclosed in a main function.

    {heading("most_used command", terminal_width, '~')}
    If you don't want to type the most likely used cli options out every time, you can use the `most_used "<code>";` command (shortcut `mu`).
    It's a shortcut for:

    `compile {get_most_used_interpret_opts()} "<code>";`

    and shrinks it down to:

    `most_used "<code>";`

    {heading("history command", terminal_width, '~')}
    To geht an overview over all previously executed commands, use the `history` command without any arguments.

    If you want to select one of the previously executed commands, this can be done by going back and forth in history with <up> and <down> or be searching the command with ctrl+r by providing a substring of the desired command.

    If you want to execute one of the commands in the history again, this can either done by "selecting" it and executing the choosen command or by looking up the <index> of the command with `history` and executing `history -r <index>`.

    If you want to change something about a command that was already executed, you can do that by "selecting" it and changing the choosen command or by looking up the <index> of the command with `history` and executing `history -e <index>`. This will open the choosen command in the default Editor (which is definid with the $EDITOR variable under Unix systems) where the command can be edited. When saving and quiting out of the editor the edited command will be executed.

    The history will get saved to the file `~/.config/pico_c_compiler/history.json` if this file exists under this path.

    {heading("color_toggle command", terminal_width, '~')}
    If you want to have colorized output, this options can be toggled with the `color_toggle` command (shortcut `ct`).

    The truth value of this option will be saved between sessions if the file `~/.config/pico_c_compiler/settings.conf` with the option `color_on: <truth_value>` exists.

    {heading("help command", terminal_width, '~')}
    If you want to see the help page from within the shell, enter `help` (shortcut `?`). The help page is the same as the one that can be viewed with the -h option.

    {heading("Multiline Command", terminal_width, '~')}
    Multiline commands can be written over multiple lines by hitting <enter> and terminating it with a `;` at the end.
    The `compile` and `most_used` command are multiline commands and thus always have to end with a `;`.

    {heading("Redirect output to file", terminal_width, '~')}
    If you want to copy the shell output to a file, enter `command > <filepath>`.
    If you want to append something to a file, enter `command >> <filepath>`.

    {heading("Copy output to clipboard", terminal_width, '~')}
    If you want to copy the shell output to your clipboard, enter `command >`.
    If you want to append something to your current clipboard copy, enter `command >>`.

    {heading("Execute OS level commands and pipe operator", terminal_width, '~')}
    If you want to execute a OS level command, use the `!` operator, e.g. `!ls`.
    If you want to pipe the shell output to a OS level command, use the pipe operator `|`, e.g. `help | wc`.

    {heading("Misc", terminal_width, '=')}
    If you discover any bugs, please report them under https://github.com/matthejue/PicoC-Compiler/issues/new/choose, thank you ^_^
    """
        ),
        terminal_width,
    )
    return colorize_help_page(description) if global_vars.args.color else description
