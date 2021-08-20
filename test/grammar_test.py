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
        self.tokens = False
        self.ast = True
        self.verbose = False


class UsefullTools():
    """Helper class for testing"""

    lexer = None
    grammar = None

    def set_everything_up_for_lexer(self, code):
        globals.args = Args()
        self.lexer = Lexer("<test>", code)
        tokens = []
        t = self.lexer.next_token()
        while t.type != TT.EOF:
            tokens += [t]
            t = self.lexer.next_token()
        return tokens

    def set_everything_up_for_ast(self, code):
        globals.args = Args()
        self.lexer = Lexer("<test>", code)

        self.grammar = Grammar(self.lexer)
        self.grammar.start_parse()


class TestLexer(unittest.TestCase, UsefullTools):

    def test_space_and_word_seperation(self, ):
        tokens = self.set_everything_up_for_lexer("  -12ab   --  (   var)")
        self.assertEqual(str(tokens), str(
            ['-', '12', 'ab', '-', '-', '(', 'var', ')']))

    def test_numbers(self, ):
        tokens = self.set_everything_up_for_lexer("12 0 10 9876543021")
        self.assertEqual(str(tokens), str(['12', '0', '10', '9876543021']))


class TestArithmeticExpressionGrammar(unittest.TestCase, UsefullTools):

    def test_basic_arithmetic_expression(self):
        self.set_everything_up_for_ast("var = 12 - 374;")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('fun' ('=' 'var' ('-' '12' '374')))")

    def test_precedence_1(self):
        self.set_everything_up_for_ast("var = 8 * cars + 2;")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('fun' ('=' 'var' ('+' ('*' '8' 'cars') '2')))")

    def test_precedence_2(self):
        self.set_everything_up_for_ast("var = 8 + 4 - 2;")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('fun' ('=' 'var' ('+' '8' ('-' '4' '2'))))")

    def test_precedence_3(self):
        self.set_everything_up_for_ast("var = cars * 4 / 2;")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('fun' ('=' 'var' ('*' 'cars' ('/' '4' '2'))))")

    def test_parenthesis(self):
        self.set_everything_up_for_ast("var = (4 + 7) * cars;")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('fun' ('=' 'var' ('*' ('+' '4' '7') 'cars')))")

    def test_negative_parenthesis_and_variable(self):
        self.set_everything_up_for_ast("var = -(-cars / 2);")
        expected_res = "('fun' ('=' 'var' ('-' ('/' ('-' 'cars') '2'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_unary_operators(self):
        self.set_everything_up_for_ast("var = -12 % (---154 - --189);")
        expected_res = "('fun' ('=' 'var' ('%' ('-' '12') ('-' ('-' "\
            "('-' ('-' '154'))) ('-' ('-' '189'))))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)


class TestLogicExpressionGrammar(unittest.TestCase, UsefullTools):

    def test_logic_expression(self):
        self.set_everything_up_for_ast("var = 12 > 3;")
        expected_res = "('fun' ('=' 'var' ('>' '12' '3')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_connected_logic_expression(self):
        self.set_everything_up_for_ast("var = 12 > 3 && dom <= 4;")
        expected_res = "('fun' ('=' 'var' ('&&' ('>' '12' '3') "\
            "('<=' 'dom' '4'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_logic_precedence_1(self, ):
        self.set_everything_up_for_ast("var = 12 >= dom && 34 < 4 || a == b;")
        expected_res = "('fun' ('=' 'var' ('||' ('&&' ('>=' '12' 'dom') "\
            "('<' '34' '4')) ('==' 'a' 'b'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_logic_precedence_2(self, ):
        self.set_everything_up_for_ast("var = 12 == dom || c >= 4 || a != b;")
        expected_res = "('fun' ('=' 'var' ('||' ('==' '12' 'dom') "\
            "('||' ('>=' 'c' '4') ('!=' 'a' 'b')))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_logic_and_arithmetic_parenthesis_mixed(self, ):
        self.set_everything_up_for_ast(
            "var = (12 <= (dom - 1) * 2 || 42 != cars) && cars == 0;")
        expected_res = "('fun' ('=' 'var' ('&&' ('||' ('<=' '12' ('*' "\
            "('-' 'dom' '1') '2')) ('!=' '42' 'cars')) ('==' 'cars' '0'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)


