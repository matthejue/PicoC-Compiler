// ---------------------------------- L_Arith ---------------------------------
exp ::= Name(str) | Num(str) | Char(str)
unary_op ::= Minus() | Not()
bin_op ::= Add() | Sub() | Mul() | Div() | Mod() | Oplus() | And() | Or()
exp ::= ArithBinOp(<exp>, <bin_op>, <exp>) | ArithUnaryOp(<unary_op>, <exp>) | Call(Name('input'), $\empty$)
stmt ::= Call(Name('print'), <exp>)
// ---------------------------------- L_Logic ---------------------------------
relation ::= Eq() | NEq() | Lt() | LtE() | Gt() | GtE()
logic_op ::= LogicAnd() | LogicOr()
exp ::= LogicBinOp(<exp>, <logic_op>, <exp>) | LogicNot(<exp>) | LogicAtom(<exp>, <relation>, <exp>) | ToBool(<exp>)
// ------------------------------ L_Assign_Alloc ------------------------------
type_qual ::= Const() | Writeable()
size_qual ::= IntType() | CharType() | VoidType()
stmt ::= Assign(Name(str), <exp>) | Alloc(<type_qual>, <size_qual>, Name(str))
// --------------------------------- L_Pointer --------------------------------
size_qual ::= PointerType(<size_qual>)
exp ::= Ref(Name(str)) | Deref(<exp>) | Ref(Deref(<exp>))
stmt ::= Assign(Deref(<exp>), <exp>)
// ---------------------------------- L_Array ---------------------------------
size_qual ::= ArrayType(<size_qual>, Num(str))
exp ::= Array(<size_qual>, <exp>+) | Subscript(Name(str), <exp>)
exp ::= Ref(Subscript(Name(str), <exp>))
stmt ::= Assign(Subscript(Name(str), <exp>), <exp>)
// --------------------------------- L_Struct ---------------------------------
size_qual ::= StructType(Name(str))
exp ::= Struct(Assign(Name(str), <exp>)+) | Attribute(Name(str), Name(str)) | Ref(Attribute(Name(str), Name(str)))
stmt ::= StructDef(Name(str), Param(Name(str), <size_qual>)+) | Assign(Attribute(Name(str), Name(str)), <exp>)
// --------------------------------- L_If_Else --------------------------------
stmt ::= If(<exp>, <stmt>*) | IfElse(<exp>, <stmt>*, Else(), <stmt>*)
// ---------------------------------- L_Loop ----------------------------------
stmt ::= While(<exp>, <stmt>*) | DoWhile(<exp>, <stmt>*)
// ----------------------------------- L_Fun ----------------------------------
size_qual ::= FunType(<size_qual>)
exp ::= Call(Name(str), <exp>*)
stmt ::= Return(<exp>) | Exp(Call(Name(str), <exp>*))
def ::= FunDef(Name(str), Param(Name(str), <size_qual>)*, <size_qual>, <stmt>*)
// ---------------------------------- L_File ----------------------------------
file ::= File(Name(str), <def>*)
