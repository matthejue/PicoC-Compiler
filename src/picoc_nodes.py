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

    class CharType(ASTNode):
        pass

    class IntType(ASTNode):
        pass

    class VoidType(ASTNode):
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

    class LtE(ASTNode):
        pass

    class GtE(ASTNode):
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

    class ArithBinOp(ASTNode):
        pass

    class ArithUnaryOp(ASTNode):
        pass

    class LogicBinOp(ASTNode):
        pass

    class LogicNot(ASTNode):
        pass

    class LogicAtom(ASTNode):
        pass

    class ToBool(ASTNode):
        pass

    class Assign(ASTNode):
        pass

    class Alloc(ASTNode):
        pass

    class If(ASTNode):
        pass

    class IfElse(ASTNode):
        pass

    class While(ASTNode):
        pass

    class DoWhile(ASTNode):
        pass

    class FunDef(ASTNode):
        pass

    class Param(ASTNode):
        pass

    class Return(ASTNode):
        pass

    class Exp(ASTNode):
        pass

    class Call(ASTNode):
        pass

    class FunType(ASTNode):
        pass

    class File(ASTNode):
        pass
