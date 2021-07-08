from parser import Parser

from abstract_syntax_tree import ASTNode
from errors import SyntaxError
from lexer import TT


class ASTBuilder(Parser):

    """Provides methods for ast contrustion"""

    def __init__(self, lexer, num_lts):
        self.root = None
        self.current_node = None
        super().__init__(lexer, num_lts)

    def down(self, match_tok, cls, token):
        """go one layer down in the abstract syntax tree

        :returns: None

        """
        new_node = cls(token)
        if not self.root:
            self.root = new_node
        else:
            self.current_node.addChild(new_node)
        savestate_node = self.current_node

        # deeper grammer rules have to be called with a new current_node
        self.current_node = new_node

        return savestate_node

    def up(self, savestate_node):
        """go one layer up in the abstract syntax tree

        :returns: None

        """
        # grammer rules called on the same layer have to be called with the
        # same old current_node again
        self.current_node = savestate_node

   def match(self, tt):
       self.current_node.addChild(self.LT(1))
       super().match(tt)
