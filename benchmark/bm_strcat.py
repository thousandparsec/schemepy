"""\
This tests nothing but string-append and substring.
"""
# test code borrowed from http://www.ccs.neu.edu/home/will/Twobit/KVW/string.txt

from benchmark import Benchmark
import helper

helper.load_backends()

code = """
(begin
  (define (grow)
    (set! s (string-append "123" s "456" s "789"))
    (set! s (string-append
              (substring s (quotient (string-length s) 2) (string-length s))
              (substring s 0 (+ 1 (quotient (string-length s) 2)))))
    s)
  (define (trial n)
    (do ((i 0 (+ i 1)))
      ((> (string-length s) n) (string-length s))
      (grow))))
"""

def call_trial(vm):
    vm.eval(vm.compile('(define s "abcdef")'))
    scm = vm.eval(vm.compile('(trial 1000000)'))
    assert vm.fromscheme(scm) == 1048566

bm = Benchmark(title="string-append and substring performance", repeat=10)
for backend in helper.BACKENDS:
    vm = helper.VM(backend=backend)
    vm.eval(vm.compile(code))
    bm.measure(backend, call_trial, vm)

helper.report(bm.report())
