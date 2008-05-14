# Test cases converted from PyPy's test_eval.py
# https://codespeak.net/viewvc/pypy/dist/pypy/lang/scheme/test/test_eval.py?view=markup

import schemepy
import schemepy.types
import nose.tools

def test_numerical():
    vm = schemepy.VM()
    
    w_num = vm.eval("(+)")
    assert vm.fromscheme(w_num) == 0
    w_num = vm.eval("(+ 4)")
    assert vm.fromscheme(w_num) == 4
    w_num = vm.eval("(+ 4 -5)")
    assert vm.fromscheme(w_num) == -1
    w_num = vm.eval("(+ 4 -5 6.1)")
    assert vm.fromscheme(w_num) == 5.1

    w_num = vm.eval("(*)")
    assert vm.fromscheme(w_num) == 1
    w_num = vm.eval("(* 4)")
    assert vm.fromscheme(w_num) == 4
    w_num = vm.eval("(* 4 -5)")
    assert vm.fromscheme(w_num) == -20
    w_num = vm.eval("(* 4 -5 6.1)")
    assert vm.fromscheme(w_num) == (4 * -5 * 6.1)

    nose.tools.assert_raises(Exception, vm.eval, "(/)")
    w_num = vm.eval("(/ 4)")
    assert vm.fromscheme(w_num) == 1 / 4.0
    w_num = vm.eval("(/ 4 -5)")
    assert vm.fromscheme(w_num) == 4 / -5.0
    w_num = vm.eval("(/ 4 -5 6.1)")
    assert vm.fromscheme(w_num) == (4 / -5.0 / 6.1)

    nose.tools.assert_raises(Exception, vm.eval, "(-)")
    w_num = vm.eval("(- 4)")
    assert vm.fromscheme(w_num) == -4
    w_num = vm.eval("(- 4 5)")
    assert vm.fromscheme(w_num) == -1
    w_num = vm.eval("(- 4 -5 6.1)")
    assert vm.fromscheme(w_num) == 4 - (-5) - 6.1

    nose.tools.assert_raises(Exception, vm.eval, "(+ 'a)")
    nose.tools.assert_raises(Exception, vm.eval, "(+ 1 'a)")
    nose.tools.assert_raises(Exception, vm.eval, "(- 'a)")
    nose.tools.assert_raises(Exception, vm.eval, "(- 1 'a)")
    nose.tools.assert_raises(Exception, vm.eval, "(* 'a)")
    nose.tools.assert_raises(Exception, vm.eval, "(* 2 'a)")
    nose.tools.assert_raises(Exception, vm.eval, "(/ 'a)")
    nose.tools.assert_raises(Exception, vm.eval, "(/ 1 'a)")

def test_numerical_nested():
    vm = schemepy.VM()
    
    w_num = vm.eval("(+ 4 (* (+ 5) 6) (+ 1 2))")
    assert vm.fromscheme(w_num) == 37

def test_ctx_simple():
    vm = schemepy.VM()
    
    vm.define("v1", vm.toscheme(4))
    vm.define("v2", vm.toscheme(5))

    w_num = vm.eval("(+ 1 v1 v2)")
    assert vm.fromscheme(w_num) == 10

    vm.define("v2", vm.toscheme(3.2))
    w_num = vm.eval("(+ 1 v1 v2)")
    assert vm.fromscheme(w_num) == 8.2

def test_ctx_define():
    vm = schemepy.VM()
    
    vm.eval("(define v1 42)")
    assert vm.fromscheme(vm.get("v1")) == 42
    w_num = vm.eval("v1")
    assert vm.fromscheme(w_num) == 42

    vm.eval("(define v2 2.1)")
    assert vm.fromscheme(vm.get("v2")) == 2.1

    w_num = vm.eval("(+ 1 v1 v2)")
    assert vm.fromscheme(w_num) == 45.1

    vm.eval("(define v2 3.1)")
    w_num = vm.eval("(+ 1 v1 v2)")
    assert vm.fromscheme(w_num) == 46.1

def text_unbound():
    vm = schemepy.VM()
    assert vm.get("foobar", default="default-foobar") == "default-foobar"

