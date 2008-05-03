
import common
setup_module = common.setup_module

import py.test

class TestExceptions(object):

	def test_crap(self):
		"""
		Checks the interprator doesn't dies properly on crap...
		"""

		m1 = common.VM()
		py.test.raises(Exception, m1.eval, 'asdasf')


