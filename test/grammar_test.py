#!/usr/bin/env python

import unittest
import sys


class Args(object):

    """For the purpose of testing constructed class which simulates the
    intended bahaviour of the args variable in globals.py"""

    def __init__(self):
        self.tokens = False
        self.ast = True
        self.verbose = False
        self.start_data_segment = 100
        self.end_data_segment = 200
        self.python_stracktrace_error_message = True


class UsefullTools():
    """Helper class for testing"""

    lexer = None
    grammar = None

    def set_everything_up_for_lexer(self, test_name, code):
        globals.test_name = test_name
        globals.args = Args()
        self.lexer = Lexer(test_name, [code])
        tokens = []
        t = self.lexer.next_token()
        while t.type != TT.EOF:
            tokens += [t]
            t = self.lexer.next_token()
        return tokens

    def set_everything_up_for_ast(self, test_name, code):
        globals.test_name = test_name
        globals.args = Args()
        self.lexer = Lexer(test_name, [code])

        self.grammar = Grammar(self.lexer)
        self.grammar.start_parse()

    def set_everything_up_for_ast_multiline(self, test_name, code_without_cr):
        globals.test_name = test_name
        globals.args = Args()
        self.lexer = Lexer(test_name, code_without_cr)

        self.grammar = Grammar(self.lexer)
        self.grammar.start_parse()

    def set_everything_up_for_visit_multiline(self, test_name, code_without_cr):
        globals.test_name = test_name
        # create new Singleton SymbolTable and CodeGenerator and remove old
        SymbolTable().__init__()
        CodeGenerator().__init__()

        globals.args = Args()
        self.lexer = Lexer(test_name, code_without_cr)

        self.grammar = Grammar(self.lexer)
        error_handler = ErrorHandler(self.grammar)
        error_handler.handle(self.grammar.start_parse)

        abstract_syntax_tree = self.grammar.reveal_ast()
        error_handler.handle(abstract_syntax_tree.visit)

        with open("./output.reti", 'w', encoding="utf-8") as fout:
            fout.writelines(abstract_syntax_tree.show_generated_code())

    def set_everything_up_for_multiline_program(self, test_name, input_string):
        multiline_string = [i.lstrip() for i in input_string.split('\n')]
        multiline_string.pop()
        self.set_everything_up_for_visit_multiline(
            test_name, multiline_string)

    def set_everything_up_for_testing_program_file(self, test_name, programpath):
        with open(programpath) as input:
            code_without_cr = list(
                map(lambda line: line.strip(), input.readlines()))
            self.set_everything_up_for_ast_multiline(
                test_name, code_without_cr)


class TestLexer(unittest.TestCase, UsefullTools):

    def test_space_and_word_seperation(self, ):
        tokens = self.set_everything_up_for_lexer("space and word seperation",
                                                  "  -12ab   --  (   var)")
        self.assertEqual(str(tokens), str(
            ['-', '12', 'ab', '-', '-', '(', 'var', ')']))

    def test_numbers(self, ):
        tokens = self.set_everything_up_for_lexer("numbers",
                                                  "12 0 10 9876543021")
        self.assertEqual(str(tokens), str(['12', '0', '10', '9876543021']))

    def test_comments(self, ):
        tokens = self.set_everything_up_for_lexer("comments",
                                                  "var = /* comment */ 10; //"
                                                  " important comment")
        self.assertEqual(str(tokens), str(['var', '=', '10', ';']))


class TestAssignmentGrammar(unittest.TestCase, UsefullTools):

    def test_constant_initialisation(self, ):
        self.set_everything_up_for_ast("constant initialisation",
                                       "void main() { const int var = 12; }")
        self.assertEqual(str(self.grammar.reveal_ast()),
                         "('main' ('=' ('const' 'int' 'var') '12'))")

    # def test_allocation(self, ):
    #     self.set_everything_up_for_ast("allocation",
    #                                    "void main() { int var; }")
    #     self.assertEqual(str(self.grammar.reveal_ast()),
    #                      "('main' ('=' ('const' 'int' 'var') '12'))")


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
        globals.test_name = "to bool"
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


class TestComments(unittest.TestCase, UsefullTools):

    def test_single_line_comment(self, ):
        self.set_everything_up_for_ast_multiline(
            "commenttest", ["void main() {", "var = 10;",
                            "// important comment",
                            "var = 0;", "}"])
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


class TestCodeGenerator(unittest.TestCase, UsefullTools):

    code = """SUBI SP 1;
    LOAD ACC encode(w);
    STOREIN SP ACC 1;
    """

    def test_code_replacment_after(self, ):
        code_generator = CodeGenerator()
        symbol_table = SymbolTable()

        var = VariableSymbol('car', symbol_table.resolve('int'))
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


