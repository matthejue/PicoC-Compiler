from ast_node import ASTNode


class NT:
    """Nodetypes"""

    ###########################################################################
    #                        Nodetypes replacing Tokens                       #
    ###########################################################################

    class Add(ASTNode):
        pass

    class Sub(ASTNode):
        pass

    class Mul(ASTNode):
        pass

    class Div(ASTNode):
        pass

    class Mod(ASTNode):
        pass

    class Oplus(ASTNode):
        pass

    class Or(ASTNode):
        pass

    class And(ASTNode):
        pass

    class Minus(ASTNode):
        pass

    class Negation(ASTNode):
        pass

    class Const(ASTNode):
        pass

    class Char(ASTNode):
        pass

    class Int(ASTNode):
        pass

    class Void(ASTNode):
        pass

    class Else(ASTNode):
        pass

    class Eq(ASTNode):
        pass

    class UEq(ASTNode):
        pass

    class Lt(ASTNode):
        pass

    class Gt(ASTNode):
        pass

    class Le(ASTNode):
        pass

    class Ge(ASTNode):
        pass

    class LAnd(ASTNode):
        pass

    class LOr(ASTNode):
        pass

    #  class LNot(ASTNode):
    #  pass

    #  class Main(ASTNode):
    #      pass

    class FunctionIdentifier(ASTNode):
        pass

    class Filename(ASTNode):
        pass

    ###########################################################################
    #                     Nodetypes containing other Nodes                    #
    ###########################################################################

    class File(ASTNode):
        pass

    class LogicBinaryOperation(ASTNode):
        pass

    class Not(ASTNode):
        pass

    class Atom(ASTNode):
        pass

    class ToBool(ASTNode):
        pass

    class If(ASTNode):
        pass

    class IfElse(ASTNode):
        pass

    class While(ASTNode):
        pass

    class DoWhile(ASTNode):
        pass

    class Assignment(ASTNode):
        pass

    class Allocation(ASTNode):
        pass

    class MainFunction(ASTNode):
        pass

    class Function(ASTNode):
        pass

    class ArithmeticOperand(ASTNode):
        pass

    class ArithmeticBinaryOperation(ASTNode):
        pass

    class ArithmeticUnaryOperation(ASTNode):
        pass
