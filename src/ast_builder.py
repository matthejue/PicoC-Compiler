import global_vars
from abstract_syntax_tree import ASTNode
from dummy_nodes import NT


class ASTBuilder:
    """Provides methods for ast construction"""
    def __init__(self, fname):
        self.root = NT.File(fname)
        self.current_node = NT.File(fname)

    def CN(self) -> ASTNode:
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
        # TODO: remove when it's sure this won't ever be needed anymore
        #  if not self.root:
        #  self.root = new_node
        #  else:
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
