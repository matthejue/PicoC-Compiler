import global_vars
from ast_node import ASTNode, strip_multiline_string
from symbol_table import VariableSymbol, ConstantSymbol
from errors import Errors
from picoc_nodes import NT
from arithmetic_nodes import Identifier, Number, Character
import warnings
from warning_handler import WarningHandler
from bitstring import Bits
from enum import Enum


class TYPE(Enum):
    """Type of assignment"""

    CONST_ASSIGNMENT = 1
    ASSIGNMENT_WITH_LITERAL = 2
    ASSIGNMENT_WITH_VARIABLE = 3
    ASSIGNMENT_WITH_COMPLEX_EXPRESSION = 4


class Assignment(ASTNode):
    """Abstract Syntax Tree Node for assignement"""

    def __init__(self, value=None, position=None):
        self.warning_handler = WarningHandler()
        super().__init__(value, position)

    assign = strip_multiline_string(
        f"""LOADIN SP ACC 1;  # Wert von 'e1' in ACC laden
        ADDI SP 1;  # Stack um eine Zelle verkürzen
        """
    )
    assign_loc = 2

    implicit_conversion = strip_multiline_string(
        """LOADI IN1 255;  # Bitmaske '00000000_00000000_00000000_11111111' für char Datentyp erstellen
        AND ACC IN1;  # Wo in der Bitmaske eine '0' ist, werden die Bits ebenfalls zu '0'
        LOADI IN2 128;  # Bitvektor '__000000_00000000_10000000' laden
        AND ACC IN1;  # Testen, ob Zahl negativ, wenn sie nur 8-Bit lang wäre
        JUMP== 3;  # Signextension für negative Zahl überspringen, wenn Zahl nicht negativ ist
        LOADI IN1 -256;  # Bitsmaske '11111111_11111111_11111111_00000000' für signextension erstellen
        OR ACC IN1;  # Wo in der Bitmaske eine '1' ist, werden die Bits ebenfallls zu '1'
        """
    )
    implicit_conversion_loc = 8

    assign_more = "STORE ACC var_address;  # Wert 'e1' in Variable 'v1' speichern\n"
    assign_more_loc = 1

    def update_match_args(
        self,
    ):
        self.location = self.children[0]
        self.expression = self.children[1]

    __match_args__ = ("location", "expression")

    def visit(self):
        self.update_match_args()

        self.code_generator.add_code(f"# Zuweisung '{self}' Start\n", 0)

        match self.location:
            case Allocation():
                self.location.visit()

        self._pretty_comments()

        try:
            self._assignment()
        except KeyError:
            # repackage the error
            match self.location:
                case Identifier(value, position):
                    raise Errors.UnknownIdentifierError(value, position)

        self.code_generator.add_code(f"# Zuweisung '{self}' Ende\n", 0)

    def _pretty_comments(self):
        if global_vars.args.verbose:
            self.assign = self.code_generator.replace_code_pre(
                self.assign, "e1", str(self.expression)
            )
            self.assign_more = self.code_generator.replace_code_pre(
                self.assign_more, "e1", str(self.expression)
            )
            match self.location:
                case Allocation(_, _, _):
                    self.assign_more = self.code_generator.replace_code_pre(
                        self.assign_more, "v1", str(self.location.identifier)
                    )
                case _:
                    self.assign_more = self.code_generator.replace_code_pre(
                        self.assign_more, "v1", str(self.location)
                    )

    def _comment_for_constant(self, name, value):
        self.code_generator.add_code(
            f"# Konstante '{name}' in Symboltabelle "
            f"den Wert '{value}' zugewiesen\n",
            0,
        )

    def _assignment(self):
        match self:
            case Assignment(Allocation(NT.Const(), _, Identifier(name)), expression):
                match expression:
                    case (Number(value, position) | Character(value, position)):
                        symbol = self.symbol_table.resolve(name)

                        # error check
                        possibly_new_value = (
                            self._implicit_conversion_and_warning_check(
                                symbol, value, position, TYPE.CONST_ASSIGNMENT
                            )
                        )
                        symbol.value = possibly_new_value
                        self._comment_for_constant(name, str(possibly_new_value))

            # nested assignment that is the assignment of another assignment
            case Assignment(
                (Identifier(name) | Allocation(_, _, Identifier(name))), Assignment()
            ):
                self.expression.visit()

                match self.expression:
                    case Assignment(Identifier(name_2, position), _):
                        symbol = self.symbol_table.resolve(name)
                        self._implicit_conversion_and_warning_check(
                            symbol, name_2, position, TYPE.ASSIGNMENT_WITH_VARIABLE
                        )

                self._adapt_code(name)

            # assigment that assigns a variable to a expression
            case Assignment(
                (
                    Identifier(name, position)
                    | Allocation(_, _, Identifier(name, position))
                ),
                expression,
            ):
                symbol = self.symbol_table.resolve(name)

                # error check 1
                # There should never be a const identifier on the left side in
                # a assignment if it's not the initialisation of the const
                # identifier
                self._const_reassignment_error_check(name, position, symbol)

                self.expression.visit()

                self.code_generator.add_code(self.assign, self.assign_loc)

                # error check 2 and possible implicit conversion
                # If the literal or variable on the right side has a larger
                # type then the variable on the left side, then throw a warning
                # and make a impilicit converstion
                match expression:
                    case (Character(value, position) | Number(value, position)):
                        self._implicit_conversion_and_warning_check(
                            symbol, value, position, TYPE.ASSIGNMENT_WITH_LITERAL
                        )
                    case Identifier(name_2, position):
                        self._implicit_conversion_and_warning_check(
                            symbol, name_2, position, TYPE.ASSIGNMENT_WITH_VARIABLE
                        )
                    case _:
                        self._implicit_conversion_and_warning_check(
                            symbol, None, None, TYPE.ASSIGNMENT_WITH_COMPLEX_EXPRESSION
                        )

                self._adapt_code(name)

    def _adapt_code(self, name):
        self.assign_more = self.code_generator.replace_code_pre(
            self.assign_more, "var_address", self.symbol_table.resolve(name).value
        )

        self.code_generator.add_code(self.assign_more, self.assign_more_loc)

    def _implicit_conversion_and_warning_check(
        self, symbol, value, position, type_of_assignment
    ):
        """return value only important for const"""
        char_range_from = global_vars.RANGE_OF_CHAR[0]
        char_range_to = global_vars.RANGE_OF_CHAR[1]
        parameter_range_from = global_vars.RANGE_OF_PARAMETER[0]
        parameter_range_to = global_vars.RANGE_OF_PARAMETER[1]

        match type_of_assignment:
            case TYPE.ASSIGNMENT_WITH_VARIABLE:
                symbol_2 = self.symbol_table.resolve(value)
                if symbol.datatype.name == "char" and symbol_2.datatype.name == "int":
                    warning = warnings.Warnings.ImplicitConversionWarning(
                        symbol.name,
                        symbol.position,
                        symbol.datatype,
                        char_range_from,
                        char_range_to,
                        value,
                        position,
                        "int",
                        None,
                    )
                    self.warning_handler.add_warning(warning)
                    self._implicit_conversion()
            case TYPE.ASSIGNMENT_WITH_COMPLEX_EXPRESSION:
                if symbol.datatype.name == "char":
                    self._implicit_conversion()
            case TYPE.ASSIGNMENT_WITH_LITERAL:
                if symbol.datatype.name == "char" and int(value) > char_range_to:
                    char_bits = Bits(int=int(value), length=32).bin[32 - 8 : 32]
                    new_value = Bits(bin=char_bits).int
                    warning = warnings.Warnings.ImplicitConversionWarning(
                        symbol.name,
                        symbol.position,
                        symbol.datatype,
                        char_range_from,
                        char_range_to,
                        value,
                        position,
                        "int",
                        new_value,
                    )
                    self.warning_handler.add_warning(warning)
                    self._implicit_conversion()
            case TYPE.CONST_ASSIGNMENT:
                if int(value) > parameter_range_to:
                    raise Errors.TooLargeLiteralError(
                        value,
                        position,
                        "constant identifier",
                        parameter_range_from,
                        parameter_range_to,
                    )
                elif symbol.datatype.name == "char" and int(value) > char_range_to:
                    char_bits = Bits(int=int(value), length=32).bin[32 - 8 : 32]
                    new_value = Bits(bin=char_bits).int
                    warning = warnings.Warnings.ImplicitConversionWarning(
                        symbol.name,
                        symbol.position,
                        symbol.datatype,
                        char_range_from,
                        char_range_to,
                        value,
                        position,
                        "int",
                        new_value,
                    )
                    self.warning_handler.add_warning(warning)
                    return new_value
                else:
                    return value

    def _implicit_conversion(self):
        self.code_generator.add_code(
            f"# Implizite Konversion von 'int' zu 'char' Start\n", 0
        )
        self.code_generator.add_code(
            self.implicit_conversion, self.implicit_conversion_loc
        )
        self.code_generator.add_code(
            f"# Implizite Konversion von 'int' zu 'char' Ende\n", 0
        )

    def _const_reassignment_error_check(self, name, position, symbol):
        match symbol:
            case ConstantSymbol():
                raise Errors.ConstReassignmentError(
                    name, position, symbol.name, symbol.position
                )

    def __repr__(self):
        if len(self.children) == 2:
            return f"({self.children[0]} = {self.children[1]})"

        return super().__repr__()


