from ast_node import ASTNode
from errors import Errors


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
        def update_match_args(self):
            self.left_exp = self.children[0]
            self.op = self.children[1]
            self.right_exp = self.children[2]

        __match_args__ = ("left_exp", "op", "right_exp")

    class UnOp(ASTNode):
        def update_match_args(self):
            self.un_op = self.children[0]
            self.opd = self.children[1]

        __match_args__ = ("un_op", "opd")

    class Atom(ASTNode):
        def update_match_args(self):
            self.left_logic_opd = self.children[0]
            self.relation = self.children[1]
            self.right_logic_opd = self.children[2]

        __match_args__ = ("left_logic_opd", "relation", "right_logic_opd")

    class ToBool(ASTNode):
        def update_match_args(self):
            self.arith_exp = self.children[0]

        __match_args__ = "arith_exp"

        def __repr__(self):
            return self.to_string_show_node()

    class Assign(ASTNode):
        def update_match_args(self):
            self.location = self.children[0]
            self.logic_exp = self.children[1]

        __match_args__ = ("location", "logic_exp")

        def __repr__(self):
            if len(self.children) == 2:
                # for the debugger one uses children, else the debugger is
                # going to throw a error if update_match_args wasn't executed
                return f"({self.children[0]} = {self.children[1]})"

            return super().__repr__()

    class Alloc(ASTNode):
        def update_match_args(self):
            self.type_qual = self.children[0]
            self.size_qual = self.children[1]
            self.identifier = self.children[2]

        __match_args__ = ("type_qual", "size_qual", "identifier")

    class PointerType(ASTNode):
        def update_match_args(self):
            self.size_qual = self.children[0]

        __match_args__ = ("size_qual",)

    class Ref(ASTNode):
        def update_match_args(self):
            self.location = self.children[0]

        __match_args__ = ("location",)

    class Deref(ASTNode):
        def update_match_args(self):
            self.location = self.children[0]

        __match_args__ = ("location",)

    class ArrayType(ASTNode):
        def update_match_args(self):
            self.size_qual = self.children[0]

        __match_args__ = ("size_qual",)

    class Array(ASTNode):
        def update_match_args(self):
            self.size_qual = self.children[0]
            self.entries = self.children[1:]

        __match_args__ = ("size_qual", "entries")

    class Subscript(ASTNode):
        def update_match_args(self):
            self.identifier = self.children[0]
            self.logic_exp = self.children[1]

        __match_args__ = ("identifier", "logic_exp")

    class StructType(ASTNode):
        def update_match_args(self):
            self.identifier = self.children[0]

        __match_args__ = ("identifier",)

    class Struct(ASTNode):
        def update_match_args(self):
            self.assignments = self.children

        __match_args__ = ("assignments",)

    class Attribute(ASTNode):
        def update_match_args(self):
            self.array_identifier = self.children[0]
            self.attribute_identifier = self.children[1]

        __match_args__ = ("array_identifier", "attribute_identifier")

    class StructDef(ASTNode):
        def update_match_args(self):
            self.struct_identifier = self.children[0]
            self.params = self.children[1:]

        __match_args__ = ("struct_identifier", "params")

    class Param(ASTNode):
        def update_match_args(self):
            self.identifier = self.children[0]
            self.size_qual = self.children[1]

        __match_args__ = ("identifier", "size_qual")

    class If(ASTNode):
        def update_match_args(self):
            self.condition = self.children[0]
            self.branch = self.children[1:]

        __match_args__ = ("condition", "branch")

        def __repr__(self):
            return self.to_string_show_node()

    class IfElse(ASTNode):
        def update_match_args(self):
            for (i, child) in enumerate(self.children):
                match child:
                    case N.Else():
                        break
            else:
                # should never happen
                ...
            self.condition = self.children[0]
            self.branch1 = self.children[1:i]
            self.branch2 = self.children[i + 1 :]

        __match_args__ = ("condition", "branch1", "branch2")

        def __repr__(self):
            return self.to_string_show_node()

    class While(ASTNode):
        def update_match_args(self):
            self.condition = self.children[0]
            self.branch = self.children[1:]

        __match_args__ = ("condition", "branch")

        def __repr__(self):
            return self.to_string_show_node()

    class DoWhile(ASTNode):
        def update_match_args(self):
            self.branch = self.children[:-1]
            self.condition = self.children[-1]

        __match_args__ = ("condition", "branch")

        def __repr__(self):
            return self.to_string_show_node()

    class FunType(ASTNode):
        def update_match_args(self):
            self.size_qual = self.children[0]

        __match_args__ = ("size_qual",)

    class Call(ASTNode):
        def update_match_args(self):
            self.functionname = self.children[0]
            self.args = self.children[1:]

        __match_args__ = ("functionname", "args")

        def __repr__(self):
            return self.to_string_show_node()

    class Return(ASTNode):
        def update_match_args(self):
            self.logic_exp = self.children[0]

        __match_args__ = ("logic_exp",)

        def __repr__(self):
            return self.to_string_show_node()

    class Exp(ASTNode):
        def update_match_args(self):
            self.call = self.children[0]

        __match_args__ = ("call",)

    class FunDef(ASTNode):
        def update_match_args(self):
            self.size_qual = self.children[0]
            self.fun_name = self.children[1]
            for (i, child) in enumerate(self.children[2:]):
                match child:
                    case N.Param(_, _):
                        pass
                    case _:
                        break
            else:
                # TODO: error message
                ...
            self.params = self.children[2:i]
            self.stmts_blocks = self.children[i:]

        __match_args__ = ("size_qual", "fun_name", "params", "stmts_blocks")

    class File(ASTNode):
        def update_match_args(self):
            self.filename = self.children[0]

            # determine the main function
            for (i, child) in enumerate(self.children):
                match child:
                    case N.FunDef(N.Name("main"), _, _, _):
                        break
            else:
                raise Errors.NoMainFunctionError(str(self.filename))
            self.main_fun = self.children[i]
            self.funs = self.children[1:i] + self.children[i + 1 :]

        __match_args__ = ("filename", "main_fun", "funs")

    class Block(ASTNode):
        def update_match_args(self):
            self.name = self.children[0]
            self.stmts = self.children[1:]

        __match_args__ = ("name", "stmts")
