from src.ast_node import ASTNode, repr_arg_types, _source_origin_visible
from src import global_vars

# Helper: include datatype fields in visible output only when double-verbose is on.
def _add_if_double_verbose(base_list, datatype):
    show_dt = global_vars.args.double_verbose
    return base_list + ([datatype] if show_dt else [])


# =========================================================================
# =                              Token Nodes                              =
# =========================================================================
# -------------------------------- L_Arith --------------------------------
class Name(ASTNode):
    # shorter then 'Identifier'
    def __init__(self, val, datatype=None):
        self.val = val
        self.datatype = datatype if datatype else Empty()

    @property
    def visible(self):
        return _add_if_double_verbose([self.val], self.datatype)

    def __eq__(self, other):
        return self.val == other.val

    __match_args__ = ("val", "datatype")


class Num(ASTNode):
    def __init__(self, val, datatype=None):
        self.val = val
        self.datatype = datatype if datatype else Empty()

    @property
    def visible(self):
        return _add_if_double_verbose([self.val], self.datatype)

    def __eq__(self, other):
        return self.val == other.val

    __match_args__ = ("val", "datatype")


class Char(ASTNode):
    def __init__(self, val, datatype=None):
        self.val = val
        self.datatype = datatype if datatype else Empty()

    @property
    def visible(self):
        return _add_if_double_verbose([self.val], self.datatype)

    __match_args__ = ("val", "datatype")


class String(ASTNode):
    def __init__(self, val, datatype=None):
        self.val = val
        self.datatype = datatype if datatype else Empty()

    @property
    def visible(self):
        return _add_if_double_verbose([self.val], self.datatype)

    __match_args__ = ("val", "datatype")


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


class Inline(ASTNode):
    def __eq__(self, other):
        return isinstance(other, Inline)


class Static(ASTNode):
    def __eq__(self, other):
        return isinstance(other, Static)


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
    def __init__(self, left_exp, bin_op, right_exp, datatype=None):
        self.left_exp = left_exp
        self.bin_op = bin_op
        self.right_exp = right_exp
        self.datatype = datatype if datatype else Empty()

    @property
    def visible(self):
        return _add_if_double_verbose(
            [self.left_exp, self.bin_op, self.right_exp], self.datatype
        )

    __match_args__ = ("left_exp", "bin_op", "right_exp", "datatype")


class UnOp(ASTNode):
    def __init__(self, un_op, exp, datatype=None):
        self.un_op = un_op
        self.exp = exp
        self.datatype = datatype if datatype else Empty()

    @property
    def visible(self):
        return _add_if_double_verbose([self.un_op, self.exp], self.datatype)

    __match_args__ = ("un_op", "exp", "datatype")


class PostInc(ASTNode):
    def __init__(self, exp, datatype=None):
        self.exp = exp
        self.datatype = datatype if datatype else Empty()

    @property
    def visible(self):
        return _add_if_double_verbose([self.exp], self.datatype)

    __match_args__ = ("exp", "datatype")


class PostDec(ASTNode):
    def __init__(self, exp, datatype=None):
        self.exp = exp
        self.datatype = datatype if datatype else Empty()

    @property
    def visible(self):
        return _add_if_double_verbose([self.exp], self.datatype)

    __match_args__ = ("exp", "datatype")


class Cast(ASTNode):
    def __init__(self, datatype, exp):
        self.datatype = datatype
        self.exp = exp

    @property
    def visible(self):
        return [self.datatype, self.exp]

    __match_args__ = ("datatype", "exp")


class Exit(ASTNode):
    def __init__(self, num):
        self.num = num

    @property
    def visible(self):
        return [self.num]

    __match_args__ = ("num",)


class Asm(ASTNode):
    def __init__(self, code):
        self.code = code

    @property
    def visible(self):
        return [self.code]

    __match_args__ = ("code",)


class SizeOf(ASTNode):
    def __init__(self, exp_datatype, datatype=None):
        self.exp_datatype = exp_datatype
        self.datatype = datatype if datatype else Empty()

    @property
    def visible(self):
        return _add_if_double_verbose([self.exp_datatype], self.datatype)

    __match_args__ = ("exp_datatype", "datatype")

