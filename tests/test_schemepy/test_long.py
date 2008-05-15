"""This file test the conversion between Scheme big integer and Python big integer."""

import common

class TestLong(object):
	def check_eval(self, value):
		"""
		Checks that the eval returns long for large integers.
		"""
		print "eval", str(value)

		m1 = common.VM()
		a = m1.eval(m1.compile(str(value)))

		assert m1.type(a) == long
		assert m1.fromscheme(a) == value
		assert type(m1.fromscheme(a)) in (int, long)
		
	def check_passthru(self, value):
		print "passthru", repr(value)

		m1 = common.VM()
		scm = m1.toscheme(value)
	
		assert m1.type(scm) == long
		assert m1.fromscheme(scm) == value
		assert type(m1.fromscheme(scm)) in (int, long)
		
	def test_longs(self):
		longs = [2**31+1, 2**31+200, 2**63-1]
		for value in longs:
			yield self.check_eval, value
			yield self.check_passthru, value
