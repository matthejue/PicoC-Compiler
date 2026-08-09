# Kernel Header Option

The `-k` / `--kernelheader` compiler option runs the normal linking path far enough to compute the final RETI section addresses, then writes only `memory_constants.header`. In this mode, `-o` selects the path used for `memory_constants.header`, not a `.reti` output path. The paired `--heap-size CELLS` and `--stack-size CELLS` options set `heap_size` and calculate `stack_start` as `heap_start + heap_size + stack_size`. The same options set these fields directly in the `.sections` file during a normal linked build.

`-k sram` generates SRAM-based kernel constants:

```c
#define SRAM_BASE (-2147483647 - 1) // -2^31
#define SRAM_MAX_ADDRESS_IN_MEMORY_MAP <sram_base + sram_max_address> // -2^31 + 2^18 - 1
#define KERNEL_HEAP_START <sram_base + heap_start> // -2^31 + heap_start
#define KERNEL_HEAP_SIZE <heap_size> // heap_size
#define PROCESS_MEMORY_START <sram_base + stack_start + 1> // -2^31 + stack_start + 1
#define KERNEL_CS_START_ASM "LOADI32 CS <sram_base + codesegment_start>" // -2^31 + codesegment_start
#define KERNEL_DS_START_ASM "LOADI32 DS <sram_base + datasegment_start>" // -2^31 + datasegment_start
#define KERNEL_SP_START_ASM "LOADI32 SP <sram_base + stack_start>" // -2^31 + stack_start
#define KERNEL_CS_ACC_ASM "LOADI32 ACC <sram_base + codesegment_start>" // -2^31 + codesegment_start
```

`SRAM_MAX_ADDRESS_IN_MEMORY_MAP`, `KERNEL_HEAP_START`, and `PROCESS_MEMORY_START` are absolute SRAM addresses, not section offsets. `KERNEL_HEAP_SIZE` is a number of SRAM cells and defaults to `4096` when the generated section value is `-1`. Supplying the two size options makes `KERNEL_HEAP_SIZE`, `KERNEL_SP_START_ASM`, and `PROCESS_MEMORY_START` use the requested layout without post-processing the header.

`-k eprom` generates EPROM start-program constants:

```c
#define SRAM_MAX_ADDRESS 262143 // 2^18 - 1
#define EPROM_DS_START_ASM "LOADI32 DS <datasegment_start>" // datasegment_start
#define EPROM_STACK_START_ASM "LOADI32 SP <sram_base + sram_max_address>" // -2^31 + 2^18 - 1
```