class Allocation(ASTNode):
    """Abstract Syntax Tree Node for allocation"""

    def update_match_args(self):
        if isinstance(self.children[0], NT.Const):
            self.const = self.children[0]
            self.prim_dt = self.children[1]
            self.identifier = self.children[2]
        else:
            self.const = None
            self.prim_dt = self.children[0]
            self.identifier = self.children[1]

    __match_args__ = ("const", "prim_dt", "identifier")

    def visit(self):
        self.update_match_args()

        self.code_generator.add_code(f"# Allokation '{self}' Start\n", 0)

        self._adapt_code()

        self.code_generator.add_code(f"# Allokation '{self}' Ende\n", 0)

    def _pretty_comments(self, const_var, name, dtype, value=None):
        suppl = ""
        if value:
            suppl += f" mit Adresse '{value}'"

        self.code_generator.add_code(
            f"# {const_var} '{name}' vom Typ '{dtype}'"
            f"{suppl} zur Symboltabelle hinzugefügt\n",
            0,
        )

    def _adapt_code(self):
        match self:
            case Allocation(
                NT.Const(),
                (NT.Char(dtype) | NT.Int(dtype)),
                Identifier(name, position),
            ):
                self._error_check(name, position)
                constant = ConstantSymbol(
                    name, self.symbol_table.resolve(dtype), position
                )
                self.symbol_table.define(constant)
                self._pretty_comments("Konstante", name, dtype)
            case Allocation(
                _, (NT.Char(dtype) | NT.Int(dtype)), Identifier(name, position)
            ):
                self._error_check(name, position)
                variable = VariableSymbol(
                    name, self.symbol_table.resolve(dtype), position
                )
                self.symbol_table.define(variable)
                address = self.symbol_table.allocate(variable)
                self._pretty_comments("Variable", name, dtype, address)

    def _error_check(self, found_name, found_pos):
        if self.symbol_table.symbols.get(found_name):
            first = self.symbol_table.symbols[found_name]
            raise Errors.RedefinitionError(
                found_name, found_pos, first.name, first.position
            )

    def __repr__(self):
        return self.to_string_show_node()
