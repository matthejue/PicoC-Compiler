from abstract_syntax_tree import ASTNode


class NT:
    """Nodetypes"""
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

    class Main(ASTNode):
        pass

    class Filename(ASTNode):
        pass