# -------------------------------- L_Logic --------------------------------
class Atom(ASTNode):
    def __init__(self, left_exp, rel, right_exp, datatype=None):
        self.left_exp = left_exp
        self.rel = rel
        self.right_exp = right_exp
        self.datatype = datatype if datatype else Empty()

    @property
    def visible(self):
        return _add_if_double_verbose([self.left_exp, self.rel, self.right_exp], self.datatype)

    __match_args__ = ("left_exp", "rel", "right_exp", "datatype")


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
        self.local_var_or_param = "local_var"

    @property
    def visible(self):
        return [self.type_qual, self.datatype, self.name, self.local_var_or_param]
            

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

    @property
    def visible(self):
        return [self.exp]

    __match_args__ = ("exp",)


class Stack(ASTNode):
    def __init__(self, num, datatype=None):
        self.num = num
        self.datatype = datatype if datatype else Empty()

    @property
    def visible(self):
        return _add_if_double_verbose([self.num], self.datatype)

    __match_args__ = ("num", "datatype")


class Stackframe(ASTNode):
    def __init__(self, num, datatype=None):
        self.num = num
        self.datatype = datatype if datatype else Empty()
        self.symbol_name: str

    @property
    def visible(self):
        return _add_if_double_verbose([self.num], self.datatype)

    __match_args__ = ("num", "datatype")


class Global(ASTNode):
    def __init__(self, num, datatype=None):
        self.num = num
        self.datatype = datatype if datatype else Empty()

    @property
    def visible(self):
        return _add_if_double_verbose([self.num], self.datatype)

    __match_args__ = ("num", "datatype")


# --------------------------------- L_Pntr --------------------------------
class PntrDecl(ASTNode):
    def __init__(self, datatype):
        self.datatype = datatype

    @property
    def visible(self):
        return [self.datatype]

    __match_args__ = ("datatype",)


class Ref(ASTNode):
    def __init__(self, exp):
        self.exp = exp

    @property
    def visible(self):
        return [self.exp]

    __match_args__ = ("exp",)


class Deref(ASTNode):
    def __init__(self, exp, datatype=None):
        self.exp = exp
        self.datatype = datatype if datatype else Empty()

    @property
    def visible(self):
        return _add_if_double_verbose([self.exp], self.datatype)

    __match_args__ = ("exp", "datatype")


# -------------------------------- L_Array --------------------------------
class ArrayDecl(ASTNode):
    def __init__(self, const_exp, datatype):
        self.const_exp = const_exp
        self.datatype = datatype

    @property
    def visible(self):
        return [self.const_exp, self.datatype]

    __match_args__ = ("const_exp", "datatype")


class Array(ASTNode):
    def __init__(self, exps):
        self.exps = exps
        self.datatype: ASTNode = Empty()

    @property
    def visible(self):
        return [self.exps, self.datatype]

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
    def __init__(self, exp, name, datatype=None):
        self.exp = exp
        self.name = name
        self.datatype = datatype if datatype else Empty()

    @property
    def visible(self):
        return _add_if_double_verbose([self.exp, self.name], self.datatype)

    __match_args__ = ("exp", "name", "datatype")

class InitPair(ASTNode):
    def __init__(self, lhs, exp):
        self.lhs = lhs
        self.exp = exp

    @property
    def visible(self):
        return [self.lhs, self.exp]

    __match_args__ = ("lhs", "exp")

class Struct(ASTNode):
    def __init__(self, assigns):
        self.assigns = assigns
        self.datatype: ASTNode = Empty()

    @property
    def visible(self):
        return [self.assigns, self.datatype]

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
    def __init__(self, name, exps, datatype=None):
        self.name = name
        self.exps = exps
        self.datatype = datatype if datatype else Empty()

    @property
    def visible(self):
        return _add_if_double_verbose([self.name, self.exps], self.datatype)

    __match_args__ = ("name", "exps", "datatype")


class FunRef(ASTNode):
    def __init__(self, name, datatype=None):
        self.name = name
        self.datatype = datatype if datatype else Empty()

    @property
    def visible(self):
        return _add_if_double_verbose([self.name], self.datatype)

    __match_args__ = ("name", "datatype")


class Empty(ASTNode):
    pass


class VariadicParam(ASTNode):
    pass


class ParamDecl(ASTNode):
    def __init__(self, type_qual, datatype):
        self.type_qual = type_qual
        self.datatype = datatype

    @property
    def visible(self):
        return [self.type_qual, self.datatype]

    __match_args__ = ("type_qual", "datatype")


class Return(ASTNode):
    def __init__(self, exp=Empty()):
        self.exp = exp

    @property
    def visible(self):
        return [self.exp]

    __match_args__ = ("exp",)


