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
            sep = ", " if i > 0 else ""
            indent = " " * (depth + 2)

            match child:
                case list() if not child:
                    acc += f"{sep}\n{indent}[]"

                case list():
                    acc += f"{sep}\n{indent}["
                    for j, list_child in enumerate(child):
                        sub_sep = ", " if j > 0 else ""
                        acc += f"{sub_sep}{list_child.__repr__(depth + 4)}"
                    acc += f"\n{indent}]"

                case str() | int():
                    acc += f"{sep}'{child}'"

                case _:
                    acc += f"{sep}{child.__repr__(depth + 2)}"


        return acc + ")"
