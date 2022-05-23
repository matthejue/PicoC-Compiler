from colormanager import ColorManager as CM
from errors import Errors
import itertools
import global_vars


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
        CM().RED + elem + CM().RESET_ALL
        for elem in (
            tokens
            if global_vars.args.verbose
            else itertools.islice(tokens, global_vars.MAX_PRINT_OUT_TOKENS + 1)
        )
        if "ANON" not in elem
    )


def args_to_str(args: list):
    if args:
        global_vars.args.verbose = True
        return ("argument " if len(args) == 1 else "arguments ") + ", ".join(
            f"{CM().BLUE}'"
            + "".join(list(map(lambda line: line.lstrip(), str(arg).split("\n"))))
            + f"'{CM().RESET_ALL}"
            for arg in args
        )
    else:
        return "no arguments"


def bug_in_compiler_error(*args):
    import inspect

    # return name of caller of this function
    raise Errors.BugInCompiler(inspect.stack()[1][3], args_to_str(args))


def remove_extension(fname):
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


def only_keep_path(fname):
    index_of_path_end = fname.rfind("/")
    if index_of_path_end == -1:
        return "./"
    return fname[: index_of_path_end + 1]


def subheading(heading, terminal_width, symbol):
    return f"{symbol * ((terminal_width - len(heading) - 2) // 2 + (1 if (terminal_width - len(heading)) % 2 else 0))} {heading} {symbol * ((terminal_width - len(heading) - 2) // 2)}"