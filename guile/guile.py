# TODO: Rational/Bignum and complex
# TODO: Add the autoconversion

import gc
gc.set_debug(gc.DEBUG_LEAK)

import sys

from ctypes.util import find_library
from ctypes import *

# Try and find a libc library and libguile
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
guile.scm_eol    = _guilehelper.scm_eol
guile.scm_c_symbol_exists = _guilehelper.scm_c_symbol_exists

guile.scm_smob_data      = _guilehelper.scm_smob_data
guile.scm_set_smob_data  = _guilehelper.scm_set_smob_data
guile.scm_return_newsmob = _guilehelper.scm_return_newsmob
guile.scm_smob_predicate = _guilehelper.scm_smob_predicate

guile.scm_is_list  = _guilehelper.scm_is_list
guile.scm_is_alist = _guilehelper.scm_is_alist
guile.scm_is_exact = _guilehelper.scm_is_exact

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
	guile.scm_is_null    = _guilehelper._scm_is_null


def SCMc(address):
	return SCM(address)

import weakref

class SCM(c_void_p):
	"""
	SCM is the base type used by Guile, for our purposes we don't care what
	it actually is so we are going to use a void pointer.
	"""
#	__cache = weakref.WeakValueDictionary()
#
#	def __new__(cls, address):
#		try:
#			return cls.__cache[address]
#		except KeyError:
#			c = c_void_p.__new__(cls)
#			return c

	def __init__(self, address=None):
		c_void_p.__init__(self)
		self.value = address

#		# Cache this object
#		self.__cache[address] = self

	def value_set(self, v):
		oldv = getattr(self, 'value', None)
		if not oldv is None:
			#print hex(id(oldv)), "Unprotecting"
			if getattr(self, 'protected', False):
				guile.scm_gc_unprotect_object(oldv)
			else:
				print "WTF! tried to unprotect an object!"
			self.protected = False

		if not v is None:
			#print hex(id(v)), "Protecting"
			guile.scm_gc_protect_object(v)
			self.protected = True

		return c_void_p.value.__set__(self, v)
	def value_get(self):
		return c_void_p.value.__get__(self)
	value = property(value_get, value_set)

	def __del__(self):
		self.value = None

	def __str__(self):
		port = guile.scm_open_output_string()
		key  = guile.scm_from_locale_keyword("per-line-prefix")
		a = guile.scm_call_4(prettyprint, self, port, key, toscm("     "))
		return "<SCM %s>" % guile.scm_get_output_string(port).topython().strip()

	def __repr__(self):
		return SCM.__str__(self)

	def type(self):
		if guile.scm_unbndp(self):
			return type(None)
		if guile.scm_is_bool(self):
			return bool
		if guile.scm_is_number(self):
			if guile.scm_is_rational(self):
				if guile.scm_is_exact(self):
					return int
				return float
#			if guile.scm_is_complex(self):
#				return complex
		if guile.scm_is_string(self):
			return str
		if guile.scm_is_pair(self):
			if guile.scm_is_list(self):
				if guile.scm_is_alist(self):
					return dict
				return list
			return 'Pair'
		if guile.scm_is_symbol(self):
			return 'Symbol'
		if guile.scm_smob_predicate(PythonSMOB.tag, self):
			return object

	def topython(self, shallow=False):
		if guile.scm_unbndp(self):
			return None
		if guile.scm_is_bool(self):
			return guile.scm_to_bool(self)
		if guile.scm_is_number(self):
			if guile.scm_is_rational(self):
				if guile.scm_is_exact(self):
					return guile.scm_to_int32(self)
				return guile.scm_to_double(self)
		if guile.scm_is_string(self):
			# FIXME: This is probably leaking memory
			return guile.scm_to_locale_string(self)
		if guile.scm_is_symbol(self):
			return guile.scm_symbol_to_string(self).topython()
		if guile.scm_is_pair(self):
			if guile.scm_is_list(self):
				if guile.scm_is_alist(self):
					d = {}

					scm = self
					while not guile.scm_is_null(scm):
						item = guile.scm_car(scm)

						key   = guile.scm_car(item).topython()
						value = guile.scm_cdr(item)

						if not shallow:
							d[key] = value.topython()
						else:
							d[key] = value
						scm = guile.scm_cdr(scm)

					return d

				l = []

				scm = self
				while not guile.scm_is_null(scm):
					item = guile.scm_car(scm)
					if not shallow:
						l.append(item.topython())
					else:
						l.append(item)
					scm = guile.scm_cdr(scm)

				return l
		if guile.scm_smob_predicate(PythonSMOB.tag, self):
			return PythonSMOB.get(self)
		raise TypeError("Don't know how to convert this type yet.")

