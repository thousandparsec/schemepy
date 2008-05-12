import common

class TestMultiVM(object):
    def test_multi_vm(self):
        """
        Check scope of one VM don't affect another's
        """
        m1 = common.VM()
        m2 = common.VM()

        m1.define("foo", m1.toscheme(1))
        m2.define("foo", m2.toscheme(2))
        m2.define("bar", m2.toscheme("bar"))

        assert m1.fromscheme(m1.get("foo")) == 1
        assert m2.fromscheme(m2.get("foo")) == 2

        assert m2.fromscheme(m2.get("bar")) == "bar"
        assert m1.get("bar", default="bar-default") == "bar-default"
