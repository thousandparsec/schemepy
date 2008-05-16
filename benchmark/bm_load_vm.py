"""\
This benchmark test the loading time of each backend.

But it seems to be hard to make this benchmark accurate. Because
it is only slow for the first time when a VM is to be loaded. Later
it will be very fast since all related stuffs are already in memory.
So repeating here just makes no help.
"""

from benchmark import Benchmark
import helper

def load_backend(backend):
    vm = helper.VM(backend=backend)

bm = Benchmark(title="Time to load the VM", repeat=1)

for backend in helper.BACKENDS:
    bm.measure(backend, load_backend, backend)

helper.report(bm.report())