from _ctypes import Py_INCREF, Py_DECREF, PyObj_FromPtr

class SCMtbits(c_void_p):
	pass

class PythonSMOB(c_void_p):
	"""
	Functions for dealing with a Python "pass-thru" object.
	"""
	def register():
		# Create the SMOB type
		PythonSMOB.tag = guile.scm_make_smob_type("PythonSMOB", 0)
		guile.scm_set_smob_free( PythonSMOB.tag, PythonSMOB.free)
		guile.scm_set_smob_print(PythonSMOB.tag, PythonSMOB.str)
	register = staticmethod(register)	

	def new(pyobj):
		"""
		Create a new PythonSMOB which wraps the given object.
		"""
		pypointer = id(pyobj)	

		# Increase the reference count to the object	
		Py_INCREF(pyobj)

		# Create the new smob
		return guile.scm_return_newsmob(PythonSMOB.tag, pypointer)
	new = staticmethod(new)

	def free(smob):
		"""
		When the guile garbage collector frees the smob, remove the 
		extra reference so Python can garbage collect the object.
		"""
		#print "PythonSMOB.free"

		# Get the python object we are pointing too
		pypointer = guile.scm_smob_data(smob)

		# Decrease the reference to the pypointer
		Py_DECREF(PyObj_FromPtr(pypointer))

		return 0
	free_cfunc = CFUNCTYPE(c_int, c_void_p)
	free = staticmethod(free)

	def str(smob, port, pstate):
		smob, port = SCM(smob), SCM(port)

		# Get the python object we are pointing too
		pypointer = guile.scm_smob_data(smob)

		pyobj = PyObj_FromPtr(pypointer)
		guile.scm_display(toscm(repr(pyobj)), port)
		guile.scm_newline(port)

	str_cfunc = CFUNCTYPE(None, c_void_p, c_void_p, c_void_p)
	str = staticmethod(str)

	def get(smob):
		pypointer = guile.scm_smob_data(smob)
		return PyObj_FromPtr(pypointer)
	get = staticmethod(get)

PythonSMOB.free = PythonSMOB.free_cfunc(PythonSMOB.free)
PythonSMOB.str  = PythonSMOB.str_cfunc(PythonSMOB.str)

# Garbage collection routines
# It is important these return a c_void_p rather then a SCM otherwise we get
# a loop from SCM's __init__ and __del__
#guile.scm_gc_protect_object.argtypes   = [c_void_p]
#guile.scm_gc_protect_object.restype    = c_void_p
#guile.scm_gc_unprotect_object.argtypes = [c_void_p]
#guile.scm_gc_unprotect_object.restype  = c_void_p

# Display functions
guile.scm_display.argtypes = [SCM, SCM]
guile.scm_display.restype  = None
guile.scm_newline.argtypes = [SCM]
guile.scm_display.restype  = None

# SMOB functions
guile.scm_make_smob_type.argtypes = [c_char_p, c_int]
guile.scm_make_smob_type.restype  = SCMtbits
guile.scm_set_smob_free.argtypes  = [SCMtbits, PythonSMOB.free_cfunc]
guile.scm_set_smob_free.restype   = None
guile.scm_set_smob_print.argtypes = [SCMtbits, PythonSMOB.str_cfunc]
guile.scm_set_smob_print.restype  = None
guile.scm_return_newsmob.argtypes = [SCMtbits, c_void_p]
guile.scm_return_newsmob.restype  = SCMc
guile.scm_smob_predicate.argtypes = [SCMtbits, SCM]
guile.scm_smob_predicate.restype  = bool

