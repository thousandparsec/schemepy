
import common
setup_module = common.setup_module

import py.test
	
class TestFloat(object):
	def eval_test(self, s, value):
		"""
		Checks that the eval returns long for large integers.
		"""
		print 'eval', s, value

		m1 = common.VM()
		a = m1.eval(common.compile(s))

		assert m1.type(a) == float
		assert m1.fromscheme(a) == value

	def passthru_test(self, s, value):
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
			# These don't seem to be portable :/
			'+inf.0':float('inf'), 
			'-inf.0':float('-inf'), 
		}

		for s, value in floats.items():
			yield self.eval_test, s, value
			yield self.passthru_test, s, value


