"""An analyzer that does syntactic analysis of an expression.

Danny Yoo (dyoo@hkn.eecs.berkeley.edu)

analyze() returns a function that can be evaluated just by calling it
with the environment and continuation.  It's based (or bastardized,
depending on your perspective... *grin*) on material in Chapter 4.1.7
of Structure and Interpretation of Computer Programs:

http://mitpress.mit.edu/sicp/full-text/book/book-Z-H-26.html#%25_sec_4.1.7

This is slightly more complicated since I'm using continuation passing
style and trampolining to get around Python's call stack.

The core forms that the analyzer recognizes is the following:

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

FIXME: the analyzer itself is not in continuation passing mode.  The
analyzed expressions that it produces do use CPS.

FIXME: quasiquotation hasn't been pushed off into the expander yet.

"""


__license__ = "MIT License"

import exceptions
import traceback

import expressions
import pogo
import environment
import pair
from symbol import Symbol
from error import SchemeError

applyInUnderlyingPython = apply


def analyze(exp):
    """analyze(exp) -> lambda env, cont: ...
    Given an expression, returns a new lambda function that can be applied
    on an environment and continuation."""
    if expressions.isSelfEvaluating(exp):
        return analyzeSelfEvaluating(exp)
    if expressions.isVariable(exp):
        return analyzeVariable(exp)
    if expressions.isQuoted(exp):
        return analyzeQuoted(exp)
    if expressions.isAssignment(exp):
        return analyzeAssignment(exp)
    if expressions.isDefinition(exp):
        return analyzeDefinition(exp)
    if expressions.isIf(exp):
        return analyzeIf(exp)
    if expressions.isLambda(exp):
        return analyzeLambda(exp)
    if expressions.isBegin(exp):
        return analyzeBegin(exp)
    ## Application checking must come last, after all the special forms.
    ## have been tested.
    if expressions.isApplication(exp):
        return analyzeApplication(exp)

    ## And if we get here, bad things have happened.
    raise SchemeError, ("Unknown expression type -- eval " +
                        expressions.toString(exp))


def analyzeSelfEvaluating(exp):
    return (lambda env, cont:
            pogo.bounce(cont, exp))


def analyzeVariable(exp):
    return (lambda env, cont:
            pogo.bounce(cont, environment.lookupVariableValue(exp, env)))


def analyzeQuoted(exp):
    text = expressions.textOfQuotation(exp)
    ## the common case is to handle simple quotation.
    if not expressions.isQuasiquoted(exp):  
        return (lambda env, cont:
                pogo.bounce(cont, text))
    else:
        return analyze(expressions.expandQuasiquotation(text))


def analyzeAssignment(exp):
    varName = expressions.assignmentVariable(exp)
    analyzedValueBody = analyze(expressions.assignmentValue(exp))
    def analyzed(env, cont):
        def c(varVal):
            environment.setVariableValue(varName, varVal, env)
            return pogo.bounce(cont, Symbol("ok"))
        return pogo.bounce(analyzedValueBody, env, c)
    return analyzed
    

def analyzeDefinition(exp):
    defName = expressions.definitionVariable(exp)
    analyzedDefValue = analyze(expressions.definitionValue(exp))
    def analyzed(env, cont):
        def c(defVal):
            environment.defineVariable(defName, defVal, env)
            return pogo.bounce(cont, Symbol("ok"))
        return pogo.bounce(analyzedDefValue, env, c)
    return analyzed


def analyzeIf(exp):
    analyzedPredicate = analyze(expressions.ifPredicate(exp))
    analyzedConsequent = analyze(expressions.ifConsequent(exp))
    analyzedAlternative = analyze(expressions.ifAlternative(exp))
    def analyzed(env, cont):
        def c(predicateVal):
            if expressions.isTrue(predicateVal):
                return pogo.bounce(analyzedConsequent, env, cont)
            else:
                return pogo.bounce(analyzedAlternative, env, cont)
        return pogo.bounce(analyzedPredicate, env, c)
    return analyzed



