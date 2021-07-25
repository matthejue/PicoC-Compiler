class ASTBuilder:

    """Provides methods for ast construction"""

    def __init__(self):
        self.root = None
        self.current_node = None

    def addChild(self, token_or_node):
        """

        :returns: None

        """
        self.current_node.addChild(token_or_node)

    def down(self, classname, token):
        """go one layer down in the abstract syntax tree

        :returns: None

        """
        new_node = classname(token)
        if not self.root:
            self.root = new_node
        else:
            self.current_node.addChild(new_node)
        savestate_node = self.current_node

        # deeper grammar rules have to be called with a new current_node
        self.current_node = new_node

        return savestate_node

    def up(self, savestate_node):
        """go one layer up in the abstract syntax tree

        :returns: None

        """
        # grammar rules called on the same layer have to be called with the
        # same old current_node again
        self.current_node = savestate_node
