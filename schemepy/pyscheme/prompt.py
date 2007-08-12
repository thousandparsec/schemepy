"""A small prompting class.

Danny Yoo (dyoo@hkn.eecs.berkeley.edu)

This hasn't been too documented yet.  There's some sample uses on
the bottom with the test() function below.

Slightly modified to work nicely with parentheses.
"""

__license__ = "MIT License"

## First, let's see if we can load up readline and make raw_input()
## nice to work with.
try:
    import readline
except ImportError: pass

import sys
import pprint

class Prompt:
    def __init__(self, name, quit_str = 'quit', quit_cmd=sys.exit,
                 callback=None):
        self.name = name
        self.quit_str = quit_str
        self.quit_cmd = quit_cmd
        self.callback = callback
        self.s = ''

    def makePrompt(self):
        if self.countOpenParens():
            return '[%s%d)] >>> ' % \
                   ('.' * (len(self.name)
                           - len(str(self.countOpenParens()))
                           - 1),
                    self.countOpenParens())
        else:
            return '[%s] >>> ' % self.name

    def countOpenParens(self):
        """Returns the number of open parens in self.s"""
        return self.s.count('(') - self.s.count(')')
        
    def promptLoop(self):
        while 1:
            try:
                self.s = self.s + '\n' + raw_input(self.makePrompt())
                if self.s == self.quit_str:
                    raise EOFError
                elif self.countOpenParens() > 0:
                    pass
                elif self.s.strip() and self.callback:
                    result = self.callback(self.s)
                    if result != None:
                        pprint.pprint(result)
                    self.s = ''
            except EOFError:
                print
                return self.quit_cmd()
            except KeyboardInterrupt:
                self.s = ''
                print



######################################################################

## Note: I should probably use the unit testing modules.
def test():
    def echoCallback(s):
        print s
    p = Prompt('test', callback=echoCallback)
    p.promptLoop()


if __name__ == '__main__':
    test()
