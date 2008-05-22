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


_mzhelper.init_mz()
global_env = SCM.in_dll(_mzhelper, "global_env")

mz.scheme_eval_string.argtypes = [c_char_p, SCM]
mz.scheme_eval_string.restype = SCM
