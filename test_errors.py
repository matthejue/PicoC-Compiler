#!/usr/bin/env python

import unittest
from lexer import *
from parser import *
from errors import *

class TestErrors(unittest.TestCase):

    def test_illegal_char_error()
        # several parenthesis
        code_ae = ["2 + "]

        # Generate tokens
        lexer = Lexer("<testin>", code_ae)
        tokens, error = lexer.create_tokens()

        # Generate ast
        parser = Parser(tokens)
        syntax_tree_rootnode, error = parser.parse()

        # Test for expected output
        expected_output = "(CONSTANT:12, ['BINOP', 'PRECEDENCE_1']:*, (CONSTANT:165, ['BINOP', 'PRECEDENCE_1']:/, (CONSTANT:241, ['BINOP', 'PRECEDENCE_1']:*, CONSTANT:2)))"
        self.assertEqual(str(syntax_tree_rootnode), expected_output)

        # 12 * (165 / (31 + 241 * 2) + 1     # Klammer zu wenig
        # 2 + ( / 12) * 14                   # Operand vergessen links
        # 2 + (165 /) * 14                   # Operand vergessen rechts
        # 2 + (165 12) * 14                  # Operator vergessen
        # 2 + (165 @ 12) * 14                # nicht existierendes Symbol
        # 123asd                             # Digits und Buchstaben gemischt

        # 12   * ( 165 /   (31 +241* 2)   )  # riesige Abstände und zu kleine Abstände bei Operatoren und Klammern


if __name__ == '__main__':
    unittest.main()
