from abstract_syntax_tree import ASTNode, strip_multiline_string
from logic_nodes import LogicAndOrNode
from arithmetic_nodes import ArithBinOp, ArithUnOp
from symbol_table import VariableSymbol, ConstantSymbol
from errors import UnknownIdentifierError
import global_vars
from dummy_nodes import Const, Int, Char, Void, Identifier, Number, Character

# TODO: genauer begutachten: "oder codela(e), falls logischer Ausdruck"


class Assign(ASTNode):
    """Abstract Syntax Tree Node for assignement"""

    ASSIGN = """# codeaa(e) (oder codela(e), falls logischer Ausdruck)
        LOADIN SP ACC 1;  # Wert von e1 in ACC laden
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        """
    ASSIGN_LOC = 2

    ASSIGN_MORE = "STORE ACC var_address;  # Wert von e1 in Variable v1 speichern\n"
    ASSIGN_MORE_LOC = 1

    def _update_match_args(self, ):
        self.variable = self.children[0]
        self.expression = self.children[1]

    __match_args__ = ("variable", "expression")

    def visit(self, ):
        if self.ignore:
            self.variable.visit()
            return

        self._update_match_args()

        self.code_generator.add_code(
            "# Assignment start or new sub-assignment start\n", 0)

        self._pretty_comments()

        self.variable.visit()

        try:
            self._assignment()
        except KeyError:
            # repackage the error
            raise UnknownIdentifierError(self.variable)

        self.code_generator.add_code(
            "# Assignment end or sub-assignment end\n", 0)

    def _pretty_comments(self, ):
        if global_vars.args.verbose:
            self.ASSIGN = self.code_generator.replace_code_pre(
                strip_multiline_string(self.ASSIGN), "e1",
                str(self.expression))
            self.ASSIGN_MORE = self.code_generator.replace_code_pre(
                strip_multiline_string(self.ASSIGN_MORE), "e1",
                str(self.expression))
            self.ASSIGN_MORE = self.code_generator.replace_code_pre(
                strip_multiline_string(self.ASSIGN_MORE), "v1",
                str(self.variable))

    def _assignment(self, ):
        match self:
            case Assign(Alloc(Const(), _, Identifier(name)), (Number(value) | Character(value))):
                self.symbol_table.resolve(name).value = value
            # nested assignment that is the assignment of another assignment
            case Assign((Identifier(name) | Alloc(_, _, Identifier(name))), Assign(_, _)):
                self.expression.visit()

                self._adapt_code(name)
            # assigment that assigns a variable to a expression
            case Assign((Identifier(name) | Alloc(_, _, Identifier(name))), _):
                self.expression.visit()

                self.code_generator.add_code(
                    strip_multiline_string(self.ASSIGN), self.ASSIGN_LOC)

                self._adapt_code(name)

    def _adapt_code(self, name):
        self.ASSIGN_MORE = self.code_generator.replace_code_pre(
            self.ASSIGN_MORE, "var_address", self.symbol_table.resolve(name).value)

        self.code_generator.add_code(self.ASSIGN_MORE, self.ASSIGN_MORE_LOC)


class Alloc(ASTNode):
    """Abstract Syntax Tree Node for allocation"""

    __match_args__ = ("const", "prim_datatype", "identifier")

    def _update_match_args(self):
        if isinstance(self.children[0], Const):
            self.const = self.children[0]
            self.prim_dt = self.children[1]
            self.identifier = self.children[2]
        else:
            self.prim_dt = self.children[0]
            self.identifier = self.children[1]

    def _get_childtokenvalue(self, idx):
        return self.children[idx].token.value

    def _get_childtoken(self, idx):
        return self.children[idx].token

    def _get_childtokenposition(self, idx):
        return self.children[idx].token.position

    def visit(self, ):
        self._update_match_args()
        self.code_generator.add_code("# Allocation start\n", 0)

        if self._get_childtokenvalue(0) == 'const':
            # the value of a ConstantNode is the name of the Constantnode if
            # there wasn't assigned a value directly to the constant which has
            # to be resolved internally in the RETI or by a RETI Code
            # Interpreter
            const = ConstantSymbol(self._get_childtokenvalue(1),
                                   self.symbol_table.resolve(self.token.value),
                                   self._get_childtokenposition(1))
            self.symbol_table.define(const)
        else:  # self._get_childtokenvalue(0) == 'var'
            var = VariableSymbol(self._get_childtokenvalue(1),
                                 self.symbol_table.resolve(self.token.value),
                                 self._get_childtokenposition(1))
            self.symbol_table.define(var)
            self.symbol_table.allocate(var)

        self.code_generator.add_code(
            "# successfully allocated " + str(self._get_childtokenvalue(1)) +
            "\n", 0)
        self.code_generator.add_code("# Allocation end\n", 0)

    def __repr__(self, ):
        acc = f"({self._get_childtoken(0)} {self.token} "\
            f"{self._get_childtoken(1)})"
        return acc
