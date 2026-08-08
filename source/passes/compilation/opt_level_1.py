from source import picoc_nodes as pn
from source import reti_nodes as rn
from source.utils.util_funs_dependent import throw_error

IVT_SECTION = "ivt"


def enabled(args) -> bool:
    return getattr(args, "optimization_level", 0) >= 1


def data_block_name(symbol_name: str) -> str:
    return symbol_name


def data_symbol_name(entry, symbol_names):
    if not isinstance(entry, pn.Block):
        return None
    symbol_name = getattr(entry, "data_symbol_name", None)
    if symbol_name is not None:
        return symbol_name
    if entry.name in symbol_names:
        return entry.name
    return None


def global_storage_symbols(symbol_table):
    for name, symbol in symbol_table._table.get("global", {}).items():
        if (
            isinstance(symbol, dict)
            and symbol.get("frame_kind") == "global"
            and "addr" in symbol
            and "size" in symbol
        ):
            yield name, symbol


def data_storage_symbols(symbol_table):
    for name, symbol in global_storage_symbols(symbol_table):
        if symbol.get("section", "data") == "data":
            yield name, symbol


def ivt_storage_symbols(symbol_table):
    for name, symbol in global_storage_symbols(symbol_table):
        if symbol.get("section") == IVT_SECTION:
            yield name, symbol


def split_global_inits(block, symbol_table, char_literal_code):
    optimized_values = {}
    runtime_stmts = []
    pending = []

    for stmt in block.stmts_instrs:
        match stmt:
            case pn.Assign(pn.Global(pn.Name(var_name)), pn.Stack(pn.Num(size))):
                values = _compile_time_values(pending, char_literal_code)
                if values is not None and len(values) == int(size):
                    optimized_values[var_name] = values
                else:
                    runtime_stmts.extend(pending)
                    runtime_stmts.append(stmt)
                pending = []
            case _:
                pending.append(stmt)

    runtime_stmts.extend(pending)
    block.stmts_instrs[:] = runtime_stmts
    return _data_blocks(symbol_table, optimized_values)


def split_ivt_data(block, symbol_table, char_literal_code):
    ivt_symbols = {
        symbol_name
        for symbol_name, _ in ivt_storage_symbols(symbol_table)
    }
    if not ivt_symbols:
        return []

    optimized_values = {}
    runtime_stmts = []
    pending = []

    for stmt in block.stmts_instrs:
        match stmt:
            case pn.Assign(pn.Global(pn.Name(var_name)), pn.Stack(pn.Num(size))) if var_name in ivt_symbols:
                values = _compile_time_values(pending, char_literal_code)
                if values is None or len(values) != int(size):
                    throw_error(
                        f"Initializer for '{var_name}' in section "
                        f"'{IVT_SECTION}' must be compile-time constant"
                    )
                optimized_values[var_name] = values
                pending = []
            case _:
                pending.append(stmt)

    runtime_stmts.extend(pending)
    block.stmts_instrs[:] = runtime_stmts
    return _data_blocks(
        symbol_table,
        optimized_values,
        storage_symbols=ivt_storage_symbols(symbol_table),
    )


def ordered_data_entries(entries, symbol_table):
    storage_symbols = list(data_storage_symbols(symbol_table))
    symbol_names = {symbol_name for symbol_name, _ in storage_symbols}
    by_symbol = {}
    other_entries = []
    for entry in entries:
        symbol_name = data_symbol_name(entry, symbol_names)
        if symbol_name is None:
            other_entries.append(entry)
        else:
            by_symbol[symbol_name] = entry

    ordered = [
        by_symbol.pop(symbol_name)
        for symbol_name, _ in storage_symbols
        if symbol_name in by_symbol
    ]
    return ordered + list(by_symbol.values()) + other_entries


def _compile_time_values(stmts, char_literal_code):
    values = []
    for stmt in stmts:
        match stmt:
            case pn.SingleLineComment():
                continue
            case pn.Exp(exp):
                value = _compile_time_value(exp, char_literal_code)
                if value is None:
                    return None
                values.append(value)
            case _:
                return None
    return values


def _compile_time_value(exp, char_literal_code):
    match exp:
        case pn.Num(val):
            return rn.Im(val)
        case pn.Char(val):
            return rn.Im(str(char_literal_code(val)))
        case pn.FunRef(pn.Name(label)):
            return rn.Ivte(rn.Name(label))
        case _:
            return None


def _data_blocks(symbol_table, optimized_values, *, storage_symbols=None):
    blocks = []
    if storage_symbols is None:
        storage_symbols = data_storage_symbols(symbol_table)
    for symbol_name, symbol in storage_symbols:
        size = int(symbol["size"])
        entries = optimized_values.get(symbol_name)
        if entries is None:
            entries = [rn.Im("0") for _ in range(size)]
        block = pn.Block(data_block_name(symbol_name), entries)
        block.scope = "global"
        block.block_idx = -1
        block.data_symbol_name = symbol_name
        blocks.append(block)
    return blocks