def test_sete():
    vm = schemepy.VM()
    vm.eval("(define x 42)")
    vm.eval("(set! x 43)")
    assert vm.fromscheme(vm.get("x")) == 43
    nose.tools.assert_raises(Exception, vm.eval, "(set! y 42)")

def test_if_simple():
    vm = schemepy.VM()
    
    w_t = vm.eval("(if #t #t #f)")
    assert vm.fromscheme(w_t) is True
    w_f = vm.eval("(if #f #t #f)")
    assert vm.fromscheme(w_f) is False
    w_f = vm.eval("(if 1 #f #t)")
    assert vm.fromscheme(w_f) is False
    w_f = vm.eval("(if #t #t)")
    assert vm.fromscheme(w_f) is True

def test_if_evaluation():
    vm = schemepy.VM()
    
    vm.eval("(define then #f)")
    vm.eval("(define else #f)")
    vm.eval("(if #t (define then #t) (define else #t))")
    assert vm.fromscheme(vm.get("then")) is True
    assert vm.fromscheme(vm.get("else")) is False

    vm.eval("(define then #f)")
    vm.eval("(define else #f)")
    vm.eval("(if #f (define then #t) (define else #t))")
    assert vm.fromscheme(vm.get("then")) is False
    assert vm.fromscheme(vm.get("else")) is True

def test_cons_simple():
    vm = schemepy.VM()
    
    w_pair = vm.eval("(cons 1 2)")
    assert vm.type(w_pair) is schemepy.types.Cons
    assert vm.fromscheme(w_pair).car == 1
    assert vm.fromscheme(w_pair).cdr == 2

    w_pair = vm.eval("(cons 1 (cons 2 3))")
    assert vm.type(w_pair) is schemepy.types.Cons
    assert isinstance(vm.fromscheme(w_pair).cdr, schemepy.types.Cons)
    assert vm.fromscheme(w_pair).car == 1
    assert vm.fromscheme(w_pair).cdr.car == 2
    assert vm.fromscheme(w_pair).cdr.cdr == 3

def test_car_simple():
    vm = schemepy.VM()
    
    w_car = vm.eval("(car (cons 1 2))")
    assert vm.fromscheme(w_car) == 1

    w_cdr = vm.eval("(cdr (cons 1 2))")
    assert vm.fromscheme(w_cdr) == 2

    w_cadr = vm.eval("(car (cdr (cons 1 (cons 2 3))))")
    assert vm.fromscheme(w_cadr) == 2

    w_cddr = vm.eval("(cdr (cdr (cons 1 (cons 2 3))))")
    assert vm.fromscheme(w_cddr) == 3

def test_comparison_homonums():
    vm = schemepy.VM()
    
    w_bool = vm.eval("(=)")
    assert vm.fromscheme(w_bool) is True

    w_bool = vm.eval("(= 1)")
    assert vm.fromscheme(w_bool) is True

    w_bool = vm.eval("(= 1 2)")
    assert vm.fromscheme(w_bool) is False

    w_bool = vm.eval("(= 2 2)")
    assert vm.fromscheme(w_bool) is True

    w_bool = vm.eval("(= 2 2 2 2)")
    assert vm.fromscheme(w_bool) is True

    w_bool = vm.eval("(= 2 2 3 2)")
    assert vm.fromscheme(w_bool) is False

    w_bool = vm.eval("(= 2.1 1.2)")
    assert vm.fromscheme(w_bool) is False

    w_bool = vm.eval("(= 2.1 2.1)")
    assert vm.fromscheme(w_bool) is True

    w_bool = vm.eval("(= 2.1 2.1 2.1 2.1)")
    assert vm.fromscheme(w_bool) is True

    w_bool = vm.eval("(= 2.1 2.1 2.1 2)")
    assert vm.fromscheme(w_bool) is False

    nose.tools.assert_raises(Exception, vm.eval, "(= 'a 1)")

def test_comparison_heteronums():
    vm = schemepy.VM()
    
    w_bool = vm.eval("(= 1 1.0 1.1)")
    assert vm.fromscheme(w_bool) is False

    w_bool = vm.eval("(= 2.0 2 2.0)")
    assert vm.fromscheme(w_bool) is True

