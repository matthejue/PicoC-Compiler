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
      repeat(choice(
        $.block,
        $.statement,
      )),
    ),

    comment: _ => token(seq('#', /[^\n]*/)),

    filename: _ => token(/[ -~]+\.reti(_blocks|_patch)?/),

    block: $ => seq(
      field('label', $.label),
      ':',
      repeat($.directive),
      repeat($.statement),
    ),

    label: $ => $.symbol,

    directive: $ => seq(
      field('name', $.directive_name),
      field('argument', $.directive_argument),
    ),

    directive_name: _ => choice(
      '.scope',
      '.instrs_before',
      '.num_instrs',
      '.block_idx',
      '.param_size',
      '.local_vars_size',
    ),

    directive_argument: $ => choice(
      $.immediate,
      $.string,
      $.symbol,
    ),

    statement: $ => seq(
      choice(
        $.instruction,
        $.jump,
      ),
      optional(';'),
    ),

    instruction: $ => choice(
      $.load_instruction,
      $.store_or_move_instruction,
      $.compute_instruction,
      $.syscall_instruction,
      $.return_from_interrupt_instruction,
    ),

    load_instruction: $ => choice(
      $.load_immediate_instruction,
      $.load_indexed_instruction,
    ),

    load_immediate_instruction: $ => seq(
      field('opcode', $.load_immediate_opcode),
      field('register', $.register),
      field('value', choice(
        $.immediate,
        $.symbolic_operand,
      )),
    ),

    load_immediate_opcode: _ => choice(
      'LOAD',
      'LOADI',
    ),

    load_indexed_instruction: $ => seq(
      field('opcode', 'LOADIN'),
      field('base', $.argument),
      field('index', $.argument),
      field('offset', choice(
        $.immediate,
        $.symbolic_operand,
      )),
    ),

    store_or_move_instruction: $ => choice(
      $.store_instruction,
      $.store_indexed_instruction,
      $.tsl_instruction,
      $.move_instruction,
    ),

    store_instruction: $ => seq(
      field('opcode', 'STORE'),
      field('register', $.register),
      field('value', choice(
        $.immediate,
        $.symbolic_operand,
      )),
    ),

    store_indexed_instruction: $ => seq(
      field('opcode', 'STOREIN'),
      field('base', $.argument),
      field('index', $.argument),
      field('offset', choice(
        $.immediate,
        $.symbolic_operand,
      )),
    ),

    tsl_instruction: $ => seq(
      field('opcode', 'TSL'),
      field('source', $.argument),
      field('target', $.register),
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

    compute_instruction: $ => choice(
      $.compute_register_instruction,
      $.compute_immediate_instruction,
    ),

    compute_register_instruction: $ => seq(
      field('opcode', $.register_argument_opcode),
      field('left', $.register),
      field('right', $.argument),
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

    compute_immediate_instruction: $ => seq(
      field('opcode', $.register_immediate_opcode),
      field('register', $.register),
      field('value', choice(
        $.immediate,
        $.symbolic_operand,
      )),
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
    ),

    syscall_instruction: $ => $.interrupt_instruction,

    interrupt_instruction: $ => seq(
      field('opcode', 'INT'),
      field('value', $.immediate),
    ),

    return_from_interrupt_instruction: $ => 'RTI',

    jump: $ => seq(
      'JUMP',
      optional(field('relation', $.relation)),
      field('target', $.jump_target),
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

    argument: $ => choice(
      $.register,
      $.symbolic_operand,
      $.immediate,
    ),

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

    symbolic_operand: $ => choice(
      $.symbol,
      $.symbol_offset,
    ),

    immediate: _ => token(choice(
      '0',
      /-?[1-9][0-9]*/,
    )),

    string: _ => token(seq("'", /[^'\n]*/, "'")),

    symbol: _ => token(/[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)?/),

    symbol_offset: $ => seq(
      field('base', $.symbol),
      field('operator', choice('+', '-')),
      field('offset', $.immediate),
    ),
  },
});
