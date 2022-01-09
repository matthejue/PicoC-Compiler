from abstract_syntax_tree import ASTNode
from dataclasses import dataclass


class NT:
    """Nodetypes"""
    @dataclass
    class Add(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class Sub(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class Mul(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class Div(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class Mod(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class Oplus(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class Or(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class And(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class Minus(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class Not(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class Const(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class Char(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class Int(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class Void(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class Main(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class Else(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class Eq(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class UEq(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class Lt(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class Gt(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class Le(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class Ge(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class LAnd(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class LOr(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"

    @dataclass
    class LNot(ASTNode):
        value: str
        position: tuple[int, int]

        def __repr__(self):
            return f"{self.value}"
