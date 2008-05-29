from ctypes.util import find_library
from ctypes import *
from schemepy.types import *
from schemepy.exceptions import *
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
PyObj_finalizer_cfun = CFUNCTYPE(None, c_void_p)
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
        Py_INCREF(obj)
        pointer = id(obj)
        return mz.PyObj_create(pointer, PyObj_finalizer)

class VM(object):
    """VM for mzscheme
    """

    module_number = 0
    @staticmethod
    def next_module_name():
        VM.module_number += 1
        return "schemepy-vm-module-%d" % VM.module_number
    
    def __init__(self, profile):
        """\
        Create a VM.
        """
        name = VM.next_module_name()
        name = mz.scheme_intern_exact_symbol(name.encode('utf-8'), len(name))
        self._module = mz.scheme_primitive_module(name, global_env)
        # TODO: deal with profile

    def define(self, name, value):
        """\
        Define a variable in Scheme. Similar to Scheme code
          (define name value)

          name can either be a string or a schemepy.types.Symbol
          value should be a Scheme value
        """
        if not isinstance(value, SCM):
            raise TypeError, "Value to define should be a Scheme value."
        name = Symbol(name)
        mz.scheme_add_global_symbol(self.toscheme(name), value, self._module)

    def get(self, name, default=None):
        """\
        Get the value bound to the symbol.

          name can either be a string or a schemepy.types.Symbol
        """
        name = Symbol(name)
        val = mz.scheme_lookup_global(self.toscheme(name), self._module)
        if val.value is None:
            return default
        return val

    def compile(self, code):
        """\
        Compile for mzscheme.
        """
        code = str(code)
        port = mz.scheme_make_sized_byte_string_input_port(code, len(code))
        sexp = mz.scheme_read(port)
        return mz.scheme_compile(sexp, global_env, False)

    def apply(self, proc, args):
        """\
        Call the Scheme procedure proc with args as arguments.

          proc should be a Scheme procedure
          args should be a list os Scheme value

        The return value is a Scheme value.
        """
        arglist = mz.scheme_null
        for arg in reversed(args):
            arglist = mz.scheme_make_pair(arg, arglist)

        return mz.scheme_apply_to_list(proc, arglist)
        
    def eval(self, code):
        """\
        eval the compiled code for mzscheme.
        """
        return mz.scheme_eval_compiled(code, self._module)

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
                return mz.scheme_make_sized_byte_string(s, len(s), True)
            except UnicodeEncodeError:
                pass
        if type(val) is Symbol:
            return mz.scheme_intern_exact_symbol(val.name.encode('utf-8'), len(val.name))
        if type(val) is Cons:
            if shallow:
                if not isinstance(val.car, SCM) or not isinstance(val.cdr, SCM):
                    raise ConversionError(val, "Invalid shallow conversion on Cons, both car and cdr should be a Scheme value.")
                return mz.scheme_make_pair(val.car, val.cdr)
            return mz.scheme_make_pair(self.toscheme(val.car), self.toscheme(val.cdr))
        if isinstance(val, list):
            scm = mz.scheme_null
            for item in reversed(val):
                if shallow:
                    if not isinstance(item, SCM):
                        raise ConversionError(val, "Invalid shallow conversion on list, every element should be a Scheme value.")
                    scm = mz.scheme_make_pair(item, scm)
                else:
                    scm = mz.scheme_make_pair(self.toscheme(item), scm)
            return scm
        if isinstance(val, dict):
            scm = mz.scheme_null
            for key, value in val.iteritems():
                if shallow:
                    if not isinstance(item, SCM):
                        raise ConversionError(val, "Invalid shallow conversion on dict, every value should be a Scheme value.")
                    scm = mz.scheme_make_pair(mz.scheme_make_pair(self.toscheme(key), value), scm)
                else:
                    scm = mz.scheme_make_pair(mz.scheme_make_pair(self.toscheme(key), self.toscheme(value)), scm)
            return scm
        if type(val) is Lambda:
            return val._lambda
        if callable(val):
            scm_proc = PyObj.new(val)
            return self.apply(scm_lambda_wrapper, [scm_py_call,
                                                   scm_proc,
                                                   self.toscheme(shallow),
                                                   self.toscheme(self)])
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
        if mz.scheme_symbol_p(val):
            mem = mz.scheme_symbol_val(val)
            length = mz.scheme_symbol_len(val)
            return Symbol(string_at(mem, length))
        if mz.scheme_null_p(val):
            return []
        if mz.scheme_alist_p(val):
            d = {}
            scm = val
            while not mz.scheme_null_p(scm):
                item = mz.scheme_pair_car(scm)
                key = self.fromscheme(mz.scheme_pair_car(item))
                value = mz.scheme_pair_cdr(item)
                if not shallow:
                    d[key] = self.fromscheme(value)
                else:
                    d[key] = value
                scm = mz.scheme_pair_cdr(scm)
            return d
        if mz.scheme_list_p(val):
            l = []
            scm = val
            while not mz.scheme_null_p(scm):
                item = mz.scheme_pair_car(scm)
                if not shallow:
                    l.append(self.fromscheme(item))
                else:
                    l.append(item)
                scm = mz.scheme_pair_cdr(scm)
            return l
        if mz.scheme_pair_p(val):
            car = mz.scheme_pair_car(val)
            cdr = mz.scheme_pair_cdr(val)
            if not shallow:
                return Cons(self.fromscheme(car), self.fromscheme(cdr))
            else:
                return Cons(car, cdr)
        if mz.scheme_procedure_p(val):
            if self.fromscheme(mz.scheme_get_proc_name(val)) == scm_py_call_identifier:
                return PyObj.get(self.apply(val, [self.toscheme(scm_py_call_extractor)]))
            return Lambda(val, self, shallow)
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
        if mz.scheme_symbol_p(val):
            return Symbol
        if mz.scheme_null_p(val):
            return list
        if mz.scheme_alist_p(val):
            return dict
        if mz.scheme_list_p(val):
            return list
        if mz.scheme_pair_p(val):
            return Cons
        if mz.scheme_procedure_p(val):
            if self.fromscheme(mz.scheme_get_proc_name(val)) == scm_py_call_identifier:
                return types.FunctionType
            return Lambda
        if mz.PyObj_p(val):
            return object
        

