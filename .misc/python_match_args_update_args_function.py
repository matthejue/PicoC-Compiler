#!/usr/bin/python
# -*- coding: utf-8 -*-


class C:

    __match_args__ = ("dvalue",)

    def __init__(self, d):
        self.d = d

    def update_args(self, ):
        self.dvalue = self.d.value


class D:
    def __init__(self, typee, value):
        self.typee = typee
        self.value = value


c = C(D("g", 69))
c.update_args()

match c:
    case C(69):
        print("yes he's g")
    case _:
        print("no he's not g")
