from benchmark import Benchmark
import helper

helper.load_backends()

code = """
(define (tail-loop-sum n)
  (define (iter sum i)
    (if (= i 0)
      sum
      (iter (+ sum i)
            (- i 1))))
   (iter 0 n))
"""

def call_sum(vm):
    scm = vm.apply(vm.get("tail-loop-sum"), [vm.toscheme(10000)])
    assert vm.fromscheme(scm) == 50005000

bm = Benchmark(title="Tail call performance", repeat=10)
for backend in helper.BACKENDS:
    vm = helper.VM(backend=backend)
    vm.eval(vm.compile(code))
    bm.measure(backend, call_sum, vm)

helper.report(bm.report())
