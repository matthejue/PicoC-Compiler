from ast_node import ASTNode
import symbol_table as st
import global_vars


# =========================================================================
# =                              Token Nodes                              =
# =========================================================================
# -------------------------------- L_Arith --------------------------------
class Name(ASTNode):
    # shorter then 'Identifier'
    pass

    def __eq__(self, other):
        return self.val == other.val


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


class DerefOp(ASTNode):
    pass


class RefOp(ASTNode):
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
        super().__init__(visible=[self.left_exp, self.bin_op, self.right_exp])

    __match_args__ = ("left_exp", "bin_op", "right_exp")


class UnOp(ASTNode):
    def __init__(self, un_op, exp):
        self.un_op = un_op
        self.exp = exp
        super().__init__(visible=[self.un_op, self.exp])

    __match_args__ = ("un_op", "exp")


class Exit(ASTNode):
    def __init__(self, num):
        self.num = num
        super().__init__(visible=[self.num])

    __match_args__ = ("num",)


# -------------------------------- L_Logic --------------------------------
class Atom(ASTNode):
    def __init__(self, left_exp, rel, right_exp):
        self.left_exp = left_exp
        self.rel = rel
        self.right_exp = right_exp
        super().__init__(visible=[self.left_exp, self.rel, self.right_exp])

    __match_args__ = ("left_exp", "rel", "right_exp")


class ToBool(ASTNode):
    def __init__(self, exp):
        self.exp = exp
        super().__init__(visible=[self.exp])

    __match_args__ = ("exp",)


# ----------------------------- L_Assign_Alloc ----------------------------
class Alloc(ASTNode):
    def __init__(self, type_qual, datatype, name):
        self.type_qual = type_qual
        self.datatype = datatype
        self.name = name
        # default is LocalVar()
        self.local_var_or_param = Name("local_var")
        super().__init__(
            visible=[
                self.type_qual,
                self.datatype,
                self.name,
            ]
            + ([self.local_var_or_param] if global_vars.args.double_verbose else [])
        )

    __match_args__ = ("type_qual", "datatype", "name", "local_var_or_param")


class Assign(ASTNode):
    def __init__(self, lhs, exp):
        self.lhs = lhs
        self.exp = exp
        super().__init__(visible=[self.lhs, self.exp])

    __match_args__ = ("lhs", "exp")


class Exp(ASTNode):
    def __init__(self, exp):
        self.exp = exp
        self.datatype: ASTNode
        self.error_data: list
        super().__init__(visible=[self.exp])

    __match_args__ = ("exp", "datatype", "error_data")


class Stack(ASTNode):
    def __init__(self, num):
        self.num = num
        super().__init__(visible=[self.num])

    __match_args__ = ("num",)


class Stackframe(ASTNode):
    def __init__(self, num):
        self.num = num
        super().__init__(visible=[self.num])

    __match_args__ = ("num",)


class Global(ASTNode):
    def __init__(self, num):
        self.num = num
        super().__init__(visible=[self.num])

    __match_args__ = ("num",)


class StackMalloc(ASTNode):
    def __init__(self, num):
        self.num = num
        super().__init__(visible=[self.num])

    __match_args__ = ("num",)


# --------------------------------- L_Pntr --------------------------------
class PntrDecl(ASTNode):
    def __init__(self, num, datatype):
        self.num = num
        self.datatype = datatype
        super().__init__(visible=[self.num, self.datatype])

    __match_args__ = ("num", "datatype")


class Ref(ASTNode):
    def __init__(self, exp):
        self.exp = exp
        self.datatype: ASTNode
        self.error_data: list
        super().__init__(visible=[self.exp])

    __match_args__ = ("exp", "datatype", "error_data")


class Deref(ASTNode):
    def __init__(self, lhs, exp):
        self.lhs = lhs
        self.exp = exp
        super().__init__(visible=[self.lhs, self.exp])

    __match_args__ = ("lhs", "exp")


# -------------------------------- L_Array --------------------------------
class ArrayDecl(ASTNode):
    def __init__(self, nums, datatype):
        self.nums = nums
        self.datatype = datatype
        super().__init__(visible=[self.nums, self.datatype])

    __match_args__ = ("nums", "datatype")


class Array(ASTNode):
    def __init__(self, exps):
        self.exps = exps
        self.datatype: ASTNode
        super().__init__(visible=[self.exps])

    __match_args__ = ("exps", "datatype")


class Subscr(ASTNode):
    def __init__(self, exp1, exp2):
        self.exp1 = exp1
        self.exp2 = exp2
        super().__init__(visible=[self.exp1, self.exp2])

    __match_args__ = ("exp1", "exp2")


# -------------------------------- L_Struct -------------------------------
class StructSpec(ASTNode):
    def __init__(self, name):
        self.name = name
        super().__init__(visible=[self.name])

    __match_args__ = ("name",)


