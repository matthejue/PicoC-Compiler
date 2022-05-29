# Compiling a file
With the following **cli-options** you won't miss anything when compiling **PicoC** into **RETI-Code**:
```bash
./picoc_compiler -i -p -l 2 -R -B 8 -D 32 -U 4 -S 0 /code.picoc
```

# Compiling via shell
Start the **shell** by passing **no arguments**. To compile **PicoC** into **RETI-Code** use the `compile <cli-options> "<code>";` command (shortcut `cpl`):
```bash
./picoc_compiler
PicoC> compile -i -p -l 2 -R -B 8 -D 32 -U 4 -S 0 "char bool_val = ('c' < 1 + 2);";
PicoC> most_used "char bool_val = ('c' < 1 + 2);";
```
- To **save** the **effort** of writing this command with all it's options everytime, one can also use the `most_used "<code>";` command (shortcut `mu`) which executes the command above with the exact **same options**, so only the string with the PicoC-Code has to be passed.
- One can **leave** the **shell** again by typing `quit`.
