from colormanager import ColorManager as CM
from lark.lexer import Token
from util_classes import Pos


class UnexpectedCharacter(Exception):
    def __init__(self, expected: str, found: str, found_pos: Pos):
        self.description = f"{CM().YELLOW}UnexpectedCharacter:{CM().RESET_ALL} No terminal matches {CM().RED}'{found}'{CM().RESET} in the current lexical context of {CM().BLUE}{expected}{CM().RESET}."
        self.expected = expected
        self.found = found
        self.found_pos = found_pos


class UnexpectedToken(Exception):
    def __init__(self, expected: str, found: Token, found_pos: Pos):
        self.description = f"{CM().YELLOW}UnexpectedToken:{CM().RESET_ALL} Expected e.g. {expected}, found {CM().RED}'{found}'{CM().RESET}."
        self.expected = expected
        self.found = found
        self.found_pos = found_pos


class UnexpectedEOF(Exception):
    def __init__(self, expected: str, last_pos: Pos):
        self.description = f"{CM().YELLOW}UnexpectedEOF:{CM().RESET_ALL} Unexpected end-of-file, expected e.g. {expected}."
        self.expected = expected
        self.last_pos = last_pos


class UnknownIdentifier(Exception):
    def __init__(self, found: str, found_pos: Pos):
        self.description = f"{CM().YELLOW}UnknownIdentifier:{CM().RESET_ALL} Identifier {CM().RED}'{found}'{CM().RESET} wasn't declared yet."
        self.found = found
        self.found_pos = found_pos


class UnknownAttribute(Exception):
    def __init__(self, attr_name, attr_pos, struct_name, struct_pos, var_name, var_pos):
        self.description = f"{CM().YELLOW}UnknownAttribute:{CM().RESET_ALL} Attribute {CM().RED}'{attr_name}'{CM().RESET}{CM().RESET_ALL} is unknown in struct type {CM().BLUE}'{struct_name}'{CM().RESET}."
        self.description2 = f"{CM().YELLOW}Note:{CM().RESET_ALL} Struct type {CM().BLUE}'{struct_name}'{CM().RESET} was declared here:"
        self.attr_name = attr_name
        self.attr_pos = attr_pos
        self.struct_type_name = struct_name
        self.struct_type_pos = struct_pos
        self.var_name = var_name
        self.var_pos = var_pos


class NoMainFunction(Exception):
    def __init__(self):
        self.description = f"{CM().YELLOW}NoMainFunction:{CM().RESET_ALL} This program contains {CM().RED}no{CM().RESET} main function. Expected exactly {CM().BLUE}1{CM().RESET} main function."


class TooLargeLiteral(Exception):
    def __init__(self, found, found_pos):
        self.description = f"{CM().YELLOW}TooLargeLiteral:{CM().RESET_ALL} The value represented by the literal '{found}' is too large."
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
        self.description = f"{CM().YELLOW}PrototypeMismatch:{CM().RESET_ALL} Parameter {CM().RED}{def_param_name}{CM().RESET_ALL} of datatype {CM().RED}{def_param_datatype}{CM().RESET_ALL} from function definition {CM().RED}{def_name}{CM().RESET_ALL} is not matching with parameter {CM().BLUE}{decl_param_name}{CM().RESET_ALL} of datatype {CM().BLUE}{decl_param_datatype}{CM().RESET_ALL} from function declaration."
        self.description2 = f"{CM().YELLOW}Note:{CM().RESET_ALL} Function {CM().BLUE}{def_name}{CM().RESET_ALL} was declared here:"
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
        self.description = f"{CM().YELLOW}ArgumentMismatch:{CM().RESET_ALL} Argument {CM().RED}{arg_exp}{CM().RESET_ALL} of datatype {CM().RED}{arg_datatype}{CM().RESET_ALL} in function call is not matching with parameter {CM().BLUE}{fun_param_name}{CM().RESET_ALL} of datatype {CM().BLUE}{fun_param_datatype}{CM().RESET_ALL} from function {CM().RED}{fun_name}{CM().RESET_ALL}."
        self.description2 = f"{CM().YELLOW}Note:{CM().RESET_ALL} Function {CM().BLUE}{fun_name}{CM().RESET_ALL} was declared here:"
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
        self.description = f"{CM().YELLOW}WrongNumberArguments:{CM().RESET_ALL} Too {('few' if too_few else 'many')} arguments. Function call contains {CM().RED}{fun_call_num_args}{CM().RESET_ALL} argument(s), but function {CM().BLUE}{fun_name}{CM().RESET_ALL} excepts {('only ' if not too_few else '')}{CM().BLUE}{fun_num_params}{CM().RESET_ALL} argument(s)."
        self.description2 = f"{CM().YELLOW}Note:{CM().RESET_ALL} Function {CM().BLUE}{fun_name}{CM().RESET_ALL} was declared here:"
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
        self.description = f"{CM().YELLOW}WrongReturnType:{CM().RESET_ALL} Function {CM().BLUE}{fun_name}{CM().RESET_ALL} has return type {CM().BLUE}{expected_return_type}{CM().RESET_ALL}, but function returns type {CM().RED}{found_return_type}{CM().RESET_ALL}."
        self.fun_name = fun_name
        self.fun_pos = fun_pos
        self.expected_return_type = expected_return_type
        self.found_return_type = found_return_type
        self.last_stmt_pos = last_stmt_pos
        self.is_return = is_return


