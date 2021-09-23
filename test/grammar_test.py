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
        self.lexer = Lexer("<test>", [code])
        tokens = []
        t = self.lexer.next_token()
        while t.type != TT.EOF:
            tokens += [t]
            t = self.lexer.next_token()
        return tokens

    def set_everything_up_for_ast(self, code):
        globals.args = Args()
        self.lexer = Lexer("<test>", [code])

        self.grammar = Grammar(self.lexer)
        self.grammar.start_parse()

    def set_everything_up_for_ast_multiline(self, testname, code_without_cr):
        globals.args = Args()
        self.lexer = Lexer(testname, code_without_cr)

        self.grammar = Grammar(self.lexer)
        self.grammar.start_parse()

    def set_everything_up_for_testing_programs(self, programname, programpath):
        with open(programpath) as input:
            code_without_cr = list(
                map(lambda line: line.strip(), input.readlines()))
            self.set_everything_up_for_ast_multiline(
                programname, code_without_cr)


class TestLexer(unittest.TestCase, UsefullTools):

    def test_space_and_word_seperation(self, ):
        tokens = self.set_everything_up_for_lexer("  -12ab   --  (   var)")
        self.assertEqual(str(tokens), str(
            ['-', '12', 'ab', '-', '-', '(', 'var', ')']))

    def test_numbers(self, ):
        tokens = self.set_everything_up_for_lexer("12 0 10 9876543021")
        self.assertEqual(str(tokens), str(['12', '0', '10', '9876543021']))

    def test_comments(self, ):
        tokens = self.set_everything_up_for_lexer(
            "var = /* comment */ 10; // important comment")
        self.assertEqual(str(tokens), str(['var', '=', '10', ';']))


class TestArithmeticExpressionGrammar(unittest.TestCase, UsefullTools):

    def test_basic_arithmetic_expression(self):
        self.set_everything_up_for_ast("void main() { var = 12 - 374; }")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('main' ('=' 'var' ('-' '12' '374')))")

    def test_precedence_1(self):
        self.set_everything_up_for_ast("void main() { var = 8 * cars + 2; }")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('main' ('=' 'var' ('+' ('*' '8' 'cars') '2')))")

    def test_precedence_2(self):
        self.set_everything_up_for_ast("void main() { var = 8 + 4 - 2; }")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('main' ('=' 'var' ('+' '8' ('-' '4' '2'))))")

    def test_precedence_3(self):
        self.set_everything_up_for_ast("void main() { var = cars * 4 / 2; }")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('main' ('=' 'var' ('*' 'cars' ('/' '4' '2'))))")

    def test_parenthesis(self):
        self.set_everything_up_for_ast("void main() { var = (4 + 7) * cars; }")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('main' ('=' 'var' ('*' ('+' '4' '7') 'cars')))")

    def test_negative_parenthesis_and_variable(self):
        self.set_everything_up_for_ast("void main() { var = -(-cars / 2); }")
        expected_res = "('main' ('=' 'var' ('-' ('/' ('-' 'cars') '2'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_unary_operators(self):
        self.set_everything_up_for_ast(
            "void main() { var = -12 % (---154 - --189); }")
        expected_res = "('main' ('=' 'var' ('%' ('-' '12') ('-' ('-' "\
            "('-' ('-' '154'))) ('-' ('-' '189'))))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)