# is Functions
guile.scm_c_symbol_exists.argstype = [c_char_p]
guile.scm_c_symbol_exists.restype  = bool

guile.scm_unbndp.argstype      = [SCM]
guile.scm_unbndp.restype       = bool

guile.scm_bool_t.argstype = []
guile.scm_bool_t.restype  = SCMc

guile.scm_is_true.argtypes     = [SCM]
guile.scm_is_true.restype      = int
guile.scm_is_bool.argstype     = [SCM]
guile.scm_is_bool.restype      = bool
guile.scm_is_number.argstype   = [SCM]
guile.scm_is_number.restype    = bool
guile.scm_is_integer.argstype  = [SCM]
guile.scm_is_integer.restype   = bool
guile.scm_is_rational.argstype = [SCM]
guile.scm_is_rational.restype  = bool
#guile.scm_is_complex.argstype  = [SCM]
#guile.scm_is_complex.restype   = bool
guile.scm_is_string.argstype   = [SCM]
guile.scm_is_string.restype    = bool
guile.scm_is_pair.argstype     = [SCM]
guile.scm_is_pair.restype      = bool
guile.scm_is_symbol.argstype   = [SCM]
guile.scm_is_symbol.restype    = bool
guile.scm_is_signed_integer.argstype = [SCM, c_int, c_int]
guile.scm_is_signed_integer.restype  = bool

# to Functions
guile.scm_to_bool.argstype     = [SCM]
guile.scm_to_bool.restype      = bool
guile.scm_to_int32.argstype    = [SCM]
guile.scm_to_int32.restype     = int
guile.scm_to_double.argstype   = [SCM]
guile.scm_to_double.restype    = c_double

guile.scm_to_locale_string.argstype = [SCM]
guile.scm_to_locale_string.restype  = c_char_p

guile.scm_symbol_to_string.argstype = [SCM]
guile.scm_symbol_to_string.restype  = SCMc

# List functions
guile.scm_is_list.argtypes  = [SCM]
guile.scm_is_list.restype   = bool
guile.scm_is_alist.argtypes = [SCM]
guile.scm_is_alist.restype  = bool
guile.scm_is_null.argtypes  = [SCM]
guile.scm_is_null.restype   = bool

guile.scm_eol.argtypes  = []
guile.scm_eol.restype   = SCMc
guile.scm_cons.argtypes = [SCM, SCM]
guile.scm_cons.restype  = SCMc
guile.scm_car.argtypes  = [SCM]
guile.scm_car.restype   = SCMc
guile.scm_cdr.argtypes  = [SCM]
guile.scm_cdr.restype   = SCMc

# Conversion functions
guile.scm_from_bool.argtypes   = [c_int]
guile.scm_from_bool.restype    = SCMc
guile.scm_from_int32.argtypes  = [c_int]
guile.scm_from_int32.restype   = SCMc
guile.scm_from_double.argtypes = [c_double]
guile.scm_from_double.restype  = SCMc
guile.scm_from_locale_stringn.argtypes  = [c_char_p, c_int]
guile.scm_from_locale_stringn.restype   = SCMc
guile.scm_from_locale_keyword.argtypes = [c_char_p]
guile.scm_from_locale_keyword.restype  = SCMc
guile.scm_from_locale_keywordn.argtypes = [c_char_p, c_int]
guile.scm_from_locale_keywordn.restype  = SCMc
guile.scm_keyword_to_symbol.argtypes = [SCM]
guile.scm_keyword_to_symbol.restype = SCMc

# Evaluation functions
guile.scm_c_eval_string.argtypes = [c_char_p]
guile.scm_c_eval_string.restype  = SCMc
guile.scm_c_lookup.restype = SCMc

guile.scm_c_define_gsubr.argtypes = [c_char_p, c_int, c_int, c_int, c_void_p]
guile.scm_c_define_gsubr.restype  = SCMc

guile.scm_c_lookup.argtypes = [c_char_p]
guile.scm_c_lookup.restype  = SCMc
guile.scm_variable_ref.argtypes = [SCM]
guile.scm_variable_ref.restype  = SCMc