_mzhelper.init_mz()
global_env = SCM.in_dll(_mzhelper, "global_env")

# global constants
mz.scheme_true = SCM.in_dll(_mzhelper, "_scheme_true")
mz.scheme_false = SCM.in_dll(_mzhelper, "_scheme_false")
mz.scheme_null = SCM.in_dll(_mzhelper, "_scheme_null")

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
mz.scheme_symbol_p = _mzhelper.scheme_symbol_p
mz.scheme_symbol_val = _mzhelper.scheme_symbol_val
mz.scheme_symbol_len = _mzhelper.scheme_symbol_len
mz.scheme_pair_p = _mzhelper.scheme_pair_p
mz.scheme_pair_car = _mzhelper.scheme_pair_car
mz.scheme_pair_cdr = _mzhelper.scheme_pair_cdr
mz.scheme_null_p = _mzhelper.scheme_null_p
mz.scheme_procedure_p = _mzhelper.scheme_procedure_p

# helpers
mz.PyObj_create = _mzhelper.PyObj_create
mz.PyObj_p = _mzhelper.PyObj_p
mz.PyObj_id = _mzhelper.PyObj_id
mz.scheme_list_p = _mzhelper.scheme_list_p
mz.scheme_alist_p = _mzhelper.scheme_alist_p
mz.scheme_get_proc_name = _mzhelper._scheme_get_proc_name

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
mz.scheme_intern_exact_symbol.argtypes = [c_char_p, c_int]
mz.scheme_intern_exact_symbol.restype = SCM
mz.scheme_make_pair.argtypes = [SCM, SCM]
mz.scheme_make_pair.restype = SCM

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
mz.scheme_symbol_val.argtypes = [SCM]
mz.scheme_symbol_val.restype = c_void_p
mz.scheme_symbol_len.argtypes = [SCM]
mz.scheme_symbol_len.restype = c_int
mz.scheme_pair_car.argtypes = [SCM]
mz.scheme_pair_car.restype = SCM
mz.scheme_pair_cdr.argtypes = [SCM]
mz.scheme_pair_cdr.restype = SCM


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
mz.scheme_symbol_p.argtypes = [SCM]
mz.scheme_symbol_p.restype = c_int
mz.scheme_pair_p.argtypes = [SCM]
mz.scheme_pair_p.restype = c_int
mz.scheme_list_p.argtypes = [SCM]
mz.scheme_list_p.restype = c_int
mz.scheme_alist_p.argtypes = [SCM]
mz.scheme_alist_p.restype = c_int
mz.scheme_null_p.argtypes = [SCM]
mz.scheme_null_p.restype = c_int
mz.scheme_procedure_p.argtypes = [SCM]
mz.scheme_procedure_p.restype = c_int

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
mz.scheme_apply_to_list.argtypes = [SCM, SCM]
mz.scheme_apply_to_list.restype = SCM
mz.scheme_primitive_module.argtypes = [SCM, SCM]
mz.scheme_primitive_module.restype = SCM
mz.scheme_finish_primitive_module.argtypes = [SCM]
mz.scheme_finish_primitive_module.restype = None
mz.scheme_lookup_global.argtypes = [SCM, SCM]
mz.scheme_lookup_global.restype = SCM
mz.scheme_add_global_symbol.argtypes = [SCM, SCM, SCM]
mz.scheme_add_global_symbol.restype = None