class TestIfElseGrammar(unittest.TestCase, UsefullTools):

    def test_if_else_grammar(self):
        self.set_everything_up_for_ast(
            "if (var >= 0) var = 12; else var = var + 1;")
        expected_res = "('fun' ('if' ('>=' 'var' '0') ('=' 'var' '12') "\
            "('else' ('=' 'var' ('+' 'var' '1')))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_if_else_braces(self):
        self.set_everything_up_for_ast(
            "if (var == 0) { var = 100; cars = cars + 1; } else "
            "{ var = var - 1; b = 1; }")
        expected_res = "('fun' ('if' ('==' 'var' '0') ('=' 'var' '100') "\
            "('=' 'cars' ('+' 'cars' '1')) ('else' "\
            "('=' 'var' ('-' 'var' '1')) ('=' 'b' '1'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_else_if(self, ):
        self.set_everything_up_for_ast(
            "if (var == 0) var = 100; else if (var == 10) { var = 5; } "
            "else var = var + 1;")
        expected_res = "('fun' ('if' ('==' 'var' '0') ('=' 'var' '100') "\
            "('else' ('if' ('==' 'var' '10') ('=' 'var' '5') ('else' "\
            "('=' 'var' ('+' 'var' '1')))))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_two_if_after_another(self, ):
        self.set_everything_up_for_ast(
            "if (var == 0) cars = 10; if (cars == 10) { var = 42; }")
        expected_res = "('fun' ('if' ('==' 'var' '0') ('=' 'cars' '10')) "\
            "('if' ('==' 'cars' '10') ('=' 'var' '42')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_mixed_if_else_after_another(self, ):
        self.set_everything_up_for_ast(
            "if (var == 0) cars = 10; else cars = cars + 1; if (cars == 10) "
            "{ var = 42; }")
        expected_res = "('fun' ('if' ('==' 'var' '0') ('=' 'cars' '10') "\
            "('else' ('=' 'cars' ('+' 'cars' '1')))) "\
            "('if' ('==' 'cars' '10') ('=' 'var' '42')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)


class TestLoopGrammar(unittest.TestCase, UsefullTools):

    def test_while_loop(self, ):
        self.set_everything_up_for_ast(
            "while ( x < 12 ) { x = x + 1; }")
        expected_res = "('fun' ('while' ('<' 'x' '12') "\
            "('=' 'x' ('+' 'x' '1'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_do_while_loop(self, ):
        self.set_everything_up_for_ast(
            "do { x = x + 1; } while ( y < 10 );")
        expected_res = "('fun' ('do while' ('=' 'x' ('+' 'x' '1')) "\
            "('<' 'y' '10')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_serveral_statements_loop(self, ):
        self.set_everything_up_for_ast(
            "do { y = x; x = x + 1; } while ( y < 10 );")
        expected_res = "('fun' ('do while' ('=' 'y' 'x') ('=' 'x' "\
            "('+' 'x' '1')) ('<' 'y' '10')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_loop_and_nested_if_else(self, ):
        self.set_everything_up_for_ast(
            "while (x < 12) { x = x + 1; if (x == 42) { y = y + 1; } }")
        expected_res = "('fun' ('while' ('<' 'x' '12') ('=' 'x' "\
            "('+' 'x' '1')) ('if' ('==' 'x' '12') ('=' 'y' ('+' 'y' '1')))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_nested_loops(self, ):
        self.set_everything_up_for_ast(
            "while (x <= 42) { while (y <= 42) { z = x * y; } }")
        expected_res = "('fun' ('while' ('<=' 'x' '42') ('while' "\
            "('<=' 'y' '42') ('=' 'z' ('*' 'x' 'y')))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_loop_statements_after_another(self, ):
        self.set_everything_up_for_ast(
            "while (x <= 100) { x = x + 1; } x = 1; do { x = x + 1; } "
            "while (x <= 100);")
        expected_res = "('fun' ('while' ('<=' 'x' '100') ('=' 'x' "\
            "('+' 'x' '1'))) ('=' 'x' ('+' 'x' '1')) ('do while' "\
            "('=' 'x' ('+' 'x' '1')) ('<=' 'x' '100')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)


if __name__ == '__main__':
    sys.path.append('/home/areo/Documents/Studium/pico_c_compiler/src')
    from lexer import Lexer, TT
    from grammar import Grammar
    import globals
    unittest.main()
