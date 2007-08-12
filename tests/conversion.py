
import sys
sys.path.append('..')

from schemepy.guile import guile
Inter = guile.Inter

def asset(a):
	if not a:
		raise SyntaxError('Error!')

def test_aaaa_unknown():
	"""
	Checks the interprator doesn't dies properly on crap...
	"""
	m1 = Inter()
	m1.eval('asdasf')

def test_eval2bool():
	"""
	Checks that the eval returns a bool for '#t' and '#f'.
	"""
	m1 = Inter()
	# True
	a = m1.eval('#t')
	asset(a.type() == bool)
	asset(a.topython() is True)

	m1 = Inter()
	# False
	a = m1.eval('#f')
	asset(a.type() == bool)
	asset(a.topython() is False)

ints = [1, 5, 1000, 2**31-1]
def test_eval2int():
	"""
	Checks that the eval returns int for small integers.
	"""
	for value in ints:
		m1 = Inter()

		a = m1.eval(str(value))
		asset(a.type() == int)
		asset(a.topython() == value)

longs = [2**31+1, 2**31+200, 2**63-1]
def test_eval2long():
	"""
	Checks that the eval returns long for large integers.
	"""
	for value in longs:
		m1 = Inter()

		a = m1.eval(str(value))
		print a, a.type()
		asset(a.type() == long)
		asset(a.topython() == value)

floats = {
	'1.0':1.0, 
	'0.0':0.0, 
	# These don't seem to be portable :/
	'`+inf.0':float('inf'), 
	'`-inf.0':float('-inf'), 
	'`+nan.0':float('NaN')}
def test_eval2float():
	"""
	Checks that the eval returns long for large integers.
	"""
	for s, value in floats.items():
		m1 = Inter()

		# Numbers
		a = m1.eval(s)
		asset(a.type() == float)
		asset(a.topython() == value)

complexs = {
	'3.2+4i' : complex(3.2, 4),
	'3+4i'   : complex(3, 4),
	# FIXME: A zero for imaginary is kind of undefined...
	'0+0i'   : complex(0, 0),
	'1.0+0i' : complex(1.0, 0),
}
def test_eval2complex():
	"""
	Checks that the eval returns long for large integers.
	"""
	for s, value in complexs.items():
		m1 = Inter()

		a = m1.eval(s)
		asset(a.type() == complex)
		asset(a.topython() == value)

strings = [ \
	 "", u"abc", u"t\n\t\n\r",  "a\0\0tl;\0a",
	u"", u"abc", u"t\n\t\n\r", u"a\0\0tl;\0a",
]
def test_eval2string():
	"""
	Checks that the eval returns long for large integers.
	"""
	for value in strings:
		m1 = Inter()

		a = m1.eval(repr(value)[1:-1])
		asset(isinstance(value, a.type()))
		asset(a.topython() == value)

lists = { \
	"`()"               : [], 					# Empty List
	"`(1 2 3)"          : [1, 2, 3], 			# Simple list with integers
	"`(1.0 2.0 3.0)"    : [1.0, 2.0, 3.0], 		# Simple list with floats
	'`("a" "aa" "aaa")' : ['a', 'aa', 'aaa'], 	# Simple list with strings
	'`(1 1.0 "a")'      : [1, 1.0, 'a'],		# List with a simpled mixed list
}
def test_eval2list():
	"""
	Checks that the eval works for various lists.
	"""
	for s, value in lists.items():
		m1 = Inter()

		a = m1.eval(s)
		asset(a.type() == list)
		asset(a.topython() == value)

alists = { \
	'((1 . 1))' : {1: 1},
	'((1 . "Hrm"))' : {1: "Hrm"},
	'(("New York" . "Albany"))' : {'New York': 'Albany'},
}
def ttest_eval2alist():
	"""
	"""
	for s, value in alists.items():
		m1 = Inter()

		a = m1.eval(s)
		asset(a.type() == DictType)
		asset(a.topython() == value)

def test_passthru():
	"""
	"""
	# Check the singleton values
	for value in [True, False]:
		m1 = Inter()

		scm = m1.to_scheme(value)
		print value, scm
		print type(value), scm.type()

		# Check the type is correct
		asset(scm.type() == bool)

		# Check we can convert back
		asset(scm.topython() is value)

	# Check the various number types
	for value in ints+longs:
		m1 = Inter()

		scm = m1.to_scheme(value)
		print value, scm
		print type(value), scm.type()
	
		# Check the type is correct
		asset(isinstance(value, scm.type()))

		# Check we can convert back
		asset(scm.topython() is value)

	# Check the various larger types
	for s, value in (lists+alists+floats).items():
		m1 = Inter()

		scm = m1.to_scheme(value)
	
		# Check the type is correct
		asset(isinstance(value, scm.type()))

		# Check we can convert back
		asset(scm.topython() is value)

	# Test python object pass thru
	m1 = Inter()

	class cls(object):
		pass
	a = cls()

	scm = m1.to_scheme(a)
	asset(scm.type() == cls)
	asset(scm.topython() is a)

if __name__ == "__main__":
	import sys
	import traceback
	for n in dir():
		if n.startswith('test'):
			try:
				print
				print
				print "Running %s" % n
				exec("%s()" % n)
			except Exception, e:
				type, val, tb = sys.exc_info()
				sys.stderr.write(''.join(traceback.format_exception(type, val, tb)))
				print e

