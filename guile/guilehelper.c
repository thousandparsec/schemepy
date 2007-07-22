
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

int _scm_is_null(SCM x) {
	return scm_is_null(x);
}

#endif

int scm_is_list(SCM x) {
	return scm_list_p(x) == SCM_BOOL_T;
}

int scm_is_alist(SCM x) {
	SCM item;

	if (!scm_is_list(x))
		return 0;
	
	while (!scm_is_null(x)) {
		item = SCM_CAR(x);
		if (!scm_is_pair(item))
			return 0;
		x = SCM_CDR(x);
	}
	return 1;
}

/*
Recursive version from j85wilson

(define (alist? x)
  (if (null? x)
    #t
    (and (pair? x)
         (pair? (car x))
         (alist? (cdr x)))))

int scm_is_alist(SCM x) {
	if(scm_is_null(x))
		return 1;
	else return (scm_is_pair(x) && scm_is_pair(SCM_CAR(x)) && scm_is_alist(SCM_CDR(x)));
}
*/

SCM scm_eol() {
	return SCM_EOL;
}

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

/* SMOB Helper functions */
void scm_set_smob_data(SCM x, void* p) {
	SCM_SET_SMOB_DATA(x, p);
}

void* scm_smob_data(SCM x) {
	return (void*)SCM_SMOB_DATA(x);
}

SCM scm_return_newsmob(scm_t_bits tag, void* data) {
	SCM_RETURN_NEWSMOB (tag, data);
}

int scm_smob_predicate(scm_t_bits tag, SCM exp) {
	return SCM_SMOB_PREDICATE (tag, exp);
}
