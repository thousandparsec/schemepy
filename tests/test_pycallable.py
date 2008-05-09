import py.test
import types

import common
setup_module = common.setup_module

def for_test_add(a, b):
    return a+b

class TestPyCallable(object):
    def passthru_test(self, func):
        m1 = common.VM()
        scm = m1.toscheme(func)

        assert m1.type(scm) == types.FunctionType
        # should be 'is'
        assert m1.fromscheme(scm) is func

    def call_in_scheme(self, cases):
        m1 = common.VM()
        scm = m1.toscheme(func)

        for case in cases:
            result = case[0]
            args = [m1.toscheme(arg) for arg in case[1:]]
            assert m1.fromscheme(m1.apply(scm, args)) == result

    def test_pycallable(self):
        cases = [[2, 1, 1], [0, 10, -10], ["foobar", "foo", "bar"]]
        funcs = [for_test_add, lambda a, b: a+b]
        for case in cases:
            for func in funcs:
                self.passthru_test(func)
                self.call_in_scheme(func, cases)

    def test_shallow_conversion(self):
        m1 = common.VM()

        def add(a, b):
            result = m1.fromscheme(a) + m1.fromscheme(b)
            return m1.toscheme(result)

        func = m1.toscheme(add, shallow=True)
        assert m1.fromscheme(m1.apply(func, [m1.toscheme(1), m1.toscheme(1)])) == 2
        assert m1.fromscheme(m1.apply(func, [m1.toscheme("foo"),
                                             m1.toscheme("bar")])) == "foobar"
