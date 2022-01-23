class Warnings:
    class TooLargeLiteralWarning:
        """If the literal assigned to a variable is too large for the datatype of
        the variable"""
        def __init__(self, variable, variable_pos, variable_type,
                     variable_from, variable_to, found, found_pos):
            self.description = f"TooLargeLiteralWarning: Literal '{found}' "
            f"assigned to variable '{variable}' of type '{variable_type}' is "
            "too large"
            self.variable = variable
            self.variable_pos = variable_pos
            self.variable_type = variable_type
            self.variable_from = variable_from
            self.variable_to = variable_to
            self.found = found
            self.found_pos = found_pos
