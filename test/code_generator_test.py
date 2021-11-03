#!/usr/bin/env python

import unittest
import sys
from testing_helpers import UsefullTools, Args


class TestCodeGenerator(unittest.TestCase, UsefullTools):

    code = """SUBI SP 1;
    LOAD ACC encode(w);
    STOREIN SP ACC 1;
    """

    def test_code_replacment_after(self, ):
        global_vars.args = Args()
        global_vars.test_name = "test code replacment after"

        # create new Singleton SymbolTable and CodeGenerator and remove old
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
    import global_vars
    unittest.main()
