import py.test

import common

class TestSymbol(object):
    def eval_test(self, s, value):
        print 'eval', s, value

        m1 = common.VM()
        a = m1.eval(common.compile(s))

        assert a.type() == common.types.Symbol
        # should be `is'
        assert a.fromscheme() is value
        
    def passthru_test(self, value):
        m1 = common.VM()

        scm = m1.toscheme(value)

        # Check the type is correct
        assert scm.type() == common.types.Symbol
        # Check we can convert back, should be `is'
        assert scm.fromscheme() is value

    def test_symbol(self):
        for value in [common.types.Symbol.intern(""),
                      common.types.Symbol.intern("symbol"),
                      common.types.Symbol.intern("#{--->!---<}#")]:
            yield self.eval_test, ("(string->symbol \"%s\")" % value), value
            yield self.passthru_test, value
