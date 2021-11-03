#!/usr/bin/env python

import unittest
import sys


class Args(object):

    """For the purpose of testing constructed class which simulates the
    intended bahaviour of the args variable in global_vars.py"""

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
        global_vars.test_name = test_name
        global_vars.args = Args()
        self.lexer = Lexer(test_name, [code])
        tokens = []
        t = self.lexer.next_token()
        while t.type != TT.EOF:
            tokens += [t]
            t = self.lexer.next_token()
        return tokens

    def set_everything_up_for_ast(self, test_name, code):
        global_vars.test_name = test_name
        global_vars.args = Args()
        self.lexer = Lexer(test_name, [code])

        self.grammar = Grammar(self.lexer)
        self.grammar.start_parse()

    def set_everything_up_for_ast_multiline(self, test_name, code_without_cr):
        global_vars.test_name = test_name
        global_vars.args = Args()
        self.lexer = Lexer(test_name, code_without_cr)

        self.grammar = Grammar(self.lexer)
        self.grammar.start_parse()

    def set_everything_up_for_visit_multiline(self, test_name, code_without_cr):
        global_vars.test_name = test_name
        # create new Singleton SymbolTable and CodeGenerator and remove old
        SymbolTable().__init__()
        CodeGenerator().__init__()

        global_vars.args = Args()
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

    def test_compile_time_error_assignment(self, ):
        test_code = """void main() {
                      var = 31 >> 7;
                    }
                    """
        try:
            self.set_everything_up_for_multiline_program(
                "compile time error assignment", test_code)
        except SystemExit:
            pass

    def test_compile_time_error_not_initialised_variable(self, ):
        test_code = """void main() {
                      int x = 12 & var;
                    }
                    """
        try:
            self.set_everything_up_for_multiline_program(
                "compile time error not initialised variable", test_code)
        except SystemExit:
            pass

    def test_no_closing_brace_if(self, ):
        test_code = """void main() {
                      if (1) {
                        const int var = 12;
                      else
                        int car = 3
                    }
                    """
        try:
            self.set_everything_up_for_multiline_program(
                "no closing brace if", test_code)
        except SystemExit:
            pass

    def test_typo_in_const(self, ):
        test_code = """void main() {
                      csnt int var = 12;
                    }
                    """
        try:
            self.set_everything_up_for_multiline_program(
                "typo in const", test_code)
        except SystemExit:
            pass

    def test_single_line_comment(self, ):
        test_code = """void main() {
                      int var = 32
                      // i think there's an error somewhere close
                      if (var < 3) {
                          var = 10;
                      }
                    }
                    """
        try:
            self.set_everything_up_for_multiline_program(
                "single line comment", test_code)
        except SystemExit:
            pass

    def test_inline_comment(self, ):
        test_code = """void main() {
                      int var = 32  // that looks problematic
                      var = 2;
                    }
                    """
        try:
            self.set_everything_up_for_multiline_program(
                "inline comment", test_code)
        except SystemExit:
            pass

    def test_stupid_inline_comment(self, ):
        test_code = """void main() {
                      int var = 32// that looks problematic
                      var = 2;
                    }
                    """
        try:
            self.set_everything_up_for_multiline_program(
                "stupid inline comment", test_code)
        except SystemExit:
            pass


if __name__ == '__main__':
    sys.path.append('/home/areo/Documents/Studium/pico_c_compiler/src')
    from lexer import Lexer, TT
    from grammar import Grammar
    import global_vars
    from code_generator import CodeGenerator
    from symbol_table import SymbolTable, VariableSymbol
    from abstract_syntax_tree import strip_multiline_string
    from errors import ErrorHandler
    unittest.main()
