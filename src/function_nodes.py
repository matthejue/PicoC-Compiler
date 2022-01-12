from abstract_syntax_tree import ASTNode, strip_multiline_string
import global_vars


class MainFunction(ASTNode):
    """Abstract Syntax Tree Node for main method"""

    start = "LOADI SP eds;\n"
    start_loc = 1

    end = "JUMP 0;\n"
    end_loc = 1

    def update_match_args(self, ):
        self.prim_dt = self.children[0]
        self.function_name = self.children[1]
        self.statements = self.children[2:]

    __match_args__ = ("prim_dt", "function_name", "statements")

    def visit(self, ):
        self.update_match_args()

        self.code_generator.add_code(
            f"# Main Funktion {self.prim_dt} {self.function_name}(){{ "
            f"{self.statements[0]} ... }} Start\n", 0)

        self._pretty_comments()

        self._adapt_code()

        self.code_generator.add_code(self.start, self.start_loc)

        for statement in self.statements:
            statement.visit()

        self.code_generator.add_code(self.end, self.end_loc)

        self.code_generator.add_code(
            f"# Main Funktion {self.prim_dt} {self.function_name}(){{ "
            f"{self.statements[0]} ... }} Ende\n", 0)

    def _pretty_comments(self, ):
        self.end = self.code_generator.replace_code_pre(
            self.end, "af",
            str(self.statements[0]) + " ... ")

    def _adapt_code(self, ):
        self.start = self.code_generator.replace_code_pre(
            self.start, "eds", str(global_vars.args.end_data_segment))

    def __repr__(self, ):
        return self.alternative_to_string()
