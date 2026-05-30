# Compiler Passes

## PicoC Shrink

- Ersetzt Array-Zugriffe durch Pointer-Arithmetik (`arr[i] -> *(arr + i)`).

## PicoC Blocks

- `If(exp, stmts)`, `IfElse(exp, stmts1, stmts2)`, `While(exp, stmts)` und
  `DoWhile(exp, stmts)` durch `Block(name, stmts_instrs)`, `GoTo(label)` und
  `IfElse(exp, stmts1, stmts2)` ersetzt.

## PicoC Symbol

- Builds the symbol table and rewrites PicoC `Name` nodes ahead of typing.
- Declares function and struct declarations and definitions to the symbol table.

## PicoC Typing

- Annotates the PicoC AST with datatype information.

## PicoC ANF

- Bringt den AST in A-Normalform.

## RETI Blocks

- PicoC-Knoten werden durch semantisch entsprechende RETI-Knoten ersetzt.

## RETI Patch

- Deals with large immediates.
- Deals with `goto` directly to the next block.
- Deals with division by zero.
- Handles the case where the `main` function is not the first function in the file.
- Handles the case where there is no `main` function.

## RETI

- Keine Blöcke mehr; Knoten werden genauso zusammengefügt, wie sie in den
  entfernten Blöcken angeordnet waren.
- `GoTo(Name(str))` wird durch ein Immediate mit passender Distanz/Adresse oder
  einen Sprungbefehl mit passender Distanz ersetzt:
  `Jump(Always(), Im(str(distance)))`.