class ReDeclarationOrDefinition(Exception):
    def __init__(self, found, found_pos, first_pos):
        self.description = f"{CM().YELLOW}ReDeclarationOrDefinition:{CM().RESET_ALL} Redeclaration or Redefinition of {CM().RED}'{found}'{CM().RESET}."
        self.found = found
        self.found_pos = found_pos
        self.description2 = (
            f"{CM().YELLOW}Note:{CM().RESET_ALL} Already declared or defined here:"
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
        self.description = f"{CM().YELLOW}DatatypeMismatch:{CM().RESET_ALL} Datatype {CM().RED}'{identifier_context_datatype}'{CM().RESET} of variable {CM().RED}'{identifier_name}'{CM().RESET} isn't matching in the present context. Expected {CM().BLUE}'{expected_datatype}'{CM().RESET}."
        self.identifier_name = identifier_name
        self.identifier_context_datatype = identifier_context_datatype
        self.identifier_pos = identifier_pos
        self.expected_pos = expected_pos
        self.expected_datatype = expected_datatype


class NodeError(Exception):
    def __init__(self, node_name, node_pos):
        self.description = f"{CM().YELLOW}DatatypeMismatch:{CM().RESET_ALL} Error occured at Node {CM().RED}{node_name}{CM().RESET}."
        self.node_name = node_name
        self.node_pos = node_pos


# -----------------------------------------------------------------------------


class ConstAssign(Exception):
    def __init__(self, found, found_pos):
        self.description = f"{CM().YELLOW}ConstAssign:{CM().RESET_ALL} Can't assign a new value to named constant {CM().RED}'{found}'{CM().RESET}."
        self.found = found
        self.found_pos = found_pos


class ConstRef(Exception):
    def __init__(self, found, found_pos):
        self.description = f"{CM().YELLOW}ConstRef:{CM().RESET_ALL} Can't apply the reference / address-of operator to named constant {CM().RED}'{found}'{CM().RESET}."
        self.found = found
        self.found_pos = found_pos


class BugInCompiler(Exception):
    def __init__(self, fun_name, args):
        self.description = f"{CM().YELLOW}BugInCompiler:{CM().RESET_ALL} Error in function {CM().BLUE}'{fun_name}'{CM().RESET} with {args}. This error should not be possible, but it occured. Please report this issue under {CM().RED}https://github.com/matthejue/PicoC-Compiler/issues/new/choose{CM().RESET}"
        self.description2 = f"{CM().YELLOW}Note:{CM().RESET_ALL} Stacktrace:"


class BugInInterpreter(Exception):
    def __init__(self, fun_name, args):
        self.description = f"{CM().YELLOW}BugInInterpreter:{CM().RESET_ALL} Error in function {CM().BLUE}'{fun_name}'{CM().RESET} with {args}. This error should not be possible, but it occured. Please report this issue under {CM().RED}https://github.com/matthejue/PicoC-Compiler/issues/new/choose{CM().RESET}"
        self.description2 = f"{CM().YELLOW}Note:{CM().RESET_ALL} Stacktrace:"
