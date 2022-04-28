#!/usr/bin/env python

from lark import Lark

with open("./src/parser_spec.lark") as fin:
    parser = Lark(fin.read(), start="file")
    print(
        parser.parse(
            r"""
test
int test(char c, int var){
    print(_fun120 /*-3*/ + 120 * -'c');
    int[] var = {12, 3, 4}; // das ist blöd
    // das ist noch blöder
    var[3] = 10;
}
    """
        ).pretty()
    )
