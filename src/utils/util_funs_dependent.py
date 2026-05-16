import itertools
import sys
import traceback
import ast
from typing import Any, Dict, List, Optional, Type

from src import global_vars
import src.picoc_nodes as pn
from src.utils.util_funs_independent import convert_to_single_line

def overwrite(old, replace_with, idx):
    return old[:idx] + replace_with + old[idx + len(replace_with) :]

NODE_TO_Symbol = {pn.Add: "+", pn.Sub: "-"}

def nodes_to_str(nodes: list):
    nodes = [NODE_TO_Symbol.get(elem, elem) for elem in nodes]
    return " or ".join(
        elem
        for elem in (
            nodes
            if global_vars.args.double_verbose
            else itertools.islice(nodes, global_vars.max_print_out_elements + 1)
        )
    )


def args_to_str(args: list):
    if args:
        # this function only gets called in case of an error, so the verbose
        # option doesn't have to be reset, because execution ends anyways
        return ("argument " if len(args) == 1 else "arguments ") + ", ".join(
            "'" + convert_to_single_line(arg) + "'" for arg in args
        )
    else:
        return "no arguments"


def throw_error(node):
    if isinstance(node, str):
        msg = node
    else:
        msg = f"Unexpected value ({type(node).__name__}): {node!r}"
    if getattr(global_vars, "args", None) and getattr(global_vars.args, "debug", False):
        # Let the post-mortem hook handle the crash when debug mode is enabled.
        raise RuntimeError(msg)
    print(msg, file=sys.stderr)
    traceback.print_stack(file=sys.stderr)
    sys.exit(1)


def remove_ext(fname):
    # if there's no '.' rindex raises a exception, find returns -1
    index_of_extension_start = fname.rfind(".")
    if index_of_extension_start == -1:
        return fname
    return fname[0:index_of_extension_start]


def get_ext(fname):
    # if there's no '.' rindex raises a exception, find returns -1
    idx_of_extension_start = fname.rfind(".")
    if idx_of_extension_start == -1:
        return fname
    return fname[idx_of_extension_start + 1 :]


def _remove_path(fname):
    index_of_path_end = fname.rfind("/")
    if index_of_path_end == -1:
        return fname
    return fname[index_of_path_end + 1 :]


def filename_without_ext(fname):
    fname = remove_ext(fname)
    return _remove_path(fname)


def remove_filename(fname):
    index_of_path_end = fname.rfind("/")
    if index_of_path_end == -1:
        return "./"
    return fname[: index_of_path_end + 1]


def filter_out_comments(instrs):
    if not (global_vars.args.verbose or global_vars.args.double_verbose):
        return instrs
    return filter(
        lambda instr: not isinstance(instr, pn.SingleLineComment),
        instrs,
    )


def subheading(heading, symbol):
    return f"{symbol * ((global_vars.terminal_columns - len(heading) - 2) // 2 + (1 if (global_vars.terminal_columns - len(heading)) % 2 else 0))} {heading} {symbol * ((global_vars.terminal_columns - len(heading) - 2) // 2)}"


def wrap_text(text):
    lines = text.split("\n")
    for l_idx, line in enumerate(lines):
        if len(line) > global_vars.terminal_columns:
            for idx in range(global_vars.terminal_columns, -1, -1):
                if line[idx] == " ":
                    lines.insert(l_idx + 1, line[idx + 1 :])
                    lines[l_idx] = line[:idx]
                    break
    return "\n".join(lines)


