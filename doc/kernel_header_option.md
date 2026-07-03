# Kernel Header Option

The `-k` / `--kernelheader` compiler option runs the normal linking path far enough to compute the final RETI section addresses, then writes only `sections.header`. The generated header contains `KERNEL_CS_START`, `KERNEL_DS_START`, and `KERNEL_HEAP_START` from the computed section metadata, plus blank user-owned definitions for `SRAM_SIZE` and `PROCESS_MEMORY_START` when the file is first created.

When `sections.header` already exists, only the generated section-address macros are refreshed. User-filled values such as `SRAM_SIZE`, `PROCESS_MEMORY_START`, and unrelated header content are preserved.
