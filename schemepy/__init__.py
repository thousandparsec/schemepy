# This package is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This package is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this package; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

import os
from exceptions import BackendNotFoundError

__all__ = ('VM', 'version')

# version is a tuple of major, minor and patch number
version = (1, 0, 0)

def VM(backend=None, profile="r5rs"):
    """\
    Get a VM.
 
    'backend' can be used to specify the backend wanted to use.
    Currently supported backends include:
     - "guile"
     - "mzscheme"
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
        backend_mod = find_backend()
    else:
        backend_mod = get_backend(backend)
        if backend_mod is None:
            raise BackendNotFoundError, "No such backend %s" % backend

    return backend_mod.VM(profile)


# All supported backends. The last one is pure-Python fallback.
SUPPORTED_BACKENDS = ['guile', 'mzscheme', 'skime']

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
