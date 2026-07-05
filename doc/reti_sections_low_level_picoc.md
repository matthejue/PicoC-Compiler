# RETI Sections / Low-Level PicoC (hubs/direct RETI asm)

- Sections: `.ivt`, `.text`, `.data`.
- Periphery details: `/home/areo/Documents/Studium/RETI-Emulator/doc/address_space.md`; `10`/`11` are SRAM.
- Use `__attribute__((section("ivt")))` on globals/functions to place them in `.ivt`.
- Use `-O1` so known global initializer values can be emitted into data/IVT sections at compile time.
- Use `__attribute__((naked))` + `asm("...");` for exact assembly blocks: function name becomes label, no prologue/epilogue.
- Use no-arg `static inline` functions with only `asm("...");` statements for inline asm helpers: the helper body is copied into each statement-form call site and no standalone helper function is emitted.
- Naked asm functions are useful as interrupt hubs: handle register-passed ISR args, then jump/call real handler functions.
