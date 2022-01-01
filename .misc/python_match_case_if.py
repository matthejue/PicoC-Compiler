#!/usr/bin/python
# -*- coding: utf-8 -*-

aasdf = [12, 24]
aasdg = [13, 24]

b = 12

match b:
    case _ if b in aasdg:
        print("nooooo")
    case _ if b in aasdf:
        print("yes")
    case _:
        print("no")