def build_ast_from_string(
    s: str,
    class_registry: Optional[Dict[str, Type["pn.ASTNode"]]] = None,
    base_class: Type["pn.ASTNode"] = None,
) -> "pn.ASTNode":
    """
    Parse strings like:
        "Assign(Alloc(Writeable(), IntType(), Name('local_var1')), Call(Name('input'), []))"
    and return a nested tree of your AST node *classes only*.

    Rules (strict):
      - Every call name (e.g., Assign, Alloc, Name, Call, ...) MUST exist in class_registry (or globals()).
        If a class is missing, print a clear error and exit(1).
      - A node may have exactly one string literal argument, which becomes node.val (e.g., Name('x')).
      - Otherwise, all arguments must be:
          * other node calls,
          * lists (possibly empty) of nodes,
          * dicts (possibly empty) whose VALUES are nodes.
        Any bare literal (int/float/bool/str) outside the single-arg-val case is an error.
      - Bare names (like `foo` not followed by `(...)`) are invalid.
    """

    if base_class is None:
        # By default, detect ASTNode in globals
        try:
            base_class = globals()["pn.ASTNode"]
        except KeyError:
            print(
                "Error: base ASTNode class is not available in globals().",
                file=sys.stderr,
            )
            sys.exit(1)

    registry: Dict[str, Type["pn.ASTNode"]] = (
        dict(globals()) if class_registry is None else dict(class_registry)
    )

    def _require_class(name: str) -> Type["pn.ASTNode"]:
        cls = registry.get(name)
        if cls is None:
            print(f"Error: Unknown AST node class '{name}'.", file=sys.stderr)
            sys.exit(1)
        if not isinstance(cls, type):
            print(f"Error: '{name}' is not a class.", file=sys.stderr)
            sys.exit(1)
        if not issubclass(cls, base_class):
            print(
                f"Error: '{name}' is not a subclass of {base_class.__name__}.",
                file=sys.stderr,
            )
            sys.exit(1)
        return cls

    def _is_node(obj: Any) -> bool:
        return isinstance(obj, base_class)

    def _ensure_list_of_nodes(obj_list: List[Any], where: str) -> List["pn.ASTNode"]:
        out: List["pn.ASTNode"] = []
        for idx, el in enumerate(obj_list):
            if not _is_node(el):
                print(
                    f"Error: Found non-node element inside list at {where}[{idx!r}]. "
                    f"Lists may only contain node instances.",
                    file=sys.stderr,
                )
                sys.exit(1)
            out.append(el)
        return out

    def _ensure_dict_of_nodes(
        obj_dict: Dict[Any, Any], where: str
    ) -> Dict[Any, "pn.ASTNode"]:
        out: Dict[Any, "pn.ASTNode"] = {}
        for k, v in obj_dict.items():
            if not _is_node(v):
                print(
                    f"Error: Found non-node dict value at {where}[{k!r}]. "
                    f"Dict values must be node instances.",
                    file=sys.stderr,
                )
                sys.exit(1)
            out[k] = v
        return out

    def _build(node: ast.AST, ctx: str) -> Any:
        # list literal
        if isinstance(node, ast.List):
            built = [_build(elt, ctx + " <list>") for elt in node.elts]
            return built  # validation happens when attaching as children

        # dict literal
        if isinstance(node, ast.Dict):
            built: Dict[Any, Any] = {}
            for k, v in zip(node.keys, node.values):
                # Keep keys as their best string/py form; values must become nodes later
                if isinstance(k, ast.Constant):
                    key = k.value
                elif isinstance(k, ast.Name):
                    key = k.id
                else:
                    key = ast.unparse(k) if hasattr(ast, "unparse") else str(k)
                built[key] = _build(v, ctx + f" <dict key={key!r}>")
            return built  # validation happens when attaching as children

        # single literal constant (only allowed as the sole argument to set .val, and must be str)
        if isinstance(node, ast.Constant):
            return node.value

        # bare name (invalid per our format)
        if isinstance(node, ast.Name):
            print(
                f"Error: Bare name '{node.id}' encountered at {ctx}. "
                f"Node types must be called like TypeName(...).",
                file=sys.stderr,
            )
            sys.exit(1)

        # function call => construct node
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                print(f"Error: Unsupported callee form at {ctx}.", file=sys.stderr)
                sys.exit(1)

            class_name = node.func.id
            cls = _require_class(class_name)

            built_args = [_build(arg, ctx + f" -> {class_name}()") for arg in node.args]

            # Case 1: exactly one string literal arg -> becomes .val, no children
            if len(built_args) == 1 and isinstance(built_args[0], str):
                return cls(built_args[0])

            # Otherwise: all args must be nodes/lists-of-nodes/dicts-of-nodes
            children: List[Any] = []
            for i, arg in enumerate(built_args):
                where = f"{class_name} arg#{i}"
                if _is_node(arg):
                    children.append(arg)
                elif isinstance(arg, list):
                    children.append(_ensure_list_of_nodes(arg, where))
                elif isinstance(arg, dict):
                    children.append(_ensure_dict_of_nodes(arg, where))
                else:
                    # any other literal or unexpected type is invalid
                    literal_preview = repr(arg)
                    print(
                        f"Error: Invalid argument {literal_preview} at {where}. "
                        f"Only nodes, lists-of-nodes, and dicts-of-nodes are allowed "
                        f"(except a single string literal to set .val).",
                        file=sys.stderr,
                    )
                    sys.exit(1)

            return cls(*children)

        print(f"Error: Unsupported syntax at {ctx}: {ast.dump(node)}", file=sys.stderr)
        sys.exit(1)

    try:
        py_ast = ast.parse(s, mode="eval")
    except SyntaxError as e:
        print(
            f"Error: Failed to parse input string as an expression: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    result = _build(py_ast.body, ctx="<root>")
    if not _is_node(result):
        print(
            "Error: Top-level expression did not produce an AST node.", file=sys.stderr
        )
        sys.exit(1)
    return result


# -------- Example usage (assuming your concrete classes are defined in scope) --------
if __name__ == "__main__":
    # Example with only known classes; otherwise it will error and exit.
    src = "Assign(Alloc(Writeable(), IntType(), Name('local_var1')), Call(Name('input'), []))"
    root = build_ast_from_string(src)
    print(root)
