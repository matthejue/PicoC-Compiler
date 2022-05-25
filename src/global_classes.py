from dataclasses import dataclass


@dataclass
class Pos:
    line: int
    column: int

    def __eq__(self, other):
        return self.line == other.line and self.column == other.column


class SingleLineComment:
    def __init__(self, val, prefix):
        self.val = val
        self.prefix = prefix

    def __repr__(self, depth=0):
        return f"\n{' ' * depth}{self.prefix} {self.val}"

    __match__ = ("val", "prefix")
