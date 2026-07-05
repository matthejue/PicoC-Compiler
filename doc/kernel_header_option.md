# Kernel Header Option

The `-k` / `--kernelheader` compiler option runs the normal linking path far enough to compute the final RETI section addresses, then writes only `memory_constants.header`. In this mode, `-o` selects the path used for `memory_constants.header`, not a `.reti` output path.

`-k sram` generates SRAM-based kernel constants:

```c
#define SRAM_BASE (-2147483647 - 1) // -2^31
#define SRAM_MAX_ADDRESS 262143 // 2^18 - 1
#define KERNEL_HEAP_START <heap_start> // heap_start
#define PROCESS_MEMORY_START <sram_base + stack_start + 1> // -2^31 + stack_start + 1
#define KERNEL_CS_START_ASM "LOADI32 CS <sram_base + codesegment_start>" // -2^31 + codesegment_start
#define KERNEL_DS_START_ASM "LOADI32 DS <sram_base + datasegment_start>" // -2^31 + datasegment_start
#define KERNEL_SP_START_ASM "LOADI32 SP <sram_base + stack_start>" // -2^31 + stack_start
#define KERNEL_CS_ACC_ASM "LOADI32 ACC <sram_base + codesegment_start>" // -2^31 + codesegment_start
```

`-k eprom` generates EPROM start-program constants:

```c
#define SRAM_MAX_ADDRESS 262143 // 2^18 - 1
#define EPROM_DS_START_ASM "LOADI32 DS <datasegment_start>" // datasegment_start
#define EPROM_STACK_START_ASM "LOADI32 SP <sram_base + sram_max_address>" // -2^31 + 2^18 - 1
```
