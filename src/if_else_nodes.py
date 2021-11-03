from abstract_syntax_tree import ASTNode, strip_multiline_string


class IfNode(ASTNode):

    """Abstract Syntax Tree Node for If"""

    start = """# codela(l)
        LOADIN SP ACC 1; # Wert von l in ACC laden
        ADDI SP 1; # Stack um eine Zelle verkürzen
        JUMP= codelength(af) + 1; # af überspringen
        # code(af)
        """

    start_loc = 3

    def visit(self, ):
        self.code_generator.add_code("# If start\n", 0)

        self.children[0].visit()

        self.code_generator.add_code(
            strip_multiline_string(self.start), self.start_loc)

        self.code_generator.add_marker()

        for child in self.children[1:]:
            child.visit()

        self.code_generator.replace_code_after(
            "codelength(af) + 1", self.code_generator.loc - self.code_generator.get_marker_loc() + 1)

        self.code_generator.remove_marker()

        self.code_generator.add_code("# If end\n", 0)


class IfElseNode(ASTNode):

    """Abstract Syntax Tree Node for Else"""

    start = """# codela(l)
        LOADIN SP ACC 1; # Wert von l in ACC laden
        ADDI SP 1; # Stack um eine Zelle verkürzen
        JUMP= codelength(af1) + 2; # af1 überspringen
        # code(af1)
        """

    start_loc = 3

    middle = """JUMP codelength(af2) + 1;
        # code(af2)
        """

    middle_loc = 1

    def visit(self, ):
        # TODO: hier ist auf jeden Fall noch ein Bug
        self.code_generator.add_code("# If Else start\n", 0)

        self.children[0].visit()

        self.code_generator.add_code(
            strip_multiline_string(self.start), self.start_loc)

        self.code_generator.add_marker()

        for child in self.children[1:]:
            child.visit()

        self.code_generator.replace_code_after(
            "codelength(af1) + 2", self.code_generator.loc - self.code_generator.get_marker_loc() + 2)

        self.code_generator.remove_marker()

        self.code_generator.add_code(
            strip_multiline_string(self.middle), self.middle_loc)

        self.code_generator.add_marker()

        for child in self.children[1:]:
            child.visit()

        self.code_generator.replace_code_after(
            "codelength(af2) + 1", self.code_generator.loc - self.code_generator.get_marker_loc() + 1)

        self.code_generator.remove_marker()

        self.code_generator.add_code_close("", 0)

        self.code_generator.add_code("# If Else end\n", 0)
