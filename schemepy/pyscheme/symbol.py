"""A simple "symbol" class for Python.  Symbols are like strings,
except that symbols should only be comparable to other symbols.  This
module is designed so that one should be able to do a "from symbol
import *" on this.

To create a new Symbol, use the Symbol() function, like this:

    hello = Symbol("hello")

All symbols are interned so that comparison using 'is' will work.  For
example,

    Symbol("hello") is Symbol("h" + "ello")

should work.

By default, all symbols are case insensitive, but if the module
variable CASE_SENSITIVE is set to a true value, symbols will become
case sensitive.

Also, we use the UserString to make sure that symbols are of a
different "class" than Strings.  isSymbol() depends on this
representation, so be careful about changing it.

"""

__license__ = "MIT License"


from UserString import UserString as __UserString
import weakref

__all__ = ['Symbol', 'isSymbol']


"""By default, symbols are case-insensitive."""
CASE_SENSITIVE = 0


class __Symbol(__UserString):
    """Support class for symbols."""
    def __eq__(self, other):
        """Comparison should only be possible between symbols.  Since all
        Symbols are interned, this is equivalent to an 'is' check."""
        return self is other


"""A global dictionary that contains all known symbols.
__interned_symbols: strings -> symbols

The dictionary uses weak references to reduce the chance of symbol abuse.
"""
__interned_symbols = weakref.WeakValueDictionary({})


def Symbol(s):
    """Generates a new Symbol that we guarantee can be compared in
    constant time to any other symbol."""
    global __interned_symbols

    ## Defensive programming measure:
    assert not isinstance(s, __Symbol), ("%s already a symbol!" % s)

    if not CASE_SENSITIVE: s = s.lower()
    if not __interned_symbols.has_key(s):
        ## Subtle note: we have to use a local variable here to store the newSymbol.
        ## If we had tried something shorter like:
        ##
        ##     __interned_symbol[s] = __Symbol(s)
        ##
        ## then the new Symbol will immediately evaporate since there
        ## aren't any hard references!  Weak references can be tricky.
        newSymbol = __Symbol(s)
        __interned_symbols[s] = newSymbol
    return __interned_symbols[s]




"""Here are definitions of symbols that we should know about."""
false = Symbol("#f")
true = Symbol("#t")
__empty_symbol = Symbol("")


def isSymbol(x):
    """Returns True if x is already a symbol."""
    return type(x) == type(__empty_symbol)



def makeUniqueTemporary(_counter = [0]):
    """Constructs a symbol that does not collide with any other
    symbol.  I'll use this to help with the macro-expansion.

    NOTE/FIXME: we do this by making an "illegal" symbol which starts
    with a number and contains a space.  The parser module doesn't
    allow such symbols to exist... although it's possible to subvert this
    by calling STRING->SYMBOL.  So this mechanism is not perfect.
    """
    while ('%d*** temporary' % _counter[0]) in __interned_symbols:
        _counter[0] += 1
    return Symbol('%d*** temporary' % _counter[0])