class TestPrograms(unittest.TestCase, UsefullTools):

    def test_gcd(self, ):
        self.set_everything_up_for_testing_program_file("gcd",
                                                        "./test/gcd.picoc")


class TestErrorMessages(unittest.TestCase, UsefullTools):

    def test_no_semicolon(self, ):
        test_code = """void main() {
                      int var = 32
                      if (var < 3) {
                          var = 10;
                      }
                    }
                    """
        try:
            self.set_everything_up_for_multiline_program(
                "no semicolon", test_code)
        except SystemExit:
            pass

    def test_no_assignment_operator(self, ):
        test_code = """void main() {
                      int var 42 % 7;
                    }
                    """
        try:
            self.set_everything_up_for_multiline_program(
                "no assignment operator", test_code)
        except SystemExit:
            pass

    def test_one_liner(self, ):
        test_code = """void main() { int var = 32  var = 10; }
        """
        try:
            self.set_everything_up_for_multiline_program(
                "one liner", test_code)
        except SystemExit:
            pass

    def test_no_closing_parenthesis(self, ):
        test_code = """void main() {
                      if (12) {
                        int var = (32 * 2;
                        var = 10;
                      }
                    }
                    """
        try:
            self.set_everything_up_for_multiline_program(
                "no closing parenthesis", test_code)
        except SystemExit:
            pass

    def test_several_parenthesis_nested(self, ):
        test_code = """void main() {
                      if (12) {
                        int var = 1 + (2 * (31 + 42);
                        var = 10;
                      }
                    }
                    """
        try:
            self.set_everything_up_for_multiline_program(
                "no closing parenthesis", test_code)
        except SystemExit:
            pass

    def test_no_opening_brace_main(self, ):
        test_code = """void main()
                    }
                    """
        try:
            self.set_everything_up_for_multiline_program(
                "no opening brace main", test_code)
        except SystemExit:
            pass

    def test_no_right_operand(self, ):
        test_code = """void main() {
                      int var = 42 % ;
                    }
                    """
        try:
            self.set_everything_up_for_multiline_program(
                "no operand right", test_code)
        except SystemExit:
            pass

    def test_no_identifier(self, ):
        test_code = """void main() {
                      int = 42 % 7;
                    }
                    """
        try:
            self.set_everything_up_for_multiline_program(
                "no assignment operator", test_code)
        except SystemExit:
            pass

    def test_invalid_character(self, ):
        test_code = """void main() {
                      int var = 12 @ 3;
                    }
                    """
        try:
            self.set_everything_up_for_multiline_program(
                "invalid character", test_code)
        except SystemExit:
            pass

    def test_no_operator(self, ):
        test_code = """void main() {
                      int var = 12 3;
                    }
                    """
        try:
            self.set_everything_up_for_multiline_program(
                "no operator", test_code)
        except SystemExit:
            pass

    def test_no_left_operand(self, ):
        test_code = """void main() {
                      int var = % 7;
                    }
                    """
        try:
            self.set_everything_up_for_multiline_program(
                "no operand left", test_code)
        except SystemExit:
            pass

    # def test_compile_time_error(self, ):
    #     test_code = """void main() {
    #                   var = 31 >> 7;
    #                 }
    #                 """
    #     try:
    #         self.set_everything_up_for_multiline_program(
    #             "compile time error", test_code)
    #     except SystemExit:
    #         pass

#     def test_no_opening_brace_if(self, ):
#         test_code = """void main() {
#                       if (1) {
#                         const int var = 12;
#                       else
#                         int car = 3
#                     }
#                     """
#         try:
#             self.set_everything_up_for_multiline_program(
#                 "no opening brace if", test_code)
#         except SystemExit:
#             pass
#
#     def test_typo_in_const(self, ):
#         test_code = """void main() {
#                       csnt int var = 12;
#                     }
#                     """
#         try:
#             self.set_everything_up_for_multiline_program(
#                 "typo in const", test_code)
#         except SystemExit:
#             pass
#
#     def test_single_line_comment(self, ):
#         test_code = """void main() {
#                       int var = 32
#                       // i think there's an error somewhere close
#                       if (var < 3) {
#                           var = 10;
#                       }
#                     }
#                     """
#         try:
#             self.set_everything_up_for_multiline_program(
#                 "no semicolon", test_code)
#         except SystemExit:
#             pass


if __name__ == '__main__':
    sys.path.append('/home/areo/Documents/Studium/pico_c_compiler/src')
    from lexer import Lexer, TT
    from grammar import Grammar
    import globals
    from code_generator import CodeGenerator
    from symbol_table import SymbolTable, VariableSymbol
    from abstract_syntax_tree import strip_multiline_string
    from errors import ErrorHandler
    unittest.main()
