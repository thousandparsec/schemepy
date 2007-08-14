
import py.test

import common
setup_module = common.setup_module

class TestBool(object):
	def test_eval_true(self):
		"""
		Checks that the eval returns true '#t'.
		"""
		m1 = common.Inter()
		a = m1.eval('#t')

		assert a.type() == bool
		assert a.topython() is True

	def test_eval_false(self):
		m1 = common.Inter()
		a = m1.eval('#f')

		assert a.type() == bool
		assert a.topython() is False

	def passthru_test(self, value):
		m1 = common.Inter()

		scm = m1.to_scheme(value)

		# Check the type is correct
		assert scm.type() == bool
		# Check we can convert back
		assert scm.topython() is value

	def test_passthru(self):
		for value in [True, False]:
			yield self.passthru_test, value

