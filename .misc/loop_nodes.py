from ast_node import ASTNode, strip_multiline_string


class While(ASTNode):
    """Abstract Syntax Tree Node for while loop"""

    condition_check = strip_multiline_string(
        """LOADIN SP ACC 1;  # Wert von 'l1' in ACC laden
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        JUMP== codelength(af) + 2;  # Statements überspringen, wenn 'l1' nicht erfüllt
        """
    )
    condition_check_loc = 3

    end = "JUMP -(codelength(af) + codelength(l) + 3);  # Zurück zur Auswertung von 'l1'\n"
    end_loc = 1

    def update_match_args(self):
        self.condition = self.children[0]
        self.branch = self.children[1:]

    __match_args__ = ("condition", "branch")

    def visit(self):
        self.update_match_args()

        dot_more = " ... " if len(self.branch) > 1 else ""
        branch = self.branch[0] if self.branch else ""
        self.code_generator.add_code(
            f"# While Statement 'While({self.condition} {branch}{dot_more})' Start\n", 0
        )

        self._pretty_comments()

        self.code_generator.add_marker()

        self.condition.visit()

        self.code_generator.add_code(self.condition_check, self.condition_check_loc)

        self.code_generator.add_marker()

        for statement in self.branch:
            statement.visit()

        self._adapt_code_1()

        self.code_generator.remove_marker()

        self._adapt_code_2()

        self.code_generator.remove_marker()

        self.code_generator.add_code(self.end, self.end_loc)

        self.code_generator.add_code(
            f"# While Statement 'While({self.condition} "
            f"{branch}{dot_more})' Ende\n",
            0,
        )

    def _pretty_comments(self):
        self.condition_check = self.code_generator.replace_code_pre(
            self.condition_check, "l1", str(self.condition)
        )
        self.end = self.code_generator.replace_code_pre(
            self.end, "l1", str(self.condition)
        )

    def _adapt_code_1(self):
        self.code_generator.replace_code_after(
            "codelength(af) + 2",
            str(self.code_generator.loc - self.code_generator.get_marker_loc() + 2),
        )

    def _adapt_code_2(self):
        self.end = self.code_generator.replace_code_pre(
            self.end,
            "(codelength(af) + codelength(l) + 3)",
            str(self.code_generator.loc - self.code_generator.get_marker_loc()),
        )
        # + 3 sind schon mit drin


class DoWhile(ASTNode):
    """Abstract Syntax Tree Node for do while Grammar"""

    condition_check = strip_multiline_string(
        """LOADIN SP ACC 1;  # Wert von 'l1' in ACC laden
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        JUMP!= -(codelength(af) + codelength(l) + 2);  # Zurück zur Ausführung der Statements
        """
    )
    condition_check_loc = 3

    def update_match_args(self):
        self.branch = self.children[:-1]
        self.condition = self.children[-1]

    __match_args__ = ("branch", "condition")

    def visit(self):
        self.update_match_args()

        dot_more = " ..." if len(self.branch) > 1 else ""
        branch = self.branch[0] if self.branch else ""
        self.code_generator.add_code(
            f"# Do While 'DoWhile({branch}{dot_more} {self.condition})' Start\n", 0
        )

        self.code_generator.add_marker()

        for statement in self.branch:
            statement.visit()

        self.condition.visit()

        self._adapt_code()

        self.code_generator.remove_marker()

        self.code_generator.add_code(self.condition_check, self.condition_check_loc)

        self.code_generator.add_code(
            f"# Do While 'DoWhile({branch}{dot_more} {self.condition})' Ende\n", 0
        )

    def _pretty_comments(self):
        self.condition_check = self.code_generator.replace_code_pre(
            self.condition_check, "l1", str(self.condition)
        )

    def _adapt_code(self):
        self.condition_check = self.code_generator.replace_code_pre(
            self.condition_check,
            "(codelength(af) + codelength(l) + 2) + 2",
            str(self.code_generator.loc - self.code_generator.get_marker_loc() + 2),
        )
