#!/usr/bin/python
# -*- coding: utf-8 -*-

class Test:
    def test(self):
        from grap import Grap
        print("1")
        Grap.do_sth(Grap)

    def test_3(self):
        print("3")


if __name__ == "__main__":
    t = Test()
    t.test()
