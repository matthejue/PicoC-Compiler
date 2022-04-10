from function_grammar import FunctionGrammar
from file_node import File
from lexer import TT
from dummy_nodes import NT


class FileGrammar(FunctionGrammar):
    def code_fi(self):
        self._file()

    def _file(self):
        savestate_node = self.ast_builder.down(File)

        self.add_and_match([TT.IDENTIFIER], classname=NT.Filename)

        while self.LTT(1) in self.PRIM_DT.keys():
            self.code_fu()

        self.ast_builder.up(savestate_node)
