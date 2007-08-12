"""Defines a base built-in environment, with all the primitives."""

__license__ = "MIT License"

import types
import math
import sys

import pogo
from symbol import Symbol, true, false
import expressions
import environment
import pair
from parser import parse
import evaluator
from error import SchemeError
import operator




def schemeParse(string):
    """Given a string, returns the pair list parsing of that string."""
    return parse(string)


def allNumbers(numbers):
    for n in numbers:
        if type(n) not in (types.IntType, types.LongType, types.FloatType):
            return 0
    return 1


def schemeAdd(*numbers):
    if len(numbers) == 0: return 0
    if not allNumbers(numbers):
        raise SchemeError, "primitive '+' --- arguments must be numbers"
    return reduce(operator.add, numbers)

def schemeSubtract(*numbers):
    if len(numbers) == 0:
        raise SchemeError, "primitive '-' --- expects 1 or more arguments"
    if not allNumbers(numbers):
        raise SchemeError, "primitive '-' --- arguments must be numbers"
    if len(numbers) == 1:
        return -numbers[0]
    return reduce(operator.sub, numbers)

def schemeMultiply(*numbers):
    if len(numbers) == 0: return 1
    if not allNumbers(numbers):
        raise SchemeError, "primitive '*' --- arguments must be numbers"
    return reduce(operator.mul, numbers)

def schemeDivide(*numbers):
    if len(numbers) == 0:
        raise SchemeError, "primitive '/' --- expects 1 or more arguments"
    if not allNumbers(numbers):
        raise SchemeError, "primitive '/' --- arguments must be numbers"
    return reduce(operator.div, numbers)

def schemeRemainder(a, b):
    if not allNumbers([a, b]):
        raise SchemeError, "primitive 'remainder' --- arguments must be numbers"
    return a % b

def schemePower(a, b):
    if not allNumbers([a, b]):
        raise SchemeError, "primitive 'power' --- arguments must be numbers"
    return a ** b

def schemeQuotient(a, b):
    if not allNumbers([a, b]):
        raise SchemeError, "primitive 'quotient' --- arguments must be numbers"
    return int(a / b)

def schemeSqrt(a):
    if not allNumbers([a]):
        raise SchemeError, "primitive 'sqrt' --- argument must be a number"
    return math.sqrt(a)

def schemeFloor(a):
    if not allNumbers([a]):
        raise SchemeError, "primitive 'floor' --- argument must be a number"
    return int(math.floor(a))

def schemeCeiling(a):
    if not allNumbers([a]):
        raise SchemeError, "primitive 'ceiling' --- argument must be a number"
    return int(math.ceil(a))

def schemeNumericalEq(a, b):
    """Here, we need to make sure that we're returning the metacircular
    values of true or false."""
    return schemeBooleanize(a == b)

def schemeLessThan(a, b): return schemeBooleanize(a < b)
def schemeLessThanOrEquals(a, b): return schemeBooleanize(a <= b)
def schemeGreaterThan(a, b): return schemeBooleanize(a > b)
def schemeGreaterThanOrEquals(a, b): return schemeBooleanize(a >= b)

def schemeEqQuestion(a, b):
    if type(a) in (types.IntType, types.FloatType, types.LongType):
        return schemeBooleanize(a == b)
    return schemeBooleanize(a is b)

def schemeEqualQuestion(a, b): return schemeBooleanize(a == b)
def schemeListQuestion(a): return schemeBooleanize(pair.isList(a))
def schemeNullQuestion(a): return schemeBooleanize(pair.isNull(a))


def schemeDisplay(thing):
    sys.stdout.write(expressions.toString(thing,
                                          quoteStrings=0))
    return Symbol("ok")


def schemeWrite(thing):
    sys.stdout.write(expressions.toString(thing,
                                          quoteStrings=1))
    return Symbol("ok")


def schemeNewline():
    sys.stdout.write("\n")
    return Symbol("ok")

def schemeStringToSymbol(mystr): return Symbol(mystr)
def schemeSymbolToString(mysymbol): return str(mysymbol)
def schemeNumberToString(mynumber): return str(mynumber)

def schemeStringAppend(*strings):
    if len(strings) == 0: return ""
    return reduce(operator.add, strings)


def schemeNot(x):
    if x == false: return true
    return false

def schemeQuit():
    sys.stdout.write("bye\n")
    sys.exit(0)

def schemeBooleanize(x):
    """Translates what Python considers true and false to the Scheme
    symbols "true" or "false"."""
    if x: return true
    return false


def schemePairQuestion(L):
    return schemeBooleanize(pair.isPair(L))


def schemeError(*args):
    raise SchemeError, ' '.join(map(expressions.toString, args))


def wrapPrimitiveWithDefaults(f):
    """Normal primitives don't know what to do with their continuation
    or environment arguments, so this wrapper provides a nice
    default."""
    def newPrimitive(cont, env, args):
        return pogo.bounce(cont, (f(*args)))
    return newPrimitive


######################################################################


def installPythonFunction(name, function, env, wrapDefaults=True):
    """Installs a new Python function as a primitive into the given
    environment 'env'"""
    if wrapDefaults:
        wrappedProcedure = expressions.makePrimitiveProcedure(
            wrapPrimitiveWithDefaults(function))
    else:
        wrappedProcedure = expressions.makePrimitiveProcedure(function)
    environment.defineVariable(Symbol(name), wrappedProcedure,
                               env)


def setupEnvironment():
    """Sets up a new environment with a bunch of fairly standard
    Scheme built-in primitives."""
    PRIMITIVE_PROCEDURES = [
        ["car", pair.car],
        ["cdr", pair.cdr],
        ["cons", pair.cons],
        ["append", pair.append],
        ["list", pair.list],
        ["set-car!", pair.setCarBang],
        ["set-cdr!", pair.setCdrBang],
        ["+", schemeAdd],
        ["-", schemeSubtract],
        ["*", schemeMultiply],
        ["/", schemeDivide],
        ["remainder", schemeRemainder],
        ["quotient", schemeQuotient],
        ["sqrt", schemeSqrt],
        ["floor", schemeFloor],
        ["ceiling", schemeCeiling],
        ["=", schemeNumericalEq],
        ["<", schemeLessThan],
        ["<=", schemeLessThanOrEquals],
        [">", schemeGreaterThan],
        [">=", schemeGreaterThanOrEquals],
        ["eq?", schemeEqQuestion],
        ["equal?", schemeEqualQuestion],
        ["list?", schemeListQuestion],
        ["pair?", schemePairQuestion],
        ["null?", schemeNullQuestion],
        ["display", schemeDisplay],
        ["write", schemeWrite],
        ["newline", schemeNewline],
        ["not", schemeNot],
        ["string->symbol", schemeStringToSymbol],
        ["symbol->string", schemeSymbolToString],
        ["number->string", schemeNumberToString],
        ["string-append", schemeStringAppend],
        ["quit", schemeQuit],
        ["exit", schemeQuit],
        ["error", schemeError],
        ["parse", schemeParse],
        ["pow", schemePower],
        ]

    initial_environment = environment.extendEnvironment(
        pair.NIL, pair.NIL, environment.THE_EMPTY_ENVIRONMENT)

    for name, proc in PRIMITIVE_PROCEDURES:
        installPythonFunction(name, proc, initial_environment)


    ## Finally, put true and false in there.
    environment.defineVariable(Symbol("#t"), Symbol("#t"), initial_environment)
    environment.defineVariable(Symbol("#f"), Symbol("#f"), initial_environment)
    return initial_environment
