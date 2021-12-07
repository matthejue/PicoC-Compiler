from abstract_syntax_tree import ASTNode, strip_multiline_string
from logic_nodes import LogicAndOrNode
from arithmetic_nodes import ArithmeticBinaryOperationNode, ArithmeticVariableConstantNode
from symbol_table import VariableSymbol, ConstantSymbol
from errors import UnknownIdentifierError
import global_vars


class AssignmentNode(ASTNode):

    """Abstract Syntax Tree Node for assignement"""

    # TODO: genauer begutachten: "oder codela(e), falls logischer Ausdruck"

    __match_args__ = ("variable", "expression")

    def __init__(self, tokentypes, variable=None, expression=None):
        super().__init__(tokentypes)
        if (variable and expression):
            self.children[0] = variable
            self.children[1] = expression

    assignment = """# codeaa(e) (oder codela(e), falls logischer Ausdruck)
        LOADIN SP ACC 1;  # Wert von expression in ACC laden
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        """

    assignment_loc = 2

    assign_more = "STORE ACC var_address;  # Wert von e in Variable xyz speichern\n"

    assign_more_loc = 1

    def _get_identifier_name(self):
        # AllocationNode needs a special treatment, because it it's token only
        # tells the type but not the value
        if isinstance(self.children[0], AllocationNode):
            # AssignmentNode(AllocationNode(TokenNode(TT.CONST, 'const'),
            #   TokenNode(TT.IDENTIFIER, x)), AssignmentNode(LogicAndOrNode(LogicAndOrNode(...))))
            return self.children[0].children[1].token.value
        else:
            # AssignmentNode(TokenNode(TT.IDENTIFIER, 'x'),
            #   AssignmentNode(LogicAndOrNode(LogicAndOrNode(...))))
            return self.children[0].token.value

    def _get_identifier_token(self):
        # AllocationNode needs a special treatment, because it it's token only
        # tells the type but not the value
        if isinstance(self.children[0], AllocationNode):
            # AssignmentNode(AllocationNode(TokenNode(TT.CONST, 'const'),
            #   TokenNode(TT.IDENTIFIER, x)), AssignmentNode(LogicAndOrNode(LogicAndOrNode(...))))
            return self.children[0].children[1].token
        else:
            # AssignmentNode(TokenNode(TT.IDENTIFIER, 'x'),
            #   AssignmentNode(LogicAndOrNode(LogicAndOrNode(...))))
            return self.children[0].token

    def _get_expression(self, ):
        return self.children[1]

    def _is_last_assignment(self, ):
        # AssignmentNode(..., AssignmentNode(LogicAndOrNode(LogicAndOrNode(...))))
        return isinstance(self.children[1].children[0], LogicAndOrNode) or isinstance(self.children[1].children[0], ArithmeticBinaryOperationNode)

    def _is_constant_identifier_on_left_side(self, ):
        # can only be found out by analysing what type of Symbol there is,
        # because a TokenNode doesn't tell whether a symbol is a constant or
        # not. Only a AllocationNode would have information whether a symbol
        # is a constant by by his first childnode
        return isinstance(self.symbol_table.resolve(
            self._get_identifier_name()), ConstantSymbol)

    def _is_single_value_on_right_side(self, ):
        # AssignmentNode(TokenNode(TT.IDENTIFIER, 'x'),
        #   AssignmentNode(ArithmeticBinaryOperationNode(ArithmeticBinaryOperationNode(ArithmeticVariableConstantNode))))
        # TODO: diese Funktion wird später unnötig, es unmöglich ist, dass bei
        # einer Konstante was anderes als ein einzelner Wert auf der anderen
        # Seite steht
        return len(self.children[1].children[0].children[0].children) == 1

    def _assign_number_to_constant_identifier(self):
        # AssignmentNode(TokenNode(TT.IDENTIFIER, 'x'),
        #   AssignmentNode(ArithmeticBinaryOperationNode(ArithmeticBinaryOperationNode(ArithmeticVariableConstantNode))))
        # TODO: das geht schöner
        self.symbol_table.resolve(self._get_identifier_name(
        )).value = self.children[1].children[0].children[0].children[0].token.value

    def visit(self, ):
        # if it's just a throw-away node that had to be taken
        if len(self.children) == 1:
            self.children[0].visit()
            return

        self.code_generator.add_code(
            "# Assignment start or new sub-assignment\n", 0)

        self.children[0].visit()

        # in case of a ConstantSymbol and a assignment with a number on the
        # right side of the =, the value gets assigned immediately
        try:
            self._assign_to_identifier()
        except KeyError:
            # repackage the error
            raise UnknownIdentifierError(self._get_identifier_token())

    def _assign_to_identifier(self, ):
        #         match self:
        #             case AssignmentNode([tokentype], AllocationNode(), ArithmeticBinaryOperationNode()):
        #                 pass
        #
        if self._is_constant_identifier_on_left_side() and self._is_single_value_on_right_side():
            self._assign_number_to_constant_identifier()
        # case of a VariableSymbol
        else:
            self.children[1].visit()

            if self._is_last_assignment():

                if global_vars.args.verbose:
                    global_vars.args.verbose = False
                    self.assign_more = self.code_generator.replace_code_pre(
                        strip_multiline_string(self.assign_more), "expression", str(self._get_expression()))
                    global_vars.args.verbose = True

                self.code_generator.add_code(strip_multiline_string(self.assignment),
                                             self.assignment_loc)

            self.assign_more = self.code_generator.replace_code_pre(
                self.assign_more, "var_address",
                self.symbol_table.resolve(self._get_identifier_name()).value)

            self.code_generator.add_code(
                self.assign_more, self.assign_more_loc)

        self.code_generator.add_code(
            "# Assignment end or sub-assignment end\n", 0)


class AllocationNode(ASTNode):

    """Abstract Syntax Tree Node for allocation"""

    def _get_childtokenvalue(self, idx):
        return self.children[idx].token.value

    def _get_childtoken(self, idx):
        return self.children[idx].token

    def _get_childtokenposition(self, idx):
        return self.children[idx].token.position

    def visit(self, ):
        self.code_generator.add_code("# Allocation start\n", 0)

        if self._get_childtokenvalue(0) == 'const':
            # the value of a ConstantNode is the name of the Constantnode if
            # there wasn't assigned a value directly to the constant which has
            # to be resolved internally in the RETI or by a RETI Code
            # Interpreter
            const = ConstantSymbol(
                self._get_childtokenvalue(1),
                self.symbol_table.resolve(self.token.value),
                self._get_childtokenposition(1))
            self.symbol_table.define(const)
        else:  # self._get_childtokenvalue(0) == 'var'
            var = VariableSymbol(
                self._get_childtokenvalue(1),
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
