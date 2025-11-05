from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import json
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
                    name: (dict(sym) if isinstance(sym, dict) else sym)
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
