
#include <libguile.h>


int guile_major_version() {
	return SCM_MAJOR_VERSION;
}

int guile_minor_version() {
	return SCM_MINOR_VERSION;
}

#if SCM_MAJOR_VERSION == 1 && SCM_MINOR_VERSION == 6

#include <guile/gh.h>
#include <string.h>

/* Good source of help http://www.koders.com/cpp/fid8730873A7BB794602B8181A514C194DFD919CB41.aspx */
SCM scm_from_bool(int x) {
	return (x ? SCM_BOOL_T : SCM_BOOL_F);
}

int scm_to_bool(SCM x) {
	return SCM_NFALSEP(x);
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

/* FIXME: Is this right? */
int scm_is_rational(SCM x) {
	return scm_real_p(x) == SCM_BOOL_T;
}

/* FIXME: Is this right? */
int scm_is_complex(SCM x) {
	return scm_number_p(x) == SCM_BOOL_T;
}

int scm_is_pair(SCM x) {
	return SCM_CONSP (x);
}

int scm_is_null(SCM x) {
	return SCM_NULLP (x);
}

int scm_is_true(SCM x) {
	return SCM_NFALSEP (x);
}

int scm_is_false(SCM x) {
	return SCM_FALSEP (x);
}

int scm_is_symbol(SCM x) {
	return SCM_SYMBOLP (x);
}

int scm_is_string(SCM x) {
	return SCM_ROSTRINGP(x);
}

int scm_to_int32(SCM x) {
	return gh_scm2long(x);
}

SCM scm_from_int32 (int n) {
	return scm_int2num (n);
}

double scm_to_double(SCM x) {
	return gh_scm2double(x);
}

SCM scm_from_double(double x) {
	return gh_double2scm(x);
}

/* same as in Guile 1.8 */
char* scm_to_locale_stringn (SCM str, size_t* lenp) {
	if SCM_UNBNDP(str) return NULL;
	return gh_scm2newstr(str, lenp);
}

char* scm_to_locale_string (SCM obj) {
	if SCM_UNBNDP(obj) return NULL;
	return scm_to_locale_stringn(obj, NULL);
}

SCM scm_from_locale_string(char* s) {
	return scm_makfrom0str(s);
}

SCM scm_from_locale_stringn(char* s, int len) {
	return scm_mem2string(s,len);
}

/*
SCM scm_take_locale_string(char* s) {
	return scm_take0str(s);
}

SCM scm_take_locale_stringn(char* s, int len) {
	sgtk_take_locale_stringn(s,len);
} */

double scm_c_real_part(SCM x) {
	return scm_to_double(scm_real_part(x));
}

double scm_c_imag_part(SCM x) {
	return scm_to_double(scm_imag_part(x));
}

SCM scm_car(SCM x) {
	return SCM_CAR(x);
}

SCM scm_cdr(SCM x) {
	return SCM_CDR(x);
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

int _scm_is_false(SCM x) {
	return scm_is_false(x);
}

int _scm_is_null(SCM x) {
	return scm_is_null(x);
}

#endif

int scm_is_fixnum(SCM x) {
        return SCM_I_INUMP(x);
}

int scm_imp(SCM x) {
	return SCM_IMP(x);
}

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

int scm_is_exact(SCM x) {
	return scm_exact_p(x) == SCM_BOOL_T;
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

int scm_is_eol(SCM x) {
	return x == SCM_EOL;
}

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
