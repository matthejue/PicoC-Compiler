from abstract_syntax_tree import ASTNode
from arithmetic_nodes import ArithOperand
from dataclasses import dataclass


class NT:
    """Nodetypes"""
    @dataclass
    class Add(ASTNode):
        value: str
        position: tuple[int, int]

    @dataclass
    class Sub(ASTNode):
        value: str
        position: tuple[int, int]

    @dataclass
    class Mul(ASTNode):
        value: str
        position: tuple[int, int]

    @dataclass
    class Div(ASTNode):
        value: str
        position: tuple[int, int]

    @dataclass
    class Mod(ASTNode):
        value: str
        position: tuple[int, int]

    @dataclass
    class Oplus(ASTNode):
        value: str
        position: tuple[int, int]

    @dataclass
    class Or(ASTNode):
        value: str
        position: tuple[int, int]

    @dataclass
    class And(ASTNode):
        value: str
        position: tuple[int, int]

    @dataclass
    class Minus(ASTNode):
        value: str
        position: tuple[int, int]

    @dataclass
    class Not(ASTNode):
        value: str
        position: tuple[int, int]

    @dataclass
    class Identifier(ArithOperand):
        value: str
        position: tuple[int, int]

    @dataclass
    class Number(ArithOperand):
        value: str
        position: tuple[int, int]

    @dataclass
    class Character(ArithOperand):
        value: str
        position: tuple[int, int]

    @dataclass
    class Const(ASTNode):
        value: str
        position: tuple[int, int]

    @dataclass
    class Char(ASTNode):
        value: str
        position: tuple[int, int]

    @dataclass
    class Int(ASTNode):
        value: str
        position: tuple[int, int]

    @dataclass
    class Void(ASTNode):
        value: str
        position: tuple[int, int]
