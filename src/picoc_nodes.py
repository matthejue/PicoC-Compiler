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

    class Not(ASTNode):
        pass

    class Const(ASTNode):
        pass

    class CharDT(ASTNode):
        pass

    class IntDT(ASTNode):
        pass

    class VoidDT(ASTNode):
        pass

    class Else(ASTNode):
        pass

    class Eq(ASTNode):
        pass

    class NEq(ASTNode):
        pass

    class Lt(ASTNode):
        pass

    class Gt(ASTNode):
        pass

    class Le(ASTNode):
        pass

    class Ge(ASTNode):
        pass

    class LogicAnd(ASTNode):
        pass

    class LogicOr(ASTNode):
        pass

    class Name(ASTNode):
        # shorter then 'Identifier'
        pass

    class Num(ASTNode):
        pass

    class Char(ASTNode):
        pass

    ###########################################################################
    #                     Nodetypes containing other Nodes                    #
    ###########################################################################

    class File(ASTNode):
        pass

    class LogicBinOp(ASTNode):
        pass

    class LogicNot(ASTNode):
        pass

    class LogicAtom(ASTNode):
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

    class Assign(ASTNode):
        pass

    class Alloc(ASTNode):
        pass

    class Fun(ASTNode):
        pass

    class ArithBinOp(ASTNode):
        pass

    class ArithUnaryOp(ASTNode):
        pass

    class Print(ASTNode):
        pass

    class Input(ASTNode):
        pass
