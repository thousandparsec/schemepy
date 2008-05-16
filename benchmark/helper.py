import sys
import os.path

sys.path.append(
    os.path.join(os.path.dirname(__file__), ".."))

from schemepy import VM
from benchmark import Benchmark


def read(file_name):
    io = open(file_name)
    cont = io.read()
    io.close()
    return cont


BACKENDS = ['guile', 'pyscheme']

def load_backends():
    """\
    Force the backends to be loaded. The loading time
    of the backends will be benchmarked separately.
    """
    for backend in BACKENDS:
        VM(backend=backend)

def report(report):
    """\
    Show the report.
    """
    print report
    
