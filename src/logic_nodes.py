from abstract_syntax_tree import ASTNode, strip_multiline_string
from dummy_nodes import NT


class LogicAndOr(ASTNode):
    """Abstract Syntax Tree Node for logic 'and' and 'or'"""

    end = strip_multiline_string(
        """ LOADIN SP ACC 2;  # Wert von l1 in ACC laden
        LOADIN SP IN2 1;  # Wert von l2 in IN2 laden
        LOP ACC IN2;  # l1 lop l2 in ACC laden
        STOREIN SP ACC 2;  # Ergebnis in zweitoberste Stack-Zelle
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        """)
    end_loc = 5

    def update_match_args(self, ):
        self.left_atom = self.children[0]
        self.binary_connective = self.children[1]
        self.right_atom = self.children[2]

    __match_args__ = ("left_atom", "binary_connective", "right_atom")

    def visit(self, ):
        self.update_match_args()

        self.code_generator.add_code(
            f"# Logische binäre Verknüpfung {self} Start\n", 0)

        self._pretty_comments()

        self.left_atom.visit()
        self.right_atom.visit()

        self._adapt_code()

        self.code_generator.add_code(self.end, self.end_loc)

        self.code_generator.add_code(
            f"# Logische binäre Verknüpfung {self} Ende\n", 0)

    def _pretty_comments(self, ):
        self.end = self.code_generator.replace_code_pre(
            self.end, "l1 lop l2", str(self))
        self.end = self.code_generator.replace_code_pre(
            self.end, "l1", str(self.left_atom))
        self.end = self.code_generator.replace_code_pre(
            self.end, "l2", str(self.right_atom))

    def _adapt_code(self, ):
        match self:
            case LogicAndOr(_, NT.LAnd(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'LOP', 'AND')
            case LogicAndOr(_, NT.LOr(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'LOP', 'OR')


class LogicNot(ASTNode):
    """Abstract Syntax Tree Node for logic not"""

    end = strip_multiline_string(
        """LOADI ACC 1;  # 1 in ACC laden
        LOADIN SP IN2 1;  # Wert von l1 in IN2 laden
        OPLUS ACC IN2;  # !(l1) in ACC laden
        STOREIN SP ACC 1;  # Ergebnis in oberste Stack-Zelle
        """)
    end_loc = 4

    def update_match_args(self, ):
        self.unary_connective = self.children[0]
        self.atom = self.children[1]

    __match_args__ = ("unary_connective", "atom")

    def visit(self, ):
        self.update_match_args()

        self.code_generator.add_code(
            f"# Logische unäre Verknüpfung {self} Start\n", 0)

        self._pretty_comments()

        self.atom.visit()

        self.code_generator.add_code(self.end, self.end_loc)

        self.code_generator.add_code(
            f"# Logische unäre Verknüpfung {self} Ende\n", 0)

    def _pretty_comments(self, ):
        self.end = self.code_generator.replace_code_pre(
            self.end, "l1", str(self.atom))


class LogicAtom(ASTNode):
    """Abstract Syntax Tree Node for logic atom"""

    end = strip_multiline_string(
        """LOADIN SP ACC 2;  # Wert von e1 in ACC laden
        LOADIN SP IN2 1;  # Wert von e2 in IN2 laden
        SUB ACC IN2;  # e1 - e2 in ACC laden
        JUMPvglop 3;  # Ergebnis 1, wenn e1 rel e2 erfüllt
        LOADI ACC 0;  # Ergebnis 0, wenn e1 rel e2 nicht erfüllt
        JUMP 2;
        LOADI ACC 1;  # Ergebnis 1, wenn e1 vglop e2 wahr
        STOREIN SP ACC 2;  # Ergebnis in zweitoberste Stack-Zelle
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        """)
    end_loc = 9

    def update_match_args(self, ):
        self.left_element = self.children[0]
        self.relation = self.children[1]
        self.right_element = self.children[2]

    __match_args__ = ("left_element", "relation", "right_element")

    def visit(self, ):
        self.update_match_args()

        self.code_generator.add_code(f"# Logisches Atom {self} Start\n", 0)

        self._pretty_comments()

        self.left_element.visit()
        self.right_element.visit()

        self._adapt_code()

        self.code_generator.add_code(self.end, self.end_loc)

        self.code_generator.add_code(f"# Logisches Atom {self} Ende\n", 0)

    def _pretty_comments(self, ):
        self.end = self.code_generator.replace_code_pre(
            self.end, "e1 rel e2", str(self))
        self.end = self.code_generator.replace_code_pre(
            self.end, "e1", str(self.left_element))
        self.end = self.code_generator.replace_code_pre(
            self.end, "e2", str(self.right_element))

    def _adapt_code(self, ):
        match self:
            case LogicAtom(_, NT.Eq(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'vglop', '==')
            case LogicAtom(_, NT.UEq(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'vglop', '!=')
            case LogicAtom(_, NT.Lt(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'vglop', '<')
            case LogicAtom(_, NT.Gt(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'vglop', '>')
            case LogicAtom(_, NT.Le(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'vglop', '<=')
            case LogicAtom(_, NT.Ge(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'vglop', '>=')


class LogicTopBottom(ASTNode):
    """Abstract Syntax Tree Node for logic top bottom"""

    end = strip_multiline_string(
        """LOADIN SP ACC 1;  # Wert von e1 in ACC laden
        JUMP== 3;  # Überspringe 2 Befehle, wenn e1 den Wert 0 hat
        LOADI ACC 1;
        STOREIN SP ACC 1;  # Ergebnis in oberste Stack-Zelle
        """)
    end_loc = 4

    def update_match_args(self, ):
        self.arithmetic_expression = self.children[0]

    __match_args__ = ("arithmetic_expression")

    def visit(self, ):
        self.update_match_args()

        self.code_generator.add_code(
            f"# Logischer Wahrheitswert aus arithmetischem Ausdruck {self} Start\n", 0)

        self._pretty_comments()

        self.arithmetic_expression.visit()

        self.code_generator.add_code(self.end, self.end_loc)

        self.code_generator.add_code(
            f"# Logischer Wahrheitswert aus arithmetischem Ausdruck {self} Ende\n", 0)

    def _pretty_comments(self, ):
        self.end = self.code_generator.replace_code_pre(
            self.end, "e1", str(self.arithmetic_expression))
