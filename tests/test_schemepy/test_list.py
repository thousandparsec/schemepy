"""This file test the conversion between Scheme list and Python list."""

import common

class TestList(object):
	def check_eval(self, s, value):
		"""
		"""
		print 'eval', s, value

		m1 = common.VM()
		a = m1.eval(m1.compile(s))

		assert m1.type(a) == list
		assert m1.fromscheme(a) == value

	def check_passthru(self, s, value):
		print "passthru", repr(value)

		m1 = common.VM()
		scm = m1.toscheme(value)
	
		assert m1.type(scm) == list
		assert m1.fromscheme(scm) == value

	def test_empty_list(self):
		m1 = common.VM()
		a = m1.eval(m1.compile("'()"))
		# eol might not be a list
		# assert m1.type(a) == list
		assert m1.fromscheme(a) == m1.eol

		scm = m1.toscheme(m1.eol)
		# assert m1.type(scm) == list
		assert m1.fromscheme(scm) == m1.eol

	def test_list(self):
		"""
		Checks that the eval works for various lists.
		"""
                lists = { \
                        "'(1 2 3)"          : [1, 2, 3],                # Simple list with integers
                        "'(1.0 2.0 3.0)"    : [1.0, 2.0, 3.0],          # Simple list with floats
                       """'("a" "aa" "aaa")""" : ['a', 'aa', 'aaa'],    # Simple list with strings
                       """'(1 1.0 "a")"""      : [1, 1.0, 'a'],         # List with a simpled mixed list
                }
		for s, value in lists.items():
			yield self.check_eval, s, value
			yield self.check_passthru, s, value
