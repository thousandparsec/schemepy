"""Syntax expansion.

This is not yet a strong foundation for a macro system, but it's a
start.  I have to finish understanding R. Kent Dybvig's "Writing
Hygenic Macros in Scheme with Syntax-Case".


At the moment, this system takes expression datums and returns
expanded expression datums.  I'll probably need to rework this, since
hygenic macros appear work on intermediate "Syntax" objects.
"""


__license__ = "MIT License"


import pair
import expressions
import pogo
import symbol
import unittest
import parser



class Expander:
    def __init__(self):
        self._handlers = {}
        self._special_forms = { 'quote' : self.t_expand_quote,
                                'set!' : self.t_expand_setbang,
                                'define' : self.t_expand_define,
                                'if' : self.t_expand_if,
                                'lambda' : self.t_expand_lambda,
                                'begin' : self.t_expand_begin,
                                }
        
    def get_keyword_tag(self, expr):
        """Tries to return the keyword.  If no keyword exists, returns
        None."""
        if pair.isPair(expr) and symbol.isSymbol(pair.car(expr)):
            return str(pair.car(expr)).lower()
        return None


    def install_handler(self, keyword, handler):
        """Adds a new macro expansion handler."""
        self._handlers[keyword.lower()] = handler


    def expand(self, expr):
        """Given an expression, tries to expand it and its subexpressions
        into core forms."""
        return pogo.pogo(self.t_expand(expr, pogo.land))


    def t_expand(self, expr, cont):
        """Trampolined expander."""
        if not pair.isList(expr):
            return pogo.bounce(cont, expr)
        
        handler = self._handlers.get(self.get_keyword_tag(expr), None)
        if handler:
            ## expand, and recursively call expansion again.
            return pogo.bounce(self.t_expand, handler(expr), cont)
        elif self.is_special_form(expr):
            return pogo.bounce(self.t_expand_special_form, expr, cont)
        else:
            ## We recursively expand all the subexpressions by mapping
            ## t_expand() across the elements.
            return pogo.bounce(pair.c_listMap, self.t_expand, expr, cont)


    def is_special_form(self, expr):
        """Returns True if expr looks like a core special form."""
        return self.get_keyword_tag(expr) in self._special_forms


    def t_expand_special_form(self, expr, cont):
        """The core special forms have a different set of expansion
        rules."""
        return self._special_forms[self.get_keyword_tag(expr)](expr, cont)


    def t_expand_quote(self, expr, cont):
        if expressions.isQuasiquoted(expr):
            expandedExp = expressions.expandQuasiquotation(text)
            return pogo.bounce(self.t_expand, expandedExp, cont)
        else:
            return pogo.bounce(cont, expr)


    def t_expand_setbang(self, expr, cont):
        variable = expressions.assignmentVariable(expr)
        value = expressions.assignmentValue(expr)
        def c_expanded(expandedValue):
            return pogo.bounce(
                cont, expressions.makeAssignment(variable, expandedValue))
        return pogo.bounce(self.t_expand, value, c_expanded)


    def t_expand_define(self, expr, cont):
        variable = expressions.definitionVariable(expr)
        value = expressions.definitionValue(expr)
        def c_expanded(expandedValue):
            return pogo.bounce(
                cont, expressions.makeDefinition(variable, expandedValue))
        return pogo.bounce(self.t_expand, value, c_expanded)


    def t_expand_if(self, expr, cont):
        pred = expressions.ifPredicate(expr)
        consq = expressions.ifConsequent(expr)
        altern = expressions.ifAlternative(expr)
        def c_pred(pred_value):
            def c_conseq(consequent_value):
                def c_altern(alternative_value):
                    return pogo.bounce(cont,
                                       expressions.makeIf(pred_value,
                                                          consequent_value,
                                                          alternative_value))
                return pogo.bounce(self.t_expand, altern, c_altern)
            return pogo.bounce(self.t_expand, consq, c_conseq)
        return pogo.bounce(self.t_expand, pred, c_pred)


    def t_expand_lambda(self, expr, cont):
        parameters = expressions.lambdaParameters(expr)
        body = expressions.lambdaBody(expr)
        def c_expanded(expandedBody):
            return pogo.bounce(cont, expressions.makeLambda(parameters,
                                                            expandedBody))
        return pogo.bounce(self.t_expand, body, c_expanded)


    def t_expand_begin(self, expr, cont):
        def c_expanded(expanded_actions):
            return pogo.bounce(cont,
                               expressions.sequenceToExp(expanded_actions))
        return pair.c_listMap(self.t_expand,
                              expressions.beginActions(expr),
                              c_expanded)
                              
    
######################################################################

## For convenience, we keep a singleton instance at the module level.
_instance = Expander()
expand = _instance.expand
install_handler = _instance.install_handler


######################################################################


def LET_handler(exp):
    return expressions.letToApplication(exp)


def COND_handler(exp):
    return expressions.condToIf(exp)


def and_clauses(exp):
    return pair.cdr(exp)

