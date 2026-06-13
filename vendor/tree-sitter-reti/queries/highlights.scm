(comment) @comment

(immediate) @number

(string) @string

(register) @constant.builtin

[
  (register_argument_opcode)
  (register_immediate_opcode)
  (load_immediate_opcode)
  (directive_name)
  (section_name)
] @keyword

(store_instruction "STORE" @keyword)

(load_indexed_instruction "LOADIN" @keyword)

(store_indexed_instruction "STOREIN" @keyword)

(tsl_instruction "TSL" @keyword)

(move_instruction "MOVE" @keyword)

(push_instruction "PUSH" @keyword)

(pop_instruction "POP" @keyword)

(interrupt_instruction "INT" @keyword)

(ivte_instruction "IVTE" @keyword)

(nop_instruction) @keyword

(jump "JUMP" @keyword)

(return_from_interrupt_instruction) @keyword

(symbol) @variable

(block
  label: (label
    (symbol) @label))

(relation) @operator
