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
