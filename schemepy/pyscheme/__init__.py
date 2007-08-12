"""Package to hold pyscheme together.

We also keep a few utility functions in here.
"""


__license__ = "MIT License"

import scheme
import pair
import parser
import symbol



def make_interpreter():
    """Simple utility function to make an pyscheme.scheme.Interpreter.
    Defaults to AnalyzingInterpreter for now."""
    return scheme.AnalyzingInterpreter()


def parse(s):
    """Parses string 's' into list structure."""
    return parser.parse(s)
