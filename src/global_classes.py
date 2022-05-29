from dataclasses import dataclass


@dataclass
class Pos:
    line: int
    column: int

    def __eq__(self, other):
        return self.line == other.line and self.column == other.column


@dataclass
class Range:
    start_pos: Pos
    end_pos: Pos
