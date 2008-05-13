import os
from exceptions import BackendNotFoundError

__all__ = ['VM']

def VM(backend=None):
    """\
    Get a VM.

    'backend' can be used to specify the backend wanted to use.
    Currently supported backends include:
     - "guile"
    Leaving the 'backend' parameter alone the default value (None)
    will let Schemepy find a default backend for you.

    When finding a default backend, Schemepy first check the
    environment variable 'BACKEND', if it exist and is a valid
    value, use it. Otherwise, use an internal default value.
    """
    if backend is None:
        backend = default_backend()
    else:
        if not backends.get(backend):
            raise BackendNotFoundError, "No such backend %s" % backend
        backend = backends[backend]

    load_backend(backend)

    return backends_loaded[backend].VM()


# A dict of 'backend name' => 'backend module name'
backends = {
    "guile" : "guile"
    }
# A dict of 'backend module name' => 'backend module'
backends_loaded = {
    }
# The default 'backend module name'
default_backend_module = "guile"

def default_backend():
    """\
    Try to find a default backend to use.
    """
    backend = os.environ.get('BACKEND')
    if (not backend) or (not backends.get(backend)):
        backend = default_backend_module

    return backend

def load_backend(backend):
    """\
    Try to load the backend. The parameter is the backend module name.
    """
    mod = __import__("schemepy.%s.%s" % (backend, backend))
    backends_loaded[backend] = mod.__getattribute__(backend).__getattribute__(backend)
