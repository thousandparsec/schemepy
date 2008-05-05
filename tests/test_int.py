
import common
setup_module = common.setup_module

import py.test

class TestInt(object):
	def eval_test(self, value):
		"""
		Checks that the eval returns int for small integers.
		"""
		print "eval", str(value)

		m1 = common.VM()
		a = m1.eval(common.compile(str(value)))

		assert a.type() in (int, long)
		assert a.fromscheme() == value

	def passthru_test(self, value):
		print "passthru", repr(value)

		m1 = common.VM()
		scm = m1.toscheme(value)
	
		assert scm.type() in (int, long)
		assert scm.fromscheme() == value

	def test_ints(self):
		ints = [1, 5, 1000, int(2**31-1), int(-2**31)]
		for value in ints:
			yield self.eval_test, value
			yield self.passthru_test, value
