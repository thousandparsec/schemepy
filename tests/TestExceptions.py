
import sys
sys.path.append('..')

from schemepy.guile import guile
Inter = guile.Inter

import py.test

class TestExceptions(object):

	def test_crap(self):
		"""
		Checks the interprator doesn't dies properly on crap...
		"""

		m1 = Inter()
		py.test.raises(Exception, m1.eval, 'asdasf')