def makeAnd(clauses):
    return pair.cons(symbol.Symbol("AND"), clauses)    

def AND_handler(exp):
    """We have to consider three cases:

    (AND)            ===>   #f
    (AND e1)         ===>   e1
    (AND e1 e2 ...)  ===>   (IF e1 (AND e2 ...)  #f)
    """
    clauses = and_clauses(exp)
    if pair.length(clauses) == 0:
        return symbol.false
    elif pair.length(clauses) == 1:
        return pair.car(clauses)
    else:
        return expressions.makeIf(pair.car(clauses),
                                  makeAnd(pair.cdr(clauses)),
                                  symbol.false)



def makeOr(clauses):
    return pair.cons(symbol.Symbol("OR"), clauses)



def OR_handler(exp):
    """We have to consider three cases:

    (OR)            ===>   #t

    (OR e1)         ===>   e1

    (OR e1 e2 ...)  ===>   (let ((temp-val e1))
                              (IF temp-val
                                  temp-val
                                  (OR e2 ...)))

                    ===>  ((lambda (temp-val)
                              (IF temp-val
                                  temp-val
                                  (OR e2 ...)))
                           e1)
    """
    clauses = and_clauses(exp)
    if pair.length(clauses) == 0:
        return symbol.true
    elif pair.length(clauses) == 1:
        return pair.car(clauses)
    else:
        temporarySymbol = symbol.makeUniqueTemporary()
        lambdaVal = expressions.makeLambda(
            pair.list(temporarySymbol),
            pair.list(expressions.makeIf(temporarySymbol,
                                         temporarySymbol,
                                         makeOr(pair.cdr(clauses)))))
        return expressions.makeApplication(
            lambdaVal, pair.list(pair.car(clauses)))



def install_core_handlers(expanderInstance):
    expanderInstance.install_handler('AND', AND_handler)
    expanderInstance.install_handler('OR', OR_handler)
    expanderInstance.install_handler('LET', LET_handler)
    expanderInstance.install_handler('COND', COND_handler)    
    


######################################################################    

class ExpanderTests(unittest.TestCase):
    def setUp(self):
        self.expander = Expander()
        install_core_handlers(self.expander)
        

    def ep(self, string):
        """Expand and parse.  Typing shortcut."""
        return self.expander.expand(parser.parse(string))


    def p(self, string):
        """Parse.  Typing shortcut."""
        return parser.parse(string)

    
    def testExpansionOnEmptyCase(self):
        self.assertEquals(self.p('()'), self.ep('()'))


    def testANDExpansion(self):
        self.assertEquals(self.p("#f"), self.ep("(and)"))
        self.assertEquals(self.p("foo"), self.ep("(and foo)"))
        self.assertEquals(self.p("(if 3 4 #f)"), self.ep("(and 3 4)"))
        self.assertEquals(self.p("(if 3 (if 4 5 #f) #f)"),
                          self.ep("(and 3 4 5)"))
        self.assertEquals(3, self.ep("(and (and (and 3)))"))

    def testOrExpansion(self):
        self.assertEquals(self.p("#t"), self.ep("(or)"))
        self.assertEquals(self.p("blah"), self.ep("(or blah)"))
        self.ep("(or foo bar)")
        self.ep("(or (and 3) (and 4) (and 5))")
        ## FIXME: I have to figure out how to test this, without
        ## knowing in advance the temporary symbols used in the
        ## expansion...


    def testQuote(self):
        self.assertEquals(self.p("(quote and)"), self.ep("'and"))


    def testSetBang(self):
        self.assertEquals(self.p("(set! x 42)"), self.ep("(set! x (AND 42))"))


    def testDefine(self):
        self.assertEquals(self.p("(define x 42)"),
                          self.ep("(define x (AND 42))"))
                          

    def testIf(self):
        self.assertEquals(self.p("(if foo bar bah!)"),
                          self.ep("(if (AND foo) (AND bar) (AND bah!))"))


    def testLambda(self):
        self.assertEquals(self.p("(lambda (x) one two)"),
                          self.ep("(lambda (x) (AND one) (AND two))"))


    def testBegin(self):
        self.assertEquals(self.p("(begin one two three)"),
                          self.ep("(begin (AND one) (begin (AND two)) (AND three))"))


    def testLet(self):
        self.assertEquals(self.p("((lambda (foo bar) (+ foo bar)) boo hoo)"),
                          self.ep("""(let ((foo boo)
                                           (bar hoo))
                                          (+ foo bar))"""))


    def testCond(self):
        self.assertEquals(self.p("""
                          (define fib
                             (lambda (x)
                                (if (= x 0)
                                    0
                                    (if (= x 1)
                                        1
                                        (+ (fib (- x 1)
                                                (- x 2)))))))
                                 """),
                          self.ep("""
                          (define (fib x)
                             (cond ((= x 0) 0)
                                   ((= x 1) 1)
                                   (else (+ (fib (- x 1)
                                                 (- x 2))))))
                          """))

    ## FIXME: add more complex cases here

        

if __name__ == '__main__':
    unittest.main()
