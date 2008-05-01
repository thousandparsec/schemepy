from ctypes.util import find_library
from ctypes import *
from schemepy.types import *
import os.path

# Load the helper library which exports the macro's as C functions
path = os.path.abspath(os.path.join(os.path.split(__file__)[0], "_guilehelper.so"))
_guilehelper = cdll.LoadLibrary(path)

ver_helper = (_guilehelper.guile_major_version(), _guilehelper.guile_minor_version())
ver_lib    = {(1, 6): '12', (1, 8): '17'}[ver_helper]

lib = find_library("guile")
if lib is None:
    raise RuntimeError("Can't find a guile library to use.")
if not lib.endswith(ver_lib):
	raise RuntimeError("The found library %s does not match the library the helper was compiled with." % lib)

guile = cdll.LoadLibrary(lib)


class SCM(c_void_p):
    """
    A SCM hold a Scheme value.
    """
    def __init__(self, value=None):
        c_void_p.__init__(self)
        self.value = value
        
    def value_set(self, value):
        oldv = getattr(self, 'value', None)
        if oldv is not None:
            guile.scm_gc_unprotect_object(oldv)
        if value is not None:
            guile.scm_gc_protect_object(value)
        return c_void_p.value.__set__(self, v)

    def value_get(self):
        return c_void_p.value.__get__(self)
    scm = property(value_get, value_set)
    
    def __del__(self):
        self.value = None

    def __str__(self):
        return "<SCM %s>" % self.value
    
    def __repr__(self):
        return self.__str__()

    def type(self):
        """\
        Get the (Python) type of the value.

        NOTE: the type is not necessarily the *real* type of
              the converted Python value. In other words,
              `scm.type() == type(scm.fromscheme())' might be
              false. But `type(scm.fromscheme())' will be at
              least a sub-type of `scm.type()'.
        """
        if guile.scm_is_bool(self):
            return bool
        if guile.scm_is_number(self):
            if guile.scm_is_true(guile.scm_exact_p(self)):
                return int
            if guile.scm_c_imag_part(self) != 0:
                return complex
            return float
        if guile.scm_is_eol(self):
            return list
        if guile.scm_is_pair(self):
            if guile.scm_is_list(self):
                if guile.scm_is_alist(self):
                    return dict
                else:
                    return list
            else:
                return Cons
        if guile.scm_is_eol(self):
            return list
        return type(None)

    def fromscheme(self, shallow=False):
        "Return a Python value corresponding to this SCM"
        if guile.scm_is_bool(self):
            if guile.scm_is_true(self):
                return True
            return False
        if guile.scm_is_number(self):
            if guile.scm_is_true(guile.scm_exact_p(self)):
                return guile.scm_to_int32(self)
            if guile.scm_c_imag_part(self) != 0:
                return complex(guile.scm_c_real_part(self),
                               guile.scm_c_imag_part(self))
            return guile.scm_to_double(self)
        if guile.scm_is_eol(self):
            return []
        if guile.scm_is_pair(self):
            if guile.scm_is_list(self):
                if guile.scm_is_alist(self):
                    d = {}
                    scm = self
                    while not guile.scm_is_null(scm):
                        item  = guile.scm_car(scm)
                        key   = guile.scm_car(item).fromscheme()
                        value = guile.scm_cdr(item)
                        if not shallow:
                            d[key] = value.fromscheme()
                        else:
                            d[key] = value
                        scm = guile.scm_cdr(scm)
                    
                    return d
                
                else:
                    l = []
                    scm = self
                    while not guile.scm_is_null(scm):
                        item = guile.scm_car(scm)
                        if not shallow:
                            l.append(item.fromscheme())
                        else:
                            l.append(item)
                        scm = guile.scm_cdr(scm)

                    return l
            else:
                car = guile.scm_car(self)
                cdr = guile.scm_cdr(self)
                if not shallow:
                    return Cons(car.fromscheme(), cdr.fromscheme())
                else:
                    return Cons(car, cdr)
        if guile.scm_is_eol(self):
            return []
        return None

    def toscm(val):
        "Convert the Python value to a SCM"
        if type(val) is bool:
            return guile.scm_from_bool(val)
        if type(val) is int:
            return guile.scm_from_int32(val)
        if type(val) is complex:
            return guile.scm_make_complex(val.real, val.imag)
        if type(val) is float:
            return guile.scm_from_double(val)
        if isinstance(val, list):
            scm = guile.scm_eol()
            for item in reversed(val):
                scm = guile.scm_cons(SCM.toscm(item), scm)
            return scm
        return SCM(None)
    toscm = staticmethod(toscm)

class Compiler(object):
    """Compiler for guile. Guile doesn't support bytecode yet. So the
    compiler just do nothing."""
    def __call__(self, code):
        return code


def exception_body(src):
    """\
    The method is used to evaluate a piece of Scheme code where exception
    will be caught safely.
    """
    return guile.scm_c_eval_string(src).value
exception_body_t = CFUNCTYPE(SCM, c_char_p)
exception_body = exception_body_t(exception_body)

exception_handler_t = CFUNCTYPE(SCM, c_void_p, c_void_p, c_void_p)
def make_exception_handler(exceptions):
    """\
    * error-signal: thrown after receiving an unhandled fatal
      signal such as SIGSEGV, SIGBUS, SIGFPE etc. The rest
      argument in the throw contains the coded signal number (at
      present this is not the same as the usual Unix signal
      number).
    
    * system-error: thrown after the operating system indicates an
      error condition. The rest argument in the throw contains the
      errno value.
    
    * numerical-overflow: numerical overflow.
    
    * out-of-range: the arguments to a procedure do not fall
      within the accepted domain.
    
    * wrong-type-arg: an argument to a procedure has the wrong
      type.
    
    * wrong-number-of-args: a procedure was called with the wrong
      number of arguments.
    
    * memory-allocation-error: memory allocation error.
    
    * stack-overflow: stack overflow error.
    
    * regular-expression-syntax: errors generated by the regular
      expression library.
    
    * misc-error: other errors. 
    """
    def exception_handle(trash, key, args):
        """\
        The callback handler of Scheme exception. It was implemented as
        a closure: the exception caught here will be append to the list
        of the closure variable `exceptions'.
        """
        key = SCM(key)
        args = SCM(args)
        exceptions.append(Exception(key.fromscheme(), args.fromscheme()))
        return guile.scm_bool_t().value
    
    return exception_handler_t(exception_handle)
        

guile.scm_internal_catch.argtypes = [SCM, exception_body_t, c_char_p, exception_handler_t, c_void_p]
guile.scm_internal_catch.restype = SCM
guile.scm_c_eval_string.argtypes = [c_char_p]
guile.scm_c_eval_string.restype  = SCM

class VM(object):
    """VM for guile.
    """

    def __init__(self):
        self.exception = None
   
    def eval(self, src):
        exceptions = []
        r = guile.scm_internal_catch(guile.scm_bool_t, exception_body, src,
                                     make_exception_handler(exceptions), None)
        if len(exceptions) != 0:
            raise exceptions[0]
        return r

    def toscheme(val):
        return SCM.toscm(val)
    toscheme = staticmethod(toscheme)

# Initialize guile
guile.scm_init_guile()

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

