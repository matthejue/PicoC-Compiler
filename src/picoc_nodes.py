from src.ast_node import ASTNode, repr_arg_types
from src import global_vars


# =========================================================================
# =                              Token Nodes                              =
# =========================================================================
# -------------------------------- L_Arith --------------------------------
class Name(ASTNode):
    # shorter then 'Identifier'
    def __init__(self, val):
        self.val = val

    @property
    def visible(self):
        return [self.val]

    def __eq__(self, other):
        return self.val == other.val

    __match_args__ = ("val",)


class Num(ASTNode):
    def __init__(self, val):
        self.val = val

    @property
    def visible(self):
        return [self.val]

    def __eq__(self, other):
        return self.val == other.val

    __match_args__ = ("val",)


class Char(ASTNode):
    def __init__(self, val):
        self.val = val

    @property
    def visible(self):
        return [self.val]

    __match_args__ = ("val",)


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

    def __repr__(self, depth=0):
        return f"\n{' ' * depth}IntType()"


class CharType(ASTNode):
    pass

    def __repr__(self, depth=0):
        return f"\n{' ' * depth}CharType()"


class VoidType(ASTNode):
    pass

    def __repr__(self, depth=0):
        return f"\n{' ' * depth}VoidType()"


# =========================================================================
# =                            Container Nodes                            =
# =========================================================================
# -------------------------------- L_Arith --------------------------------
class BinOp(ASTNode):
    def __init__(self, left_exp, bin_op, right_exp):
        self.left_exp = left_exp
        self.bin_op = bin_op
        self.right_exp = right_exp

    @property
    def visible(self):
        return [self.left_exp, self.bin_op, self.right_exp]

    __match_args__ = ("left_exp", "bin_op", "right_exp")


class UnOp(ASTNode):
    def __init__(self, un_op, exp):
        self.un_op = un_op
        self.exp = exp

    @property
    def visible(self):
        return [self.un_op, self.exp]

    __match_args__ = ("un_op", "exp")


class Exit(ASTNode):
    def __init__(self, num):
        self.num = num

    @property
    def visible(self):
        return [self.num]

    __match_args__ = ("num",)


# -------------------------------- L_Logic --------------------------------
class Atom(ASTNode):
    def __init__(self, left_exp, rel, right_exp):
        self.left_exp = left_exp
        self.rel = rel
        self.right_exp = right_exp

    @property
    def visible(self):
        return [self.left_exp, self.rel, self.right_exp]

    __match_args__ = ("left_exp", "rel", "right_exp")


class ToBool(ASTNode):
    def __init__(self, exp):
        self.exp = exp

    @property
    def visible(self):
        return [self.exp]

    __match_args__ = ("exp",)


# ----------------------------- L_Assign_Alloc ----------------------------
class Alloc(ASTNode):
    def __init__(self, type_qual, datatype, name):
        self.type_qual = type_qual
        self.datatype = datatype
        self.name = name
        # default is LocalVar()
        self.local_var_or_param = Name("local_var")

    @property
    def visible(self):
        return [
            self.type_qual,
            self.datatype,
            self.name,
        ] + ([self.local_var_or_param] if global_vars.args.double_verbose else [])

    __match_args__ = ("type_qual", "datatype", "name", "local_var_or_param")


class Assign(ASTNode):
    def __init__(self, lhs, exp):
        self.lhs = lhs
        self.exp = exp

    @property
    def visible(self):
        return [self.lhs, self.exp]

    __match_args__ = ("lhs", "exp")


class Exp(ASTNode):
    def __init__(self, exp):
        self.exp = exp
        self.datatype = Empty()

    @property
    def visible(self):
        return [self.exp] + ([self.datatype] if global_vars.args.double_verbose else [])

    __match_args__ = ("exp", "datatype")


class Stack(ASTNode):
    def __init__(self, num):
        self.num = num

    @property
    def visible(self):
        return [self.num]

    __match_args__ = ("num",)


