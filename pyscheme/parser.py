"""parser.py --- A small scheme parser.

Danny Yoo (dyoo@hkn.eecs.berkeley.edu)

This parser might be useful if we wanted to grab information from the
user using Schemeish lists.  It might also be nice if one is planning
to write a Scheme interpreter in Python.  *cough*


The main functions to use in this module are

    tokenize(): makes a list of tokens out of a string

    parse(s): parse string s, and return a either an atomic value
        (symbol or number) or a pair.

If anything bad happens during the parsing, we'll raise a ParserError.


Some special notes: this module should behave well even under unusual
input: there should be no possibility of hitting the recursion limit,
since we are using trampolined style.
"""

__license__ = "MIT License"

import re
from symbol import Symbol
import pair
import unittest
import pogo


"""The End Of File token is a sentinal that terminates a list of tokens."""
EOF_TOKEN = (None, None)


"""Here are the patterns we pay attention when breaking down a string
into tokens."""
PATTERNS = [ ('whitespace', re.compile(r'(\s+)')),
             ('comment', re.compile(r'(;[^\n]*)')),
             ('(', re.compile(r'(\()')),
             (')', re.compile(r'(\))')),
             ('number', re.compile(r'''( [+\-]?    ## optional sign,
                                         (?:       ## followed by some
                                                   ## decimals
                                              \d+\.\d+
                                            | \d+\.
                                            | \.\d+
                                            | \d+
                                         )
                                       )
                                         ''',
                                   re.VERBOSE)),
             ('symbol',
              re.compile(r'''([a-zA-Z\+\=\?\!\@\#\$\%\^\&\*\-\/\.\>\<]
                              [\w\+\=\?\!\@\#\$\%\^\&\*\-\/\.\>\<]*)''',
                                   re.VERBOSE)),
             ('string', re.compile(r'''
                                      "
                                      (([^\"] | \\")*)
                                      "
                                      ''',
                                   re.VERBOSE)),
             ('\'', re.compile(r'(\')')),
             ('`', re.compile(r'(`)')),
             ## fixme: add UNQUOTE-SPLICING form as well
             (',', re.compile(r'(,)')),
             ]


def tokenize(s):
    """Given a string 's', return a list of its tokens.  A token can
    be one of the following types listed in the PATTERNS above, and
    each token is a 2-tuple: (type, content)."""
    tokens = []
    while 1:
        should_continue = 0
        for tokenType, regex in PATTERNS:
            match_obj = regex.match(s)
            if match_obj:
                should_continue = 1
                tokens.append( (tokenType, match_obj.group(1)) )
                s = s[match_obj.span()[1] :]
        if should_continue == 0:
            break
    tokens.append(EOF_TOKEN)
    return filter(lambda x: x[0] not in ('whitespace', 'comment'),
                  tokens)


"""With the lexer done, now let's direct our attention to the parser."""
######################################################################

class ParserError(Exception):
    """Our personalized exception class."""
    pass


def peek(tokens):
    """Take a quick glance at the first token in our tokens list."""
    if len(tokens) == 0:
        raise ParserError, "While peeking: ran out of tokens."
    return tokens[0]


def eat(tokens, tokenType):
    """Digest the first token in our tokens list, making sure that we're
    biting on the right tokenType of thing."""
    if len(tokens) == 0:
        raise ParserError, "While trying to eat %s: ran out of tokens." % \
              (repr(tokenType),)
    if tokens[0][0] != tokenType:
        raise ParserError, "While trying to eat %s: got token %s instead." % \
                            (repr(tokenType), repr(tokens[0]))
    return tokens.pop(0)

######################################################################




def identity_cont(val):
    return pogo.land(val)


"""Below is our parser for symbol-lists.  We'll use a recursive
descent parsing technique, since Scheme's syntax is so well suited for
it.  Actually, it's a bit more complicated than this.

There is one major problem with a naive rec-descent approach: with
unusual input, we can run into Python's recursion stack limit.  To get
around this, we first wrote the parser normally, and then attacked the
recursion using CPS and trampolining style.  The result is that the
parser works, even with evil input, but it's a bit harder to read.
"""


def parseSingleExpression(tokens, cont=identity_cont):
    """Returns a single Expression, given a sequence of tokens.
    Raises a ParserException if our tokens haven't been exhausted."""
    def c(expression):
        eat(tokens, None)
        return pogo.bounce(cont, expression)

    return parseExpression(tokens, c)


