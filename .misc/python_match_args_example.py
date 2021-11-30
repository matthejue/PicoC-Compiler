#!/usr/bin/python3.10
#  from pudb import set_trace


class Test:

    __match_args__ = ("x", "y")

    def __init__(self, *args):
        self.x = args[0]
        self.y = args[1]
        self.z = args[2]


#  set_trace()
test = Test(13, 12, 4)

match test:
    case Test(13, 12):
        print("that's it")
    case _:
        print("that's not it")
