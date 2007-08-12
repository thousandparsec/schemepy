"""Implementation of pairs for Python.

Pairs are like linked lists in Python.  For historical reasons, we use
the following funny names to construct and destructure lists:

    cons(head, tail) --- constructs a ConsPair that consists of a
    head and a tail.

    car(pair) --- returns the head of a ConsPair.

    cdr(pair) --- returns the tail of a ConsPair.

Scheme's lists are built up of pair chains terminated by NIL.

The reason we use a separate factory function --- cons() --- instead
of directly using the ConsPair is because we may want the freedom to
change implementation later on.  In SICP, in fact, there's a totally
screwy implementation that uses lambdas entirely, with no real data
structure.

There are a few more convenience functions here to rapidly make these
pair structures.  For example, there's a list() function here that,
given a set of arguments, produces a pair chain.
"""


__license__ = "MIT License"


"""This module is not 'from pair import *' safe!  Particularly because
we define a few functions here that have names that conflict with
builtins.  Let's enforce this restriction."""
__all__ = []


from sets import Set

from symbol import Symbol
from error import SchemeError
import pogo
import unittest


"""The NIL atom.  There should be only one!"""
NIL = []


class ConsPair(list): pass


def isNull(x):
    return x is NIL


def isPair(p):
    return type(p) is ConsPair


def cons(head, rest):
    """Returns the concatentation of head with rest."""
    return ConsPair([head, rest])



def car(p):
    """Returns the head of the pair."""
    if not isPair(p):
        raise SchemeError, "CAR --- argument is not a pair."
    if p is NIL:
        raise SchemeError, "CAR --- cannot take CAR of empty list."
    else:
        return p[0]


def cdr(p):
    """Returns the tail of the pair."""
    if not isPair(p):
        raise SchemeError, "CDR --- argument is not a pair."
    if p is NIL:
        raise SchemeError, "CDR --- cannot take CDR of empty list."
    else:
        return p[1]


def cddr(p):
    return cdr(cdr(p))

def cdddr(p):
    return cdr(cdr(cdr(p)))


def cadr(p):
    return car(cdr(p))

def caddr(p):
    return car(cdr(cdr(p)))

def cadddr(p):
    return car(cdr(cdr(cdr(p))))



def setCarBang(pair, element):
    """Sets the head of the pair to the element."""
    if not isPair(pair):
        raise SchemeError, "SET-CAR! --- cannot set car of non-pair."
    pair[0] = element
    return Symbol("ok")


def setCdrBang(pair, element):
    """Sets the tail of the pair to the element."""
    if not isPair(pair):
        raise SchemeError, "SET-CAR! --- cannot set car of non-pair."
    pair[1] = element
    return Symbol("ok")



## Hmm... some of these functions really belong in builtins.py.

def isList(p):
    """Returns True if p refers to a list-like structure.
    Note: loopy structures don't qualify as lists.
    """
    seenPairIds = Set()
    while True:
        if id(p) in seenPairIds:
            return 0
        seenPairIds.add(id(p))
        if isNull(p): return 1
        if not isPair(p): return 0
        p = cdr(p)


def isDottedPair(p):
    """Returns True if p refers to an improper list, where the cdr is
    not a pair."""
    if not isPair(p): return 0
    elif isPair(cdr(p)) or isNull(cdr(p)): return 0
    else: return 1


def length(p):
    """Returns the length of p.  Assumes that p is a list."""
    if not isList(p): raise SchemeError, "LENGTH --- not a list"
    length = 0
    while True:
        if isNull(p): return length
        length += 1
        p = cdr(p)


def reverse(p):
    """Reverses a list."""
    if not isList(p): raise SchemeError, "REVERSE --- not a list"
    result = NIL
    while not isNull(p):
        result = cons(car(p), result)
        p = cdr(p)
    return result



