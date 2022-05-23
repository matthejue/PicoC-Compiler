from lark.visitors import Visitor
from lark import Tree


class DTVisitorPicoC(Visitor):
    def _return_deepest_tree(self, tree: Tree):
        current_tree = tree
        while current_tree.children[1].data.value != "name":
            current_tree = current_tree.children[1]
        return current_tree

    # ----------------------------- L_Assign_Alloc ----------------------------
    def alloc(self, tree: Tree):
        deepest_tree = self._return_deepest_tree(tree.children[1])
        size_qual = tree.children[0]
        tree.children[0] = tree.children[1]
        tree.children[1] = deepest_tree.children[1]
        deepest_tree.children[1] = size_qual

    # -------------------------------- L_Array --------------------------------
    def array_decl(self, tree: Tree):
        left_tree = tree.children[0]
        tree.children[0] = tree.children[1]
        tree.children[1] = left_tree

    def array_init_decl(self, tree: Tree):
        left_tree = tree.children[0]
        tree.children[0] = tree.children[1]
        tree.children[1] = left_tree

    def array_init(self, tree: Tree):
        deepest_tree = tree.children[1]
        size_qual = tree.children[0]
        tree.children[0] = tree.children[1]
        tree.children[1] = deepest_tree.children[1]
        deepest_tree.children[1] = size_qual