def parseExpression(tokens, cont=identity_cont):
    """Returns an Expression, given a sequence of tokens.
    An expression is made up of one of the following things:
        o  A quoted expression
        o  An atom (like a number or symbol or string)
        o  A list.
    This procedure tries to take care of all these potentials."""
    look_ahead_type = peek(tokens)[0]

    def make_c(quoteType):
        def c(expr):
            return pogo.bounce(cont, pair.list(Symbol(quoteType), expr))
        return c
    if look_ahead_type == '\'':
        eat(tokens, '\'')
        return parseExpression(tokens, make_c('quote'))
    if look_ahead_type == '`':
        eat(tokens, '`')
        return parseExpression(tokens, make_c('quasiquote'))
    elif look_ahead_type == ',':
        eat(tokens, ',')
        return parseExpression(tokens, make_c('unquote'))
    elif look_ahead_type == '(':
        return parseList(tokens, cont)
    elif look_ahead_type in ('number', 'symbol', 'string'):
        return parseAtom(tokens, cont)
    else:
        raise ParserError, "While parsing Expression: no alternatives."


def parseAtom(tokens, cont):
    """Returns an Atom, given a sequence of tokens.
    An atom is either a number, a symbol, or a string."""
    if peek(tokens)[0] == 'number':
        return pogo.bounce(cont, toNumber(eat(tokens, 'number')[1]))
    elif peek(tokens)[0] == 'symbol':
        return pogo.bounce(cont, Symbol(eat(tokens, 'symbol')[1]))
    elif peek(tokens)[0] == 'string':
        return pogo.bounce(cont, eat(tokens, 'string')[1])
    else:
        raise ParserError, "While parsing Atom: no alternatives."


def toNumber(s):
    """Tries to convert string 's' into a number."""
    try:
        return int(s)
    except ValueError:
        return float(s)





def parseList(tokens, cont):
    """Parses a parenthesized list expression."""
    eat(tokens, "(")
    def c_expressionsEaten(val):
        eat(tokens, ")")
        return pogo.bounce(cont, val)
    return pogo.bounce(parseExpressionStar, tokens, c_expressionsEaten)


def parseExpressionStar(tokens, cont):
    """Tries to eat as many expressions as it can see."""
    START_EXPR_SET = ('\'', '`', ',', '(', 'number', 'symbol', 'string')
    if peek(tokens) == ('symbol', '.'):
        ## Handle dotted pairs
        eat(tokens, "symbol")
        return pogo.bounce(parseExpression, tokens, cont)
    elif peek(tokens)[0] in START_EXPR_SET:
        def c_first_eaten(firstVal):
            def c_rest_eaten(restVal):
                return pogo.bounce(cont, pair.cons(firstVal, restVal))
            return pogo.bounce(parseExpressionStar, tokens, c_rest_eaten)
        return pogo.bounce(parseExpression, tokens, c_first_eaten)
    else:
        return pogo.bounce(cont, pair.NIL)


def parse(s):
    """Parse a single string.  This is just a convenience function."""
    return pogo.pogo(parseSingleExpression(tokenize(s),
                                           identity_cont))



######################################################################

class ParserTests(unittest.TestCase):
    def testAtomParsing(self):
        self.assertEquals(42, parse("42"))
        self.assertEquals("particle-man", parse('"particle-man"'))


    def testBrokenNegativeExampleFromBaypiggies(self):
        ## embarassing case that didn't work during the Baypiggies meeting
        ## on September 9, 2004.  Doh!
        self.assertEquals(-42, parse("-42")) 
        

    def testLists(self):
        self.assertEquals(pair.list(1, 2), parse("(1 2)"))
        self.assertEquals(pair.list(1, 2, pair.list(3), 4),
                          parse("(1 2 (3) 4)"))
        self.assertEquals(pair.list(pair.list(pair.list())),
                                          parse("((()))"))

    def testQuotation(self):
        self.assertEquals(pair.list(Symbol("quote"),
                                          Symbol("atom-man")),
                          parse("'atom-man"))
        self.assertEquals(pair.list(Symbol("quasiquote"),
                                          Symbol("istanbul")),
                          parse("`istanbul"))

        self.assertEquals(pair.list(Symbol("unquote"),
                                          Symbol("constantinople")),
                          parse(",constantinople"))

    def testDottedPair(self):
        cons = pair.cons ## shortcut
        self.assertEquals(cons(Symbol("alpha"), Symbol("beta")),
                          parse("(alpha . beta)"))
        self.assertEquals(cons(Symbol("a"),
                               cons(Symbol("b"),
                                    cons(cons(Symbol("c"), Symbol("d")),
                                         pair.NIL))),
                          parse("(a b (c . d))"))


    def testQuotedList(self):
        self.assertEquals(pair.list(Symbol("quote"),
                                          pair.list(Symbol("foo"),
                                                          Symbol("bar"))),
                          parse("'(foo bar)"))


    def testEmptyList(self):
        self.assertEquals(pair.NIL, parse("()"))


    def testStressWithSuperNesting(self):
        ## An evil test to see if this raises bad errors.
        N = 1000
        bigNestedList = pair.list()
        for ignored in xrange(N-1):
            bigNestedList = pair.list(bigNestedList)
        try:
            self.assertEquals(bigNestedList,
                              parse( "(" * N + ")" * N))
        except RuntimeError, e:
            self.fail(e)


if __name__ == '__main__':
    unittest.main()
