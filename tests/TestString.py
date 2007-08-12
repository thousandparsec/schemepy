
import sys
sys.path.append('..')

from schemepy.guile import guile
Inter = guile.Inter

import py.test

class TestString(object):
	def string_test(self, value):
		m1 = Inter()
		a = m1.eval(repr(value)[1:-1])

		assert isinstance(value, a.type())
		assert a.topython() == value

	def passthru_test(self, value):
		m1 = Inter()
		scm = m1.to_scheme(value)
	
		assert scm.type() == str
		assert scm.topython() == value

	def test_string(self):
		"""
		Checks that the eval returns strings for various input.
		"""
		strings = [ \
			 "", u"abc", u"t\n\t\n\r",  "a\0\0tl;\0a",
			u"", u"abc", u"t\n\t\n\r", u"a\0\0tl;\0a",
		]
		for value in strings:
			yield self.eval_test, value
			yield self.passthru_test, value
