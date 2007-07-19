
from ctypes.util import find_library
from ctypes import *
pythonapi.PyFile_AsFile.restype = c_void_p

# Try and find a libc library and libmng
import sys
if sys.platform == 'win32':
	# Find a libc like library
	libc = cdll.msvcrt

	# Look in the dll directory
	import os.path
	lib = os.path.join(os.dirname(__file__), "dll", "libmng.dll")
else:
	libc = cdll.LoadLibrary(find_library("c"))
	lib = find_library("guile")

if lib is None:
	raise RuntimeError("Was not able to find a libmng library which I can use.")

guile = cdll.LoadLibrary(lib)


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
		return c_void_p.__str__(self)

# Python function wrapper
#  Takes the SCM  arguments and splits them into bits for the function.
#  Checks the return type is a SCM too.

guile.scm_c_eval_string.argtypes = [c_char_p]
guile.scm_c_eval_string.restype  = SCM
guile.scm_c_lookup.restype = SCM

guile.scm_c_define_gsubr.argtypes = [c_char_p, c_int, c_int, c_int, c_void_p]
guile.scm_c_define_gsubr.restype  = SCM

import inspect

class Inter(object):
	__slots__ = ['module']

	def __init__(self, modules=[]):
		self.module = guile.scm_c_eval_string('(make-scope)')

	def eval(self, s):
		guile.scm_set_current_module(self.module)
		return guile.scm_c_eval_string(s)

	def register(self, name, func):
		if not callable(func):
			raise TypeError('The thing you register must be callable')

		args, varargs, varkw, defaults = inspect.getargspec(func)
		if not (varargs is None and varkw is None and defaults is None):
			raise TypeError("Don't know how to deal with this type of function yet..")
	
		guile.scm_set_current_module(self.module)

		WRAPPERFUNC = CFUNCTYPE(SCM, *([SCM]*len(args)))
		guile.scm_c_define_gsubr(name, len(args), 0, 0, WRAPPERFUNC(func))

def test():
	print "Hello 1 2 3"

if __name__ == '__main__':
	# Initlise guile
	guile.scm_init_guile()

	# Create a "scope" for this class
	guile.scm_c_primitive_load ("scope.scm")

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


	m1.register('test', test)
	m1.eval('(test)')


	#func_symbol = guile.scm_c_lookup("do-hello")
	#func        = guile.scm_variable_ref(func_symbol)
	
	#guile.scm_call_0(func)

