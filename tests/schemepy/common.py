import os
from schemepy import types

try:
    backend = os.environ['BACKEND']
except KeyError:
    raise Exception, "You need to specify the BACKEND environment variable."

try:
    exec("from schemepy.%s import %s as backend" % (backend, backend))
except ImportError:
    raise Exception("Backend named %s doesn't exist." % backend)

VM = backend.VM
compiler = backend.Compiler