guile.scm_imp      = _guilehelper.scm_imp
guile.scm_is_eol   = _guilehelper.scm_is_eol 
guile.scm_is_list  = _guilehelper.scm_is_list
guile.scm_is_alist = _guilehelper.scm_is_alist
guile.scm_is_exact = _guilehelper.scm_is_exact
# These are guile 1.8 functions
if hasattr(_guilehelper, 'scm_from_bool'):
	guile.scm_from_bool  = _guilehelper.scm_from_bool
	guile.scm_to_bool    = _guilehelper.scm_to_bool

	guile.scm_is_bool    = _guilehelper.scm_is_bool
	guile.scm_is_number  = _guilehelper.scm_is_number
	guile.scm_is_integer = _guilehelper.scm_is_integer
	guile.scm_is_rational= _guilehelper.scm_is_rational
	guile.scm_is_complex = _guilehelper.scm_is_complex 
	guile.scm_is_pair    = _guilehelper.scm_is_pair
	guile.scm_is_symbol  = _guilehelper.scm_is_symbol
	guile.scm_is_null    = _guilehelper.scm_is_null
	guile.scm_is_string  = _guilehelper.scm_is_string
	guile.scm_is_true    = _guilehelper.scm_is_true

	guile.scm_to_int32    = _guilehelper.scm_to_int32
	guile.scm_from_int32  = _guilehelper.scm_from_int32
	guile.scm_to_double   = _guilehelper.scm_to_double
	guile.scm_from_double = _guilehelper.scm_from_double

	guile.scm_to_locale_string    = _guilehelper.scm_to_locale_string
	guile.scm_from_locale_stringn = _guilehelper.scm_from_locale_stringn

	guile.scm_c_real_part = _guilehelper.scm_c_real_part
	guile.scm_c_imag_part = _guilehelper.scm_c_imag_part

	guile.scm_car = _guilehelper.scm_car
	guile.scm_cdr = _guilehelper.scm_cdr

	guile.scm_from_signed_integer = guile.scm_int2num
	guile.scm_from_locale_keyword = guile.scm_c_make_keyword

else:
	guile.scm_from_bool  = _guilehelper._scm_from_bool
#	guile.scm_is_bool    = _guilehelper._scm_is_bool
#	guile.scm_is_number  = _guilehelper._scm_is_number
#	guile.scm_is_integer = _guilehelper._scm_is_integer
#	guile.scm_is_pair    = _guilehelper._scm_is_pair
	guile.scm_is_symbol  = _guilehelper._scm_is_symbol
	guile.scm_is_true    = _guilehelper._scm_is_true
	guile.scm_is_null    = _guilehelper._scm_is_null


# Helper functions
guile.scm_c_real_part.argstypes = [SCM]
guile.scm_c_real_part.restype  = c_double
guile.scm_c_imag_part.argstypes = [SCM]
guile.scm_c_imag_part.restype  = c_double
guile.scm_bool_t.argstype = []
guile.scm_bool_t.restype  = SCM
guile.scm_bool_f.argstype = []
guile.scm_bool_f.restype  = SCM
guile.scm_eol.argtypes  = []
guile.scm_eol.restype   = SCM
guile.scm_cons.argtypes = [SCM, SCM]
guile.scm_cons.restype  = SCM
guile.scm_car.argtypes  = [SCM]
guile.scm_car.restype   = SCM
guile.scm_cdr.argtypes  = [SCM]
guile.scm_cdr.restype   = SCM


# Predict functions
guile.scm_exact_p.argtypes = [SCM]
guile.scm_exact_p.restype = SCM
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
guile.scm_is_complex.argstype  = [SCM]
guile.scm_is_complex.restype   = bool
guile.scm_is_string.argstype   = [SCM]
guile.scm_is_string.restype    = bool
guile.scm_is_pair.argstype     = [SCM]
guile.scm_is_pair.restype      = bool
guile.scm_is_symbol.argstype   = [SCM]
guile.scm_is_symbol.restype    = bool
guile.scm_is_list.argtypes  = [SCM]
guile.scm_is_list.restype   = bool
guile.scm_is_alist.argtypes = [SCM]
guile.scm_is_alist.restype  = bool
guile.scm_is_null.argtypes  = [SCM]
guile.scm_is_null.restype   = bool
guile.scm_is_eol.argtypes   = [SCM]
guile.scm_is_eol.restype    = bool

# Conversion functions
guile.scm_from_int32.argtypes = [c_int]
guile.scm_from_int32.restype = SCM
guile.scm_make_complex.argtypes = [c_double, c_double]
guile.scm_make_complex.restype = SCM
guile.scm_from_double.argtypes = [c_double]
guile.scm_from_double.restype = SCM
guile.scm_to_double.argstypes   = [SCM]
guile.scm_to_double.restype    = c_double
guile.scm_from_bool.argtypes   = [c_int]
guile.scm_from_bool.restype    = SCM
