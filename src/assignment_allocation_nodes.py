from abstract_syntax_tree import ASTNode, strip_multiline_string
from symbol_table import VariableSymbol, ConstantSymbol, BuiltInTypeSymbol
from errors import Errors
from dummy_nodes import NT
from arithmetic_nodes import Identifier, Number, Character
import global_vars


class Assignment(ASTNode):
    """Abstract Syntax Tree Node for assignement"""

    assign = strip_multiline_string(
        """LOADIN SP ACC 1;  # Wert von e1 in ACC laden
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        """)
    assign_loc = 2

    assign_more = "STORE ACC var_address;  # Wert von e1 in Variable v1 speichern\n"
    assign_more_loc = 1

    def update_match_args(self, ):
        self.location = self.children[0]
        self.expression = self.children[1]

    __match_args__ = ("location", "expression")

    def visit(self, ):
        self.update_match_args()

        self.code_generator.add_code(
            f"# Zuweisung {self} Start\n", 0)

        self.location.update_match_args()
        self.location.visit()

        self._pretty_comments()

        try:
            self._assignment()
        except KeyError:
            # repackage the error
            match self.location:
                case Identifier(value, position):
                    raise Errors.UnknownIdentifierError(value, position)

        self.code_generator.add_code(
            f"# Zuweisung {self} Ende\n", 0)

    def _pretty_comments(self, ):
        if global_vars.args.verbose:
            self.assign = self.code_generator.replace_code_pre(
                self.assign, "e1", str(self.expression))
            self.assign_more = self.code_generator.replace_code_pre(
                self.assign_more, "e1", str(self.expression))
            match self.location:
                case Allocation(_, _, _):
                    self.assign_more = self.code_generator.replace_code_pre(
                        self.assign_more, "v1", str(self.location.identifier))
                case _:
                    self.assign_more = self.code_generator.replace_code_pre(
                        self.assign_more, "v1", str(self.location))

    def _comment_for_constant(self, name, value):
        self.code_generator.add_code("# Konstante " + name + " in Symboltabelle "
                                     "den Wert " + value + " zugewiesen\n", 0)

    def _assignment(self, ):
        match self:
            case Assignment(Allocation(NT.Const(), _, Identifier(name)), assignment):
                match assignment:
                    case (Number(value, position) | Character(value, position)):
                        symbol = self.symbol_table.resolve(name)
                        self._error_check(name, symbol, value, position)
                        symbol.value = value
                        self._comment_for_constant(name, value)
                    case Identifier(value, position):
                        symbol = self.symbol_table.resolve(name)
                        self._error_check(
                            name, symbol, self.symbol_table.resolve(value).value, position)
                        symbol.value = self.symbol_table.resolve(value).value
                        self._comment_for_constant(name, value)
            # nested assignment that is the assignment of another assignment
            case Assignment((Identifier(name) | Allocation(_, _, Identifier(name))), Assignment(_, _)):
                self.expression.visit()

                self._adapt_code(name)
            # assigment that assigns a variable to a expression
            case Assignment((Identifier(name) | Allocation(_, _, Identifier(name))), _):
                # all literals in the assignent (context of the variable) must
                # be in the range of the datatype of the variable
                global_vars.variable_context = self.symbol_table.resolve(name)

                self.expression.visit()

                global_vars.variable_context = None

                self.code_generator.add_code(self.assign, self.assign_loc)

                self._adapt_code(name)

    def _adapt_code(self, name):
        self.assign_more = self.code_generator.replace_code_pre(
            self.assign_more, "var_address", self.symbol_table.resolve(name).value)

        self.code_generator.add_code(self.assign_more, self.assign_more_loc)

    def _error_check(self, name, symbol, value, position):
        range_from = symbol.datatype.range_from_to[0]
        range_to = symbol.datatype.range_from_to[1]
        if not (int(value) <= range_to):  # range_from <=
            raise Errors.TooLargeLiteralError(
                name, symbol.position, symbol.datatype, range_from, range_to, value, position)

    def __repr__(self):
        if len(self.children) == 2:
            return f"({self.children[0]} = {self.children[1]})"

        return super().__repr__()


class Allocation(ASTNode):
    """Abstract Syntax Tree Node for allocation"""

    def update_match_args(self):
        if isinstance(self.children[0], NT.Const):
            self.const = self.children[0]
            self.prim_dt = self.children[1]
            self.identifier = self.children[2]
        else:
            self.const = None
            self.prim_dt = self.children[0]
            self.identifier = self.children[1]

    __match_args__ = ("const", "prim_dt", "identifier")

    def visit(self, ):
        self.update_match_args()

        self.code_generator.add_code(f"# Allokation {self} Start\n", 0)

        self._adapt_code()

        self.code_generator.add_code(f"# Allokation {self} Ende\n", 0)

    def _pretty_comments(self, const_var, name, dtype, value=None):
        suppl = ""
        if value:
            suppl += " mit Adresse " + value

        self.code_generator.add_code("# " + const_var + " " + name + " vom Typ "
                                     + dtype + suppl + " zur Symboltabelle "
                                     "hinzugefügt\n", 0)

    def _adapt_code(self, ):
        match self:
            case Allocation(NT.Const(), (NT.Char(dtype) | NT.Int(dtype)), Identifier(name, position)):
                self._error_check(name, position)
                constant = ConstantSymbol(
                    name, self.symbol_table.resolve(dtype), position)
                self.symbol_table.define(constant)
                self._pretty_comments("Konstante", name, dtype)
            case Allocation(_, (NT.Char(dtype) | NT.Int(dtype)), Identifier(name, position)):
                self._error_check(name, position)
                variable = VariableSymbol(
                    name, self.symbol_table.resolve(dtype), position)
                self.symbol_table.define(variable)
                address = self.symbol_table.allocate(variable)
                self._pretty_comments("Variable", name, dtype, address)

    def _error_check(self, found_name, found_pos):
        if self.symbol_table.symbols.get(found_name):
            first = self.symbol_table.symbols[found_name]
            raise Errors.RedefinitionError(
                found_name, found_pos, first.name, first.position)

    def __repr__(self, ):
        return self.alternative_to_string()
