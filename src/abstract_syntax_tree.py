# from enum import Enum
from lexer import Token, TT
from enum import Enum
from code_generator import CodeGenerator
from symbol_table import SymbolTable


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

    def _visit(self, ):
        self.children[0].visit()

        self.code_generator.add_code_open(
            self.condition_check, self.condition_check_loc)

        for child in self.children[1:]:
            child.visit()

        self.code_generator.replace_jump("codelength(af) + 2", 2)

        self.code_generator.replace_jump_backwards([self.end],
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

    def _visit(self, ):
        # little hack to get a artificial ucp_stock entry
        self.code_generator.add_code_open("", 0)

        for child in self.children[1:]:
            child.visit()

        self.children[0]._visit()

        self.code_generator.replace_jump_backwards([self.condition_check],
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

    reti_code_condition_check = """
        # codela(l)
        LOADIN SP ACC 1; # Wert von l in ACC laden
        ADDI SP 1; # Stack um eine Zelle verkürzen
        JUMP= {codelength(af) + 1}; # af überspringen
        # code(af)
        """
    lines_of_code = 3


class IfElseNode(ASTNode):

    """Abstract Syntax Tree Node for Else"""

    reti_code_condition_check = """
        # codela(l)
        LOADIN SP ACC 1; # Wert von l in ACC laden
        ADDI SP 1; # Stack um eine Zelle verkürzen
        JUMP= {codelength(af1) + 2}; # af1 überspringen
        # code(af1)
        JUMP {codelength(af2) + 1};
        # code(af2)
        """
    lines_of_code = 4


class MainFunctionNode(ASTNode):

    """Abstract Syntax Tree Node for main method"""

    reti_code_end = """
        LOADI SP eds
        # code(af)
        JUMP 0
        """
    lines_of_code = 2


class ArithmeticVariableConstantNode(ASTNode):

    """Abstract Syntax Tree Node for arithmetic variables and constants"""

    reti_code_first_half = "SUBI SP 1\n"

    class reti_code(Enum):

        """reti code variable and constant"""

        variable = "LOAD ACC {a}\n"
        constant = "LOAD ACC {encode(w)}\n"
        constant_identifier = "LOAD ACC {encode(c)}\n"
    reti_code_second_half = "STOREIN SP ACC 1"

    lines_of_code = 13


class ArithmeticBinaryOperationNode(ASTNode):

    """Abstract Syntax Tree Node for for arithmetic binary operations"""

    reti_code = """
        # codeaa(e1)
        # codeaa(e2)
        LOADIN SP ACC 2; # Wert von e 1 in ACC laden
        LOADIN SP IN2 1; # Wert von e 2 in IN2 laden
        OP ACC IN2; # e1 binop e2 in ACC laden
        STOREIN SP ACC 2; # Ergebnis in zweitoberste Stack-Zelle
        ADDI SP 1; # Stack um eine Zelle verkürzen
        """


class ArithmeticUnaryOperationNode(ASTNode):

    """Abstract Syntax Tree Node for for arithmetic unary operations"""

    reti_code_first_half = """
        # codeaa(e1)
        LOADI ACC 0; # 0 in ACC laden
        LOADIN SP IN2 1; # Wert von e1 in IN2 laden
        SUB ACC IN2; # (0 - e1) in ACC laden
        """

    reti_code_bitwise_negation = "SUBI ACC 1; # transform negation to"\
        "complement\n"

    reti_code_second_half = "STOREIN SP ACC 1; # Ergebnis in oberste"\
        "Stack-Zelle"


class LogicAndOrNode(ASTNode):

    """Abstract Syntax Tree Node for logic 'and' and 'or'"""

    reti_code = """
        # start codela(l1)
        # codeaa(e)
        LOADIN SP ACC 1;  # Wert von e in ACC laden
        JUMP = 3;  # Überspringe 2 Befehle, wenn e den Wert 0 hat
        LOADI ACC 1;
        STOREIN SP ACC 1;  # Ergebnis in oberste Stack-Zelle
        # start codela(l2)
        # codeaa(e)
        LOADIN SP ACC 1;  # Wert von e in ACC laden
        JUMP = 3;  # Überspringe 2 Befehle, wenn e den Wert 0 hat
        LOADI ACC 1;
        STOREIN SP ACC 1;  # Ergebnis in oberste Stack-Zelle
        # finished loading
        LOADIN SP ACC 2;  # Wert von l1 in ACC laden
        LOADIN SP IN2 1;  # Wert von l2 in IN2 laden
        LOP ACC IN2;  # l1 lop l 2 in ACC laden
        STOREIN SP ACC 2;  # Ergebnis in zweitoberste Stack-Zelle
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        """
    lines_of_code = 13


class LogicNotNode(ASTNode):

    """Abstract Syntax Tree Node for logic not"""

    reti_code = """
        # start codela(l1)
        # codeaa(e)
        LOADIN SP ACC 1;  # Wert von e in ACC laden
        JUMP = 3;  # Überspringe 2 Befehle, wenn e den Wert 0 hat
        LOADI ACC 1;
        STOREIN SP ACC 1;  # Ergebnis in oberste Stack-Zelle
        # finished loading
        LOADI ACC 1;  # 1 in ACC laden
        LOADIN SP IN2 1;  # Wert von l1 in IN2 laden
        OPLUS ACC IN2;  # !(l1) in ACC laden
        STOREIN SP ACC 1;  # Ergebnis in oberste Stack-Zelle
        """
    lines_of_code = 8


class LogicAtomNode(ASTNode):

    """Abstract Syntax Tree Node for logic atom"""

    reti_code = """
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
    lines_of_code = 9


class LogicTopBottomNode(ASTNode):

    """Abstract Syntax Tree Node for logic top bottom"""

    reti_code = """
        # codeaa(e)
        LOADIN SP ACC 1;  # Wert von e in ACC laden
        JUMP = 3;  # Überspringe 2 Befehle, wenn e den Wert 0 hat
        LOADI ACC 1;
        STOREIN SP ACC 1;  # Ergebnis in oberste Stack-Zelle
        """
    lines_of_code = 4


class AssignmentNode(ASTNode):

    """Abstract Syntax Tree Node for assignement"""

    reti_code = """
        # codeaa(e) (oder codela(e), falls logischer Ausdruck)
        LOADIN SP ACC 1;  # Wert von e in ACC laden
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        STORE ACC a;  # Wert von e in Adresse a speichern
        """
    lines_of_code = 3

    def _visit(self, ):
        pass


class AllocationNode(ASTNode):

    """Abstract Syntax Tree Node for allocation"""

    reti_code = None
    lines_of_code = 0
