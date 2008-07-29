import weakref

from schemepy.exceptions import *

from skime.skime.types.symbol import Symbol
from skime.skime.types.pair import Pair as Cons

class Lambda(object):
    "A Lambda object mapping to a Scheme procedure"

    __slots__ = '_lambda', '_vm', '_shallow'

    def __init__(self, lam, vm, shallow):
        self._lambda = lam
        self._vm = vm
        self._shallow = shallow

    def get_vm(self):
        return self._vm
    def set_vm(self, val):
        raise AttributeError, "Readonly attribute: vm"
    def get_shallow(self):
        return self._shallow
    def set_shallow(self, val):
        raise AttributeError, "Readonly attribute: shallow"
    vm = property(get_vm, set_vm, "The VM this lambda created from")
    shallow = property(get_shallow, set_shallow, "Whether this lambda is a shallow wrapper or deep one")

    def __call__(self, *args):
        """\
        Call this lambda.

        If this lambda is shallow, it should be called with Scheme values
        and return a Scheme value. Otherwise, it should be called with Python
        values and return a Python value.
        """
        if not self._shallow:
            args = [self._vm.toscheme(arg) for arg in args]
        else:
            args = list(args)
            
        result = self._vm.apply(self._lambda, args)

        if self._shallow:
            return result
        return self._vm.fromscheme(result)
