from ast_node import ASTNode


class N:
    """Nodes"""

    # =========================================================================
    # =                              Token Nodes                              =
    # =========================================================================
    # -------------------------------- L_Arith --------------------------------
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

    # -------------------------------- L_Logic --------------------------------
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

    # ----------------------------- L_Assign_Alloc ----------------------------
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

    # =========================================================================
    # =                            Container Nodes                            =
    # =========================================================================
    # -------------------------------- L_Arith --------------------------------
    class BinOp(ASTNode):
        def __init__(self, left_exp, bin_op, right_exp):
            self.left_exp = left_exp
            self.bin_op = bin_op
            self.right_exp = right_exp
            super().__init__(children=[self.left_exp, self.bin_op, self.right_exp])

        __match_args__ = ("left_exp", "bin_op", "right_exp")

    class UnOp(ASTNode):
        def __init__(self, un_op, exp):
            self.un_op = un_op
            self.exp = exp
            super().__init__(children=[self.un_op, self.exp])

        __match_args__ = ("un_op", "exp")

    # -------------------------------- L_Logic --------------------------------
    class Atom(ASTNode):
        def __init__(self, left_exp, rel, right_exp):
            self.left_exp = left_exp
            self.rel = rel
            self.right_exp = right_exp
            super().__init__(children=[self.left_exp, self.rel, self.right_exp])

        __match_args__ = ("left_exp", "rel", "right_exp")

    class ToBool(ASTNode):
        def __init__(self, exp):
            self.exp = exp
            super().__init__(children=[self.exp])

        __match_args__ = ("exp",)

    # ----------------------------- L_Assign_Alloc ----------------------------
    class Alloc(ASTNode):
        def __init__(self, type_qual, datatype, name):
            self.type_qual = type_qual
            self.datatype = datatype
            self.name = name
            super().__init__(
                children=[
                    self.type_qual,
                    self.datatype,
                    self.name,
                ]
            )

        __match_args__ = (
            "type_qual",
            "datatype",
            "name",
        )

    class Assign(ASTNode):
        def __init__(self, assign_lhs, exp):
            self.assign_lhs = assign_lhs
            self.exp = exp
            super().__init__(children=[self.assign_lhs, self.exp])

        __match_args__ = ("assign_lhs", "exp")

    class Exp(ASTNode):
        def __init__(self, exp):
            self.exp = exp
            super().__init__(children=[self.exp])

        __match_args__ = ("exp",)

    class Stack(ASTNode):
        def __init__(self, num):
            self.num = num
            super().__init__(children=[self.num])

        __match_args__ = ("num",)

    # ------------------------------- L_Pointer -------------------------------
    class PntrDecl(ASTNode):
        def __init__(self, num, datatype):
            self.num = num
            self.datatype = datatype
            super().__init__(children=[self.num, self.datatype])

        __match_args__ = ("num", "datatype")

    class Ref(ASTNode):
        def __init__(self, ref_loc):
            self.ref_loc = ref_loc
            self.datatype = ""
            super().__init__(children=[self.ref_loc, self.datatype])

        __match_args__ = ("ref_loc", "datatype")

    class Deref(ASTNode):
        def __init__(self, deref_loc, exp):
            self.deref_loc = deref_loc
            self.exp = exp
            super().__init__(children=[self.deref_loc, self.exp])

        __match_args__ = ("deref_loc", "exp")

    # -------------------------------- L_Array --------------------------------
    class ArrayDecl(ASTNode):
        def __init__(self, nums, datatype):
            self.nums = nums
            self.datatype = datatype
            super().__init__(children=[self.nums, self.datatype])

        __match_args__ = (
            "nums",
            "datatype",
        )

    class Array(ASTNode):
        def __init__(self, exps):
            self.exps = exps
            super().__init__(children=[self.exps])

        __match_args__ = ("datatype", "exps")

    class Subscr(ASTNode):
        def __init__(self, deref_loc, exp):
            self.deref_loc = deref_loc
            self.exp = exp
            super().__init__(children=[self.deref_loc, self.exp])

        __match_args__ = ("deref_loc", "exp")

    # -------------------------------- L_Struct -------------------------------
    class StructSpec(ASTNode):
        def __init__(self, name):
            self.name = name
            super().__init__(children=[self.name])

        __match_args__ = ("name",)

    class Attr(ASTNode):
        def __init__(self, ref_loc, name):
            self.ref_loc = ref_loc
            self.name = name
            super().__init__(children=[self.ref_loc, self.name])

        __match_args__ = ("ref_loc", "name")

    class Struct(ASTNode):
        def __init__(self, assigns):
            self.assigns = assigns
            super().__init__(children=[self.assigns])

        __match_args__ = ("assigns",)

    class StructDecl(ASTNode):
        def __init__(self, name, params):
            self.name = name
            self.params = params
            super().__init__(children=[self.name, self.params])

        __match_args__ = ("name", "params")

    class Param(ASTNode):
        def __init__(self, datatype, name):
            self.datatype = datatype
            self.name = name
            super().__init__(children=[self.datatype, self.name])

        __match_args__ = ("datatype", "name")

    # ------------------------------- L_If_Else -------------------------------
    class If(ASTNode):
        def __init__(self, exp, stmts_goto):
            self.exp = exp
            self.stmts_goto = stmts_goto
            super().__init__(children=[self.exp, self.stmts_goto])

        __match_args__ = ("exp", "stmts_goto")

    class IfElse(ASTNode):
        def __init__(self, exp, stmts_goto1, stmts_goto2):
            self.exp = exp
            self.stmts_goto1 = stmts_goto1
            self.stmts_goto2 = stmts_goto2
            super().__init__(children=[self.exp, self.stmts_goto1, self.stmts_goto2])

        __match_args__ = ("exp", "stmts_goto1", "stmts_goto2")

    # --------------------------------- L_Loop --------------------------------
    class While(ASTNode):
        def __init__(self, exp, stmts_goto):
            self.exp = exp
            self.stmts_goto = stmts_goto
            super().__init__(children=[self.exp, self.stmts_goto])

        __match_args__ = ("exp", "stmts_goto")

    class DoWhile(ASTNode):
        def __init__(self, exp, stmts_goto):
            self.exp = exp
            self.stmts_goto = stmts_goto
            super().__init__(children=[self.exp, self.stmts_goto])

        __match_args__ = ("exp", "stmts_goto")

    # --------------------------------- L_Fun ---------------------------------
    class Call(ASTNode):
        def __init__(self, name, exps):
            self.name = name
            self.exps = exps
            super().__init__(children=[self.name, self.exps])

        __match_args__ = ("name", "exps")

    class Return(ASTNode):
        def __init__(self, exp):
            self.exp = exp
            super().__init__(children=[self.exp])

        __match_args__ = ("exp",)

    class FunDecl(ASTNode):
        def __init__(self, datatype, name, params):
            self.datatype = datatype
            self.name = name
            self.params = params
            super().__init__(children=[self.datatype, self.name, self.params])

        __match_args__ = ("datatype", "name", "params")

    class FunDef(ASTNode):
        def __init__(self, datatype, name, params, stmts_blocks):
            self.datatype = datatype
            self.name = name
            self.params = params
            self.stmts_blocks = stmts_blocks
            super().__init__(
                children=[
                    self.datatype,
                    self.name,
                    self.params,
                    self.stmts_blocks,
                ]
            )

        __match_args__ = ("datatype", "name", "params", "stmts_blocks")

    # --------------------------------- L_File --------------------------------
    class File(ASTNode):
        def __init__(self, name, decls_defs):
            self.name = name
            self.decls_defs = decls_defs
            super().__init__(children=[self.name, self.decls_defs])

        __match_args__ = ("name", "decls_defs")

    # -------------------------------- L_Block --------------------------------
    class Block(ASTNode):
        def __init__(self, name, stmts_instrs):
            self.name = name
            self.stmts_instrs = stmts_instrs
            self.instrs_before = ""
            self.instrs_after = ""
            super().__init__(
                children=[
                    self.name,
                    self.stmts_instrs,
                    self.instrs_before,
                    self.instrs_after,
                ]
            )

        __match_args__ = ("name", "stmts_instrs", "instrs_before", "instrs_after")

    class GoTo(ASTNode):
        def __init__(self, name):
            self.name = name
            super().__init__(children=[self.name])

        __match_args__ = ("name",)
