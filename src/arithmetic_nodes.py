from abstract_syntax_tree import ASTNode, strip_multiline_string
from symbol_table import VariableSymbol, ConstantSymbol
from errors import UnknownIdentifierError
from dummy_nodes import NT
import global_vars


class ArithOperand(ASTNode):
    """Abstract Syntax Tree Node for arithmetic variables and constants"""

    start = "SUBI SP 1;  # Stack um eine Zelle erweitern\n"
    constant = "LOADI ACC encode(w);  # Wert von e1 in ACC laden\n"
    constant_identifier = "LOADI ACC encode(c);  # Wert von e1 in ACC laden\n"
    variable_identifier = "LOAD ACC var_identifier;  # Wert von e1 in ACC laden\n"
    end = "STOREIN SP ACC 1;  # Wert in oberste Stacke-Zelle\n"

    all_loc = 1

    __match_args__ = ("value", "position")

    def visit(self, ):
        self.code_generator.add_code("# Arithmetic Operand start\n", 0)

        self.code_generator.add_code(self.start, self.all_loc)

        try:
            self._adapt_code()
        except KeyError:
            # repackage the error
            raise UnknownIdentifierError(self.value)

        self.code_generator.add_code(self.end, self.all_loc)

        self.code_generator.add_code("# Arithmetic Operand end\n", 0)

    def _adapt_code(self, ):
        match self:
            case NT.Identifier(value):
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
            case (NT.Number(value) | NT.Character(value)):
                self.constant = self._pretty_comments(self.constant)
                self.constant = self.code_generator.replace_code_pre(
                    self.constant, "encode(w)", value)
                self.code_generator.add_code(self.constant, self.all_loc)

    def _pretty_comments(self, code):
        if global_vars.args.verbose:
            code = self.code_generator.replace_code_pre(
                code, "e1", self.value)
        return code


class ArithBinOp(ASTNode):
    """Abstract Syntax Tree Node for for arithmetic binary operations.
    Dient als Container für andere Nodes, daher ist es nicht genauer
    spezifiert, als Addition oder Subtraktion, da erst später feststeht, ob die
    Binary Operation eine Addition oder Subtraktion ist etc."""

    end = """# codeaa(e1)
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
        self._update_match_args()

        self.code_generator.add_code(
            "# Arithmetic Binary Operation start\n", 0)

        self.left_operand.visit()
        self.right_operand.visit()

        self._pretty_comments()

        self._adapt_code()

        self.code_generator.add_code(strip_multiline_string(self.end),
                                     self.end_loc)

        self.code_generator.add_code("# Arithmetic Binary Operation end\n", 0)

    def _pretty_comments(self, ):
        if global_vars.args.verbose:
            self.end = self.code_generator.replace_code_pre(
                strip_multiline_string(self.end), 'e1', str(self.left_operand))
            self.end = self.code_generator.replace_code_pre(
                strip_multiline_string(self.end), 'e2', str(self.right_operand))
            self.end = self.code_generator.replace_code_pre(
                strip_multiline_string(self.end), 'e1 binop e2', str(self))

    def _adapt_code(self, ):
        match self:
            case ArithBinOp(_, NT.Add(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'ADD')
            case ArithBinOp(_, NT.Sub(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'SUB')
            case ArithBinOp(_, NT.Mul(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'MUL')
            case ArithBinOp(_, NT.Div(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'DIV')
            case ArithBinOp(_, NT.Mod(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'MOD')
            case ArithBinOp(_, NT.Oplus, _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'OPLUS')
            case ArithBinOp(_, NT.And(), _):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'AND')
            case ArithBinOp(_, NT.Or(), ):
                self.end = self.code_generator.replace_code_pre(
                    self.end, 'OP', 'OR')


class ArithUnOp(ASTNode):
    """Abstract Syntax Tree Node for for arithmetic unary operations"""

    start = """# codeaa(e1)
        LOADI ACC 0;  # 0 in ACC laden
        LOADIN SP IN2 1;  # Wert von e1 in IN2 laden
        SUB ACC IN2;  # (0 - e1) in ACC laden
        """
    start_loc = 3

    bitwise_not = "SUBI ACC 1;  # zu Bitweise Negation unwandeln\n"
    bitwise_not_loc = 1

    end = "STOREIN SP ACC 1;  # Ergebnis in oberste Stack-Zelle\n"
    end_loc = 1

    def _update_match_args(self, ):
        self.operation = self.children[0]
        self.operand = self.children[1]

    __match_args__ = ("operation", "operand")

    def visit(self, ):
        self.code_generator.add_code("# Arithmetic Unary Operation start\n", 0)

        self.operand.visit()

        self.code_generator.add_code(strip_multiline_string(self.start),
                                     self.start_loc)

        self._adapt_code()

        self.code_generator.add_code(self.end, self.end_loc)

        self.code_generator.add_code("# Arithmetic Unary Operation end\n", 0)

    def _pretty_comments(self, ):
        if global_vars.args.verbose:
            self.code_generator.replace_code_pre(
                self.start, "e1", str(self.operand))

    def _adapt_code(self, ):
        match self:
            case ArithUnOp(NT.Not(), _):
                self.code_generator.add_code(self.bitwise_not,
                                             self.bitwise_not_loc)
            case ArithUnOp(NT.Minus(), _):
                pass
