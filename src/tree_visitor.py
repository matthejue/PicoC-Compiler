from abstract_syntax_tree import (TokenNode, WhileNode, DoWhileNode, IFNode,
                                  IfElseNode, MainFunctionNode, AssignmentNode,
                                  AllocationNode,
                                  ArithmeticBinaryOperationNode,
                                  ArithmeticUnaryOperationNode,
                                  ArithmeticVariableConstantNode,
                                  LogicAndOrNode, LogicNotNode, LogicAtomNode)


class CodeGenerator:

    """Encapsulates all tree-walking code associated with a particular
    task into a single visitor class"""

    def __init__(self, ):
        self.combined_reti_code = ""

    def visit(self, node):
        if node.reti_code_start:
            self.combined_reti_code += node.reti_code_start

        # e.g. while and if have a condition check at the start
        if node.reti_code_condition_check:
            node.children[0].visit()
            self.combined_reti_code += node.reti_code_condition_check

        # many nodes have code that has to be inserted in between other code
        first_iteraion = True
        for child in node.children:
            # skipt first child if there is a condition check at the beginning
            if first_iteraion and node.reti_code_condition_check:
                first_iteraion = False
                continue

            child.visit()

        if node.reti_code_end:
            self.combined_reti_code += node.reti_code_end
