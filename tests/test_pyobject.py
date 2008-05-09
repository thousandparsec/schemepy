import py.test

import common
setup_module = common.setup_module

class Foo(object):
    pass

class TestPyObject(object):
    def passthru_test(self, obj):
        m1 = common.VM()
        scm = m1.toscheme(obj)

        assert m1.type(scm) == object
        # should be 'is'
        assert m1.fromscheme(scm) is obj

    def test_passthru(self):
        for obj in [Foo(), Foo, self]:
            yield self.passthru_test, obj
