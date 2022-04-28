# Abstract Syntax
## L_Arith
```
exp ::= Name(str) | Num(str) | Char(str)
unary_op ::= Minus() | Not()
bin_op ::= Add() | Sub() | Mul() | Div() | Mod() | Oplus() | And() | Or()
exp ::= ArithBinOp(<exp>, <bin_op>, <exp>) | ArithUnaryOp(<unary_op>, <exp>)
exp ::= Call(Name('input'), $\empty$)
stmt ::= Call(Name('print'), <exp>)
```
## L_Logic
```
relation ::= Eq() | NEq() | Lt() | LtE() | Gt() | GtE()
logic_op ::= LogicAnd() | LogicOr()
exp ::= LogicBinOp(<exp>, <logic_op>, <exp>) | LogicNot(<exp>) | LogicAtom(<exp>, <relation>, <exp>) | ToBool(<exp>)
```
## L_Assign_Alloc
```
type_qual ::= Const() | Writeable()
size_qual ::= IntType() | CharType() | VoidType()
stmt ::= Assign(Name(str), <exp>) | Alloc(<type_qual>, <size_qual>, Name(str))
```
## L_Pointer
```
size_qual ::= PointerType(<size_qual>)
exp ::= Ref(Name(str)) | Deref(<exp>)
exp ::= Ref(Deref(<exp>))
stmt ::= Assign(Deref(<exp>), <exp>)
```
## L_Array
```
size_qual ::= ArrayType(<size_qual>, Num(str))
exp ::= Array(<size_qual>, <exp>+) | Subscript(Name(str), <exp>)
exp ::= Ref(Subscript(Name(str), <exp>))
stmt ::= Assign(Subscript(Name(str), <exp>), <exp>)
```
## L_Struct
```
size_qual ::= StructType(Name(str))
exp ::= Struct(Assign(Name(str), <exp>)+) | Attribute(Name(str), Name(str))
exp ::= Ref(Attribute(Name(str), Name(str)))
stmt ::= StructDef(Name(str), Param(Name(str), <size_qual>)+) | Assign(Attribute(Name(str), Name(str)), <exp>)
```
## L_If_Else
```
stmt ::= If(<exp>, <stmt>\*) | IfElse(<exp>, <stmt>\*, Else(), <stmt>\*)
```
## L_Loop
```
stmt ::= While(<exp>, <stmt>*) | DoWhile(<exp>, <stmt>\*)
```
## L_Fun
```
size_qual ::= FunType(<size_qual>)
exp ::= Call(Name(str), <exp>*)
stmt ::= Return(<exp>) | Exp(Call(Name(str), <exp>*))
def ::= FunDef(Name(str), Param(Name(str), <size_qual>)*, <size_qual>, <stmt>\*)
```
## L_PicoC
```
picoc ::= File(Name(str), <def>*)
```

<!-- # L_PicoC -->
<!-- ## Concrete Syntax -->
<!-- ### L_Arith -->
<!-- ``` -->
<!-- dig_no_0 := 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 -->
<!-- dig_with_0 := 0 | <dig_no_0> -->
<!-- num := 0 | <dig_no_0><dig_with_0>* -->
<!-- letter := a | b | ... | y | z | A | B | ... | Y | Z -->
<!-- char := '<letter>' -->
<!-- name := [<letter> | _][<letter> | <dig_with_0> | _]\* -->
<!-- ------------------------------------------------------------------------------- -->
<!-- unary_op := - | ~ -->
<!-- !arith_opd := <name> | <num> | <char> | <unary_op>+ <arith_opd> | (<arith_exp_logic_exp>) | input() -->
<!-- prec1_op := \* | / | % -->
<!-- prec2_op := + | - | ^ | & | | -->
<!-- prec1 := <arith_opd> [<prec1_op> <arith_opd>]* -->
<!-- prec2 := <prec1> [<prec2_op> <prec1>]* -->
<!-- arith_exp := <prec2> -->
<!-- !stmt := print(<arith_exp>) -->
<!-- !arith_stmt := <prec2> -->
<!-- ``` -->
<!-- ### L_Logic -->
<!-- ``` -->
<!-- relation := == | != | < | <= | > | >= -->
<!-- !logic_opd := !+<logic_opd> | (<logic_exp>) | <arith_exp> | <logic_opd> <relation> <logic_opd> -->
<!-- and_exp := <logic_opd> [&& <logic_opd>)]* -->
<!-- or_exp := <and_exp> [|| <and_exp>]* -->
<!-- logic_exp := <or_exp> -->
<!-- arith_exp_logic_exp :=  <arith_exp> | <logic_exp> -->
<!-- ``` -->
<!-- ### L_Assign_Alloc -->
<!-- ``` -->
<!-- size_qual := int | char | void -->
<!-- stmt := <size_qual> <name> | [const]? <size_qual> <name> = <num> | <name> = <arith_exp_logic_exp> -->
<!-- ``` -->
<!-- - [const]? <size_qual> <name> = <num> da muss noch was geändert werden -->
<!-- ### L_Pointer -->
<!-- ``` -->
<!-- size_qual := <size_qual>\* -->
<!-- arith_opd := &<name> | \*<arith_exp_logic_exp> -->
<!-- arith_opd := &\*<arith_exp_logic_exp> -->
<!-- stmt := \*<name> = <arith_exp_logic_exp> -->
<!-- ``` -->
<!-- ### L_Array -->
<!-- ``` -->
<!-- size_qual := <size_qual>[\[<num>\]] -->
<!-- arith_opd := {[<arith_exp_logic_exp>,]+} | <name>[<arith_exp_logic_exp>] -->
<!-- arith_opd := &<name>[<arith_exp_logic_exp>] -->
<!-- stmt := <name>[<arith_exp_logic_exp>] = <arith_exp_logic_exp> -->
<!-- ``` -->
<!-- ### L_Struct -->
<!-- ``` -->
<!-- size_qual := struct <name> -->
<!-- arith_opd := {[.<name>=<arith_exp_logic_exp>,]+} | <name>.<name> -->
<!-- arith_opd := &<name>.<name> -->
<!-- stmt := struct <name> {[<size_qual> <name>;]+} | <name>.<name> = <arith_exp_logic_exp> -->
<!-- ``` -->
<!-- ### L_If_Else -->
<!-- ``` -->
<!-- stmt := if(<arith_exp_logic_exp>){<stmt>\*} | if(<arith_exp_logic_exp>){<stmt>\*} else {<stmt>\*} | if(<arith_exp_logic_exp>){<stmt>\*} else <stmt> -->
<!-- ``` -->
<!-- ### L_Loop -->
<!-- ``` -->
<!-- stmt := while(<arith_exp_logic_exp>){<stmt>\*} | do{<stmt>\*}while(<arith_exp_logic_exp>); -->
<!-- ``` -->
<!-- ### L_Fun -->
<!-- ``` -->
<!-- size_qual := <size_qual> fun -->
<!-- arith_opd := <name>([<arith_exp_logic_exp>,]\*) -->
<!-- stmt := return <arith_exp_logic_exp> | <name>([<arith_exp_logic_exp>,]\*) -->
<!-- !def := <size_qual> <name>([<size_qual> <name>,]\*){<stmt>\*} -->
<!-- ``` -->
<!-- ### L_PicoC -->
<!-- ``` -->
<!-- L\_PicoC := <name> <def>\* -->
<!-- ``` -->
