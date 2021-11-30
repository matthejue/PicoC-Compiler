#!/usr/bin/python

import unittest
from testing_helpers import UsefullTools


class TestLexer(unittest.TestCase, UsefullTools):
    def test_space_and_word_seperation(self, ):
        tokens = self.set_everything_up_for_lexer("space and word seperation",
                                                  "  -12ab   --  (   var)")
        self.assertEqual(str(tokens),
                         str(['-', '12', 'ab', '-', '-', '(', 'var', ')']))

    def test_numbers(self, ):
        tokens = self.set_everything_up_for_lexer("numbers",
                                                  "12 0 10 9876543021")
        self.assertEqual(str(tokens), str(['12', '0', '10', '9876543021']))

    def test_comments(self, ):
        tokens = self.set_everything_up_for_lexer(
            "comments", "var = /* comment */ 10; //"
            " important comment")
        self.assertEqual(str(tokens), str(['var', '=', '10', ';']))


class TestComments(unittest.TestCase, UsefullTools):
    def test_single_line_comment(self, ):
        self.set_everything_up_for_ast_multiline("commenttest", [
            "void main() {", "var = 10;", "// important comment", "var = 0;",
            "}"
        ])
        expected_res = "('main' ('=' 'var' '10') ('=' 'var' '0'))"
        self.assertEqual(str(self.grammar.reveal_ast()), expected_res)


if __name__ == '__main__':
    unittest.main()
