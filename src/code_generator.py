from abstract_syntax_tree import (TokenNode, WhileNode, DoWhileNode, IFNode,
                                  IfElseNode, MainFunctionNode, AssignmentNode,
                                  AllocationNode,
                                  ArithmeticBinaryOperationNode,
                                  ArithmeticUnaryOperationNode,
                                  ArithmeticVariableConstantNode,
                                  LogicAndOrNode, LogicNotNode, LogicAtomNode)


class CodeGenerator:

    """Encapsulates all tree-walking code associated with a particular
    task into a single visitor class. Implenents the Singleton pattern"""

    _instance = None
    generated_code = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CodeGenerator, cls).__new__(cls)
            # Initialization
        return cls._instance

    def add_code(self, code):
        """Add raw reti code to the generated code.

        :returns: None
        """
        self.generated_code += [code]
        return self.generated_code[-1]

    def replace_jump(self, code, num_lines):
        """Jumps have to be adapted depending on how many lines of reti code
        are between them and their destination.

        :code: code were jumps should be replaced
        :returns: None
        """
        code[-1] = code[-1].format(num_lines)

    def replace_code(self, code, word):
        """Depending on the Token sometimes different reti code commands have
        to be executed

        :code: code were commands should be replaced
        :returns: None
        """
        self.code[-1] = self.code[-1].format(word)

    def finish(self, ):
