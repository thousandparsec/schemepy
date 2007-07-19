
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


INITMODULE = CFUNCTYPE(None, c_void_ptr)
def py_initmodule(ptr):
	print "Init Module..."

	return
initmodule=INITMODULE(py_initmodule)

guile.scm_c_define_module.restype = SCM

class Inter:
	__slots__ = ['modulename']

	def __init__(self, modules=[]):
		self.modulename = str(id(self))
		self.module     = guile.scm_c_define_module(self.modulename, initmodule, None)


if __name__ == '__main__':
	# Initlise guile
	guile.scm_init_guile()

	# Create a "scope" for this class
	guile.scm_c_primitive_load ("scope.scm")

	m1 = Inter()
	m2 = Inter()


	#func_symbol = guile.scm_c_lookup("do-hello")
	#func        = guile.scm_variable_ref(func_symbol)
	
	#guile.scm_call_0(func)

