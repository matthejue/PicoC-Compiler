from lark.visitors import Visitor
from lark.tree import Tree
from lark.lexer import Token
from global_funs import remove_extension


class DTVisitorPicoC(Visitor):
    def file(self, tree: Tree):
        tree.children[0] = Token(
            tree.children[0].type,
            remove_extension(tree.children[0].value) + ".dt",
            tree.children[0].line,
            tree.children[0].column,
            tree.children[0].end_line,
            tree.children[0].end_column,
        )


class DTVisitorRETI(Visitor):
    def program(self, tree: Tree):
        tree.children[0] = Token(
            tree.children[0].type,
            remove_extension(tree.children[0].value) + ".rdt",
            tree.children[0].line,
            tree.children[0].column,
            tree.children[0].end_line,
            tree.children[0].end_column,
        )


class DTSimpleVisitorPicoC(Visitor):
    def _return_deepest_tree(self, tree: Tree):
        # array_decl made all continuation nodes to the right
        current_tree = tree
        while current_tree.children[1].data.value != "name":
            current_tree = current_tree.children[1]
        return current_tree

    # ----------------------------- L_Assign_Alloc ----------------------------
    def alloc(self, tree: Tree):
        pre_name_tree = self._return_deepest_tree(tree.children[1])
        type_specifier = tree.children[0]
        tree.children[0] = tree.children[1]
        tree.children[1] = pre_name_tree.children[1]
        pre_name_tree.children[1] = type_specifier

    # -------------------------------- L_Array --------------------------------
    def array_decl(self, tree: Tree):
        pntr_decl_tree = tree.children[0]
        tree.children[0] = tree.children[1]
        tree.children[1] = pntr_decl_tree

    # --------------------------------- L_File --------------------------------
    def file(self, tree: Tree):
        tree.children[0] = Token(
            tree.children[0].type,
            remove_extension(tree.children[0].value) + ".dt_simple",
            tree.children[0].line,
            tree.children[0].column,
            tree.children[0].end_line,
            tree.children[0].end_column,
        )