def test_lambda_noargs():
    vm = schemepy.VM()

    w_lambda = vm.eval("(lambda () 12)")
    assert vm.type(w_lambda) is schemepy.types.Lambda

    vm.define("f1", w_lambda)
    w_result = vm.eval("(f1)")
    assert vm.type(w_result) is int
    assert vm.fromscheme(w_result) == 12

def test_lambda_args():
    vm = schemepy.VM()
    
    w_lam = vm.eval("(define f1 (lambda (n) n))")

    w_result = vm.eval("(f1 42)")
    assert vm.type(w_result) is int
    assert vm.fromscheme(w_result) == 42

    w_result = vm.eval("((lambda (n m) (+ n m)) 42 -42)")
    assert vm.type(w_result) is int
    assert vm.fromscheme(w_result) == 0

def test_lambda_top_ctx():
    vm = schemepy.VM()
    
    vm.eval("(define n 42)")
    vm.eval("(define f1 (lambda (m) (+ n m)))")
    w_result = vm.eval("(f1 -42)")
    assert vm.type(w_result) is int
    assert vm.fromscheme(w_result) == 0

    vm.eval("(define n 84)")
    w_result = vm.eval("(f1 -42)")
    assert vm.type(w_result) is int
    assert vm.fromscheme(w_result) == 42

def test_lambda_fac():
    vm = schemepy.VM()
    
    vm.eval("""
        (define fac
            (lambda (n)
                (if (= n 1)
                    n
                    (* (fac (- n 1)) n))))""")
    assert vm.type(vm.get("fac")) is schemepy.types.Lambda
    w_result = vm.eval("(fac 4)")
    assert vm.fromscheme(w_result) == 24

    w_result = vm.eval("(fac 5)")
    assert vm.fromscheme(w_result) == 120

def test_lambda2():
    vm = schemepy.VM()
    
    vm.eval("""(define adder (lambda (x) (lambda (y) (+ x y))))""")
    w_lambda = vm.eval("(adder 6)")
    assert vm.type(w_lambda) is schemepy.types.Lambda

    vm.eval("""(define add6 (adder 6))""")
    w_result = vm.eval("(add6 5)")
    assert vm.type(w_result) is int
    assert vm.fromscheme(w_result) == 11

    w_result = vm.eval("((adder 6) 5)")
    assert vm.type(w_result) is int
    assert vm.fromscheme(w_result) == 11

def test_lambda_long_body():
    vm = schemepy.VM()
    
    vm.eval("""(define long_body (lambda () (define x 42) (+ x 1)))""")
    w_result = vm.eval("(long_body)")
    assert vm.fromscheme(w_result) == 43
    assert vm.get("x", default="default-x") == "default-x"

def test_lambda_lstarg():
    vm = schemepy.VM()
    w_result = vm.eval("""((lambda x x) 1 2 3)""")
    assert vm.type(w_result) is list
    assert vm.fromscheme(w_result) == [1, 2, 3]

def test_lambda_dotted_lstarg():
    vm = schemepy.VM()
    w_result = vm.eval("""((lambda (x y . z) z) 3 4)""")
    assert vm.fromscheme(w_result) == []

    w_result = vm.eval("""((lambda (x y . z) z) 3 4 5 6)""")
    assert vm.type(w_result) is list
    assert vm.fromscheme(w_result) == [5, 6]

def test_define_lambda_sugar():
    vm = schemepy.VM()
    
    vm.eval("""(define (f x) (+ x 1))""")
    w_result = vm.eval("(f 1)")
    assert vm.fromscheme(w_result) == 2

    vm.eval("""(define (f2) (+ 1 1))""")
    w_result = vm.eval("(f2)")
    assert vm.fromscheme(w_result) == 2

    vm.eval("""(define (f3 . x) x)""")
    w_result = vm.eval("(f3 1 2)")
    assert vm.type(w_result) is list
    assert vm.fromscheme(w_result) == [1, 2]

    vm.eval("""(define (f4 x . y) x y)""")
    w_result = vm.eval("(f4 1 2)")
    assert vm.type(w_result) is list
    assert vm.fromscheme(w_result) == [2]