# Quick call functions
guile.scm_call_0.argtypes = [SCM]
guile.scm_call_0.restype  = SCMc
guile.scm_call_1.argtypes = [SCM, SCM]
guile.scm_call_1.restype  = SCMc
guile.scm_call_2.argtypes = [SCM, SCM, SCM]
guile.scm_call_2.restype  = SCMc
guile.scm_call_3.argtypes = [SCM, SCM, SCM, SCM]
guile.scm_call_3.restype  = SCMc
guile.scm_call_4.argtypes = [SCM, SCM, SCM, SCM, SCM]
guile.scm_call_4.restype  = SCMc

guile.scm_open_output_string.argtypes = []
guile.scm_open_output_string.restype  = SCMc
guile.scm_get_output_string.argtypes = [SCM]
guile.scm_get_output_string.restype  = SCMc

# Conversion from python types to the "SCM" type
def toscm(a):
	try:
		return scmmapping[type(a)](a)
	except KeyError:
		return None

def string2scm(s):
	return guile.scm_from_locale_stringn(s, len(s))

def list2scm(l):
	scm = guile.scm_eol()
	for item in reversed(l):
		scm = guile.scm_cons(toscm(item), scm)
	return scm

def dict2scm(d):
	scm = guile.scm_eol()
	for key, value in d.iteritems():
		scm = guile.scm_cons(guile.scm_cons(toscm(key), toscm(value)), scm)
	return scm

scmmapping = {
	bool: 	guile.scm_from_bool,
	int: 	guile.scm_from_int32, 	# FIXME: This won't probably work on 64bit machine...
	float: 	guile.scm_from_double,
#	ComplexType: 	guile.
	long: 	None,
	dict: 	dict2scm,
	list: 	list2scm,
	str: 	string2scm, 
}

import inspect
class wrapper(object):
	"""\
	This class wraps a callable so that the scheme enviroment can call a 
	Python callable.

	It can also automatically convert scheme values into their Python
	equivalents.
	"""

	def __init__(self, f):
		"""
		Wrapper(f) 

		f is the callable you want to wrap.
		"""
		self.f = f

		self.args, self.varargs, trash, self.defaults = inspect.getargspec(f)
		if self.defaults is None:
			self.defaults = []

		if not trash is None:
			raise TypeError("Don't know how to deal with this type of function yet..")

		arguments = len(self.args)+(self.varargs)
		self.cfunctype = CFUNCTYPE(SCM, *([c_void_p]*arguments))(self)
	
	def varargs_get(self):
		return self.__varargs
	def varargs_set(self, v):
		self.__varargs = not v is None
	varargs = property(varargs_get, varargs_set)

	def unamed(self):
		return len(self.args)-len(self.defaults)
	unamed = property(unamed)

	def __call__(self, *args):
		args = [SCM(x) for x in args]

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
			if rstarg.type() == list:
				# Unpack the list shallowly
				rst = rstarg.topython(shallow=True)
			else:
				# WTF?
				print "Rest wasn't a list.."

		r = self.f(*(req+opt+rst))
		if not r is None and not isinstance(r, SCM):
			raise TypeError("Return type was not a SCM!")
		return r

# Stuff for Exception catching
#
# These to functions are needed to 
def exception_body(code):
	s = guile.scm_c_eval_string(code)
	return s.value
exception_body_t = CFUNCTYPE(SCM, c_char_p)
exception_body   = exception_body_t(exception_body)

def exception_handler(trash, key, args):
	"""\
	* error-signal: thrown after receiving an unhandled fatal signal such as SIGSEGV, SIGBUS, SIGFPE etc. The rest argument in the throw contains the coded signal number (at present this is not the same as the usual Unix signal number).
	* system-error: thrown after the operating system indicates an error condition. The rest argument in the throw contains the errno value.
	* numerical-overflow: numerical overflow.
	* out-of-range: the arguments to a procedure do not fall within the accepted domain.
	* wrong-type-arg: an argument to a procedure has the wrong type.
	* wrong-number-of-args: a procedure was called with the wrong number of arguments.
	* memory-allocation-error: memory allocation error.
	* stack-overflow: stack overflow error.
	* regular-expression-syntax: errors generated by the regular expression library.
	* misc-error: other errors. 
	"""
	raise Exception(key.topython(), args.topython())
