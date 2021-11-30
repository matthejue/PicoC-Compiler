from abstract_syntax_tree import ASTNode, strip_multiline_string
from symbol_table import VariableSymbol, ConstantSymbol
from errors import UnknownIdentifierError
from lexer import TT


class ArithmeticVariableConstant(ASTNode):
    """Abstract Syntax Tree Node for arithmetic variables and constants"""

    start = "SUBI SP 1;\n"
    constant = "LOADI ACC encode(w);\n"
    constant_identifier = "LOADI ACC encode(c);\n"
    variable_identifier = "LOAD ACC var_identifier;\n"
    end = "STOREIN SP ACC 1;\n"

    all_loc = 1

    __match_args__ = ("variable_constant", )

    def _update_match_args(self):
        self.variable_constant = self.token

    def visit(self, ):
        self._update_match_args()
        self.code_generator.add_code("# Variable / Constant start\n", 0)

        self.code_generator.add_code(self.start, self.all_loc)

        try:
            self._insert_identifier()
        except KeyError:
            # repackage the error
            raise UnknownIdentifierError(self.token)

        self.code_generator.add_code(self.end, self.all_loc)

        self.code_generator.add_code("# Variable / Constant end\n", 0)

    def _insert_identifier(self, ):
        if self.token.type == TT.IDENTIFIER:
            var_or_const = self.symbol_table.resolve(self.token.value)
            if isinstance(var_or_const, VariableSymbol):
                self.variable_identifier = self.code_generator.replace_code_pre(
                    self.variable_identifier, "var_identifier",
                    str(var_or_const.value))
                self.code_generator.add_code(self.variable_identifier,
                                             self.all_loc)
            elif isinstance(var_or_const, ConstantSymbol):
                self.constant_identifier = self.code_generator.replace_code_pre(
                    self.constant_identifier, "encode(c)",
                    str(var_or_const.value))
                self.code_generator.add_code(self.constant_identifier,
                                             self.all_loc)
        elif self.token.type in [TT.NUMBER, TT.CHAR]:
            self.constant = self.code_generator.replace_code_pre(
                self.constant, "encode(w)", str(self.token.value))
            self.code_generator.add_code(self.constant, self.all_loc)


class ArithmeticBinaryOperationNode(ASTNode):
    """Abstract Syntax Tree Node for for arithmetic binary operations"""

    __match_args__ = ("left_operand", "operation", "right_operand")

    def _update_match_args(self):
        self.left_operand = self.children[0]
        self.operation = self.children[1]
        self.right_operand = self.children[2]

    end = """# codeaa(e1)
        # codeaa(e2)
        LOADIN SP ACC 2; # Wert von e1 in ACC laden
        LOADIN SP IN2 1; # Wert von e2 in IN2 laden
        OP ACC IN2; # e1 binop e2 in ACC laden
        STOREIN SP ACC 2; # Ergebnis in zweitoberste Stack-Zelle
        ADDI SP 1; # Stack um eine Zelle verkürzen
        """

    end_loc = 5

    #  def _get_operand_left(self):
    #  self.children[0].children[]
#
    #  def _get_operand_left(self):
    #  self.children[1].children[]

    def visit(self, ):
        self._update_match_args()
        if len(self.children) == 1:
            self.children[0].visit()
            return

        self.code_generator.add_code("# Arithmetic Binary Operation start\n",
                                     0)

        self.children[0].visit()
        self.children[1].visit()

        match self:
            case ArithmeticBinaryOperationNode(left_operand, operation, right_operand):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'e1', str(left_operand))
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'e2', str(right_operand))

        match self.token.value:
            case '+':
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'ADD')
            case '-':
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'SUB')
            case '*':
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'MUL')
            case '/':
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'DIV')
            case '%':
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'MOD')
            case '^':
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'OPLUS')
            case '|':
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'OR')
            case '&':
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'AND')

        self.code_generator.add_code(strip_multiline_string(self.end),
                                     self.end_loc)

        self.code_generator.add_code("# Arithmetic Binary Operation end\n", 0)


class ArithmeticUnaryOperationNode(ASTNode):
    """Abstract Syntax Tree Node for for arithmetic unary operations"""

    start = """# codeaa(e1)
        LOADI ACC 0; # 0 in ACC laden
        LOADIN SP IN2 1; # Wert von e1 in IN2 laden
        SUB ACC IN2; # (0 - e1) in ACC laden
        """

    start_loc = 3

    bitwise_negation = "SUBI ACC 1; # transform negation to complement\n"

    bitwise_negation_loc = 1

    end = "STOREIN SP ACC 1; # Ergebnis in oberste Stack-Zelle\n"

    end_loc = 1

    def visit(self, ):
        self.code_generator.add_code("# Arithmetic Unary Operation start\n", 0)

        self.children[0].visit()

        self.code_generator.add_code(strip_multiline_string(self.start),
                                     self.start_loc)

        if self.token.value == '~':
            self.code_generator.add_code(self.bitwise_negation,
                                         self.bitwise_negation_loc)

        self.code_generator.add_code(self.end, self.end_loc)

        self.code_generator.add_code("# Arithmetic Unary Operation end\n", 0)
