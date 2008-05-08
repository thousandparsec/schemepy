import py.test

import common
setup_module = common.setup_module

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from schemepy.types import Symbol

class TestSymbol(object):
    def eval_test(self, s, value):
        print 'eval', s, value

        m1 = common.VM()
        a = m1.eval(common.compile(s))

        assert m1.type(a) is Symbol
        # should be `is'
        assert m1.fromscheme(a) is value
        
    def passthru_test(self, value):
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
            yield self.eval_test, ("(string->symbol \"%s\")" % value.name), value
            yield self.passthru_test, value
