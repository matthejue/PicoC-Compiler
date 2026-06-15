# RETI Sections / Low-Level PicoC (hubs/direct RETI asm)

- Sections: `.interrupt_vector_table`, `.text`, `.data`.
- Periphery details: `/home/areo/Documents/Studium/RETI-Emulator/doc/address_space.md`; `10`/`11` are SRAM.
- Use `__attribute__((section("interrupt_vector_table")))` on globals/functions to place them in `.interrupt_vector_table`.
- Use `-O1` so known global initializer values can be emitted into data/IVT sections at compile time.
- Use `__attribute__((naked))` + `asm("...");` for exact assembly blocks: function name becomes label, no prologue/epilogue.
- Naked asm functions are useful as interrupt hubs: handle register-passed ISR args, then jump/call real handler functions.
