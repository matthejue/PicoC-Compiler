#!/usr/bin/env python

from lark import Lark

with open("./src/parser_spec.lark") as fin:
    parser = Lark(fin.read(), start="picoc")
    print(
        parser.parse(
            r"""
test
int test(){
    print(_fun120 + 120 * -'c')
}
    """
        ).pretty()
    )
