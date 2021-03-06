import global_vars
from ast_node import PicoCNode


class ASTBuilder:
    """Provides methods for ast construction"""

    def __init__(self):
        self.root: PicoCNode = None
        self.current_node: PicoCNode = None
        self.return_nodes = {}

    def CN(self) -> PicoCNode:
        """Current node

        :returns: Node
        """
        return self.current_node

    def down(self, classname):
        """go one layer down in the abstract syntax tree

        :returns: None
        """
        # during tasting actions are disallowed
        if global_vars.is_tasting:
            return

        new_node = classname()

        if not self.root:
            self.root = new_node
        else:
            self.current_node.add_child(new_node)

        savestate_node = self.current_node

        # deeper grammar rules have to be called with a new current_node
        self.current_node = new_node

        return savestate_node

    def up(self, savestate_node):
        """go one layer up in the abstract syntax tree

        :returns: None
        """
        # during tasting actions are disallowed
        if global_vars.is_tasting:
            return

        # grammar rules called on the same layer have to be called with the
        # same old current_node again
        self.current_node = savestate_node

    def save(self, fname):
        """Save a node"""
        if global_vars.is_tasting:
            return

        if not self.return_nodes.get(fname):
            self.return_nodes[fname] = [self.current_node]
        else:
            self.return_nodes[fname] += [self.current_node]

    def go_back(self, fname):
        if global_vars.is_tasting:
            return

        return_node = self.return_nodes[fname].pop()
        return_node.children.pop()
        return_node.children += self.current_node.children
        self.current_node = return_node

    def discard(self, fname):
        if global_vars.is_tasting:
            return

        self.return_nodes[fname].pop()

    def __repr__(self):
        return str(self.root)
