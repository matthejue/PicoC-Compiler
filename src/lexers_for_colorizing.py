#!/usr/bin/env python

from pygments.lexer import RegexLexer, bygroups
from pygments.token import *
from pygments.token import Token
from pygments.formatters.terminal import TerminalFormatter
from pygments.formatters import HtmlFormatter
from pygments import highlight

# resources: https://pygments.org/docs/lexerdevelopment/
# https://pygments.org/docs/api/#module-pygments.lexer
# https://docs.python.org/3/library/re.html#regular-expression-syntax
# https://pygments.org/docs/styledevelopment/#creating-own-styles
# https://pygments.org/docs/lexers/
# https://pygments.org/docs/formatters/#TerminalFormatter


class TokenLexer(RegexLexer):
    name = "Tokens"
    aliases = ["tokens"]
    filenames = ["*.tokens"]

    # TODO: korrigieren sobald chars gescheit umgesetzt
    tokens = {
        "root": [
            (r"\[", String.Delimiter),
            (
                r"(Token)(\()('[^']*')(,)( )('[^']*'|\"[^\"]*\")(\))",
                bygroups(
                    Keyword,
                    String.Delimiter,
                    Name.Variable,
                    Punctuation,
                    Whitespace,
                    Name.Attribute,
                    String.Delimiter,
                ),
            ),
            (r",", Punctuation),
            (r" ", Whitespace),
            (r"\]\n", String.Delimiter),
        ],
    }


class DTLexer(RegexLexer):
    name = "Derivation Tree"
    aliases = ["dt"]
    filenames = ["*.dt"]

    tokens = {
        "root": [
            (r" *[^ \n]+", Name.Variable, "node"),
        ],
        "node": [
            (r" *[^\n]+\n", Name.Attribute, "#pop"),
            (r" *\n", Whitespace, "#pop"),
        ],
    }


class RETILexer(RegexLexer):
    name = "RETI"
    aliases = ["reti"]
    filenames = ["*.reti"]

    tokens = {
        "root": [
            (r" *#[^\n]+\n", Comment),
            (
                r" *(CALL)( )(INPUT|PRINT)( )([^ \n]+)(\n)",
                bygroups(
                    Keyword,
                    Whitespace,
                    Name.Tag,
                    Whitespace,
                    Name,
                    Whitespace,
                ),
            ),
            (
                r" *(JUMP)([^ \n]*)( )([^ \n]+)(\n)",
                bygroups(
                    Keyword,
                    Operator,
                    Whitespace,
                    Number,
                    Whitespace,
                ),
            ),
            (
                r" *([^ \n]+)( )([^ \n]+)( )([^ \n]+)(\n)",
                bygroups(
                    Keyword,
                    Whitespace,
                    Name,
                    Whitespace,
                    Number,
                    Whitespace,
                ),
            ),
            (
                r" *([^ \n]+)( )([^ \n]+)( )([^ \n]+)( )([^ \n]+)(\n)",
                bygroups(
                    Keyword,
                    Whitespace,
                    Name,
                    Whitespace,
                    Name,
                    Whitespace,
                    Number,
                    Whitespace,
                ),
            ),
        ],
    }
    # tokens = {
    #     "root": [
    #         (r" *#[^\n]+\n", Comment),
    #         (
    #             r" *(CALL)( )(INPUT|PRINT)( )([^ ]+)(;)(\n?)",
    #             bygroups(
    #                 Keyword,
    #                 Whitespace,
    #                 Name.Tag,
    #                 Whitespace,
    #                 Name,
    #                 Punctuation,
    #                 Whitespace,
    #             ),
    #         ),
    #         (
    #             r" *(JUMP)([^ ]*)( )([^ ]+)(;)(\n?)",
    #             bygroups(
    #                 Keyword,
    #                 Operator,
    #                 Whitespace,
    #                 Number,
    #                 Punctuation,
    #                 Whitespace,
    #             ),
    #         ),
    #         (
    #             r" *([^ ]+)( )([^ ]+)( )([^ ]+)(;)(\n?)",
    #             bygroups(
    #                 Keyword,
    #                 Whitespace,
    #                 Name,
    #                 Whitespace,
    #                 Number,
    #                 Punctuation,
    #                 Whitespace,
    #             ),
    #         ),
    #         (
    #             r" *([^ ]+)( )([^ ]+)( )([^ ]+)( )([^ ]+)(;)(\n?)",
    #             bygroups(
    #                 Keyword,
    #                 Whitespace,
    #                 Name,
    #                 Whitespace,
    #                 Name,
    #                 Whitespace,
    #                 Number,
    #                 Punctuation,
    #                 Whitespace,
    #             ),
    #         ),
    #     ],
    # }


if __name__ == "__main__":
    print(
        highlight(
            "LOADIN BAF PC 1\n",
            RETILexer(),
            TerminalFormatter(
                colorscheme={
                    Comment: ("magenta", "brightmagenta"),
                    Whitespace: ("gray", "white"),
                    Keyword: ("blue", "brightblue"),
                    Punctuation: ("gray", "white"),
                    Name: ("cyan", "brightcyan"),
                    Number: ("red", "brightred"),
                    Name.Tag: ("green", "brightgreen"),
                    Operator: ("yellow", "brightyellow"),
                }
            ),
        ),
    )
