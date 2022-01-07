#!/usr/bin/python
# -*- coding: utf-8 -*-

class Test:

    __match_args__ = ("a", "b", "c")

    def __init__(self, b, c):
        self.b = b
        self.c = c


t = Test(1, 2)

a = False
match t:
    case Test(_, 1, 2):
        a = True
    case _:
        a = False

a
