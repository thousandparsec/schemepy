#include "scheme.h"

Scheme_Env *global_env;

/**
 * It's strange that bool constants from mzscheme.so is different
 * from what's seen from this library (from the header file). And
 * since value seen from this library consists with the eval-ed
 * values (i.e. scheme_eval_string("#t", env)), we'll use constants
 * from here.
 */
Scheme_Object *_scheme_true;
Scheme_Object *_scheme_false;

void init_mz()
{
    scheme_set_stack_base(NULL, 1); /* required for OS X, only */
    global_env = scheme_basic_env();

    _scheme_true = scheme_true;
    _scheme_false = scheme_false;
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
