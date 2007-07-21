
from ctypes.util import find_library
from ctypes import *
pythonapi.PyFile_AsFile.restype = c_void_p

# Try and find a libc library and libmng
import sys
import os.path
if sys.platform == 'win32':
	# Find a libc like library
	libc = cdll.msvcrt

	# Look in the dll directory
	lib = os.path.join(os.dirname(__file__), "dll", "libmng.dll")
else:
	libc = cdll.LoadLibrary(find_library("c"))
	lib = find_library("guile")

if lib is None:
	raise RuntimeError("Was not able to find a guile library which I can use.")

guile = cdll.LoadLibrary(lib)

# Load the helper library which exports the macro's as C functions
path = os.path.abspath(os.path.join(os.path.split(__file__)[0], "_guilehelper.so"))
_guilehelper = cdll.LoadLibrary(path)

# Macros
guile.scm_unbndp = _guilehelper.scm_unbndp
guile.scm_bool_t = _guilehelper.scm_bool_t
guile.scm_bool_f = _guilehelper.scm_bool_f
guile.scm_c_symbol_exists = _guilehelper.scm_c_symbol_exists

# These are guile 1.8 functions
if hasattr(_guilehelper, 'scm_from_bool'):
	guile.scm_from_bool  = _guilehelper.scm_from_bool
	guile.scm_is_bool    = _guilehelper.scm_is_bool
	guile.scm_is_number  = _guilehelper.scm_is_number
	guile.scm_is_integer = _guilehelper.scm_is_integer
	guile.scm_is_pair    = _guilehelper.scm_is_pair

	guile.scm_from_signed_integer = guile.scm_int2num
else:
	guile.scm_from_bool  = _guilehelper._scm_from_bool
#	guile.scm_is_bool    = _guilehelper._scm_is_bool
#	guile.scm_is_number  = _guilehelper._scm_is_number
#	guile.scm_is_integer = _guilehelper._scm_is_integer
#	guile.scm_is_pair    = _guilehelper._scm_is_pair
	guile.scm_is_symbol  = _guilehelper._scm_is_symbol
	guile.scm_is_true    = _guilehelper._scm_is_true


class SCM(c_void_p):
	"""
	SCM is the base type used by Guile, for our purposes we don't care what
	it actually is so we are going to use a void pointer.
	"""
	def __str__(self):
		"""
		(use-modules (ice-9 pretty-print))

		(pretty-print (lambda (x) x))
		"""
		port = guile.scm_open_output_string()
		guile.scm_call_2(prettyprint, self, port)
		return "<SCM %s>" % guile.scm_get_output_string(port).topython().strip()

	def __repr__(self):
		return c_void_p.__repr__(self)

	def type(self):
		if guile.scm_unbndp(self):
			return type(None)
		if guile.scm_is_bool(self):
			return bool
		if guile.scm_is_number(self):
			if guile.scm_is_integer(self):
				return int
#			if guile.scm_is_rational(self):
#				return float
#			if guile.scm_is_complex(self):
#				return complex
		if guile.scm_is_string(self):
			return str
		if guile.scm_is_pair(self):
			return list
		if guile.scm_is_symbol(self):
			return 'Symbol'

	def topython(self):
		if guile.scm_unbndp(self):
			return None
		if guile.scm_is_bool(self):
			return guile.scm_to_bool(self)
		if guile.scm_is_number(self):
			if guile.scm_is_integer(self):
				return guile.scm_to_int32(self)
#			if guile.scm_is_rational(self):
#				return guile.scm_to_double(self)
		if guile.scm_is_string(self):
			# FIXME: This is probably leaking memory
			return guile.scm_to_locale_string(self)
		if guile.scm_is_symbol(self):
			return guile.scm_symbol_to_string(self).topython()
		raise TypeError("Don't know how to convert this type yet.")

guile.scm_c_symbol_exists.argstype = [c_char_p]
guile.scm_c_symbol_exists.restype  = bool

# is Functions
guile.scm_is_bool.argstype     = [SCM]
guile.scm_is_bool.restype      = bool
guile.scm_is_number.argstype   = [SCM]
guile.scm_is_number.restype    = bool
guile.scm_is_integer.argstype  = [SCM]
guile.scm_is_integer.restype   = bool
#guile.scm_is_rational.argstype = [SCM]
#guile.scm_is_rational.restype  = bool
#guile.scm_is_complex.argstype  = [SCM]
#guile.scm_is_complex.restype   = bool
guile.scm_is_string.argstype   = [SCM]
guile.scm_is_string.restype    = bool
guile.scm_is_pair.argstype     = [SCM]
guile.scm_is_pair.restype      = bool
guile.scm_is_symbol.argstype   = [SCM]
guile.scm_is_symbol.restype    = bool


