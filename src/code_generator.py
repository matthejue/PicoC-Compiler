import global_vars


class _CodeGenerator:
    """Encapsulates all tree-walking code associated with a particular
    task into a single visitor class. Implenents the Singleton pattern

    :ucp_stock: list of pointers to the start of a unfinihsed code layerwise
    :loc_stock: lines of code stock
    """

    _instance = None

    def __init__(self):
        self.code_arranger = CodeArranger()
        self.idx = -1
        self.loc = 0
        self.metadata = []

    def add_code(self, code, loc):
        self.code_arranger.add_code(code)

        self.idx += 1
        self.loc += loc

    def add_marker(self, ):
        """save information about a code piece one does e.g. later want to jump
        back to
        :idx: index of the code piece
        :loc: lines of code up to this code piece's end
        """
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
        self.code_arranger.replace_code(self.metadata[-1][0], pattern, word)

    def replace_code_pre(self, code, pattern, word):
        """Jumps backwards, e.g. needed for while loops.

        :returns: code
        """
        return code.replace(pattern, word)

    def show_code(self, ):
        """Sets the generated / modified code pieces together to one unified
        generated code

        :returns: unified generated code
        """
        return self.code_arranger.align_comments() if global_vars.args.verbose\
            else self.code_arranger.remove_comments()


class CodeArranger:
    def __init__(self):
        self.generated_code = []
        # only single line strings
        # imortant for having comments aligned
        self.amax_comment_distance = 0

    def add_code(self, code):
        self.generated_code += [code]

    def replace_code(self, idx, pattern, word):
        self.generated_code[idx] = self.generated_code[idx].replace(
            pattern, word)

    def remove_comments(self, ):
        clean_code = ""
        for code_line in self._convert_to_lines():
            comment_start = code_line.find(';')
            if comment_start > 0:
                clean_code += code_line[:comment_start + 1] + '\n'
        return clean_code

    def align_comments(self, ):
        aligned_code = ""
        for code_line in self._convert_to_lines():
            if code_line[0] != '#':
                num_spaces = self.amax_comment_distance -\
                    (code_line.index(';') + 1)
                code_line = code_line.replace('  ', ' ' * num_spaces)

            aligned_code += code_line + '\n'
        return aligned_code

    def _convert_to_lines(self, ):
        code_lines = []
        for code in self.generated_code:
            code_lines += code.split('\n')[:-1]

            # find out longest distance from start of line to to a comment
            for code_line in code_lines:
                # no +1 to compensate find() starting with 0 because # +1 index
                # too much for the distance from the start
                self.amax_comment_distance = max(
                    self.amax_comment_distance,
                    code_line.find('#') + global_vars.args.distance)
        return code_lines


def CodeGenerator():
    if _CodeGenerator._instance is None:
        _CodeGenerator._instance = _CodeGenerator()
    return _CodeGenerator._instance