class Stackframe(ASTNode):
    def __init__(self, num):
        self.num = num

    @property
    def visible(self):
        return [self.num]

    __match_args__ = ("num",)


class Global(ASTNode):
    def __init__(self, num):
        self.num = num

    @property
    def visible(self):
        return [self.num]

    __match_args__ = ("num",)


class StackMalloc(ASTNode):
    def __init__(self, num):
        self.num = num

    @property
    def visible(self):
        return [self.num]

    __match_args__ = ("num",)


# --------------------------------- L_Pntr --------------------------------
class PntrDecl(ASTNode):
    def __init__(self, num, datatype):
        self.num = num
        self.datatype = datatype

    @property
    def visible(self):
        return [self.num, self.datatype]

    __match_args__ = ("num", "datatype")


class Ref(ASTNode):
    def __init__(self, exp):
        self.exp = exp
        self.datatype: ASTNode

    @property
    def visible(self):
        return [self.exp]

    __match_args__ = ("exp", "datatype")


class Deref(ASTNode):
    def __init__(self, exp1, exp2):
        self.exp1 = exp1
        self.exp2 = exp2

    @property
    def visible(self):
        return [self.exp1, self.exp2]

    __match_args__ = ("exp1", "exp2")


# -------------------------------- L_Array --------------------------------
class ArrayDecl(ASTNode):
    def __init__(self, nums, datatype):
        self.nums = nums
        self.datatype = datatype

    @property
    def visible(self):
        return [self.nums, self.datatype]

    __match_args__ = ("nums", "datatype")


class Array(ASTNode):
    def __init__(self, exps):
        self.exps = exps
        self.datatype: ASTNode

    @property
    def visible(self):
        return [self.exps]

    __match_args__ = ("exps", "datatype")


class Subscr(ASTNode):
    def __init__(self, exp1, exp2):
        self.exp1 = exp1
        self.exp2 = exp2

    @property
    def visible(self):
        return [self.exp1, self.exp2]

    __match_args__ = ("exp1", "exp2")


# -------------------------------- L_Struct -------------------------------
class StructSpec(ASTNode):
    def __init__(self, name):
        self.name = name

    @property
    def visible(self):
        return [self.name]

    __match_args__ = ("name",)


class Attr(ASTNode):
    def __init__(self, exp, name):
        self.exp = exp
        self.name = name

    @property
    def visible(self):
        return [self.exp, self.name]

    __match_args__ = ("exp", "name")


class Struct(ASTNode):
    def __init__(self, assigns):
        self.assigns = assigns
        self.datatype: ASTNode

    @property
    def visible(self):
        return [self.assigns]

    __match_args__ = ("assigns", "datatype")


class StructDecl(ASTNode):
    def __init__(self, name, allocs):
        self.name = name
        self.allocs = allocs

    @property
    def visible(self):
        return [self.name, self.allocs]

    __match_args__ = ("name", "allocs")


# ------------------------------- L_If_Else -------------------------------
class If(ASTNode):
    def __init__(self, exp, stmts):
        self.exp = exp
        self.stmts = stmts

    @property
    def visible(self):
        return [self.exp, self.stmts]

    __match_args__ = ("exp", "stmts")


class IfElse(ASTNode):
    def __init__(self, exp, stmts1, stmts2):
        self.exp = exp
        self.stmts1 = stmts1
        self.stmts2 = stmts2

    @property
    def visible(self):
        return [self.exp, self.stmts1, self.stmts2]

    __match_args__ = ("exp", "stmts1", "stmts2")


# --------------------------------- L_Loop --------------------------------
class While(ASTNode):
    def __init__(self, exp, stmts):
        self.exp = exp
        self.stmts = stmts

    @property
    def visible(self):
        return [self.exp, self.stmts]

    __match_args__ = ("exp", "stmts")


