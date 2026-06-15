# Compiler Pass Order

- Per `.picoc` file:
  `raw code -> preprocessed code -> Tree-sitter tokens -> parse tree -> AST via transformer -> picoc_shrink -> picoc_blocks -> picoc_symbol -> symbol table -> picoc_typing -> picoc_anf -> reti_blocks`.
- If `--compile/-c`: stop after `.reti_blocks` + `.st`.
- If linking: insert `_start` if `main` exists, merge sections/symbol tables, then `combined reti_blocks -> reti_patch -> reti`.
- External `.reti_blocks` input needs matching `.st`; enters at link stage.
