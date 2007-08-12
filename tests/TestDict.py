
import sys
sys.path.append('..')

from schemepy.guile import guile
Inter = guile.Inter

import py.test

class TestDict(object):
	def eval_test(self, s, value):
		m1 = Inter()
		a = m1.eval(s)

		assert a.type() == dict
		assert a.topython() == value

	def passthru_test(self, s, value):
		m1 = Inter()
		scm = m1.to_scheme(value)
	
		assert scm.type() == dict
		assert scm.topython() == value

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