# to Functions
guile.scm_to_bool.argstype     = [SCM]
guile.scm_to_bool.restype      = bool
guile.scm_to_int32.argstype    = [SCM]
guile.scm_to_int32.restype     = int
guile.scm_to_double.argstype   = [SCM]
guile.scm_to_double.restype    = float

guile.scm_to_locale_string.argstype = [SCM]
guile.scm_to_locale_string.restype = c_char_p

guile.scm_symbol_to_string.argstype = [SCM]
guile.scm_symbol_to_string.restype  = SCM

# Evaluation functions
guile.scm_c_eval_string.argtypes = [c_char_p]
guile.scm_c_eval_string.restype  = SCM
guile.scm_c_lookup.restype = SCM

guile.scm_c_define_gsubr.argtypes = [c_char_p, c_int, c_int, c_int, c_void_p]
guile.scm_c_define_gsubr.restype  = SCM

guile.scm_bool_t.restype = SCM

guile.scm_list_p.argtypes = [SCM]
guile.scm_list_p.restype  = SCM

guile.scm_is_true.argtypes = [SCM]
guile.scm_is_true.restype = int


guile.scm_c_lookup.argtypes = [c_char_p]
guile.scm_c_lookup.restype  = SCM
guile.scm_variable_ref.argtypes = [SCM]
guile.scm_variable_ref.restype  = SCM

# Quick call functions
guile.scm_call_0.argtypes = [SCM]
guile.scm_call_0.restype  = SCM
guile.scm_call_1.argtypes = [SCM, SCM]
guile.scm_call_1.restype  = SCM
guile.scm_call_2.argtypes = [SCM, SCM, SCM]
guile.scm_call_2.restype  = SCM

guile.scm_open_output_string.argtypes = []
guile.scm_open_output_string.restype  = SCM
guile.scm_get_output_string.argtypes = [SCM]
guile.scm_get_output_string.restype  = SCM

# Conversion from python types to the "SCM" type
def toscm(a):
	try:
		return scmmapping[type(a)](a)
	except KeyError:
		return None

def string2scm(s):
	return guile.scm_from_locale_stringn(s, len(s))

def list2scm(l):
	return None

scmmapping = {
	bool: 	guile.scm_from_bool,
	int: 	guile.scm_from_int32,
#	float: 	guile.scm_from_double,
#	ComplexType: 	guile.
	long: 	None,
	None: 	None,
	dict: 	None,
	list: 	list2scm,
	str: 	string2scm, }

import inspect
class wrapper(object):
	def __init__(self, f):
		self.f = f

		self.args, self.varargs, trash, self.defaults = inspect.getargspec(f)
		if self.defaults is None:
			self.defaults = []

		if not trash is None:
			raise TypeError("Don't know how to deal with this type of function yet..")
	
	def varargs_get(self):
		return self.__varargs
	def varargs_set(self, v):
		self.__varargs = not v is None
	varargs = property(varargs_get, varargs_set)

	def unamed(self):
		return len(self.args)-len(self.defaults)
	unamed = property(unamed)

	def __call__(self, *args):
		args = list(args)

		# Get out the required arguments
		req = args[:self.unamed]

		# Split out the optional and "rest" bits
		if self.varargs:
			optargs, rstarg = args[len(req):-1], args[-1]
		else:
			optargs, rstarg = args[len(req):],   None
			
		# Check the optional bits
		opt = []
		for arg in optargs:
			# Is the optional arg undefined
			if guile.scm_unbndp(arg):
				break
			opt.append(arg)

		# Check if the rest part is defined
		rst = []
		if rstarg and not guile.scm_unbndp(rstarg):
			# Check the rest argument is a list...
			if guile.scm_is_true(guile.scm_list_p(rstarg)):
				print "Rest was a list.."
			else:
				print "Rest wasn't a list.."

			# Unpack the list shallowly
			rst = [] #topython(rst, shallow=True)

		r = self.f(*(req+opt+rst))
		if not r is None and not isinstance(r, SCM):
			raise TypeError("Return type was not a SCM!")
		return r

	def cfunctype(self):
		arguments = len(self.args)+(self.varargs)
		return CFUNCTYPE(SCM, *([SCM]*arguments))(self)