class TestLogicExpressionGrammar(unittest.TestCase, UsefullTools):

    def test_logic_expression(self):
        self.set_everything_up_for_ast("void main() { var = 12 > 3; }")
        expected_res = "('main' ('=' 'var' ('>' '12' '3')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_connected_logic_expression(self):
        self.set_everything_up_for_ast(
            "void main() { var = 12 > 3 && dom <= 4; }")
        expected_res = "('main' ('=' 'var' ('&&' ('>' '12' '3') "\
            "('<=' 'dom' '4'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_logic_precedence_1(self, ):
        self.set_everything_up_for_ast(
            "void main() { var = 12 >= dom && 34 < 4 || a == b; }")
        expected_res = "('main' ('=' 'var' ('||' ('&&' ('>=' '12' 'dom') "\
            "('<' '34' '4')) ('==' 'a' 'b'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_logic_precedence_2(self, ):
        self.set_everything_up_for_ast(
            "void main() { var = 12 == dom || c >= 4 || a != b; }")
        expected_res = "('main' ('=' 'var' ('||' ('==' '12' 'dom') "\
            "('||' ('>=' 'c' '4') ('!=' 'a' 'b')))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_logic_and_arithmetic_parenthesis_mixed(self, ):
        self.set_everything_up_for_ast(
            "void main() { var = (12 <= (dom - 1) * 2 || 42 != cars) && cars == 0; }")
        expected_res = "('main' ('=' 'var' ('&&' ('||' ('<=' '12' ('*' "\
            "('-' 'dom' '1') '2')) ('!=' '42' 'cars')) ('==' 'cars' '0'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)


class TestIfElseGrammar(unittest.TestCase, UsefullTools):

    def test_if_else_grammar(self):
        self.set_everything_up_for_ast(
            "void main() { if (var >= 0) var = 12; else var = var + 1; }")
        expected_res = "('main' ('if' ('>=' 'var' '0') ('=' 'var' '12') "\
            "'else' ('=' 'var' ('+' 'var' '1'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_if_else_braces(self):
        self.set_everything_up_for_ast(
            "void main() { if (var == 0) { var = 100; cars = cars + 1; } else "
            "{ var = var - 1; b = 1; } }")
        expected_res = "('main' ('if' ('==' 'var' '0') ('=' 'var' '100') "\
            "('=' 'cars' ('+' 'cars' '1')) 'else' "\
            "('=' 'var' ('-' 'var' '1')) ('=' 'b' '1')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_else_if(self, ):
        self.set_everything_up_for_ast(
            "void main() { if (var == 0) var = 100; else if (var == 10) { var = 5; } "
            "else var = var + 1; }")
        expected_res = "('main' ('if' ('==' 'var' '0') ('=' 'var' '100') "\
            "'else' ('if' ('==' 'var' '10') ('=' 'var' '5') 'else' "\
            "('=' 'var' ('+' 'var' '1')))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_two_if_after_another(self, ):
        self.set_everything_up_for_ast(
            "void main() { if (var == 0) cars = 10; if (cars == 10) { var = 42; } }")
        expected_res = "('main' ('if' ('==' 'var' '0') ('=' 'cars' '10')) "\
            "('if' ('==' 'cars' '10') ('=' 'var' '42')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_mixed_if_else_after_another(self, ):
        self.set_everything_up_for_ast(
            "void main() { if (var == 0) cars = 10; else cars = cars + 1; if (cars == 10) "
            "{ var = 42; } }")
        expected_res = "('main' ('if' ('==' 'var' '0') ('=' 'cars' '10') "\
            "'else' ('=' 'cars' ('+' 'cars' '1'))) "\
            "('if' ('==' 'cars' '10') ('=' 'var' '42')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)


class TestLoopGrammar(unittest.TestCase, UsefullTools):

    def test_while_loop(self, ):
        self.set_everything_up_for_ast(
            "void main() { while ( x < 12 ) { x = x + 1; } }")
        expected_res = "('main' ('while' ('<' 'x' '12') "\
            "('=' 'x' ('+' 'x' '1'))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_do_while_loop(self, ):
        self.set_everything_up_for_ast(
            "void main() { do { x = x + 1; } while ( y < 10 ); }")
        expected_res = "('main' ('do while' ('=' 'x' ('+' 'x' '1')) "\
            "('<' 'y' '10')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_several_statements_loop(self, ):
        self.set_everything_up_for_ast(
            "void main() { do { y = x; x = x + 1; } while ( y < 10 ); }")
        expected_res = "('main' ('do while' ('=' 'y' 'x') ('=' 'x' "\
            "('+' 'x' '1')) ('<' 'y' '10')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_loop_and_nested_if_else(self, ):
        self.set_everything_up_for_ast(
            "void main() { while (x < 12) { x = x + 1; if (x == 42) { y = y + 1; } } }")
        expected_res = "('main' ('while' ('<' 'x' '12') ('=' 'x' "\
            "('+' 'x' '1')) ('if' ('==' 'x' '42') ('=' 'y' ('+' 'y' '1')))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_nested_loops(self, ):
        self.set_everything_up_for_ast(
            "void main() { while (x <= 42) { while (y <= 42) { z = x * y; } } }")
        expected_res = "('main' ('while' ('<=' 'x' '42') ('while' "\
            "('<=' 'y' '42') ('=' 'z' ('*' 'x' 'y')))))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

    def test_loop_statements_after_another(self, ):
        self.set_everything_up_for_ast(
            "void main() { while (x <= 100) { x = x + 1; } x = 10; do { x = x + 1; } "
            "while (x <= 100); }")
        expected_res = "('main' ('while' ('<=' 'x' '100') ('=' 'x' "\
            "('+' 'x' '1'))) ('=' 'x' '10') ('do while' "\
            "('=' 'x' ('+' 'x' '1')) ('<=' 'x' '100')))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)


