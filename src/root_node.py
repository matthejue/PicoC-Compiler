from abstract_syntax_tree import ASTNode


class Root(ASTNode):
    def __repr__(self):
        return f"{self.children[0]}"

    def update_match_args(self, ):
        self.root_file = self.children[0]

    __match_args__ = ("root_file", )

    def visit(self, ):
        self.update_match_args()

        self.root_file.visit()
