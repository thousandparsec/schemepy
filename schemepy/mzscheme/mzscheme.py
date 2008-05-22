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

    def fromscheme(self, val, shallow=False):
        "Get a Python value from a Scheme value."
        if not isinstance(val, SCM):
            raise ArgumentError("Expecting a Scheme value, but get a %s." % val)

        if mz.scheme_bool_p(val):
            if mz.scheme_false_p(val):
                return False
            return True

_mzhelper.init_mz()
global_env = SCM.in_dll(_mzhelper, "global_env")

# global constants
mz.scheme_true = SCM.in_dll(mz, "scheme_true")
mz.scheme_false = SCM.in_dll(mz, "scheme_false")

# macros
mz.scheme_bool_p = _mzhelper.scheme_bool_p
mz.scheme_false_p = _mzhelper.scheme_false_p

# Predicts
mz.scheme_bool_p.argtypes = [SCM]
mz.scheme_bool_p.restype = int
mz.scheme_false_p.argtypes = [SCM]
mz.scheme_false_p.restype = int

mz.scheme_eval_string.argtypes = [c_char_p, SCM]
mz.scheme_eval_string.restype = SCM
