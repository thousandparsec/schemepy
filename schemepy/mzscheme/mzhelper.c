#include "scheme.h"

Scheme_Env *global_env;

/**
 * It's strange that constants from mzscheme.so is different
 * from what's seen from this library (from the header file). And
 * since value seen from this library consists with the eval-ed
 * values (i.e. scheme_eval_string("#t", env)), we'll use constants
 * from here.
 */
Scheme_Object *_scheme_true;
Scheme_Object *_scheme_false;
Scheme_Object *_scheme_null;

/**
 * Used to catch exceptions
 */
static const char *catched_apply_proc_code = \
    "(lambda (proc . args)"
    "  (with-handlers"
    "   ([exn:fail:read?"
    "     (lambda (exn) (cons #f (cons \"ScmSyntaxError\" (exn-message exn))))]"
    "    [exn:fail:syntax?"
    "     (lambda (exn) (cons #f (cons \"ScmSyntaxError\" (exn-message exn))))]"
    "    [exn:fail:contract:variable?"
    "     (lambda (exn) (cons #f (cons \"ScmUnboundVariable\" (exn-message exn))))]"
    "    [exn:fail:contract:arity?"
    "     (lambda (exn) (cons #f (cons \"ScmWrongArgNumber\" (exn-message exn))))]"
    "    [exn:fail:contract?"
    "     (lambda (exn) (cons #f (cons \"ScmWrongArgType\" (exn-message exn))))]"
    "    [exn:fail:contract:divide-by-zero?"
    "     (lambda (exn) (cons #f (cons \"ScmNumericalError\" (exn-message exn))))]"
    "    [exn:fail:filesystem?"
    "     (lambda (exn) (cons #f (cons \"ScmSystemError\" (exn-message exn))))]"
    "    [exn:fail:network?"
    "     (lambda (exn) (cons #f (cons \"ScmSystemError\" (exn-message exn))))]"
    "    [exn:fail:out-of-memory?"
    "     (lambda (exn) (cons #f (cons \"ScmSystemError\" (exn-message exn))))]"
    "    [exn:fail?"
    "     (lambda (exn) (cons #f (cons \"ScmMiscError\" (exn-message exn))))])"
    "   (cons #t (apply proc args))))";
static Scheme_Object *proc_scheme_compile;
static Scheme_Object *proc_scheme_eval;
static Scheme_Object *proc_scheme_apply;

static Scheme_Object *do_compile(int argc, Scheme_Object **argv);
static Scheme_Object *do_eval(int argc, Scheme_Object **argv);
static Scheme_Object *do_apply(int argc, Scheme_Object **argv);

/**
 * A mzscheme type to hold Python object
 */
Scheme_Type PyObj_type;
typedef struct PyObj_t
{
    Scheme_Object header;
    unsigned int id;           /* the Python object id */
} PyObj;
/**
 * Create a PyObj reference to a Python object. The id
 * of the Python object is passed as parameter. Besides,
 * a function is passed as the finalizer of this reference.
 *
 * NOTE:
 * the reference count if the Python object is not incremented
 * here, it should be increased in Python before passing the
 * id here.
 */
PyObj *PyObj_create(unsigned int id, void (*finalizer)(void *p))
{
    PyObj *obj = (PyObj *)scheme_malloc(sizeof(PyObj));
    obj->header.type = PyObj_type;
    obj->id = id;
    scheme_register_finalizer(obj, (void (*)(void *, void *))finalizer,
                              NULL, NULL, NULL);
    return obj;
}
int PyObj_p(Scheme_Object *o)
{
    return o->type == PyObj_type;
}
unsigned PyObj_id(Scheme_Object *o)
{
    return ((PyObj *)o)->id;
}

void init_mz()
{
    scheme_set_stack_base(NULL, 1); /* required for OS X, only */
    global_env = scheme_basic_env();

    _scheme_true = scheme_true;
    _scheme_false = scheme_false;
    _scheme_null = scheme_null;

    PyObj_type = scheme_make_type("Python Object");

    proc_scheme_compile = scheme_make_prim_w_arity(do_compile, "schemepy-do-compile", 2, 2);
    proc_scheme_eval = scheme_make_prim_w_arity(do_eval, "schemepy-do-eval", 2, 2);
    proc_scheme_apply = scheme_make_prim_w_arity(do_apply, "schemepy-do-apply", 2, 2);
}

Scheme_Object *init_catched_apply_proc(Scheme_Env *namespace)
{
    return scheme_eval_string(catched_apply_proc_code, namespace);
}

int scheme_bool_p(Scheme_Object *o)
{
    return SCHEME_BOOLP(o);
}
int scheme_false_p(Scheme_Object *o)
{
    return SCHEME_FALSEP(o);
}

/**
 * Number type mapping:
 *
 *    Mz              Py
 * --------       ---------
 * fixnum         int
 * double         float
 * float          float
 * rational       float
 * bignum         long
 * complex        complex
 */

int scheme_fixnum_p(Scheme_Object *o)
{
    return SCHEME_INTP(o);
}
int scheme_fixnum_value(Scheme_Object *o)
{
    return SCHEME_INT_VAL(o);
}

