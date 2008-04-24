
import common
setup_module = common.setup_module

import py.test

class TestList(object):
	def eval_test(self, s, value):
		"""
		"""
		print 'eval', s, value

		m1 = common.Inter()
		a = m1.eval(s)

		assert a.type() == list
		assert a.topython() == value

	def passthru_test(self, s, value):
		print "passthru", repr(value)

		m1 = common.Inter()
		scm = m1.to_scheme(value)
	
		assert scm.type() == list
		assert scm.topython() == value

	def test_list(self):
		"""
		Checks that the eval works for various lists.
		"""
		lists = { \
			"`()"               : [], 					# Empty List
			"`(1 2 3)"          : [1, 2, 3], 			# Simple list with integers
			"`(1.0 2.0 3.0)"    : [1.0, 2.0, 3.0], 		# Simple list with floats
			'`("a" "aa" "aaa")' : ['a', 'aa', 'aaa'], 	# Simple list with strings
			'`(1 1.0 "a")'      : [1, 1.0, 'a'],		# List with a simpled mixed list
		}
		for s, value in lists.items():
			yield self.eval_test, s, value
			yield self.passthru_test, s, value
