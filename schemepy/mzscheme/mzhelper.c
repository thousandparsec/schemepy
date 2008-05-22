#include "scheme.h"

int main(int argc, char *argv[])
{
  Scheme_Env *e = NULL;
  Scheme_Object *curout = NULL, *v = NULL;
  Scheme_Config *config = NULL;
  int i;
  mz_jmp_buf * volatile save = NULL, fresh;

  MZ_GC_DECL_REG(5);
  MZ_GC_VAR_IN_REG(0, e);
  MZ_GC_VAR_IN_REG(1, curout);
  MZ_GC_VAR_IN_REG(2, save);
  MZ_GC_VAR_IN_REG(3, config);
  MZ_GC_VAR_IN_REG(4, v);

# ifdef MZ_PRECISE_GC
#  define STACK_BASE &__gc_var_stack__
# else
#  define STACK_BASE NULL
# endif

  scheme_set_stack_base(STACK_BASE, 1);

  MZ_GC_REG();

  e = scheme_basic_env();

  config = scheme_current_config();
  curout = scheme_get_param(config, MZCONFIG_OUTPUT_PORT);

  for (i = 1; i < argc; i++) {
    save = scheme_current_thread->error_buf;
    scheme_current_thread->error_buf = &fresh;
    if (scheme_setjmp(scheme_error_buf)) {
      scheme_current_thread->error_buf = save;
      return -1; /* There was an error */
    } else {
      v = scheme_eval_string(argv[i], e);
      scheme_display(v, curout);
      v = scheme_make_character('\n');
      scheme_display(v, curout);
      /* read-eval-print loop, implicitly uses the initial Scheme_Env: */
      v = scheme_builtin_value("read-eval-print-loop");
      scheme_apply(v, 0, NULL);
      scheme_current_thread->error_buf = save;
    }
  }

  MZ_GC_UNREG();

  return 0;
}
