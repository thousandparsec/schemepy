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
        sym = Symbol.symbols.get(name)
        if sym:
            return sym
        else:
            sym = Symbol(name)
            Symbol.symbols[name] = sym
            return sym

class Lambda(object):
    "A Lambda object mapping to a Scheme procedure"

    __slots__ = '_lambda', 'vm', 'shallow'

    def __init__(self, lam, vm, shallow):
        self._lambda = lam
        self.vm = vm
        self.shallow = shallow

    def __call__(self, *args, **options):
        """\
        Call this lambda.

        If this lambda is shallow, it should be called with Scheme values
        and return a Scheme value. Otherwise, it should be called with Python
        values and return a Python value.

        The vm where this lambda should run can be specified through the `vm'
        keyword argument.
        """
        vm = self.vm
        if options.get('vm'):
            vm = options['vm']
        if not vm:
            raise VMNotFoundError, "Lambda can't be called without a VM."
        
        if not self.shallow:
            args = [vm.toscheme(arg) for arg in args]
            
        result = vm.apply(self._lambda, args)

        if self.shallow:
            return result
        return self.vm.fromscheme(result)
