from abstract_syntax_tree import ASTNode, strip_multiline_string
from symbol_table import VariableSymbol, ConstantSymbol
from errors import UnknownIdentifierError
import global_vars
from dummy_nodes import NT
from arithmetic_nodes import Identifier, Number, Character


class Assign(ASTNode):
    """Abstract Syntax Tree Node for assignement"""

    assign = strip_multiline_string("""# codeaa(e1) (oder codela(e1), falls logischer Ausdruck)
        LOADIN SP ACC 1;  # Wert von e1 in ACC laden
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        """)
    assign_loc = 2

    assign_more = "STORE ACC var_address;  # Wert von e1 in Variable v1 speichern\n"
    assign_more_loc = 1

    def _update_match_args(self, ):
        self.variable = self.children[0]
        self.expression = self.children[1]

    __match_args__ = ("variable", "expression")

    def visit(self, ):
        self._update_match_args()

        self.code_generator.add_code(
            "# Zuweisung oder new Sub-Zuweisung Start\n", 0)

        self._pretty_comments()

        self.variable.visit()

        try:
            self._assignment()
        except KeyError:
            # repackage the error
            raise UnknownIdentifierError(self.variable)

        self.code_generator.add_code(
            "# Zuweisung oder Sub-Zuweisung Ende\n", 0)

    def _pretty_comments(self, ):
        if global_vars.args.verbose:
            self.assign = self.code_generator.replace_code_pre(
                self.assign, "e1", str(self.expression))
            self.assign_more = self.code_generator.replace_code_pre(
                self.assign_more, "e1", str(self.expression))
            self.assign_more = self.code_generator.replace_code_pre(
                self.assign_more, "v1", str(self.variable))

    def _assignment(self, ):
        match self:
            case Assign(Alloc(NT.Const(), _, Identifier(name)), (Number(value) | Character(value))):
                self.symbol_table.resolve(name).value = value
            # nested assignment that is the assignment of another assignment
            case Assign((Identifier(name) | Alloc(_, _, Identifier(name))), Assign(_, _)):
                self.expression.visit()

                self._adapt_code(name)
            # assigment that assigns a variable to a expression
            case Assign((Identifier(name) | Alloc(_, _, Identifier(name))), _):
                self.expression.visit()

                self.code_generator.add_code(self.assign, self.assign_loc)

                self._adapt_code(name)
            case _:
                # raise InvalidConstantAssignment(self.variable)
                # TODO
                pass

    def _adapt_code(self, name):
        self.assign_more = self.code_generator.replace_code_pre(
            self.assign_more, "var_address", self.symbol_table.resolve(name).value)

        self.code_generator.add_code(self.assign_more, self.assign_more_loc)

    def __repr__(self):
        if len(self.children) == 2:
            return f"({self.children[0]} = {self.children[1]})"

        return super().__repr__()


class Alloc(ASTNode):
    """Abstract Syntax Tree Node for allocation"""

    def _update_match_args(self):
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
        self._update_match_args()

        self.code_generator.add_code("# Allokation Start\n", 0)

        self._adapt_code()

        self.code_generator.add_code("# Allokation Ende\n", 0)

    def _pretty_comments(self, const_var, name, dtype):
        self.code_generator.add_code("# " + const_var + " " + name + " vom Typ "
                                     + dtype + " zur Symboltabelle"
                                     "hinzugefügt\n", 0)

    def _adapt_code(self, ):
        match self:
            case Alloc(NT.Const(), (NT.Char(dtype) | NT.Int(dtype)), Identifier(name, position)):
                constant = ConstantSymbol(
                    name, self.symbol_table.resolve(dtype), position)
                self.symbol_table.define(constant)
                self._pretty_comments("Konstante", name, dtype)
            case Alloc(_, (NT.Char(dtype) | NT.Int(dtype)), Identifier(name, position)):
                variable = VariableSymbol(
                    name, self.symbol_table.resolve(dtype), position)
                self.symbol_table.define(variable)
                self.symbol_table.allocate(variable)
                self._pretty_comments("Variable", name, dtype)
