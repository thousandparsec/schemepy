
import py.test

import common
setup_module = common.setup_module

class TestBool(object):
	def test_eval_true(self):
		"""
		Checks that the eval returns true '#t'.
		"""
		m1 = common.VM()
		a = m1.eval(common.compile('#t'))

		assert a.type() == bool
		assert a.fromscheme() is True

	def test_eval_false(self):
		m1 = common.VM()
		a = m1.eval(common.compile('#f'))

		assert a.type() == bool
		assert a.fromscheme() is False

	def passthru_test(self, value):
		m1 = common.VM()

		scm = m1.toscheme(value)

		# Check the type is correct
		assert scm.type() == bool
		# Check we can convert back
		assert scm.fromscheme() is value

	def test_passthru(self):
		for value in [True, False]:
			yield self.passthru_test, value

