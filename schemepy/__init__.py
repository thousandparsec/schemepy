import os
from exceptions import BackendNotFoundError

__all__ = ['VM']

def VM(backend=None, profile="scheme-report-environment"):
    """\
    Get a VM.
 
    'backend' can be used to specify the backend wanted to use.
    Currently supported backends include:
     - "guile"
     - "mzscheme"
     - "pyscheme"
     - "skime"
    Leaving the 'backend' parameter alone the default value (None)
    will let Schemepy find a default backend for you.
 
    When finding a default backend, Schemepy first check the
    environment variable 'BACKEND', if it exist and is a valid
    value, use it. Otherwise, use an internal default value.
 
    profile can be
     - scheme-report-environment (default)
     - null-environment
    """
    if backend is None:
        backend = find_backend()
    else:
        backend = get_backend(backend)
        if backend is None:
            raise BackendNotFoundError, "No such backend %s" % backend

    return backend.VM(profile)


# All supported backends. The last one is pure-Python fallback.
SUPPORTED_BACKENDS = ['guile', 'mzscheme', 'pyscheme', 'skime']

# A dict of 'backend name' => status
# 
#   if status is False, the backend is not loadable
#   otherwise, it is the loaded backend object
BACKENDS = {}

DEFAULT_BACKEND=None

def find_backend():
    global DEFAULT_BACKEND
    if DEFAULT_BACKEND:
        return DEFAULT_BACKEND
    
    backends = SUPPORTED_BACKENDS

    env_bk = os.environ.get('BACKEND')
    if env_bk in SUPPORTED_BACKENDS:
        backends = [env_bk] + backends
    
    for bk_name in backends:
        backend = get_backend(bk_name)
        if backend:
            DEFAULT_BACKEND = backend
            return backend

def get_backend(bk_name):
    backend = BACKENDS.get(bk_name)
    if backend:
        return backend
    if backend is False:                # not loadable
        return None
    
    try:
        mod = __import__("schemepy.%s.%s" % (bk_name, bk_name))
        backend = getattr(getattr(mod, bk_name), bk_name)
        BACKENDS[bk_name] = backend
        return backend
    except:
        BACKENDS[bk_name] = False
        return None
