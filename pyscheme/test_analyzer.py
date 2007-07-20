import unittest

import sys

import analyzer
import parser
import test_scheme
from environment import THE_EMPTY_ENVIRONMENT, extendEnvironment, defineVariable
from symbol import Symbol
import pair
from error import SchemeError
import scheme


class AnalyzerEvaluatorMixin:
    def setUp(self):
         ## sets the recursion limit to something fairly small to test
         ## out the the tail recursion.
        self.old_recursion_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(55)
        self.interp = scheme.AnalyzingInterpreter()

    def tearDown(self):
        sys.setrecursionlimit(self.old_recursion_limit)


    def pe(self, s):
        """Parse and evaluate."""
        return self.interp.eval(parser.parse(s))



class AnalyzingBasicSchemeTestCase(
    AnalyzerEvaluatorMixin, test_scheme.BasicSchemeTests, unittest.TestCase):
    pass


class AnalyzingExtendedSchemeTestCase(
    AnalyzerEvaluatorMixin, test_scheme.ExtendedSchemeTests, unittest.TestCase):
    pass



    
class IndependentAnalyzerTests(unittest.TestCase):
    def setUp(self):
        ## We set up a VERY minimal environment here for some tests.
        ## We also set the recursion limit to something dreadful to see that
        ## call/cc is doing the right thing.
        ##

        ## Note: these tests directly work with analyzer.eval, and not
        ## through the nicer scheme.AnalyzingInterpreter interface.

        self.env = extendEnvironment(pair.list(Symbol('pi')),
                                     pair.list(3.1415926),
                                     THE_EMPTY_ENVIRONMENT)
        defineVariable(Symbol("#t"), Symbol("#t"), self.env)
        defineVariable(Symbol("#f"), Symbol("#f"), self.env)
        self.old_recursion_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(100)


    def tearDown(self):
        self.env = None
        sys.setrecursionlimit(self.old_recursion_limit)


    def pe(self, s):
        """Parse and evaluate."""
        return analyzer.eval(parser.parse(s),
                             self.env)




    def testSelfEvaluating(self):
        self.assertEquals(42, self.pe("42"))
        self.assertEquals(pair.list(), self.pe("()"))


    def testVariable(self):
        self.assertEquals(3.1415926, self.pe("pi"))
        self.assertRaises(SchemeError, self.pe, "nonexistantvalue")


    def testQuotation(self):
        self.assertEquals(Symbol("foobar"), self.pe("'foobar"))
        self.assertEquals(Symbol("foobar"), self.pe("'foobar"))
        self.assertEquals(pair.list(1, 2, 3), self.pe("'(1 2 3)"))


    def testAssignment(self):
        self.assertEquals(Symbol("ok"),
                          self.pe("(set! pi 'three-point-one-four)"))
        self.assertEquals(Symbol("three-point-one-four"),
                          self.pe("pi"))
        self.assertRaises(SchemeError, self.pe, "(set! nonexistantvalue 42)")



    def testDefinition(self):
        self.assertEquals(Symbol("ok"),
                          self.pe("(define name 'danny)"))
        self.assertEquals(Symbol("danny"), self.pe("name"))


    def testIf(self):
        self.assertEquals(Symbol("ok"), self.pe("(if #t 'ok 'not-ok)"))
        self.assertEquals(Symbol("ok"), self.pe("(if #f 'not-ok 'ok)"))


    def testLambda(self):
        ## Can't test much yet without application.
        self.pe("(lambda (x) 'hello 'world)")

        
    def testBegin(self):
        self.assertEquals(Symbol("hello"),
                          self.pe("(begin 'hello)"))
        self.assertEquals(Symbol("world"),
                          self.pe("(begin 'hello '(this is a test) 'world)"))
        self.assertRaises(SchemeError, self.pe, "(begin)")

        
    def testSimpleApplication(self):
        self.assertEquals(Symbol("hello"),
                          self.pe("((lambda (x) x) 'hello)"))
        self.assertEquals(Symbol("hi"),
                          self.pe("((lambda (x y) y) '(this is a test) 'hi)"))



if __name__ == '__main__':
    unittest.main()
