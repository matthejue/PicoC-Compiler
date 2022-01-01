#!/usr/bin/python
# -*- coding: utf-8 -*-
from abstract_syntax_tree import ASTNode
from lexer import Token
from dataclasses import dataclass


@dataclass
class ToBoolNode(ASTNode):
    token: Token


@dataclass
class VariableNode(ASTNode):
    token: Token
