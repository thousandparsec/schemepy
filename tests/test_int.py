
import common
setup_module = common.setup_module

import py.test

class TestInt(object):
	def eval_test(self, value):
		"""
		Checks that the eval returns int for small integers.
		"""
		print "eval", str(value)

		m1 = common.Inter()
		a = m1.eval(str(value))

		assert a.type() == int
		assert a.topython() == value

	def passthru_test(self, value):
		print "passthru", repr(value)

		m1 = common.Inter()
		scm = m1.to_scheme(value)
	
		assert scm.type() == int
		assert scm.topython() == value

	def test_ints(self):
		ints = [1, 5, 1000, int(2**31-1), int(-2**31)]
		for value in ints:
			yield self.eval_test, value
			yield self.passthru_test, value
