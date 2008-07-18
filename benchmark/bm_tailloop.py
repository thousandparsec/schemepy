from benchmark import Benchmark
import helper

helper.load_backends()

code = """
(lambda (n)
  (define (iter sum i)
    (if (= i 0)
      sum
      (iter (+ sum i)
            (- i 1))))
   (iter 0 n))
"""

def call_sum(proc, vm):
    scm = vm.apply(proc, [vm.toscheme(10000)])
    assert vm.fromscheme(scm) == 50005000

bm = Benchmark(title="Tail call performance", repeat=10)
for backend in helper.BACKENDS:
    vm = helper.VM(backend=backend)
    proc = vm.eval(vm.compile(code))
    bm.measure(backend, call_sum, proc, vm)

helper.report(bm.report())
