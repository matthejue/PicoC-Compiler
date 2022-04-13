#!/usr/bin/python
# -*- coding: utf-8 -*-

from enum import Enum


class TT(Enum):
    """Tokentypes that are part of the parse_picoc. Their strings are used for
    differentiation and for error messages"""

    SEMICOLON = ";"
    PLUS_OP = "+"
    MINUS_OP = "-"
    MUL_OP = "*"
    DIV_OP = "/"
    MOD_OP = "%"
    AND_OP = "&"
    OR_OP = "|"
    OPLUS_OP = "^"
    NOT_OP = "~"
    BITSHIFT_L = "<<"
    BITSHIFT_R = ">>"
    EQ_COMP = "=="
    UEQ_COMP = "!="
    LT_COMP = "<"
    GT_COMP = ">"
    LE_COMP = "<="
    GE_COMP = ">="
    ASSIGNMENT = "="
    NOT = "!"
    AND = "&&"
    OR = "||"
    L_PAREN = "("
    R_PAREN = ")"
    L_BRACE = "{"
    R_BRACE = "}"
    CONST = "const"  # constant qualifier
    VAR = "var"  # var qualifier
    INT = "int"
    CHAR = "char"
    MAIN = "main"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    DO = "do"
    IDENTIFIER = "identifier"
    TO_BOOL = "to bool"
    EOF = "end of file"


SPECIAL_MAPPINGS = ("/", "&", "|", "=", "<", ">", "!")
NOT_TO_MAP = ("identifier", "to bool", "end of file")
STRING_TO_TT_SIMPLE = {
    value.value: value
    for value in (
        value
        for key, value in TT.__dict__.items()
        if not key.startswith("_")
        and value.value not in NOT_TO_MAP
        and value.value[0] not in SPECIAL_MAPPINGS
        and len(value.value) < 2
    )
}
list(STRING_TO_TT_SIMPLE.keys())[:10]
list(STRING_TO_TT_SIMPLE.keys())[10:20]
STRING_TO_TT_COMPLEX = {
    value.value: value
    for value in (
        value
        for key, value in TT.__dict__.items()
        if not key.startswith("_")
        and value.value not in NOT_TO_MAP
        and value.value[0] in SPECIAL_MAPPINGS
        and len(value.value) <= 2
    )
}
list(STRING_TO_TT_COMPLEX.keys())[:10]
list(STRING_TO_TT_COMPLEX.keys())[10:20]
STRING_TO_TT_WORDS = {
    value.value: value
    for value in (
        value
        for key, value in TT.__dict__.items()
        if not key.startswith("_")
        and value.value not in NOT_TO_MAP
        and value.value[0] not in SPECIAL_MAPPINGS
        and len(value.value) >= 2
    )
}
list(STRING_TO_TT_WORDS.keys())[:10]
