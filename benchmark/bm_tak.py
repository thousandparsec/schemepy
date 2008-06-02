from benchmark import Benchmark
import helper

helper.load_backends()

code = """
(define (tak x y z)
  (if (not (< y x))
      z
      (tak (tak (- x 1) y z)
           (tak (- y 1) z x)
           (tak (- z 1) x y))))
"""

def call_tak(vm):
    for case in [(7,  (18, 12, 6)),
                 (15, (30, 15, 9)),
                 (10, (33, 15, 9)),
                 (15, (40, 15, 9))]:
        scm = vm.apply(vm.get("tak"), [vm.toscheme(x) for x in case[1]])
        assert vm.fromscheme(scm) == case[0]

bm = Benchmark(title="tak benchmark", repeat=3)
for backend in helper.BACKENDS:
    vm = helper.VM(backend=backend)
    vm.eval(vm.compile(code))
    bm.measure(backend, call_tak, vm)

helper.report(bm.report())

