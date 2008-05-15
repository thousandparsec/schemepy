"""This file test the conversion of a Python normal object to a
Scheme value and back."""

import common

class Foo(object):
    pass

class TestPyObject(object):
    def check_passthru(self, obj):
        m1 = common.VM()
        scm = m1.toscheme(obj)

        assert m1.type(scm) == object
        # should be 'is'
        assert m1.fromscheme(scm) is obj

    def test_passthru(self):
        for obj in [Foo(), Foo(), self]:
            yield self.check_passthru, obj
