from global_classes import Pos
import global_vars


class ASTNode:
    def __init__(self, val="", pos=Pos(-1, -1), visible=[]):
        """
        :tokentype: list of TT's, first entry will be the TT of the Node
        """
        # necesary for reti nodes and the symbol table
        self.val: str = val
        # TODO: reason for self.val: str = val if val else self.__class__.__name__.upper()?
        self.pos: Pos = pos
        self.visible = visible

    __match_args__ = ("val", "pos")

    def __repr__(self, depth=0):
        if not self.visible:
            if not self.val:
                return f"\n{' ' * depth}{self.__class__.__name__}{'()' if global_vars.args.verbose else ''}"
            return f"\n{' ' * depth}{self.__class__.__name__}{'(' if global_vars.args.verbose else ' '}'{self.val}'{')' if global_vars.args.verbose else ''}"

        acc = ""

        if depth > 0:
            acc += f"\n{' ' * depth}{self.__class__.__name__}{'(' if global_vars.args.verbose else ' '}"
        else:
            acc += f"{' ' * depth}{self.__class__.__name__}{'(' if global_vars.args.verbose else ' '}"

        for i, child in enumerate(self.visible):
            if isinstance(child, list):
                if not child:
                    acc += f"\n{' ' * (depth+2)}[]"
                    continue
                acc += f"\n{' ' * (depth + 2)}["
                for i, list_child in enumerate(child):
                    acc += f"{', ' if i > 0 else ''}{list_child.__repr__(depth+4)}"
                acc += f"\n{' ' * (depth + 2)}]"
                continue
            elif isinstance(child, dict):
                dict_children = child.values()
                if not dict_children:
                    acc += f"\n{' ' * (depth+2)}[]"
                    continue
                acc += f"\n{' ' * (depth + 2)}["
                for i, dict_child in enumerate(dict_children):
                    acc += f"{', ' if i > 0 else ''}{dict_child.__repr__(depth+4)}"
                acc += f"\n{' ' * (depth + 2)}]"
                continue

            acc += f"{', ' if i > 0 else ''}{child.__repr__(depth+2)}"

        return acc + (f"\n{' ' * depth})" if global_vars.args.verbose else "")
