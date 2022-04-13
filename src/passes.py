from picoc_nodes import NT


class PicoCCompiler(object):
    def remove_exp(self):
        ...

    def remove_stmt(self):
        ...

    def remove_complex_opds(self, f: NT.File):
        match f:
            case NT.File():
                ...
