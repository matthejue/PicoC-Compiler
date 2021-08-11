#!/usr/bin/env python

import unittest
import sys
import os


class TestArithmeticExpressionGrammar(unittest.TestCase):

    def test_basic_arithmetic_expression(self):
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
    from src.lexer import Lexer
    from src.grammar import Grammar
    unittest.main()
