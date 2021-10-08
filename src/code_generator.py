import globals


class _CodeGenerator:

    """Encapsulates all tree-walking code associated with a particular
    task into a single visitor class. Implenents the Singleton pattern

    :ucp_stock: list of pointers to the start of a unfinihsed code layerwise
    :loc_stock: lines of code stock
    """

    _instance = None

    def __init__(self):
        self.generated_code = []
        # self.loc_stock = [0]
        # self.ucp_stock = [0]
        # self.loc_layer = 0

        self.idx = -1
        self.loc = 0
        self.metadata = []

    def add_code(self, code, loc):
        self.generated_code += [code]

        self.idx += 1
        self.loc += loc

    def add_marker(self, ):
        self.metadata += [(self.idx, self.loc)]

    def remove_marker(self, ):
        self.metadata.pop()

    def get_marker_loc(self, ):
        return self.metadata[-1][1]

    def replace_code_after(self, pattern, word):
        """Depending on the Token sometimes different reti code commands have
        to be executed

        :pattern: pattern that should be replaced
        :word: by what the pattern should be replaced
        :returns: None
        """
        self.generated_code[self.metadata[-1][0]] =\
            self.generated_code[self.metadata[-1]
                                [0]].replace(pattern, str(word))

    def replace_code_pre(self, code_as_ref, pattern, word):
        """Jumps backwards are e.g. needed for while loops.

        :returns: None
        """
        return code_as_ref.replace(pattern, str(word))

    def show_code(self, ):
        """Sets the generated / modified code pieces together to one unified
        generated code

        :returns: unified generated code
        """
        code_acc = ""
        for code_piece in self.generated_code:
            if not globals.args.comments:
                cleaned_code = ""
                include = True
                for c1, c2 in list((code_piece[i], code_piece[i+1]) for
                                   i in range(len(code_piece)-1)):
                    if c1 == '#':
                        include = False
                    elif c1 + c2 == '\n#':
                        include = False
                    elif c1 == '\n':
                        include = True

                    if include:
                        cleaned_code += c1
                if include:
                    cleaned_code += c2
                code_piece = cleaned_code

            code_acc += code_piece
        return code_acc


def CodeGenerator():
    """Factory Function as possible way to implement Singleton Pattern.
    Taken from here:
    https://stackoverflow.com/questions/52351312/singleton-pattern-in-python

    :returns: None
    """
    if _CodeGenerator._instance is None:
        _CodeGenerator._instance = _CodeGenerator()
    return _CodeGenerator._instance