mz.PyObj_create.argtypes = [c_uint, PyObj_finalizer_cfun]
mz.PyObj_create.restype = PyObj
mz.PyObj_p.argtypes = [SCM]
mz.PyObj_p.restype = c_int
mz.PyObj_id.argtypes = [SCM]
mz.PyObj_id.restype = c_uint

mz.scheme_get_proc_name.argtypes = [SCM]
mz.scheme_get_proc_name.restype = SCM

def scm_py_call(narg, arg):
    """\
    This function will be registered to the Scheme world to call a Python
    callable.
    
    py_callable is a Python callable, wrapped as a SMOB in Scheme world.
    shallow     is whether the wrap is shallow, i.e. the args and return values
                will be auto-converted if not shallow.
    vm          is the vm in which to call the function.
    scm_args    is a Scheme cons-list for the function.

    This function will not be available to normal Scheme code.
    """
    if narg != 4:
        # TODO: is it safe to raise exception in a C handler?
        raise TypeError("scm_py_call takes exactly 4 arguments.")
    py_callable = arg[0]
    shallow     = arg[1]
    vm          = arg[2]
    scm_args    = arg[3]
    
    vm = PyObj.get(vm)
    py_callable, shallow = vm.fromscheme(py_callable), vm.fromscheme(shallow)
    args = vm.fromscheme(scm_args, shallow=shallow)
    result = py_callable(*args)
    if not shallow:
        result = vm.toscheme(result)
    else:
        if not isinstance(result, SCM):
            # TODO: is it safe to raise exception in a C handler
            raise TypeError("Return type is not a SCM!")
    return result.value

scm_py_call_t = CFUNCTYPE(SCM, c_int, POINTER(SCM))
scm_py_call = scm_py_call_t(scm_py_call)

mz.scheme_make_prim_w_arity.argtypes = [scm_py_call_t, c_char_p, c_int, c_int]
mz.scheme_make_prim_w_arity.restype = SCM

scm_py_call = mz.scheme_make_prim_w_arity(scm_py_call, "schemepy-py-call", 4, 4)

scm_py_call_identifier = Symbol("schemepy-python-callable")
scm_py_call_extractor = Symbol("schemepy-python-get-callable")
scm_lambda_wrapper = mz.scheme_eval_string("""
            (lambda (call-py py-callable shallow vm)
              ; this will infer mzscheme to name the lambda
              ; by `schemepy-python-callable'
              (let ((schemepy-python-callable
                      (case-lambda
                        [(x)
                          (if (eq? x 'schemepy-python-get-callable)
                              py-callable
                            (call-py py-callable shallow vm (list x)))]
                        [args
                          (call-py py-callable shallow vm args)])))
                schemepy-python-callable))""", global_env)