def test_quote():
    sym = schemepy.types.Symbol.intern
    vm = schemepy.VM()
    
    w_fnum = vm.eval("(quote 42)")
    assert vm.fromscheme(w_fnum) == 42

    w_sym = vm.eval("(quote symbol)")
    assert vm.type(w_sym) is schemepy.types.Symbol
    assert vm.fromscheme(w_sym) is sym("symbol")

    w_lst = vm.eval("(quote (1 2 3))")
    assert vm.type(w_lst) is list
    assert vm.fromscheme(w_lst) == [1, 2, 3]

    w_lst = vm.eval("(quote (a (x y) c))")
    assert vm.type(w_lst) is list
    assert vm.fromscheme(w_lst) == [sym("a"), [sym("x"), sym("y")], sym("c")]

def test_quote_parse():
    sym = schemepy.types.Symbol.intern
    vm = schemepy.VM()

    w_fnum = vm.eval("'42")
    assert vm.fromscheme(w_fnum) == 42

    w_sym = vm.eval("'symbol")
    assert vm.type(w_sym) is schemepy.types.Symbol
    assert vm.fromscheme(w_sym) is sym("symbol")

    w_lst = vm.eval("'(1 2 3)")
    assert vm.type(w_lst) is list
    assert vm.fromscheme(w_lst) == [1, 2, 3]

    w_lst = vm.eval("'(a (x y) c)")
    assert vm.type(w_lst) is list
    assert vm.fromscheme(w_lst) == [sym("a"), [sym("x"), sym("y")], sym("c")]

def test_list():
    vm = schemepy.VM()
    vm.define("var", vm.toscheme(42))
    w_lst = vm.eval("(list 1 var (+ 2 1) 'a)")
    assert vm.type(w_lst) is list
    assert vm.fromscheme(w_lst) == [1, 42, 3, schemepy.types.Symbol.intern("a")]

def test_begin():
    vm = schemepy.VM()
    w_global = vm.toscheme(0)
    vm.define("var", w_global)
    w_result = vm.eval("(begin (set! var 11) (+ var 33))")
    assert vm.fromscheme(w_result) == 44
    assert vm.fromscheme(vm.get("var")) == 11

def test_let():
    vm = schemepy.VM()
    w_global = vm.toscheme(0)
    vm.define("var", w_global)
    w_result = vm.eval("(let ((var 42) (x (+ 2 var))) (+ var x))")
    assert vm.fromscheme(w_result) == 44
    assert vm.fromscheme(vm.get("var")) == 0

    w_result = vm.eval("""
        (let ((x (lambda () 1)))
            (let ((y (lambda () (x)))
                  (x (lambda () 2))) (y)))""")
    assert vm.fromscheme(w_result) == 1

    nose.tools.assert_raises(Exception, vm.eval, "(let ((y 0) (x y)) x)")

def test_letrec():
    vm = schemepy.VM()
    w_result = vm.eval("""
        (letrec ((even?
                    (lambda (n)
                        (if (= n 0)
                            #t
                            (odd? (- n 1)))))
                 (odd?
                    (lambda (n)
                        (if (= n 0)
                            #f
                            (even? (- n 1))))))
                (even? 2000))""")
    assert vm.fromscheme(w_result) is True

    w_result = vm.eval("""
        (let ((x (lambda () 1)))
            (letrec ((y (lambda () (x)))
                     (x (lambda () 2))) (y)))""")
    assert vm.fromscheme(w_result) == 2

    nose.tools.assert_raises(Exception, vm.eval, "(letrec ((y 0) (x y)) x)")

def test_letstar():
    #test for (let* ...)
    vm = schemepy.VM()
    w_result = vm.eval("""
        (let* ((x 42)
                (y (- x 42))
                (z (+ x y)))
                z)""")
    assert vm.fromscheme(w_result) == 42

    nose.tools.assert_raises(Exception, vm.eval, "(let* ((x (+ 1 y)) (y 0)) x)")

