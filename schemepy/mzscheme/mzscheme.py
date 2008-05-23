from ctypes.util import find_library
from ctypes import *
# from schemepy.types import *
# from schemepy.exceptions import *
import types
import os.path

# Load the helper library which exports the macro's as C functions
path = os.path.abspath(os.path.join(os.path.split(__file__)[0], '_mzhelper.so'))
_mzhelper = cdll.LoadLibrary(path)

lib = find_library("mzscheme")
if lib is None:
    raise RuntimeError("Can't find a mzscheme library to use.")

mz = cdll.LoadLibrary(lib)

class SCM(c_void_p):
    """
    A Scheme_Object pointer in mzscheme.
    """
    def __str__(self):
        return "<SCM %s>" % self.value
    def __repr__(self):
        return self.__str__()

class VM(object):
    """VM for mzscheme
    """

    def __init__(self, profile):
        """\
        Create a VM.
        """
        # TODO: deal with profile

    def compile(self, code):
        """\
        Compile for mzscheme.
        """
        # TODO: mzscheme support compiling, add support for it
        return code

    def eval(self, code):
        """\
        eval the compiled code for mzscheme.
        """
        return mz.scheme_eval_string(code, global_env)

    def toscheme(self, val, shallow=False):
        "Convert a Python value to a Scheme value."
        if type(val) is bool:
            if val is True:
                return mz.scheme_true
            return mz.scheme_false
        if type(val) is int:
            return mz.scheme_make_integer_value(val)
        if type(val) is float:
            return mz.scheme_make_double(val)

    def fromscheme(self, val, shallow=False):
        "Get a Python value from a Scheme value."
        if not isinstance(val, SCM):
            raise ArgumentError("Expecting a Scheme value, but get a %s." % val)

        if mz.scheme_bool_p(val):
            if mz.scheme_false_p(val):
                return False
            return True
        if mz.scheme_fixnum_p(val):
            return mz.scheme_fixnum_value(val)
        if mz.scheme_bignum_p(val):
            src = mz.scheme_bignum_to_string(val, 10)
            # TODO: Do we need to free src?
            return eval(src)
        if mz.scheme_real_p(val):
            return mz.scheme_real_value(val)
        if mz.scheme_number_p(val):
            img = self.fromscheme(mz.scheme_complex_imaginary_part(val))
            real = self.fromscheme(mz.scheme_complex_real_part(val))
            if img == 0:
                return float(real)
            return complex(real, img)

    def type(self, val):
        "Get the corresponding Python type of the Scheme value."
        if mz.scheme_bool_p(val):
            return bool
        if mz.scheme_fixnum_p(val):
            return int
        if mz.scheme_bignum_p(val):
            return long
        if mz.scheme_real_p(val):
            return float
        if mz.scheme_number_p(val):
            img = self.fromscheme(mz.scheme_complex_imaginary_part(val))
            if img == 0:
                return float
            return complex

_mzhelper.init_mz()
global_env = SCM.in_dll(_mzhelper, "global_env")

# global constants
mz.scheme_true = SCM.in_dll(_mzhelper, "_scheme_true")
mz.scheme_false = SCM.in_dll(_mzhelper, "_scheme_false")

# macros
mz.scheme_bool_p = _mzhelper.scheme_bool_p
mz.scheme_false_p = _mzhelper.scheme_false_p
mz.scheme_fixnum_p = _mzhelper.scheme_fixnum_p
mz.scheme_fixnum_value = _mzhelper.scheme_fixnum_value
mz.scheme_bignum_p = _mzhelper.scheme_bignum_p
mz.scheme_real_p = _mzhelper.scheme_real_p
mz.scheme_real_value = _mzhelper.scheme_real_value
mz.scheme_number_p = _mzhelper.scheme_number_p

# constructors
mz.scheme_make_integer_value.argtypes = [c_int]
mz.scheme_make_integer_value.restype = SCM
mz.scheme_make_double.argtypes = [c_double]
mz.scheme_make_double.restype = SCM

# extractor
mz.scheme_fixnum_value.argtypes = [SCM]
mz.scheme_fixnum_value.restype = c_int
mz.scheme_bignum_to_string.argtypes = [SCM, c_int]
mz.scheme_bignum_to_string.restype = c_char_p
mz.scheme_real_value.argtypes = [SCM]
mz.scheme_real_value.restype = c_double
mz.scheme_complex_real_part.argtypes = [SCM]
mz.scheme_complex_real_part.restype = SCM
mz.scheme_complex_imaginary_part.argtypes = [SCM]
mz.scheme_complex_imaginary_part.restype = SCM

# Predicts
mz.scheme_bool_p.argtypes = [SCM]
mz.scheme_bool_p.restype = c_int
mz.scheme_false_p.argtypes = [SCM]
mz.scheme_false_p.restype = c_int
mz.scheme_fixnum_p.argtypes = [SCM]
mz.scheme_fixnum_p.restype = c_int
mz.scheme_bignum_p.argtypes = [SCM]
mz.scheme_bignum_p.restype = c_int
mz.scheme_real_p.argtypes = [SCM]
mz.scheme_bignum_p.restype = c_int

# Helper
mz.scheme_eval_string.argtypes = [c_char_p, SCM]
mz.scheme_eval_string.restype = SCM
