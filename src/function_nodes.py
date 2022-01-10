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
        self.main = self.children[1]
        self.statements = self.children[2:]

    __match_args__ = ("prim_dt", "main", "statements")

    def visit(self, ):
        self.update_match_args()

        self.code_generator.add_code("# Main Funktion Start\n", 0)

        self._pretty_comments()

        self._adapt_code()

        self.code_generator.add_code(self.start, self.start_loc)

        for statement in self.statements:
            statement.visit()

        self.code_generator.add_code(self.end, self.end_loc)

        self.code_generator.add_code("# Main Funktion Ende\n", 0)

    def _pretty_comments(self, ):
        self.end = self.code_generator.replace_code_pre(
            self.end, "af",
            str(self.statements[0]) + " ... ")

    def _adapt_code(self, ):
        self.start = self.code_generator.replace_code_pre(
            self.start, "eds", str(global_vars.args.end_data_segment))
