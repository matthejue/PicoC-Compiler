# Pico-C Compiler

## Usage
```
usage: pico_c_compiler.py [-h] [-p] [-a] [-t] [-v] [infile] [outfile]

Compiles Pico-C Code into RETI Code.

positional arguments:
  infile         Input file with Pico-C Code
  outfile        Output file with RETI Code

optional arguments:
  -h, --help     show this help message and exit
  -p, --print    Also output the file output to the terminal
  -a, --ast      Output the Abstract Syntax Tree instead of RETI Code
  -t, --tokens   Output the Tokenlist instead of RETI Code
  -v, --verbose  Create verbose output for the ast
```

## Used Resources
- After a rewrite of the whole codebase, the code is now based on the really
  great Lookahead Lexer Parser Patterns from [1], more precisely:
  - LL(1) Recursive-Descent Lexer (p. 31 et seq. from [1])
  - LL(k) Recursive-Descent Parser (p. 41 et seq. from [1])

[1] Parr, Terence. Language implementation patterns: create your own
domain-specific and general programming languages. Pragmatic Bookshelf, 2009.
