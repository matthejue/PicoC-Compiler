# from enum import Enum
from lexer import Token, TT
from enum import Enum
from code_generator import CodeGenerator
from symbol_table import SymbolTable, VariableSymbol


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
        self.symbol_table = SymbolTable()

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

    condition_check = """
        # codela(l)
        LOADIN SP ACC 1; # Wert von l in ACC laden
        ADDI SP 1; # Stack um eine Zelle verkürzen
        JUMP= codelength(af) + 2; # af überspringen, wenn l unerfüllt
        # code(af)
        """

    condition_check_loc = 3

    end = """
        # zurück zur Auswertung von l
        JUMP -(codelength(af) + codelength(l) + 3);
        """

    end_loc = 1

    def visit(self, ):
        self.children[0].visit()

        self.code_generator.add_code_open(
            self.condition_check, self.condition_check_loc)

        for child in self.children[1:]:
            child.visit()

        self.code_generator.replace_jump("codelength(af) + 2", 2)

        self.code_generator.replace_jump_directly([self.end],
                                                  "(codelength(af) +"
                                                  " codelength(l) + 3)")
        # + 3 sind schon mit drin

        self.code_generator.add_code_close(self.end, self.end_loc)


class DoWhileNode(ASTNode):

    """Abstract Syntax Tree Node for do while Grammar"""

    # Problem mit code(af)
    condition_check = """
        # code(af)
        # codela(l)
        LOADIN SP ACC 1; # Wert von l in ACC laden
        ADDI SP 1; # Stack um eine Zelle verkürzen
        # zurück zur Ausführung von af
        JUMP<> -(codelength(af) + codelength(l) + 2);
        """

    condition_check_loc = 3

    def visit(self, ):
        # little hack to get a artificial ucp_stock entry
        self.code_generator.add_code_open("", 0)

        for child in self.children[1:]:
            child.visit()

        self.children[0].visit()

        self.code_generator.replace_jump_directly([self.condition_check],
                                                  "(codelength(af) + "
                                                  "codelength(l) + 2), 2")

        self.code_generator.add_code_close(self.condition_check,
                                           self.condition_check_loc)

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

    end = """
        # codela(l)
        LOADIN SP ACC 1; # Wert von l in ACC laden
        ADDI SP 1; # Stack um eine Zelle verkürzen
        JUMP= {codelength(af) + 1}; # af überspringen
        # code(af)
        """

    end_loc = 3

    def visit(self, ):
        pass


class IfElseNode(ASTNode):

    """Abstract Syntax Tree Node for Else"""

    # TODO

    end = """
        # codela(l)
        LOADIN SP ACC 1; # Wert von l in ACC laden
        ADDI SP 1; # Stack um eine Zelle verkürzen
        JUMP= {codelength(af1) + 2}; # af1 überspringen
        # code(af1)
        JUMP {codelength(af2) + 1};
        # code(af2)
        """

    end_loc = 4

    def visit(self, ):
        pass


class MainFunctionNode(ASTNode):

    """Abstract Syntax Tree Node for main method"""

    start = """
        LOADI SP eds
        """

    start_loc = 1

    end = """
        # code(af)
        JUMP 0
        """

    end_loc = 2

    def visit(self, ):
        self.code_generator.add_code(self.start, self.start_loc)

        for child in self.children:
            child.visit()

        self.code_generator.add_code(self.end, self.end_loc)


class ArithmeticVariableConstantNode(ASTNode):

    """Abstract Syntax Tree Node for arithmetic variables and constants"""

    start = "SUBI SP 1\n"
    variable_identifier = "LOAD ACC var_identifier\n"
    constant = "LOAD ACC encode(w)\n"
    constant_identifier = "LOAD ACC {encode(c)}\n"
    end = "STOREIN SP ACC 1"

    all_loc = 1

    def visit(self, ):
        self.code_generator.add_code(self.start, self.all_loc)

        if self.token.type == TT.IDENTIFIER:
            var_value = self.symbol_table.resolve(self.token.value)
            self.code_generator.replace_code_directly_(
                [self.variable_identifier], "var_identifier", var_value)
            self.code_generator.add_code(self.identifier, self.all_loc)
        elif self.token.type == TT.NUMBER:
            self.code_generator.replace_code_directly(
                [self.constant], "encode(w)", str(self.token.value))
            self.code_generator.add_code(self.constant, self.all_loc)
        # elif constant identifier

        self.code_generator.add_code(self.end, self.all_loc)