def test_numbers():
    vm = schemepy.VM()
    
    assert vm.fromscheme(vm.eval("(integer? 42)"))
    assert vm.fromscheme(vm.eval("(integer? 42.0)"))
    assert not vm.fromscheme(vm.eval("(integer? 42.1)"))

    assert vm.fromscheme(vm.eval("(rational? 42)"))
    assert vm.fromscheme(vm.eval("(rational? 42.1)"))

    assert vm.fromscheme(vm.eval("(real? 42)"))
    assert vm.fromscheme(vm.eval("(real? 42.1)"))

    assert vm.fromscheme(vm.eval("(complex? 42)"))
    assert vm.fromscheme(vm.eval("(complex? 42.1)"))

    assert vm.fromscheme(vm.eval("(number? 42)"))
    assert vm.fromscheme(vm.eval("(number? 42.1)"))

def test_exactness():
    vm = schemepy.VM()
    
    assert vm.fromscheme(vm.eval("(exact? 42)"))
    assert not vm.fromscheme(vm.eval("(exact? 42.0)"))
    nose.tools.assert_raises(Exception, vm.eval, "(exact? 'a)" )

    assert not vm.fromscheme(vm.eval("(inexact? 42)"))
    assert vm.fromscheme(vm.eval("(inexact? 42.0)"))
    nose.tools.assert_raises(Exception, vm.eval, "(inexact? 'a)" )

def test_number_predicates():
    vm = schemepy.VM()
    
    assert vm.fromscheme(vm.eval("(zero? 0)"))
    assert vm.fromscheme(vm.eval("(zero? 0.0)"))
    assert not vm.fromscheme(vm.eval("(zero? 1.0)"))
    nose.tools.assert_raises(Exception, vm.eval, "(zero? 'a)" )

    assert not vm.fromscheme(vm.eval("(odd? 0)"))
    assert vm.fromscheme(vm.eval("(odd? 1)"))
    nose.tools.assert_raises(Exception, vm.eval, "(odd? 1.1)" )

    assert vm.fromscheme(vm.eval("(even? 0)"))
    assert not vm.fromscheme(vm.eval("(even? 1)"))
    nose.tools.assert_raises(Exception, vm.eval, "(even? 1.1)" )

def test_delay_promise_force():
    vm = schemepy.VM()
    
    w_promise = vm.eval("(delay (+ 1 2))")
    vm.define("d", w_promise)
    nose.tools.assert_raises(Exception, vm.eval, "(d)")

    w_value = vm.eval("(force d)")
    assert vm.fromscheme(w_value) == 3
    nose.tools.assert_raises(Exception, vm.eval, "(force 'a)")

    vm.eval("(define d2 (delay (+ 1 x)))")
    vm.eval("(define x 42)")
    w_result = vm.eval("(force d2)")
    assert vm.fromscheme(w_result) == 43
    vm.eval("(set! x 0)")
    w_result = vm.eval("(force d2)")
    assert vm.fromscheme(w_result) == 43

def test_lambda_context():
    vm = schemepy.VM()
    vm.eval("""
            (define b (lambda ()
                        (define lam (lambda () (set! a 42)))
                        (define a 12)
                        (lam)
                        a))
                        """)
    w_num = vm.eval("(b)")
    assert vm.fromscheme(w_num) == 42

def test_deep_recursion():
    vm = schemepy.VM()
    vm.eval("(define a 0)")
    vm.eval("""
        (define loop (lambda (n)
                        (set! a (+ a 1))
                        (if (= n 0)
                            n
                            (loop (- n 1)))))""")

    vm.eval("(loop 2000)")
    assert vm.fromscheme(vm.get("a")) == 2001

def test_setcar():
    vm = schemepy.VM()
    w_pair = vm.eval("(define lst '(1 2 3 4))")
    vm.eval("(set-car! lst 11)")
    assert vm.fromscheme(vm.eval("(car lst)")) == 11

    vm.eval("(set-car! (cdr lst) 12)")
    assert vm.fromscheme(vm.eval("(car (cdr lst))")) == 12

def test_setcdr():
    vm = schemepy.VM()
    
    w_pair = vm.eval("(define lst '(1 2 3 4))")
    vm.eval("(set-cdr! lst (cdr (cdr lst)))")
    w_lst = vm.eval("lst")
    assert vm.fromscheme(w_lst) == [1, 3, 4]

    vm.eval("(set-cdr! (cdr lst) '(12))")
    w_lst = vm.eval("lst")
    assert vm.fromscheme(w_lst) == [1, 3, 12]

    #warning circural list
    vm.eval("(set-cdr! (cdr (cdr lst)) lst)")
    w_lst = vm.eval("lst")
    vm.type(w_lst) is list