def analyzeSequence(exps):
    def sequentially(analyzedFirst, analyzedSecond):
        def c(env, cont):
            def c_first_exec(ignoredVal):
                return pogo.bounce(analyzedSecond, env, cont)
            return pogo.bounce(analyzedFirst, env, c_first_exec)
        return c
    if pair.isNull(exps):
        raise SchemeError, "Empty sequence -- ANALYZE"

    analyzedSeqs = analyze(expressions.firstExp(exps))
    exps = expressions.restExps(exps)
    while not pair.isNull(exps):
        analyzedSeqs = sequentially(analyzedSeqs,
                                    analyze(expressions.firstExp(exps)))
        exps = expressions.restExps(exps)
    return analyzedSeqs



def analyzeLambda(exp):
    params = expressions.lambdaParameters(exp)
    analyzedBody = analyzeSequence(expressions.lambdaBody(exp))
    def analyzed(env, cont):
        return pogo.bounce(cont,
                           expressions.makeProcedure(params,
                                                     analyzedBody,
                                                     env))
    return analyzed


def analyzeBegin(exp):
    analyzedActions = analyzeSequence(expressions.beginActions(exp))
    return analyzedActions



def analyzeApplication(exp):
    analyzedOperator = analyze(expressions.operator(exp))
    analyzedOperands = analyzeOperands(expressions.operands(exp))

    def analyzed(env, cont):
        def c_operator_exec(operatorVal):
            def c_operands_exec(operandVals):
                return pogo.bounce(apply, operatorVal, operandVals, env, cont)
            return pogo.bounce(analyzedOperands, env, c_operands_exec)
        return pogo.bounce(analyzedOperator, env, c_operator_exec)
    return analyzed



def analyzeOperands(operands):
    analyzedOperands = pair.listMap(analyze, operands)
    ## Simple case: if no operands, return something that just
    ## passes NIL to its continuation
    def analyzed(env, cont):
        return execRands(analyzedOperands, env, cont)
    return analyzed


def execRands(rands, env, cont):
    """Executes each operand and constructs a new list."""
    def eval_first_cont(headVal):
        def eval_rest_cont(tailVal):
            return pogo.bounce(cont, pair.cons(headVal, tailVal))
        return execRands(expressions.restOperands(rands), env, eval_rest_cont)
    if pair.isNull(rands):
        return pogo.bounce(cont, pair.NIL)
    return texec(expressions.firstOperand(rands),
                 env, eval_first_cont)



def eval(exp, env):
    """This version of eval calls analyze, and then texec()s it
    against the environment."""
    analyzedExp = analyze(exp)
    return pogo.pogo(texec(analyzedExp, env, pogo.land))


def texec(analyzedExp, env, cont):
    """texec applies the analyzedExpression against the environment.
    Trampolined by eval(), and will be used by primitives like EVAL
    and CALL/CC."""
    return analyzedExp(env, cont)



def apply(procedure, arguments, env, cont):
    """Applies a procedure on a list of arguments."""
    if expressions.isPrimitiveProcedure(procedure):
        return applyPrimitiveProcedure(procedure, arguments, env, cont)
    elif expressions.isContinuationProcedure(procedure):
        return applyContinuationProcedure(procedure, arguments)
    elif expressions.isCompoundProcedure(procedure):
        newEnv = environment.extendEnvironment (
            expressions.procedureParameters(procedure),
            arguments,
            expressions.procedureEnvironment(procedure))
        return texec(expressions.procedureBody(procedure), newEnv, cont)
    raise SchemeError, "Unknown procedure type -- apply " + str(procedure)



def applyPrimitiveProcedure(proc, args, env, cont):
    try:
        return applyInUnderlyingPython(
            expressions.primitiveImplementation(proc),
            [cont, env, pair.toPythonList(args)])
    except Exception, e:
        if isinstance(e, exceptions.SystemExit): raise e
##        traceback.print_exc(e)
        raise SchemeError, e



def applyContinuationProcedure(proc, args):
    try:
        return applyInUnderlyingPython(
            expressions.continuationImplementation(proc),
            pair.toPythonList(args))
    except Exception, e:
        if isinstance(e, exceptions.SystemExit): raise e
        raise SchemeError, e
