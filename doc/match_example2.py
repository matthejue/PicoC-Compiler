#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Union

# --- Node types ---
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
p_hello_world = Element("p", [Text("hello"), Text("world")])
p_hello_world_extras = Element("p", [Text("hello"), Text("world"), Text("!"), Text("more")])

# --- Matching demos ---
def exact_two_texts(node):
    match node:
        # Requires EXACTLY two children: Text("hello"), Text("world")
        case Element("p", [Text("hello"), Text("world")]):
            return "matched EXACT two texts"
        case _:
            return "no match (length mismatch or different content)"

def at_least_two_texts_then_any(node):
    match node:
        # Allows extra children; they go into 'rest'
        case Element("p", [Text("hello"), Text("world"), *rest]):
            return f"matched with extras, rest length = {len(rest)}"
        case _:
            return "no match"

print("Exact-two on exact-two:     ", exact_two_texts(p_hello_world))
print("Exact-two on extras:        ", exact_two_texts(p_hello_world_extras))   # <-- won't match
print("At-least-two on exact-two:  ", at_least_two_texts_then_any(p_hello_world))
print("At-least-two on extras:     ", at_least_two_texts_then_any(p_hello_world_extras))
