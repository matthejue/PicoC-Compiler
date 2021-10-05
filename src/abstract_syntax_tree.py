# from enum import Enum
from lexer import Token, TT
from code_generator import CodeGenerator
from symbol_table import SymbolTable, VariableSymbol, ConstantSymbol


class TokenNode:

    """Abstract Syntax Tree Node for Leaves"""

    def __init__(self, token):

        self.token = token

    def getNodeType(self):
        """

        :returns: None

        """
        return self.token.type

    def isEmpty(self):
        return not self.token

    def __repr__(self):
        return f"{self.token}"

    def visit(self, ):
        pass


class ASTNode(TokenNode):

    """Node of a Normalized Heterogeneous Abstract Syntax Tree (AST), partially
    also has some different Normalized Heterogeneous AST Nodes. A AST holds the
    relevant Tokens and represents grammatical relationships the parser came
    across.  Homogeneous AST means having only one node type and all childs
    normalized in a list. Normalized Heterogeneous means different Node types
    and all childs normalized in a list"""

    lines_of_code = 0
    reti_code = ""

    def __init__(self, tokentypes):
        # at the time of creation the tokenvalue is unknown
        self.children = []
        # the first tokentype is always the actual tokentype and the others are
        # for symbols like e.g. '-' which had to get a seperate tokentype
        # because they overlap with e.g. unary and binary operations
        super().__init__(Token(tokentypes[0], None))
        self.tokentypes = tokentypes
        # decide whether a node should be ignored and just show his children if
        # he has any
        self.ignore = True
        self.code_generator = CodeGenerator()
        self.symbol_table = SymbolTable(100)

    def addChild(self, node):
        """

        :returns: None
        """
        # in case the representative tokens of self appear as attribute of a
        # TokenNode, the token of self can finally register the right value
        # Because of e.g. <alloc>: <word> <word> ... one should only take the
        # first TokenNode matching the possible representative tokens
        if self._is_tokennode(node) and node.token.type in\
                self.tokentypes:
            self.token.value = node.token.value
            self.ignore = False
            return

        self.children += [node]

    def _is_tokennode(self, node):
        """checks if something is a TokenNode

        :returns: boolean

        """
        # being not instance of ASTNode means being instance of TokenNode
        return not isinstance(node, ASTNode)

    def get_childvalue(self, idx):
        return self.children[idx].token.value

    def get_childtoken(self, idx):
        return self.children[idx].token

    def __repr__(self):
        # if Node doesn't even reach it's own operation token it's unnecessary
        # and should be skipped
        if not self.children:
            return f"{self.token}"
        # TODO: swap the order of this conditional statements when finishing
        # the project because if a node isn't activated it should never be
        # seen, it's just useful for debugging to have it the other way round
        elif self.ignore:
            return f"{self.children[0]}"

        acc = f"({self.token}"

        for child in self.children:
            acc += f" {child}"

        acc += ")"
        return acc


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

        self.children[0].visit()

        self.code_generator.add_code_open(
            strip_multiline_string(self.condition_check),
            self.condition_check_loc)

        for child in self.children[1:]:
            child.visit()

        self.code_generator.replace_jump("codelength(af) + 2", 2)

        self.code_generator.replace_jump_back([self.end],
                                              "(codelength(af) +"
                                              " codelength(l) + 3)")
        # + 3 sind schon mit drin

        self.code_generator.add_code_close(
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

        # little hack to get a artificial ucp_stock entry
        self.code_generator.add_code_open("", 0)

        for child in self.children[1:]:
            child.visit()

        self.children[0].visit()

        self.code_generator.replace_jump_back([self.condition_check],
                                              "(codelength(af) + "
                                              "codelength(l) + 2), 2")

        self.code_generator.add_code_close(strip_multiline_string(self.condition_check),
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
            self.token = Token(TT.DO_WHILE, "do while")
            self.ignore = False
            return

        self.children += [node]


class IfNode(ASTNode):

    """Abstract Syntax Tree Node for If"""

    # TODO

    start = """# codela(l)
        LOADIN SP ACC 1; # Wert von l in ACC laden
        ADDI SP 1; # Stack um eine Zelle verkürzen
        JUMP= codelength(af) + 1; # af überspringen
        # code(af)
        """

    start_loc = 3

    def visit(self, ):
        self.code_generator.add_code("# If start\n", 0)

        self.children[0].visit()

        self.code_generator.add_code_open(
            strip_multiline_string(self.start), self.start_loc)

        for child in self.children[1:]:
            child.visit()

        self.code_generator.replace_jump("codelength(af) + 1", 1)

        self.code_generator.add_code_close("", 0)

        self.code_generator.add_code("# If end\n", 0)


class IfElseNode(ASTNode):

    """Abstract Syntax Tree Node for Else"""

    # TODO

    start = """# codela(l)
        LOADIN SP ACC 1; # Wert von l in ACC laden
        ADDI SP 1; # Stack um eine Zelle verkürzen
        JUMP= codelength(af1) + 2; # af1 überspringen
        # code(af1)
        """

    start_loc = 3

    middle = """JUMP {codelength(af2) + 1};
        # code(af2)
        """

    middle_loc = 1

    def visit(self, ):
        self.code_generator.add_code("# If Else start\n", 0)

        self.children[0].visit()

        self.code_generator.add_code_open(
            strip_multiline_string(self.start), self.start_loc)

        for child in self.children[1:]:
            child.visit()

        self.code_generator.replace_jump("codelength(af1) + 2", 2)

        self.code_generator.add_code(
            strip_multiline_string(self.middle), self.middle_loc)

        self.code_generator.set_marker()

        for child in self.children[1:]:
            child.visit()

        self.code_generator.replace_jump_marker(
            self.end, "codelength(af2) + 1", 1)

        self.code_generator.add_code_close("", 0)

        self.code_generator.add_code("# If Else end\n", 0)


class MainFunctionNode(ASTNode):

    """Abstract Syntax Tree Node for main method"""

    start = """LOADI SP eds
        """

    start_loc = 1

    end = """# code(af)
        JUMP 0
        """

    end_loc = 2

    def visit(self, ):
        self.code_generator.add_code("# Main start\n", 0)

        # TODO: Don't forget to remove this improvised conditional breakpoint
        import globals
        if globals.test_name == "while_generation":
            if globals.test_name == "while_generation":
                pass

        self.code_generator.add_code(
            strip_multiline_string(self.start), self.start_loc)

        for child in self.children:
            child.visit()

        self.code_generator.add_code(
            strip_multiline_string(self.end), self.end_loc)

        self.code_generator.add_code("# Main end\n", 0)


class ArithmeticVariableConstantNode(ASTNode):

    """Abstract Syntax Tree Node for arithmetic variables and constants"""

    start = "SUBI SP 1\n"
    constant = "LOADI ACC encode(w)\n"
    constant_identifier = "LOADI ACC encode(c)\n"
    variable_identifier = "LOAD ACC var_identifier\n"
    end = "STOREIN SP ACC 1\n"

    all_loc = 1

    def visit(self, ):
        self.code_generator.add_code("# Variable / Constant start\n", 0)

        self.code_generator.add_code(
            strip_multiline_string(self.start), self.all_loc)

        if self.token.type == TT.IDENTIFIER:
            var_or_const = self.symbol_table.resolve(self.token.value)
            if isinstance(var_or_const, VariableSymbol):
                self.variable_identifier = self.code_generator.replace_code_directly(
                    self.variable_identifier, "var_identifier", str(var_or_const.value))
                self.code_generator.add_code(
                    strip_multiline_string(self.variable_identifier), self.all_loc)
            elif isinstance(var_or_const, ConstantSymbol):
                self.constant_identifier = self.code_generator.replace_code_directly(
                    self.constant_identifier, "encode(c)", str(var_or_const.value))
                self.code_generator.add_code(
                    strip_multiline_string(self.constant_identifier), self.all_loc)
        elif self.token.type == TT.NUMBER:
            self.constant = self.code_generator.replace_code_directly(
                self.constant, "encode(w)", str(self.token.value))
            self.code_generator.add_code(
                strip_multiline_string(self.constant), self.all_loc)

        self.code_generator.add_code(
            strip_multiline_string(self.end), self.all_loc)

        self.code_generator.add_code("# Variable / Constant end\n", 0)


class ArithmeticBinaryOperationNode(ASTNode):

    """Abstract Syntax Tree Node for for arithmetic binary operations"""

    end = """# codeaa(e1)
        # codeaa(e2)
        LOADIN SP ACC 2; # Wert von e 1 in ACC laden
        LOADIN SP IN2 1; # Wert von e 2 in IN2 laden
        OP ACC IN2; # e1 binop e2 in ACC laden
        STOREIN SP ACC 2; # Ergebnis in zweitoberste Stack-Zelle
        ADDI SP 1; # Stack um eine Zelle verkürzen
        """

    end_loc = 5

    def visit(self, ):
        if len(self.children) == 1:
            self.children[0].visit()
            return

        self.code_generator.add_code(
            "# Arithmetic Binary Operation start\n", 0)

        self.children[0].visit()
        self.children[1].visit()
        self.code_generator.add_code(
            strip_multiline_string(self.end), self.end_loc)

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

    end = "STOREIN SP ACC 1; # Ergebnis in oberste Stack-Zelle"

    end_loc = 1

    def visit(self, ):
        self.code_generator.add_code("# Arithmetic Unary Operation start\n", 0)

        self.children[0].visit()

        self.code_generator.add_code(
            strip_multiline_string(self.start), self.start_loc)

        if self.token.value == "~":
            self.code_generator.add_code(strip_multiline_string(self.bitwise_negation),
                                         self.bitwise_negation_loc)

        self.code_generator.add_code(
            strip_multiline_string(self.end), self.end_loc)

        self.code_generator.add_code("# Arithmetic Unary Operation end\n", 0)


class LogicAndOrNode(ASTNode):

    """Abstract Syntax Tree Node for logic 'and' and 'or'"""

    end = """# codela(l1)
        # codela(l2)
        LOADIN SP ACC 2;  # Wert von l1 in ACC laden
        LOADIN SP IN2 1;  # Wert von l2 in IN2 laden
        LOP ACC IN2;  # l1 lop l 2 in ACC laden
        STOREIN SP ACC 2;  # Ergebnis in zweitoberste Stack-Zelle
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        """

    end_loc = 5

    def visit(self, ):
        if len(self.children) == 1:
            self.children[0].visit()
            return

        self.code_generator.add_code("# Logic Binary Operation start\n", 0)

        self.children[0].visit()
        self.children[1].visit()

        self.code_generator.add_code(
            strip_multiline_string(self.end), self.end_loc)

        self.code_generator.add_code("# Logic Binary Operation end\n", 0)


class LogicNotNode(ASTNode):

    """Abstract Syntax Tree Node for logic not"""

    end = """# codela(l1)
        LOADI ACC 1;  # 1 in ACC laden
        LOADIN SP IN2 1;  # Wert von l1 in IN2 laden
        OPLUS ACC IN2;  # !(l1) in ACC laden
        STOREIN SP ACC 1;  # Ergebnis in oberste Stack-Zelle
        """

    end_loc = 4

    def visit(self, ):
        self.code_generator.add_code("# Logic Unary Operation start\n", 0)

        self.children[0].visit()

        self.code_generator.add_code(
            strip_multiline_string(self.end), self.end_loc)

        self.code_generator.add_code("# Logic Unary Operation end\n", 0)


class LogicAtomNode(ASTNode):

    """Abstract Syntax Tree Node for logic atom"""

    end = """# codeaa(e1)
        # codeaa(e2)
        LOADIN SP ACC 2;  # Wert von e1 in ACC laden
        LOADIN SP IN2 1;  # Wert von e2 in IN2 laden
        SUB ACC IN2;  # e1 - e2 in ACC laden
        JUMPvglop 3;  # Ergebnis 1, wenn e1 vglop e2 wahr
        LOADI ACC 0;  # Ergebnis 0, wenn e1 vglop e2 falsch
        JUMP 2;
        LOADI ACC 1;  # Ergebnis 1, wenn e1 vglop e2 wahr
        STOREIN SP ACC 2;  # Ergebnis in zweitoberste Stack-Zelle
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        """

    end_loc = 9

    def visit(self, ):
        self.code_generator.add_code("# Logic Atom start\n", 0)

        self.children[0].visit()
        self.children[1].visit()

        self.code_generator.add_code(
            strip_multiline_string(self.end), self.end_loc)

        self.code_generator.add_code("# Logic Atom end\n", 0)


class LogicTopBottomNode(ASTNode):

    """Abstract Syntax Tree Node for logic top bottom"""

    end = """# codeaa(e)
        LOADIN SP ACC 1;  # Wert von e in ACC laden
        JUMP = 3;  # Überspringe 2 Befehle, wenn e den Wert 0 hat
        LOADI ACC 1;
        STOREIN SP ACC 1;  # Ergebnis in oberste Stack-Zelle
        """

    end_loc = 4

    def visit(self, ):
        self.code_generator.add_code("# Logic Top Bottom start\n", 0)

        self.children[0].visit()

        self.code_generator.add_code(
            strip_multiline_string(self.end), self.end_loc)

        self.code_generator.add_code("# Logic Top Bottom end\n", 0)


class AssignmentNode(ASTNode):

    """Abstract Syntax Tree Node for assignement"""

    # TODO: genauer begutachten: "oder codela(e), falls logischer Ausdruck"

    end = """# codeaa(e) (oder codela(e), falls logischer Ausdruck)
        LOADIN SP ACC 1;  # Wert von e in ACC laden
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        """

    end_loc = 2

    store_more = "STORE ACC var_address;  # Wert von e in Adresse a speichern\n"

    store_more_loc = 1

    def _get_identifier_name(self, idx=0):
        # AllocationNode needs a special treatment, because it it's token only
        # tells the type but not the value
        if isinstance(self.children[idx], AllocationNode):
            return self.children[idx].children[1].token.value
        else:
            return self.children[idx].token.value

    def _is_constant_identifier(self, ):
        return isinstance(self.symbol_table.resolve(
            self._get_identifier_name(0)), ConstantSymbol)

    def _is_single_value_on_right_side(self, ):
        return len(self.children[1].children[0].children) == 1

    def _assign_number_to_constant_identifier(self):
        self.symbol_table.resolve(self._get_identifier_name(0)).value =\
            self.children[1].children[0].children[0].children[0].token.value

    # def _assign_constant_to_constant_identifier(self):
    #     self.symbol_table.resolve(
    #         self._get_identifier_name(0)).value = self.symbol_table.resolve(self._get_identifier_name(1)).value

    def _is_last_assignment(self, ):
        return not (isinstance(self.children[1], AllocationNode) or
                    isinstance(self.children[1], TokenNode))

    def visit(self, ):
        # if it's just a throw-away node that had to be taken
        if len(self.children) == 1:
            self.children[0].visit()
            return

        self.code_generator.add_code("# Assignment start\n", 0)

        self.children[0].visit()
        self.children[1].visit()

        # # look at the next node if it's a also a constant
        # if _is_constant_identifier(1):
        #     self.children[1].visit()
        #     _assign_to_constant_identifier()
        # in case of a ConstantSymbol and a assignment with a number on the
        # right side of the =, the value gets assigned immediately
        if self._is_constant_identifier() and self._is_single_value_on_right_side():
            self._assign_number_to_constant_identifier()

        # case of a VariableSymbol
        else:
            if self._is_last_assignment():
                self.code_generator.add_code(strip_multiline_string(self.end),
                                             self.end_loc)

            self._store_more = self.code_generator.replace_code_directly(
                self.store_more, "var_address",
                self.symbol_table.resolve(self._get_identifier_name(0)).value)

            # TODO: Überlegen, ob man den neuen Wert der Variable auch in der
            # SymbolTable speichern sollte oder ob der SRAM ausreicht

            self.code_generator.add_code(
                strip_multiline_string(self.store_more), self.store_more_loc)

        self.code_generator.add_code("# Assignment end\n", 0)


class AllocationNode(ASTNode):

    """Abstract Syntax Tree Node for allocation"""

    def visit(self, ):
        self.code_generator.add_code("# Allocation start\n", 0)

        if self.get_childvalue(0) == 'const':
            # the value of a ConstantNode is the name of the Constantnode if
            # there wasn't assigned a value directly to the constant which has
            # to be resolved internally in the RETI or by a RETI Code Interpreter
            const = ConstantSymbol(
                self.get_childvalue(1),
                self.symbol_table.resolve(self.token.value), self.get_childvalue(1))
            self.symbol_table.define(const)
        else:  # self.get_childvalue(0) == 'var'
            var = VariableSymbol(
                self.get_childvalue(1),
                self.symbol_table.resolve(self.token.value))
            self.symbol_table.define(var)
            self.symbol_table.allocate(var)

        self.code_generator.add_code(
            "# successfully allocated " + str(self.get_childvalue(0)) + "\n", 0)
        self.code_generator.add_code("# Allocation end\n", 0)

    def __repr__(self, ):
        acc = f"({self.get_childtoken(0)} {self.token} {self.get_childtoken(1)})"
        return acc


def strip_multiline_string(mutline_string):
    """helper function to make mutlineline string usable on different
    indent levels

    :grammar: grammar specification
    :returns: None
    """
    mutline_string = [i.lstrip() for i in mutline_string.split('\n')]
    mutline_string.pop()
    mutline_string_acc = ''
    for line in mutline_string:
        mutline_string_acc += line + '\n'
    return mutline_string_acc