class ArithmeticBinaryOperationNode(ASTNode):

    """Abstract Syntax Tree Node for for arithmetic binary operations"""

    end = """
        # codeaa(e1)
        # codeaa(e2)
        LOADIN SP ACC 2; # Wert von e 1 in ACC laden
        LOADIN SP IN2 1; # Wert von e 2 in IN2 laden
        OP ACC IN2; # e1 binop e2 in ACC laden
        STOREIN SP ACC 2; # Ergebnis in zweitoberste Stack-Zelle
        ADDI SP 1; # Stack um eine Zelle verkürzen
        """

    end_loc = 5

    def visit(self, ):
        self.children[0].visit()
        self.children[1].visit()
        self.code_generator.add_code(self.end, self.end_loc)


class ArithmeticUnaryOperationNode(ASTNode):

    """Abstract Syntax Tree Node for for arithmetic unary operations"""

    start = """
        # codeaa(e1)
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
        self.children[0].visit()

        self.code_generator.add_code(self.start, self.start_loc)

        if self.token.value == "~":
            self.code_generator.add_code(self.bitwise_negation,
                                         self.bitwise_negation_loc)

        self.code_generator.add_code(self.end, self.end_loc)


class LogicAndOrNode(ASTNode):

    """Abstract Syntax Tree Node for logic 'and' and 'or'"""

    end = """
        # codela(l1)
        # codela(l2)
        LOADIN SP ACC 2;  # Wert von l1 in ACC laden
        LOADIN SP IN2 1;  # Wert von l2 in IN2 laden
        LOP ACC IN2;  # l1 lop l 2 in ACC laden
        STOREIN SP ACC 2;  # Ergebnis in zweitoberste Stack-Zelle
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        """

    end_loc = 5

    def visit(self, ):
        self.children[0].visit()
        self.children[1].visit()

        self.code_generator.add_code(self.end, self.end_loc)


class LogicNotNode(ASTNode):

    """Abstract Syntax Tree Node for logic not"""

    end = """
        # codela(l1)
        LOADI ACC 1;  # 1 in ACC laden
        LOADIN SP IN2 1;  # Wert von l1 in IN2 laden
        OPLUS ACC IN2;  # !(l1) in ACC laden
        STOREIN SP ACC 1;  # Ergebnis in oberste Stack-Zelle
        """

    end_loc = 4

    def visit(self, ):
        self.children[0].visit()

        self.code_generator.add_code(self.end, self.end_loc)


class LogicAtomNode(ASTNode):

    """Abstract Syntax Tree Node for logic atom"""

    end = """
        # codeaa(e1)
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
        self.children[0].visit()
        self.children[1].visit()

        self.code_generator.add_code(self.end, self.end_loc)


class LogicTopBottomNode(ASTNode):

    """Abstract Syntax Tree Node for logic top bottom"""

    end = """
        # codeaa(e)
        LOADIN SP ACC 1;  # Wert von e in ACC laden
        JUMP = 3;  # Überspringe 2 Befehle, wenn e den Wert 0 hat
        LOADI ACC 1;
        STOREIN SP ACC 1;  # Ergebnis in oberste Stack-Zelle
        """

    end_loc = 4

    def visit(self, ):
        self.children[0].visit()

        self.code_generator.add_code(self.end, self.end_loc)


class AssignmentNode(ASTNode):

    """Abstract Syntax Tree Node for assignement"""

    # TODO: genauer begutachten: "oder codela(e), falls logischer Ausdruck"

    end = """
        # codeaa(e) (oder codela(e), falls logischer Ausdruck)
        LOADIN SP ACC 1;  # Wert von e in ACC laden
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        STORE ACC var_identifier;  # Wert von e in Adresse a speichern
        """

    end_loc = 3

    def visit(self, ):
        self.children[1].visit()

        var_value = self.symbol_table.resolve(self.children[0].token.value)
        self.code_generator.replace_code_directly(self.end, "var_identifier",
                                                  var_value)

        self.code_generator.add_code(self.end, self.end_loc)


class AllocationNode(ASTNode):

    """Abstract Syntax Tree Node for allocation"""

    def visit(self, ):
        var = VariableSymbol(
            self.children[1].token.value, self.children[0].token.value)

        self.symbol_table.define(var)