def test_quasiquote():
    sym = schemepy.types.Symbol.intern
    vm = schemepy.VM()
    
    w_res = vm.eval("(quasiquote (list (unquote (+ 1 2)) 4))")
    assert vm.fromscheme(w_res) == [sym("list"), 3, 4]

    w_res = vm.eval("""
                (let ((name 'a))
                    (quasiquote (list (unquote name)
                                      (quote (unquote name)))))""")
    assert vm.fromscheme(w_res) == [sym("list"), sym("a"), [sym("quote"), sym("a")]]

    nose.tools.assert_raises(Exception, vm.eval, "`(,,(+ 1 2))")

def test_quasiquote_nested():
    sym = schemepy.types.Symbol.intern
    vm = schemepy.VM()
    
    w_res = vm.eval("""
                (quasiquote
                    (a (quasiquote
                           (b (unquote (+ 1 2))
                              (unquote (foo
                                       (unquote (+ 1 3))
                                       d))
                                e))
                            f))""")
    assert vm.fromscheme(w_res) == \
           [sym("a"), [sym("quasiquote"), [sym("b"), [sym("unquote"), [sym("+"), 1, 2]],
                                           [sym("unquote"), [sym("foo"), 4, sym("d")]],
                                           sym("e")]], sym("f")]

    w_res = vm.eval("""
                (let ((name1 'x)
                      (name2 'y))
                    (quasiquote (a
                                (quasiquote (b
                                             (unquote (unquote name1))
                                             (unquote (quote
                                                        (unquote name2)))
                                             d))
                                 e)))""")
    assert vm.fromscheme(w_res) == \
           [sym("a"), [sym("quasiquote"), [sym("b"), [sym("unquote"), sym("x")],
                                           [sym("unquote"), [sym("quote"), sym("y")]],
                                           sym("d")]], sym("e")]

def test_quasiquote_splicing():
    vm = schemepy.VM()
    
    w_res = vm.eval("""`(1 2 ,@(list 3 4) 5 6)""")
    assert vm.fromscheme(w_res) == [1, 2, 3, 4, 5, 6]
    nose.tools.assert_raises(Exception, vm.eval, "`(,@(list 1 ,@(list 2 3)))")

    w_res = vm.eval("""`(1 2 ,@(list 3 4) . ,(+ 2 3))""")
    assert vm.type(w_res) is schemepy.types.Cons
    assert vm.fromscheme(w_res).cdr.cdr.cdr.cdr == 5

    w_res = vm.eval("""`(( foo  7) ,@(cdr '(c)) . ,(car '(cons)))""")
    assert vm.type(w_res) is schemepy.types.Cons
    assert vm.fromscheme(w_res).cdr == schemepy.types.Symbol.intern("cons")
    assert vm.fromscheme(w_res).car == [schemepy.types.Symbol.intern("foo"), 7]

