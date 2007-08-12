"""Provides functions to extract portions of the expression tree and
to construct new expressions.  Heavily used in eval.py"""

__license__ = "MIT License"

import sys
from sets import Set

import pair
import types
from symbol import isSymbol, false, Symbol
import unittest
import pogo
import parser


def isSelfEvaluating(exp):
    """Returns True if the expression is self-evaluating."""
    return isNumber(exp) or isString(exp) or pair.isNull(exp)


def isNumber(x):
    """Returns True if we see a number."""
    return type(x) in (types.IntType, types.FloatType, types.LongType)


def isString(x):
    """Returns True if we see a string."""
    return type(x) == types.StringType



def isVariable(exp):
    """Returns true if the expression looks like a symbol."""
    return isSymbol(exp)


def isTaggedList(exp, tag):
    """Returns true if the expression is tagged with the 'tag'."""
    if pair.isList(exp) and pair.length(exp) > 0:
        return pair.car(exp) == tag
    return 0


######################################################################

def isQuoted(exp):
    return (isTaggedList(exp, Symbol("quote")) or
            isTaggedList(exp, Symbol("quasiquote")))

def makeQuoted(exp):
    return pair.list(Symbol("quote"), exp)


def isQuasiquoted(exp):
    return isTaggedList(exp, Symbol("quasiquote"))


def isUnquoted(exp):
    return isTaggedList(exp, Symbol("unquote"))


def textOfQuotation(exp):
    return pair.cadr(exp)


def textOfUnquotation(exp):
    return pair.cadr(exp)


def expandQuasiquotation(exp, depth=1):
    """Takes a quasiquoted expression and constructs a new quoted
    expression.

    FIXME: this function is SO evil.  *grin*  Must clean this up.
    """
    if not pair.isList(exp):
        return makeQuoted(exp)
    if isUnquoted(exp):
        if depth == 1:
            return textOfUnquotation(exp)
        else:
            return pair.list(
                Symbol("list"),
                makeQuoted(Symbol("unquote")),
                expandQuasiquotation(textOfUnquotation(exp), depth - 1))
    if isQuasiquoted(exp):
        return pair.list(
            Symbol("list"),
            makeQuoted(Symbol("quasiquote")),
            expandQuasiquotation(textOfUnquotation(exp), depth + 1))
    else:
        return pair.cons(
            Symbol("list"),
            pair.listMap(lambda subexp:
                         expandQuasiquotation(subexp, depth),
                         exp))



######################################################################

def isLet(exp):
    return isTaggedList(exp, Symbol("let"))


def letBindings(exp):
    return pair.cadr(exp)


def letBindingVariables(bindings):
    if pair.isNull(bindings): return pair.list()
    return pair.cons(pair.car(pair.car(bindings)),
                           letBindingVariables(pair.cdr(bindings)))

def letBindingValues(bindings):
    if pair.isNull(bindings): return pair.list()
    return pair.cons(pair.cadr(pair.car(bindings)),
                           letBindingValues(pair.cdr(bindings)))

def letBody(exp):
    return pair.cdr(pair.cdr(exp))

def letToApplication(exp):
    bindings = letBindings(exp)
    return pair.cons(makeLambda(letBindingVariables(bindings),
                                      letBody(exp)),
                      letBindingValues(bindings))

######################################################################


def isAssignment(exp):
    """Assignments have the form (set! <var> <value>)."""
    return isTaggedList(exp, Symbol("set!"))


def assignmentVariable(exp):
    return pair.cadr(exp)


def assignmentValue(exp):
    return pair.caddr(exp)


def makeAssignment(var, val):
    return pair.list(Symbol("set!"), var, val)


######################################################################


def isDefinition(exp):
    return isTaggedList(exp, Symbol("define"))


def definitionVariable(exp):
    if isSymbol(pair.cadr(exp)):
        return pair.cadr(exp)
    return pair.car(pair.cadr(exp))


def definitionValue(exp):
    if isSymbol(pair.cadr(exp)):
        return pair.caddr(exp)
    return makeLambda(pair.cdr(pair.cadr(exp)),
                      pair.cddr(exp))

def makeDefinition(var, val):
    return pair.list(Symbol("define"), var, val)

######################################################################

def isLambda(exp):
    return isTaggedList(exp, Symbol("lambda"))


def lambdaParameters(exp):
    return pair.cadr(exp)


def lambdaBody(exp):
    return pair.cddr(exp)


def makeLambda(parameters, body):
    return pair.append(pair.list(Symbol("lambda"), parameters),
                       body)


######################################################################