class DoWhile(ASTNode):
    def __init__(self, exp, stmts):
        self.exp = exp
        self.stmts = stmts

    @property
    def visible(self):
        return [self.exp, self.stmts]

    __match_args__ = ("exp", "stmts")


# --------------------------------- L_Fun ---------------------------------
class Call(ASTNode):
    def __init__(self, name, exps):
        self.name = name
        self.exps = exps

    @property
    def visible(self):
        return [self.name, self.exps]

    __match_args__ = ("name", "exps")


class Empty(ASTNode):
    pass


class Return(ASTNode):
    def __init__(self, exp=Empty()):
        self.exp = exp

    @property
    def visible(self):
        return [self.exp]

    __match_args__ = ("exp",)


class FunDecl(ASTNode):
    def __init__(self, datatype, name, allocs):
        self.datatype = datatype
        self.name = name
        self.allocs = allocs

    @property
    def visible(self):
        return [self.datatype, self.name, self.allocs]

    __match_args__ = ("datatype", "name", "allocs")


class FunDef(ASTNode):
    def __init__(self, datatype, name, allocs, stmts_blocks):
        self.datatype = datatype
        self.name = name
        self.allocs = allocs
        self.stmts_blocks = stmts_blocks

    @property
    def visible(self):
        return [self.datatype, self.name, self.allocs, self.stmts_blocks]

    __match_args__ = ("datatype", "name", "allocs", "stmts_blocks")


class NewStackframe(ASTNode):
    def __init__(self, fun_name):
        self.fun_name = fun_name

    @property
    def visible(self):
        return [self.fun_name]

    __match_args__ = ("fun_name",)


class RemoveStackframe(ASTNode):
    pass


# --------------------------------- L_File --------------------------------
class File(ASTNode):
    def __init__(self, name, decls_defs_blocks_instrs):
        self.name = name
        self.decls_defs_blocks_instrs = decls_defs_blocks_instrs

    @property
    def visible(self):
        return [self.name, self.decls_defs_blocks_instrs]

    def __repr__(self, incl_filenode=False):
        if not self.decls_defs_blocks_instrs:
            return ""
        if incl_filenode:
            return super().__repr__(is_file=True)
        else:
            instrs_str = str(self.decls_defs_blocks_instrs[0])
            for instr in self.decls_defs_blocks_instrs[1:]:
                instrs_str += str(instr)
            return instrs_str

    __match_args__ = ("name", "decls_defs_blocks_instrs")


# -------------------------------- L_Block --------------------------------
class Block(ASTNode):
    def __init__(self, name, stmts_instrs):
        self.name = name
        self.stmts_instrs = stmts_instrs
        self.instrs_before: Num = Num(-1)
        self.num_instrs: Num = Num(-1)
        self.param_size: Num
        self.local_vars_size: Num

    @property
    def visible(self):
        return [self.name, self.stmts_instrs] + (
            [self.instrs_before, self.num_instrs]
            if global_vars.args.double_verbose
            else []
        )

    def __repr__(self, depth=0):
        return f"\n{depth * ' '}{self.name}:" + repr_arg_types(
            0, self.stmts_instrs, depth, "", is_block=True
        )

    __match_args__ = (
        "name",
        "stmts_instrs",
        "instrs_before",
        "num_instrs",
        "param_size",
        "local_vars_size",
    )


class GoTo(ASTNode):
    def __init__(self, name):
        self.name: Name = name

    @property
    def visible(self):
        return [self.name]

    __match_args__ = ("name",)


# ------------------------------- L_Comment -------------------------------
class SingleLineComment(ASTNode):
    def __init__(self, prefix, content):
        self.prefix = prefix
        self.content = content

    @property
    def visible(self):
        return [self.prefix, self.content]

    def __repr__(self, depth=0):
        return f"\n{' ' * depth}{self.prefix} {self.content}"

    __match_args__ = ("prefix", "content")


# ------------------------------- L_Placeholder -------------------------------
class Placeholder(ASTNode):
    pass
