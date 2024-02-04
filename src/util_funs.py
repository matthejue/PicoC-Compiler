from colormanager import ColorManager as CM
import errors
import itertools
import global_vars
import picoc_nodes as pn
from util_classes import Pos
import re


def overwrite(old, replace_with, idx, color=""):
    return (
        old[:idx]
        + color
        + replace_with
        + (CM().RESET_ALL if color else "")
        + old[idx + len(replace_with) :]
    )


def tokennames_to_str(tokens: set):
    tokens = set(global_vars.TOKENNAME_TO_SYMBOL.get(elem, elem) for elem in tokens)
    return " or ".join(
        CM().BLUE + elem + CM().RESET_ALL
        for elem in (
            tokens
            if global_vars.args.double_verbose
            else itertools.islice(tokens, global_vars.max_print_out_elements + 1)
        )
        if "ANON" not in elem
    )


def nodes_to_str(nodes: list):
    nodes = [global_vars.NODE_TO_Symbol.get(elem, elem) for elem in nodes]
    return " or ".join(
        CM().BLUE + elem + CM().RESET_ALL
        for elem in (
            nodes
            if global_vars.args.double_verbose
            else itertools.islice(nodes, global_vars.max_print_out_elements + 1)
        )
    )


def args_to_str(args: list):
    if args:
        # this function only gets called in case of an error, so the verbose
        # option doesn't have to be reset, because execution ends anyways
        return ("argument " if len(args) == 1 else "arguments ") + ", ".join(
            f"{CM().BLUE}'" + convert_to_single_line(arg) + f"'{CM().RESET_ALL}"
            for arg in args
        )
    else:
        return "no arguments"


def repr_single_line(self, depth=0):
    if not self.visible:
        if not self.val:
            return f"\n{' ' * depth}{CM().BLUE}{self.__class__.__name__}{CM().RESET}{CM().CYAN}{'()' if global_vars.args.double_verbose else ''}{CM().RESET}"
        return f"\n{' ' * depth}{CM().BLUE}{self.__class__.__name__}{CM().RESET}{CM().CYAN}{'(' if global_vars.args.double_verbose else ' '}{CM().RESET}{CM().RED}'{self.val}'{CM().RESET}{CM().CYAN}{')' if global_vars.args.double_verbose else ''}{CM().RESET}"

    acc = ""

    if depth > 0:
        acc += f"\n{' ' * depth}{CM().BLUE}{self.__class__.__name__}{CM().RESET}{CM().CYAN}{'(' if global_vars.args.double_verbose else ' '}{CM().RESET}"
    else:
        acc += f"{' ' * depth}{CM().BLUE}{self.__class__.__name__}{CM().RESET}{CM().CYAN}{'(' if global_vars.args.double_verbose else ' '}{CM().RESET}"

    for i, child in enumerate(self.visible):
        match child:
            case list():
                if not child:
                    acc += f"{', ' if i > 0 else ''}\n{' ' * (depth+2)}{CM().CYAN}[]{CM().RESET}"
                    continue

                acc += f"{', ' if i > 0 else ''}\n{' ' * (depth + 2)}{CM().CYAN}[{CM().RESET}"
                for i, list_child in enumerate(child):
                    match list_child:
                        case (
                            pn.If()
                            | pn.IfElse()
                            | pn.While()
                            | pn.DoWhile()
                            | pn.Block()
                            | pn.FunDef()
                            | pn.FunDecl()
                            | pn.StructDecl()
                        ):
                            pass
                        case _:
                            acc += f"\n{' ' * (depth + 4)}{convert_to_single_line(list_child)}"
                            continue
                    acc += f"{', ' if i > 0 else ''}{list_child.__repr__(depth+4)}"
                acc += f"\n{' ' * (depth + 2)}{CM().CYAN}]{CM().RESET}"
                continue
            case dict():
                dict_children = child.values()
                if not dict_children:
                    acc += f"{', ' if i > 0 else ''}\n{' ' * (depth+2)}{CM().CYAN}[]{CM().RESET}"
                    continue
                acc += f"{', ' if i > 0 else ''}\n{' ' * (depth + 2)}{CM().CYAN}[{CM().RESET}"
                for i, dict_child in enumerate(dict_children):
                    acc += f"{', ' if i > 0 else ''}{dict_child.__repr__(depth+4)}"
                acc += f"\n{' ' * (depth + 2)}{CM().CYAN}]{CM().RESET}"
                continue
            case pn.Atom():
                acc += f"\n{' ' * (depth + 2)}{convert_to_single_line(child)}"
                continue
            case _:
                pass

        acc += f"{', ' if i > 0 else ''}{child.__repr__(depth+2)}"

    return acc + (
        f"\n{' ' * depth}{CM().CYAN}){CM().RESET}"
        if global_vars.args.double_verbose
        else ""
    )


