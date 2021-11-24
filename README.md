# Pico-C Compiler

## Usage
```
usage: pico_c_compiler.py [-h] [-p] [-a] [-t] [-s START_DATA_SEGMENT]
                          [-e END_DATA_SEGMENT] [-m] [-S]
                          [-O OPTIMIZATION_LEVEL] [-b] [-P] [-v]
                          [infile] [outfile]

Compiles Pico-C Code into RETI Code.
PicoC is a subset of C including while loops, if and else statements,
assignments, arithmetic and logic expressions.
All Code has to be written into a

void main() { /* your program */ }

main function.

If you discover any bugs I would be very grateful if you could report it
via email to juergmatth@gmail.com, attaching the malicious code to the
email ^_^

positional arguments:
  infile                input file with Pico-C Code
  outfile               output file with RETI Code

optional arguments:
  -h, --help            show this help message and exit
  -p, --print           output the file output to the terminal and if
                        --symbol_table is active output the symbol table
                        beneath
  -a, --ast             output the Abstract Syntax Tree instead of RETI Code
  -t, --tokens          output the Tokenlist instead of RETI Code
  -s START_DATA_SEGMENT, --start_data_segment START_DATA_SEGMENT
                        where the allocation of variables starts (default 100)
  -e END_DATA_SEGMENT, --end_data_segment END_DATA_SEGMENT
                        where the stackpointer starts (default 200)
  -m, --python_stracktrace_error_message
                        show python error messages with stacktrace
  -S, --symbol_table    output the final symbol table into a CSV file after
                        the whole Abstract Syntax Tree was visited
  -O OPTIMIZATION_LEVEL, --optimization-level OPTIMIZATION_LEVEL
                        set the optimiziation level of the compiler (0=save
                        all variables on the stack, 1=use graph coloring to
                        find the best assignment of variables to registers,
                        2=partially interpret expressions) [NOT IMPLEMENTED
                        YET]
  -b, --binary          produce binary encoded RETI code [NOT IMPLEMENTED YET]
  -P, --prefix-notation
                        write Abstract Syntax Tree in prefix notation [NOT
                        IMPLEMENTED YET]
  -v, --verbose         also show tokentypes in the ast, add comments to the
                        RETI Code and show more context around error messages
                        [NOT IMPLEMENTED YET]

```

## Used Resources
- After a rewrite of the whole codebase, the code is now based on the really
  great Lookahead Lexer Parser Patterns from [1], more precisely:
  - LL(1) Recursive-Descent Lexer (p. 31 et seq. from [1])
  - LL(k) Recursive-Descent Parser (p. 41 et seq. from [1])

[1] Parr, Terence. Language implementation patterns: create your own
domain-specific and general programming languages. Pragmatic Bookshelf, 2009.
