from abstract_syntax_tree import ASTNode, strip_multiline_string
import global_vars


class MainFunctionNode(ASTNode):
    """Abstract Syntax Tree Node for main method"""

    start = "LOADI SP eds;\n"
    start_loc = 1

    end = """# code(af)
        JUMP 0;
        """
    end_loc = 1

    def _update_match_args(self, ):
        self.prim_dt = self.children[0]
        self.main = self.children[1]
        self.af = self.children[2:]

    def visit(self, ):
        self._update_match_args()

        self.code_generator.add_code("# Main start\n", 0)

        self._adapt_code()

        for statement in self.af:
            statement.visit()

        self._pretty_comments()

        self.code_generator.add_code(strip_multiline_string(self.end),
                                     self.end_loc)

        self.code_generator.add_code("# Main end\n", 0)

    def _adapt_code(self, ):
        self.start = self.code_generator.replace_code_pre(
            self.start, "eds", str(global_vars.args.end_data_segment))

        self.code_generator.add_code(self.start, self.start_loc)

    def _pretty_comments(self, ):
        self.end = self.code_generator.replace_code_pre(
            self.end, "af",
            str(self.af[0]) + " ... ")
