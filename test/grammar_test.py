#!/usr/bin/env python

import unittest
import sys
from testing_helpers import UsefullTools


class TestStatementGrammar(unittest.TestCase, UsefullTools):

    def test_semicolon_after_another(self, ):
        tokens = self.set_everything_up_for_ast("semicolon after another",
                                                "void main() { ; int x = 12"
                                                "; ; if (x < 10) { ; }; }")
        self.assertEqual(str(self.grammar.reveal_ast(
        )), "('main' ('=' ('var' 'int' 'x') '12') ('if' ('<' 'x' '10')))")


class TestAssignmentGrammar(unittest.TestCase, UsefullTools):

    def test_constant_initialisation(self, ):
        self.set_everything_up_for_ast("constant initialisation",
                                       "void main() { const int var = 12; }")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('main' ('=' ('const' 'int' 'var') '12'))")

    def test_allocation(self, ):
        self.set_everything_up_for_ast("allocation",
                                       "void main() { int x; }")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('main' ('var' 'int' 'x'))")


class TestArithmeticExpressionGrammar(unittest.TestCase, UsefullTools):

    def test_basic_arithmetic_expression(self):
        self.set_everything_up_for_ast("basic arithmetic expression",
                                       "void main() { var = 12 - 374; }")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('main' ('=' 'var' ('-' '12' '374')))")

    def test_precedence_1(self):
        self.set_everything_up_for_ast("precedence 1",
                                       "void main() { var = 8 * cars + 2; }")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('main' ('=' 'var' ('+' ('*' '8' 'cars') '2')))")

    def test_precedence_2(self):
        self.set_everything_up_for_ast("precedence 2",
                                       "void main() { var = 8 + 4 - 2; }")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('main' ('=' 'var' ('+' '8' ('-' '4' '2'))))")

    def test_precedence_3(self):
        self.set_everything_up_for_ast("precedence 3",
                                       "void main() { var = cars * 4 / 2; }")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('main' ('=' 'var' ('*' 'cars' ('/' '4' '2'))))")

    def test_parenthesis(self):
        self.set_everything_up_for_ast("parenthesis",
                                       "void main() { var = (4 + 7) * cars; }")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('main' ('=' 'var' ('*' ('+' '4' '7') 'cars')))")

    def test_negative_parenthesis_and_variable(self):
        self.set_everything_up_for_ast("negative parenthesis and variable",
                                       "void main() { var = -(-cars / 2); }")
        expected_res = "('main' ('=' 'var' ('-' ('/' ('-' 'cars') '2'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_unary_operators(self):
        self.set_everything_up_for_ast("unary operators",
                                       "void main() { var = -12 % (---154 - "
                                       "--189); }")
        expected_res = "('main' ('=' 'var' ('%' ('-' '12') ('-' ('-' "\
            "('-' ('-' '154'))) ('-' ('-' '189'))))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)


class TestLogicExpressionGrammar(unittest.TestCase, UsefullTools):

    def test_logic_expression(self):
        self.set_everything_up_for_ast("logic expression",
                                       "void main() { var = 12 > 3; }")
        expected_res = "('main' ('=' 'var' ('>' '12' '3')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_connected_logic_expression(self):
        self.set_everything_up_for_ast("connected logic expression",
                                       "void main() { var = 12 > 3 && dom <= "
                                       "4; }")
        expected_res = "('main' ('=' 'var' ('&&' ('>' '12' '3') "\
            "('<=' 'dom' '4'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_logic_precedence_1(self, ):
        self.set_everything_up_for_ast("logic precedence 1",
                                       "void main() { var = 12 >= dom && 34 <"
                                       " 4 || a == b; }")
        expected_res = "('main' ('=' 'var' ('||' ('&&' ('>=' '12' 'dom') "\
            "('<' '34' '4')) ('==' 'a' 'b'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_logic_precedence_2(self, ):
        self.set_everything_up_for_ast("logic precedence 2",
                                       "void main() { var = 12 == dom || c >="
                                       " 4 || a != b; }")
        expected_res = "('main' ('=' 'var' ('||' ('==' '12' 'dom') "\
            "('||' ('>=' 'c' '4') ('!=' 'a' 'b')))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_logic_and_arithmetic_parenthesis_mixed(self, ):
        self.set_everything_up_for_ast("logic and arithmetic parenthesis "
                                       "mixed",
                                       "void main() { var = (12 <= (dom - 1) "
                                       "* 2 || 42 != cars) && cars == 0; }")
        expected_res = "('main' ('=' 'var' ('&&' ('||' ('<=' '12' ('*' "\
            "('-' 'dom' '1') '2')) ('!=' '42' 'cars')) ('==' 'cars' '0'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)


