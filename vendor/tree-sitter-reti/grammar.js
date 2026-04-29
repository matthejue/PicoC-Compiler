/**
 * @file RETI assembly grammar for tree-sitter
 * @license MIT
 */

/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

module.exports = grammar({
  name: 'reti',

  extras: $ => [
    /\s/,
    $.comment,
  ],

  rules: {
    source_file: $ => seq(
      optional(field('filename', $.filename)),
      repeat($._line),
    ),

    _line: $ => choice(
      $.block,
      $.statement,
      $.directive,
    ),

    block: $ => prec.right(seq(
      field('label', $.label),
      ':',
      repeat($._block_line),
    )),

    _block_line: $ => choice(
      $.statement,
      $.directive,
    ),

    statement: $ => seq(
      choice(
        $.instruction,
        $.jump,
      ),
      optional(';'),
    ),

    comment: _ => token(seq('#', /[^\n]*/)),

    filename: _ => token(/[ -~]+\.reti(_blocks|_patch)?/),

    label: $ => $.symbol,

    immediate: _ => token(choice(
      '0',
      /-?[1-9][0-9]*/,
    )),

    string: _ => token(seq("'", /[^'\n]*/, "'")),

    symbol: _ => token(/[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)*/),

    register: _ => choice(
      'ACC',
      'IN1',
      'IN2',
      'PC',
      'SP',
      'BAF',
      'CS',
      'DS',
    ),

    argument: $ => choice(
      $.register,
      $.symbolic_operand,
      $.immediate,
    ),

    symbolic_operand: $ => choice(
      $.symbol,
      $.symbol_offset,
    ),

    symbol_offset: $ => prec.left(seq(
      field('base', $.symbol),
      field('operator', choice('+', '-')),
      field('offset', $.immediate),
    )),

    relation: _ => choice(
      '<',
      '<=',
      '>',
      '>=',
      '==',
      '!=',
      '_NOP',
    ),

    jump: $ => seq(
      'JUMP',
      optional(field('relation', $.relation)),
      field('target', $.jump_target),
    ),

    jump_target: $ => choice(
      $.immediate,
      $.symbolic_operand,
      $.goto_target,
    ),

    goto_target: $ => seq(
      'GoTo',
      '(',
      field('target', $.name_target),
      ')',
    ),

    name_target: $ => seq(
      'Name',
      '(',
      field('value', $.string),
      ')',
    ),

    instruction: $ => choice(
      $.register_argument_instruction,
      $.register_immediate_instruction,
      $.indexed_memory_instruction,
      $.move_instruction,
      $.interrupt_instruction,
      $.return_from_interrupt_instruction,
    ),

    register_argument_opcode: _ => choice(
      'ADD',
      'SUB',
      'MULT',
      'DIV',
      'MOD',
      'OPLUS',
      'OR',
      'AND',
    ),

    register_immediate_opcode: _ => choice(
      'ADDI',
      'SUBI',
      'MULTI',
      'DIVI',
      'MODI',
      'OPLUSI',
      'ORI',
      'ANDI',
      'LOAD',
      'LOADI',
      'STORE',
    ),

    indexed_memory_opcode: _ => choice(
      'LOADIN',
      'STOREIN',
    ),

    register_argument_instruction: $ => seq(
      field('opcode', $.register_argument_opcode),
      field('left', $.register),
      field('right', $.argument),
    ),

    register_immediate_instruction: $ => seq(
      field('opcode', $.register_immediate_opcode),
      field('register', $.register),
      field('value', choice(
        $.immediate,
        $.symbolic_operand,
      )),
    ),

    indexed_memory_instruction: $ => seq(
      field('opcode', $.indexed_memory_opcode),
      field('base', $.argument),
      field('index', $.argument),
      field('offset', choice(
        $.immediate,
        $.symbolic_operand,
      )),
    ),

    move_instruction: $ => seq(
      field('opcode', 'MOVE'),
      field('target', $.register),
      field('source', $.register),
    ),

    interrupt_instruction: $ => seq(
      field('opcode', 'INT'),
      field('value', $.immediate),
    ),

    return_from_interrupt_instruction: $ => 'RTI',

    directive: $ => prec.right(seq(
      field('name', $.directive_name),
      repeat1(field('argument', $.directive_argument)),
    )),

    directive_name: _ => token(/\.[A-Za-z_][A-Za-z0-9_]*/),

    directive_argument: $ => choice(
      $.register,
      $.immediate,
      $.string,
      $.symbolic_operand,
    ),
  },
});
