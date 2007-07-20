"""Environment stuff.  Exercise 4.11 asks us to develop an alternative
environment implementation.  This is an implementation of environments
that uses a chained list of Python dictionaries.
"""

__license__ = "MIT License"

from symbol import Symbol
from error import SchemeError
import pair

def enclosingEnvironment(env):
    return env[1:]

def firstFrame(env):
    return env[0]


THE_EMPTY_ENVIRONMENT = []


def makeFrame(var_pairs, val_pairs):
    """Note: here I diverge from SICP's implementation: instead of
    using a cons, I use a Python list.  The selectors frameVariables()
    and frameValues() reflect this."""
    car, cdr, isNull = pair.car, pair.cdr, pair.isNull
    frame = {}
    while not isNull(var_pairs):
        if pair.isPair(var_pairs):
            if not isNull(val_pairs):
                frame[car(var_pairs)] = car(val_pairs)
                var_pairs, val_pairs = cdr(var_pairs), cdr(val_pairs)
            else:
                raise SchemeError, "Too few arguments supplied"
        else:
            frame[var_pairs] = val_pairs
            var_pairs, val_pairs = pair.NIL, pair.NIL
    if isNull(val_pairs):
        return frame
    else:
        raise SchemeError, "Too many arguments supplied"




def addBindingToFrame(var, val, frame):
    frame[var] = val


def extendEnvironment(var_pairs, val_pairs, base_env):
    """Extends an environment with a new set of bindings.  Extended to
    support Scheme's dotted notation for varargs."""
##     if Symbol('.') in vars:
##         vararg_start = vars.index(Symbol('.'))
##         return [makeFrame(vars[:vararg_start] + [vars[vararg_start+1]],
##                           vals[:vararg_start] + [vals[vararg_start:]])
##                 ] + base_env
##     elif len(vars) == len(vals):
    return [makeFrame(var_pairs, val_pairs)] + base_env
## FIXME: add length check!
##     elif len(vars) < len(vals):
##         raise SchemeError, \
##               "Too many arguments supplied %s %s" % (vars, vals)
##     raise SchemeError, "Too few arguments supplied %s %s" % (vars, vals)




def lookupVariableValue(var, env):
    while 1:
        if env == THE_EMPTY_ENVIRONMENT:
            raise SchemeError, "Unbound variable " + var
        frame = firstFrame(env)
        if frame.has_key(var):
            return frame[var]
        env = enclosingEnvironment(env)
    

def setVariableValue(var, val, env):
    while 1:
        if env == THE_EMPTY_ENVIRONMENT:
            raise SchemeError, "Unbound variable -- SET! " + var
        frame = firstFrame(env)
        if frame.has_key(var):
            frame[var] = val
            return
        env = enclosingEnvironment(env)


def defineVariable(var, val, env):
    frame = firstFrame(env)
    if frame.has_key(var):
        frame[var] = val
        return
    addBindingToFrame(var, val, frame)


