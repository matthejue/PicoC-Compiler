from src import global_vars
from src import picoc_nodes as pn
from src import reti_nodes as rn
from src.utils.util_funs_dependent import throw_error
from src.utils.util_funs_independent import convert_to_single_line
import copy


class PicocBlocksPass:
    COMMENT_VISIBLE_FILTERS = {
        rn.Instr: (),
        pn.Array: (),
        pn.Struct: (),
        pn.StructDecl: (),
        pn.If: (1,),
        pn.IfElse: (1, 2),
        pn.While: (1,),
        pn.DoWhile: (1,),
        pn.Call: (),
        pn.FunDecl: (3,),
        pn.FunDef: (3, 4),
        pn.File: (1,),
        pn.Block: (1,),
    }

    def _single_line_comment(self, node, prefix):
        if not (global_vars.args.verbose or global_vars.args.double_verbose):
            return []

        def _repr_with_visible(node_for_repr, visible):
            if not visible:
                return f"\n{node_for_repr.__class__.__name__}()"
            parts = []
            for child in visible:
                match child:
                    case list() as lst:
                        if not lst:
                            parts.append("[]")
                        else:
                            lst_parts = []
                            for item in lst:
                                try:
                                    lst_parts.append(convert_to_single_line(item))
                                except Exception:
                                    lst_parts.append(repr(item))
                            parts.append("[" + ", ".join(lst_parts) + "]")
                    case str() as s:
                        parts.append(f"'{s}'")
                    case int() as i:
                        parts.append(str(i))
                    case _:
                        try:
                            parts.append(child.__repr__())
                        except Exception:
                            parts.append(repr(child))
            return f"\n{node_for_repr.__class__.__name__}(" + ", ".join(parts) + ")"

        if hasattr(node, "visible"):
            visible_copy = copy.deepcopy(list(node.visible))
            filtered_indexes = self.COMMENT_VISIBLE_FILTERS.get(type(node), ())
            for i, visible_list_item in enumerate(visible_copy):
                if isinstance(visible_list_item, list) and i in filtered_indexes:
                    visible_copy[i] = []
            node_repr = _repr_with_visible(node, visible_copy)
            return [pn.SingleLineComment(prefix, convert_to_single_line(node_repr))]

        return [pn.SingleLineComment(prefix, convert_to_single_line(node))]

    def _char_literal_code(self, val: str) -> int:
        if len(val) == 2 and val[0] == "\\":
            escape_map = {
                "0": 0,
                "n": 10,
                "t": 9,
                "r": 13,
                "\\": 92,
                "'": 39,
                '"': 34,
            }
            return escape_map.get(val[1], ord(val[1]))
        return ord(val)

    def _create_block(
        self,
        labelbase,
        stmts,
        blocks,
        *,
        add_id=True,
        label_prefix=None,
        show_id_comment=False,
    ):
        if add_id and label_prefix is not None:
            labelbase = f"{label_prefix}_{labelbase}"
        label = labelbase + (f".{self.block_idx}" if add_id else "")
        new_block = pn.Block(
            label,
            stmts,
        )
        new_block.block_idx = self.block_idx
        new_block.show_id_comment = show_id_comment
        blocks[label] = new_block
        self.block_idx += 1
        return pn.GoTo(pn.Name(label))

    def _picoc_blocks_stmt(self, stmt, processed_stmts, blocks, label_prefix):
        match stmt:
            # --------------------------- L_If_Else ---------------------------
            case pn.If(exp, stmts):
                goto_after = self._create_block(
                    "if_else_after", processed_stmts, blocks, label_prefix=label_prefix
                )

                stmts_if = [goto_after]
                for sub_stmt in reversed(stmts):
                    stmts_if = self._inherit_origin_many(
                        self._picoc_blocks_stmt(
                            sub_stmt, stmts_if, blocks, label_prefix
                        ),
                        sub_stmt,
                    )
                goto_if = self._create_block(
                    "if", stmts_if, blocks, label_prefix=label_prefix
                )

                return self._single_line_comment(stmt, "//") + [
                    pn.IfElse(exp, [goto_if], [goto_after])
                ]
            case pn.IfElse(exp, stmts1, stmts2):
                goto_after = self._create_block(
                    "if_else_after", processed_stmts, blocks, label_prefix=label_prefix
                )

                stmts_else = [goto_after]
                for stmt in reversed(stmts2):
                    stmts_else = self._inherit_origin_many(
                        self._picoc_blocks_stmt(stmt, stmts_else, blocks, label_prefix),
                        stmt,
                    )
                goto_else = self._create_block(
                    "else", stmts_else, blocks, label_prefix=label_prefix
                )

                stmts_if = [goto_after]
                for stmt in reversed(stmts1):
                    stmts_if = self._inherit_origin_many(
                        self._picoc_blocks_stmt(stmt, stmts_if, blocks, label_prefix),
                        stmt,
                    )
                goto_if = self._create_block(
                    "if", stmts_if, blocks, label_prefix=label_prefix
                )

                return self._single_line_comment(stmt, "//") + [
                    pn.IfElse(exp, [goto_if], [goto_else])
                ]
            # ----------------------------- L_Loop ----------------------------
            case pn.While(exp, stmts):
                # Example:
                # while (i < max) {
                #   i = i + 1;
                # }
                # print(i);
                #
                # Becomes roughly:
                #
                # current block:
                #   goto condition_check
                #
                # condition_check:
                #   if (i < max) goto while_branch else goto while_after
                #
                # while_branch:
                #   i = i + 1
                #   goto condition_check
                #
                # while_after:
                #   print(i)
                #
                # Blocks are sorted by descending block_idx later. Because this
                # pass walks statements in reverse and _create_block counts upward,
                # create the code-after-loop block first, then loop-body, then
                # condition-check.
                goto_after = self._inherit_origin(
                    self._create_block(
                        "while_after",
                        processed_stmts,
                        blocks,
                        label_prefix=label_prefix,
                    ),
                    exp,
                )
                # Keep goto_loopback_condition_check and the later
                # goto_condition_check separate; later object changes must not
                # affect both instruction sites.
                goto_loopback_condition_check = self._inherit_origin(
                    pn.GoTo(pn.Name("placeholder")), stmt
                )
                stmts_while = [goto_loopback_condition_check]
                for sub_stmt in reversed(stmts):
                    stmts_while = self._inherit_origin_many(
                        self._picoc_blocks_stmt(
                            sub_stmt, stmts_while, blocks, label_prefix
                        ),
                        sub_stmt,
                    )
                goto_branch = self._inherit_origin(
                    self._create_block(
                        "while_branch", stmts_while, blocks, label_prefix=label_prefix
                    ),
                    exp,
                )
                goto_condition_check = self._inherit_origin(
                    self._create_block(
                        "condition_check",
                        [
                            self._inherit_origin(
                                pn.IfElse(exp, [goto_branch], [goto_after]), exp
                            )
                        ],
                        blocks,
                        label_prefix=label_prefix,
                    ),
                    stmt,
                )
                goto_loopback_condition_check.name.val = goto_condition_check.name.val

                return self._single_line_comment(stmt, "//") + [goto_condition_check]
            case pn.DoWhile(exp, stmts):
                # Example:
                # do {
                #   i = i + 1;
                # } while (i < max);
                # print(i);
                #
                # Becomes roughly:
                #
                # current block:
                #   goto do_while_branch
                #
                # do_while_branch:
                #   i = i + 1
                #   if (i < max) goto do_while_branch else goto do_while_after
                #
                # do_while_after:
                #   print(i)
                goto_after = self._inherit_origin(
                    self._create_block(
                        "do_while_after",
                        processed_stmts,
                        blocks,
                        label_prefix=label_prefix,
                    ),
                    exp,
                )
                goto_loopback_branch = self._inherit_origin(
                    pn.GoTo(pn.Name("placeholder")), exp
                )
                stmts_while = [
                    self._inherit_origin(
                        pn.IfElse(exp, [goto_loopback_branch], [goto_after]), exp
                    )
                ]
                for sub_stmt in reversed(stmts):
                    stmts_while = self._inherit_origin_many(
                        self._picoc_blocks_stmt(
                            sub_stmt, stmts_while, blocks, label_prefix
                        ),
                        sub_stmt,
                    )
                goto_branch = self._inherit_origin(
                    self._create_block(
                        "do_while_branch",
                        stmts_while,
                        blocks,
                        label_prefix=label_prefix,
                    ),
                    stmt,
                )
                goto_loopback_branch.name.val = goto_branch.name.val

                return self._single_line_comment(stmt, "//") + [goto_branch]
            # ----------------------------- L_Fun -----------------------------
            case pn.Return():
                return [stmt]
            case _:
                return [stmt] + processed_stmts

    def _picoc_blocks_def(self, decl_def):
        match decl_def:
            # ----------------------------- L_Fun -----------------------------
            case pn.FunDef(storage_class_specifiers, datatype, pn.Name(val) as name, allocs, stmts):
                fun_name = val
                blocks = dict()
                processed_stmts = []
                for stmt in reversed(stmts):
                    processed_stmts = self._inherit_origin_many(
                        self._picoc_blocks_stmt(stmt, processed_stmts, blocks, fun_name),
                        stmt,
                    )

                self._create_block(
                    fun_name,
                    processed_stmts,
                    blocks,
                    add_id=False,
                    show_id_comment=True,
                )
                self.all_blocks |= blocks
                fun_def = pn.FunDef(
                    storage_class_specifiers,
                    datatype,
                    name,
                    allocs,
                    list(
                        sorted(
                            blocks.values(),
                            key=lambda block: -int(block.block_idx),
                        )
                    ),
                )
                return [
                    self._inherit_origin(fun_def, decl_def)
                ]
            case pn.StructSpec() | pn.FunDecl() | pn.StructDecl() | pn.Exp() | pn.Assign():
                return [decl_def]
            case _:
                throw_error(decl_def)

    def picoc_blocks(self, file: pn.File):
        match file:
            # ----------------------------- L_File ----------------------------
            case pn.File(pn.Name(val), decls_defs):
                decls_defs_blocks = []
                for decl_def in decls_defs:
                    decls_defs_blocks += self._picoc_blocks_def(decl_def)
                return pn.File(
                    pn.Name(global_vars.tstate.path_without_ext + ".picoc_blocks"),
                    decls_defs_blocks,
                )
            case _:
                throw_error(file)
