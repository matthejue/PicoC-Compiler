#!/usr/bin/env python3

from dataclasses import dataclass
from typing import List, Union

@dataclass
class Text:
    value: str
    __match_args__ = ("value",)

@dataclass
class Element:
    name: str
    children: List[Union["Element", Text]]
    __match_args__ = ("name", "children")


p_two      = Element("p", [Text("a"), Text("b")])
p_many     = Element("p", [Text("a"), Text("b"), Text("c"), Text("d")])
p_one      = Element("p", [Text("a")])
div_many   = Element("div", [Text("a"), Text("b"), Text("c")])

def demo(node):
    match node:
        # EXACT length = 2 (the two underscores each stand for "one item")
        case Element("p", [_, _]):
            return "p with exactly two children (ignored values)"

        # ANY length >= 2 — extras are allowed and discarded by *_
        case Element("p", [_, _, *_]):
            return "p with at least two children (extras ignored)"

        # Catch-all for any <div> with any number of children
        case Element("div", [*_]):
            return "div of any length"

        case _:
            return "no match"

print(demo(p_two))   # p with exactly two children (ignored values)
print(demo(p_many))  # p with at least two children (extras ignored)
print(demo(p_one))   # no match (needs ≥ 2)
print(demo(div_many))# div of any length
