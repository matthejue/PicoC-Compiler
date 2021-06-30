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

## Used Resources
- After a rewrite of the whole codebase, the code is now based on the really
  great Lookahead Lexer Parser Patterns from [1], more precisely:
  - LL(1) Recursive-Descent Lexer (p. 31 from [1])
  - LL(k) Recursive-Descent Parser (p. 41 from [1])

[1] Parr, Terence. Language implementation patterns: create your own
domain-specific and general programming languages. Pragmatic Bookshelf, 2009.