exception_handler_t = CFUNCTYPE(SCM, c_void_p, SCM, SCM)
exception_handler   = exception_handler_t(exception_handler)

guile.scm_internal_catch.argtypes = [SCM, exception_body_t, c_char_p, exception_handler_t, c_void_p]
guile.scm_internal_catch.restype  = SCMc

class Inter(object):
	__slots__ = ['module', 'pythonfuncs']

	def __init__(self, modules=[]):
		self.module = guile.scm_c_eval_string('(make-scope)')
		self.pythonfuncs = {}

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
		# Store a copy of the function so it doesn't get garbage collected
		self.pythonfuncs[name] = w

		guile.scm_set_current_module(self.module)
		guile.scm_c_define_gsubr(name, w.unamed, len(w.defaults), w.varargs, w.cfunctype)

	def __getattr__(self, key):
		guile.scm_set_current_module(self.module)
		if not guile.scm_c_symbol_exists(key):
			raise KeyError('No such %s exists in the environment.' % key)

		return guile.scm_variable_ref(guile.scm_c_lookup(key))

# Initlise guile
guile.scm_init_guile()

# Create a "scope" for this class
guile.scm_c_primitive_load ("profiles/scope.scm")

# Load the pretty-print module..
guile.scm_c_eval_string("(use-modules (ice-9 pretty-print))")
prettyprint_symbol = guile.scm_c_lookup("pretty-print")
prettyprint        = guile.scm_variable_ref(prettyprint_symbol)

# Register the python SMOB
PythonSMOB.register()

if __name__ == '__main__':
	m1 = Inter()

	# Create a PythonSMOB
	import gc # We need to check that everything still works...

	class A(object):
		def __del__(self):
			print "DEL!!", self

	a = A()
	print 0, id(a), 'refs', sys.getrefcount(a)
	scm = PythonSMOB.new(a)
	print 1, scm,   'refs', sys.getrefcount(a)
	print 2, scm.type()
	b = scm.topython()

	print 3, b
	print 4, a is b

	print 5, 'refs', sys.getrefcount(a)
	del b
	gc.collect()

	print 6, 'refs', sys.getrefcount(a)
	del a
	gc.collect()

	print 7
	print scm

	b = scm.topython()

	print 8
	del scm
	# Force Guile's garbage collection a few times
	guile.scm_gc()
	guile.scm_gc()

	print 9, 'refs', sys.getrefcount(b)
	gc.collect()

	del b
	# the __del__ method of A should get called here.

	# Check the guile GC isn't getting my objects...
	print "---------------------"
	a = A()
	scm = PythonSMOB.new(a)
	print scm
	# Force Guile's garbage collection a few times
	guile.scm_gc()
	guile.scm_gc()
	guile.scm_gc()
	guile.scm_gc()
	guile.scm_gc()
	guile.scm_gc()
	print scm
	del scm

	print "---------------------"

	# Conversion to Scheme objects..
	print "\nConverting Python objects into Scheme objects...."
	print True, toscm(True)
	print False, toscm(False)
	print 1, toscm(1)
	print 2, toscm(2)
	print 1.0, toscm(1.0)
	print 'Test', toscm('Test')
	print [10,5, 10], toscm([10, 5, 10])
	print {1:'test', 2:'hello'}, toscm({1:'test', 2:'hello'})
	print

	# Test scopes
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


	# Conversion from Scheme objects..
	# Numbers
	a = m1.eval("1")
	print a
	print a.type()
	print a.topython()

	a = m1.eval("2")
	print a
	print a.type()
	print a.topython()

	a = m1.eval("1.0")
	print a
	print a.type()
	print a.topython()

	# String

	# List
	a = m1.eval("""'(1 2 3 4 5)""")
	print a
	print a.type()
	print a.topython()

	# Dictionary
	a = m1.eval("""'(("New York" . "Albany") ("Oregon"   . "Salem") ("Florida"  . "Miami"))""")
	print a
	print a.type()
	print a.topython()

	# Function registration
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