class TestComments(unittest.TestCase, UsefullTools):

    def test_single_line_comment(self, ):
        self.set_everything_up_for_ast_multiline(
            "commenttest", ["void main() {", "var = 10;", "// important comment", "var = 0;", "}"])
        expected_res = "('main' ('=' 'var' '10') ('=' 'var' '0'))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)

#     def test_single_line_comment_end_of_line(self, ):
#         self.set_everything_up_for_ast_multiline(
#             [['int var;']['var = 0; // important comment']['var = var + 1;']])
#         expected_res = "('fun' ('\t'))"
#         self.assertEqual(str(self.grammar.reveal_ast()), expected_res)
#
#     def test_multi_line_comments(self, ):
#         pass


class TestCodeGenerator(unittest.TestCase):

    code = """SUBI SP 1
    LOAD ACC encode(w)
    STOREIN SP ACC 1
    """

    def test_code_replacment(self, ):
        code_generator = CodeGenerator()
        symbol_table = SymbolTable()

        var = VariableSymbol('car', 'int')
        symbol_table.define(var)
        symbol_table.allocate(var)

        expected_res = self.strip_multiline_string("""SUBI SP 1
        LOAD ACC 100
        STOREIN SP ACC 1
        """)

        code_generator.add_code(self.strip_multiline_string(self.code), 3)

        code_generator.replace_code(
            'encode(w)', symbol_table.resolve('car').address)
        self.assertEqual(code_generator.show_code(), expected_res)

    def test_while_generation(self, ):
        test_code = """
        int main()
        {
          n = 0;
          while (n > 0) {
            n = n + 1;
          }
        }
        """
        lexer = Lexer("<while_generation>", test_code)
        grammar = Grammar(lexer)
        grammar.start_parse()
        # abstract_syntax_tree = grammar.reveal_ast()
        # abstract_syntax_tree.visit()

    def strip_multiline_string(self, mutline_string):
        """helper function to make mutlineline string usable on different
        indent levels

        :grammar: grammar specification
        :returns: None
        """
        mutline_string = [i.lstrip() for i in mutline_string.split('\n')]
        mutline_string.pop()
        mutline_string_acc = ""
        for line in mutline_string:
            mutline_string_acc += line
        return mutline_string_acc


class TestPrograms(unittest.TestCase, UsefullTools):

    def test_gcd(self, ):
        self.set_everything_up_for_testing_programs("gcd",
                                                    "./test/gcd.picoc")


if __name__ == '__main__':
    sys.path.append('/home/areo/Documents/Studium/pico_c_compiler/src')
    from lexer import Lexer, TT
    from grammar import Grammar
    import globals
    from code_generator import CodeGenerator
    from symbol_table import SymbolTable, VariableSymbol
    from abstract_syntax_tree import (ArithmeticBinaryOperationNode,
                                      ArithmeticVariableConstantNode,
                                      MainFunctionNode, WhileNode, IfNode,
                                      LogicAtomNode, AssignmentNode,
                                      AllocationNode)
    unittest.main()
