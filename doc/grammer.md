# L_PicoC
## Abstract Syntax
### L_Arith
```
dig_no_0 := 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
dig_with_0 := 0 | <dig_no_0>
num := 0 | <dig_no_0><dig_with_0>*
letter := a | b | ... | y | z | A | B | ... | Y | Z
char := '<letter>'
name := [<letter> | _][<letter> | <dig_with_0> | _]\*
-------------------------------------------------------------------------------
unary_op := - | ~
arith_opd := <name> | <num> | <char> | <unary_op>+ <arith_opd> | (<arith_logic_exp>) | input()
prec1_op := \* | / | %
prec2_op := + | - | ^ | & | |
prec1 := <arith_opd> [<prec1_op> <arith_opd>]*
prec2 := <prec1> [<prec2_op> <prec1>]*
arith_exp := <prec2>
stmt := print(<arith_exp>)
arith_stmt := <prec2>
```
### L_Logic
```
rel := == | != | < | <= | > | >=
logic_opd := !+<logic_opd> | (<logic_exp>) | <arith_exp> | <arith_exp> <rel> <arith_exp>
and_exp := <logic_op> [&& <logic_op>)]*
or_exp := <and_exp> [|| <and_exp>]*
logic_exp := <or_exp>
arith_logic_exp :=  <arith_exp> | <logic_exp>
```
### L_Assign_Alloc
```
type_qual := Const() | Writeable()
size_qual := IntType() | CharType() | VoidType()
stmt := Assign(Name(str), <exp>) | Alloc(<type_qual>, <size_qual>, <exp>)
```
### L_Pointer
```
size_qual := PointerType()
exp := Ref(Name(str), <exp>) | Ref(Deref(Name(str), <exp>), <exp>) | Deref(Name(str), <exp>)
stmt := Assign(Deref(Name(str), <exp>), <exp>)
```
### L_Array
```
size_qual := ArrayType()
exp := Array(<exp>+, <size_qual>) | Subscript(Name(str), <exp>)
exp := Ref(Subscript(Name(str), <exp>), <exp>)
stmt := Assign(Subscript(Name(str), <exp>), <exp>)
```
### L_Struct
```
size_qual := StructType(Name(str))
exp := Struct(Assign(Attribute(Name(str), <exp>), <exp>)+) | Attribute(Name(str), Name(str))
exp := Ref(Attribute(Name(str), Name(str)), <exp>)
stmt := StructDef(Name(str), Param(Name(str), <size_qual>)+) | Assign(Attribute(Name(str), <exp>), <exp>)
```
### L_If_Else
```
stmt := If(<exp>, <stmt>\*) | IfElse(<exp>, <stmt>\*, Else(), <stmt>\*)
```
### L_Loop
```
stmt := While(<exp>, <stmt>\*) | DoWhile(<exp>, <stmt>\*)
```
### L_Fun
```
size_qual := FunType()
def := FunDef(Name(str), Param(Name(str), <size_qual>)\*, <size_qual>, <stmt>\*) | Return(<exp>) | Call(Name(str), <exp>\*) | Call(Name(str), <exp>\*)
```
### L_PicoC
```
L\_PicoC := File(Name(str), <def>\*)
```

## Abstract Syntax
### L_Arith
```
exp := Name(str) | Num(str) | Char(str)
unary_op := Minus() | Not()
bin_op := Add() | Sub() | Mul() | Div() | Mod() | Oplus() | And() | Or()
exp := ArithBinOp(<exp>, <bin_op>, <exp>) | ArithUnaryOp(<unary_op>, <exp>)
exp := Call(Name('input'), $\empty$)
stmt := Call(Name('print'), <exp>)
```
### L_Logic
```
rel := Eq() | NEq() | Lt() | LtE() | Gt() | GtE()
logic_op := LogicAnd() | LogicOr()
exp := LogicBinOp(<exp>, <logic_op>, <exp>) | LogicNot(<exp>) | LogicAtom(<exp>, <rel>, <exp>) | ToBool(<exp>)
```
### L_Assign_Alloc
```
type_qual := Const() | Writeable()
size_qual := IntType() | CharType() | VoidType()
stmt := Assign(Name(str), <exp>) | Alloc(<type_qual>, <size_qual>, <exp>)
```
### L_Pointer
```
size_qual := PointerType()
exp := Ref(Name(str), <exp>) | Ref(Deref(Name(str), <exp>), <exp>) | Deref(Name(str), <exp>)
stmt := Assign(Deref(Name(str), <exp>), <exp>)
```
### L_Array
```
size_qual := ArrayType()
exp := Array(<exp>+, <size_qual>) | Subscript(Name(str), <exp>)
exp := Ref(Subscript(Name(str), <exp>), <exp>)
stmt := Assign(Subscript(Name(str), <exp>), <exp>)
```
### L_Struct
```
size_qual := StructType(Name(str))
exp := Struct(Assign(Attribute(Name(str), <exp>), <exp>)+) | Attribute(Name(str), Name(str))
exp := Ref(Attribute(Name(str), Name(str)), <exp>)
stmt := StructDef(Name(str), Param(Name(str), <size_qual>)+) | Assign(Attribute(Name(str), <exp>), <exp>)
```
### L_If_Else
```
stmt := If(<exp>, <stmt>\*) | IfElse(<exp>, <stmt>\*, Else(), <stmt>\*)
```
### L_Loop
```
stmt := While(<exp>, <stmt>\*) | DoWhile(<exp>, <stmt>\*)
```
### L_Fun
```
size_qual := FunType()
def := FunDef(Name(str), Param(Name(str), <size_qual>)\*, <size_qual>, <stmt>\*) | Return(<exp>) | Call(Name(str), <exp>\*) | Call(Name(str), <exp>\*)
```
### L_PicoC
```
L\_PicoC := File(Name(str), <def>\*)
```
