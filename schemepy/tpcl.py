# Thousand Parsec Component Language support

from os import path

def setup(vm):
    """\
    Setup TPCL environment in vm.
    """
    vm.load(path.join(path.dirname(__file__),
                      "scheme", "tpcl.ss"))
