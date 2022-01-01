from abstract_syntax_tree import ASTNode, strip_multiline_string
from symbol_table import VariableSymbol, ConstantSymbol
from errors import UnknownIdentifierError
from lexer import TT, Token


class ArithmeticOperand(ASTNode):
    """Abstract Syntax Tree Node for arithmetic variables and constants"""

    START = "SUBI SP 1; # Stack um eine Zelle erweitern\n"
    CONSTANT = "LOADI ACC encode(w); # e1 in ACC laden\n"
    CONSTANT_IDENTIFIER = "LOADI ACC encode(c); # e1 in ACC laden\n"
    VARIABLE_IDENTIFIER = "LOAD ACC var_identifier; # e1 in ACC laden\n"
    END = "STOREIN SP ACC 1; # Wert in oberste Stacke-Zelle\n"

    ALL_LOC = 1

    def _update_match_args(self):
        self.operand = self.token.type

    __match_args__ = ("operand")

    def visit(self, ):
        self._update_match_args()

        self.code_generator.add_code("# ArithmeticOperand start\n", 0)

        self.code_generator.add_code(self.START, self.ALL_LOC)

        try:
            self._adapt_code()
        except KeyError:
            # repackage the error
            raise UnknownIdentifierError(self.token)

        self.code_generator.add_code(self.END, self.ALL_LOC)

        self.code_generator.add_code("# ArithmeticOperand end\n", 0)

    def _adapt_code(self, ):
        match self.token:
            case Token(TT.IDENTIFIER, value):
                symbol = self.symbol_table.resolve(value)
                match symbol:
                    case VariableSymbol(value):
                        self.VARIABLE_IDENTIFIER = self._pretty_comments(
                            self.VARIABLE_IDENTIFIER)
                        self.VARIABLE_IDENTIFIER = self.code_generator.replace_code_pre(
                            self.VARIABLE_IDENTIFIER, "var_identifier", str(value))
                        self.code_generator.add_code(self.VARIABLE_IDENTIFIER,
                                                     self.ALL_LOC)
                    case ConstantSymbol(value):
                        self.CONSTANT_IDENTIFIER = self._pretty_comments(
                            self.CONSTANT_IDENTIFIER)
                        self.CONSTANT_IDENTIFIER = self.code_generator.replace_code_pre(
                            self.CONSTANT_IDENTIFIER, "encode(c)", str(value))
                        self.code_generator.add_code(self.CONSTANT_IDENTIFIER,
                                                     self.ALL_LOC)
            case (Token((TT.NUMBER | TT.CHAR), value)):
                self.CONSTANT = self._pretty_comments(self.CONSTANT)
                self.CONSTANT = self.code_generator.replace_code_pre(
                    self.CONSTANT, "encode(w)", str(value))
                self.code_generator.add_code(self.CONSTANT, self.ALL_LOC)

    def _pretty_comments(self, code):
        code = self.code_generator.replace_code_pre(
            code, "e1", str(self.token.value))
        return code


class ArithmeticBinaryOperation(ASTNode):
    """Abstract Syntax Tree Node for for arithmetic binary operations"""

    END = """# codeaa(e1)
        # codeaa(e2)
        LOADIN SP ACC 2; # e1 in ACC laden
        LOADIN SP IN2 1; # e2 in IN2 laden
        OP ACC IN2; # e1 binop e2 in ACC laden
        STOREIN SP ACC 2; # Ergebnis in zweitoberste Stack-Zelle
        ADDI SP 1; # Stack um eine Zelle verkürzen
        """

    end_loc = 5

    def _update_match_args(self):
        self.left_operand = self.children[0]
        self.operation = self.token.type
        self.right_operand = self.children[1]

    __match_args__ = ("left_operand", "operation", "right_operand")

    def visit(self, ):
        #  if len(self.children) == 1:
        if self.ignore():
            self.children[0].visit()
            return

        self._update_match_args()

        self.code_generator.add_code("# ArithmeticBinaryOperation start\n", 0)

        self.left_operand.visit()
        self.right_operand.visit()

        self._pretty_comments()

        self._adapt_code()

        self.code_generator.add_code("# ArithmeticBinaryOperation end\n", 0)

    def _pretty_comments(self, ):
        self.END = self.code_generator.replace_code_pre(
            self.END, 'e1', str(self.left_operand))
        self.END = self.code_generator.replace_code_pre(
            self.END, 'e2', str(self.right_operand))
        self.END = self.code_generator.replace_code_pre(
            self.END, 'e1 binop e2', str(self))

    def _adapt_code(self, ):
        match self.operation:
            case TT.PLUS_OP:
                self.END = self.code_generator.replace_code_pre(
                    self.END, 'OP', 'ADD')
            case TT.MINUS_OP:
                self.END = self.code_generator.replace_code_pre(
                    self.END, 'OP', 'SUB')
            case TT.MUL_OP:
                self.END = self.code_generator.replace_code_pre(
                    self.END, 'OP', 'MUL')
            case TT.DIV_OP:
                self.END = self.code_generator.replace_code_pre(
                    self.END, 'OP', 'DIV')
            case TT.MOD_OP:
                self.END = self.code_generator.replace_code_pre(
                    self.END, 'OP', 'MOD')
            case TT.PLUS_OP:
                self.END = self.code_generator.replace_code_pre(
                    self.END, 'OP', 'OPLUS')
            case TT.AND_OP:
                self.END = self.code_generator.replace_code_pre(
                    self.END, 'OP', 'AND')
            case TT.OR_OP:
                self.END = self.code_generator.replace_code_pre(
                    self.END, 'OP', 'OR')

        self.code_generator.add_code(strip_multiline_string(self.END),
                                     self.end_loc)


class ArithmeticUnaryOperation(ASTNode):
    """Abstract Syntax Tree Node for for arithmetic unary operations"""

    START = """# codeaa(e1)
        LOADI ACC 0; # 0 in ACC laden
        LOADIN SP IN2 1; # Wert von e1 in IN2 laden
        SUB ACC IN2; # (0 - e1) in ACC laden
        """

    START_LOC = 3

    BITWISE_NEGATION = "SUBI ACC 1; # zu Bitweise Negation unwandeln\n"

    BITWISE_NEGATION_LOC = 1

    END = "STOREIN SP ACC 1; # Ergebnis in oberste Stack-Zelle\n"

    END_LOC = 1

    def _update_match_args(self, ):
        self.operation = self.token.type
        self.operand = self.children[0]

    __match_args__ = ("operation", "operand")

    def visit(self, ):
        self.code_generator.add_code("# ArithmeticUnaryOperation start\n", 0)

        self.operand.visit()

        self.code_generator.add_code(strip_multiline_string(self.START),
                                     self.START_LOC)

        self._adapt_code()

        self.code_generator.add_code(self.END, self.END_LOC)

        self.code_generator.add_code("# ArithmeticUnaryOperation end\n", 0)

    def _pretty_comments(self, ):
        self.code_generator.replace_code_pre(
            self.START, "e1", self.token.value)

    def _adapt_code(self, ):
        match self.operation:
            case TT.NOT_OP:
                self.code_generator.add_code(self.BITWISE_NEGATION,
                                             self.BITWISE_NEGATION_LOC)
