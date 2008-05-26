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
    """\
    A Scheme_Object pointer in mzscheme.
    """
    def __init__(self, value=None):
        c_void_p.__init__(self)
        self.value = value

    def value_set(self, value):
        oldv = getattr(self, 'value', None)
        if oldv is not None:
            mz.scheme_gc_ptr_ok(oldv)
        if value is not None:
            mz.scheme_dont_gc_ptr(value)
        return c_void_p.value.__set__(self, value)
    def value_get(self):
        return c_void_p.value.__get__(self)
    value = property(value_get, value_set)

    def __del__(self):
        if mz is None:
            return # the mz library has been unloaded, do nothing
        # We should be careful here in __del__, originally my code
        # of 'self.value' is firing some exceptions saying that
        # NoneType has no 'value' attribute.
        value = getattr(self, 'value', None)
        if value is not None:
            mz.scheme_gc_ptr_ok(value)
    
    def __str__(self):
        return "<SCM %s>" % self.value
    def __repr__(self):
        return self.__str__()

from _ctypes import Py_INCREF, Py_DECREF, PyObj_FromPtr
def PyObj_del(scm):
    """\
    The finalizer of PyObj. Decrease the ref-count of
    the referenced Python object here.
    """
    Py_DECREF(PyObj_FromPtr(PyObj.pointer(scm)))
PyObj_finalizer_cfun = CFUNCTION(None, c_void_p)
PyObj_finalizer = PyObj_finalizer_cfun(PyObj_del)
    
class PyObj(SCM):
    """\
    A mzscheme type holding Python value.
    """
    @staticmethod
    def pointer(scm):
        "The the id of the referenced Python Object."
        return mz.PyObj_id(scm)

    @staticmethod
    def get(scm):
        "Return the referenced Python Object."
        return PyObj_FromPtr(mz.PyObj_id(scm))

    @staticmethod
    def new(obj):
        """\
        Create a new PyObj with reference to obj.
        """
        PY_INCREF(obj)
        pointer = id(obj)
        return mz.PyObj_create(pointer, PyObj_finalizer)

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
        code = str(code)
        port = mz.scheme_make_sized_byte_string_input_port(code, len(code))
        sexp = mz.scheme_read(port)
        return mz.scheme_compile(sexp, global_env, False)

    def eval(self, code):
        """\
        eval the compiled code for mzscheme.
        """
        return mz.scheme_eval_compiled(code, global_env)

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
        if type(val) is complex:
            return mz.scheme_make_complex(self.toscheme(val.real),
                                          self.toscheme(val.imag))
        if type(val) is str:
            return mz.scheme_make_sized_byte_string(val, len(val), True)
        if type(val) is unicode:
            try:
                s = str(val)
                return mz.scm_make_sized_byte_string(s, len(s), True)
            except UnicodeEncodeError:
                pass
        return PyObj.new(val)
        
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
        if mz.scheme_byte_string_p(val):
            mem = mz.scheme_byte_string_val(val)
            length = mz.scheme_byte_string_len(val)
            return string_at(mem, length)
        if mz.scheme_char_string_p(val):
            return self.fromscheme(mz.scheme_char_string_to_byte_string_locale(val))
        if mz.PyObj_p(val):
            return PyObj.get(val)

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
        if mz.scheme_byte_string_p(val):
            return str
        if mz.scheme_char_string_p(val):
            return str
        if mz.PyObj_p(val):
            return object

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
mz.scheme_char_string_p = _mzhelper.scheme_char_string_p
mz.scheme_byte_string_p = _mzhelper.scheme_byte_string_p
mz.scheme_byte_string_val = _mzhelper.scheme_byte_string_val
mz.scheme_byte_string_len = _mzhelper.scheme_byte_string_len

# helpers
mz.PyObj_create = _mzhelper.PyObj_create
mz.PyObj_p = _mzhelper.PyObj_p
mz.PyObj_id = _mzhelper.PyObj_id

# constructors
mz.scheme_make_integer_value.argtypes = [c_int]
mz.scheme_make_integer_value.restype = SCM
mz.scheme_make_double.argtypes = [c_double]
mz.scheme_make_double.restype = SCM
mz.scheme_char_string_to_byte_string_locale.argtypes = [SCM]
mz.scheme_char_string_to_byte_string_locale.restype = SCM
mz.scheme_make_sized_byte_string_input_port.argtypes = [c_char_p, c_int]
mz.scheme_make_sized_byte_string_input_port.restype = SCM
mz.scheme_make_sized_byte_string.argteyps = [c_char_p, c_int, c_int]
mz.scheme_make_sized_byte_string.restype = SCM

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
mz.scheme_make_complex.argtypes = [SCM, SCM]
mz.scheme_make_complex.restype = SCM
mz.scheme_byte_string_val.argtypes = [SCM]
mz.scheme_byte_string_val.restype = c_void_p
mz.scheme_byte_string_len.argtypes = [SCM]
mz.scheme_byte_string_len.restype = c_int

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
mz.scheme_byte_string_p.argtypes = [SCM]
mz.scheme_byte_string_p.restype = c_int
mz.scheme_char_string_p.argtypes = [SCM]
mz.scheme_char_string_p.restype = c_int

# Helper
mz.scheme_eval_string.argtypes = [c_char_p, SCM]
mz.scheme_eval_string.restype = SCM
mz.scheme_read.argteyps = [SCM]
mz.scheme_read.restype = SCM
mz.scheme_compile.argtypes = [SCM, SCM, c_int]
mz.scheme_compile.restype = SCM
mz.scheme_eval_compiled.argtypes = [SCM, SCM]
mz.scheme_eval_compiled.restype = SCM
mz.scheme_gc_ptr_ok.argtypes = [SCM]
mz.scheme_dont_gc_ptr.argtypes = [SCM]

mz.PyObj_create.argtypes = [c_uint, PyObj_finalizer_cfun]
mz.PyObj_create.restype = PyObj
mz.PyObj_p.argtypes = [SCM]
mz.PyObj_p.restype = c_int
mz.PyObj_id.argtypes = [SCM]
mz.PyObj_id.restype = c_uint
