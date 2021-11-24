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

    def visit(self, ):
        self.code_generator.add_code("# Main start\n", 0)

        self.code_generator.add_code(self.start, self.start_loc)

        self.code_generator.add_marker()

        self.code_generator.replace_code_after(
            'eds', global_vars.args.end_data_segment)

        self.code_generator.remove_marker()

        for child in self.children:
            child.visit()

        self.code_generator.add_code(
            strip_multiline_string(self.end), self.end_loc)

        self.code_generator.add_code("# Main end\n", 0)
