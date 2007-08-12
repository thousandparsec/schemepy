"""'pogo' defines primitives to do trampolined-style programming."""

import traceback

__license__ = "MIT License"


def pogo(bouncer):
    """A trampoline that bounces a single bouncer.  See:

    http://www.cs.indiana.edu/hyplan/sganz/publications/icfp99/paper.pdf
    """
    try:
        while True:
            if bouncer[0] == 'land':
                return bouncer[1]
            elif bouncer[0] == 'bounce':
                bouncer = bouncer[1](*bouncer[2])
            else:
                traceback.print_exc()
                raise TypeError, "not a bouncer"
    except TypeError:
        traceback.print_exc()
        raise TypeError, "not a bouncer"


def bounce(function, *args):
    """Returns a new trampolined value that continues bouncing on the
    trampoline."""
    return ('bounce', function, args)


def land(value):
    """Returns a new trampolined value that lands off the trampoline."""
    return ('land', value)


######################################################################
import unittest
class PogoTest(unittest.TestCase):
    def testFactorial(self):
        def iter_fact(n):
            result = 1
            while n != 0:
                result *= n
                n -= 1
            return result
        def tramp_fact(n, k=1):
            if n == 0:
                return land(k)
            return bounce(tramp_fact, n-1, k*n)
        self.assertEquals(6, pogo(tramp_fact(3)))
        self.assertEquals(6, pogo(tramp_fact(3)))
        for i in [1, 10, 100, 1000]:
            self.assertEquals(iter_fact(i), pogo(tramp_fact(i)))

    def testEvenOdd(self):
        def tramp_even(n):
            if n == 0:
                return land(True)
            return bounce(tramp_odd, n-1)
        def tramp_odd(n):
            if n == 0:
                return land(False)
            return bounce(tramp_even, n-1)
        for i in range(20) + [100, 1000, 10000]:
            self.assertEquals(i % 2 == 0, pogo(tramp_even(i)))
            


if __name__ == '__main__':
    unittest.main()
