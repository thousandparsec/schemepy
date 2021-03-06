"""This file test the float number handling of Scheme and conversion
between Python float number."""

import common
	
class TestFloat(object):
	def check_eval(self, s, value):
		"""
		Checks that the eval returns long for large integers.
		"""
		print 'eval', s, value

		m1 = common.VM()
		a = m1.eval(m1.compile(s))

		assert m1.type(a) == float
		assert m1.fromscheme(a) == value

	def check_passthru(self, s, value):
		print "passthru", repr(value)

		m1 = common.VM()
		scm = m1.toscheme(value)
	
		assert m1.type(scm) == float
		assert m1.fromscheme(scm) == value

	def test_passthru_nan(self):
		print "passthru_nan"

		value = float('NaN')

		m1 = common.VM()
		scm = m1.toscheme(value)
	
		assert m1.type(scm) == float
		# float('NaN') != float('NaN')
		assert str(m1.fromscheme(scm)) == str(float('NaN'))

	def test_floats(self):
		floats = {
			'1.0':1.0, 
			'0.0':0.0, 
			# Complex types with zero imaginary part should come back as floats
			'0.0+0.0i': 0.0,
			'123.0+0.0i': 123.0,
		}

		for s, value in floats.items():
			yield self.check_eval, s, value
			yield self.check_passthru, s, value