#      print(
#          highlight(
#              "[Token('FILENAME', './stdin.picoc'), Token('VOID_DT', 'void'), Token('NAME', 'main'), Token('LPAR', '('), Token('RPAR', ')'), Token('LBRACE', '{'), Token('WHILE', 'while'), Token('LPAR', '('), Token('NUM', '0'), Token('RPAR', ')'), Token('LBRACE', '{'), Token('PRINT', 'print'), Token('LPAR', '('), Token('NUM', '1'), Token('ADD', '+'), Token('NUM', '1'), Token('RPAR', ')'), Token('SEMICOLON', ';'), Token('RBRACE', '}'), Token('RBRACE', '}')]",
#              TokenLexer(),
#              TerminalFormatter(
#                  colorscheme={
#                      Whitespace: ("gray", "white"),
#                      Keyword: ("blue", "brightblue"),
#                      Punctuation: ("gray", "white"),
#                      String.Delimiter: ("cyan", "brightcyan"),
#                      Name.Variable: ("green", "brightgreen"),
#                      Name.Attribute: ("red", "brightred"),
#                      Name.Tag: ("blue", "brightblue"),
#                  }
#              ),
#              outfile=None,
#          )
#      )
#
#      print(
#          highlight(
#              """file
#                ./stdin.dt_simple
#                decls_defs
#                  decl_def
#                    fun_def
#                      type_spec
#                        prim_dt       void
#                      pntr_deg
#                      name    main
#                      fun_params
#                      decl_exec_stmts
#                        exec_part
#                          exec_direct_stmt
#                            while_stmt
#                              logic_or
#                                logic_and
#                                  eq_exp
#                                    rel_exp
#                                      arith_or
#                                        arith_oplus
#                                          arith_and
#                                            arith_prec2
#                                              arith_prec1
#                                                un_exp
#                                                  post_exp
#                                                    prim_exp  0
#                              exec_part
#                                compound_stmt
#                                  exec_part
#                                    exec_exp_stmt
#                                      logic_or
#                                        logic_and
#                                          eq_exp
#                                            rel_exp
#                                              arith_or
#                                                arith_oplus
#                                                  arith_and
#                                                    arith_prec2
#                                                      arith_prec1
#                                                        un_exp
#                                                          post_exp
#                                                            print_exp
#                                                              logic_or
#                                                                logic_and
#                                                                  eq_exp
#                                                                    rel_exp
#                                                                      arith_or
#                                                                        arith_oplus
#                                                                          arith_and
#                                                                            arith_prec2
#                                                                              arith_prec2
#                                                                                arith_prec1
#                                                                                  un_exp
#                                                                                    post_exp
#                                                                                      prim_exp        1
#                                                                              prec2_op        +
#                                                                              arith_prec1
#                                                                                un_exp
#                                                                                  post_exp
#                                                                                    prim_exp  1""",
#              DTLexer(),
#              TerminalFormatter(
#                  colorscheme={
#                      Whitespace: ("gray", "white"),
#                      Keyword: ("blue", "brightblue"),
#                      Punctuation: ("gray", "white"),
#                      String.Delimiter: ("cyan", "brightcyan"),
#                      Name.Variable: ("green", "brightgreen"),
#                      Name.Attribute: ("red", "brightred"),
#                  }
#              ),
#              outfile=None,
#          )
#      )
#
#      print(
#          highlight(
#              #  """LOADI ACC 1;
#              #  ADDI ACC 1;
#              #  LOADIN ACC IN1 2;
#              #  # asdfadsf
#              #  CALL INPUT ACC;
#              #  ## asdfadsf
#              #  CALL PRINT ACC;""",
#              """
#              ## begin
#              CALL INPUT ACC;
#              SUBI SP 1;
#              STOREIN SP ACC 1;
#              LOADIN SP ACC 1;
#              STOREIN DS ACC 0;
#              ADDI SP 1;
#              ## this should be visible
#              ## this should be visible
#              SUBI SP 1;
#              LOADIN DS ACC 0;
#              STOREIN SP ACC 1;
#              LOADIN SP ACC 1;
#              ADDI SP 1;
#              CALL PRINT ACC;
#              ## end
#              LOADIN BAF PC -1;""",
#              RETILexer(),
#              #  HtmlFormatter(debug_token_types=True),
#              TerminalFormatter(
#                  colorscheme={
#                      Comment: ("magenta", "brightmagenta"),
#                      Whitespace: ("gray", "white"),
#                      Keyword: ("blue", "brightblue"),
#                      Punctuation: ("gray", "white"),
#                      Name: ("cyan", "brightcyan"),
#                      Number: ("red", "brightred"),
#                      Name.Tag: ("green", "brightgreen"),
#                  }
#              ),
#              outfile=None,
#          )
#      )
