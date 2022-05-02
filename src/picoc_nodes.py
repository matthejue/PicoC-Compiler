from ast_node import ASTNode


class N:
    """Nodes"""

    ###########################################################################
    #                        Nodetypes replacing Tokens                       #
    ###########################################################################

    class Name(ASTNode):
        # shorter then 'Identifier'
        pass

    class Num(ASTNode):
        pass

    class Char(ASTNode):
        pass

    class Minus(ASTNode):
        pass

    class Not(ASTNode):
        pass

    class Add(ASTNode):
        pass

    class Sub(ASTNode):
        pass

    class Mul(ASTNode):
        pass

    class Div(ASTNode):
        pass

    class Mod(ASTNode):
        pass

    class Oplus(ASTNode):
        pass

    class And(ASTNode):
        pass

    class Or(ASTNode):
        pass

    class Eq(ASTNode):
        pass

    class NEq(ASTNode):
        pass

    class Lt(ASTNode):
        pass

    class Gt(ASTNode):
        pass

    class LtE(ASTNode):
        pass

    class GtE(ASTNode):
        pass

    class LogicAnd(ASTNode):
        pass

    class LogicOr(ASTNode):
        pass

    class LogicNot(ASTNode):
        pass

    class Const(ASTNode):
        pass

    class Writeable(ASTNode):
        pass

    class IntType(ASTNode):
        pass

    class CharType(ASTNode):
        pass

    class VoidType(ASTNode):
        pass

    class Else(ASTNode):
        pass

    ###########################################################################
    #                     Nodetypes containing other Nodes                    #
    ###########################################################################

    class BinOp(ASTNode):
        def __init__(self, left_exp, op, right_exp):
            self.left_exp = left_exp
            self.op = op
            self.right_exp = right_exp

        __match_args__ = ("left_exp", "op", "right_exp")

    class UnOp(ASTNode):
        def __init__(self, un_op, opd):
            self.un_op = un_op
            self.opd = opd

        __match_args__ = ("un_op", "opd")

    class Atom(ASTNode):
        def __init__(self, left_logic_opd, relation, right_logic_opd):
            self.left_logic_opd = left_logic_opd
            self.relation = relation
            self.right_logic_opd = right_logic_opd

        __match_args__ = ("left_logic_opd", "relation", "right_logic_opd")

    class ToBool(ASTNode):
        def __init__(self, arith_exp):
            self.arith_exp = arith_exp

        __match_args__ = ("arith_exp",)

        def __repr__(self):
            return self.to_string_show_node()

    class Assign(ASTNode):
        def __init__(self, location, logic_exp):
            self.location = location
            self.logic_exp = logic_exp

        __match_args__ = ("location", "logic_exp")

        def __repr__(self):
            if len(self.children) == 2:
                # for the debugger one uses children, else the debugger is
                # going to throw a error if __init__ wasn't executed
                return f"({self.children[0]} = {self.children[1]})"

            return super().__repr__()

    class Alloc(ASTNode):
        def __init__(self, type_qual, size_qual, identifier):
            self.type_qual = type_qual
            self.size_qual = size_qual
            self.identifier = identifier

        __match_args__ = ("type_qual", "size_qual", "identifier")

    class PointerType(ASTNode):
        def __init__(self, size_qual):
            self.size_qual = size_qual

        __match_args__ = ("size_qual",)

    class Ref(ASTNode):
        def __init__(self, location):
            self.location = location

        __match_args__ = ("location",)

    class Deref(ASTNode):
        def __init__(self, location):
            self.location = location

        __match_args__ = ("location",)

    class ArrayType(ASTNode):
        def __init__(self, size_qual):
            self.size_qual = size_qual

        __match_args__ = ("size_qual",)

    class Array(ASTNode):
        def __init__(self, size_qual, entries):
            self.size_qual = size_qual
            self.entries = entries

        __match_args__ = ("size_qual", "entries")

    class Subscript(ASTNode):
        def __init__(self, identifier, logic_exp):
            self.identifier = identifier
            self.logic_exp = logic_exp

        __match_args__ = ("identifier", "logic_exp")

    class StructType(ASTNode):
        def __init__(self, identifier):
            self.identifier = identifier

        __match_args__ = ("identifier",)

    class Struct(ASTNode):
        def __init__(self, assignments):
            self.assignments = assignments

        __match_args__ = ("assignments",)

    class Attribute(ASTNode):
        def __init__(self, array_identifier, attribute_identifier):
            self.array_identifier = array_identifier
            self.attribute_identifier = attribute_identifier

        __match_args__ = ("array_identifier", "attribute_identifier")

    class StructDecl(ASTNode):
        def __init__(self, struct_identifier, params):
            self.struct_identifier = struct_identifier
            self.params = params

        __match_args__ = ("struct_identifier", "params")

    class Param(ASTNode):
        def __init__(self, size_qual, identifier):
            self.size_qual = size_qual
            self.identifier = identifier

        __match_args__ = ("size_qual", "identifier")

    class If(ASTNode):
        def __init__(self, condition, branch):
            self.condition = condition
            self.branch = branch

        __match_args__ = ("condition", "branch")

        def __repr__(self):
            return self.to_string_show_node()

    class IfElse(ASTNode):
        def __init__(self, condition, branch1, branch2):
            self.condition = condition
            self.branch1 = branch1
            self.branch2 = branch2

        __match_args__ = ("condition", "branch1", "branch2")

        def __repr__(self):
            return self.to_string_show_node()

    class While(ASTNode):
        def __init__(self, condition, branch):
            self.condition = condition
            self.branch = branch

        __match_args__ = ("condition", "branch")

        def __repr__(self):
            return self.to_string_show_node()

    class DoWhile(ASTNode):
        def __init__(self, branch, condition):
            self.branch = branch
            self.condition = condition

        __match_args__ = ("condition", "branch")

        def __repr__(self):
            return self.to_string_show_node()

    class FunType(ASTNode):
        def __init__(self, size_qual):
            self.size_qual = size_qual

        __match_args__ = ("size_qual",)

    class Call(ASTNode):
        def __init__(self, functionname, args):
            self.functionname = functionname
            self.args = args

        __match_args__ = ("functionname", "args")

        def __repr__(self):
            return self.to_string_show_node()

    class Return(ASTNode):
        def __init__(self, logic_exp):
            self.logic_exp = logic_exp

        __match_args__ = ("logic_exp",)

        def __repr__(self):
            return self.to_string_show_node()

    class Exp(ASTNode):
        def __init__(self, call):
            self.call = call

        __match_args__ = ("call",)

    class FunDef(ASTNode):
        def __init__(self, size_qual, fun_name, params, stmts_blocks):
            self.size_qual = size_qual
            self.fun_name = fun_name
            self.params = params
            self.stmts_blocks = stmts_blocks

        __match_args__ = ("size_qual", "fun_name", "params", "stmts_blocks")

    class File(ASTNode):
        def __init__(self, filename, main_fun, funs):
            self.filename = filename
            self.main_fun = main_fun
            self.funs = funs

        __match_args__ = ("filename", "main_fun", "funs")

    class Block(ASTNode):
        def __init__(self, name, stmsts):
            self.name = name
            self.stmts = stmsts

        __match_args__ = ("name", "stmts")
