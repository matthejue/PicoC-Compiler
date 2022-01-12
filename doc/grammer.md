# Logic grammar (code_le)
# Concrete Syntax
<code_le> = <pred_2>
<pred_2> =  <pred_1> '||' <pred_1>
<pred_1> = <logic_operand> '&&' <logic_operand>
<logic_operand> = !<logic_operand> | (<code_le>) | <code_ae> | <code_ae> <cmp> <code_ae>
<cmp> = '<' | '>' | '<=' | '>=' | '==' | '!='

# Abstract Syntax
<code_le> = LogicBinaryOperation(<logic_operand>, <logic_connective>, <logic_operand>)
<logic_operand> = Not(<logic_operand>) | <code_le> | ToBool(<code_ae>) | Atom(<code_ae>, <cmp>, <code_ae>)
<logic_connective> = LAnd() | LOr()
<cmp> = Lt() | Gt() | Le() | Ge() | Eq() | UEq()


ae zu at = arithmetic_term umbennenen
arithmetic_term_grammar umbenennen
