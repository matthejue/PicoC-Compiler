#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Union

# --- Tiny tree model ---
@dataclass
class Text:
    value: str
    __match_args__ = ("value",)

@dataclass
class Element:
    name: str
    children: List[Union["Element", Text]]
    __match_args__ = ("name", "children")


# --- Example nodes ---
hello_world_p = Element("p", [Text("hello"), Text("world")])
hello_world_p_extra = Element("p", [Text("hello"), Text("world"), Text("!")])
hello_p = Element("p", [Text("hello")])
div_hello_world = Element("div", [Text("hello"), Text("world")])

# --- Matcher functions ---

def is_exact_hello_world_paragraph(node) -> bool:
    match node:
        # Sequence pattern [Text("hello"), Text("world")] means EXACTLY two children,
        # in this order, both Text nodes with those exact values.
        case Element("p", [Text("hello"), Text("world")]):
            return True
        case _:
            return False

def describe(node) -> str:
    match node:
        # You can also bind inner values:
        case Element("p", [Text(a), Text(b)]):
            return f"<p> with exactly two Text nodes: {a!r}, {b!r}"
        # This matches a <div> with any number of children (thanks to the star pattern)
        case Element("div", [*children]):
            return f"<div> with {len(children)} child(ren)"
        case _:
            return "something else"

# --- Demos ---
print(is_exact_hello_world_paragraph(hello_world_p))         # True
print(is_exact_hello_world_paragraph(hello_world_p_extra))   # False (extra child)
print(is_exact_hello_world_paragraph(hello_p))               # False (too few)
print(is_exact_hello_world_paragraph(div_hello_world))       # False (wrong element name)

print(describe(hello_world_p))        # <p> with exactly two Text nodes: 'hello', 'world'
print(describe(div_hello_world))      # <div> with 2 child(ren)
