from picoc_nodes import NT


class PicoCCompiler(object):

    ###########################################################################
    #                         Remove complex operands                         #
    ###########################################################################

    def remove_exp(self):
        ...

    def remove_stmt(self):
        ...

    def remove_complex_opds(self, f: NT.File):
        match f:
            case NT.File():
                ...

    ###########################################################################
    #                           Select Instructions                           #
    ###########################################################################

    def select_exp(
        self,
    ):
        ...

    def select_stmt(
        self,
    ):
        ...

    def select_instructions(self, arg1):
        pass
