class Warnings:
    class ImplicitConversionWarning:
        """If the literal assigned to a variable is too large for the datatype of
        the variable"""
        def __init__(self, variable_old, variable_pos, variable_type,
                     variable_from, variable_to, found, found_pos, found_type,
                     found_new):
            literal_or_variable = "Literal" if found_new else "Value of variable"
            self.description = f"ImplicitConversionWarning: " + literal_or_variable\
                + f" '{found}' will be implicitly converted from '{found_type}' to "\
                f"'{variable_type}' in the course of being assigned to '{variable_old}'"\
                + f". Changes value from '{found}' to '{found_new}'" if found_new else ""
            self.variable = variable_old
            self.variable_pos = variable_pos
            self.variable_type = variable_type
            self.variable_from = variable_from
            self.variable_to = variable_to
            self.found = found
            self.found_pos = found_pos
            self.found_type = found_type
            self.found_new = found_new
