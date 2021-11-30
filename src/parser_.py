from ast_builder import ASTBuilder
from abstract_syntax_tree import TokenNode
import global_vars
from errors import MismatchedTokenError, UnknownIdentifierError, UnclosedCharacterError
from lexer import TT


class BacktrackingParser():
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

    def LT(self, i):
        """Lookahead Token

        :returns: find out token looking ahead i tokens
        """
        self._sync(i)
        # i - 1 because the token self.lt_idx points at is already a lookahead
        # token because all tokens in self.lts are lookahead tokens
        return self.lts[self.lt_idx + i - 1]

    def LTT(self, i):
        """Lookahead tokentype

        :returns: find out type locking ahead i tokens
        """
        return self.LT(i).type

    def match(self, token):
        """Check if one of the token are the next token in the lexer to match. In
        general checks if non-terminal symbols are at the right syntactial
        sition

        :token: possibly matching tokentypes (because of symbols like e.g. '-')
        :returns: None, possibly an exception
        """
        if (self.LTT(1) == token):
            self._consume_next_token()
        else:
            raise MismatchedTokenError(token.value, self.LT(1))

    def match_and_add(self, tokentype, classname):
        """Add the current token to the ast and check for match

        :tokentype: possibly matching tokentype
        :returns: None, possibly an exception
        """
        if not global_vars.is_tasting:
            self.ast_builder.CN().add_child(classname(self.LT(1)))
        self.match(tokentype)

    def match_and_determine(self, tokentype):
        if not global_vars.is_tasting:
            self.ast_builder.CN().determine(self.LT(1))
        self.match(tokentype)

    def _sync(self, i):
        """ensures that one can look ahead i tokens. If one has looked ahead i
        < j tokens previously and next one is going to look ahead j > i tokens
        one only has too load j-i tokens

        :returns: None
        """
        if self.lt_idx + i - 1 > len(self.lts) - 1:
            not_filled_up = self.lt_idx + i - 1 - (len(self.lts) - 1)
            self._fill(not_filled_up)

    def _fill(self, not_filled_up):
        """add not_filled_up many tokens

        :grammar: grammar specification
        :returns: None
        """
        for _ in range(0, not_filled_up):
            self.lts += [self.lexer.next_token()]

    def _consume_next_token(self):
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

    def _mark(self):
        """rememeber with a marker index where the last taste method call
        occured

        :returns: None
        """
        self.markers += [self.lt_idx]
        # only if all elements of the list are deleted, actions get executed
        # again
        global_vars.is_tasting += 1
        # return self.lt_idx

    def _release(self):
        """go the the last remembered marker and forget about it

        :returns: None
        """
        self.lt_idx = self.markers.pop()
        global_vars.is_tasting -= 1

#     def _is_tasting(self):
#         """if in the taste method every mark() found his corresponding
#         release()
#
#         :returns: boolean
#         """
#         return len(self.markers) > 0

    def taste(self, rule, errors):
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
        except (UnknownIdentifierError, UnclosedCharacterError) as e:
            raise e
        except Exception as e:
            errors += [e]
            tastes_good = False
        self._release()
        return tastes_good


# class LL_Recursive_Decent_Parser:

# """Analyzes the syntactic structure of a token sequence generated by the
# Lexer using  k>1 lookahead tokens
# """

# def __init__(self, lexer, num_lts):
# """
# :lts: lookahead tokens
# :num_lts: number of lookahead tokens
# :lt_idx: lookahead token index

# """
# self.lexer = lexer
# self.num_lts = num_lts
# self.lts = [0] * self.num_lts
# self.lt_idx = 0
# for _ in range(self.num_lts):
# self.next_token()
# self.ast_builder = ASTBuilder()

# def next_token(self):
# """fills next position in the lookahead tokenlist with token

# :returns: None
# """
# self.lts[self.lt_idx] = self.lexer.next_token()
# self.lt_idx = (self.lt_idx + 1) % self.num_lts

# def LT(self, i):
# """Lookahead Token

# :returns: find out token looking ahead i tokens
# """
# return self.lts[(self.lt_idx + i - 1) % self.num_lts]

# def LTT(self, i):
# """Lookahead tokentype

# :returns: find out type locking ahead i tokens
# """
# return self.LT(i).type

# def match(self, tts):
# """Check if one of the tts are the next token in the lexer to match. In
# general checks if non-terminal symbols are at the right syntactial
# position

# :tts: possibly matching tokentypes (because of symbols like e.g. '-')
# :returns: None, possibly an exception
# """
# if (self.LTT(1) in tts):
# self.next_token()
# else:
# raise SyntaxError("'" + tts.value + "'", self.LT(1))

# def match_and_add(self, tts):
# """Add the current token to the ast and check for match

# :tts: possibly matching tokentypes (because of symbols like e.g. '-')
# :returns: None, possibly an exception
# """
# # if (self.ast_builder.current_node.token not in tts):
# self.ast_builder.addChild(TokenNode(self.LT(1)))
# self.match(tts)
