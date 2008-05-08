
import common
setup_module = common.setup_module

import py.test

class TestComplex(object):
	def eval_test(self, s, value):
		"""
		Checks that the eval returns long for large integers.
		"""
		print 'eval', s, value

		m1 = common.VM()
		a = m1.eval(common.compile(s))

		assert m1.type(a) == complex
		assert m1.fromscheme(a) == value

	def passthru_test(self, s, value):
		print 'passthru', value		

		m1 = common.VM()
		scm = m1.toscheme(value)

		# Check the type is correct
		assert m1.type(scm) == complex
		# Check we can convert back
		assert m1.fromscheme(scm) == value

	def test_complexs(self):
		complexs = {
			# Complex with zero imaginary are auto converted to floats
			'3.2+4i' : complex(3.2, 4),
			'3+4i'   : complex(3, 4),
			'0+1.0i' : complex(0, 1.0),
		}
		for s, value in complexs.items():
			yield self.eval_test, s, value
			yield self.passthru_test, s, value


