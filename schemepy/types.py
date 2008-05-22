import weakref

from schemepy.exceptions import *

class Cons(object):
    "A Cons object mapping to a Scheme cons pair"
    
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def __eq__(self, o):
        if type(o) is not Cons:
            return false
        return self.car == o.car and self.cdr == o.cdr

class Symbol(object):
    symbols = weakref.WeakValueDictionary({})

    def __new__(cls, name):
        """\
        Get the interned symbol of name. If no found, create
        a new interned symbol.
        """
        if cls.symbols.has_key(name):
            return cls.symbols[name]

        sym = object.__new__(cls)
        sym._name = name
        cls.symbols[name] = sym
        return sym

    def __eq__(self, other):
        return self is other

    def get_name(self):
        return self._name
    def set_name(self):
        raise AttributeError("Can't modify name of a symbol.")
    name = property(get_name, set_name)

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
