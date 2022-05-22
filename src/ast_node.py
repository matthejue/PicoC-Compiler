from global_classes import Pos


class ASTNode:
    def __init__(self, val="", pos=Pos(-1, -1), children=[]):
        """
        :tokentype: list of TT's, first entry will be the TT of the Node
        """
        self.val: str = val
        self.pos: Pos = pos
        self.children = children

    __match_args__ = ("val", "pos")

    def __repr__(self, depth=0):
        if not self.children:
            if not self.val:
                return f"\n{' ' * depth}{self.__class__.__name__}"
            return f"\n{' ' * depth}{self.__class__.__name__}('{self.val}')"

        acc = ""

        if depth > 0:
            acc += f"\n{' ' * depth}{self.__class__.__name__}"
        else:
            acc += f"{' ' * depth}{self.__class__.__name__}"

        for child in self.children:
            if isinstance(child, list):
                if not child:
                    acc += f"\n{' ' * (depth+2)}[]"
                    continue
                acc += f"\n{' ' * (depth + 2)}["
                for child_child in child:
                    if isinstance(child_child, str) and child_child:
                        acc += f"\n{' ' * (depth+4)}// {child_child}"
                    else:
                        acc += f"{child_child.__repr__(depth+4)}"
                acc += f"\n{' ' * (depth + 2)}]"
                continue
            elif isinstance(child, str):
                if child:
                    acc += f"\n{' ' * (depth+2)}// {child}"
                continue

            acc += f"{child.__repr__(depth+2)}"

        return acc
