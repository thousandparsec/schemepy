
import sys
sys.path.append('..')

from schemepy.guile import guile
Inter = guile.Inter

import py.test
	
class TestFloat(object):
	def eval_test(self, s, value):
		"""
		Checks that the eval returns long for large integers.
		"""
		print 'eval', s, value

		m1 = Inter()
		a = m1.eval(s)

		assert a.type() == float
		assert a.topython() == value

	def passthru_test(self, s, value):
		print "passthru", repr(value)

		m1 = Inter()
		scm = m1.to_scheme(value)
	
		assert scm.type() == float
		assert scm.topython() == value

	def test_floats(self):
		floats = {
			'1.0':1.0, 
			'0.0':0.0, 
			# These don't seem to be portable :/
			'`+inf.0':float('inf'), 
			'`-inf.0':float('-inf'), 
			'`+nan.0':float('NaN')}

		for s, value in floats.items():
			yield self.eval_test, s, value
			yield self.passthru_test, s, value
