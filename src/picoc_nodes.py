from ast_node import PicoCNode


class N:
    """Nodes"""

    # =========================================================================
    # =                              Token Nodes                              =
    # =========================================================================
    # -------------------------------- L_Arith --------------------------------
    class Name(PicoCNode):
        # shorter then 'Identifier'
        pass

    class Num(PicoCNode):
        pass

    class Char(PicoCNode):
        pass

    class Minus(PicoCNode):
        pass

    class Not(PicoCNode):
        pass

    class Add(PicoCNode):
        pass

    class Sub(PicoCNode):
        pass

    class Mul(PicoCNode):
        pass

    class Div(PicoCNode):
        pass

    class Mod(PicoCNode):
        pass

    class Oplus(PicoCNode):
        pass

    class And(PicoCNode):
        pass

    class Or(PicoCNode):
        pass

    # -------------------------------- L_Logic --------------------------------
    class Eq(PicoCNode):
        pass

    class NEq(PicoCNode):
        pass

    class Lt(PicoCNode):
        pass

    class Gt(PicoCNode):
        pass

    class LtE(PicoCNode):
        pass

    class GtE(PicoCNode):
        pass

    class LogicAnd(PicoCNode):
        pass

    class LogicOr(PicoCNode):
        pass

    class LogicNot(PicoCNode):
        pass

    # ----------------------------- L_Assign_Alloc ----------------------------
    class Const(PicoCNode):
        pass

    class Writeable(PicoCNode):
        pass

    class IntType(PicoCNode):
        pass

    class CharType(PicoCNode):
        pass

    class VoidType(PicoCNode):
        pass

    # =========================================================================
    # =                            Container Nodes                            =
    # =========================================================================
    # -------------------------------- L_Arith --------------------------------
    class BinOp(PicoCNode):
        def __init__(self, left_exp, bin_op, right_exp):
            self.left_exp = left_exp
            self.bin_op = bin_op
            self.right_exp = right_exp
            super().__init__(children=[self.left_exp, self.bin_op, self.right_exp])

        __match_args__ = ("left_exp", "bin_op", "right_exp")

    class UnOp(PicoCNode):
        def __init__(self, un_op, exp):
            self.un_op = un_op
            self.exp = exp
            super().__init__(children=[self.un_op, self.exp])

        __match_args__ = ("un_op", "exp")

    # -------------------------------- L_Logic --------------------------------
    class Atom(PicoCNode):
        def __init__(self, left_exp, relation, right_exp):
            self.left_exp = left_exp
            self.relation = relation
            self.right_exp = right_exp
            super().__init__(children=[self.left_exp, self.relation, self.right_exp])

        __match_args__ = ("left_exp", "relation", "right_exp")

    class ToBool(PicoCNode):
        def __init__(self, exp):
            self.exp = exp
            super().__init__(children=[self.exp])

        __match_args__ = ("exp",)

    # ----------------------------- L_Assign_Alloc ----------------------------
    class Alloc(PicoCNode):
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

    class Assign(PicoCNode):
        def __init__(self, assign_lhs, exp):
            self.assign_lhs = assign_lhs
            self.exp = exp
            super().__init__(children=[self.assign_lhs, self.exp])

        __match_args__ = ("assign_lhs", "exp")

    class Exp(PicoCNode):
        def __init__(self, exp):
            self.exp = exp
            super().__init__(children=[self.exp])

        __match_args__ = ("exp",)

    class Stack(PicoCNode):
        def __init__(self, num):
            self.num = num
            super().__init__(children=[self.num])

        __match_args__ = ("num",)

    # ------------------------------- L_Pointer -------------------------------
    class PntrDecl(PicoCNode):
        def __init__(self, num, datatype):
            self.num = num
            self.datatype = datatype
            super().__init__(children=[self.num, self.datatype])

        __match_args__ = ("num", "datatype")

    class Ref(PicoCNode):
        def __init__(self, ref_loc):
            self.ref_loc = ref_loc
            super().__init__(children=[self.ref_loc])

        __match_args__ = ("ref_loc",)

    class Deref(PicoCNode):
        def __init__(self, deref_loc, exp):
            self.deref_loc = deref_loc
            self.exp = exp
            super().__init__(children=[self.deref_loc, self.exp])

        __match_args__ = ("deref_loc", "exp")

    # -------------------------------- L_Array --------------------------------
    class ArrayDecl(PicoCNode):
        def __init__(self, nums, datatype):
            self.nums = nums
            self.datatype = datatype
            super().__init__(children=[self.nums, self.datatype])

        __match_args__ = (
            "nums",
            "datatype",
        )

    class Array(PicoCNode):
        def __init__(self, exps):
            self.exps = exps
            super().__init__(children=[self.exps])

        __match_args__ = ("datatype", "exps")

    class Subscr(PicoCNode):
        def __init__(self, deref_loc, exp):
            self.deref_loc = deref_loc
            self.exp = exp
            super().__init__(children=[self.deref_loc, self.exp])

        __match_args__ = ("deref_loc", "exp")

    # -------------------------------- L_Struct -------------------------------
    class StructSpec(PicoCNode):
        def __init__(self, name):
            self.name = name
            super().__init__(children=[self.name])

        __match_args__ = ("name",)

    class Attr(PicoCNode):
        def __init__(self, ref_loc, name):
            self.ref_loc = ref_loc
            self.name = name
            super().__init__(children=[self.ref_loc, self.name])

        __match_args__ = ("ref_loc", "name")

    class Struct(PicoCNode):
        def __init__(self, assigns):
            self.assigns = assigns
            super().__init__(children=[self.assigns])

        __match_args__ = ("assigns",)

    class StructDecl(PicoCNode):
        def __init__(self, name, params):
            self.name = name
            self.params = params
            super().__init__(children=[self.name, self.params])

        __match_args__ = ("name", "params")

    class Param(PicoCNode):
        def __init__(self, datatype, name):
            self.datatype = datatype
            self.name = name
            super().__init__(children=[self.datatype, self.name])

        __match_args__ = ("datatype", "name")

    # ------------------------------- L_If_Else -------------------------------
    class If(PicoCNode):
        def __init__(self, exp, stmts):
            self.exp = exp
            self.stmts = stmts
            super().__init__(children=[self.exp, self.stmts])

        __match_args__ = ("exp", "stmts")

    class IfElse(PicoCNode):
        def __init__(self, exp, stmts1, stmts2):
            self.exp = exp
            self.stmts1 = stmts1
            self.stmts2 = stmts2
            super().__init__(children=[self.exp, self.stmts1, self.stmts2])

        __match_args__ = ("exp", "stmts1", "stmts2")

    # --------------------------------- L_Loop --------------------------------
    class While(PicoCNode):
        def __init__(self, exp, stmts):
            self.exp = exp
            self.stmts = stmts
            super().__init__(children=[self.exp, self.stmts])

        __match_args__ = ("exp", "stmts")

    class DoWhile(PicoCNode):
        def __init__(self, exp, stmts):
            self.exp = exp
            self.stmts = stmts
            super().__init__(children=[self.exp, self.stmts])

        __match_args__ = ("exp", "stmts")

    # --------------------------------- L_Fun ---------------------------------
    class Call(PicoCNode):
        def __init__(self, name, exps):
            self.name = name
            self.exps = exps
            super().__init__(children=[self.name, self.exps])

        __match_args__ = ("name", "exps")

    class Return(PicoCNode):
        def __init__(self, exp):
            self.exp = exp
            super().__init__(children=[self.exp])

        __match_args__ = ("exp",)

    class FunDecl(PicoCNode):
        def __init__(self, datatype, name, params):
            self.datatype = datatype
            self.name = name
            self.params = params
            super().__init__(children=[self.datatype, self.name, self.params])

        __match_args__ = ("datatype", "name", "params")

    class FunDef(PicoCNode):
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
    class File(PicoCNode):
        def __init__(self, name, decls_defs):
            self.name = name
            self.decls_defs = decls_defs
            super().__init__(children=[self.name, self.decls_defs])

        __match_args__ = ("name", "decls_defs")

    # -------------------------------- L_Block --------------------------------
    class Block(PicoCNode):
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

        __match_args__ = ("name", "stmts_instrs")

    class GoTo(PicoCNode):
        def __init__(self, name):
            self.name = name
            super().__init__(children=[self.name])

        __match_args__ = ("name",)
