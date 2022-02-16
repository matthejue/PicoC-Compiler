import os
import global_vars
from abstract_syntax_tree import strip_multiline_string
from colorizer import colorize_help_page


def header(heading, terminal_width):
    return f"""{'=' * terminal_width}
    {'= ' + ' ' * ((terminal_width - len(heading) - 6) // 2 +
    (1 if (terminal_width - len(heading) - 6) % 2 else 0))}`{heading}`{' ' *
    ((terminal_width - len(heading) - 6) // 2) + ' ='}
    {'=' * terminal_width}
    """


def wrap_text(text, terminal_width):
    lines = text.split('\n')
    for l_idx, line in enumerate(lines):
        if len(line) > terminal_width:
            for idx in range(terminal_width, -1, -1):
                if line[idx] == ' ':
                    lines.insert(l_idx + 1, line[idx + 1:])
                    lines[l_idx] = line[:idx]
                    break
    return "\n".join(lines)


def generate_help_message():
    try:
        terminal_width = os.get_terminal_size().columns
    except OSError:
        terminal_width = 79
    description = wrap_text(
        strip_multiline_string(f"""
    Usage: compile [-h] [-c] [-t] [-a] [-s] [-p] [-b BEGIN_DATA_SEGMENT] [-e END_DATA_SEGMENT] [-d DISTANCE] [-v] [-S SIGHT] [-C] [infile]

    Compiles PicoC Code into RETI Code.

    {header("PicoC", terminal_width)}
    PicoC is a subset of C including the datatypes int and char, if, else if and else statements, while and do while loops, arithmetic expressions, including the binary operators `+`, `-`, `*`, `/`, `%`, `&`, `|`, `^` and unary operators `-`, `~`, logic expressions, including comparison relations `==`, `!=`, `<`, `>`, `<=`, `>=` and logical connectives `!`, `&&`, `||` and assignments with the assignment operator `=`.
    The code can be commented with single line comments (`//`) and multiline comments (`/*` and `*/`).

    All statements have to be enclosed in a

    `void main() {{ /* your program */ }}`

    function.

    {header("Shell", terminal_width)}
    If called without arguments, a shell is going to open.

    In the shell the cursor can be moved with the <left> and <right> arrow key. Previous and next commands can be retrieved with the <up> and <down> arrow key. A command can be completed with <tab>.

    In the shell "commands" like `compile`, `most_used`, `color_toggle`, `history` etc. can be executed.

    The shell can be exited again by typing `quit`.

    {header("compile command", terminal_width)}
    PicoC Code can be compiled into RETI Code with the `compile <cli options> "<code>";` command (shortcut `cpl`).
    The cli options are the same as for calling the compiler from outside, except for the `infile` argument which is interpreted as string with PicoC Code and which will be compiled as if it was enclosed in a main function.

    {header("most_used command", terminal_width)}
    If you don't want to type the most likely used cli options out every time, you can use the `most_used "<code>";` command (shortcut `mu`).
    It's a shortcut for:

    `compile -c -t -a -s -p -v -b 100 -e 200 -d 20 -S 2 "<code>";`

    and shrinks it down to:

    `most_used "<code>";`

    {header("history command", terminal_width)}
    To geht an overview over all previously executed commands, use the `history` command without any arguments.

    If you want to select one of the previously executed commands, this can be done by going back and forth in history with <up> and <down> or be searching the command with ctrl+r by providing a substring of the desired command.

    If you want to execute one of the commands in the history again, this can either done by "selecting" it and executing the choosen command or by looking up the <index> of the command with `history` and executing `history -r <index>`.

    If you want to change something about a command that was already executed, you can do that by "selecting" it and changing the choosen command or by looking up the <index> of the command with `history` and executing `history -e <index>`. This will open the choosen command in the default Editor (which is definid with the $EDITOR variable under Unix systems) where the command can be edited. When saving and quiting out of the editor the edited command will be executed.

    The history will get saved to the file `~/.config/pico_c_compiler/history.json` if this file exists under this path.

    {header("color_toggle command", terminal_width)}
    If you want to have colorized output, this options can be toggled with the `color_toggle` command (shortcut `ct`).

    The truth value of this option will be saved between sessions if the file `~/.config/pico_c_compiler/settings.conf` with the option `color_on: <truth_value>` exists.

    {header("help command", terminal_width)}
    If you want to see the help page from within the shell, enter `help`. The help page is the same as the one that can be viewed with the -h option.

    {header("Multiline Command", terminal_width)}
    Multiline commands can be written over multiple lines by hitting <enter> and terminating it with a `;` at the end.
    The `compile` and `most_used` command are multiline commands and thus always have to end with a `;`.

    {header("Redirect output to file", terminal_width)}
    If you want to copy the shell output to a file, enter `command > <filepath>`.
    If you want to append something to a file, enter `command >> <filepath>`.

    {header("Copy output to clipboard", terminal_width)}
    If you want to copy the shell output to your clipboard, enter `command >`.
    If you want to append something to your current clipboard copy, enter `command >>`.

    {header("Execute OS level commands and pipe operator", terminal_width)}
    If you want to execute a OS level command, use the `!` operator, e.g. `!ls`.
    If you want to pipe the shell output to a OS level command, use the pipe operator `|`, e.g. `help | wc`.

    {header("Misc", terminal_width)}
    If you discover any bugs I would be very grateful if you could report it via email to `juergmatth@gmail.com`, attaching the malicious code to the email. ^_^

    {header("Positional arguments", terminal_width)}
      infile                input file with PicoC Code. In the shell this is interpreted as string with PicoC Code

    {header("Optional arguments", terminal_width)}
      -h, --help            show this help message and exit. With the -C option it can be colorized.
      -c, --concrete_syntax
      >                     also print the concrete syntax (content of input file). Only works if --print option is active
      -t, --tokens          also write the tokenlist
      -a, --abstract-syntax
      >                     also write the abstract syntax
      -s, --symbol_table    also write the final symbol table into a `.csv` file
      -p, --print           print all file outputs to the terminal. Is always activated in the shell. Doesn't have to be activated manually in the shell.
      -b, --begin_data_segment BEGIN_DATA_SEGMENT
      >                     where the datasegment starts (default `100`)
      -e, --end_data_segment END_DATA_SEGMENT
      >                     where the datasegment ends and where the stackpointer starts (default `200`)
      -d, --distance DISTANCE
      >                     distance of the comments from the instructions for the --verbose option. The passed value gets added to the minimum distance of 2 spaces
      -v, --verbose         also show tokentype and position for tokens, write the nodetype in front of parenthesis in the abstract syntax tree, add comments to the RETI Code
      -S, --sight SIGHT     sets the number of lines visible around a error message
      -C, --color           colorizes the terminal output. Gets ignored in the shell. Instead in the shell colors can be toggled via the `color_toggle` command (shortcut `ct`)
    """), terminal_width)
    return colorize_help_page(
        description) if global_vars.args.color else description
