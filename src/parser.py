from ast_builder import ASTBuilder
import global_vars
from errors import Errors
from lexer import Token, TT


class BacktrackingParser:
    """Analyzes the syntactic structure of a token sequence generated by the
    Lexer using theoretically infinitely many lookahead tokens and is
    furthermore able to backtrack and thus able to also distinguish rules which
    have the same identical syntactical structure for their first finitely many
    tokens"""

    def __init__(self, lexer):
        """
        :lts: lookahead tokens
        :num_lts: number of lookahead tokens
        :lt_idx: lookahead token index
        :errors: errors that accurred in the last diverging tasting processes
        :max_errors: number of errors that should be collected before
        resetting. Should prevent a list that gets longer and longer
        """
        self.lexer = lexer
        self.markers = []
        self.lts = []
        self.lt_idx = 0
        self.ast_builder = ASTBuilder()

    def LT(self, i) -> Token:
        """Lookahead Token

        :returns: find out token looking ahead i tokens
        """
        self._sync(i)
        # i - 1 because the token self.lt_idx points at is already a lookahead
        # token because all tokens in self.lts are lookahead tokens
        return self.lts[self.lt_idx + i - 1]

    def LTT(self, i) -> TT:
        """Lookahead tokentype

        :returns: find out type locking ahead i tokens
        """
        return self.LT(i).type

    def consume_next_token(self):
        """fills next position in the lookahead tokenlist with token

        :returns: None
        """
        self.lt_idx += 1
        # if one is already one index over the length of self.lts and doesn't
        # need the lookahead tokens anymore because there's no self.taste going
        # on
        if self.lt_idx == len(self.lts) and not global_vars.is_tasting:
            self.lt_idx = 0
            self.lts = []
        self._sync(1)

    def match(self, tokentypes):
        """Check if one of the token are the next token in the lexer to match. In
        general checks if non-terminal symbols are at the right syntactial
        position

        :tokentypes: list of tokentypes
        """
        if self.LTT(1) in tokentypes:
            self.consume_next_token()
        else:
            token = self.LT(1)
            raise Errors.MismatchedTokenError(
                " or ".join(tokentype.value for tokentype in tokentypes),
                token.value,
                token.position,
            )

    def add_and_match(self, tokentypes, classname=None, mapping=None):
        """Same as add, but also check for match

        :tokentypes: list of tokentypes
        :classname: what kind of nodetype should be added
        :mapping: dictionray from which the right nodetype gets determined by
        the LTT
        """
        self._add(classname, mapping)
        self.match(tokentypes)

    def add_and_consume(self, classname=None, mapping=None):
        self._add(classname, mapping)
        self.consume_next_token()

    def _add(self, classname=None, mapping=None):
        """Add the node with the given classname if given or else right
        nodetype matching the tokentype of the current token and with the right
        tokenvalue to the ast

        :classname: nodetype
        :mapping: see docstring of add_and_match
        """
        if not global_vars.is_tasting:
            if not classname:
                classname = mapping.get(self.LTT(1))
                # leave it to the match function to throw the error
                if not classname:
                    return
            self.ast_builder.CN().add_child(
                classname(self.LT(1).value, self.LT(1).position)
            )

    def _sync(self, i):
        """Ensures that one can look ahead i tokens. If one has looked ahead i
        < j tokens previously and next one is going to look ahead j > i tokens
        one only has too load j-i tokens

        :returns: None
        """
        if self.lt_idx + i - 1 > len(self.lts) - 1:
            not_filled_up = self.lt_idx + i - 1 - (len(self.lts) - 1)
            self._fill(not_filled_up)

    def _fill(self, not_filled_up):
        """Add not_filled_up many tokens

        :grammar: grammar specification
        :returns: None
        """
        for _ in range(0, not_filled_up):
            self.lts += [self.lexer.next_token()]

    def _mark(self):
        """rememeber with a marker index where the last taste method call
        occured

        :returns: None
        """
        self.markers += [self.lt_idx]
        # only if all elements of the list are deleted, actions get executed
        # again
        global_vars.is_tasting += 1

    def _release(self):
        """go the the last remembered marker and forget about it

        :returns: None
        """
        self.lt_idx = self.markers.pop()
        global_vars.is_tasting -= 1

    def taste(self, rule, error):
        """Tries ("tastes") out alternative and says whether it will raise a
        exception so one can go on and try out the next alternative. Is used in
        case of syntactically undistinguishable grammar rules.

        :returns: boolean
        """
        tastes_good = True
        self._mark()
        try:
            rule()
        # Lexer errors should always be reported, else it can happen that only
        # the first taste triggers the lexer error and the next taste can
        # continue without error from the last lexer position
        except (Errors.UnknownIdentifierError, Errors.UnclosedCharacterError) as e:
            raise e
        except Exception as e:
            error.val = e
            tastes_good = False
        self._release()
        return tastes_good