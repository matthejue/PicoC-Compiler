from abstract_syntax_tree import ASTNode, strip_multiline_string


class WhileNode(ASTNode):

    """Abstract Syntax Tree Node for while loop"""

    condition_check = """# codela(l)
        LOADIN SP ACC 1; # Wert von l in ACC laden
        ADDI SP 1; # Stack um eine Zelle verkürzen
        JUMP= codelength(af) + 2; # af überspringen, wenn l unerfüllt
        # code(af)
        """

    condition_check_loc = 3

    end = """# zurück zur Auswertung von l
        JUMP -(codelength(af) + codelength(l) + 3);
        """

    end_loc = 1

    def visit(self, ):
        self.code_generator.add_code("# While start\n", 0)

        self.code_generator.add_marker()

        self.children[0].visit()

        self.code_generator.add_code(
            strip_multiline_string(self.condition_check),
            self.condition_check_loc)

        self.code_generator.add_marker()

        for child in self.children[1:]:
            child.visit()

        self.code_generator.replace_code_after(
            "codelength(af) + 2", self.code_generator.loc - self.code_generator.get_marker_loc() + 2)

        self.code_generator.remove_marker()

        self.end = self.code_generator.replace_code_pre(self.end,
                                                        "(codelength(af) + codelength(l) + 3)", self.code_generator.loc -
                                                        self.code_generator.get_marker_loc())
        # + 3 sind schon mit drin

        self.code_generator.remove_marker()

        self.code_generator.add_code(
            strip_multiline_string(self.end), self.end_loc)

        self.code_generator.add_code("# While end\n", 0)


class DoWhileNode(ASTNode):

    """Abstract Syntax Tree Node for do while Grammar"""

    # Problem mit code(af)
    condition_check = """# code(af)
        # codela(l)
        LOADIN SP ACC 1; # Wert von l in ACC laden
        ADDI SP 1; # Stack um eine Zelle verkürzen
        # zurück zur Ausführung von af
        JUMP<> -(codelength(af) + codelength(l) + 2);
        """

    condition_check_loc = 3

    def visit(self, ):
        self.code_generator.add_code("# Do While start\n", 0)

        self.code_generator.add_marker()

        for child in self.children[1:]:
            child.visit()

        self.children[0].visit()

        self.condition_check = self.code_generator.replace_code_pre(self.condition_check,
                                                                    "(codelength(af) + "
                                                                    "codelength(l) + 2) + 2",
                                                                    self.code_generator.loc - self.code_generator.get_marker_loc() + 2)

        self.code_generator.remove_marker()

        self.code_generator.add_code(strip_multiline_string(self.condition_check),
                                     self.condition_check_loc)

        self.code_generator.add_code("# Do While end\n", 0)

    def addChild(self, node):
        """do while loops should be called 'do while' and not 'do'

        :returns: None
        """
        # in case the representative tokens of self appear as attribute of a
        # TokenNode, the token of self can finally register the right value
        # Because of e.g. <alloc>: <word> <word> ... one should only take the
        # first TokenNode matching the possible representative tokens
        if self._is_tokennode(node) and node.token.type in\
                self.tokentypes:
            self.token.value = "do while"
            self.token.position = node.token.position
            self.ignore = False
            return

        self.children += [node]
