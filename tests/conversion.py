
import sys
sys.path.append('..')

from schemepy.guile import guile
Inter = guile.Inter

import py.test

def asset(a):
	if not a:
		raise SyntaxError('Error!')

class TestExceptions(object):

	def test_crap(self):
		"""
		Checks the interprator doesn't dies properly on crap...
		"""

		m1 = Inter()
		py.test.raises(Exception, m1.eval, 'asdasf')


class TestEvalBool(object):
	def test_true(self):
		"""
		Checks that the eval returns true '#t'.
		"""
		m1 = Inter()
		a = m1.eval('#t')

		assert a.type() == bool
		assert a.topython() is True

	def test_false(self):
		m1 = Inter()
		a = m1.eval('#f')

		assert a.type() == bool
		assert a.topython() is False

class TestEvalInt(object):
	def int_test(self, value):
		"""
		Checks that the eval returns int for small integers.
		"""
		m1 = Inter()
		a = m1.eval(str(value))

		assert a.type() == int
		assert a.topython() == value

	def test_ints(self):
		ints = [1, 5, 1000, 2**31-1]
		for value in ints:
			yield self.int_test, value

class TestEvalLong(object):
	def long_test(self, value):
		"""
		Checks that the eval returns long for large integers.
		"""
		m1 = Inter()
		a = m1.eval(str(value))

		assert a.type() == long
		assert a.topython() == value

	def test_longs(self):
		longs = [2**31+1, 2**31+200, 2**63-1]
		for value in longs:
			yield (self.long_test, value)
	
class TestEvalFloat(object):
	def float_test(self, s, value):
		"""
		Checks that the eval returns long for large integers.
		"""
		m1 = Inter()
		a = m1.eval(s)

		assert a.type() == float
		assert a.topython() == value

	def test_floats(self):
		floats = {
			'1.0':1.0, 
			'0.0':0.0, 
			# These don't seem to be portable :/
			'`+inf.0':float('inf'), 
			'`-inf.0':float('-inf'), 
			'`+nan.0':float('NaN')}

		for s, value in floats.items():
			yield self.float_test, s, value

class TestEvalComplex(object):
	def complex_test(self, s, value):
		"""
		Checks that the eval returns long for large integers.
		"""
		m1 = Inter()
		a = m1.eval(s)

		assert a.type() == complex
		assert a.topython() == value

	def test_complexs(self):
		complexs = {
			'3.2+4i' : complex(3.2, 4),
			'3+4i'   : complex(3, 4),
			# FIXME: A zero for imaginary is kind of undefined...
			'0+0i'   : complex(0, 0),
			'1.0+0i' : complex(1.0, 0),
		}
		for s, value in complexs.items():
			yield self.complex_test, s, value

class TestEvalString(object):
	def string_test(self, value):
		m1 = Inter()
		a = m1.eval(repr(value)[1:-1])

		assert isinstance(value, a.type())
		assert a.topython() == value

	def test_string(self):
		"""
		Checks that the eval returns strings for various input.
		"""
		strings = [ \
			 "", u"abc", u"t\n\t\n\r",  "a\0\0tl;\0a",
			u"", u"abc", u"t\n\t\n\r", u"a\0\0tl;\0a",
		]
		for value in strings:
			yield self.string_test, value

class TestEvalList(object):
	def list_test(self, s, value):
		"""
		"""
		m1 = Inter()
		a = m1.eval(s)

		assert a.type() == list
		assert a.topython() == value

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
			yield self.list_test, s, value

class TestEvalDict(object):
	def dict_test(self, s, value):
		m1 = Inter()

		a = m1.eval(s)
		assert a.type() == dict
		assert a.topython() == value

	def test_dict(self):
		"""
		"""
		dicts = { \
			'`((1 . 1))' : {1: 1},
			'`((1 . "Hrm"))' : {1: "Hrm"},
			'`(("New York" . "Albany"))' : {'New York': 'Albany'},
		}
		for s, value in dicts.items():
			yield self.dict_test, s, value

##def test_passthru(self):
##	"""
##	"""
##	# Check the singleton values
##	for value in [True, False]:
##		m1 = Inter()
##
##		scm = m1.to_scheme(value)
##		# Check the type is correct
##		assert scm.type() == bool
##
##		# Check we can convert back
##		assert scm.topython() is value
##
##	# Check the various number types
##	for value in ints+longs:
##		m1 = Inter()
##
##		scm = m1.to_scheme(value)
##		# Check the type is correct
##		assert isinstance(value, scm.type())
##
##		# Check we can convert back
##		assert scm.topython() is value
##
##	# Check the various larger types
##	for s, value in (lists+alists+floats).items():
##		m1 = Inter()
##
##		scm = m1.to_scheme(value)
##	
##		# Check the type is correct
##		assert isinstance(value, scm.type())
##
##		# Check we can convert back
##		assert scm.topython() is value
##
##	# Test python object pass thru
##	m1 = Inter()
##
##	class cls(object):
##		pass
##	a = cls()
##
##	scm = m1.to_scheme(a)
##	assert scm.type() == cls
##	assert scm.topython() is a

if __name__ == "__main__":
    unittest.main()
