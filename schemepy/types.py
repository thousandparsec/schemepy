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
    "A Symbol object mapping to a Scheme symbol"

    symbols = {}
    __slots__ = '_name'
    
    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return "<symbol %s>" % self.name.__repr__()

    def get_name(self):
        return self._name
    def set_name(self, value):
        raise AttributeError, "Can't modify symbol's name."
    name = property(get_name, set_name, "name of the symbol")
        
    @staticmethod
    def intern(name):
        if type(name) is Symbol:
            return name
        sym = Symbol.symbols.get(name)
        if sym:
            return sym
        else:
            sym = Symbol(name)
            Symbol.symbols[name] = sym
            return sym

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
