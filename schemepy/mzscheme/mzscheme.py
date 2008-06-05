from ctypes.util import find_library
from ctypes import *
from schemepy.types import *
from schemepy import exceptions
import types
import os.path

lib = find_library("mzscheme3m")
if lib is None:
    raise RuntimeError("Can't find a mzscheme library to use.")

mz = cdll.LoadLibrary(lib)

# Load the helper library which exports the macro's as C functions
path = os.path.abspath(os.path.join(os.path.split(__file__)[0], '_mzhelper.so'))
_mzhelper = cdll.LoadLibrary(path)

class SCM(c_void_p):
    """\
    Corresponding to the type Scheme_Object * in C.
    """
    pass

class SCMRef(object):
    """\
    Hold a Scheme_Object * value.

    If the value is immediate integer value embedded in the pointer, hold it drectly.
    Otherwise, use a immobile to hold it indrectly to survive the memory-moving GC
    of mzscheme.
    """
    def __init__(self, value):
        """\
        Create a SCM referencing to the Scheme value.
        """
        self._indirect = False
        self._value = None
        self.value = value

    def value_set(self, value):
        if self._value is not None and self._indirect:
            mz.scheme_free_immobile_box(self._value)
        if value is not None:
            if mz.scheme_immediate_p(value):
                self._indirect = False
                self._value = value
            else:
                self._indirect = True
                self._value = mz.scheme_malloc_immobile_box(value)
    def value_get(self):
        if self._indirect:
            return self._value[0].value
        return self._value
    value = property(value_get, value_set, "The underlying Scheme value")

    @classmethod
    def from_param(cls, obj):
        "Used by ctypes"
        if not isinstance(obj, SCMRef):
            raise ArgumentError("Expecting a SCMRef but got a %s" % obj)
        return obj.value

    def __del__(self):
        """\
        When this object is released by the Python GC. Also release the
        referencing Scheme Object so that it can be collected by the
        mzscheme GC later.
        """
        if mz is None:
            return # mz library has been unloaded, do nothing
        if self._indirect and self._value is not None:
            mz.scheme_free_immobile_box(self._value)
            
    def __str__(self):
        if self._indirect:
            return "<SCM => @%x>" % self._value[0].value
        return "<SCM @%x>" % self._value
    def __repr__(self):
        return self.__str__()
                
from _ctypes import Py_INCREF, Py_DECREF, PyObj_FromPtr
def PyObj_del(scm):
    """\
    The finalizer of PyObj. Decrease the ref-count of
    the referenced Python object here.
    """
    Py_DECREF(PyObj_FromPtr(PyObj.pointer(SCMRef(scm))))
PyObj_finalizer_cfun = CFUNCTYPE(None, c_void_p)
PyObj_finalizer = PyObj_finalizer_cfun(PyObj_del)
    
