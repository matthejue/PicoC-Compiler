#!/usr/bin/env python

import unittest
from src.lexer import Lexer
from src.grammar import Grammar
from src import globals


class TestArithmeticExpressionGrammar(unittest.TestCase):

    def test_basic_arithmetic_expression(self):
        class Args(object):
            def __init__(self):
                self.print = False
                self.tokens = False
                self.ast = True
                self.verbose = False
        globals.args = Args()
        code = "var = 12 + 3;"

        lexer = Lexer("<test>", code)

        grammar = Grammar(lexer)
        grammar.start_parse()

        self.assertEqual(str(grammar.reveal_ast()),
                         "('my_function' ('=' 'var' ('+' '12' '3')))")


if __name__ == '__main__':
    # sys.path.append('/home/areo/Documents/Studium/pico_c_compiler/src')
    # from lexer import Lexer
    # from grammar import Grammar
    unittest.main()
