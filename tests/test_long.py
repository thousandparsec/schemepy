
import common
setup_module = common.setup_module

import py.test

class TestLong(object):
	def eval_test(self, value):
		"""
		Checks that the eval returns long for large integers.
		"""
		print "eval", str(value)

		m1 = common.VM()
		a = m1.eval(str(value))

		assert a.type() == long
		assert a.fromscheme() == value

	def passthru_test(self, value):
		print "passthru", repr(value)

		m1 = common.VM()
		scm = m1.toscheme(value)
	
		assert scm.type() == long
		assert scm.fromscheme() == value

	def test_longs(self):
		longs = [2**31+1, 2**31+200, 2**63-1]
		for value in longs:
			yield self.eval_test, value
			yield self.passthru_test, value
