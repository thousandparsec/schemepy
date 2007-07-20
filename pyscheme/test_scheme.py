#!/usr/bin/env python
"""
Unit tests on PyScheme.
"""


import unittest
import symbol
from symbol import Symbol
from error import SchemeError
import pair
import sys
import parser
import scheme


class RegularInterpreterMixin:
    def setUp(self):
         ## sets the recursion limit to something fairly small to test
         ## out the the tail recursion.
        self.old_recursion_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(50)
        self.interp = scheme.RegularInterpreter()

    def tearDown(self):
        sys.setrecursionlimit(self.old_recursion_limit)


    def pe(self, s):
        return self.interp.eval(parser.parse(s))
    


class BasicSchemeTests:
    """Defines a set of test cases that assumes the presence of a pe()
    method."""

    def testSimpleStuff(self):
        self.assertEquals(42, self.pe("42"))


    def testBadTypes(self):
        self.assertRaises(SchemeError, self.pe, "(* (list 1 2 3 4 5) 3)")


    def testEq(self):
        self.assertEquals(symbol.true, self.pe("""
        (begin
           (define x 3)
           (define y '(4))
           (eq? (cdr (cons x y)) y))"""))
        self.assertEquals(symbol.true, self.pe("(eq? (cdr '(1)) (cdr '(1)))"))
        self.assertEquals(symbol.false, self.pe("(eq? '(1) '(1))"))


    def testDefinition(self):
        self.assertRaises(SchemeError, self.pe, "pi") ## lookup before defn
        self.assertEquals(Symbol("ok"), self.pe("(define pi 3.1415926)"))
        self.assertEquals(3.1415926, self.pe("pi"))


    def testQuotation(self):
        self.assertEquals(pair.list(Symbol("foo"),
                                          Symbol("bar")),
                          self.pe("'(foo bar)"))

    def testQuasiquotation(self):
        self.pe("(define one 1)")
        self.pe("(define two 2)")
        self.pe("(define three 3)")
        self.assertEquals(pair.list(Symbol("one"),
                                          Symbol("two"),
                                          3),
                          self.pe("`(one two ,three)"))
        self.assertEquals(pair.list(Symbol("one"),
                                          Symbol("two"),
                                          (pair.list
                                           (Symbol("unquote"),
                                            Symbol("three")))),
                          self.pe("'(one two ,three)"))

        ## this evil case occurs in R5RS
        self.assertEquals(parser.parse("(a `(b ,(+ 1 2) ,(foo 4 d) e) f)"),
                          self.pe("`(a `(b ,(+ 1 2) ,(foo ,(+ 1 3) d) e) f)"))



    def testVarArgs(self):
        self.pe("(define (mylist . args) args)")
        self.assertEquals(parser.parse("(1 2 3)"), self.pe("(mylist 1 2 3)"))
        self.pe("""(define (list2 a b . c)
                      (list a b c))""")
        self.assertEquals(pair.list(1, 2, pair.list()),
                          self.pe("(list2 1 2)"))

    def testMinusOne(self):
        self.assertEquals(-1, self.pe("(- 1)"))

    def testApply(self):
        self.assertEquals(15, self.pe("(apply + '(1 2 3 4 5))"))
        self.pe("(define (compose f g) (lambda (x) (f (g x))))")
        self.pe("(define (square x) (* x x))")
        self.pe("(define (double x) (* x 2))")
        self.assertEquals(64, self.pe("(apply (compose square double) '(4))"))


    def testTooManyAndTooFew(self):
        self.pe("(define (square x) (* x x))")
        self.assertRaises(SchemeError, self.pe, "(square)")
        self.assertRaises(SchemeError, self.pe, "(square 1 2)")
        self.pe("(define (f x . y) (cons x y))")
        self.assertRaises(SchemeError, self.pe, "(f)")


    def testAnotherQuasiquote(self):
        self.pe("(define x 42)")
        self.assertEquals(42, self.pe("x"))
        self.assertEquals(pair.list
                          (Symbol("x"),
                           pair.list(Symbol("quote"),
                                           pair.list(Symbol("x"), 42))),
                          self.pe("`(x '(x ,x))"))

    def testLet(self):
        self.assertEquals(5,
                          self.pe("""(let ((x 3)
                                           (y 4)
                                           (z 2))
                                        (+ x z))"""))

    def testAssignment(self):
        self.pe("(define x 0)")
        self.pe("""(define (inc*2)
                      (set! x (+ x 1))
                      (set! x (+ x 1)))""")
        self.pe("(inc*2)")
        self.assertEquals(2, self.pe("x"))


    def defineRecursiveFunctions(self):
        self.pe("""(define (factorial x)
                      (if (= x 0) 1 (* x (factorial (- x 1)))))""")

        self.pe("""(define (even? x) (if (= x 0) #t (odd? (- x 1))))""")
        self.pe("""(define (odd? x) (if (= x 0) #f (even? (- x 1))))""")

        
    def testRecursion(self):
        self.defineRecursiveFunctions()
        self.assertEquals(6, self.pe("(factorial 3)"))
        self.assertEquals(symbol.true, self.pe("(even? 4)"))


    def testTailRecursiveEval(self):
        """This is a test to see that eval() doesn't break, even on
        deeply recursive functions.  Basically, this is a test of the
        trampoline."""
        self.defineRecursiveFunctions()
        def myFactorial(n):
            return reduce(lambda x, y: x*y, range(1,n+1), 1)
        self.assertEquals(myFactorial(50), self.pe("(factorial 50)"))
        self.assertEquals(symbol.true, self.pe("(even? 42)"))



    def testArithmetic(self):
        self.assertEquals(3, self.pe("(+ 1 2)"))
        self.assertEquals(7, self.pe("(- 8 1)"))
        self.assertEquals(42, self.pe("(* 2 21)"))
        self.assertEquals(2, self.pe("(/ 4 2)"))



    def testIf(self):
        self.assertEquals(Symbol("danny"), self.pe("(if 42 'danny 'yoo)"))
        self.assertEquals(Symbol("yoo"), self.pe("(if #f 'danny 'yoo)"))



    def testCond(self):
        self.assertEquals(Symbol("ok"), self.pe(
            """(define (even? x) (= (remainder x 2) 0))"""))
        self.assertEquals(Symbol("ok"), self.pe(
            """(define (odd? x) (not (even? x)))"""))
        self.assertEquals(Symbol("ok"), self.pe(
            """(cond ((even? 3) "not-ok")
               ((odd? 2) "still-not-ok")
               (#t 'ok))"""))




    def testListPrimitives(self):
        self.assertEquals(symbol.true, self.pe("(list? '(1 2 3))"))
        self.assertEquals(symbol.false, self.pe("(list? (cons 1 (cons 2 3)))"))


    def testStringEvaluating(self):
        self.assertEquals("hello",
                          self.pe("\"hello\""))


    def testLambda(self):
        self.pe("""(define square
                        (lambda (x) (* x x)))""")
        self.assertEquals(49, self.pe("(square 7)"))


    def testWithYOperator(self):
        """A stress test with the infamous Y operator.  This one comes from
        Taming the Y Operator, by Guillermo Juan Rozas."""
        self.pe("""(define (y f)
                      ((lambda (g) (g g))
                       (lambda (x)
                         (f (lambda ()
                              (x x))))))""")
        self.pe("""(define factorial
                      (y (lambda (self)
                            (lambda (n)
                               (if (= n 0)
                                   1
                                   (* n ((self) (- n 1))))))))""")
        self.assertEquals(3628800, self.pe("(factorial 10)"))


    def testGensymConstruction(self):
        self.pe("""(define (make-counter prefix)
                      (let ((i 0))
                         (lambda ()
                           (begin
                              (set! i (+ i 1))
                              (string->symbol
                                 (string-append (symbol->string prefix)
                                                (number->string i)))))))""")
        self.pe("""(define gensym1 (make-counter 'g))""")
        self.pe("""(define gensym2 (make-counter 'h))""")
        self.assertEquals(Symbol("g1"), self.pe("(gensym1)"))
        self.assertEquals(Symbol("g2"), self.pe("(gensym1)"))
        self.assertEquals(Symbol("g3"), self.pe("(gensym1)"))
        self.assertEquals(Symbol("h1"), self.pe("(gensym2)"))

                                 
    def testAndAndOr(self):
        self.pe("""(define (how-tall? height)
                      (cond ((or (<= height 0) (>= height 12)) 'impossible)
                            ((and (< 0 height) (< height 3)) 'midget)
                            ((and (<= 3 height) (< height 6.5)) 'medium)
                            ((and (<= 6.5 height) (< height 12)) 'giant)))""")
        
        ## according to http://usedwigs.com/lists.html
        self.pe("(define mini-me (+ 2 (/ 8.0 12)))")

        ## according to http://www.geocities.com/Colosseum/3522/facts.htm
        self.pe("(define shaq (+ 7 (/ 1.0 12)))")

        ## according to http://animatedtv.about.com/cs/faqs/a/simpsonbios.htm
        self.pe("(define homer 6)")  

        self.assertEquals(Symbol("giant"), self.pe("(how-tall? shaq)"))
        self.assertEquals(Symbol("midget"), self.pe("(how-tall? mini-me)"))
        self.assertEquals(Symbol("medium"), self.pe("(how-tall? homer)"))
        self.assertEquals(Symbol("impossible"), self.pe("(how-tall? 0)"))
        self.assertEquals(Symbol("impossible"), self.pe("(how-tall? 100)"))        


    def testSetCarCdr(self):
        self.pe("(define x '(hello world))")
        self.pe("(define y x)")
        self.pe("(define z (cons 'hi 'earth))")
        self.pe("(set-car! x 'hi)")
        self.pe("(set-cdr! y 'earth)")
        self.assertEquals(pair.cons(Symbol("hi"), Symbol("earth")),
                          self.pe("x"))
        self.assert_(self.pe("(eq? x y)"))
        self.assert_(self.pe("(not (eq? x z))"))
        self.assert_(self.pe("(equal? x z)"))


    def defineCons(self):
        self.pe("""(define cons
                      (lambda (x y)
                         (lambda (dispatch)
                            (if (= dispatch 'car)
                                x
                                y))))""")

    def testApplication(self):
        self.defineCons()
        self.assertEquals(Symbol("ok"),
                          self.pe("(define myname (cons 'danny 'yoo))"))
        self.assertEquals(Symbol("danny"),
                          self.pe("(myname 'car)"))
        self.assertEquals(Symbol("yoo"),
                          self.pe("(myname 'cdr)"))





