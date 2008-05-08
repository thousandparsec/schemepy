
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

		assert m1.type(a) == bool
		assert m1.fromscheme(a) is True

	def test_eval_false(self):
		m1 = common.VM()
		a = m1.eval(common.compile('#f'))

		assert m1.type(a) == bool
		assert m1.fromscheme(a) is False

	def passthru_test(self, value):
		m1 = common.VM()

		scm = m1.toscheme(value)

		# Check the type is correct
		assert m1.type(scm) == bool
		# Check we can convert back
		assert m1.fromscheme(scm) is value

	def test_passthru(self):
		for value in [True, False]:
			yield self.passthru_test, value

