from abstract_syntax_tree import ASTNode, strip_multiline_string


class LogicAndOrNode(ASTNode):

    """Abstract Syntax Tree Node for logic 'and' and 'or'"""

    end = """# codela(l1)
        # codela(l2)
        LOADIN SP ACC 2;  # Wert von l1 in ACC laden
        LOADIN SP IN2 1;  # Wert von l2 in IN2 laden
        LOP ACC IN2;  # l1 lop l 2 in ACC laden
        STOREIN SP ACC 2;  # Ergebnis in zweitoberste Stack-Zelle
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        """

    end_loc = 5

    def visit(self, ):
        if len(self.children) == 1:
            self.children[0].visit()
            return

        self.code_generator.add_code("# Logic Binary Operation start\n", 0)

        self.children[0].visit()
        self.children[1].visit()

        if self.token.value == '&&':
            self.end = self.code_generator.replace_code_pre(
                self.end, 'LOP', 'AND')
        elif self.token.value == '||':
            self.end = self.code_generator.replace_code_pre(
                self.end, 'LOP', 'OR')

        self.code_generator.add_code(
            strip_multiline_string(self.end), self.end_loc)

        self.code_generator.add_code("# Logic Binary Operation end\n", 0)


class LogicNotNode(ASTNode):

    """Abstract Syntax Tree Node for logic not"""

    end = """# codela(l1)
        LOADI ACC 1;  # 1 in ACC laden
        LOADIN SP IN2 1;  # Wert von l1 in IN2 laden
        OPLUS ACC IN2;  # !(l1) in ACC laden
        STOREIN SP ACC 1;  # Ergebnis in oberste Stack-Zelle
        """

    end_loc = 4

    def visit(self, ):
        self.code_generator.add_code("# Logic Unary Operation start\n", 0)

        self.children[0].visit()

        self.code_generator.add_code(
            strip_multiline_string(self.end), self.end_loc)

        self.code_generator.add_code("# Logic Unary Operation end\n", 0)


class LogicAtomNode(ASTNode):

    """Abstract Syntax Tree Node for logic atom"""

    end = """# codeaa(e1)
        # codeaa(e2)
        LOADIN SP ACC 2;  # Wert von e1 in ACC laden
        LOADIN SP IN2 1;  # Wert von e2 in IN2 laden
        SUB ACC IN2;  # e1 - e2 in ACC laden
        JUMPvglop 3;  # Ergebnis 1, wenn e1 vglop e2 wahr
        LOADI ACC 0;  # Ergebnis 0, wenn e1 vglop e2 falsch
        JUMP 2;
        LOADI ACC 1;  # Ergebnis 1, wenn e1 vglop e2 wahr
        STOREIN SP ACC 2;  # Ergebnis in zweitoberste Stack-Zelle
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        """

    end_loc = 9

    def visit(self, ):
        self.code_generator.add_code("# Logic Atom start\n", 0)

        self.children[0].visit()
        self.children[1].visit()

        if self.token.value == '>':
            self.end = self.code_generator.replace_code_pre(
                self.end, 'vglop', '>')
        elif self.token.value == '==':
            self.end = self.code_generator.replace_code_pre(
                self.end, 'vglop', '=')
        elif self.token.value == '>=':
            self.end = self.code_generator.replace_code_pre(
                self.end, 'vglop', '>=')
        elif self.token.value == '<':
            self.end = self.code_generator.replace_code_pre(
                self.end, 'vglop', '<')
        elif self.token.value == '!=':
            self.end = self.code_generator.replace_code_pre(
                self.end, 'vglop', '<>')
        elif self.token.value == '<=':
            self.end = self.code_generator.replace_code_pre(
                self.end, 'vglop', '<=')

        self.code_generator.add_code(
            strip_multiline_string(self.end), self.end_loc)

        self.code_generator.add_code("# Logic Atom end\n", 0)


class LogicTopBottomNode(ASTNode):

    """Abstract Syntax Tree Node for logic top bottom"""

    end = """# codeaa(e)
        LOADIN SP ACC 1;  # Wert von e in ACC laden
        JUMP= 3;  # Überspringe 2 Befehle, wenn e den Wert 0 hat
        LOADI ACC 1;
        STOREIN SP ACC 1;  # Ergebnis in oberste Stack-Zelle
        """

    end_loc = 4

    def visit(self, ):
        self.code_generator.add_code("# Logic Top Bottom start\n", 0)

        self.children[0].visit()

        self.code_generator.add_code(
            strip_multiline_string(self.end), self.end_loc)

        self.code_generator.add_code("# Logic Top Bottom end\n", 0)
