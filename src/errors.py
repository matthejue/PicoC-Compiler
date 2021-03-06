from colormanager import ColorManager as CM
from lark.lexer import Token
from global_classes import Pos


class UnexpectedCharacter(Exception):
    def __init__(self, expected: str, found: str, found_pos: Pos):
        self.description = f"{CM().YELLOW}UnexpectedCharacter:{CM().RESET_ALL} No terminal matches {CM().RED}'{found}'{CM().RESET} in the current lexical context of {CM().BLUE}{expected}{CM().RESET}"
        self.expected = expected
        self.found = found
        self.found_pos = found_pos


class UnexpectedToken(Exception):
    def __init__(self, expected: str, found: Token, found_pos: Pos):
        self.description = f"{CM().YELLOW}UnexpectedToken:{CM().RESET_ALL} Expected e.g. {expected}, found {CM().RED}'{found}'{CM().RESET}"
        self.expected = expected
        self.found = found
        self.found_pos = found_pos


class UnexpectedEOF(Exception):
    def __init__(self, expected: str, last_pos: Pos):
        self.description = f"{CM().YELLOW}UnexpectedEOF:{CM().RESET_ALL} Unexpected end-of-file, expected e.g. {expected}"
        self.expected = expected
        self.last_pos = last_pos


class UnknownIdentifier(Exception):
    def __init__(self, found: str, found_pos: Pos):
        self.description = f"{CM().YELLOW}UnknownIdentifier:{CM().RESET_ALL} Identifier {CM().RED}'{found}'{CM().RESET} wasn't declared yet"
        self.found = found
        self.found_pos = found_pos


class Redefinition(Exception):
    def __init__(self, found, found_pos, first_pos):
        self.description = f"{CM().YELLOW}Redefinition:{CM().RESET_ALL} Redefinition of {CM().RED}'{found}'{CM().RESET}"
        self.found = found
        self.found_pos = found_pos
        self.description2 = f"{CM().YELLOW}Note:{CM().RESET_ALL} Already defined here:"
        self.first_pos = first_pos


class Redeclaration(Exception):
    def __init__(self, found, found_pos, first_pos):
        self.description = f"{CM().YELLOW}Redeclaration:{CM().RESET_ALL} Redeclaration of {CM().RED}'{found}'{CM().RESET}"
        self.found = found
        self.found_pos = found_pos
        self.description2 = f"{CM().YELLOW}Note:{CM().RESET_ALL} Already declared here:"
        self.first_pos = first_pos


class UnknownAttribute(Exception):
    def __init__(self, attribute_name, attribute_pos, struct_name):
        self.description = f"{CM().YELLOW}UnknownAttribute:{CM().RESET_ALL} Struct {CM().BLUE}'{struct_name}'{CM().RESET} doesn't have a attribute {CM().RED}'attribute_name'{CM().RESET}"
        self.attribute_name = attribute_name
        self.attribute_pos = attribute_pos
        self.struct_name = struct_name


class DatatypeMismatch(Exception):
    def __init__(
        self, var_name, var_context_datatype, var_pos, expected_pos, expected_datatype
    ):
        self.description = f"{CM().YELLOW}DatatypeMismatch:{CM().RESET_ALL} Datatype {CM().RED}{var_context_datatype}{CM().RESET} of variable {CM().RED}{var_name}{CM().RESET} isn't matching in the present context. Expected {CM().BLUE}{expected_datatype}{CM().RESET}"
        self.var_name = var_name
        self.var_context_datatype = var_context_datatype
        self.var_pos = var_pos
        self.expected_pos = expected_pos
        self.expected_datatype = expected_datatype


class NodeError(Exception):
    def __init__(self, node_name, node_pos):
        self.description = f"{CM().YELLOW}DatatypeMismatch:{CM().RESET_ALL} Error occured at Node {CM().RED}{node_name}{CM().RESET}"
        self.node_name = node_name
        self.node_pos = node_pos


# -----------------------------------------------------------------------------


class ConstAssign(Exception):
    def __init__(self, found, found_pos):
        self.description = f"{CM().YELLOW}ConstAssign:{CM().RESET_ALL} Can't assign a new value to named constant {CM().RED}'{found}'{CM().RESET}"
        self.found = found
        self.found_pos = found_pos


class ConstRef(Exception):
    def __init__(self, found, found_pos):
        self.description = f"{CM().YELLOW}ConstRef:{CM().RESET_ALL} Can't apply the reference / address-of operator to named constant {CM().RED}'{found}'{CM().RESET}"
        self.found = found
        self.found_pos = found_pos


# TODO
class TooLargeLiteral(Exception):
    def __init__(self, found, found_pos, found_symbol_type, found_from, found_to):
        self.description = f"{CM().YELLOW}TooLargeLiteral:{CM().RESET_ALL} Literal '{found}' is too large"
        self.found = found
        self.found_pos = found_pos
        self.found_symbol_type = found_symbol_type
        self.found_from = found_from
        self.found_to = found_to


# TODO
class NoMainFunction(Exception):
    def __init__(self, fname):
        self.description = f"{CM().YELLOW}NoMainFunction:{CM().RESET_ALL} There's no main function in file '{fname}'"


# TODO
class MoreThanOneMainFunction(Exception):
    def __init__(self, first_pos, second_pos):
        self.description = f"{CM().YELLOW}MoreThanOneMainFunction:{CM().RESET_ALL} There're at least two main functions"
        self.first_pos = first_pos
        self.second_pos = second_pos


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
        self.def_name = def_name
        self.def_pos = def_pos
        self.def_param_name = def_param_name
        self.def_param_datatype = def_param_datatype
        self.def_param_pos = def_param_pos
        self.decl_pos = decl_pos
        self.decl_param_name = decl_param_name
        self.decl_param_datatype = decl_param_datatype
        self.decl_param_pos = decl_param_pos


class BugInCompiler(Exception):
    def __init__(self, fun_name, args):
        self.description = f"{CM().YELLOW}BugInCompiler:{CM().RESET_ALL} Error in function {CM().BLUE}'{fun_name}'{CM().RESET} with {args}. This error should not be possible, but it occured. Please report this issue under {CM().RED}https://github.com/matthejue/PicoC-Compiler/issues/new/choose{CM().RESET}"
        self.description2 = f"{CM().YELLOW}Note:{CM().RESET_ALL} Stacktrace:"


class BugInInterpreter(Exception):
    def __init__(self, fun_name, args):
        self.description = f"{CM().YELLOW}BugInInterpreter:{CM().RESET_ALL} Error in function {CM().BLUE}'{fun_name}'{CM().RESET} with {args}. This error should not be possible, but it occured. Please report this issue under {CM().RED}https://github.com/matthejue/PicoC-Compiler/issues/new/choose{CM().RESET}"
        self.description2 = f"{CM().YELLOW}Note:{CM().RESET_ALL} Stacktrace:"
