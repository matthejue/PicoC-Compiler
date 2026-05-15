from src import picoc_nodes as pn
from src import global_vars
from src.utils.util_funs_independent import convert_to_single_line
from src.log import log

_SOURCE_ORIGIN_HIDDEN_NODE_NAMES = {
    "SingleLineComment",
    "Num"
}


class ASTNode:
    def __init__(self, visible=[]):
        # val="", 
        """
        :tokentype: list of TT's, first entry will be the TT of the Node
        """
        # necesary for reti nodes and the symbol table
        # self.val: str = val
        # TODO: reason for self.val: str = val if val else self.__class__.__name__.upper()?
        self.visible = visible

    # __match_args__ = ("val",)

    def __repr__(self, depth=0, is_file=False):
        visible = list(self.visible)
        origin_visible = _source_origin_visible(self)
        if origin_visible is not None:
            visible.append(origin_visible)
        if not visible:
            return f"\n{' ' * depth}{self.__class__.__name__}()"

        acc = ""

        acc += f"\n{' ' * depth}{self.__class__.__name__}("

        for i, child in enumerate(visible):
            acc = repr_arg_types(i, child, depth, acc, is_file=is_file)

        return acc + ")"


def _source_origin_visible(node):
    if not global_vars.args.double_verbose:
        return None
    if node.__class__.__name__ in _SOURCE_ORIGIN_HIDDEN_NODE_NAMES:
        return None
    origin = get_source_origin(node)
    if origin is None:
        return None
    source_file, source_line = origin
    return f"{source_file}:{source_line}"


def set_source_origin(node, source_file, source_line):
    if isinstance(node, ASTNode):
        node.source_file = source_file
        node.source_line = source_line
    return node


def get_source_origin(node):
    source_file = getattr(node, "source_file", None)
    source_line = getattr(node, "source_line", None)
    if source_file is None or source_line is None:
        return None
    return source_file, source_line


def copy_source_origin(target, source):
    if not isinstance(target, ASTNode):
        from src.utils.util_funs_dependent import throw_error
        throw_error(target)
    if getattr(target, "suppress_source_origin", False):
        return target
    # Do not overwrite an existing origin. For example, While/DoWhile body
    # rewriting calls _inherit_origin_many(..., sub_stmt); without this guard,
    # condition-related jumps already marked with the condition/loop origin
    # would be overwritten with the current body statement's origin.
    if get_source_origin(target) is not None:
        return target
    origin = get_source_origin(source)
    if origin is not None:
        target.source_file, target.source_line = origin
    return target


def copy_source_origin_to_many(targets, source):
    return [copy_source_origin(target, source) for target in targets]


def suppress_source_origin(node):
    if isinstance(node, ASTNode):
        node.suppress_source_origin = True
    return node


def repr_arg_types(i, arg, depth, acc, *, is_block=False, is_file=False):
    sep = ", " if i > 0 else ""
    depth2 = depth + 2
    indent2 = " " * (depth2)
    depth4 = depth + 4
    indent4 = " " * (depth4)

    match arg:
        case list() if not arg:
            acc += sep if is_block else f"{sep}\n{indent2}[]"

        case list():
            acc += sep if is_block else f"{sep}\n{indent2}["
            for j, list_child in enumerate(arg):
                sub_sep = ", " if j > 0 else ""
                subindent = indent2 if is_block else indent4
                subdepth = depth2 if is_block else depth4

                match list_child:
                    # Nested control-flow / structure nodes
                    case (
                        pn.If()
                        | pn.IfElse()
                        | pn.While()
                        | pn.DoWhile()
                        | pn.Block()
                        | pn.FunDef()
                        | pn.FunDecl()
                        | pn.FunPtrDecl()
                        | pn.StructDecl()
                    ):
                        acc += f"{sub_sep}{list_child.__repr__(subdepth)}"

                    # Everything else gets converted to a single line
                    case _:
                        # log("list_child", convert_to_single_line(list_child))
                        acc += f"{"" if is_block or is_file else sub_sep}\n{subindent}{convert_to_single_line(list_child)}"
            acc += "" if is_block else f"\n{indent2}]"
        case str() | int():
            acc += f"{sep}'{arg}'"

        case _:
            acc += f"{sep}{arg.__repr__(depth2)}"

    return acc
