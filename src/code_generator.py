

class CodeGenerator:

    """Encapsulates all tree-walking code associated with a particular
    task into a single visitor class. Implenents the Singleton pattern

    :ucp_stock: list of pointers to the start of a unfinihsed code layerwise
    :loc_stock: lines of code stock
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CodeGenerator, cls).__new__(cls)
            # Initialization
            cls._instance.generated_code = []
            cls._instance.ucp_stock = [0]
            cls._instance.loc_stock = [0]
            cls._instance.loc_layer = 0
            cls._instance.loc_idx = 0
        return cls._instance

    def add_code_open(self, code, lines_of_code):
        """Add raw reti code to the generated code.

        :returns: None
        """
        self.loc_layer += 1
        self.loc_idx += 1
        self.ucp_stock += [self.loc_idx]
        self.add_code(code, lines_of_code)

    def add_code(self, code, lines_of_code):
        self.generated_code += [code]

        self.loc_stock += [self.loc_stock[-1] + lines_of_code]

    def add_code_close(self, code, lines_of_code):
        """Add raw reti code to the generated code.

        :returns: None
        """
        self.generated_code += [code]

        self.loc_layer -= 1
        self.ucp_stock.pop()
        if self.loc_layer == 0:
            self.loc_idx = 0
            self.loc_stock.clear()
            self.loc_stock += [0]
        else:
            self.loc_idx += 1
            self.loc_stock += [self.loc_stock[-1] + lines_of_code]

    def replace_jump(self, pattern, offset=0):
        """Jumps have to be adapted depending on how many lines of reti code
        are between them and their destination

        :returns: None
        """
        # -how many steps the last 0 layer is away from the current code
        # snippet + how many steps the target code snippet is away from the
        # last 0 layer
        idx = -self.loc_idx + self.ucp_stock[-1]
        # current lines of code from the last 0 layer to the current code
        # snippet - lines of code from the last 0 layer to the target code
        # snippet
        loc = self.loc_stock[-1] - self.loc_stock[self.ucp_stock[-1]] + offset

        self.generated_code[idx] = self.generated_code[idx].replace(pattern,
                                                                    str(loc))

    def replace_jump_backwards(self, code_as_ref, pattern, offset=0):
        """Jumps backwards are e.g. needed for while loops.

        :returns: None
        """
        # One does not only have to jump to the start of the while, but has to
        # jump before the while and it's condition evaluation. We want to know
        # the LOC difference between e.g. the end of the while and the start
        # of the while statement.
        loc = self.loc_stock[-1] - \
            self.loc_stock[self.ucp_stock[-1] - 1] + offset

        # the pythonic way to pass a string as reference (in a list)
        code_as_ref[0] = code_as_ref[0].replace(pattern, str(loc))

    def replace_code(self, pattern, word):
        """Depending on the Token sometimes different reti code commands have
        to be executed

        :pattern: pattern that should be replaced
        :word: by what the pattern should be replaced
        :returns: None
        """
        idx = -self.loc_idx + self.ucp_stock[-1]
        self.generated_code[idx] = self.generated_code[idx].replace(pattern,
                                                                    str(word))

    def show_code(self, ):
        """Sets the generated / modified code pieces together to one unified
        generated code

        :returns: unified generated code
        """
        code_acc = ""
        for code_piece in self.generated_code:
            code_acc += code_piece
        return code_acc
