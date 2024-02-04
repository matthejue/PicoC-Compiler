from dataclasses import dataclass


@dataclass
class Pos:
    line: int
    column: int

    def __eq__(self, other):
        return self.line == other.line and self.column == other.column

    def __repr__(self, depth=0):
        return f"{' ' * depth}Pos({self.line}, {self.column})"


@dataclass
class Range:
    start_pos: Pos
    end_pos: Pos
