"""\
This tests the performance gained by compiling the code
before evaluating it.
"""

from benchmark import Benchmark
import helper

helper.load_backends()

code_sort = """
(begin
  (define (insertion-sort lst)
    (define (insert-in-list new lst)
      (if (null? lst)
        (list new)
        (if (< new (car lst))
          (cons new lst)
          (cons (car lst) (insert-in-list new (cdr lst))))))
    (define (helper unsorted sorted)
      (if (null? unsorted)
        sorted
        (helper (cdr unsorted)
                (insert-in-list (car unsorted) sorted))))
    (helper lst '()))

  (define (sorted? lst)
    (if (null? lst)
      #t
      (if (null? (cdr lst))
        #t
        (if (< (car lst)
               (car (cdr lst)))
            (sorted? (cdr lst))
            #f))))
    
  (define lst '(5 9 2 4 7 6 3 1 8 10 -5 83))
  (define sorted (insertion-sort lst))

  (sorted? sorted))
"""

def call_sort(vm, compiled):
    scm = vm.eval(compiled)
    assert vm.type(scm) is bool, "Type should be bool"
    assert vm.fromscheme(scm) == True, "The array should be sorted"

bm = Benchmark(title="performance improvements by compiling (sort)", repeat=100)
for backend in helper.BACKENDS:
    vm = helper.VM(backend=backend)
    compiled = vm.compile(code_sort)
    bm.measure(backend, call_sort, vm, compiled)

helper.report(bm.report())


code_calc = """
(begin
  (define a 5)
  (define b 10)
  (define c (- a b))

  (+ a
     (* b 10 11)
     (apply + (list (* b c) 1 2 (- 3 a) b 5))
     9
     b))
"""

def call_calc(vm, compiled):
    scm = vm.eval(compiled)
    assert vm.type(scm) is int, "Type should be int"
    assert vm.fromscheme(scm) == 1090, "The result should be 1090"

bm = Benchmark(title="performance improvements by compiling (calc)", repeat=1000)
for backend in helper.BACKENDS:
    vm = helper.VM(backend=backend)
    compiled = vm.compile(code_calc)
    bm.measure(backend, call_calc, vm, compiled)

helper.report(bm.report())
