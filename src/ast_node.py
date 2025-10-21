import global_vars


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

    def __repr__(self, depth=0):
        if not self.visible:
            return f"\n{' ' * depth}{self.__class__.__name__}()"

        acc = ""

        if depth > 0:
            acc += "\n"
        acc += f"{' ' * depth}{self.__class__.__name__}("

        for i, child in enumerate(self.visible):
            if isinstance(child, list):
                if not child:
                    acc += f"{', ' if i > 0 else ''}\n{' ' * (depth+2)}[]"
                    continue
                acc += f"{', ' if i > 0 else ''}\n{' ' * (depth + 2)}["
                for i, list_child in enumerate(child):
                    acc += f"{', ' if i > 0 else ''}{list_child.__repr__(depth+4)}"
                acc += f"\n{' ' * (depth + 2)}]"
            elif isinstance(child, dict):
                dict_children = child.values()
                if not dict_children:
                    acc += f"{', ' if i > 0 else ''}\n{' ' * (depth+2)}[]"
                    continue
                acc += f"{', ' if i > 0 else ''}\n{' ' * (depth + 2)}["
                for i, dict_child in enumerate(dict_children):
                    acc += f"{', ' if i > 0 else ''}{dict_child.__repr__(depth+4)}"
                acc += f"\n{' ' * (depth + 2)}]"
            elif isinstance(child, str):
                acc += f"{', ' if i > 0 else ''}'{child}'"
            elif isinstance(child, int):
                acc += f"{', ' if i > 0 else ''}{child}"
            else:
                acc += f"{', ' if i > 0 else ''}{child.__repr__(depth+2)}"

        return acc + ")"
