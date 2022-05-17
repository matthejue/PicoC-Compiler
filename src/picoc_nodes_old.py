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

    # ------------------------------- L_Pointer -------------------------------
    class PNTR_PLUS(PicoCNode):
        pass

    class PNTR_MINUS(PicoCNode):
        pass

    # --------------------------------- L_Fun ---------------------------------
    class Null(PicoCNode):
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
        def __init__(self, type_qual, size_qual, pntr_decl):
            self.type_qual = type_qual
            self.size_qual = size_qual
            self.pntr_decl = pntr_decl
            super().__init__(
                children=[
                    self.type_qual,
                    self.size_qual,
                    self.pntr_decl,
                ]
            )

        __match_args__ = (
            "type_qual",
            "size_qual",
            "pntr_decl",
        )

    class Assign(PicoCNode):
        def __init__(self, assign_lhs, exp):
            self.assign_lhs = assign_lhs
            self.exp = exp
            super().__init__(children=[self.assign_lhs, self.exp])

        __match_args__ = ("assign_lhs", "exp")

    # ------------------------------- L_Pointer -------------------------------
    class PntrDecl(PicoCNode):
        def __init__(self, deg, array_decl):
            self.deg = deg
            self.array_decl = array_decl
            super().__init__(children=[self.deg, self.array_decl])

        __match_args__ = ("deg", "array_decl")

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
        def __init__(self, identifier, dims):
            self.identifier = identifier
            self.dims = dims
            super().__init__(children=[self.identifier, self.dims])

        __match_args__ = (
            "identifier",
            "dims",
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
        def __init__(self, identifier):
            self.identifier = identifier
            super().__init__(children=[self.identifier])

        __match_args__ = ("identifier",)

    class Struct(PicoCNode):
        def __init__(self, assigns):
            self.assigns = assigns
            super().__init__(children=[self.assigns])

        __match_args__ = ("assigns",)

    class Attr(PicoCNode):
        def __init__(self, ref_loc, attr_identifier):
            self.ref_loc = ref_loc
            self.attr_identifier = attr_identifier
            super().__init__(children=[self.ref_loc, self.attr_identifier])

        __match_args__ = ("ref_loc", "attr_identifier")

    class StructDecl(PicoCNode):
        def __init__(self, identifier, params):
            self.identifier = identifier
            self.params = params
            super().__init__(children=[self.identifier, self.params])

        __match_args__ = ("identifier", "params")

    class Param(PicoCNode):
        def __init__(self, size_qual, identifier):
            self.size_qual = size_qual
            self.identifier = identifier
            super().__init__(children=[self.size_qual, self.identifier])

        __match_args__ = ("size_qual", "identifier")

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
        def __init__(self, identifier, exps):
            self.identifier = identifier
            self.exps = exps
            super().__init__(children=[self.identifier, self.exps])

        __match_args__ = ("identifier", "exps")

    class Return(PicoCNode):
        def __init__(self, exp):
            self.exp = exp
            super().__init__(children=[self.exp])

        __match_args__ = ("exp",)

    class Exp(PicoCNode):
        def __init__(self, call_alloc):
            self.call_alloc = call_alloc
            super().__init__(children=[self.call_alloc])

        __match_args__ = ("call_alloc",)

    class FunDecl(PicoCNode):
        def __init__(self, size_qual, identifier, params):
            self.size_qual = size_qual
            self.identifier = identifier
            self.params = params
            super().__init__(children=[self.size_qual, self.identifier, self.params])

        __match_args__ = ("size_qual", "identifier", "params")

    class FunDef(PicoCNode):
        def __init__(self, size_qual, identifier, params, stmts_blocks):
            self.size_qual = size_qual
            self.identifier = identifier
            self.params = params
            self.stmts_blocks = stmts_blocks
            super().__init__(
                children=[
                    self.size_qual,
                    self.identifier,
                    self.params,
                    self.stmts_blocks,
                ]
            )

        __match_args__ = ("size_qual", "identifier", "params", "stmts_blocks")

    # --------------------------------- L_File --------------------------------
    class File(PicoCNode):
        def __init__(self, name, decls_defs):
            self.name = name
            self.decls_defs = decls_defs
            super().__init__(children=[self.name, self.decls_defs])

        __match_args__ = ("name", "decls_defs")

    # -------------------------------- L_Block --------------------------------
    class Block(PicoCNode):
        def __init__(self, label, stmts_instrs):
            self.label = label
            self.stmts_instrs = stmts_instrs
            self.instrs_before = ""
            self.instrs_after = ""
            super().__init__(
                children=[
                    self.label,
                    self.stmts_instrs,
                    self.instrs_before,
                    self.instrs_after,
                ]
            )

        __match_args__ = ("label", "stmts_instrs")

        def add_info(self, info):
            self.children += N.Num(info)

    class GoTo(PicoCNode):
        def __init__(self, label):
            self.label = label
            super().__init__(children=[self.label])

        __match_args__ = ("label",)
