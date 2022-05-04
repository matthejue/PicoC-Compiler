from ast_node import ASTNode


class N:
    """Nodes"""

    # -------------------------------------------------------------------------
    # -                              Token Nodes                              -
    # -------------------------------------------------------------------------
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
        def __init__(self):
            super().__init__("writeable", tuple())

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

    # ------------------------------- L_If_Else -------------------------------
    class Else(ASTNode):
        pass

    # -------------------------------------------------------------------------
    # -                            Container Nodes                            -
    # -------------------------------------------------------------------------
    # -------------------------------- L_Arith --------------------------------
    class BinOp(ASTNode):
        def __init__(self, left_exp, op, right_exp):
            self.left_exp = left_exp
            self.op = op
            self.right_exp = right_exp
            super().__init__(children=[self.left_exp, self.op, self.right_exp])

        __match_args__ = ("left_exp", "op", "right_exp")

    class UnOp(ASTNode):
        def __init__(self, un_op, opd):
            self.un_op = un_op
            self.opd = opd
            super().__init__(children=[self.un_op, self.opd])

        __match_args__ = ("un_op", "opd")

    # -------------------------------- L_Logic --------------------------------
    class Atom(ASTNode):
        def __init__(self, left_logic_opd, relation, right_logic_opd):
            self.left_logic_opd = left_logic_opd
            self.relation = relation
            self.right_logic_opd = right_logic_opd
            super().__init__(
                children=[self.left_logic_opd, self.relation, self.right_logic_opd]
            )

        __match_args__ = ("left_logic_opd", "relation", "right_logic_opd")

    class ToBool(ASTNode):
        def __init__(self, arith_exp):
            self.arith_exp = arith_exp
            super().__init__(children=[self.arith_exp])

        __match_args__ = ("arith_exp",)

        def __repr__(self):
            return self.to_string_show_node()

    # ----------------------------- L_Assign_Alloc ----------------------------
    class Assign(ASTNode):
        def __init__(self, location, arith_exp_logic_exp):
            self.location = location
            self.arith_exp_logic_exp = arith_exp_logic_exp
            super().__init__(children=[self.location, self.arith_exp_logic_exp])

        __match_args__ = ("location", "arith_exp_logic_exp")

        def __repr__(self):
            if len(self.children) == 2:
                # for the debugger one uses children, else the debugger is
                # going to throw a error if __init__ wasn't executed
                return f"({self.children[0]} = {self.children[1]})"

            return super().__repr__()

    class Alloc(ASTNode):
        def __init__(self, type_qual, datatype, pntr_decl, identifier, array_decl):
            self.type_qual = type_qual
            self.datatype = datatype
            self.pntr_decl = pntr_decl
            self.identifier = identifier
            self.array_decl = array_decl
            super().__init__(
                children=[
                    self.type_qual,
                    self.datatype,
                    self.pntr_decl,
                    self.identifier,
                    self.array_decl,
                ]
            )

        __match_args__ = (
            "type_qual",
            "datatype",
            "pntr_decl",
            "identifier",
            "array_decl",
        )

    # ------------------------------- L_Pointer -------------------------------
    class PntrDecl(ASTNode):
        def __init__(self, pntr_deg):
            self.pntr_deg = pntr_deg
            super().__init__(children=[self.pntr_deg])

        def __repr__(self):
            return f"*({self.pntr_deg.value})"

        __match_args__ = ("pntr_deg",)

    class Ref(ASTNode):
        def __init__(self, location):
            self.location = location
            super().__init__(children=[self.location])

        __match_args__ = ("location",)

    class Deref(ASTNode):
        def __init__(self, location, offset):
            self.location = location
            self.offset = offset
            super().__init__(children=[self.location, self.offset])

        __match_args__ = ("location", "offset")

    # -------------------------------- L_Array --------------------------------
    class ArrayDecl(ASTNode):
        def __init__(self, dims):
            self.dims = dims
            super().__init__(children=[self.dims])

        def __repr__(self):
            if not self.dims:
                return "[](0)"
            subscrs = ""
            for dim in self.dims:
                subscrs += f"[{dim.value}]"

        __match_args__ = ("dims",)

    class Array(ASTNode):
        def __init__(self, entries):
            self.entries = entries
            super().__init__(children=[self.entries])

        __match_args__ = ("datatype", "entries")

    class Subscript(ASTNode):
        def __init__(self, identifier, arith_exp_logic_exp):
            self.identifier = identifier
            self.arith_exp_logic_exp = arith_exp_logic_exp
            super().__init__(children=[self.identifier, self.arith_exp_logic_exp])

        __match_args__ = ("identifier", "arith_exp_logic_exp")

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
        def __init__(self, condition, branch_stmts):
            self.condition = condition
            self.branch_stmts = branch_stmts
            super().__init__(children=[self.condition, self.branch_stmts])

        __match_args__ = ("condition", "branch_stmts")

        def __repr__(self):
            return self.to_string_show_node()

    class IfElse(ASTNode):
        def __init__(self, condition, branch1_stmts, branch2_stmts):
            self.condition = condition
            self.branch1_stmts = branch1_stmts
            self.branch2_stmts = branch2_stmts
            super().__init__(
                children=[self.condition, self.branch1_stmts, self.branch2_stmts]
            )

        __match_args__ = ("condition", "branch1_stmts", "branch2_stmts")

        def __repr__(self):
            return self.to_string_show_node()

    # --------------------------------- L_Loop --------------------------------
    class While(ASTNode):
        def __init__(self, condition, branch_stmts):
            self.condition = condition
            self.branch_stmts = branch_stmts
            super().__init__(children=[self.condition, self.branch_stmts])

        __match_args__ = ("condition", "branch_stmts")

        def __repr__(self):
            return self.to_string_show_node()

    class DoWhile(ASTNode):
        def __init__(self, condition, branch_stmts):
            self.condition = condition
            self.branch_stmts = branch_stmts
            super().__init__(children=[self.condition, self.branch_stmts])

        __match_args__ = ("condition", "branch_stmts")

        def __repr__(self):
            return self.to_string_show_node()

    # --------------------------------- L_Fun ---------------------------------
    class Call(ASTNode):
        def __init__(self, functionname, args):
            self.functionname = functionname
            self.args = args
            super().__init__(children=[self.functionname, self.args])

        __match_args__ = ("functionname", "args")

        def __repr__(self):
            return self.to_string_show_node()

    class Return(ASTNode):
        def __init__(self, arith_exp_logic_exp):
            self.arith_exp_logic_exp = arith_exp_logic_exp
            super().__init__(children=[self.arith_exp_logic_exp])

        __match_args__ = ("arith_exp_logic_exp",)

        def __repr__(self):
            return self.to_string_show_node()

    class Exp(ASTNode):
        def __init__(self, call):
            self.call = call
            super().__init__(children=[self.call])

        __match_args__ = ("call",)

    class FunDef(ASTNode):
        def __init__(self, datatype, fun_name, params, stmts_blocks):
            self.datatype = datatype
            self.fun_name = fun_name
            self.params = params
            self.stmts_blocks = stmts_blocks
            super().__init__(
                children=[self.datatype, self.fun_name, self.params, self.stmts_blocks]
            )

        __match_args__ = ("datatype", "fun_name", "params", "stmts_blocks")

    # --------------------------------- L_File --------------------------------
    class File(ASTNode):
        def __init__(self, filename, main_fun, funs):
            self.filename = filename
            self.main_fun = main_fun
            self.funs = funs
            super().__init__(children=[self.filename, self.main_fun, self.funs])

        __match_args__ = ("filename", "main_fun", "funs")

    # -------------------------------- L_Block --------------------------------
    class Block(ASTNode):
        def __init__(self, blockname, stmsts):
            self.blockname = blockname
            self.stmts = stmsts
            super().__init__(children=[self.blockname, self.stmts])

        __match_args__ = ("blockname", "stmts")

    class Goto(ASTNode):
        def __init__(self, labelname):
            self.labelname = labelname
            super().__init__(children=[self.labelname])

        __match_args__ = ("blockname",)
