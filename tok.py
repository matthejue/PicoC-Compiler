###############################################################################
#                                    Token                                    #
###############################################################################

class Token:
    """Identifies what a certain string slice is.
    Has a type and optionaly metadata.
    """

    def __init__(self, type, md):
        self.type, self.md = type, md

    def __repr__(self):
        return f'{self.type}:{self.md.value}'

###############################################################################
#                                  Metadata                                   #
###############################################################################


class Metadata:
    """Additional Information about the Token"""

    def __init__(self, col, row, fname, code, value=None):
        self.col, self.row = col, row
        self.fname, self.code = fname, code
        self.current_char = None
        self.value = value

    def copy(self, value=None):
        """Copy the medadata for a token but only with the line
        :returns: Copy of the metadata

        """
        line = [self.code[self.row]]

        # in case the token identifies several characters
        if value:
            return Metadata(self.col, self.row, self.fname, line, value)
        # else the token only identifies one character
        return Metadata(self.col, self.row, self.fname, line,
                        self.current_char)