class TestIfElseGrammar(unittest.TestCase, UsefullTools):

    def test_if_else_grammar(self):
        self.set_everything_up_for_ast("if else grammar",
                                       "void main() { if (var >= 0) var = 12; "
                                       "else var = var + 1; }")
        expected_res = "('main' ('if' ('>=' 'var' '0') ('=' 'var' '12') "\
            "'else' ('=' 'var' ('+' 'var' '1'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_if_else_braces(self):
        self.set_everything_up_for_ast("if else braces",
                                       "void main() { if (var == 0) { var = "
                                       "100; cars = cars + 1; } else "
                                       "{ var = var - 1; b = 1; } }")
        expected_res = "('main' ('if' ('==' 'var' '0') ('=' 'var' '100') "\
            "('=' 'cars' ('+' 'cars' '1')) 'else' "\
            "('=' 'var' ('-' 'var' '1')) ('=' 'b' '1')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_else_if(self, ):
        self.set_everything_up_for_ast("else if",
                                       "void main() { if (var == 0) var = 100;"
                                       " else if (var == 10) { var = 5; } "
                                       "else var = var + 1; }")
        expected_res = "('main' ('if' ('==' 'var' '0') ('=' 'var' '100') "\
            "'else' ('if' ('==' 'var' '10') ('=' 'var' '5') 'else' "\
            "('=' 'var' ('+' 'var' '1')))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_two_if_after_another(self, ):
        self.set_everything_up_for_ast("two if after another",
                                       "void main() { if (var == 0) cars = 10;"
                                       " if (cars == 10) { var = 42; } }")
        expected_res = "('main' ('if' ('==' 'var' '0') ('=' 'cars' '10')) "\
            "('if' ('==' 'cars' '10') ('=' 'var' '42')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_mixed_if_else_after_another(self, ):
        self.set_everything_up_for_ast("mixed if else after another",
                                       "void main() { if (var == 0) cars = 10;"
                                       " else cars = cars + 1; if (cars == "
                                       "10) { var = 42; } }")
        expected_res = "('main' ('if' ('==' 'var' '0') ('=' 'cars' '10') "\
            "'else' ('=' 'cars' ('+' 'cars' '1'))) "\
            "('if' ('==' 'cars' '10') ('=' 'var' '42')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_if_arithmetic_expression_as_logical_expression(self, ):
        self.set_everything_up_for_ast("if arithmetic expression as logical "
                                       "expression",
                                       "void main() { if (123 * var) { var = "
                                       "123; } }")
        expected_res = "('main' ('if' ('to bool' ('*' '123' 'var')) "\
            "('=' 'var' '123')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)


class TestLoopGrammar(unittest.TestCase, UsefullTools):

    def test_while_loop(self, ):
        self.set_everything_up_for_ast("while loop",
                                       "void main() { while ( x < 12 ) { x = "
                                       "x + 1; } }")
        expected_res = "('main' ('while' ('<' 'x' '12') "\
            "('=' 'x' ('+' 'x' '1'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_do_while_loop(self, ):
        self.set_everything_up_for_ast("do while loop",
                                       "void main() { do { x = x + 1; } "
                                       "while ( y < 10 ); }")
        expected_res = "('main' ('do while' ('=' 'x' ('+' 'x' '1')) "\
            "('<' 'y' '10')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_several_statements_loop(self, ):
        self.set_everything_up_for_ast("several statements loop",
                                       "void main() { do { y = x; x = x + 1; "
                                       "} while ( y < 10 ); }")
        expected_res = "('main' ('do while' ('=' 'y' 'x') ('=' 'x' "\
            "('+' 'x' '1')) ('<' 'y' '10')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_loop_and_nested_if_else(self, ):
        self.set_everything_up_for_ast("loop and nested if else",
                                       "void main() { while (x < 12) { x = x "
                                       "+ 1; if (x == 42) { y = y + 1; } } }")
        expected_res = "('main' ('while' ('<' 'x' '12') ('=' 'x' "\
            "('+' 'x' '1')) ('if' ('==' 'x' '42') ('=' 'y' ('+' 'y' '1')))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_nested_loops(self, ):
        self.set_everything_up_for_ast("nested loops",
                                       "void main() { while (x <= 42) { "
                                       "while (y <= 42) { z = x * y; } } }")
        expected_res = "('main' ('while' ('<=' 'x' '42') ('while' "\
            "('<=' 'y' '42') ('=' 'z' ('*' 'x' 'y')))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_loop_statements_after_another(self, ):
        self.set_everything_up_for_ast("loop statements after another",
                                       "void main() { while (x <= 100) { x = "
                                       "x + 1; } x = 10; do { x = x + 1; } "
                                       "while (x <= 100); }")
        expected_res = "('main' ('while' ('<=' 'x' '100') ('=' 'x' "\
            "('+' 'x' '1'))) ('=' 'x' '10') ('do while' "\
            "('=' 'x' ('+' 'x' '1')) ('<=' 'x' '100')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)


class TestCodeGenerator(unittest.TestCase, UsefullTools):

    code = """SUBI SP 1;
    LOAD ACC encode(w);
    STOREIN SP ACC 1;
    """

    def test_code_replacment_after(self, ):
        code_generator = CodeGenerator()
        symbol_table = SymbolTable()

        var = VariableSymbol('car', symbol_table.resolve('int'), (0, 0))
        symbol_table.define(var)
        symbol_table.allocate(var)

        expected_res = strip_multiline_string("""SUBI SP 1;
        LOAD ACC 100;
        STOREIN SP ACC 1;
        """)

        code_generator.add_code(strip_multiline_string(self.code), 3)

        code_generator.add_marker()

        code_generator.replace_code_after(
            'encode(w)', symbol_table.resolve('car').value)

        code_generator.remove_marker()

        self.assertEqual(code_generator.show_code(), expected_res)

    def test_while_generation(self, ):
        test_code = """void main() {
                       int i = 0;
                       int x = 1;
                       while (i < 10) {
                         if (i == 5) {
                           x = 2;
                         }
                         i = i + x;
                       }
                       const int y = i % 10;
                     }
                     """
        self.set_everything_up_for_multiline_program(
            "while generation", test_code)

    def test_constant_initialisation(self, ):
        test_code = """void main() {
                        const int var = 42;
                    }
                    """
        self.set_everything_up_for_multiline_program(
            "constant initialisation", test_code)

    # TODO: Einen Test mit IfElseNode machen
    # TODO: diese Datei in 2 Dateien splitten mit code_generator_test and
    # parser_test


if __name__ == '__main__':
    sys.path.append('/home/areo/Documents/Studium/pico_c_compiler/src')
    from code_generator import CodeGenerator
    from symbol_table import SymbolTable, VariableSymbol
    from abstract_syntax_tree import strip_multiline_string
    unittest.main()