def isIf(exp):
    return isTaggedList(exp, Symbol("if"))


def ifPredicate(exp):
    return pair.cadr(exp)


def ifConsequent(exp):
    return pair.caddr(exp)


def ifAlternative(exp):
    if not pair.isNull(pair.cdddr(exp)):
        return pair.cadddr(exp)
    return false


def makeIf(predicate, consequent, alternative):
    return pair.list(Symbol("if"), predicate, consequent, alternative)


######################################################################

def isBegin(exp):
    return isTaggedList(exp, Symbol("begin"))


def beginActions(exp):
    return pair.cdr(exp)


def isLastExp(seq):
    return pair.isNull(pair.cdr(seq))


def firstExp(seq):
    return pair.car(seq)


def restExps(seq):
    return pair.cdr(seq)


def sequenceToExp(seq):
    if pair.isNull(seq): return seq
    if isLastExp(seq): return firstExp(seq)
    return makeBegin(seq)


def makeBegin(seq):
    return pair.cons(Symbol("begin"), seq)


######################################################################


def isApplication(exp):
    return pair.isList(exp)


def operator(exp):
    if pair.length(exp) == 0:
        raise SchemeError, \
              "No operator given for procedure application -- OPERATOR"
    return pair.car(exp)


def operands(exp):
    return pair.cdr(exp)


def isNoOperands(ops):
    return pair.isNull(ops)


def firstOperand(ops):
    return pair.car(ops)


def restOperands(ops):
    return pair.cdr(ops)


def makeApplication(operators, operands):
    return pair.cons(operators, operands)


######################################################################


def isCond(exp):
    return isTaggedList(exp, Symbol("cond"))


def condClauses(exp):
    return pair.cdr(exp)


def isCondElseClause(clause):
    return condPredicate(clause) == Symbol("else")


def condPredicate(clause):
    return pair.car(clause)


def condActions(clause):
    return pair.cdr(clause)


def condToIf(exp):
    return expandClauses(condClauses(exp))


def expandClauses(clauses):
    if pair.isNull(clauses):
        return false
    first = pair.car(clauses)
    rest = pair.cdr(clauses)
    if isCondElseClause(first):
        if pair.isNull(rest):
            return sequenceToExp(condActions(first))
        raise SchemeError, "else clause isn't last -- condToIf" + clauses
    return makeIf(condPredicate(first),
                  sequenceToExp(condActions(first)),
                  expandClauses(rest))

def isTrue(x):
    return (x != false)


def isFalse(x):
    return (x == false)

                                
######################################################################


def makeProcedure(parameters, body, env):
    return pair.list(Symbol("procedure"), parameters, body, env)

def isCompoundProcedure(p):
    return isTaggedList(p, Symbol("procedure"))

def procedureParameters(p):
    return pair.cadr(p)

def procedureBody(p):
    return pair.caddr(p)

def procedureEnvironment(p):
    return pair.cadddr(p)



######################################################################
"""Here's where we define the primitives of Scheme."""
def isPrimitiveProcedure(proc):
    return isTaggedList(proc, Symbol("primitive"))


def primitiveImplementation(proc):
    return pair.cadr(proc)


def makePrimitiveProcedure(proc):
    return pair.list(Symbol("primitive"), proc)



## We have to tag a continuation slightly different: applying a
## continuation abandons the current computation.
def isContinuationProcedure(proc):
    return isTaggedList(proc, Symbol("continuation"))


def continuationImplementation(proc):
    return pair.cadr(proc)


def makeContinuationProcedure(proc):
    """Procedure is defined to be a function that takes a single 'val'
    argument."""
    return pair.list(Symbol("continuation"), proc)


######################################################################

