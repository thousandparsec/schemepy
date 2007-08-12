#!/usr/bin/env python

"""A translation of a Scheme interpreter in Python, modeling the
metacircular evaluator in Ch. 4 of The Structure and Interpretation of
Computer Programs.  (http://www-mitpress.mit.edu/sicp/)

AUTHOR:

    Danny Yoo (dyoo@hkn.eecs.berkeley.edu)

SYNOPSIS:

    It's Scheme.  *grin*  At least, quite a bit of Scheme.

    Scheme is a variant of Lisp, and it's used in many introductory CS
    courses.  It is pretty powerful despite its deceptive size.  For
    more information on Scheme, visit the Scheme home page:

        http://www.swiss.ai.mit.edu/projects/scheme


OLD BUGS:

    One major deficiency of this implementation had in the past was
    the lack of tail call elimination.  However, I've gotten this to
    work by using trampolined style.  This involved rewriting the
    interpreter into CPS form, and trampolining the resulting tail
    calls.  The resulting interpreter looks quite a bit uglier, but at
    least it shouldn't stack overflow easily.

BUGS:

    Not all of R5RS is implemented, and probably will never be until I
    finish reading and understanding it.


MISCELLANEOUS:

    This source code is for the public domain; I'm writing it just for
    the fun of it.  This is certainly not meant to be efficient or
    even useful.  *grin*

    My future goals is to make this usable enough to run something
    like the explicit-register simulator and compiler in SICP Ch. 5.
    I'm learning more about the advanced features in scheme
    (continuations, hygenic macros), so I'll probably use this as a
    future testbed to make sure I understand those ideas.
"""

__license__ = "MIT License"


import sys
import optparse
import symbol
import parser
import evaluator
import builtins
import analyzer
import prompt
import error
import expressions
import environment
import pogo
import pair
import expander

######################################################################


class Interpreter:
    """Meant to be subclassed.
    Subclasses should define _eval and _env in their constructors.

    _eval should be a callable that takes an expression and
    environment, and returns a value.

    _env should be an environment.

    """

    def __init__(self):
        self._eval = None
        self._env = None
        self._expander = expander.Expander()
        expander.install_core_handlers(self._expander)


    def eval(self, exp):
        """Evaluates an expression exp."""
        return self.get_evaluator()(self.get_expander().expand(exp),
                                    self.get_environment())


    def install_function(self, name, function):
        """Installs a Python function into the toplevel environment."""
        builtins.installPythonFunction(name, function, self.get_environment())


    def repl(self):
        """A thin method around the repl function."""
        return repl(self)

        
    def get_evaluator(self):
        """Returns the evaluation function."""
        return self._eval


    def get_environment(self):
        """Returns the toplevel environment frame."""
        return self._env

    def get_expander(self):
        """Returns the syntax expander."""
        return self._expander


    def install_special_builtins(self):
        """Adds some unusual builtin cases that involve the interpreter
        itself."""
        for (name, function) in self.get_special_builtins():
            builtins.installPythonFunction(name,
                                           function,
                                           self.get_environment(),
                                           wrapDefaults=False)

    def get_special_builtins(self):
        """Returns a list of 2-tuples: name of the special builtin, and
        the function value of the builtin."""
        return ()





class RegularInterpreter(Interpreter):
    """This interpreter evaluates expressions in a way similar to
    the metacircular evaluator described by SICP.  The only significant
    difference is the internal use of trampolining style plus CPS."""
    def __init__(self):
        Interpreter.__init__(self)
        self._eval = evaluator.eval
        self._env = builtins.setupEnvironment()
        self.install_special_builtins()


    def get_special_builtins(self):
        return (('load', self.schemeLoad),
                ('call/cc', self.schemeCallcc),
                ('call-with-current-continuation', self.schemeCallcc),
                ('eval', self.schemeEval),
                ('apply', self.schemeApply),
                ('dir', self.schemeDir))


    def schemeDir(self, cont, env, args):
        """A quick function to inspect the first frame."""
        if len(args) != 0:
            raise TypeError, ("dir expected at most 0 arguments, got %s" % len(args))
        names = environment.firstFrame(env).keys()
        names.sort()
        return pogo.bounce(cont, pair.list(*names))


    def schemeLoad(self, cont, env, args):
        """Special primitive: implements LOAD."""
        symbolicFilename = str(args[0])
        try:
            f = open(symbolicFilename)
            try:
                text = "(begin \n%s\n 'ok)" % f.read()
            finally:
                f.close()
            expandedExp = self.get_expander().expand(parser.parse(text))
            return evaluator.teval(expandedExp, env, cont)
        except IOError, e:
            raise error.SchemeError, "LOAD error -- %s" % str(e)
        except TypeError, e:
            raise error.SchemeError, "LOAD error -- argument must be a string"


    def schemeApply(self, cont, env, args):
        return evaluator.apply(args[0], args[1], env, cont)


    def schemeEval(self, cont, env, args):
        expandedExp = self.get_expander().expand(args[0])
        return evaluator.teval(expandedExp, env, cont)


    def schemeCallcc(self, cont, env, args):
        lambdaBody = args[0]
        def c2(val):
            return pogo.bounce(cont, val)
        cont_procedure = expressions.makeContinuationProcedure(c2)
        return evaluator.apply(lambdaBody, pair.list(cont_procedure),
                               env, cont)



