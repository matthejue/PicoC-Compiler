from src import picoc_nodes as pn
from src.utils.util_funs_independent import convert_to_single_line
from src.log import log

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
        if not self.visible:
            return f"\n{' ' * depth}{self.__class__.__name__}()"

        acc = ""

        acc += f"\n{' ' * depth}{self.__class__.__name__}("

        for i, child in enumerate(self.visible):
            acc = repr_arg_types(i, child, depth, acc, is_file=is_file)

        return acc + ")"


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
