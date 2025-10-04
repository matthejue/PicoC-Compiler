from lark.lexer import Token
from util_classes import Pos


class UnexpectedCharacter(Exception):
    def __init__(self, expected: str, found: str, found_pos: Pos):
        self.description = f"UnexpectedCharacter: No terminal matches '{found}' in the current lexical context of {expected}."
        self.expected = expected
        self.found = found
        self.found_pos = found_pos


class UnexpectedToken(Exception):
    def __init__(self, expected: str, found: Token, found_pos: Pos):
        self.description = f"UnexpectedToken: Expected e.g. {expected}, found '{found}'."
        self.expected = expected
        self.found = found
        self.found_pos = found_pos


class UnexpectedEOF(Exception):
    def __init__(self, expected: str, last_pos: Pos):
        self.description = f"UnexpectedEOF: Unexpected end-of-file, expected e.g. {expected}."
        self.expected = expected
        self.last_pos = last_pos


class UnknownIdentifier(Exception):
    def __init__(self, found: str, found_pos: Pos):
        self.description = f"UnknownIdentifier: Identifier '{found}' wasn't declared yet."
        self.found = found
        self.found_pos = found_pos


class UnknownAttribute(Exception):
    def __init__(self, attr_name, attr_pos, struct_name, struct_pos, var_name, var_pos):
        self.description = f"UnknownAttribute: Attribute '{attr_name}' is unknown in struct type '{struct_name}'."
        self.description2 = f"Note: Struct type '{struct_name}' was declared here:"
        self.attr_name = attr_name
        self.attr_pos = attr_pos
        self.struct_type_name = struct_name
        self.struct_type_pos = struct_pos
        self.var_name = var_name
        self.var_pos = var_pos


class NoMainFunction(Exception):
    def __init__(self):
        self.description = f"NoMainFunction: This program contains no main function. Expected exactly 1 main function."


class TooLargeLiteral(Exception):
    def __init__(self, found, found_pos):
        self.description = f"TooLargeLiteral: The value represented by the literal '{found}' is too large."
        self.found = found
        self.found_pos = found_pos


class PrototypeMismatch(Exception):
    def __init__(
        self,
        def_name,
        def_pos,
        def_param_name,
        def_param_datatype,
        def_param_pos,
        decl_pos,
        decl_param_name,
        decl_param_datatype,
        decl_param_pos,
    ):
        self.description = f"PrototypeMismatch: Parameter {def_param_name} of datatype {def_param_datatype} from function definition {def_name} is not matching with parameter {decl_param_name} of datatype {decl_param_datatype} from function declaration."
        self.description2 = f"Note: Function {def_name} was declared here:"
        self.def_name = def_name
        self.def_pos = def_pos
        self.def_param_name = def_param_name
        self.def_param_datatype = def_param_datatype
        self.def_param_pos = def_param_pos
        self.decl_pos = decl_pos
        self.decl_param_name = decl_param_name
        self.decl_param_datatype = decl_param_datatype
        self.decl_param_pos = decl_param_pos


class ArgumentMismatch(Exception):
    def __init__(
        self,
        fun_call_pos,
        arg_exp,
        arg_datatype,
        arg_pos,
        fun_name,
        fun_pos,
        fun_param_name,
        fun_param_datatype,
        fun_param_pos,
    ):
        self.description = f"ArgumentMismatch: Argument {arg_exp} of datatype {arg_datatype} in function call is not matching with parameter {fun_param_name} of datatype {fun_param_datatype} from function {fun_name}."
        self.description2 = f"Note: Function {fun_name} was declared here:"
        self.fun_call_pos = fun_call_pos
        self.arg_exp = arg_exp
        self.arg_datatype = arg_datatype
        self.arg_pos = arg_pos
        self.fun_name = fun_name
        self.fun_pos = fun_pos
        self.fun_param_name = fun_param_name
        self.fun_param_datatype = fun_param_datatype
        self.fun_param_pos = fun_param_pos


class WrongNumberArguments(Exception):
    def __init__(
        self,
        too_few,
        fun_call_pos,
        fun_call_num_args,
        fun_name,
        fun_pos,
        fun_num_params,
    ):
        self.description = f"WrongNumberArguments: Too {('few' if too_few else 'many')} arguments. Function call contains {fun_call_num_args} argument(s), but function {fun_name} excepts {('only ' if not too_few else '')}{fun_num_params} argument(s)."
        self.description2 = f"Note: Function {fun_name} was declared here:"
        self.too_few = too_few
        self.fun_call_pos = fun_call_pos
        self.fun_call_num_args = fun_call_num_args
        self.fun_name = fun_name
        self.fun_pos = fun_pos
        self.fun_num_params = fun_num_params


class WrongReturnType(Exception):
    def __init__(
        self,
        fun_name,
        fun_pos,
        expected_return_type,
        found_return_type,
        last_stmt_pos,
        is_return,
    ):
        self.description = f"WrongReturnType: Function {fun_name} has return type {expected_return_type}, but function returns type {found_return_type}."
        self.fun_name = fun_name
        self.fun_pos = fun_pos
        self.expected_return_type = expected_return_type
        self.found_return_type = found_return_type
        self.last_stmt_pos = last_stmt_pos
        self.is_return = is_return


class ReDeclarationOrDefinition(Exception):
    def __init__(self, found, found_pos, first_pos):
        self.description = f"ReDeclarationOrDefinition: Redeclaration or Redefinition of '{found}'."
        self.found = found
        self.found_pos = found_pos
        self.description2 = (
            f"Note: Already declared or defined here:"
        )
        self.first_pos = first_pos


class DatatypeMismatch(Exception):
    def __init__(
        self,
        identifier_name,
        identifier_context_datatype,
        identifier_pos,
        expected_pos,
        expected_datatype,
    ):
        self.description = f"DatatypeMismatch: Datatype '{identifier_context_datatype}' of variable '{identifier_name}' isn't matching in the present context. Expected '{expected_datatype}'."
        self.identifier_name = identifier_name
        self.identifier_context_datatype = identifier_context_datatype
        self.identifier_pos = identifier_pos
        self.expected_pos = expected_pos
        self.expected_datatype = expected_datatype


class NodeError(Exception):
    def __init__(self, node_name, node_pos):
        self.description = f"DatatypeMismatch: Error occured at Node {node_name}."
        self.node_name = node_name
        self.node_pos = node_pos


# -----------------------------------------------------------------------------


class ConstAssign(Exception):
    def __init__(self, found, found_pos):
        self.description = f"ConstAssign: Can't assign a new value to named constant '{found}'."
        self.found = found
        self.found_pos = found_pos


class ConstRef(Exception):
    def __init__(self, found, found_pos):
        self.description = f"ConstRef: Can't apply the reference / address-of operator to named constant '{found}'."
        self.found = found
        self.found_pos = found_pos


class BugInCompiler(Exception):
    def __init__(self, fun_name, args):
        self.description = f"BugInCompiler: Error in function '{fun_name}' with {args}. This error should not be possible, but it occured. Please report this issue under https://github.com/matthejue/PicoC-Compiler/issues/new/choose"
        self.description2 = f"Note: Stacktrace:"


class BugInInterpreter(Exception):
    def __init__(self, fun_name, args):
        self.description = f"BugInInterpreter: Error in function '{fun_name}' with {args}. This error should not be possible, but it occured. Please report this issue under https://github.com/matthejue/PicoC-Compiler/issues/new/choose"
        self.description2 = f"Note: Stacktrace:"
