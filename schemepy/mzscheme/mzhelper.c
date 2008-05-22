#include "scheme.h"

Scheme_Env *global_env;

void init_mz()
{
    scheme_set_stack_base(NULL, 1); /* required for OS X, only */
    global_env = scheme_basic_env();
}

int scheme_bool_p(Scheme_Object *o)
{
    return SCHEME_BOOLP(o);
}
int scheme_false_p(Scheme_Object *o)
{
    return SCHEME_FALSEP(o);
}
