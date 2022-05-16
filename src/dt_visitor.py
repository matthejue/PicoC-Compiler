from lark.visitors import Visitor
from lark.lexer import Token
from lark import Tree


class DTVisitor(Visitor):
    name_tree: Token
    deepest_alloc_tree: Tree

    def array_decl(self, tree):
        if tree.children[0].data.value == "name":
            self.name_tree = tree.children[0]
            self.deepest_alloc_tree = tree

    def alloc(self, tree):
        size_qual = tree.children[0]
        tree.children[0] = tree.children[1]
        self.deepest_alloc_tree.children[0] = size_qual

        tree.children[1] = self.name_tree