def test_type_predicates():
    vm = schemepy.VM()

    assert vm.fromscheme(vm.eval("(pair? 1)")) is False
    assert vm.fromscheme(vm.eval("(pair? 'symb)")) is False
    assert vm.fromscheme(vm.eval("(pair? #f)")) is False
    assert vm.fromscheme(vm.eval("(pair? '())")) is False
    assert vm.fromscheme(vm.eval("(pair? +)")) is False
    assert vm.fromscheme(vm.eval("(pair? (lambda () 1))")) is False
    assert vm.fromscheme(vm.eval("(pair? '(1))")) is True
    assert vm.fromscheme(vm.eval("(pair? (list 1))")) is True
    assert vm.fromscheme(vm.eval("(pair? (cons 1 2))")) is True

    assert vm.fromscheme(vm.eval("(procedure? 1)")) is False
    assert vm.fromscheme(vm.eval("(procedure? 'symb)")) is False
    assert vm.fromscheme(vm.eval("(procedure? #f)")) is False
    assert vm.fromscheme(vm.eval("(procedure? '())")) is False
    assert vm.fromscheme(vm.eval("(procedure? '(1))")) is False
    assert vm.fromscheme(vm.eval("(procedure? (list 1))")) is False
    assert vm.fromscheme(vm.eval("(procedure? (cons 1 2))")) is False
    assert vm.fromscheme(vm.eval("(procedure? +)")) is True
    assert vm.fromscheme(vm.eval("(procedure? (lambda () 1))")) is True

    assert vm.fromscheme(vm.eval("(symbol? 1)")) is False
    assert vm.fromscheme(vm.eval("(symbol? 'symb)")) is True
    assert vm.fromscheme(vm.eval("(symbol? #f)")) is False
    assert vm.fromscheme(vm.eval("(symbol? '())")) is False
    assert vm.fromscheme(vm.eval("(symbol? '(1))")) is False
    assert vm.fromscheme(vm.eval("(symbol? (list 1))")) is False
    assert vm.fromscheme(vm.eval("(symbol? (cons 1 2))")) is False
    assert vm.fromscheme(vm.eval("(symbol? +)")) is False
    assert vm.fromscheme(vm.eval("(symbol? (lambda () 1))")) is False

    assert vm.fromscheme(vm.eval("(boolean? 1)")) is False
    assert vm.fromscheme(vm.eval("(boolean? 'symb)")) is False
    assert vm.fromscheme(vm.eval("(boolean? #f)")) is True
    assert vm.fromscheme(vm.eval("(boolean? #t)")) is True
    assert vm.fromscheme(vm.eval("(boolean? '())")) is False
    assert vm.fromscheme(vm.eval("(boolean? '(1))")) is False
    assert vm.fromscheme(vm.eval("(boolean? (list 1))")) is False
    assert vm.fromscheme(vm.eval("(boolean? (cons 1 2))")) is False
    assert vm.fromscheme(vm.eval("(boolean? +)")) is False
    assert vm.fromscheme(vm.eval("(boolean? (lambda () 1))")) is False

def test_eqv():
    vm = schemepy.VM()

    assert vm.fromscheme(vm.eval("(eqv? #t #t)")) is True
    assert vm.fromscheme(vm.eval("(eqv? #f #f)")) is True
    assert vm.fromscheme(vm.eval("(eqv? 'symb 'symb)")) is True
    assert vm.fromscheme(vm.eval("(eqv? 'symb 'SYMB)")) is False
    assert vm.fromscheme(vm.eval("(eqv? 42 42)")) is True
    assert vm.fromscheme(vm.eval("(eqv? 42.1 42.1)")) is True
    assert vm.fromscheme(vm.eval("(eqv? '() '())")) is True
    assert vm.fromscheme(vm.eval("""(let ((p (cons 1 2)))
                           (eqv? p p))""")) is True
    assert vm.fromscheme(vm.eval("""(let ((p (lambda (x) x)))
                           (eqv? p p))""")) is True

    assert vm.fromscheme(vm.eval("(eqv? #t 'symb)")) is False
    assert vm.fromscheme(vm.eval("(eqv? #f 42)")) is False
    assert vm.fromscheme(vm.eval("(eqv? #t #f)")) is False
    assert vm.fromscheme(vm.eval("(eqv? 'symb1 'symb2)")) is False
    assert vm.fromscheme(vm.eval("(eqv? 42 42.0)")) is False
    assert vm.fromscheme(vm.eval("(eqv? 42.0 42)")) is False
    assert vm.fromscheme(vm.eval("(eqv? 42 43)")) is False
    assert vm.fromscheme(vm.eval("(eqv? 42.1 42.2)")) is False
    assert vm.fromscheme(vm.eval("(eqv? (cons 1 2) (cons 1 2))")) is False
    assert vm.fromscheme(vm.eval("""(eqv? (lambda () 1)
                               (lambda () 2))""")) is False

