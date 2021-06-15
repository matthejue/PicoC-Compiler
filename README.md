# Pico-C Compiler

## Usage
```
usage: pico_c_compiler.py [-h] [-p] [-a] [-t] [infile] [outfile]

Compiles Pico-C Code into RETI Code.

positional arguments:
  infile        Input file with Pico-C Code
  outfile       Output file with RETI Code

optional arguments:
  -h, --help    show this help message and exit
  -p, --print   Print the file output also out to the terminal
  -a, --ast     Output the Abstract Syntax Tree instead of RETI Code
  -t, --tokens  Output the Tokenlist instead of RETI Code
```
