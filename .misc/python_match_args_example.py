#!/usr/bin/python3.10

class Apple:

    __match_args__ = ("x",)

    def __init__(self, *args):
        self.x = args[0]


class Test:

    __match_args__ = ("x", "y")

    def __init__(self, *args):
        self.x = args[0]
        self.y = args[1]
        self.z = args[2]


#  set_trace()
test = Test(Apple(3), 12, 4)

match test:
    case Test(Apple(3), 12):
        print("that's it")
    case _:
        print("that's not it")
