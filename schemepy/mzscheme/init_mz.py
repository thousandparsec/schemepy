from ctypes import *

def setup_ctypes(mz, _mzhelper, SCM, SCMRef):
    # macros
    mz.scheme_immediate_p = _mzhelper.scheme_immediate_p
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
    
    # global constants
    mz.scheme_true = SCM.in_dll(_mzhelper, "_scheme_true")
    mz.scheme_false = SCM.in_dll(_mzhelper, "_scheme_false")
    mz.scheme_null = SCM.in_dll(_mzhelper, "_scheme_null")
    
    # helpers
    mz.PyObj_create = _mzhelper.PyObj_create
    mz.PyObj_p = _mzhelper.PyObj_p
    mz.PyObj_id = _mzhelper.PyObj_id
    mz.scheme_list_p = _mzhelper.scheme_list_p
    mz.scheme_alist_p = _mzhelper.scheme_alist_p
    mz.scheme_get_proc_name = _mzhelper._scheme_get_proc_name
    
    mz.set_current_namespace = _mzhelper.set_current_namespace
    
    mz.catched_scheme_compile = _mzhelper.catched_scheme_compile
    mz.catched_scheme_eval = _mzhelper.catched_scheme_eval
    mz.catched_scheme_apply = _mzhelper.catched_scheme_apply
    
    mz.init_scm_py_call = _mzhelper.init_scm_py_call
    
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
    mz.scheme_pair_car.argtypes = [SCMRef]
    mz.scheme_pair_car.restype = SCMRef
    mz.scheme_pair_cdr.argtypes = [SCMRef]
    mz.scheme_pair_cdr.restype = SCMRef
    
    
    # Predicts
    mz.scheme_immediate_p.argtypes = [SCM]
    mz.scheme_immediate_p.restype = c_int
    mz.scheme_bool_p.argtypes = [SCMRef]
    mz.scheme_bool_p.restype = c_int
    mz.scheme_false_p.argtypes = [SCMRef]
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
    mz.scheme_eval_string.argtypes = [c_char_p, SCMRef]
    mz.scheme_eval_string.restype = SCMRef
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
    mz.scheme_make_namespace.argtypes = [c_int, c_void_p]
    mz.scheme_make_namespace.restype = SCM
    mz.scheme_lookup_global.argtypes = [SCM, SCM]
    mz.scheme_lookup_global.restype = SCM
    mz.scheme_add_global_symbol.argtypes = [SCM, SCM, SCM]
    mz.scheme_add_global_symbol.restype = None
    
    mz.scheme_free_immobile_box.argtypes = [POINTER(SCM)]
    mz.scheme_free_immobile_box.restype = None
    mz.scheme_malloc_immobile_box.argtypes = [SCM]
    mz.scheme_malloc_immobile_box.restype = POINTER(SCM)
    
    mz.set_current_namespace.argtypes = [SCMRef]
    mz.set_current_namespace.restype = None
    
    mz.catched_scheme_compile.argtypes = [c_char_p, c_int, SCMRef]
    mz.catched_scheme_compile.restype = SCMRef
    mz.catched_scheme_eval.argtypes = [SCMRef, SCMRef]
    mz.catched_scheme_eval.restype = SCMRef
    mz.catched_scheme_apply.argtypes = [SCMRef, SCMRef]
    mz.catched_scheme_apply.restype = SCMRef
    
