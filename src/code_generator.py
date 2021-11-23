import global_vars


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
        """E.g. to get the previous loc for calculation of the difference
        """
        return self.metadata[-1][1]

    def replace_code_after(self, pattern, word):
        """Replace code afterwards after adding it, e.g. for a if-statement to
        jump over a codeblock of beforehand unknown size

        :pattern: pattern that should be replaced
        :word: by what the pattern should be replaced
        :returns: None
        """
        self.generated_code[self.metadata[-1][0]] =\
            self.generated_code[self.metadata[-1]
                                [0]].replace(pattern, str(word))

    def replace_code_pre(self, code, pattern, word):
        """Jumps backwards, e.g. needed for while loops.

        :returns: code
        """
        return code.replace(pattern, str(word))

    def show_code(self, ):
        """Sets the generated / modified code pieces together to one unified
        generated code

        :returns: unified generated code
        """
        code_acc = ""
        for code_piece in self.generated_code:
            if not global_vars.args.verbose:
                code_piece = self._clean_up_code_piece(code_piece)
            code_acc += code_piece
            # code_acc += "\n"
        return code_acc

    def _clean_up_code_piece(self, code_piece):
        cleaned_code = ""
        stop_include_next_c = False
        include = True
        has_seen_semicolon = False
        reset = False
        for c in code_piece:
            if c == '#' and not reset:
                include = False
            elif c == '#' and reset:
                # in case there're two single line comments after
                # another in one code_piece
                include = False
                has_seen_semicolon = False
                reset = False
            elif c == ';':
                stop_include_next_c = True
                has_seen_semicolon = True
            elif c == '\n':
                reset = True
            elif reset:
                stop_include_next_c = False
                include = True
                has_seen_semicolon = False
                reset = False
            elif stop_include_next_c:
                include = False
                stop_include_next_c = False

            if include and c != '\n':
                cleaned_code += c
            elif has_seen_semicolon and c == '\n':
                cleaned_code += c
        return cleaned_code


def CodeGenerator():
    """Factory Function as possible way to implement Singleton Pattern.
    Taken from here:
    https://stackoverflow.com/questions/52351312/singleton-pattern-in-python

    :returns: None
    """
    if _CodeGenerator._instance is None:
        _CodeGenerator._instance = _CodeGenerator()
    return _CodeGenerator._instance
