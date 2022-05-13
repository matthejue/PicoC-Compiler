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

    # ------------------------------- L_Pointer -------------------------------
    class PNTR_PLUS(ASTNode):
        pass

    class PNTR_MINUS(ASTNode):
        pass

    # --------------------------------- L_Fun ---------------------------------
    class Null(ASTNode):
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
        def __init__(self, left_exp, relation, right_exp):
            self.left_exp = left_exp
            self.relation = relation
            self.right_exp = right_exp
            super().__init__(children=[self.left_exp, self.relation, self.right_exp])

        __match_args__ = ("left_exp", "relation", "right_exp")

    class ToBool(ASTNode):
        def __init__(self, exp):
            self.exp = exp
            super().__init__(children=[self.exp])

        __match_args__ = ("exp",)

    # ----------------------------- L_Assign_Alloc ----------------------------
    class Alloc(ASTNode):
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

    class Assign(ASTNode):
        def __init__(self, loc, exp):
            self.loc = loc
            self.exp = exp
            super().__init__(children=[self.loc, self.exp])

        __match_args__ = ("loc", "exp")

    # ------------------------------- L_Pointer -------------------------------
    class PntrDecl(ASTNode):
        def __init__(self, deg, array_decl):
            self.deg = deg
            self.array_decl = array_decl
            super().__init__(children=[self.deg, self.array_decl])

        __match_args__ = ("deg", "array_decl")

    class Ref(ASTNode):
        def __init__(self, ref_loc):
            self.ref_loc = ref_loc
            super().__init__(children=[self.ref_loc])

        __match_args__ = ("ref_loc",)

    class Deref(ASTNode):
        def __init__(self, deref_loc, exp):
            self.deref_loc = deref_loc
            self.exp = exp
            super().__init__(children=[self.deref_loc, self.exp])

        __match_args__ = ("deref_loc", "exp")

    # -------------------------------- L_Array --------------------------------
    class ArrayDecl(ASTNode):
        def __init__(self, identifier, dims):
            self.identifier = identifier
            self.dims = dims
            super().__init__(children=[self.identifier, self.dims])

        __match_args__ = (
            "identifier",
            "dims",
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
        def __init__(self, identifier):
            self.identifier = identifier
            super().__init__(children=[self.identifier])

        __match_args__ = ("identifier",)

    class Struct(ASTNode):
        def __init__(self, assigns):
            self.assigns = assigns
            super().__init__(children=[self.assigns])

        __match_args__ = ("assigns",)

    class Attr(ASTNode):
        def __init__(self, ref_loc, attr_identifier):
            self.ref_loc = ref_loc
            self.attr_identifier = attr_identifier
            super().__init__(children=[self.ref_loc, self.attr_identifier])

        __match_args__ = ("ref_loc", "attr_identifier")

    class StructDecl(ASTNode):
        def __init__(self, identifier, params):
            self.identifier = identifier
            self.params = params
            super().__init__(children=[self.identifier, self.params])

        __match_args__ = ("identifier", "params")

    class Param(ASTNode):
        def __init__(self, size_qual, identifier):
            self.size_qual = size_qual
            self.identifier = identifier
            super().__init__(children=[self.size_qual, self.identifier])

        __match_args__ = ("size_qual", "identifier")

    # ------------------------------- L_If_Else -------------------------------
    class If(ASTNode):
        def __init__(self, exp, stmts):
            self.exp = exp
            self.stmts = stmts
            super().__init__(children=[self.exp, self.stmts])

        __match_args__ = ("exp", "stmts")

    class IfElse(ASTNode):
        def __init__(self, exp, stmts1, stmts2):
            self.exp = exp
            self.stmts1 = stmts1
            self.stmts2 = stmts2
            super().__init__(children=[self.exp, self.stmts1, self.stmts2])

        __match_args__ = ("exp", "stmts1", "stmts2")

    # --------------------------------- L_Loop --------------------------------
    class While(ASTNode):
        def __init__(self, exp, stmts):
            self.exp = exp
            self.stmts = stmts
            super().__init__(children=[self.exp, self.stmts])

        __match_args__ = ("exp", "stmts")

    class DoWhile(ASTNode):
        def __init__(self, exp, stmts):
            self.exp = exp
            self.stmts = stmts
            super().__init__(children=[self.exp, self.stmts])

        __match_args__ = ("exp", "stmts")

    # --------------------------------- L_Fun ---------------------------------
    class Call(ASTNode):
        def __init__(self, identifier, exps):
            self.identifier = identifier
            self.exps = exps
            super().__init__(children=[self.identifier, self.exps])

        __match_args__ = ("identifier", "exps")

    class Return(ASTNode):
        def __init__(self, exp):
            self.exp = exp
            super().__init__(children=[self.exp])

        __match_args__ = ("exp",)

    class Exp(ASTNode):
        def __init__(self, call):
            self.call = call
            super().__init__(children=[self.call])

        __match_args__ = ("call",)

    class FunDecl(ASTNode):
        def __init__(self, size_qual, identifier, params):
            self.size_qual = size_qual
            self.identifier = identifier
            self.params = params
            super().__init__(children=[self.size_qual, self.identifier, self.params])

        __match_args__ = ("size_qual", "identifier", "params")

    class FunDef(ASTNode):
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
    class File(ASTNode):
        def __init__(self, name, decls_defs):
            self.name = name
            self.decls_defs = decls_defs
            super().__init__(children=[self.name, self.decls_defs])

        __match_args__ = ("name", "decls_defs")

    # -------------------------------- L_Block --------------------------------
    class Block(ASTNode):
        def __init__(self, label, stmts):
            self.label = label
            self.stmts = stmts
            super().__init__(children=[self.label, self.stmts])

        __match_args__ = ("label", "stmts")

    class GoTo(ASTNode):
        def __init__(self, label):
            self.label = label
            super().__init__(children=[self.label])

        __match_args__ = ("label",)
