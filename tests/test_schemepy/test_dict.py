"""This file test the conversion between Scheme alist and Python dict."""

import common

class TestDict(object):
	def check_eval(self, s, value):
		print 'eval', s, value

		m1 = common.VM()
		a = m1.eval(m1.compile(s))

		assert m1.type(a) == dict
		assert m1.fromscheme(a) == value

	def check_passthru(self, s, value):
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
			yield self.check_eval, s, value
			yield self.check_passthru, s, value
