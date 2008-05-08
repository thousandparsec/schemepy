import py.test

import common
setup_module = common.setup_module

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from schemepy.types import Cons


class TestCons(object):
    def eval_test(self, s, value):
        print 'eval', s, value

        m1 = common.VM()
        a = m1.eval(common.compile(s))

        assert m1.type(a) is Cons

        assert m1.fromscheme(a) == value

    def passthru_test(self, value):
        m1 = common.VM()

        scm = m1.toscheme(value)

        assert m1.type(scm) is Cons
        assert m1.fromscheme(scm) == value

    def test_list(self):
        m1 = common.VM()

        l = Cons(1, [])
        scm = m1.toscheme(l)

        assert m1.type(scm) == list
        assert m1.fromscheme(scm) == [1]

    def test_cons(self):
        for value, code in [(Cons(1, 2), "`(1 . 2)"),
                            (Cons("foo", "bar"), '`("foo" . "bar")')]:
            yield self.eval_test, code, value
            yield self.passthru_test, value
