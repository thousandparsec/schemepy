"""This file test the exception handling mechanism of Schemepy."""

import common
from nose.tools import raises
SchemeError = common.exceptions.SchemeError

class TestExceptions(object):

	@raises(SchemeError)
	def test_crap(self):
		"""
		Checks the interprator doesn't dies properly on crap...
		"""

		m1 = common.VM()
		m1.eval(m1.compile('foobar'))
		assert False, "Never reach here"


