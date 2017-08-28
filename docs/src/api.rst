===================
The API of Schemepy
===================

.. contents::

schemepy
========

The ``schemepy`` module manages various backends. Each backend is
loaded the first when required.

VM(backend, profile)
--------------------

Create a VM. Load the specified backend if not loaded yet.

Params:

* ``backend``: the default value is ``None``, which means Schemepy
  will find a suitable backend automatically. If the environment
  variable ``BACKEND`` is defined and valid, it will be used to select
  the backend. Otherwise, Schemepy will try a list of default backends
  one-by-one until a valid one (ie. there's corresponding native
  Scheme implementation installed in your system) is found. Or else it
  will fall back to the pure-Python Scheme implementation which is
  guaranteed to be always available.

  Here's a list of supported backends:

  * ``guile``
  * ``mzscheme``
  * ``skime``

* ``profile``: default is ``"r5rs"``. Used to
  specify the profile of the VM. Currently supported profiles are:

  * ``minimal``: A minimal Scheme environment.
  * ``r5rs``: A R5RS compatible Scheme environment.
  * ``tpcl``: A Thousand Parsec Component Language compatible environment.

VM
==

A VM object represents a Scheme VM. All communications with the Scheme
environment are through the VM object.

Different backend has different VM implementation, but the behavior
from the user's view should be identical in well-defined situations.

compile(code)
-------------

Compile a piece of Scheme code. The code should contain a single
s-expression (multiple s-expressions can be wrapped with the ``begin``
form as a single s-expression). In some backend where compiling is not
supported, this step may involve simple parsing or just return the
original code.

The return value is the compiled code, which can be arbitrary type
depends on the backend.

eval(compiled)
--------------

Evaluate the compiled code. Code should be compiled before evaluating,
and it should be compiled with the same VM.

The return value is a Scheme value.

load(path)
----------

Load a Scheme script and evaluate its contents in the top-level
environment of the VM. The load paths are not searched. ``path`` must
either be a full path or a path relative to the current directory
(Note: the *current directory* of the Scheme VM may be different from
the Python VM).

type(value)
-----------

Get the corresponding Python of the Scheme value. Note the returned
type is not necessarily the type of the Python object converted from
the Scheme value. In other words, ``vm.type(val)`` may not be the same
to ``type(vm.fromscheme(val))``. 

An example is a value converted from a generic Python object. When
using the ``type`` method, the result will be ``object``. But the
returned value will be the original object, which might be of any
type.

Not all Scheme value are able to be converted to a corresponding
Python object (refer to the `type mapping document
<type-mapping.html>`_ for more details). In this case,
``type(None)`` will be returned.

fromscheme(value, shallow)
--------------------------

Convert a Scheme value to a Python value. When the Scheme value is not
convertable, a ``schemepy.exceptions.ConversionError`` will be
raised. On what value is convertable and what is the converted result,
refer to the `type mapping document`_.

Params:

* ``value``: The Scheme value.
* ``shallow``: Default is ``False``. Refer to the `type mapping
  document (shallow vs deep) <type-mapping.html#shallow-vs-deep>`_ for
  more information.

toscheme(value, shallow)
------------------------

Convert a Python value to a Scheme value. Every Python object is
convertable. On the conversion rule of each type of object, refer to
the `type mapping document`_.

Params:

* ``value``: The Python value to be converted.
* ``shallow``: Default is ``False``. Refer to the `type mapping
  document (shallow vs deep) <type-mapping.html#shallow-vs-deep>`_ for
  more information.

apply(proc, args)
-----------------

Call a Scheme procedure.

Params:

* ``proc``: The Scheme procedure to call.
* ``args``: The arguments to the procedure. It should be a (Python) list of
  Scheme values.

The return value is a Scheme value.

define(name, value)
-------------------

Define a global variable in the VM.

Params:

* ``name``: Can be either a (Python) string or a
  ``schemepy.types.Symbol``. It is the name of the variable to be
  defined.
* ``value``: Should be a Scheme value. Used as the value of the
  variable.

get(name, default)
------------------

Get the value of a global variable in the VM.

Params:

* ``name``: The name of the variable to look up. Can be either a
  (Python) string or a ``schemepy.types.Symbol``.
* ``default``: Default is ``None``. It is returned when the variable
  is not defined.

repl()
------

Enter the read-eval-print loop. All errors occured will be caught in
the loop itself so this method will never throw.

exceptions
==========

The exceptions raised in Scheme will be caught and re-raised in
Python. Different backends have different exception hirarchies, but
Schemepy will (try to) map those exception hirarchies to the Schemepy
Scheme exception hirarchy.

All Scheme exceptions are sub-class of
``schemepy.exceptions.SchemeError``. They are:

* ``ScmSystemError``
* ``ScmNumericalError``
* ``ScmWrongArgType``
* ``ScmWrongArgNumber``
* ``ScmSyntaxError``
* ``ScmUnboundVariable``
* ``ScmMiscError``

