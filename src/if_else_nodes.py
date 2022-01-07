from abstract_syntax_tree import ASTNode, strip_multiline_string
import global_vars
from dummy_nodes import NT


class If(ASTNode):
    """Abstract Syntax Tree Node for If"""

    start = """# codela(l1)
        LOADIN SP ACC 1;  # Wert von l1 in ACC laden
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        JUMP= codelength(af) + 1;  # Branch überspringen
        # code(statements)
        """
    start_loc = 3

    def _update_match_args(self, ):
        self.condition = self.children[0]
        self.branch = self.children[1:]

    __match_args__ = ("condition", "branch")

    def visit(self, ):
        self._update_match_args()
        self.code_generator.add_code("# If start\n", 0)

        self._pretty_comments()

        self.condition.visit()

        self.code_generator.add_code(strip_multiline_string(self.start),
                                     self.start_loc)

        self.code_generator.add_marker()

        for statement in self.branch:
            statement.visit()

        self._adapt_code()

        self.code_generator.remove_marker()

        self.code_generator.add_code("# If end\n", 0)

    def _pretty_comments(self, ):
        if global_vars.args.verbose:
            self.start = self.code_generator.replace_code_pre(
                strip_multiline_string(self.start), 'l1', str(self.condition))
            self.start = self.code_generator.replace_code_pre(
                strip_multiline_string(self.start), 'statements',
                str(self.branch[0]) + " ... ")

    def _adapt_code(self, ):
        self.code_generator.replace_code_after(
            "codelength(af) + 1",
            str(self.code_generator.loc -
                self.code_generator.get_marker_loc() + 1))


class IfElse(ASTNode):
    """Abstract Syntax Tree Node for Else"""

    start = """# codela(l1)
        LOADIN SP ACC 1;  # Wert von l1 in ACC laden
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        JUMP= codelength(af1) + 2;  # Zu Else-Branch springen, wenn l1 nicht erfüllt
        # code(statements1)
        """
    start_loc = 3

    middle = """JUMP codelength(af2) + 1;  # Else-Branch überspringen
        # code(statements2)
        """
    middle_loc = 1

    def _idx_of_else_node(self):
        """Finds out the index of the ElseNode whichs marks the border between
        the If and Else Codeblocks
        """
        for (i, child) in enumerate(self.children):
            if isinstance(child, NT.Else):
                return i
        return -1

    def _update_match_args(self, ):
        self.condition = self.children[0]
        self.branch1 = self.children[1:self._idx_of_else_node()]
        self.branch2 = self.children[self._idx_of_else_node() + 1:]

    __match_args__ = ("condition", "branch1", "branch2")

    def visit(self, ):
        self._update_match_args()

        self.code_generator.add_code("# If Else start\n", 0)

        self._pretty_comments()

        self.condition.visit()

        self.code_generator.add_code(strip_multiline_string(self.start),
                                     self.start_loc)

        self.code_generator.add_marker()

        for statement in self.branch1:
            statement.visit()

        self._adapt_code_1()

        self.code_generator.remove_marker()

        self.code_generator.add_code(strip_multiline_string(self.middle),
                                     self.middle_loc)

        self.code_generator.add_marker()

        for statement in self.branch2:
            statement.visit()

        self._adapt_code_2()

        self.code_generator.remove_marker()

        self.code_generator.add_code("# If Else end\n", 0)

    def _pretty_comments(self, ):
        if global_vars.args.verbose:
            self.start = self.code_generator.replace_code_pre(
                strip_multiline_string(self.start), "l1", str(self.condition))
            self.start = self.code_generator.replace_code_pre(
                strip_multiline_string(self.start), "statements1",
                str(self.branch1[0]) + " ... ")
            self.middle = self.code_generator.replace_code_pre(
                strip_multiline_string(self.middle), "statements2",
                str(self.branch2[0]) + " ... ")

    def _adapt_code_1(self, ):
        self.code_generator.replace_code_after(
            "codelength(af1) + 2",
            str(self.code_generator.loc -
                self.code_generator.get_marker_loc() + 2))

    def _adapt_code_2(self, ):
        self.code_generator.replace_code_after(
            "codelength(af2) + 1",
            self.code_generator.loc - self.code_generator.get_marker_loc() + 1)
