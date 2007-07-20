"""A evaluator based on CPS form and trampolining.



FIXME: add a lot more documentation here about how this all works.


The core forms that the evaluator recognizes is the following:

    self evaluating expressions
    variable references
    QUOTE
    SET!
    DEFINE
    IF
    LAMBDA
    BEGIN
    function application

Other special forms are handled by derivation: the expander module translates
the derived forms into these core forms.

FIXME: quasiquotation hasn't been pushed off into the expander yet.

"""

__license__ = "MIT License"

import pogo
import expressions
import environment
import exceptions
import traceback
import types
import pair
from parser import parse
from symbol import false, Symbol
from error import SchemeError

def identity(val):
    """The identity function."""
    return val



"""We need to save Python's apply() function, since we use it later on
to evaluate primitive procedure calls.  For symmetry, I'm also saving
Python's eval() function within evalInUnderlyingPython()."""
evalInUnderlyingPython = eval
applyInUnderlyingPython = apply



######################################################################
## The heart of the interpreter is eval/apply.
##
## Some notes here: I'm using trampolined style to get around Python's
## lack of tail recursion.


def eval(exp, env):
    return pogo.pogo(teval(exp, env, pogo.land))


def teval(exp, env, cont):
    """Evaluates an expression 'exp' in an environment 'env'.

    Exercise 4.3 asks us to rewrite this in a more natural
    data-directed manner.  Pychecker, also, doesn't like seeing
    so many 'return' statements in one function.  *grin*
    """
    if expressions.isSelfEvaluating(exp):
        return pogo.bounce(cont, exp)
    if expressions.isVariable(exp):
        return pogo.bounce(cont, environment.lookupVariableValue(exp, env))
    if expressions.isQuoted(exp):
        return evalQuoted(exp, env, cont)
    if expressions.isAssignment(exp):
        return evalAssignment(exp, env, cont)
    if expressions.isDefinition(exp):
        return evalDefinition(exp, env, cont)
    if expressions.isIf(exp):
        return evalIf(exp, env, cont)
    if expressions.isLambda(exp):
        return pogo.bounce(cont, expressions.makeProcedure
                          (expressions.lambdaParameters(exp),
                           expressions.lambdaBody(exp),
                           env))
    if expressions.isBegin(exp):
        return evalSequence(expressions.beginActions(exp), env, cont)
    if expressions.isApplication(exp):
        return evalApplication(exp, env, cont)
    raise SchemeError, "Unknown expression type -- eval " + str(exp)



def apply(procedure, arguments, env, cont):
    """Applies a procedure on a list of arguments."""
    if expressions.isPrimitiveProcedure(procedure):
        return applyPrimitiveProcedure(procedure, arguments, env, cont)
    elif expressions.isContinuationProcedure(procedure):
        return applyContinuationProcedure(procedure, arguments)
    if expressions.isCompoundProcedure(procedure):
        newEnv = environment.extendEnvironment(
            expressions.procedureParameters(procedure),
            arguments,
            expressions.procedureEnvironment(procedure))
        return evalSequence(expressions.procedureBody(procedure), newEnv, cont)
    raise SchemeError, "Unknown procedure type -- apply " + str(procedure)



def applyPrimitiveProcedure(proc, args, env, cont):
    try:
        return applyInUnderlyingPython(expressions.primitiveImplementation(proc),
                                       [cont, env, pair.toPythonList(args)])
    except Exception, e:
        if isinstance(e, exceptions.SystemExit): raise e
        raise SchemeError, e


def applyContinuationProcedure(proc, args):
    try:
        return applyInUnderlyingPython(expressions.continuationImplementation(proc),
                                       pair.toPythonList(args))
    except Exception, e:
        if isinstance(e, exceptions.SystemExit): raise e
        raise SchemeError, e



def evalRands(exps, env, cont):
    """Given a list of expressions, returns a new list containing the
    values of evaluating each on of them.  If the continuation is
    given, then calls cont() on the evaluated operands instead."""
    def c1(head_val):
        def c2(tail_val):
            return pogo.bounce(cont, pair.cons(head_val, tail_val))
        return evalRands(expressions.restOperands(exps), env, c2)
    if expressions.isNoOperands(exps):
        return pogo.bounce(cont, pair.list())
    return teval(expressions.firstOperand(exps), env, c1)


def evalIf(exp, env, cont):
    def c(predicate_val):
        if expressions.isTrue(predicate_val):
            return teval(expressions.ifConsequent(exp), env, cont)
        else:
            return teval(expressions.ifAlternative(exp), env, cont)
    return teval(expressions.ifPredicate(exp), env, c)


def evalSequence(exps, env, cont):
    def c(val):
        return evalSequence(expressions.restExps(exps), env, cont)
    if expressions.isLastExp(exps):
        return teval(expressions.firstExp(exps), env, cont)
    else:
        return teval(expressions.firstExp(exps), env, c)


def evalAssignment(exp, env, cont):
    def c(val):
        environment.setVariableValue(expressions.assignmentVariable(exp),
                                     val, env)
        return pogo.bounce(cont, Symbol("ok"))
    return teval(expressions.assignmentValue(exp), env, c)


def evalDefinition(exp, env, cont):
    def c(val):
        environment.defineVariable(
            expressions.definitionVariable(exp), val, env)
        return pogo.bounce(cont, Symbol("ok"))
    return teval(expressions.definitionValue(exp), env, c)


def evalApplication(exp, env, cont):
    def c1(operator_val):
        def c2(operands_val):
            return apply(operator_val, operands_val, env, cont)
        return evalRands(expressions.operands(exp), env, c2)
    return teval(expressions.operator(exp), env, c1)


def evalQuoted(exp, env, cont):
    """Returns a quoted expression, using deepQuotedEval to look for
    UNQUOTE.

    Consequently, quoted elements are properly turned into cons pairs.
    """
    text = expressions.textOfQuotation(exp)
    if expressions.isQuasiquoted(exp):
        expandedExp = expressions.expandQuasiquotation(text)
        return pogo.bounce(teval,
                               expandedExp,
                               env,
                               cont)
    else:
        return pogo.bounce(cont, text)
