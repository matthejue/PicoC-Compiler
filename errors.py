###############################################################################
#                                   Errors                                    #
###############################################################################

class Error:
    """Label for sth that is now allowed in pico_c Code"""

    def __init__(self, md, error_label, description):
        self.md = md
        self.error_label = error_label
        self.description = description

    def __repr__(self):
        output = f'File "{self.md.fname}", line {self.md.row + 1}\n'
        for line in self.md.code:
            line_with_pointer = point_at_error(line, self.md.col)
            output += f'{line_with_pointer}\n'
        output += f'{self.error_label}: {self.description}'
        return output


def point_at_error(line, col):
    """point with an arrow at the cause of the error.
    :returns: string with an extra row containing an arrow

    """
    return line + '\n' + ' ' * col + '^'


class SyntaxError(Error):
    """Doing sth which is not permitted in the grammer rules."""

    def __init__(self, md, char_listing):
        super().__init__(md, "SyntaxError", "Expected " + char_listing)


class IllegalCharacterError(Error):
    """Doing sth which is not permitted in the grammer rules."""

    def __init__(self, md, char):
        super().__init__(md, "IllegalCharError",
                         "Character " + char + " is not permitted here")
