"""This file test the conversion between Python string/unicode and
Scheme string."""

import common

class TestString(object):
	def check_eval(self, value):
		print "eval", repr(value)

		m1 = common.VM()
		a = m1.eval(m1.compile('"%s"' % value))

		assert m1.type(a) in (str, unicode)
		assert m1.fromscheme(a) == value

	def check_passthru(self, value):
		print "passthru", repr(value)

		m1 = common.VM()
		scm = m1.toscheme(value)
	
		assert m1.type(scm) in (str, unicode)
		assert m1.fromscheme(scm) == value

	def test_string(self):
		"""
		Checks that the eval returns strings for various input.
		"""
		strings = [ \
			 "", "abc", "t\n\t\n\r",  "a\0\0tl;\0a",
			u"", u"abc", u"t\n\t\n\r", u"a\0\0tl;\0a",
		]
		for value in strings:
			yield self.check_eval, value
			yield self.check_passthru, value
