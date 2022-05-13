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
        def __init__(self, un_op, opd):
            self.un_op = un_op
            self.opd = opd
            super().__init__(children=[self.un_op, self.opd])

        __match_args__ = ("un_op", "opd")

    # -------------------------------- L_Logic --------------------------------
    class Atom(ASTNode):
        def __init__(self, left_arith_exp, relation, right_arith_exp):
            self.left_arith_exp = left_arith_exp
            self.relation = relation
            self.right_arith_exp = right_arith_exp
            super().__init__(
                children=[self.left_arith_exp, self.relation, self.right_arith_exp]
            )

        __match_args__ = ("left_arith_exp", "relation", "right_arith_exp")

    class ToBool(ASTNode):
        def __init__(self, arith_exp):
            self.arith_exp = arith_exp
            super().__init__(children=[self.arith_exp])

        __match_args__ = ("arith_exp",)

    # ----------------------------- L_Assign_Alloc ----------------------------
    class Assign(ASTNode):
        def __init__(self, location, logic_exp):
            self.location = location
            self.logic_exp = logic_exp
            super().__init__(children=[self.location, self.logic_exp])

        __match_args__ = ("location", "logic_exp")

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

    # ------------------------------- L_Pointer -------------------------------
    class PntrDecl(ASTNode):
        def __init__(self, deg, array_decl):
            self.deg = deg
            self.array_decl = array_decl
            super().__init__(children=[self.deg, self.array_decl])

        __match_args__ = ("deg", "array_decl")

    class Ref(ASTNode):
        def __init__(self, location):
            self.location = location
            super().__init__(children=[self.location])

        __match_args__ = ("location",)

    class Deref(ASTNode):
        def __init__(self, location, logic_exp):
            self.location = location
            self.logic_exp = logic_exp
            super().__init__(children=[self.location, self.logic_exp])

        __match_args__ = ("location", "logic_exp")

    # -------------------------------- L_Array --------------------------------
    class ArrayDecl(ASTNode):
        def __init__(self, name_pntr_decl, dims):
            self.name_pntr_decl = name_pntr_decl
            self.dims = dims
            super().__init__(children=[self.name_pntr_decl, self.dims])

        __match_args__ = (
            "pntr_decl",
            "dims",
        )

    class Array(ASTNode):
        def __init__(self, logic_exps):
            self.logic_exps = logic_exps
            super().__init__(children=[self.logic_exps])

        __match_args__ = ("datatype", "logic_exps")

    class Subscr(ASTNode):
        def __init__(self, subscr_opd, logic_exp):
            self.subscr_opd = subscr_opd
            self.logic_exp = logic_exp
            super().__init__(children=[self.subscr_opd, self.logic_exp])

        __match_args__ = ("subscr_opd", "offset")

    # -------------------------------- L_Struct -------------------------------
    class StructSpec(ASTNode):
        def __init__(self, identifier):
            self.identifier = identifier
            super().__init__(children=[self.identifier])

        __match_args__ = ("identifier",)

    class Struct(ASTNode):
        def __init__(self, assignments):
            self.assignments = assignments
            super().__init__(children=[self.assignments])

        __match_args__ = ("assignments",)

    class Attr(ASTNode):
        def __init__(self, array_identifier, attribute_identifier):
            self.array_identifier = array_identifier
            self.attribute_identifier = attribute_identifier
            super().__init__(
                children=[self.array_identifier, self.attribute_identifier]
            )

        __match_args__ = ("array_identifier", "attribute_identifier")

    class StructDecl(ASTNode):
        def __init__(self, struct_identifier, params):
            self.struct_identifier = struct_identifier
            self.params = params
            super().__init__(children=[self.struct_identifier, self.params])

        __match_args__ = ("struct_identifier", "params")

    class Param(ASTNode):
        def __init__(self, datatype, identifier):
            self.datatype = datatype
            self.identifier = identifier
            super().__init__(children=[self.datatype, self.identifier])

        __match_args__ = ("datatype", "identifier")

    # ------------------------------- L_If_Else -------------------------------
    class If(ASTNode):
        def __init__(self, condition, stmts):
            self.condition = condition
            self.stmts = stmts
            super().__init__(children=[self.condition, self.stmts])

        __match_args__ = ("condition", "branch_stmts")

    class IfElse(ASTNode):
        def __init__(self, condition, stmts1, stmts2):
            self.condition = condition
            self.stmts1 = stmts1
            self.stmts2 = stmts2
            super().__init__(children=[self.condition, self.stmts1, self.stmts2])

        __match_args__ = ("condition", "stmts1", "stmts2")

    # --------------------------------- L_Loop --------------------------------
    class While(ASTNode):
        def __init__(self, condition, stmts):
            self.condition = condition
            self.stmts = stmts
            super().__init__(children=[self.condition, self.stmts])

        __match_args__ = ("condition", "stmts")

    class DoWhile(ASTNode):
        def __init__(self, condition, stmts):
            self.condition = condition
            self.stmts = stmts
            super().__init__(children=[self.condition, self.stmts])

        __match_args__ = ("condition", "stmts")

    # --------------------------------- L_Fun ---------------------------------
    class Call(ASTNode):
        def __init__(self, name, logic_exps):
            self.name = name
            self.logic_exps = logic_exps
            super().__init__(children=[self.name, self.logic_exps])

        __match_args__ = ("name", "args")

    class Return(ASTNode):
        def __init__(self, logic_exp):
            self.logic_exp = logic_exp
            super().__init__(children=[self.logic_exp])

        __match_args__ = ("logic_exp",)

    class Exp(ASTNode):
        def __init__(self, call):
            self.call = call
            super().__init__(children=[self.call])

        __match_args__ = ("call",)

    class FunDecl(ASTNode):
        def __init__(self, datatype, fun_name, params):
            self.datatype = datatype
            self.fun_name = fun_name
            self.params = params
            super().__init__(children=[self.datatype, self.fun_name, self.params])

        __match_args__ = ("datatype", "fun_name", "params")

    class FunDef(ASTNode):
        def __init__(self, size_qual, fun_name, params, stmts_blocks):
            self.size_qual = size_qual
            self.fun_name = fun_name
            self.params = params
            self.stmts_blocks = stmts_blocks
            super().__init__(
                children=[self.size_qual, self.fun_name, self.params, self.stmts_blocks]
            )

        __match_args__ = ("size_qual", "fun_name", "params", "stmts_blocks")

    # --------------------------------- L_File --------------------------------
    class File(ASTNode):
        def __init__(self, name, decls_and_defs):
            self.name = name
            self.decls_and_defs = decls_and_defs
            super().__init__(children=[self.name, self.decls_and_defs])

        __match_args__ = ("name", "decls_and_defs")

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