def listMap(f, p):
    """Maps a function f across p."""
    if not isList(p): raise SchemeError, "MAP --- not a list"
    resultsRev = NIL
    while not isNull(p):
        resultsRev = cons(f(car(p)), resultsRev)
        p = cdr(p)
    return reverse(resultsRev)



def c_listMap(c_f, p, cont, allow_improper_lists=False):
    """Maps a function f across p, but in a continuation-passed style.

    'c_f' is a function that takes a 2-tuple (element, cont),
    the element and the continuation.

    'cont' is the continutation we apply on the mapped list.

    If the optional keyword parameter 'allow_improper' is set to True,
    then we'll also allow mapping across improper lists.
    """
    if isNull(p):
        return pogo.bounce(cont, NIL)
    if not isPair(p):
        if allow_improper_lists:
            return pogo.bounce(c_f, p, cont)
        else:
            raise SchemeError, "CMAP --- not a list"
    def c_head(head_val):
        def c_tail(tail_val):
            return pogo.bounce(cont, cons(head_val, tail_val))
        return pogo.bounce(c_listMap, c_f, cdr(p), c_tail,
                           allow_improper_lists)
    return pogo.bounce(c_f, car(p), c_head)


    
def append(*lists):
    """Appends all lists together."""
    appended_list = lists[-1]
    for i in xrange(len(lists)-2, -1, -1):
        next_list = lists[i]
        appended_list = pogo.pogo(
            c_appendTwo(next_list, appended_list, pogo.land))
    return appended_list


def c_appendTwo(front, back, cont):
    """Appends two lists together.  Written in continuation passing style."""
    if not isList(front): raise SchemeError, "MAP --- not a list"
    if not isList(back): raise SchemeError, "MAP --- not a list"
    if isNull(front):
        return pogo.bounce(cont, back)
    def c(appendedRest):
        return pogo.bounce(cont, cons(car(front),
                                                appendedRest))
    return pogo.bounce(c_appendTwo, cdr(front), back, c)



def toPythonList(pair):
    """Does a shallow conversion of a pair list chain to a Python list."""
    if not isList(pair): raise SchemeError, "not a list"
    elements = []
    while not isNull(pair):
        elements.append(car(pair))
        pair = cdr(pair)
    return elements


"""Let's save the old version of Python's list function."""
list_in_underlying_python = list 


def list(*elements):
    """Does a shallow conversion of a Python list to a pair chain.

Warning: this does have the same name as the builtin list() function
in Python.
    """
    result = list_in_underlying_python(elements)
    result.reverse()
    return reduce(lambda x, y: cons(y, x), [NIL] + result)


######################################################################

class PairTests(unittest.TestCase):
    def testNull(self):
        self.assert_(isList(NIL))

    def testReversal(self):
        self.assertEquals(list(1, 2, 3, 4, 5),
                          reverse(list(5, 4, 3, 2, 1)))

    def testMapping(self):
        self.assertEquals(list(2, 4, 6, 8),
                          listMap(lambda x: x*2, list(1, 2, 3, 4)))

    def testAppendTwo(self):
        self.assertEquals(list(1, 2, 3, 4),
                          pogo.pogo(c_appendTwo(list(1, 2),
                                                list(3, 4),
                                                pogo.land)))


    def testContinuationMapping(self):
        def c_square(x, cont):
            return pogo.bounce(cont, x**2)

        self.assertEquals(cons(4, 9),
                          pogo.pogo(c_listMap(c_square, cons(2, 3),
                                              pogo.land,
                                              allow_improper_lists=True)))
        self.assertRaises(SchemeError,
                          pogo.pogo,
                          pogo.bounce(c_listMap, c_square,
                                      cons(2, 3), pogo.land))

        self.assertEquals(list(1, 4, 9, 16),
                          pogo.pogo(c_listMap(c_square,
                                              list(1, 2, 3, 4),
                                              pogo.land)))


if __name__ == '__main__':
    unittest.main()
