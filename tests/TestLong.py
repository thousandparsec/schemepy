
import sys
sys.path.append('..')

from schemepy.guile import guile
Inter = guile.Inter

import py.test

class TestLong(object):
	def eval_test(self, value):
		"""
		Checks that the eval returns long for large integers.
		"""
		print "eval", str(value)

		m1 = Inter()
		a = m1.eval(str(value))

		assert a.type() == long
		assert a.topython() == value

	def passthru_test(self, value):
		print "passthru", repr(value)

		m1 = Inter()
		scm = m1.to_scheme(value)
	
		assert scm.type() == long
		assert scm.topython() == value

	def test_longs(self):
		longs = [2**31+1, 2**31+200, 2**63-1]
		for value in longs:
			yield self.eval_test, value
			yield self.passthru_test, value
