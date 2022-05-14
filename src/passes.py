from picoc_nodes import N as PN
from reti_nodes import N as RN


class Passes:
    def __init__(self):
        self.block_id = 0
        self.name_id = 0
        self.all_blocks = dict()

    # =========================================================================
    # =                           PicoC -> PicoC_mon                          =
    # =========================================================================

    def _generate_name(self, name: str) -> PN.Name:
        self.name_id += 1
        return PN.Name(f"{name}.{self.name_id}")

    def _make_assigns(self, tmps):
        return [PN.Assign(lhs, rhs) for lhs, rhs in tmps]

    def _picoc_to_picoc_mon_exp(self, exp, atomic):
        match exp:
            case PN.BinOp(left_exp, bin_op, right_exp):
                atom1, tmps1 = self._picoc_to_picoc_mon_exp(left_exp, atomic=True)
                atom2, tmps2 = self._picoc_to_picoc_mon_exp(right_exp, atomic=True)
                if atomic:
                    new_tmp = self._generate_name("tmp")
                    return (
                        new_tmp,
                        tmps1 + tmps2 + [(new_tmp, PN.BinOp(atom1, bin_op, atom2))],
                    )
                return (PN.BinOp(atom1, bin_op, atom2), tmps1 + tmps2)
            case PN.UnOp(un_op, exp):
                atom, tmps = self._picoc_to_picoc_mon_exp(exp, atomic=True)
                if atomic:
                    new_tmp = self._generate_name("tmp")
                    return (
                        new_tmp,
                        tmps + [(new_tmp, PN.UnOp(un_op, atom))],
                    )
                return (PN.UnOp(un_op, atom), tmps)
            case PN.Atom(left_exp, relation, right_exp):
                atom1, tmps1 = self._picoc_to_picoc_mon_exp(left_exp, atomic=True)
                atom2, tmps2 = self._picoc_to_picoc_mon_exp(right_exp, atomic=True)
                if atomic:
                    new_tmp = self._generate_name("tmp")
                    return (
                        new_tmp,
                        tmps1 + tmps2 + [(new_tmp, PN.Atom(atom1, relation, atom2))],
                    )
                return (PN.Atom(atom1, relation, atom2), tmps1 + tmps2)
            case PN.ToBool(exp):
                atom, tmps = self._picoc_to_picoc_mon_exp(exp, atomic=True)
                if atomic:
                    new_tmp = self._generate_name("tmp")
                    return (new_tmp, tmps + [(new_tmp, PN.ToBool(atom))])
                return (PN.ToBool(atom), tmps)
            case PN.Deref(deref_loc, exp):
                atom1, tmps1 = self._picoc_to_picoc_mon_exp(deref_loc, atomic=True)
                atom2, tmps2 = self._picoc_to_picoc_mon_exp(exp, atomic=True)
                if atomic:
                    new_tmp = self._generate_name("tmp")
                    return (
                        new_tmp,
                        tmps1 + tmps2 + [(new_tmp, PN.Deref(atom1, atom2))],
                    )
                return (PN.Deref(atom1, atom2), tmps1 + tmps2)
            case PN.Ref(ref_loc):
                atom, tmps = self._picoc_to_picoc_mon_exp(ref_loc, atomic=True)
                if atomic:
                    new_tmp = self._generate_name("tmp")
                    return (
                        new_tmp,
                        tmps + [(new_tmp, PN.Ref(atom))],
                    )
                return (PN.Ref(atom), tmps)
            case PN.Subscr(deref_loc, exp):
                atom1, tmps1 = self._picoc_to_picoc_mon_exp(deref_loc, atomic=True)
                atom2, tmps2 = self._picoc_to_picoc_mon_exp(exp, atomic=True)
                if atomic:
                    new_tmp = self._generate_name("tmp")
                    return (
                        new_tmp,
                        tmps1 + tmps2 + [(new_tmp, PN.Subscr(atom1, atom2))],
                    )
                return (PN.Subscr(atom1, atom2), tmps1 + tmps2)
            case PN.Attr(ref_loc, attr_identifier):
                atom, tmps = self._picoc_to_picoc_mon_exp(ref_loc, atomic=True)
                if atomic:
                    new_tmp = self._generate_name("tmp")
                    return (
                        new_tmp,
                        tmps + [(new_tmp, PN.Attr(atom, attr_identifier))],
                    )
                return (PN.Attr(atom, attr_identifier), tmps)
            case PN.Call(identifier, exps):
                atoms, tmps = [], []
                atom_tmps = []
                for exp in exps:
                    atom_tmps += self._picoc_to_picoc_mon_exp(exp, atomic=True)
                    atoms += [atom_tmps[0]]
                    tmps += atom_tmps[1]
                if atomic:
                    new_tmp = self._generate_name("tmp")
                    return (
                        new_tmp,
                        tmps + [(new_tmp, PN.Call(identifier, atoms))],
                    )
                return (PN.Call(identifier, atoms), tmps)
            case _:
                return (exp, [])

    def _picoc_to_picoc_mon_stmt(self, stmt):
        match stmt:
            case PN.Assign(loc, exp):
                atom1, tmps1 = self._picoc_to_picoc_mon_exp(loc, atomic=False)
                atom2, tmps2 = self._picoc_to_picoc_mon_exp(exp, atomic=False)
                return (
                    self._make_assigns(tmps1)
                    + self._make_assigns(tmps2)
                    + [PN.Assign(atom1, atom2)]
                )
            case PN.Assign(
                PN.Alloc(type_qual, size_qual, pntr_decl), PN.Struct(assigns)
            ):
                atoms, tmps = [], []
                assigns_mon = []
                for assign in assigns:
                    match assign:
                        case PN.Assign(attr, exp):
                            atom_tmps = self._picoc_to_picoc_mon_exp(exp, atomic=False)
                            tmps += atom_tmps[1]
                            assigns_mon += [PN.Assign(attr, atom_tmps[0])]
                return self._make_assigns(tmps) + [
                    PN.Assign(
                        PN.Alloc(type_qual, size_qual, pntr_decl),
                        PN.Struct(assigns_mon),
                    )
                ]
            case PN.Assign(PN.Alloc(type_qual, size_qual, pntr_decl), PN.Array(exps)):
                atoms, tmps = [], []
                for exp in exps:
                    atom_tmps = self._picoc_to_picoc_mon_stmt(exp)
                    atoms += [atom_tmps[0]]
                    tmps += atom_tmps[1]
                return self._make_assigns(tmps) + [
                    PN.Assign(
                        PN.Alloc(type_qual, size_qual, pntr_decl), PN.Array(atoms)
                    )
                ]
            case PN.If(exp, stmts):
                atom, tmps = self._picoc_to_picoc_mon_exp(exp, atomic=False)
                stmts_mon = []
                for stmt in stmts:
                    stmts_mon += self._picoc_to_picoc_mon_stmt(stmt)
                return self._make_assigns(tmps) + [PN.If(atom, stmts_mon)]
            case PN.IfElse(exp, stmts1, stmts2):
                atom, tmps = self._picoc_to_picoc_mon_exp(exp, atomic=False)
                stmts1_mon = []
                for stmt1 in stmts1:
                    stmts1_mon += self._picoc_to_picoc_mon_stmt(stmt1)
                stmts2_mon = []
                for stmt2 in stmts2:
                    stmts2_mon += self._picoc_to_picoc_mon_stmt(stmt2)
                return self._make_assigns(tmps) + [
                    PN.IfElse(atom, stmts1_mon, stmts2_mon)
                ]
            case PN.While(exp, stmts):
                atom, tmps = self._picoc_to_picoc_mon_exp(exp, atomic=False)
                stmts_mon = []
                for stmt in stmts:
                    stmts_mon += self._picoc_to_picoc_mon_stmt(stmt)
                return self._make_assigns(tmps) + [PN.While(atom, stmts_mon)]
            case PN.DoWhile(exp, stmts):
                atom, tmps = self._picoc_to_picoc_mon_exp(exp, atomic=False)
                stmts_mon = []
                for stmt in stmts:
                    stmts_mon += self._picoc_to_picoc_mon_stmt(stmt)
                return self._make_assigns(tmps) + [PN.DoWhile(atom, stmts_mon)]
            case PN.Exp(call):
                atom, tmps = self._picoc_to_picoc_mon_exp(call, atomic=False)
                return self._make_assigns(tmps) + [PN.Exp(atom)]
            case PN.Return(exp):
                atom, tmps = self._picoc_to_picoc_mon_exp(exp, atomic=False)
                return self._make_assigns(tmps) + [PN.Return(atom)]
            case _:
                return [stmt]

    def _picoc_to_picoc_mon_def(self, decl_def):
        match decl_def:
            case PN.FunDef(size_qual, identifier, params, stmts):
                stmts_mon = []
                for stmt in stmts:
                    stmts_mon += self._picoc_to_picoc_mon_stmt(stmt)
                return PN.FunDef(size_qual, identifier, params, stmts_mon)
            case _:
                return decl_def

    def picoc_to_picoc_mon(self, file: PN.File):
        match file:
            case PN.File(name, decls_defs):
                decls_defs_mon = []
                for decl_def in decls_defs:
                    decls_defs_mon += [self._picoc_to_picoc_mon_def(decl_def)]
        return PN.File(name, decls_defs_mon)

    # =========================================================================
    # =                       PicoC_mon -> PicoC_Blocks                       =
    # =========================================================================

    def _create_block(self, labelbase, stmts, blocks):
        label = f"{labelbase}.{self.block_id}"
        new_block = PN.Block(PN.Name(label), stmts)
        blocks[label] = new_block
        self.block_id += 1
        return PN.GoTo(PN.Name(label))

    def _picoc_mon_to_picoc_block_stmt(self, stmt, processed_stmts, blocks):
        match stmt:
            case PN.If(exp, stmts):
                goto_after = self._create_block(
                    "if_else_after", processed_stmts, blocks
                )

                stmts_if = [goto_after]
                for stmt in reversed(stmts):
                    stmts_if = self._picoc_mon_to_picoc_block_stmt(
                        stmt, stmts_if, blocks
                    )
                goto_if = self._create_block("if", stmts_if, blocks)

                return [PN.If(exp, [goto_if])]
            case PN.IfElse(exp, stmts1, stmts2):
                goto_after = self._create_block(
                    "if_else_after", processed_stmts, blocks
                )

                stmts_else = [goto_after]
                for stmt in reversed(stmts2):
                    stmts_else = self._picoc_mon_to_picoc_block_stmt(
                        stmt, stmts_else, blocks
                    )
                goto_else = self._create_block("else", stmts_else, blocks)

                stmts_if = [goto_after]
                for stmt in reversed(stmts1):
                    stmts_if = self._picoc_mon_to_picoc_block_stmt(
                        stmt, stmts_if, blocks
                    )
                goto_if = self._create_block("if", stmts_if, blocks)

                return [PN.IfElse(exp, [goto_if], [goto_else])]
            case PN.While(exp, stmts):
                goto_after = self._create_block("while_after", processed_stmts, blocks)

                goto_branch = PN.GoTo(PN.Name("placeholder"))
                goto_condition_check = PN.GoTo(PN.Name("placeholder"))
                stmts_while = [goto_condition_check]

                for stmt in reversed(stmts):
                    stmts_while = self._picoc_mon_to_picoc_block_stmt(
                        stmt, stmts_while, blocks
                    )
                goto_branch.label.value = self._create_block(
                    "while_branch", stmts_while, blocks
                ).label.value

                condition_check = [PN.IfElse(exp, goto_branch, goto_after)]
                goto_condition_check.label.value = self._create_block(
                    "condition_check", condition_check, blocks
                ).label.value

                return [goto_condition_check]
            case PN.DoWhile(exp, stmts):
                goto_after = self._create_block(
                    "do_while_after", processed_stmts, blocks
                )

                goto_branch = PN.GoTo(PN.Name("placeholder"))
                stmts_while = [PN.IfElse(exp, goto_branch, goto_after)]

                for stmt in reversed(stmts):
                    stmts_while = self._picoc_mon_to_picoc_block_stmt(
                        stmt, stmts_while, blocks
                    )
                goto_branch.label.value = self._create_block(
                    "do_while_branch", stmts_while, blocks
                ).label.value

                return [goto_branch]
            case PN.Return():
                return [stmt]
            case _:
                return [stmt] + processed_stmts

    def _picoc_mon_to_picoc_block_def(self, decl_def):
        match decl_def:
            case PN.FunDef(size_qual, PN.Name(fun_name) as name, params, stmts):
                blocks = dict()
                processed_stmts = []
                for stmt in reversed(stmts):
                    processed_stmts = self._picoc_mon_to_picoc_block_stmt(
                        stmt, processed_stmts, blocks
                    )
                self._create_block(fun_name, processed_stmts, blocks)
                self.all_blocks |= blocks
                return PN.FunDef(
                    size_qual,
                    name,
                    params,
                    list(
                        sorted(
                            blocks.values(),
                            key=lambda block: -int(
                                block.label.value[block.label.value.rindex(".") + 1 :]
                            ),
                        )
                    ),
                )
            case _:
                return decl_def

    def picoc_mon_to_picoc_block(self, file: PN.File):
        match file:
            case PN.File(name, decls_defs):
                decls_defs_blocks = []
                for decl_def in decls_defs:
                    decls_defs_blocks += [self._picoc_mon_to_picoc_block_def(decl_def)]
        return PN.File(name, decls_defs_blocks)

    # =========================================================================
    # =                      PicoC_Blocks -> RETI_Blocks                      =
    # =========================================================================
    def _picoc_block_to_reti_block_block(self):
        ...

    def _picoc_block_to_reti_block_def(self, decl_def):
        match decl_def:
            case PN.FunDef(size_qual, identifier, params, blocks):
                pass

    def picoc_block_to_reti_block(self, file: PN.File):
        match file:
            case PN.File(name, decls_defs):
                reti_blocks = []
                for decl_def in decls_defs:
                    reti_blocks += [self._picoc_mon_to_picoc_block_def(decl_def)]
        return PN.File(name, reti_blocks)

    # =========================================================================
    # =                          RETI_Blocks -> RETI                          =
    # =========================================================================

    def reti_block_to_reti(self):
        ...
