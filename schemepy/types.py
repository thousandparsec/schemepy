from schemepy.exceptions import *

class Cons(object):
    "A Cons object map to a Scheme cons pair"
    
    def __init__(self, car, cdr):
        self._car = car
        self._cdr = cdr

    def get_car(self):
        return self._car.fromscheme()
    def get_cdr(self):
        return self._cdr.fromscheme()
    def set_car(self, val):
        self._car = val.toscheme()
    def set_cdr(self, val):
        self._cdr = val.toscheme()
    car = property(get_car, set_car, "The car of the cons.")
    cdr = property(get_cdr, set_cdr, "The cdr of the cons.")

    def tolist(self):
        """\
        Convert to a Python list.
        """
        l = [self.car]
        cons = self.cdr
        while isinstance(cons, Cons):
            l.append(cons.car)
            cons = cons.cdr
        if cons == []:          # '() in Scheme
            return l
        else:
            raise ConversionError(self, "Not a valid Scheme list.")
        
