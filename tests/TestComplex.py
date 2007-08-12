
import sys
sys.path.append('..')

from schemepy.guile import guile
Inter = guile.Inter

import py.test

class TestComplex(object):
	def eval_test(self, s, value):
		"""
		Checks that the eval returns long for large integers.
		"""
		m1 = Inter()
		a = m1.eval(s)

		assert a.type() == complex
		assert a.topython() == value

	def passthru_test(self, s, value):
		m1 = Inter()
		scm = m1.to_scheme(value)

		# Check the type is correct
		assert scm.type() == complex
		# Check we can convert back
		assert scm.topython() == value

	def test_complexs(self):
		complexs = {
			'3.2+4i' : complex(3.2, 4),
			'3+4i'   : complex(3, 4),
			# FIXME: A zero for imaginary is kind of undefined...
			'0+0i'   : complex(0, 0),
			'1.0+0i' : complex(1.0, 0),
		}
		for s, value in complexs.items():
			yield self.eval_test, s, value
			yield self.passthru_test, s, value

