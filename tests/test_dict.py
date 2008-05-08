
import common
setup_module = common.setup_module

import py.test

class TestDict(object):
	def eval_test(self, s, value):
		print 'eval', s, value

		m1 = common.VM()
		a = m1.eval(s)

		assert m1.type(a) == dict
		assert m1.fromscheme(a) == value

	def passthru_test(self, s, value):
		print "passthru", repr(value)

		m1 = common.VM()
		scm = m1.toscheme(value)
	
		assert m1.type(scm) == dict
		assert m1.fromscheme(scm) == value

	def test_dict(self):
		"""
		"""
		dicts = { \
			'`((1 . 1))' : {1: 1},
			'`((1 . "Hrm"))' : {1: "Hrm"},
			'`(("New York" . "Albany"))' : {'New York': 'Albany'},
		}
		for s, value in dicts.items():
			yield self.eval_test, s, value
			yield self.passthru_test, s, value

