"""This file test the conersion from a Scheme lambda/procedure and back."""

import common

Lambda = common.types.Lambda

class TestLambda(object):
    """Lambda in Scheme should be callable in Python."""
    def call_in_python_shallow(self, code, cases):
        m1 = common.VM()
        lam = m1.eval(m1.compile(code))

        assert m1.type(lam) is Lambda

        func = m1.fromscheme(lam, shallow=True)
        assert func.shallow is True
        assert func.vm is m1
        
        for case in cases:
            result = case[0]
            args = [m1.toscheme(arg) for arg in case[1:]]
            assert m1.fromscheme(func(*args)) == result

    def call_in_python(self, code, cases):
        m1 = common.VM()
        lam = m1.eval(m1.compile(code))

        assert m1.type(lam) is Lambda

        func = m1.fromscheme(lam)
        assert func.shallow is not True
        assert func.vm is m1
        
        for case in cases:
            result = case[0]
            args = case[1:]
            assert func(*args) == result

    def call_in_scheme(self, code, cases):
        m1 = common.VM()
        lam = m1.eval(m1.compile(code))

        for case in cases:
            result = case[0]
            args = [m1.toscheme(arg) for arg in case[1:]]
            rlt = m1.apply(lam, args)
            assert m1.fromscheme(rlt) == result

    def check_passthru(self, code, cases):
        m1 = common.VM()
        lam = m1.eval(m1.compile(code))
        func = m1.fromscheme(lam)
        lam = m1.toscheme(func)

        for case in cases:
            result = case[0]
            args = [m1.toscheme(arg) for arg in case[1:]]
            rlt = m1.apply(lam, args)
            assert m1.fromscheme(rlt) == result

    def test_closure(self):
        code = """(let ((v 0))
                       (lambda (x)
                           (set! v (+ v x))
                         v))"""
        m1 = common.VM()
        lam = m1.eval(m1.compile(code))

        func = m1.fromscheme(lam)
        assert func(1) == 1
        assert func(1) == 2
        assert func(1) == 3

    def test_lambda(self):
        tests = [("(lambda (x) (* x x))", [[1, 1], # Test normal lambda
                                           [4, 2]]),
                 ("(lambda (a b) (+ a a b))", [[4, 1, 2], # Test parameter passing order
                                               [8, 2, 4]]),
                 ("+", [[10, 1, 2, 3, 4],          # Test built-in procedure
                        [0, -10, 10]])]

        for test in tests:
            yield self.call_in_python, test[0], test[1]
            yield self.call_in_scheme, test[0], test[1]
            yield self.call_in_python_shallow, test[0], test[1]
            yield self.check_passthru, test[0], test[1]
