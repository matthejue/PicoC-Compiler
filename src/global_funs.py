from colormanager import ColorManager as CM
import errors
import itertools
import global_vars
import picoc_nodes as pn
import sys
import os


def overwrite(old, replace_with, idx, color=""):
    return (
        old[:idx]
        + color
        + replace_with
        + (CM().RESET_ALL if color else "")
        + old[idx + len(replace_with) :]
    )


def set_to_str(tokens: set):
    tokens = set(global_vars.MAP_NAME_TO_SYMBOL.get(elem, elem) for elem in tokens)
    return " or ".join(
        CM().BLUE + elem + CM().RESET_ALL
        for elem in (
            tokens
            if global_vars.args.verbose
            else itertools.islice(tokens, global_vars.MAX_PRINT_OUT_TOKENS + 1)
        )
        if "ANON" not in elem
    )


def args_to_str(args: list):
    if args:
        # this function only gets called in case of an error, so the verbose
        # option doesn't have to be reset, because execution ends anyways
        global_vars.args.verbose = True
        return ("argument " if len(args) == 1 else "arguments ") + ", ".join(
            f"{CM().BLUE}'" + convert_to_single_line(arg) + f"'{CM().RESET_ALL}"
            for arg in args
        )
    else:
        return "no arguments"


def convert_to_single_line(stmt):
    return "".join(list(map(lambda line: line.lstrip(), str(stmt).split("\n"))))


def bug_in_compiler(*args):
    import inspect

    # return name of caller of this function
    raise errors.BugInCompiler(inspect.stack()[1][3], args_to_str(args))


def bug_in_interpreter(*args):
    import inspect

    # return name of caller of this function
    raise errors.BugInInterpreter(inspect.stack()[1][3], args_to_str(args))


def remove_extension(fname):
    # if there's no '.' rindex raises a exception, find returns -1
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


def only_keep_path(fname):
    index_of_path_end = fname.rfind("/")
    if index_of_path_end == -1:
        return "./"
    return fname[: index_of_path_end + 1]


def subheading(heading, terminal_width, symbol):
    return f"{symbol * ((terminal_width - len(heading) - 2) // 2 + (1 if (terminal_width - len(heading)) % 2 else 0))} {heading} {symbol * ((terminal_width - len(heading) - 2) // 2)}"


def filter_out_comments(instrs):
    if not global_vars.args.verbose:
        return instrs
    return filter(
        lambda instr: not isinstance(instr, pn.SingleLineComment),
        instrs,
    )


def strip_multiline_string(multiline_str):
    """helper function to make mutlineline string usable on different
    indent levels

    :grammar: grammar specification
    :returns: None
    """
    multiline_str = "".join([i.lstrip() + "\n" for i in multiline_str.split("\n")[:-1]])
    # every code piece ends with \n, so the last element can always be poped
    return multiline_str


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


def get_most_used_interpret_opts():
    with open(
        f"{os.path.dirname(sys.argv[0])}/../most_used_interpret_opts.txt",
        "r",
        encoding="utf-8",
    ) as fin:
        most_used_opts = fin.read()
    return most_used_opts
