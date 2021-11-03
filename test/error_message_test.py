#!/usr/bin/env python

import unittest
from testing_helpers import UsefullTools


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
        # TODO: hier wird expected an der falschen Stelle angezeigt
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

    def test_unclosed_character_error(self, ):
        test_code = """void main() {
                      int x = 'C' + 1;
                      x = x + ('a - 'A');
                    }
                    """
        try:
            self.set_everything_up_for_multiline_program(
                "unclosed character error", test_code)
        except SystemExit:
            pass


if __name__ == '__main__':
    unittest.main()