int scheme_bignum_p(Scheme_Object *o)
{
    return SCHEME_BIGNUMP(o);
}

int scheme_real_p(Scheme_Object *o)
{
    return SCHEME_REALP(o) && ! SCHEME_COMPLEX_IZIP(o);
}
double scheme_real_value(Scheme_Object *o)
{
    if (SCHEME_RATIONALP(o))
        return scheme_rational_to_double(o);
    if (SCHEME_DBLP(o))
        return SCHEME_DBL_VAL(o);
    return SCHEME_FLOAT_VAL(o);
}

int scheme_number_p(Scheme_Object *o)
{
    return SCHEME_NUMBERP(o);
}


int scheme_char_string_p(Scheme_Object *o)
{
    return SCHEME_CHAR_STRINGP(o);
}
int scheme_byte_string_p(Scheme_Object *o)
{
    return SCHEME_BYTE_STRINGP(o);
}
char *scheme_byte_string_val(Scheme_Object *o)
{
    return SCHEME_BYTE_STR_VAL(o);
}
int scheme_byte_string_len(Scheme_Object *o)
{
    return SCHEME_BYTE_STRLEN_VAL(o);
}

int scheme_symbol_p(Scheme_Object *o)
{
    return SCHEME_SYMBOLP(o);
}
char *scheme_symbol_val(Scheme_Object *o)
{
    return SCHEME_SYM_VAL(o);
}
int scheme_symbol_len(Scheme_Object *o)
{
    return SCHEME_SYM_LEN(o);
}

int scheme_null_p(Scheme_Object *o)
{
    return SCHEME_NULLP(o);
}
int scheme_pair_p(Scheme_Object *o)
{
    return SCHEME_PAIRP(o);
}
Scheme_Object *scheme_pair_car(Scheme_Object *o)
{
    return SCHEME_CAR(o);
}
Scheme_Object *scheme_pair_cdr(Scheme_Object *o)
{
    return SCHEME_CDR(o);
}
int scheme_list_p(Scheme_Object *o)
{
    while (1)
    {
        if (SCHEME_NULLP(o))
            return 1;
        if (!SCHEME_PAIRP(o))
            return 0;
        o = SCHEME_CDR(o);
    }
    return 0; /* should reach here */
}
int scheme_alist_p(Scheme_Object *o)
{
    while (1)
    {
        if (SCHEME_NULLP(o))
            return 1;
        if (!SCHEME_PAIRP(o))
            return 0;
        if (!SCHEME_PAIRP(SCHEME_CAR(o)))
            return 0;
        o = SCHEME_CDR(o);
    }
}

int scheme_procedure_p(Scheme_Object *o)
{
    return SCHEME_PROCP(o);
}

Scheme_Object *_scheme_get_proc_name(Scheme_Object *o)
{
    const char *s;
    int len;
    s = scheme_get_proc_name(o, &len, -1);
    if (s)
    {
        if (len < 0)
            return (Scheme_Object *)s;
        else
            return scheme_intern_exact_symbol(s, len);
    }
    return _scheme_false;
}

/**
 * Those procedures are wrapper of the mzscheme procedures
 * that call with exception handler. The return value of
 * each function is a cons. When the action success without
 * exception, the return value is
 *
 *   (#t . result)
 *
 * otherwise, the return value is
 *
 *   (#f . (ExceptionName . parameter))
 *
 */
static Scheme_Object *do_compile(int argc, Scheme_Object **argv)
{
    Scheme_Object *sexp = scheme_read((Scheme_Object *)argv[0]);
    return scheme_compile(sexp, (Scheme_Env *)argv[1], 0);
}  
Scheme_Object *catched_scheme_compile(char *code, int len, Scheme_Object *env, Scheme_Object *catched_apply_proc)
{
    Scheme_Object *params[3];
    Scheme_Object *port = scheme_make_sized_byte_string_input_port(code, len);
    Scheme_Object *result;

    params[0] = proc_scheme_compile;
    params[1] = port;
    params[2] = env;
    result = scheme_apply(catched_apply_proc, 3, params);

    scheme_close_input_port(port);
    return result;
}
static Scheme_Object *do_eval(int argc, Scheme_Object **argv)
{
    Scheme_Object *compiled = argv[0];
    Scheme_Env *env = (Scheme_Env *)argv[1];
    return scheme_eval_compiled(compiled, env);
}
Scheme_Object *catched_scheme_eval(Scheme_Object *compiled, Scheme_Env *env, Scheme_Object *catched_apply_proc)
{
    Scheme_Object *params[3];
    params[0] = proc_scheme_eval;
    params[1] = compiled;
    params[2] = (Scheme_Object *)env;
    return scheme_apply(catched_apply_proc, 3, params);
}
static Scheme_Object *do_apply(int argc, Scheme_Object **argv)
{
    return scheme_apply_to_list(argv[0], argv[1]);
}
Scheme_Object *catched_scheme_apply(Scheme_Object *proc, Scheme_Object *args, Scheme_Object *catched_apply_proc)
{
    Scheme_Object *params[3];
    params[0] = proc_scheme_apply;
    params[1] = proc;
    params[2] = args;
    return scheme_apply(catched_apply_proc, 3, params);
}
