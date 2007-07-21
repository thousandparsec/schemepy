
#include <libguile.h>

#if SCM_MINOR_VERSION < 7
/* Good source of help http://www.koders.com/cpp/fid8730873A7BB794602B8181A514C194DFD919CB41.aspx */
SCM scm_from_bool(x) {
	return (x ? SCM_BOOL_T : SCM_BOOL_F);
}

int scm_is_bool(SCM x) { 
	return SCM_BOOLP (x); 
}

int scm_is_number(SCM x) {
	return scm_number_p(x) == SCM_BOOL_T;
}

int scm_is_integer(SCM x) {
	return SCM_INUMP (x);
}

int scm_is_pair(SCM x) {
	return SCM_CONSP (x);
}

#else

/* Damn inline functions :/ */
SCM _scm_from_bool(int x) {
	return scm_from_bool(x);
}

int _scm_is_symbol(SCM x) {
	return scm_is_symbol(x);
}

int _scm_is_true(SCM x) {
	return scm_is_true(x);
}

#endif

int scm_unbndp(SCM x) {
	return SCM_UNBNDP(x);
}

SCM scm_bool_t() {
	return SCM_BOOL_T;
}

SCM scm_bool_f() {
	return SCM_BOOL_F;
}

int scm_c_symbol_exists(const char *name) { 
	SCM sym; 
	SCM var;
	
	sym = scm_str2symbol(name);

	/* Check to see if the symbol exists */
	var = scm_sym2var (sym, 
					   scm_current_module_lookup_closure(), 
					   SCM_BOOL_F
					  );

	if (var != SCM_BOOL_F)
			return 1;
	return 0;
}

