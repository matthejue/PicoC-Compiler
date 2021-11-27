#!/usr/bin/python3.10

class Test:

    __match_args__ = ("x", "y")

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


test = Test("asdf", 12, 3)

match test:
    case Test("asdf", 12):
        print("that's it")
    case _:
        print("that's not it")