# Stuff for Exception catching
def exception_body(code):
	s = guile.scm_c_eval_string(code)
	return s.value
exception_body_t = CFUNCTYPE(SCM, c_char_p)
exception_body   = exception_body_t(exception_body)

def exception_handler(trash, key, args):
	print "Exception handler!", trash, key, args

	print key.type(), args.type()
	print key.topython()
	print 

	raise Exception(key.topython(), args)
exception_handler_t = CFUNCTYPE(SCM, c_void_p, SCM, SCM)
exception_handler   = exception_handler_t(exception_handler)
guile.scm_internal_catch.argtypes = [SCM, exception_body_t, c_char_p, exception_handler_t, c_void_p]

class Inter(object):
	__slots__ = ['module']

	def __init__(self, modules=[]):
		self.module = guile.scm_c_eval_string('(make-scope)')

	def eval(self, s):
		"""
		Evaluate a scheme string.
		"""
		guile.scm_set_current_module(self.module)
		return guile.scm_internal_catch(guile.scm_bool_t(), exception_body, s, exception_handler, None)

	def register(self, name, func, autoconvert=False):
		"""
		Register a python function into the scheme namespace using "name".

		If autoconvert is True, then the arguments will be converted to the python 
		types and the return value converted back to scheme types.

		If autoconvert is False, then the arguments will be Scheme types and must
		be converted manually. The return type must also be a Scheme type.
		"""
		if not callable(func):
			raise TypeError('The thing you register must be callable')

		w = wrapper(func)

		guile.scm_set_current_module(self.module)
		guile.scm_c_define_gsubr(name, w.unamed, len(w.defaults), w.varargs, w.cfunctype())

	def __getattr__(self, key):
		guile.scm_set_current_module(self.module)
		if not guile.scm_c_symbol_exists(key):
			raise KeyError('No such %s exists in the environment.' % key)

		return guile.scm_variable_ref(guile.scm_c_lookup(key))

def testfunc1():
	print "Hello 1 2 3"
	print

def testfunc2(a):
	print a
	print

def testfunc3(a, *args):
	print a, args
	print

def testfunc4(a, v='test'):
	print a, v
	print

def testfunc5(a, **kw):
	print a, kw
	print

def testfunc6(a, v='test', *args):
	print a, v, args
	print

def testfunc7(a, v='test', **kw):
	print a, v, kw
	print

def testfunc8(a, v='test', *args, **kw):
	print a, v, args, kw
	print

if __name__ == '__main__':
	# Initlise guile
	guile.scm_init_guile()

	# Create a "scope" for this class
	guile.scm_c_primitive_load ("profiles/scope.scm")
	# Load the pretty-print module..
	guile.scm_c_eval_string("(use-modules (ice-9 pretty-print))")

	prettyprint_symbol = guile.scm_c_lookup("pretty-print")
	prettyprint        = guile.scm_variable_ref(prettyprint_symbol)

	m1 = Inter()
	m2 = Inter()

	print m1.module
	print m2.module

	m1.eval("""
(define do-hello
  (lambda ()
    (display "Hello world from 1.") 
     (newline)))
""")
	m1.eval('(do-hello)')

	m2.eval("""
(define do-hello
  (lambda ()
    (display "Hello world from 2.") 
     (newline)))
""")
	m2.eval('(do-hello)')

	print inspect.getargspec(testfunc1)
	print inspect.getargspec(testfunc2)
	print inspect.getargspec(testfunc3)
	print inspect.getargspec(testfunc4)
	print inspect.getargspec(testfunc5)
	print inspect.getargspec(testfunc6)
	print inspect.getargspec(testfunc7)
	print inspect.getargspec(testfunc8)

	print 'test1'
	m1.register('test1', testfunc1)
	m1.eval('(test1)')

	print m1.test1
	try:
		m1.test2
	except KeyError, e:
		print e

	print 'test2'
	m1.register('test2', testfunc2)
	m1.eval('(test2 test1)')

	print 'test3'
	m1.register('test3', testfunc3)
	m1.eval('(test3 test2)')
	m1.eval('(test3 test2 test1)')
	m1.eval('(test3 test2 test1 test1)')

	print 'test4'
	m1.register('test4', testfunc4)
	m1.eval('(test4 test1)')
	m1.eval('(test4 test1 test2)')

