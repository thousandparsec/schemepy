import types
import re

from schemepy.exceptions import *
import schemepy.types

import scheme
import parser
import expressions
import symbol
import pair
import environment
import error
import pogo
import analyzer

class VM(object):
    """\
    The VM of pyscheme. A wrapper of pyscheme's interpreter
    and parser.
    """

    def __init__(self, profile):
        if profile == "scheme-report-environment":
            interp = scheme.AnalyzingInterpreter()
        elif profile == "null-environment":
            interp = scheme.MinimalInterpreter()
        else:
            raise ProfileNotFoundError, "No such profile %s" % profile

        self._interp = interp
        self._parse = parser.parse

    def compile(self, code):
        """Compile for pyscheme. This is in fact parsing."""
        try:
            return self._parse(code)
        except Exception, e:
            self._parse_error(e)

    def eval(self, compiled):
        try:
            return self._interp.eval(compiled)
        except Exception, e:
            self._parse_error(e)

    def repl(self):
        self._interp.repl()

    def define(self, name, value):
        """Define a variable in Scheme"""
        name = schemepy.types.Symbol(name)
        environment.defineVariable(self.toscheme(name),
                                   value,
                                   self._interp.get_environment())

    def get(self, name, default=None):
        """Get a value bound to the symbol"""
        name = schemepy.types.Symbol(name)
        try:
            val = environment.lookupVariableValue(self.toscheme(name),
                                                  self._interp.get_environment())
        except error.SchemeError:
            return default
        return val

    def apply(self, proc, args):
        """Call the scheme procedure"""
        # NOTE: This is specific to AnalyzerInterpreter (and MinimalInterpreter)
        # which we used. But RegularInterpreter should use evaluator.apply instead.
        try:
            return pogo.pogo(analyzer.apply(proc,
                                            self.toscheme(args, shallow=True),
                                            self._interp.get_environment(),
                                            pogo.land))
        except Exception, e:
            self._parse_error(e)

    def toscheme(self, val, shallow=False):
        "Convert a Python value to a Scheme value."
        if callable(val):
            val = self._wrap_python_callable(val, shallow)
            return expressions.makePrimitiveProcedure(val)
        if val is True:
            return symbol.true
        if val is False:
            return symbol.false
        if type(val) is schemepy.types.Symbol:
            return symbol.Symbol(val.name)
        if type(val) is schemepy.types.Cons:
            car = val.car
            cdr = val.cdr
            if not shallow:
                car = self.toscheme(car)
                cdr = self.toscheme(cdr)
            return pair.cons(car, cdr)
        if isinstance(val, list):
            lst = pair.NIL
            for el in reversed(val):
                if not shallow:
                    el = self.toscheme(el)
                lst = pair.cons(el, lst)
            return lst
        if isinstance(val, dict):
            lst = pair.NIL
            for key, value in val.items():
                key = self.toscheme(key)
                if not shallow:
                    value = self.toscheme(value)
                lst = pair.cons(pair.cons(key, value), lst)
            return lst
        return val

    def fromscheme(self, val, shallow=False):
        "Convert a Scheme value to a Python value."
        if expressions.isCompoundProcedure(val):
            return schemepy.types.Lambda(val, self, shallow)
        if expressions.isPrimitiveProcedure(val):
            fun = expressions.primitiveImplementation(val)
            orig = fun.__dict__.get("_orig", None)
            if orig and callable(orig):
                return orig
            return schemepy.types.Lambda(val, self, shallow)
        if symbol.isSymbol(val):
            if val == symbol.true:
                return True
            if val == symbol.false:
                return False
            return schemepy.types.Symbol(str(val))
        if pair.isNull(val):
            return []
        if isAList(val):
            dic = {}
            while not pair.isNull(val):
                el = pair.car(val)
                key = self.fromscheme(pair.car(el))
                value = pair.cdr(el)
                if not shallow:
                    value = self.fromscheme(value)
                dic[key] = value
                val = pair.cdr(val)
            return dic
        if pair.isList(val):
            lst = []
            while not pair.isNull(val):
                el = pair.car(val)
                if not shallow:
                    el = self.fromscheme(el)
                lst.append(el)
                val = pair.cdr(val)
            return lst
        if pair.isPair(val):
            car = pair.car(val)
            cdr = pair.cdr(val)
            if not shallow:
                car = self.fromscheme(car)
                cdr = self.fromscheme(cdr)
            return schemepy.types.Cons(car, cdr)
        return val

    def type(self, val):
        "Get the Python type of a Scheme value."
        if expressions.isCompoundProcedure(val):
            return schemepy.types.Lambda
        if expressions.isPrimitiveProcedure(val):
            fun = expressions.primitiveImplementation(val)
            orig = fun.__dict__.get("_orig", None)
            if orig and callable(orig):
                return types.FunctionType
            return schemepy.types.Lambda
        if symbol.isSymbol(val):
            if val == symbol.true or val == symbol.false:
                return bool
            return schemepy.types.Symbol
        if pair.isNull(val):
            return list
        if isAList(val):
            return dict
        if pair.isList(val):
            return list
        if pair.isPair(val):
            return schemepy.types.Cons
        t = type(val)
        if t not in (int, complex, float, long, str, unicode):
            return object
        return t

    def _wrap_python_callable(self, meth, shallow):
        """\
        Wrap a Python callable. Do auto-converting on the
        return value and parameters.
        """
        def wrapped(cont, env, args):
            if not shallow:
                args = [self.toscheme(arg) for arg in args]
            return pogo.bounce(cont, (meth(*args)))
        wrapped._orig = meth
        return wrapped

    def _parse_error(self, e):
        if isinstance(e, error.SchemeError):
            msg = str(e.message)
            if msg.startswith("Unbound variable"):
                raise ScmUnboundVariable(msg)
            if msg.startswith("Too many arguments supplied") or \
               msg.startswith("Too few arguments supplied") or \
               re.search('takes exactly \d+ arguments \(\d+ given\)', msg) or \
               re.search(' --- expects .* arguments', msg):
                raise ScmWrongArgNumber(msg)
            if re.search(' --- arguments must be ', msg):
                raise ScmWrongArgType(msg)
            raise ScmMiscError(msg)
        if isinstance(e, parser.ParserError):
            raise ScmSyntaxError(e.message)
        raise e
    

# Helper functions
def isAList(lst):
    """\
    Check whether the pyscheme list lst is an associate list
    """
    while not pair.isNull(lst):
        if not pair.isPair(lst):
            return False
        if not pair.isPair(pair.car(lst)):
            return False
        lst = pair.cdr(lst)
    return True

# Configuration
symbol.CASE_SENSITIVE = True