class Attr(ASTNode):
    def __init__(self, exp, name):
        self.exp = exp
        self.name = name
        super().__init__(visible=[self.exp, self.name])

    __match_args__ = ("exp", "name")


class Struct(ASTNode):
    def __init__(self, assigns):
        self.assigns = assigns
        self.datatype: ASTNode
        super().__init__(visible=[self.assigns])

    __match_args__ = ("assigns", "datatype")


class StructDecl(ASTNode):
    def __init__(self, name, allocs):
        self.name = name
        self.allocs = allocs
        super().__init__(visible=[self.name, self.allocs])

    __match_args__ = ("name", "allocs")


# ------------------------------- L_If_Else -------------------------------
class If(ASTNode):
    def __init__(self, exp, stmts_goto):
        self.exp = exp
        self.stmts_goto = stmts_goto
        super().__init__(visible=[self.exp, self.stmts_goto])

    __match_args__ = ("exp", "stmts_goto")


class IfElse(ASTNode):
    def __init__(self, exp, stmts_goto1, stmts_goto2):
        self.exp = exp
        self.stmts_goto1 = stmts_goto1
        self.stmts_goto2 = stmts_goto2
        super().__init__(visible=[self.exp, self.stmts_goto1, self.stmts_goto2])

    __match_args__ = ("exp", "stmts_goto1", "stmts_goto2")


# --------------------------------- L_Loop --------------------------------
class While(ASTNode):
    def __init__(self, exp, stmts_goto):
        self.exp = exp
        self.stmts_goto = stmts_goto
        super().__init__(visible=[self.exp, self.stmts_goto])

    __match_args__ = ("exp", "stmts_goto")


class DoWhile(ASTNode):
    def __init__(self, exp, stmts_goto):
        self.exp = exp
        self.stmts_goto = stmts_goto
        super().__init__(visible=[self.exp, self.stmts_goto])

    __match_args__ = ("exp", "stmts_goto")


# --------------------------------- L_Fun ---------------------------------
class Call(ASTNode):
    def __init__(self, name, exps):
        self.name = name
        self.exps = exps
        super().__init__(visible=[self.name, self.exps])

    __match_args__ = ("name", "exps")


class Return(ASTNode):
    def __init__(self, exp=st.Empty()):
        self.exp = exp
        super().__init__(visible=[self.exp])

    __match_args__ = ("exp",)


class FunDecl(ASTNode):
    def __init__(self, datatype, name, allocs):
        self.datatype = datatype
        self.name = name
        self.allocs = allocs
        super().__init__(visible=[self.datatype, self.name, self.allocs])

    __match_args__ = ("datatype", "name", "allocs")


class FunDef(ASTNode):
    def __init__(self, datatype, name, allocs, stmts_blocks):
        self.datatype = datatype
        self.name = name
        self.allocs = allocs
        self.stmts_blocks = stmts_blocks
        super().__init__(
            visible=[
                self.datatype,
                self.name,
                self.allocs,
                self.stmts_blocks,
            ]
        )

    __match_args__ = ("datatype", "name", "allocs", "stmts_blocks")


class NewStackframe(ASTNode):
    def __init__(self, fun_name, goto_after_call):
        self.fun_name = fun_name
        self.goto_after_call = goto_after_call
        super().__init__(visible=[self.fun_name, self.goto_after_call])

    __match_args__ = ("fun_name", "goto_after_call")


class RemoveStackframe(ASTNode):
    pass


# --------------------------------- L_File --------------------------------
class File(ASTNode):
    def __init__(self, name, decls_defs_blocks):
        self.name = name
        self.decls_defs_blocks = decls_defs_blocks
        super().__init__(visible=[self.name, self.decls_defs_blocks])

    __match_args__ = ("name", "decls_defs_blocks")


# -------------------------------- L_Block --------------------------------
class Block(ASTNode):
    def __init__(self, name, stmts_instrs):
        self.name = name
        self.stmts_instrs = stmts_instrs
        self.instrs_before: Num
        self.num_instrs: Num
        self.signature_size: Num
        self.local_vars_size: Num
        super().__init__(
            visible=[
                self.name,
                self.stmts_instrs,
            ]
        )

    __match_args__ = (
        "name",
        "stmts_instrs",
        "instrs_before",
        "num_instrs",
        "signature_size",
        "local_vars_size",
    )


class GoTo(ASTNode):
    def __init__(self, name):
        self.name = name
        super().__init__(visible=[self.name])

    __match_args__ = ("name",)


# ------------------------------- L_Comment -------------------------------
class SingleLineComment:
    def __init__(self, prefix, content):
        self.prefix = prefix
        self.content = content

    def __repr__(self, depth=0):
        return f"\n{' ' * depth}{self.prefix} {self.content}"

    __match_args__ = ("prefix", "content")


class RETIComment(ASTNode):
    def __repr__(self, depth=0):
        return f"\n{' ' * depth}# {self.val}"


# ------------------------------- L_Placeholder -------------------------------
class Placeholder(ASTNode):
    pass