def test_eq():
    vm = schemepy.VM()

    assert vm.fromscheme(vm.eval("(eq? #t #t)")) is True
    assert vm.fromscheme(vm.eval("(eq? #f #f)")) is True
    assert vm.fromscheme(vm.eval("(eq? 'symb 'symb)")) is True
    assert vm.fromscheme(vm.eval("(eq? 'symb 'SYMB)")) is False
    assert vm.fromscheme(vm.eval("(eq? '() '())")) is True
    assert vm.fromscheme(vm.eval("""(let ((n 42))
                           (eq? n n))""")) is True
    assert vm.fromscheme(vm.eval("""(let ((p (cons 1 2)))
                           (eq? p p))""")) is True
    assert vm.fromscheme(vm.eval("""(let ((p (lambda (x) x)))
                           (eq? p p))""")) is True

    assert vm.fromscheme(vm.eval("(eq? #t 'symb)")) is False
    assert vm.fromscheme(vm.eval("(eq? #f 42)")) is False
    assert vm.fromscheme(vm.eval("(eq? #t #f)")) is False
    assert vm.fromscheme(vm.eval("(eq? 'symb1 'symb2)")) is False
    assert vm.fromscheme(vm.eval("(eq? 42.1 42.1)")) is False
    assert vm.fromscheme(vm.eval("(eq? 42 42.0)")) is False
    assert vm.fromscheme(vm.eval("(eq? 42.0 42)")) is False
    assert vm.fromscheme(vm.eval("(eq? 42 43)")) is False
    assert vm.fromscheme(vm.eval("(eq? 42.1 42.2)")) is False
    assert vm.fromscheme(vm.eval("(eq? (cons 1 2) (cons 1 2))")) is False
    assert vm.fromscheme(vm.eval("""(eq? (lambda () 1)
                               (lambda () 2))""")) is False

def test_equal():
    vm = schemepy.VM()

    assert vm.fromscheme(vm.eval("(equal? #t #t)")) is True
    assert vm.fromscheme(vm.eval("(equal? #f #f)")) is True
    assert vm.fromscheme(vm.eval("(equal? 'symb 'symb)")) is True
    assert vm.fromscheme(vm.eval("(equal? 'symb 'SYMB)")) is False
    assert vm.fromscheme(vm.eval("(equal? 42 42)")) is True
    assert vm.fromscheme(vm.eval("(equal? 42.1 42.1)")) is True
    assert vm.fromscheme(vm.eval("(equal? '() '())")) is True
    assert vm.fromscheme(vm.eval("""(let ((p (cons 1 2)))
                           (equal? p p))""")) is True
    assert vm.fromscheme(vm.eval("""(let ((p (lambda (x) x)))
                           (equal? p p))""")) is True

    assert vm.fromscheme(vm.eval("(equal? #t 'symb)")) is False
    assert vm.fromscheme(vm.eval("(equal? #f 42)")) is False
    assert vm.fromscheme(vm.eval("(equal? #t #f)")) is False
    assert vm.fromscheme(vm.eval("(equal? 'symb1 'symb2)")) is False
    assert vm.fromscheme(vm.eval("(equal? 42 42.0)")) is False
    assert vm.fromscheme(vm.eval("(equal? 42.0 42)")) is False
    assert vm.fromscheme(vm.eval("(equal? 42 43)")) is False
    assert vm.fromscheme(vm.eval("(equal? 42.1 42.2)")) is False
    assert vm.fromscheme(vm.eval("(equal? (cons 1 2) (cons 1 2))")) is True
    assert vm.fromscheme(vm.eval("""(equal? (lambda () 1)
                               (lambda () 2))""")) is False
    assert vm.fromscheme(vm.eval("(equal? '(a (b) c) '(a (b) c))")) is True
    assert vm.fromscheme(vm.eval("(equal? '(a (b) c) '(a (e) c))")) is False

def test_apply():
    vm = schemepy.VM()
    
    assert vm.fromscheme(vm.eval("(apply + (list 3 4))")) == 7

    vm.eval("""(define compose
                    (lambda (f g)
                      (lambda args
                        (f (apply g args)))))""")
    w_result = vm.eval("((compose (lambda (x) (* x x)) +) 3 5)")
    assert vm.fromscheme(w_result) == 64

    assert vm.fromscheme(vm.eval("(apply + '())")) == 0
    nose.tools.assert_raises(Exception, vm.eval, "(apply 1)")
    nose.tools.assert_raises(Exception, vm.eval, "(apply 1 '(1))")
    nose.tools.assert_raises(Exception, vm.eval, "(apply + 42)")
