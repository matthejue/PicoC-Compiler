from parse_fun import FunParser
from lexer import TT
from picoc_nodes import N


class FileParser(FunParser):
    def parse_file(self):
        self._file()

    def _file(self):
        savestate_node = self.ast_builder.down(N.File)

        self.add_and_match([TT.IDENTIFIER], classname=N.Name)

        while self.LTT(1) in self.PRIM_DT.keys():
            self.parse_fun()

        self.ast_builder.up(savestate_node)
