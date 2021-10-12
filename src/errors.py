from sys import exit


class SyntaxError(Exception):

    """If there're Token sequences generated from the input that are not
    permitted by the grammar rules"""

    def __init__(self, expected, found):
        self.description = f"SyntaxError: Expected {expected}"\
            f", found {found.value}"
        super().__init__(self.description)
        self.expected = expected
        self.found = found


class InvalidCharacterError(Exception):

    """If there're Token sequences generated from the input that are not
    permitted by the grammar rules"""

    def __init__(self, found):
        self.description = f"InvalidCharacterError: "\
            f"{found} is not a permitted character"
        super().__init__(self.description)
        self.found = found


class NoApplicableRuleError(Exception):

    """If no rule is applicable in a situation where several undistinguishable
    alternatives are possible"""

    def __init__(self, expected, found):
        self.description = f"NoApplicableRuleError: Expected {expected}"\
            f", found {found.value}"
        super().__init__(self.description)
        self.expected = expected
        self.found = found


class MismatchedTokenError(Exception):

    """If token shouldn't syntactically appear at this position"""

    def __init__(self, expected, found):
        self.description = f"MismatchedTokenError: Expected {expected}"\
            f", found {found.value}"
        super().__init__(self.description)
        self.expected = expected
        self.found = found


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
            error_message += self._point_at_error(e) + '\n'
            print(error_message)
            exit(0)
        except NoApplicableRuleError as e:
            error_message += self._error_message_header(e) + '\n'
            error_message += self._point_at_error(e) + '\n'
            print(error_message)
            exit(0)
        except MismatchedTokenError as e:
            error_message += self._error_message_header(e) + '\n'
            error_message += self._point_at_error(e) + '\n'
            print(error_message)
            exit(0)

    def _error_message_header(self, error):
        return self.grammar.lexer.fname + ':' + str(error.found.start[0])\
            + ':' + str(error.found.start[1]) + ': ' + error.description

    def _point_at_error(self, error):
        # TODO: Was ist wenn sich ein Token über mehrere Zeilen erstreck mit ^~
        line = self.grammar.lexer.input[error.found.start[0]]
        return line + '\n' + ' ' * (error.found.start[1]-1) + '^' +\
            '~' * (error.found.end[1]-error.found.start[1])
