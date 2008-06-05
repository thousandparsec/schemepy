"""\
This benchmark measure the performance of converting a normal
number between Python and Scheme.
"""


from benchmark import Benchmark
import helper

helper.load_backends()

def do_convert(vm, cases):
    for obj in cases:
        scm = vm.toscheme(obj)
        # we don't asser the euqality because sometimes the time to
        # test the equality may be longer than the conversion (e.g.
        # when testing two big chunk of string).
        vm.fromscheme(scm)


class Foo(object):
    pass
BIG_TEXT = open(__file__).read()

cases = [("integers", [1, 10, -5]),
         ("float numbers", [0.5, -3.2, 0.0]),
         ("big numbers", [2**33, -2**34, 10**10]),
         ("bool values", [True, False, False]),
         ("strings", ["foo", "", "baz"]),
         ("big string", [BIG_TEXT, BIG_TEXT, BIG_TEXT]),
         ("symbols", [helper.Symbol("foo"), helper.Symbol(""), helper.Symbol("bar")]),
         ("cons pairs", [helper.Cons(1, 2), helper.Cons([], []), helper.Cons(1, helper.Cons(2, []))]),
         ("lists", [[1, 2, 3], [1, 2, 3, 4], []]),
         ("dicts", [{1:1, 2:2}, {}, {1:10, 10:1}]),
         ("callables", [__import__, do_convert, list.sort]),
         ("objects", [Foo(), Foo(), object()])
         ]

for case in cases:
    bm = Benchmark(title="performance of converting " + case[0], repeat=1000)
    for backend in helper.BACKENDS:
        vm = helper.VM(backend=backend)
        bm.measure(backend, do_convert, vm, case[1])
    helper.report(bm.report())
