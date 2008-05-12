import common

Symbol = common.types.Symbol

class TestSymbol(object):
    def check_eval(self, s, value):
        print 'eval', s, value

        m1 = common.VM()
        a = m1.eval(s)

        assert m1.type(a) is Symbol
        # should be `is'
        assert m1.fromscheme(a) is value
        
    def check_passthru(self, value):
        m1 = common.VM()

        scm = m1.toscheme(value)

        # Check the type is correct
        assert m1.type(scm) is Symbol
        # Check we can convert back, should be `is'
        assert m1.fromscheme(scm) is value

    def test_symbol(self):
        for value in [Symbol.intern(""),
                      Symbol.intern("symbol"),
                      Symbol.intern("#{--->!---<}#")]:
            yield self.check_eval, ("(string->symbol \"%s\")" % value.name), value
            yield self.check_passthru, value
