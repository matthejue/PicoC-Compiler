from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import json
import re
from src import picoc_nodes as pn
from src.utils.util_funs_independent import convert_to_single_line

Symbol = Dict[str, Any]  # e.g. {"kind": "var", "type": "int", ...}
Scope = Dict[str, Symbol]  # symbol_name -> Symbol


class SymbolTable:
    def __init__(self) -> None:
        self._table: Dict[str, Scope] = {"global": {}}
        self._parents: Dict[str, Optional[str]] = {"global": None}

    def items(self):
        """Iterate over (scope_name, symbols_dict) pairs, plus '__parents__'."""
        for k, v in self._table.items():
            yield k, v
        yield "__parents__", self._parents

    # ----- core, minimal helpers -----
    def _ensure_scope(self, scope: str) -> None:
        self._table.setdefault(scope, {})

    def set_parent(self, scope: str, parent: Optional[str]) -> None:
        if scope == parent:
            raise ValueError("A scope cannot be its own parent.")
        self._ensure_scope(scope)
        if parent is not None:
            self._ensure_scope(parent)
        self._parents[scope] = parent

    def contains(self, symbol_name: str, *, scope: str) -> bool:
        """Return True if 'symbol_name' exists in exactly this scope."""
        bucket = self._table.get(scope)
        return bucket is not None and symbol_name in bucket

    def declare(self, symbol_name: str, symbol: Symbol, scope: str) -> None:
        """Add (or overwrite) a symbol in the given scope."""
        self._ensure_scope(scope)
        self._table[scope][symbol_name] = dict(symbol)

    def resolve(self, symbol_name: str, *, scope: str) -> Tuple[Optional[Symbol], Optional[str]]:
        """
        Look up 'symbol_name' starting at 'scope' and walking parents outward.
        Returns (symbol_dict, found_scope) or (None, None) if not found.
        """
        cur = scope
        while cur is not None:
            bucket = self._table.get(cur)
            if bucket and symbol_name in bucket:
                return bucket[symbol_name], cur
            cur = self._parents.get(cur)  # None ends the walk
        return None, None

    # ----- JSON (pretty print, save/load) -----
    def to_json_str(self, *, pretty: bool = True) -> str:
        payload = dict(self._table)
        payload["__parents__"] = dict(self._parents)
        return json.dumps(
            payload,
            indent=2 if pretty else None,
            sort_keys=pretty,
            ensure_ascii=False,
            default=_json_default,  # stringify unknown/custom types
        )

    def save_json(self, path: str | Path, *, pretty: bool = True) -> None:
        Path(path).write_text(self.to_json_str(pretty=pretty), encoding="utf-8")

    @classmethod
    def load_json(cls, path: str | Path) -> "SymbolTable":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        st = cls()
        st._table.clear()
        st._parents.clear()
        for k, v in data.items():
            if k == "__parents__":
                st._parents.update(v)
            else:
                st._table[k] = {
                    name: (
                        _restore_symbol_payload(dict(sym)) if isinstance(sym, dict) else sym
                    )
                    for name, sym in v.items()
                }
        # Make sure every scope in parents exists and vice versa
        for s in list(st._parents.keys()):
            st._ensure_scope(s)
        for s in list(st._table.keys()):
            if s not in st._parents:
                st._parents[s] = None if s == "global" else None
        return st

    def __repr__(self) -> str:
        return self.to_json_str(pretty=True)


def _json_default(ast):
    return convert_to_single_line(ast)


_AST_STRING_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\(.*\)$", re.DOTALL)
_PICOC_AST_REGISTRY = {
    name: value
    for name, value in vars(pn).items()
    if isinstance(value, type) and issubclass(value, pn.ASTNode)
}
_PICOC_AST_EVAL_SCOPE = dict(_PICOC_AST_REGISTRY)


def _restore_alloc(type_qual, datatype, name, local_var_or_param="local_var"):
    alloc = pn.Alloc(type_qual, datatype, name)
    alloc.local_var_or_param = local_var_or_param
    return alloc


def _restore_fun_decl(*args):
    if len(args) == 3:
        datatype, name, allocs = args
        return pn.FunDecl([], datatype, name, allocs)
    if len(args) == 4:
        storage_class_specifiers, datatype, name, allocs = args
        return pn.FunDecl(storage_class_specifiers, datatype, name, allocs)
    raise TypeError(f"Unsupported FunDecl payload: {args!r}")


def _restore_fun_def(*args):
    if len(args) == 4:
        datatype, name, allocs, stmts_blocks = args
        return pn.FunDef([], datatype, name, allocs, stmts_blocks)
    if len(args) == 5:
        storage_class_specifiers, datatype, name, allocs, stmts_blocks = args
        return pn.FunDef(storage_class_specifiers, datatype, name, allocs, stmts_blocks)
    raise TypeError(f"Unsupported FunDef payload: {args!r}")


_PICOC_AST_EVAL_SCOPE.update(
    {
        "Alloc": _restore_alloc,
        "FunDecl": _restore_fun_decl,
        "FunDef": _restore_fun_def,
    }
)


def _restore_symbol_payload(value):
    if isinstance(value, dict):
        return {key: _restore_symbol_payload(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_restore_symbol_payload(item) for item in value]
    if isinstance(value, str) and _AST_STRING_RE.match(value):
        node_name = value.split("(", 1)[0]
        if node_name in _PICOC_AST_REGISTRY:
            return eval(value, {"__builtins__": {}}, _PICOC_AST_EVAL_SCOPE)
    return value
