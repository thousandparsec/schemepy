"""This file test the conversion between Python schemepy.types.Cons
and Scheme cons pair."""

import common

Cons = common.types.Cons

class TestCons(object):
    def check_eval(self, s, value):
        print 'eval', s, value

        m1 = common.VM()
        a = m1.eval(m1.compile(s))

        assert m1.type(a) is Cons

        assert m1.fromscheme(a) == value

    def check_passthru(self, value):
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
            yield self.check_eval, code, value
            yield self.check_passthru, value