def convert_to_single_line(stmt, no_colors=False):
    if no_colors:
        CM().color_off()
    tmp = global_vars.args.double_verbose
    global_vars.args.double_verbose = True
    single_line = "".join(list(map(lambda line: line.lstrip(), str(stmt).split("\n"))))
    global_vars.args.double_verbose = tmp
    if no_colors:
        if global_vars.args.color:
            CM().color_on()
        else:
            CM().color_off()
    return single_line


def find_first_pos_in_node(nodes):
    res = []
    for node in nodes:
        if isinstance(node, list):
            res += find_first_pos_in_node(node)
        elif node.pos == Pos(-1, -1):
            res += find_first_pos_in_node(node.visible)
        else:  # node.pos != Pos(-1, -1):
            return [node, node.pos]
    return res


def throw_error(*nodes):
    node_name_and_node_pos = find_first_pos_in_node(nodes)
    if node_name_and_node_pos:
        node_name, node_pos = node_name_and_node_pos
        raise errors.NodeError(convert_to_single_line(str(node_name)), node_pos)
    else:
        raise Exception


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


def get_extension(fname):
    # if there's no '.' rindex raises a exception, find returns -1
    idx_of_extension_start = fname.rfind(".")
    if idx_of_extension_start == -1:
        return fname
    return fname[idx_of_extension_start + 1 :]


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


def filter_out_comments(instrs):
    if not (global_vars.args.verbose or global_vars.args.double_verbose):
        return instrs
    return filter(
        lambda instr: not isinstance(instr, pn.SingleLineComment),
        instrs,
    )


def subheading(heading, terminal_width, symbol):
    return f"{symbol * ((terminal_width - len(heading) - 2) // 2 + (1 if (terminal_width - len(heading)) % 2 else 0))} {heading} {symbol * ((terminal_width - len(heading) - 2) // 2)}"


#  def heading(heading, terminal_width, symbol):
#      return f"""{symbol * terminal_width}
#      {symbol + ' ' + ' ' * ((terminal_width - len(heading) - 6) // 2 +
#      (1 if (terminal_width - len(heading) - 6) % 2 else 0))}`{heading}`{' ' *
#      ((terminal_width - len(heading) - 6) // 2) + ' ' + symbol}
#      {symbol * terminal_width}
#      """


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


def get_test_metadata(code):
    regex = re.search(
        r"((\/\/|#) +in(put)?: *(\d+( +\d+)*) *\n)?((\/\/|#) +exp(ected)?: *(\d+( +\d+)*) *\n)?((\/\/|#) +data(segment)?: *(\d+) *\n)?(.*(\n)?)*",
        code,
    )
    global_vars.input = list(map(lambda x: int(x), regex.group(4).split())) if regex and regex.group(4) else []
    global_vars.expected = list(map(lambda x: int(x), regex.group(9).split())) if regex and regex.group(9) else []
    global_vars.datasegment = regex.group(14) if regex and regex.group(14) else 64


#  def strip_multiline_string(multiline_str):
#      """helper function to make mutlineline string usable on different
#      indent levels
#
#      :grammar: grammar specification
#      :returns: None
#      """
#      multiline_str = "".join([i.lstrip() + "\n" for i in multiline_str.split("\n")[:-1]])
#      # every code piece ends with \n, so the last element can always be poped
#      return multiline_str


#  def get_most_used_interpret_opts():
#      with open(
#          f"{os.path.dirname(os.path.realpath(sys.argv[0]))}/../most_used_compile_and_interpret_opts.txt",
#          "r",
#          encoding="utf-8",
#      ) as fin:
#          most_used_opts = fin.read()
#      return most_used_opts
