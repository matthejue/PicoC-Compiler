from ast_node import ASTNode
from function_nodes import MainFunction
from errors import Errors


class File(ASTNode):
    def update_match_args(
        self,
    ):
        self.filename = self.children[0]

        # determine the main function
        for (i, child) in enumerate(self.children):
            if isinstance(child, MainFunction):
                break
        else:
            raise Errors.NoMainFunctionError(str(self.filename))
        self.main_function = self.children[i]
        self.functions = self.children[1:i] + self.children[i + 1 :]

    __match_args__ = ("filename", "main_function", "functions")

    def visit(
        self,
    ):
        self.update_match_args()

        self.code_generator.add_code(f"# File '{self.filename}' Start\n", 0)

        self.main_function.visit()

        self.code_generator.add_code(f"# File '{self.filename}' Ende\n", 0)

    def __repr__(
        self,
    ):
        return self.to_string_show_node()
