from abstract_syntax_tree import ASTNode, strip_multiline_string
from symbol_table import VariableSymbol, ConstantSymbol
from errors import Errors
from dummy_nodes import NT
import global_vars


class ArithmeticOperand(ASTNode):
    """Abstract Syntax Tree Node for arithmetic variables and constants"""

    start = "SUBI SP 1;  # Stack um eine Zelle erweitern\n"
    constant = "LOADI ACC encode(w);  # Wert von e1 in ACC laden\n"
    constant_identifier = "LOADI ACC encode(c);  # Wert von e1 in ACC laden\n"
    variable_identifier = "LOAD ACC var_identifier;  # Wert von e1 in ACC laden\n"
    end = "STOREIN SP ACC 1;  # Wert in oberste Stacke-Zelle\n"

    all_loc = 1

    __match_args__ = ("value", "position")

    def visit(self, ):
        self.code_generator.add_code(
            f"# Arithmetischer Operand {self} Start\n", 0)

        self.code_generator.add_code(self.start, self.all_loc)

        try:
            self._adapt_code()
        except KeyError:
            # repackage the error
            match self:
                case Variable_Constant_Identifier(value, position):
                    raise Errors.UnknownIdentifierError(value, position)

        self.code_generator.add_code(self.end, self.all_loc)

        self.code_generator.add_code(
            f"# Arithmetischer Operand {self} Ende\n", 0)

    def _adapt_code(self, ):
        match self:
            case Variable_Constant_Identifier(value):
                symbol = self.symbol_table.resolve(value)
                match symbol:
                    case VariableSymbol(value):
                        self.variable_identifier = self._pretty_comments(
                            self.variable_identifier)
                        self.variable_identifier = self.code_generator.replace_code_pre(
                            self.variable_identifier, "var_identifier", value)
                        self.code_generator.add_code(self.variable_identifier,
                                                     self.all_loc)
                    case ConstantSymbol(value):
                        self.constant_identifier = self._pretty_comments(
                            self.constant_identifier)
                        self.constant_identifier = self.code_generator.replace_code_pre(
                            self.constant_identifier, "encode(c)", value)
                        self.code_generator.add_code(self.constant_identifier,
                                                     self.all_loc)
            case (Number(value) | Character(value)):
                self.constant = self._pretty_comments(self.constant)
                self.constant = self.code_generator.replace_code_pre(
                    self.constant, "encode(w)", value)
                self.code_generator.add_code(self.constant, self.all_loc)

    def _pretty_comments(self, code):
        if global_vars.args.verbose:
            code = self.code_generator.replace_code_pre(
                code, "e1", self.value)
        return code


class Variable_Constant_Identifier(ArithmeticOperand):
    pass


class Number(ArithmeticOperand):
    pass


class Character(ArithmeticOperand):
    pass


class ArithmeticBinaryOperation(ASTNode):
    """Abstract Syntax Tree Node for for arithmetic binary operations.
    Dient als Container für andere Nodes, daher ist es nicht genauer
    spezifiert, als Addition oder Subtraktion, da erst später feststeht, ob die
    Binary Operation eine Addition oder Subtraktion ist etc."""

    end = strip_multiline_string(
        """LOADIN SP ACC 2;  # Wert von e1 in ACC laden
        LOADIN SP IN2 1;  # Wert von e2 in IN2 laden
        OP ACC IN2;  # Wert von e1 binop e2 in ACC laden
        STOREIN SP ACC 2;  # Ergebnis in zweitoberste Stack-Zelle
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        """)
    end_loc = 5

    def update_match_args(self):
        self.left_operand = self.children[0]
        self.operation = self.children[1]
        self.right_operand = self.children[2]

    __match_args__ = ("left_operand", "operation", "right_operand")

    def visit(self, ):
        self.update_match_args()

        self.code_generator.add_code(
            f"# Arithmetische binäre Operation {self} Start\n", 0)

        self._pretty_comments()

        self.left_operand.visit()
        self.right_operand.visit()

        self._adapt_code()

        self.code_generator.add_code(self.end, self.end_loc)

        self.code_generator.add_code(
            f"# Arithmetische binäre Operation {self} Ende\n", 0)

    def _pretty_comments(self, ):
        if global_vars.args.verbose:
            self.end = self.code_generator.replace_code_pre(
                self.end, 'e1 binop e2', str(self))
            self.end = self.code_generator.replace_code_pre(
                self.end, 'e1', str(self.left_operand))
            self.end = self.code_generator.replace_code_pre(
                self.end, 'e2', str(self.right_operand))

    def _adapt_code(self, ):
        match self:
            case ArithmeticBinaryOperation(_, NT.Add(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'ADD')
            case ArithmeticBinaryOperation(_, NT.Sub(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'SUB')
            case ArithmeticBinaryOperation(_, NT.Mul(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'MUL')
            case ArithmeticBinaryOperation(_, NT.Div(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'DIV')
            case ArithmeticBinaryOperation(_, NT.Mod(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'MOD')
            case ArithmeticBinaryOperation(_, NT.Oplus, _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'OPLUS')
            case ArithmeticBinaryOperation(_, NT.And(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'AND')
            case ArithmeticBinaryOperation(_, NT.Or(), ):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'OR')

    def __repr__(self, ):
        return self.alternative_to_string()


class ArithmeticUnaryOperation(ASTNode):
    """Abstract Syntax Tree Node for for arithmetic unary operations"""

    start = strip_multiline_string(
        """LOADI ACC 0;  # 0 in ACC laden
        LOADIN SP IN2 1;  # Wert von e1 in IN2 laden
        SUB ACC IN2;  # (0 - e1) in ACC laden
        """)
    start_loc = 3

    bitwise_not = "SUBI ACC 1;  # zu Bitweise Negation unwandeln\n"
    bitwise_not_loc = 1

    end = "STOREIN SP ACC 1;  # Ergebnis in oberste Stack-Zelle\n"
    end_loc = 1

    def update_match_args(self, ):
        self.operation = self.children[0]
        self.operand = self.children[1]

    __match_args__ = ("operation", "operand")

    def visit(self, ):
        self.update_match_args()

        self.code_generator.add_code(
            f"# Arithmetische unäre Operation {self} Start\n", 0)

        self._pretty_comments()

        self.operand.visit()

        self.code_generator.add_code(self.start, self.start_loc)

        self._adapt_code()

        self.code_generator.add_code(self.end, self.end_loc)

        self.code_generator.add_code(
            f"# Arithmetische unäre Operation {self} Ende\n", 0)

    def _pretty_comments(self, ):
        if global_vars.args.verbose:
            self.code_generator.replace_code_pre(
                self.start, "e1", str(self.operand))

    def _adapt_code(self, ):
        match self:
            case ArithmeticUnaryOperation(NT.Negation(), _):
                self.code_generator.add_code(self.bitwise_not,
                                             self.bitwise_not_loc)

    def __repr__(self, ):
        return self.alternative_to_string()
