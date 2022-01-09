from abstract_syntax_tree import ASTNode
from function_nodes import MainFunction


class File(ASTNode):
    def __repr__(self, ):
        acc = f"({self.value}"
        for child in self.children:
            acc += f" {child}"
        return acc + ")"

    def _update_match_args(self, ):
        for (i, child) in enumerate(self.children):
            if isinstance(child, MainFunction):
                break
        else:
            i = 0
            # raise NoMainFunctionError()
        self.main_function = self.children[i]
        self.functions = self.children[:i] + self.children[i + 1:]

    def visit(self, ):
        self._update_match_args()
        self.main_function.visit()
