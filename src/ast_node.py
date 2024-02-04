from util_classes import Pos
import global_vars
from colormanager import ColorManager as CM


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
                return f"\n{' ' * depth}{CM().BLUE}{self.__class__.__name__}{CM().RESET}{CM().CYAN}{'()' if global_vars.args.double_verbose else ''}{CM().RESET}"
            return f"\n{' ' * depth}{CM().BLUE}{self.__class__.__name__}{CM().RESET}{CM().CYAN}{'(' if global_vars.args.double_verbose else ' '}{CM().RESET}{CM().RED}'{self.val}'{CM().RESET}{CM().CYAN}{')' if global_vars.args.double_verbose else ''}{CM().RESET}"

        acc = ""

        if depth > 0:
            acc += f"\n{' ' * depth}{CM().BLUE}{self.__class__.__name__}{CM().RESET}{CM().CYAN}{'(' if global_vars.args.double_verbose else ' '}{CM().RESET}"
        else:
            acc += f"{' ' * depth}{CM().BLUE}{self.__class__.__name__}{CM().RESET}{CM().CYAN}{'(' if global_vars.args.double_verbose else ' '}{CM().RESET}"

        for i, child in enumerate(self.visible):
            if isinstance(child, list):
                if not child:
                    acc += f"{', ' if i > 0 else ''}\n{' ' * (depth+2)}{CM().CYAN}[]{CM().RESET}"
                    continue
                acc += f"{', ' if i > 0 else ''}\n{' ' * (depth + 2)}{CM().CYAN}[{CM().RESET}"
                for i, list_child in enumerate(child):
                    acc += f"{', ' if i > 0 else ''}{list_child.__repr__(depth+4)}"
                acc += f"\n{' ' * (depth + 2)}{CM().CYAN}]{CM().RESET}"
                continue
            elif isinstance(child, dict):
                dict_children = child.values()
                if not dict_children:
                    acc += f"{', ' if i > 0 else ''}\n{' ' * (depth+2)}{CM().CYAN}[]{CM().RESET}"
                    continue
                acc += f"{', ' if i > 0 else ''}\n{' ' * (depth + 2)}{CM().CYAN}[{CM().RESET}"
                for i, dict_child in enumerate(dict_children):
                    acc += f"{', ' if i > 0 else ''}{dict_child.__repr__(depth+4)}"
                acc += f"\n{' ' * (depth + 2)}{CM().CYAN}]{CM().RESET}"
                continue

            acc += f"{', ' if i > 0 else ''}{child.__repr__(depth+2)}"

        return acc + (
            f"\n{' ' * depth}{CM().CYAN}){CM().RESET}"
            if global_vars.args.double_verbose
            else ""
        )
