# L_PicoC
## Concrete Syntax
### L_Arith
### L_Logic
### L_Assign_Alloc
### L_If_Else
### L_Loop
### L_Stmts
### L_Fun
### L_PicoC

## Abstract Syntax
### L_Arith
```
exp := Name(str) | Num(str) | Char(str)
unary_op := Minus() | Not()
bin_op := Add() | Sub() | Mul() | Div() | Mod() | Oplus() | And() | Or()
exp := ArithBinOp(exp, bin_op, exp) | ArithUnaryOp(exp, unary_op, exp)
exp := Call(Name('input'), $\empty$)
stmt := Call(Name('print'), exp)
```
### L_Logic
```
rel := Eq() | NEq() | Lt() | LtE() | Gt() | GtE()
logic_op := LogicAnd() | LogicOr()
exp := LogicBinOp(exp, logic_op, exp) | LogicNot(exp) | LogicAtom(exp, rel, exp) | ToBool(exp)
```
### L_Pointer
```
size_qual := PointerType()
exp := Ref(Name(str), exp) | Ref(Deref(Name(str), exp), exp) | Deref(Name(str), exp)
stmt := Assign(Deref(Name(str), exp), exp)
```
### L_Array
```
size_qual := ArrayType()
exp := Array(exp+, size_qual) | Subscript(Name(str), exp)
exp := Ref(Subscript(Name(str), exp), exp)
stmt := Assign(Subscript(Name(str), exp), exp)
```
### L_Struct
```
size_qual := StructType(Name(str))
exp := Struct(Assign(Attribute(Name(str), exp), exp)+) | Attribute(Name(str), Name(str))
exp := Ref(Attribute(Name(str), Name(str)), exp)
stmt := StructDef(Name(str), Param(Name(str), size_qual)+) | Assign(Attribute(Name(str), exp), exp)
```
### L_Assign_Alloc
```
type_qual := Const() | Writeable()
size_qual := IntType() | CharType() | VoidType()
stmt := Assign(Name(str), exp) | Alloc(type_qual, size_qual, exp)
```
### L_If_Else
```
stmt := If(exp, stmt\*) | IfElse(exp, stmt\*, Else(), stmt\*)
```
### L_Loop
```
stmt := While(exp, stmt\*) | DoWhile(exp, stmt\*)
```
### L_Fun
```
size_qual := FunType()
def := FunDef(Name(str), Param(Name(str), size_qual)\*, size_qual, stmt\*) | Return(exp) | Call(Name(str), exp\*) | Call(Name(str), exp\*)
```
### L_PicoC
```
L\_PicoC := File(Name(str), def\*)
```
