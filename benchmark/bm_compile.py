"""\
This tests the performance gained by compiling the code
before evaluating it.
"""

from benchmark import Benchmark
import helper

helper.load_backends()

code = """
(begin
  (define a 5)
  (define b 10)

  (+ a
     (* b 10 11)
     (apply + (map (lambda (x) (* x x))
		   (list 1 2 3 a b 5)))
     9
     b))
"""

def call_calc(vm, compiled):
    scm = vm.eval(compiled)
    assert vm.type(scm) is int, "Type should be int"
    assert vm.fromscheme(scm) == 1288, "Result should equal to 1288"

bm = Benchmark(title="performance improvements by compiling", repeat=10000)
for backend in helper.BACKENDS:
    vm = helper.VM(backend=backend)
    compiled = vm.compile(code)
    bm.measure(backend, call_calc, vm, compiled)

helper.report(bm.report())

