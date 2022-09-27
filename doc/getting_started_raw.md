# Compiling a file directly

- Click on the **image** to see a short **tutorial** showcasing how to **compile a file**.

<a href="https://asciinema.org/a/524089" target="_blank"><img src="https://asciinema.org/a/524089.svg" /></a>

- With the following **cli-options** you won't miss anything when compiling **PicoC** into **RETI-Code**:

```bash
./picoc_compiler most_used_interpret_opts /code.picoc
```

# Compiling via shell mode

- Click on the **image** to see a short **tutorial** showcasing the **shell mode**.

<a href="https://asciinema.org/a/524088" target="_blank"><img src="https://asciinema.org/a/524088.svg" /></a>

- Start the **shell** by passing **no arguments**. To compile **PicoC** into **RETI-Code** use the `compile <cli-options> "<code>";` command (shortcut `cpl`):
```bash
./picoc_compiler
PicoC> compile most_used_interpret_opts "char bool_val = ('c' < 1 + 2);";
PicoC> most_used "char bool_val = ('c' < 1 + 2);";
```
- To **save** the **effort** of writing this command with all it's options everytime, one can also use the `most_used "<code>";` command (shortcut `mu`) which executes the command above with the exact **same options**, so only the string with the PicoC-Code has to be passed.
- One can **leave** the **shell** again by typing `quit`.

# Watching execution via show mode

- Click on the **image** to see a short **tutorial** showcasing the **show mode**.


