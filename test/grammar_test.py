#!/usr/bin/env python

from pico_c_compiler.src.grammar import Grammar
from pico_c_compiler.src.lexer import Lexer
import unittest
import sys
sys.path.append('../')


class TestArithmeticExpressionGrammar(unittest.TestCase):

    def test_basic_arithmetic_expression(self):
        code = "var = 12 + 3;"
        # TODO: remove temporary solution to only read first line

        lexer = Lexer("<test>", code)

        grammar = Grammar(lexer)
        grammar.start_parse()

        self.assertEqual(str(grammar.reveal_ast()),
                         "('my_function' ('=' 'var' ('+' '12' '3')))")


if __name__ == '__main__':
    unittest.main()