class ExtendedSchemeTests:
    """Another set of tests that explore some of the more esoteric
    features.  Assumes that there's a pe() method that does parse/eval."""
    def testEvalCallcc(self):
        self.assertEquals(42, self.pe("(call/cc (lambda (x) 42))"))
        self.assertEquals(42, self.pe("(call/cc (lambda (x) (x 42)))"))
        self.assertEquals(15, self.pe("(+ 1 2 3 4 (call/cc (lambda (x) 5)))"))
        self.assertEquals(5, self.pe("(call/cc (lambda (x) (+ 1 2 3 4 (x 5))))"))
        self.pe("""
            (define (member x l)
               (call/cc (lambda (exit)
                            (cond ((null? l) (exit #f))
                                  ((equal? x (car l)) l)
                                  (#t (member x (cdr l)))))))""")
        self.assertEquals(self.pe("(list 4 5)"),
                          self.pe("(member 4 (list 1 2 3 4 5))"))
    

    def testLoad(self):
        ## A small test of the stack module in the 't' test directory.
        self.pe('(load "t/stack.scm")')
        self.pe("(define s (make-stack))")
        self.pe("(push s 42)")
        self.pe("(push s 'foobar)")
        self.pe("(push s (lambda (x) x))")
        self.assertEquals(Symbol("muhaha"),
                          self.pe("((pop s) 'muhaha)"))
        self.assertEquals(Symbol("foobar"), self.pe("(pop s)"))
        self.assertEquals(42, self.pe("(pop s)"))
        self.assertRaises(SchemeError, self.pe, "(pop s)")


    def testDir(self):
        self.assertEquals(pair.list(),
                          self.pe("((lambda () (dir)))"))
        self.assertEquals(pair.list(Symbol("x")),
                          self.pe("((lambda (x) (dir)) 42)"))
    

    def testSchemeEval(self):
        self.assertEquals(42, self.pe("(+ 2 (eval '(+ 30 10)))"))
        self.assertEquals(42, self.pe("(+ 2 (eval '(+ 30 ((lambda () 10)))))"))
        self.assertEquals(Symbol("hello"),
                          self.pe("((eval '(lambda () 'hello)))"))

        ## Quick test to see that EVAL'ed expressions are also
        ## expanded, since AND is derived.
        self.assertEquals(Symbol("foo"),
                          self.pe("(eval '(AND 'this 'is 'a 'foo))"))


    def testParse(self):
        self.assertEquals(parser.parse("(this is ( a test))"),
                          self.pe('(parse "(this is ( a test))")'))




class BasicSchemeTestCase(RegularInterpreterMixin,
                          BasicSchemeTests, unittest.TestCase):
    pass


class ExtendedSchemeTestCase(RegularInterpreterMixin,
                             ExtendedSchemeTests, unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