class FunDecl(ASTNode):
    def __init__(self, storage_class_specifiers, datatype, name, allocs):
        self.storage_class_specifiers = storage_class_specifiers
        self.datatype = datatype
        self.name = name
        self.allocs = allocs

    @property
    def visible(self):
        return [self.storage_class_specifiers, self.datatype, self.name, self.allocs]

    __match_args__ = ("storage_class_specifiers", "datatype", "name", "allocs")


class FunPtrDecl(ASTNode):
    def __init__(self, datatype, params):
        self.datatype = datatype  # return datatype
        self.params = params

    @property
    def visible(self):
        return [self.datatype, self.params]

    __match_args__ = ("datatype", "params")


class FunDef(ASTNode):
    def __init__(self, storage_class_specifiers, datatype, name, allocs, stmts_blocks):
        self.storage_class_specifiers = storage_class_specifiers
        self.datatype = datatype
        self.name = name
        self.allocs = allocs
        self.stmts_blocks = stmts_blocks

    @property
    def visible(self):
        return [
            self.storage_class_specifiers,
            self.datatype,
            self.name,
            self.allocs,
            self.stmts_blocks,
        ]

    __match_args__ = ("storage_class_specifiers", "datatype", "name", "allocs", "stmts_blocks")


class NewStackframe(ASTNode):
    def __init__(self, local_var_count):
        self.local_var_count = local_var_count

    @property
    def visible(self):
        return [self.local_var_count]

    __match_args__ = ("local_var_count",)


class SaveReturnAddress(ASTNode):
    def __init__(self, label=Empty()):
        self.label = label

    @property
    def visible(self):
        return [] if isinstance(self.label, Empty) else [self.label]

    __match_args__ = ("label",)


class RestoreReturnAddress(ASTNode):
    pass


class RestoreStackframe(ASTNode):
    pass

# --------------------------------- L_File --------------------------------
class File(ASTNode):
    def __init__(self, name, decls_defs_blocks_instrs):
        self.name = name
        self.decls_defs_blocks_instrs = decls_defs_blocks_instrs

    @property
    def visible(self):
        return [self.name, self.decls_defs_blocks_instrs]

    def __repr__(self):
        entries_str = ""
        for entry in self.decls_defs_blocks_instrs:
            entries_str += entry.__repr__(0)
        return entries_str

    __match_args__ = ("name", "decls_defs_blocks_instrs")


class Section(ASTNode):
    def __init__(self, name, entries):
        self.name = name
        self.entries = entries

    @property
    def visible(self):
        return [self.name, self.entries]

    def __repr__(self, depth=0):
        acc = f"\n{' ' * (depth + 2)}.{self.name}"
        for entry in self.entries:
            if isinstance(entry, Block):
                acc += entry.__repr__(depth)
            else:
                acc += entry.__repr__(depth + 2)
        return acc

    __match_args__ = ("name", "entries")


# -------------------------------- L_Block --------------------------------
class Block(ASTNode):
    def __init__(self, name, stmts_instrs):
        self.name = name
        self.stmts_instrs = stmts_instrs
        self.scope: str
        self.instrs_before: Num = Num(-1)
        self.num_instrs: Num = Num(-1)
        self.block_idx: int

    @property
    def visible(self):
        return [self.name, self.stmts_instrs] + (
            [self.scope, self.instrs_before, self.num_instrs]
            if global_vars.args.double_verbose
            else []
        )

    def __repr__(self, depth=0):
        acc = f"\n{depth * ' '}{self.name}:" + repr_arg_types(
            0, self.stmts_instrs, depth, "", is_block=True
        )
        origin_visible = _source_origin_visible(self)
        if origin_visible is not None:
            acc = repr_arg_types(1, origin_visible, depth, acc, is_block=True)
        return acc

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


# ---------------------------------- L_Misc -----------------------------------
class SingleLineComment(ASTNode):
    def __init__(self, prefix, content):
        self.prefix = prefix
        self.content = content

    @property
    def visible(self):
        return [self.prefix, self.content]

    def __repr__(self, depth=0):
        acc = f"\n{' ' * depth}{self.prefix} {self.content}"
        origin_visible = _source_origin_visible(self)
        if origin_visible is not None:
            acc += f", '{origin_visible}'"
        return acc

    __match_args__ = ("prefix", "content")

class Debug(ASTNode):
    pass

class Error(ASTNode):
    pass

# ------------------------------- L_Placeholder -------------------------------
class Placeholder(ASTNode):
    pass
