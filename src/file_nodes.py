from abstract_syntax_tree import ASTNode


class File(ASTNode):
    def __init__(self, name):
        self.value = name
        self.children = []

    def __repr__(self, ):
        acc = f"({self.value}"
        for child in self.children:
            acc += f" {child}"
        return acc + ")"
