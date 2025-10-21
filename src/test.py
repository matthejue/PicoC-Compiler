#!/usr/bin/env python3
import ast
import importlib
from types import ModuleType
from typing import Any, Union

class PicocParseError(ValueError):
    """Raised for invalid/unsupported node strings."""
    pass

def _eval_literal(node: ast.AST) -> Any:
    """Evaluate safe Python literals inside the node string."""
    if isinstance(node, ast.Constant):
        # Supports str, int, float, bool, None, etc.
        return node.value
    if isinstance(node, ast.List):
        return [_eval_literal(elt) for elt in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(_eval_literal(elt) for elt in node.elts)
    if isinstance(node, ast.Dict):
        return {_eval_literal(k): _eval_literal(v) for k, v in zip(node.keys, node.values)}
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub) and isinstance(node.operand, ast.Constant):
        # Negative numbers like -1, -3.14
        val = node.operand.value
        if isinstance(val, (int, float, complex)):
            return -val
    # Disallow names and anything else at literal positions.
    raise PicocParseError(f"Unsupported literal syntax: {ast.dump(node, include_attributes=False)}")

def _build_from_ast(node: ast.AST, picoc_ns: ModuleType) -> Any:
    """Recursively build picoc_nodes instances from an AST."""
    if isinstance(node, ast.Call):
        # Function must be a simple name like Assign(...), Call(...), Name(...)
        if not isinstance(node.func, ast.Name):
            raise PicocParseError("Only simple class names (e.g., Assign(...)) are allowed.")
        class_name = node.func.id

        cls = getattr(picoc_ns, class_name, None)
        if cls is None or not isinstance(cls, type):
            raise PicocParseError(f"Unknown node '{class_name}' — not defined in picoc_nodes.")

        # Positional args: each can be another node (ast.Call) or a literal/list/etc.
        args = [
            _build_from_ast(a, picoc_ns) if isinstance(a, ast.Call) else _eval_literal(a)
            for a in node.args
        ]
        # Keyword args supported, too.
        kwargs = {}
        for kw in node.keywords:
            if kw.arg is None:
                # No support for **kwargs expansions
                raise PicocParseError("Dict unpack (**kwargs) is not supported.")
            val = _build_from_ast(kw.value, picoc_ns) if isinstance(kw.value, ast.Call) else _eval_literal(kw.value)
            kwargs[kw.arg] = val

        return cls(*args, **kwargs)

    # If we get here at the top level, the expression wasn't a Call (i.e., a class instantiation)
    raise PicocParseError("Top-level expression must be a class construction like Assign(...).")

def build_picoc_node(expr: str, picoc_nodes: Union[str, ModuleType] = "picoc_nodes") -> Any:
    """
    Build nested picoc_nodes objects from a string like:
        "Assign(Alloc(Writeable(), IntType(), Name('local_var1')), Call(Name('input'), []))"

    Params
    ------
    expr : str
        The nested constructor string.
    picoc_nodes : str | module
        The module name or module object that defines your node classes.
        Defaults to importing a module named 'picoc_nodes'.

    Returns
    -------
    Any
        The constructed top-level node instance.

    Raises
    ------
    PicocParseError
        If the syntax is invalid, contains unsupported constructs,
        or references a class not present in picoc_nodes.
    """
    if isinstance(picoc_nodes, str):
        picoc_ns = importlib.import_module(picoc_nodes)
    else:
        picoc_ns = picoc_nodes

    try:
        tree = ast.parse(expr.strip(), mode="eval")
    except SyntaxError as e:
        raise PicocParseError(f"Invalid syntax at line {e.lineno}, col {e.offset}: {e.msg}") from e

    # We only allow a single expression: must be a Call at the top.
    if not isinstance(tree, ast.Expression):
        raise PicocParseError("Expression parsing failed unexpectedly.")
    return _build_from_ast(tree.body, picoc_ns)
