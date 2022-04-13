from error_handler import ErrorHandler, AnnotationScreen
import warnings
from colormanager import ColorManager as CM


class _WarningHandler(ErrorHandler):
    """Output a detailed warning"""

    _instance = None

    def __init__(self, fname, finput):
        self.fname = fname
        self.finput = finput
        # list of warnings collected during execution
        self.warnings = []

    def add_warning(self, warning):
        self.warnings += [warning]

    def show_warnings(self):
        for warning in self.warnings:
            match warning:
                case warnings.Warnings.ImplicitConversionWarning() as w:
                    warning_header = self._warning_header(w.found_pos, w.description)
                    warning_screen = AnnotationScreen(
                        self.finput, w.found_pos[0], w.found_pos[0]
                    )
                    warning_screen.mark(w.found_pos, len(w.found))

                    node_header = self._warning_header(
                        w.variable_pos,
                        f"{CM().MAGENTA}Note{CM().RESET}: Variable '{w.variable}' definied as type "
                        f"'{w.variable_type}' here:",
                    )
                    warning_screen_2 = AnnotationScreen(
                        self.finput, w.variable_pos[0], w.variable_pos[0]
                    )
                    warning_screen_2.mark(w.variable_pos, len(w.variable))

                    warning_screen.filter()
                    warning_screen_2.filter()

                    node_end = self._warning_header(
                        None,
                        f"{CM().MAGENTA}Note{CM().RESET}: Datatype '{w.variable_type}' has only range "
                        f"{w.variable_from} to {w.variable_to}",
                    )
                    print(
                        f"\n"
                        + warning_header
                        + str(warning_screen)
                        + node_header
                        + str(warning_screen_2)
                        + node_end
                    )

    def _warning_header(self, pos, descirption):
        return super()._error_header(pos, descirption)


def WarningHandler(fname=None, finput=None):
    """Factory Function as possible way to implement Singleton Pattern.
    Taken from here:
    https://stackoverflow.com/questions/52351312/singleton-pattern-in-python

    :returns: None
    """
    if not _WarningHandler._instance:
        if not fname or not finput:
            raise Exception(
                "When being initialised for the first time fname and finput"
                "must be provided"
            )
        _WarningHandler._instance = _WarningHandler(fname, finput)
    return _WarningHandler._instance
