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
      repeat($.statement),
    ),

    statement: $ => seq(
      choice(
        $.instruction,
        $.jump,
      ),
      optional(';'),
    ),

    comment: _ => token(seq('#', /[^\n]*/)),

    filename: _ => token(/[ -~]+\.reti/),

    immediate: _ => token(choice(
      '0',
      /-?[1-9][0-9]*/,
    )),

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
      $.immediate,
    ),

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
      field('target', $.immediate),
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
      field('value', $.immediate),
    ),

    indexed_memory_instruction: $ => seq(
      field('opcode', $.indexed_memory_opcode),
      field('base', $.argument),
      field('index', $.argument),
      field('offset', $.immediate),
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
  },
});
