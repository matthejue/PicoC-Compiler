from sys import exit


class SyntaxError(Exception):

    """If there're Token sequences generated from the input that are not
    permitted by the grammar rules"""

    def __init__(self, expected, found):
        self.description = f"SyntaxError: Expected {expected}"\
            f", found {found.value}"
        super().__init__(self.description)


class InvalidCharacterError(Exception):

    """If there're Token sequences generated from the input that are not
    permitted by the grammar rules"""

    def __init__(self, found):
        self.description = f"InvalidCharacterError: "\
            f"{found} is not a permitted character"
        super().__init__(self.description)


class NoApplicableRuleError(Exception):

    """If no rule is applicable in a situation where several undistinguishable
    alternatives are possible"""

    def __init__(self, expected, found):
        self.description = f"NoApplicableRuleError: Expected {expected}"\
            f", found {found.value}"
        super().__init__(self.description)


class MismatchedTokenError(Exception):

    """If token shouldn't syntactically appear at this position"""

    def __init__(self, expected, found):
        self.description = f"MismatchedTokenError: Expected {expected}"\
            f", found {found.value}"
        super().__init__(self.description)


class ErrorHandler:

    """Output a detailed error message"""

    def __init__(self, grammar):
        self.grammar = grammar

    def handle(self, function):
        error_message = ""
        try:
            function()
        except InvalidCharacterError as e:
            error_message += self._error_message_header(e) + '\n'
            error_message += self._point_at_error() + '\n'
            print(error_message)
            exit(0)
        except NoApplicableRuleError as e:
            error_message += self._error_message_header(e) + '\n'
            error_message += self._point_at_error() + '\n'
            print(error_message)
            exit(0)
        except MismatchedTokenError as e:
            error_message += self._error_message_header(e) + '\n'
            error_message += self._point_at_error() + '\n'
            print(error_message)
            exit(0)

    def _error_message_header(self, error):
        return self.grammar.lexer.fname + ':' + str(self.grammar.lexer.lc_row)\
            + ':' + str(self.grammar.lexer.lc_col) + ': ' + error.description

    def _point_at_error(self, ):
        line = self.grammar.lexer.input[self.grammar.lexer.lc_row]
        return line + '\n' + ' ' * self.grammar.lexer.lc_col + '^'
