
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

		assert m1.type(a) in (int, long)
		assert m1.fromscheme(a) == value

	def passthru_test(self, value):
		print "passthru", repr(value)

		m1 = common.VM()
		scm = m1.toscheme(value)
	
		assert m1.type(scm) in (int, long)
		assert m1.fromscheme(scm) == value

	def test_ints(self):
		ints = [1, 5, 1000, int(2**31-1), int(-2**31)]
		for value in ints:
			yield self.eval_test, value
			yield self.passthru_test, value