class PyObj(object):
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

    profiles = {
        "scheme-report-environment" : "(scheme-report-environment 5)",
        "null-environment" : "(null-environment 5)"
        }
    def __init__(self, profile):
        """\
        Create a VM.
        """
        env = VM.profiles.get(profile, None)
        if not env:
            raise ProfileNotFoundError("No such profile %s" % profile)
        self._module = mz.scheme_eval_string(env, global_env_ref)

    def ensure_namespace(meth):
        """\
        Set the current namespace parameter before calling methods.
        """
        def decorated_meth(self, *args, **kw):
            mz.set_current_namespace(self._module)
            return meth(self, *args, **kw)
        return decorated_meth

    def filter_exception(meth):
        """\
        The decorator parse the return value of catched function calls,
        raise exceptions when necessary and return the filtered value
        otherwise.
        """
        def filtered_meth(self, *args, **kw):
            rlt = meth(self, *args, **kw)
            if self.fromscheme(mz.scheme_pair_car(rlt)) is True:
                return mz.scheme_pair_cdr(rlt)
            excp = mz.scheme_pair_cdr(rlt)
            ex_name = self.fromscheme(mz.scheme_pair_car(excp))
            ex_msg =  self.fromscheme(mz.scheme_pair_cdr(excp))
            raise getattr(exceptions, ex_name)(ex_msg)
        return filtered_meth
        
    def define(self, name, value):
        """\
        Define a variable in Scheme. Similar to Scheme code
          (define name value)

          name can either be a string or a schemepy.types.Symbol
          value should be a Scheme value
        """
        if not isinstance(value, SCMRef):
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

    @ensure_namespace
    @filter_exception
    def compile(self, code):
        """\
        Compile for mzscheme.
        """
        return mz.catched_scheme_compile(code, len(code), self._module)

    @ensure_namespace
    @filter_exception
    def apply(self, proc, args):
        """\
        Call the Scheme procedure proc with args as arguments.

          proc should be a Scheme procedure
          args should be a list os Scheme value

        The return value is a Scheme value.
        """
        arglist = mz.scheme_null_ref
        for arg in reversed(args):
            arglist = mz.scheme_make_pair(arg, arglist)

        return mz.catched_scheme_apply(proc, arglist)

    @ensure_namespace
    @filter_exception
    def eval(self, code):
        """\
        eval the compiled code for mzscheme.
        """
        return mz.catched_scheme_eval(code, self._module)

    @ensure_namespace
    def repl(self):
        """\
        Enter a read-eval-print-loop
        """
        mz.scheme_apply(mz.scheme_builtin_value("read-eval-print-loop"), 0, None)

    def toscheme(self, val, shallow=False):
        "Convert a Python value to a Scheme value."
        if type(val) is bool:
            if val is True:
                return mz.scheme_true_ref
            return mz.scheme_false_ref
        if type(val) is int:
            return mz.scheme_make_integer_value(val)
        if type(val) is long:
            return mz.scheme_eval_string(str(val), self._module)
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
            scm = mz.scheme_null_ref
            for item in reversed(val):
                if shallow:
                    if not isinstance(item, SCM):
                        raise ConversionError(val, "Invalid shallow conversion on list, every element should be a Scheme value.")
                    scm = mz.scheme_make_pair(item, scm)
                else:
                    scm = mz.scheme_make_pair(self.toscheme(item), scm)
            return scm
        if isinstance(val, dict):
            scm = mz.scheme_null_ref
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
        if not isinstance(val, SCMRef):
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
        if mz.scheme_list_p(val):
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
        raise ConversionError(self, "Don't know how to convert this type.")

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
        if mz.scheme_list_p(val):
            if mz.scheme_alist_p(val):
                return dict
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

import init_mz
init_mz.setup_ctypes(mz, _mzhelper, SCM, SCMRef)

mz.scheme_null_ref = SCMRef(mz.scheme_null)
mz.scheme_false_ref = SCMRef(mz.scheme_false)
mz.scheme_true_ref = SCMRef(mz.scheme_true)
global_env_ref = SCMRef(global_env)


mz.PyObj_create.argtypes = [c_uint, PyObj_finalizer_cfun]
mz.PyObj_create.restype = SCMRef
mz.PyObj_p.argtypes = [SCMRef]
mz.PyObj_p.restype = c_int
mz.PyObj_id.argtypes = [SCMRef]
mz.PyObj_id.restype = c_uint

mz.scheme_get_proc_name.argtypes = [SCMRef]
mz.scheme_get_proc_name.restype = SCMRef

def scm_py_call_func(narg, arg):
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
    
    vm = PyObj.get(SCMRef(vm))
    py_callable, shallow = vm.fromscheme(SCMRef(py_callable)), vm.fromscheme(SCMRef(shallow))
    args = vm.fromscheme(SCMRef(scm_args), shallow=shallow)
    result = py_callable(*args)
    if not shallow:
        result = vm.toscheme(result)
    else:
        if not isinstance(result, SCMRef):
            # TODO: is it safe to raise exception in a C handler
            raise TypeError("Return type is not a SCM!")
    return result.value

scm_py_call_t = CFUNCTYPE(SCM, c_int, POINTER(SCM))
scm_py_call_proc = scm_py_call_t(scm_py_call_func)

mz.init_scm_py_call.argtypes = [scm_py_call_t]
mz.init_scm_py_call.restype = SCMRef

scm_py_call = mz.init_scm_py_call(scm_py_call_proc)

scm_py_call_identifier = Symbol("schemepy-python-callable")
scm_py_call_extractor = Symbol("schemepy-python-get-callable")
scm_lambda_wrapper = SCMRef(SCM.in_dll(_mzhelper, "scm_lambda_wrapper"))
