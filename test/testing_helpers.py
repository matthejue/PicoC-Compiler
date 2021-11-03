import sys


class Args():

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
        global_vars.args = Args()
        global_vars.test_name = test_name

        # create new Singleton SymbolTable and CodeGenerator and remove old
        SymbolTable().__init__()
        CodeGenerator().__init__()

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


if __name__ == 'testing_helpers':
    sys.path.append('/home/areo/Documents/Studium/pico_c_compiler/src')
    from lexer import Lexer, TT
    from grammar import Grammar
    import global_vars
    from code_generator import CodeGenerator
    from symbol_table import SymbolTable, VariableSymbol
    from abstract_syntax_tree import strip_multiline_string
    from error_handler import ErrorHandler
