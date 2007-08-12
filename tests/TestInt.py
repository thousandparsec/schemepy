
import sys
sys.path.append('..')

from schemepy.guile import guile
Inter = guile.Inter

import py.test

def asset(a):
	if not a:
		raise SyntaxError('Error!')

class TestInt(object):
	def eval_test(self, value):
		"""
		Checks that the eval returns int for small integers.
		"""
		m1 = Inter()
		a = m1.eval(str(value))

		assert a.type() == int
		assert a.topython() == value

	def passthru_test(self, value):
		m1 = Inter()
		scm = m1.to_scheme(value)
	
		assert scm.type() == int
		assert scm.topython() == value

	def test_ints(self):
		ints = [1, 5, 1000, 2**31-1]
		for value in ints:
			yield self.eval_test, value
			yield self.passthru_test, value