def toString(expr, quoteStrings=1):
    """Given a Scheme expression, returns a string that tries to nicely
    return it as a string.
    
    If quoteStrings is true, puts quotes around string expressions.

    Notes: this is a little tricky just because we have to account for
    loopy structures.  We keep a set of expressions that we've already
    seen, to make sure we don't retrace any steps.
    """
    seenExpressionIds = Set()

    def isLoopyPair(expr):
        return (pair.isPair(expr) and
                id(pair.cdr(expr)) in seenExpressionIds)

    def markExprAsSeen(expr):
        if not pair.isNull(expr):
            seenExpressionIds.add(id(expr))

    def t_expressionToString(expr, cont):
        """Helper function for toString: written in CPS/trampolined
        form to avoid growing control context."""
        if id(expr) in seenExpressionIds:
            return pogo.bounce(cont, "[...]")

        if pair.isNull(expr):
            return pogo.bounce(cont, "()")
        if not pair.isPair(expr):
            return t_atomExpressionToString(expr, cont)
        elif isPrimitiveProcedure(expr) or isCompoundProcedure(expr):
            return t_procedureExpressionToString(expr, cont)
        else:
            return t_pairExpressionToString(expr, cont)

    def t_atomExpressionToString(expr, cont):
        """Converts an atomic expression (string, number) to a string.
        Written in CPS/trampolined form."""
        if type(expr) is str and quoteStrings:
            return pogo.bounce(cont, "\"%s\"" % expr.replace('"', '\\"'))
        else:
            return pogo.bounce(cont, str(expr))
        
    def t_procedureExpressionToString(expr, cont):
        """Converts a procedure expression to a string."""
        if isPrimitiveProcedure(expr):
            return pogo.bounce(cont,
                                   ('(%s %s <procedure-env>)') % (
                Symbol('primitive-procedure'),
                primitiveImplementation(expr)))
        elif isCompoundProcedure(expr):
            def c_parameters(parameterString):
                def c_body(bodyString):
                    return pogo.bounce(cont,
                                           '(%s %s %s <procedure-env>)' % 
                                           (Symbol('compound-procedure'),
                                            parameterString,
                                            bodyString))
                return t_expressionToString(procedureBody(expr), c_body)
            return t_expressionToString(procedureParameters(expr),
                                        c_parameters)
        
    def t_pairExpressionToString(expr, cont):
        """Converts a pair expression to a string."""
        pieces = []
        def loop(loop_exp, loop_cont):
            if pair.isNull(loop_exp):
                return pogo.bounce(loop_cont, pieces)
            elif pair.isDottedPair(loop_exp) or isLoopyPair(loop_exp):
                def c_car(carString):
                    def c_cdr(cdrString):
                        pieces.append(carString)
                        pieces.append(".")
                        pieces.append(cdrString)
                        return pogo.bounce(loop_cont, pieces)
                    return t_expressionToString(pair.cdr(loop_exp), c_cdr)
                return t_expressionToString(pair.car(loop_exp), c_car)
            else:
                def c_car(carString):
                    pieces.append(carString)
                    return pogo.bounce(loop, pair.cdr(loop_exp), loop_cont)
                return pogo.bounce(t_expressionToString,
                                       pair.car(loop_exp),
                                       c_car)

        markExprAsSeen(expr)
        return loop(expr,
                    lambda pieces: pogo.bounce(cont,
                                                   '(' +
                                                   ' '.join(pieces) +
                                                   ')'))

    return pogo.pogo(t_expressionToString(expr, pogo.land))



######################################################################


class ExpressionTests(unittest.TestCase):
    def setUp(self):
        self._oldrecursionlimit = sys.getrecursionlimit()
        sys.setrecursionlimit(50)

    def tearDown(self):
        sys.setrecursionlimit(self._oldrecursionlimit)

    
    def constructEvilNestedExpression(self, n):
        result = pair.list()
        for i in xrange(n-1):
            result = pair.list(result)
        return result


    def testSimpleExpressionToString(self):
        self.assertEquals("5", toString(5))
        self.assertEquals("x", toString(Symbol("x")))


    def testSimpleListExpressionToString(self):
        self.assertEquals("(x)", toString(pair.list(Symbol("x"))))
        self.assertEquals("(1 2)", toString(pair.list(1, 2)))
        self.assertEquals("(1 (2) 3)", toString(
            pair.list(1, pair.list(2), 3)))
        
    def testDottedPairs(self):
        self.assertEquals("(1 . 2)", toString(pair.cons(1, 2)))


    def testNullList(self):
        self.assertEquals("()", toString(pair.list()))
        self.assertEquals("(() ())", toString(
            pair.list(pair.list(), pair.list())))


    def testTailRecursiveExpressionToString(self):
        n = 1000
        evilExpression = self.constructEvilNestedExpression(n)
        self.assertEquals('(' * n + ')' * n,
                          toString(evilExpression))


    def testRecursiveExpressionsDontKillUs(self):
        ## Makes sure that circular structures do not kill us.
        loopyList = pair.cons(1, 1)
        pair.setCdrBang(loopyList, loopyList)
        self.assertEquals("(1 . [...])", toString(loopyList))


    def testLargerExpression(self):
        program = parser.parse("""
 (define (factorial x)
    (if (= x 0)
         1
         (* x (factorial (- x 1)))))""")
        self.assertEquals("(define (factorial x) (if (= x 0) 1 (* x (factorial (- x 1)))))",
                          toString(program))


if __name__ == '__main__':
    unittest.main()
