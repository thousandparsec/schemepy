import py.test

import common

class TestLambda(object):
    """Lambda in Scheme should be callable in Python."""
    def call_in_python(self, code, cases):
        m1 = common.VM()
        lam = m1.eval(common.compile(s))

        assert type(lam) is common.types.Lambda

        func = lam.fromscheme()
        for case in cases:
            result = case[0]
            args = case[1:]
            assert func(*args).fromscheme() == result

    def call_in_scheme(self, code, cases):
        m1 = common.VM()
        lam = m1.eval(common.compile(s))

        for case in cases:
            result = case[0]
            args = [m1.toscheme(arg) for arg in case[1:]]
            rlt = m1.apply(lam, args)
            assert rlt.fromscheme() == result

    def test_lambda(self):
        tests = [("(lambda (x) (* x x))", [[1, 1],
                                           [4, 2]]),
                 ("""(let ((v 0))
                       (lambda (x)
                         (set! v (+ x v))
                         v))""", [[1, 1],
                                  [1, 2],
                                  [4, 6]])]
        for test in tests:
            yield self.call_in_python, test[0], test[1]
            yield self.call_in_scheme, test[0], test[1]
