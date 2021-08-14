#!/usr/bin/env python

import unittest
import sys
# from src.lexer import Lexer
# from src.grammar import Grammar
# from src import globals


class Args(object):

    """For the purpose of testing constructed class which simulates the
    intended bahaviour of the args variable in globals.py"""

    def __init__(self):
        self.print = False
        self.tokens = False
        self.ast = True
        self.verbose = False


class UsefullTools():
    """Helper class for testing"""

    lexer = None
    grammar = None

    def set_everything_up(self, code):
        globals.args = Args()
        self.lexer = Lexer("<test>", code)

        self.grammar = Grammar(self.lexer)
        self.grammar.start_parse()


class TestArithmeticExpressionGrammar(unittest.TestCase, UsefullTools):

    def test_basic_arithmetic_expression(self):
        self.set_everything_up("var = 12 - 374;")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('fun' ('=' 'var' ('-' '12' '374')))")

    def test_precedence_1(self):
        self.set_everything_up("var = 8 * cars + 2;")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('fun' ('=' 'var' ('+' ('*' '8' 'cars') '2')))")

    def test_precedence_2(self):
        self.set_everything_up("var = 8 + 4 - 2;")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('fun' ('=' 'var' ('+' '8' ('-' '4' '2'))))")

    def test_precedence_3(self):
        self.set_everything_up("var = cars * 4 / 2;")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('fun' ('=' 'var' ('*' 'cars' ('/' '4' '2'))))")

    def test_parenthesis(self):
        self.set_everything_up("var = (4 + 7) * cars;")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('fun' ('=' 'var' ('*' ('+' '4' '7') 'cars')))")

    def test_negative_parenthesis_and_variable(self):
        self.set_everything_up("var = -(-cars / 2);")
        expected_res = "('fun' ('=' 'var' ('-' ('/' ('-' 'cars') '2'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_unary_operators(self):
        self.set_everything_up("var = -12 % (---154 - --189);")
        expected_res = "('fun' ('=' 'var' ('%' ('-' '12') ('-' ('-' "\
            "('-' ('-' '154'))) ('-' ('-' '189'))))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)


class TestLogicExpressionGrammar(unittest.TestCase, UsefullTools):

    def test_logic_expression(self):
        self.set_everything_up("var = 12 > 3;")
        expected_res = "('fun' ('=' 'var' ('>' '12' '3')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_connected_logic_expression(self):
        self.set_everything_up("var = 12 > 3 && dom <= 4;")
        expected_res = "('fun' ('=' 'var' ('&&' ('>' '12' '3') "\
            "('<=' 'dom' '4'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_logic_precedence_1(self, ):
        self.set_everything_up("var = 12 >= dom && 34 < 4 || a == b;")
        expected_res = "('fun' ('=' 'var' ('||' ('&&' ('>=' '12' 'dom') "\
            "('<' '34' '4')) ('==' 'a' 'b'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_logic_precedence_2(self, ):
        self.set_everything_up("var = 12 == dom || c >= 4 || a != b;")
        expected_res = "('fun' ('=' 'var' ('||' ('==' '12' 'dom') "\
            "('||' ('>=' 'c' '4') ('!=' 'a' 'b')))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_logic_parenthesis_and_arithmetic_parenthesis_mixed(self, ):
        # TODO: Bug fixen
        self.set_everything_up(
            "var = (12 <= (dom - 1) * 2 || 42 != cars) && cars == 0;")
        expected_res = "('fun' ('=' 'var' ('&&' ('||' ('<=' '12' ('*' "\
            "('-' 'dom' '1') '2') ('!=' '42' 'cars'))) ('==' 'cars' '0'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)


if __name__ == '__main__':
    sys.path.append('/home/areo/Documents/Studium/pico_c_compiler/src')
    from lexer import Lexer
    from grammar import Grammar
    import globals
    unittest.main()
