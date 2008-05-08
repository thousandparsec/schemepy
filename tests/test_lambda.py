import py.test

import common
setup_module = common.setup_module

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from schemepy.types import Lambda

class TestLambda(object):
    """Lambda in Scheme should be callable in Python."""
    def call_in_python_shallow_test(self, code, cases):
        m1 = common.VM()
        lam = m1.eval(common.compile(code))

        assert lam.type() is Lambda

        func = lam.fromscheme(shallow=True)
        func.vm = m1
        for case in cases:
            result = case[0]
            args = [m1.toscheme(arg) for arg in case[1:]]
            assert func(*args).fromscheme() == result

    def call_in_python_test(self, code, cases):
        m1 = common.VM()
        lam = m1.eval(common.compile(code))

        assert lam.type() is Lambda

        func = lam.fromscheme()
        func.vm = m1
        for case in cases:
            result = case[0]
            args = case[1:]
            assert func(*args) == result

    def call_in_scheme_test(self, code, cases):
        m1 = common.VM()
        lam = m1.eval(common.compile(code))

        for case in cases:
            result = case[0]
            args = [m1.toscheme(arg) for arg in case[1:]]
            rlt = m1.apply(lam, args)
            assert rlt.fromscheme() == result

    def passthru_test(self, code, cases):
        m1 = common.VM()
        lam = m1.eval(common.compile(code))
        func = lam.fromscheme()
        lam = m1.toscheme(func)

        for case in cases:
            result = case[0]
            args = [m1.toscheme(arg) for arg in case[1:]]
            rlt = m1.apply(lam, args)
            assert rlt.fromscheme() == result

    def test_closure(self):
        code = """(let ((v 0))
                       (lambda (x)
                           (set! v (+ v x))
                         v))"""
        m1 = common.VM()
        lam = m1.eval(common.compile(code))

        func = lam.fromscheme()
        func.vm = m1
        assert func(1) == 1
        assert func(1) == 2
        assert func(1) == 3

    def test_lambda(self):
        tests = [("(lambda (x) (* x x))", [[1, 1], # Test normal lambda
                                           [4, 2]]),
                 ("+", [[10, 1, 2, 3, 4],          # Test built-in procedure
                        [0, -10, 10]])]

        for test in tests:
            yield self.call_in_python_test, test[0], test[1]
            yield self.call_in_scheme_test, test[0], test[1]
            yield self.call_in_python_shallow_test, test[0], test[1]
            yield self.passthru_test, test[0], test[1]