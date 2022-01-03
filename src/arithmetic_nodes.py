from abstract_syntax_tree import ASTNode, strip_multiline_string
from symbol_table import VariableSymbol, ConstantSymbol
from errors import UnknownIdentifierError
from dummy_nodes import Identifier, Number, Character, Add, Sub, Mul, Div, Mod, Oplus, And, Or, Not, Minus
import global_vars


class ArithOperand(ASTNode):
    """Abstract Syntax Tree Node for arithmetic variables and constants"""

    START = "SUBI SP 1;  # Stack um eine Zelle erweitern\n"
    CONSTANT = "LOADI ACC encode(w);  # Wert von e1 in ACC laden\n"
    CONSTANT_IDENTIFIER = "LOADI ACC encode(c);  # Wert von e1 in ACC laden\n"
    VARIABLE_IDENTIFIER = "LOAD ACC var_identifier;  # Wert von e1 in ACC laden\n"
    END = "STOREIN SP ACC 1;  # Wert in oberste Stacke-Zelle\n"

    ALL_LOC = 1

    __match_args__ = ("value")

    def visit(self, ):
        self.code_generator.add_code("# Arithmetic Operand start\n", 0)

        self.code_generator.add_code(self.START, self.ALL_LOC)

        try:
            self._adapt_code()
        except KeyError:
            # repackage the error
            raise UnknownIdentifierError(self.value)

        self.code_generator.add_code(self.END, self.ALL_LOC)

        self.code_generator.add_code("# Arithmetic Operand end\n", 0)

    def _adapt_code(self, ):
        match self:
            case Identifier(value):
                symbol = self.symbol_table.resolve(value)
                match symbol:
                    case VariableSymbol(value):
                        self.VARIABLE_IDENTIFIER = self._pretty_comments(
                            self.VARIABLE_IDENTIFIER)
                        self.VARIABLE_IDENTIFIER = self.code_generator.replace_code_pre(
                            self.VARIABLE_IDENTIFIER, "var_identifier", value)
                        self.code_generator.add_code(self.VARIABLE_IDENTIFIER,
                                                     self.ALL_LOC)
                    case ConstantSymbol(value):
                        self.CONSTANT_IDENTIFIER = self._pretty_comments(
                            self.CONSTANT_IDENTIFIER)
                        self.CONSTANT_IDENTIFIER = self.code_generator.replace_code_pre(
                            self.CONSTANT_IDENTIFIER, "encode(c)", value)
                        self.code_generator.add_code(self.CONSTANT_IDENTIFIER,
                                                     self.ALL_LOC)
            case (Number(value) | Character(value)):
                self.CONSTANT = self._pretty_comments(self.CONSTANT)
                self.CONSTANT = self.code_generator.replace_code_pre(
                    self.CONSTANT, "encode(w)", value)
                self.code_generator.add_code(self.CONSTANT, self.ALL_LOC)

    def _pretty_comments(self, code):
        if global_vars.args.verbose:
            code = self.code_generator.replace_code_pre(
                code, "e1", str(self.value))
            return code


class ArithBinOp(ASTNode):
    """Abstract Syntax Tree Node for for arithmetic binary operations.
    Dient als Container für andere Nodes, daher ist es nicht genauer
    spezifiert, als Addition oder Subtraktion, da erst später feststeht, ob die
    Binary Operation eine Addition oder Subtraktion ist etc."""

    END = """# codeaa(e1)
        # codeaa(e2)
        LOADIN SP ACC 2;  # Wert von e1 in ACC laden
        LOADIN SP IN2 1;  # Wert von e2 in IN2 laden
        OP ACC IN2;  # Wert von e1 binop e2 in ACC laden
        STOREIN SP ACC 2;  # Ergebnis in zweitoberste Stack-Zelle
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        """

    end_loc = 5

    def _update_match_args(self):
        self.left_operand = self.children[0]
        self.operation = self.children[1]
        self.right_operand = self.children[2]

    __match_args__ = ("left_operand", "operation", "right_operand")

    def visit(self, ):
        if self.ignore:
            self.children[0].visit()
            return

        self._update_match_args()

        self.code_generator.add_code(
            "# Arithmetic Binary Operation start\n", 0)

        self.left_operand.visit()
        self.right_operand.visit()

        self._pretty_comments()

        self._adapt_code()

        self.code_generator.add_code("# Arithmetic Binary Operation end\n", 0)

    def _pretty_comments(self, ):
        if global_vars.args.verbose:
            self.END = self.code_generator.replace_code_pre(
                strip_multiline_string(self.END), 'e1', str(self.left_operand))
            self.END = self.code_generator.replace_code_pre(
                strip_multiline_string(self.END), 'e2', str(self.right_operand))
            self.END = self.code_generator.replace_code_pre(
                strip_multiline_string(self.END), 'e1 binop e2', str(self))

    def _adapt_code(self, ):
        match self.operation:
            case Add():
                self.END = self.code_generator.replace_code_pre(
                    self.END, 'OP', 'ADD')
            case Sub():
                self.END = self.code_generator.replace_code_pre(
                    self.END, 'OP', 'SUB')
            case Mul():
                self.END = self.code_generator.replace_code_pre(
                    self.END, 'OP', 'MUL')
            case Div():
                self.END = self.code_generator.replace_code_pre(
                    self.END, 'OP', 'DIV')
            case Mod():
                self.END = self.code_generator.replace_code_pre(
                    self.END, 'OP', 'MOD')
            case Oplus():
                self.END = self.code_generator.replace_code_pre(
                    self.END, 'OP', 'OPLUS')
            case And():
                self.END = self.code_generator.replace_code_pre(
                    self.END, 'OP', 'AND')
            case Or():
                self.END = self.code_generator.replace_code_pre(
                    self.END, 'OP', 'OR')

        self.code_generator.add_code(strip_multiline_string(self.END),
                                     self.end_loc)


class ArithUnOp(ASTNode):
    """Abstract Syntax Tree Node for for arithmetic unary operations"""

    START = """# codeaa(e1)
        LOADI ACC 0;  # 0 in ACC laden
        LOADIN SP IN2 1;  # Wert von e1 in IN2 laden
        SUB ACC IN2;  # (0 - e1) in ACC laden
        """
    START_LOC = 3

    BITWISE_NOT = "SUBI ACC 1;  # zu Bitweise Negation unwandeln\n"
    BITWISE_NEGATION_LOC = 1

    END = "STOREIN SP ACC 1;  # Ergebnis in oberste Stack-Zelle\n"
    END_LOC = 1

    def _update_match_args(self, ):
        self.operation = self.children[0]
        self.operand = self.children[1]

    __match_args__ = ("operation", "operand")

    def visit(self, ):
        self.code_generator.add_code("# Arithmetic Unary Operation start\n", 0)

        self.operand.visit()

        self.code_generator.add_code(strip_multiline_string(self.START),
                                     self.START_LOC)

        self._adapt_code()

        self.code_generator.add_code(self.END, self.END_LOC)

        self.code_generator.add_code("# Arithmetic Unary Operation end\n", 0)

    def _pretty_comments(self, ):
        if global_vars.args.verbose:
            self.code_generator.replace_code_pre(self.START, "e1", self.value)

    def _adapt_code(self, ):
        match self.operation:
            case Not():
                self.code_generator.add_code(self.BITWISE_NOT,
                                             self.BITWISE_NEGATION_LOC)
            case Minus():
                pass
