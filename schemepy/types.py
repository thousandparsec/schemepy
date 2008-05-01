from schemepy.exceptions import *

class Cons(object):
    "A Cons object map to a Scheme cons pair"
    
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr
