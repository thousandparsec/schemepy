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
