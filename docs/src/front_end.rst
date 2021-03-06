==================
Schemepy Front-end
==================

.. contents::

Schemepy front-end will define a unified interface. It will be
independent to the back-end used.

Phases
======

Using Schemepy to embed Scheme in the Python program involves 6
phases:

* Load and configure Schemepy.
* Create a VM.
* Extend the VM.
* Compile and run the Scheme program.

Load and configure Schemepy
===========================

If you've installed Schemepy properly in your ``sys.path``, loading
can be done simply by

.. sourcecode:: python

  import schemepy as scheme

The configuration is totally optional because usually the default
values can serve you well. But if you do want some customization, the
rule of thumb is to do it before you start using Schemepy.

Config which back-end to use
----------------------------

By default, Schemepy will search your system automatically and use the
first supported Scheme implementation as the back-end it found. If no
one found, it will use the build-in pure-Python Scheme
implementation. You can customize this process if you would prefer
one back-end to the other.

FIXME: describe how it is customized.

Config the behavior fo the front-end
------------------------------------

FIXME: describe how it is customized. 

Create a VM
===========

To create a new VM is simple:

.. sourcecode:: python

  vm = scheme.VM()

This VM will contain a basic environment where Scheme code can run
(FIXME: shall we define a standard environment? It it necessary? Or is
it feasible? This would have something to do with sandboxing).

Extend the VM
=============

The VM can be extended by adding global variables or primitives to the
environment.

Global variables
----------------

Adding global variables to the VM can be done through ``define`` or
``set``, the have similar semantic to ``define`` and ``set!`` in
Scheme.

.. sourcecode:: python

  vm.define("var", val)

The value should be a Scheme value. One can get a Scheme value by
calling ``scheme.toscheme(val)`` from a Python value ``val``.

Functions
---------

Functions can also be added to the VM by the same way as normal
objects:

.. sourcecode:: python

  def myadd(a, b):
    a = vm.fromscheme(a)
    b = vm.fromscheme(b)

    return vm.toscheme(a+b)

  vm.define("myadd", vm.toscheme(myadd, shallow=True))

Alternatively, you can omit the ``shallow=True`` to let Schemepy do
the convertion of the function parameters and return values for you
automatically.

.. sourcecode:: python

  def myadd2(a, b):
    return a+b

  vm.define("myadd2", vm.toscheme(myadd2)

Here's the map between Scheme type and Python type, more detailed
description can be found in `the type mapping document
<type-mapping.html>`_:

=================== ===============
Scheme Type         Python Type
=================== ===============
bool                bool
int                 int
float               float
complex             complex
symbol              schemepy.symbol
cons                schemepy.cons
vector              list
hash                dict
python data         Normal Object
object              Scheme Object
primitive function  callable
lambda              callable         
=================== ===============

Compile and run the Scheme program
==================================

Schemepy compiles Scheme source code into a compiled form. It can be
executed multiple times in different environments.

.. sourcecode:: python

  compiled = vm.compile(source)

When an error occured during parsing, a ``CompileException`` will be
thrown. It has the following attributes:

* ``lineno``: the line on which the error occured.
* ``position``: the position the error was detected at.
* ``message``: a human readable message why this is not valid.

To run a piece of compiled source code, just call ``eval`` method of
the VM:

.. sourcecode:: python

  result = vm.eval(compiled)

Like ``install_function``, the result can be automatically
converted. This behavior can be controlled by a global configuration
or through the ``autoconvert`` keyword parameter of ``eval``.