######################################################################



class AnalyzingInterpreter(Interpreter):
    """This version of the interpreter will do syntax analysis on its
    expressions before it executes them.  Should be a win on speed."""
    def __init__(self):
        Interpreter.__init__(self)
        self._eval = analyzer.eval
        self._env = builtins.setupEnvironment()                       
        self.install_special_builtins()


    def get_special_builtins(self):
        return ( ('load', self.schemeLoad),
                 ('dir', self.schemeDir),
                 ('call-with-current-continuation', self.schemeCallcc),
                 ('call/cc', self.schemeCallcc),
                 ('apply', self.schemeApply),
                 ('eval', self.schemeEval),
                 )

    def schemeDir(self, cont, env, args):
        """A quick function to inspect the first frame."""
        if len(args) != 0:
            raise TypeError, ("dir expected at most 0 arguments, got %s" % len(args))
        names = environment.firstFrame(env).keys()
        names.sort()
        return pogo.bounce(cont, pair.list(*names))


    def schemeLoad(self, cont, env, args):
        """Special primitive: implements LOAD."""
        symbolicFilename = str(args[0])
        try:
            f = open(symbolicFilename)
            try:
                text = "(begin \n%s\n 'ok)" % f.read()
            finally:
                f.close()
            expandedExp = self.get_expander().expand(parser.parse(text))
            analyzedExp = analyzer.analyze(expandedExp)
            return analyzer.texec(analyzedExp, env, cont)
        except IOError, e:
            raise error.SchemeError, "LOAD error -- %s" % str(e)
        except TypeError, e:
            raise error.SchemeError, "LOAD error -- argument must be a string"


    def schemeApply(self, cont, env, args):
        return analyzer.apply(args[0],
                              args[1],
                              env, cont)


    def schemeEval(self, cont, env, args):
        expandedExp = self.get_expander().expand(args[0])
        analyzedExp = analyzer.analyze(expandedExp)
        return analyzer.texec(analyzedExp, env, cont)


    def schemeCallcc(self, cont, env, args):
        analyzedLambdaBody = args[0]
        def c2(val):
            return pogo.bounce(cont, val)
        cont_procedure = expressions.makeContinuationProcedure(c2)
        return analyzer.apply(analyzedLambdaBody,
                              pair.list(cont_procedure),
                              env,
                              cont)



######################################################################


class MinimalInterpreter(Interpreter):
    """
    This is just a really minimal interpreter that supports only the
    core forms.  No builtins, no expander, nothing except the
    following:

        self evaluating expressions
        variable references
        QUOTE
        SET!
        DEFINE
        IF
        LAMBDA
        BEGIN
        function application
    
    Furthermore, each evaluation generates a whole new environment, so
    no state should be saved between calls to eval.

    This is a demonstration of a restricted Scheme.

    In the future, we may even want to modify EVAL so that it goes
    through a version of pogo.pogo that bounds the number of bounces
    allowed before getting an answer.  So we can do some interesting
    things here...
    """

    def __init__(self):
        Interpreter.__init__(self)

    def get_evaluator(self):
        return analyzer.eval

    def get_environment(self):
        return environment.extendEnvironment(pair.list(),
                                             pair.list(),
                                             environment.THE_EMPTY_ENVIRONMENT)
    def get_expander(self):
        class SillyExpander:
            def expand(self, expr): return expr
        return SillyExpander()



######################################################################


def repl(interp=AnalyzingInterpreter()):
    """A fairly standard 'read->eval->print' loop."""
    print 'Welcome to PyScheme!  Type: (QUIT) to quit.\n'
    def promptCallback(s):
        try:
            print expressions.toString(interp.eval(parser.parse(s)))
        except (error.SchemeError, parser.ParserError), e:
            print "ERROR (%s): %s" % (e.__class__, e)

    p = prompt.Prompt(name="PyScheme", callback=promptCallback,
                      quit_str=None)
    try:
        p.promptLoop()
    except SystemExit:
        pass ## Get out smoothly.
            

def isNonInteractive(args):
    """Returns True if we want to run in non-interactive mode."""
    return len(args) >= 1

def runNonInteractive(interp, args):
    """Executes the interpreter on args[0]."""
    interp.eval(pair.list(symbol.Symbol("load"),
                                args[0]))


def chooseInterpreter(options):
    """Choose which interpreter we should use."""
    if options.interpreter_type == 'regular':
        return RegularInterpreter()
    else:
        return AnalyzingInterpreter()


def configureOptionParser():
    optparser = optparse.OptionParser()
    optparser.add_option("--regular",
                      help="invoke regular interpreter",
                      action="store_const",
                      const="regular",
                      dest="interpreter_type",
                      )
    optparser.add_option("--analyzer",
                      help="invoke analyzing interpreter [default]",
                      action="store_const",
                      const="analyzer",
                      dest="interpreter_type",
                      )
    return optparser


def main():
    """Main driver."""
    optparser = configureOptionParser()
    options, args = optparser.parse_args()
    interp = chooseInterpreter(options)

    if isNonInteractive(args):
        runNonInteractive(interp, args)
    else:
        repl(interp)



if __name__ == '__main__':
    main()
