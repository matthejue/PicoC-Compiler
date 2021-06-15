#!/usr/bin/env python

import unittest
from lexer import Lexer
from parser import Parser


class TestArithmeticExpreessions(unittest.TestCase):

    def test_unop(self):
        # severnal unary operators
        code_ae = ["2 * ---12"]

        # Generate tokens
        lexer = Lexer("<testin>", code_ae)
        tokens, error = lexer.create_tokens()

        # Generate ast
        parser = Parser(tokens)
        syntax_tree_rootnode, error = parser.parse()

        # Test for expected output
        expected_output = "(CONSTANT:2, ['BINOP', 'PRECEDENCE_1']:*, (UNOP:-, (UNOP:-, (UNOP:-, CONSTANT:12))))"
        self.assertEqual(str(syntax_tree_rootnode), expected_output)

    def test_parenthesis(self):
        # several parenthesis
        code_ae = ["12 * (165 / (241 * 2))"]

        # Generate tokens
        lexer = Lexer("<testin>", code_ae)
        tokens, error = lexer.create_tokens()

        # Generate ast
        parser = Parser(tokens)
        syntax_tree_rootnode, error = parser.parse()

        # Test for expected output
        expected_output = "(CONSTANT:12, ['BINOP', 'PRECEDENCE_1']:*, (CONSTANT:165, ['BINOP', 'PRECEDENCE_1']:/, (CONSTANT:241, ['BINOP', 'PRECEDENCE_1']:*, CONSTANT:2)))"
        self.assertEqual(str(syntax_tree_rootnode), expected_output)

        # parenthesis and precedence rules

    def test_precedence_rules(self):
        # basic precedence rules
        code_ae = ["21 * 561 + 4"]

        # Generate tokens
        lexer = Lexer("<testin>", code_ae)
        tokens, error = lexer.create_tokens()

        # Generate ast
        parser = Parser(tokens)
        syntax_tree_rootnode, error = parser.parse()

        # Test for expected output
        expected_output = "((CONSTANT:21, ['BINOP', 'PRECEDENCE_1']:*, CONSTANT:561), ['BINOP', 'PRECEDENCE_2']:+, CONSTANT:4)"
        self.assertEqual(str(syntax_tree_rootnode), expected_output)

        # precedence rules and parenthesis
        code_ae = ["2 * (165 / 12) + 15"]

        # Generate tokens
        lexer = Lexer("<testin>", code_ae)
        tokens, error = lexer.create_tokens()

        # Generate ast
        parser = Parser(tokens)
        syntax_tree_rootnode, error = parser.parse()

        # Test for expected output
        expected_output = "((CONSTANT:2, ['BINOP', 'PRECEDENCE_1']:*, (CONSTANT:165, ['BINOP', 'PRECEDENCE_1']:/, CONSTANT:12)), ['BINOP', 'PRECEDENCE_2']:+, CONSTANT:15)"
        self.assertEqual(str(syntax_tree_rootnode), expected_output)

    def test_varying_spacing(self):
        # varying spacing with parenthesis and operators
        code_ae = ["11   * ( 165/   (31 +241)   )"]

        # Generate tokens
        lexer = Lexer("<testin>", code_ae)
        tokens, error = lexer.create_tokens()

        # Generate ast
        parser = Parser(tokens)
        syntax_tree_rootnode, error = parser.parse()

        # Test for expected output
        expected_output = "(CONSTANT:11, ['BINOP', 'PRECEDENCE_1']:*, (CONSTANT:165, ['BINOP', 'PRECEDENCE_1']:/, (CONSTANT:31, ['BINOP', 'PRECEDENCE_2']:+, CONSTANT:241)))"
        self.assertEqual(str(syntax_tree_rootnode), expected_output)


if __name__ == '__main__':
    unittest.main()
