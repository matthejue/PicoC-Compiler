# Compiling a file
With the following **cli-options** you won't miss anything when compiling **PicoC** into **RETI-Code**:
```bash
./pico_c_compiler -c -t -a -s -p -v -b 100 -e 200 -d 20 -S 2 ./code.picoc
```

# Starting Shell
Start the **shell** by passing **no arguments**. To compile **PicoC** into **RETI-Code use the `compile <cli-options> "<code>";` command:
```bash
./pico_c_compiler
PicoC> compile -c -t -a -s -p -v -b 100 -e 200 -d 20 -S 2 "char bool_val = (12 < 1 + 2);";

```
- **Leave** the **shell** again by typing `quit`.
