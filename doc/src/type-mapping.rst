======================================
Type mapping between Python and Scheme
======================================

.. contents::

This document described the type mapping between Scheme and Python.

Cons
====

A Scheme cons can be considered as many different structures. Schemepy
will try to recognize it as alist, list and normal pair in that order,
and converted to dict, list and a Cons object respectively. It might
not necessary be a Python dict/list. If some housekeeping information
is needed, it might be an instance of a sub-class of the Python
dict/list.

When converted to Python value, both car and cdr of a cons will be
converted recursively. However, this behavior can be prohibited by
passing ``shallow=True`` to the ``fromscheme`` converting method.

alist
-----

A Scheme association list (``((1 . 2) (3 . 4))``) maps to a Python
dict (``{1:2, 3:4}``).

list
----

A Scheme list (``(1 2 3 4)``) maps to a Python list (``[1, 2, 3,
4]``). A Scheme empty list (``()``) maps a Python empty list (``[]``).

pair
----

A normal cons (a.k.a pair) in Scheme maps to a special type
``schemepy.types.Cons``.

vector
======

Most scheme implementation support the vector type, this can be mapped
to Python's list type. A vector can be converted to a Python list,
when converting back, it will still be a vector.

hash
====

Most scheme implementation support the hash type, this can be mapped
to Python's dict type. A hash can be converted to a Python dict, when
converting back, it will still be a hash.

symbol
======

A Scheme symbol will be converted to an instance of
``schemepy.types.Symbol``. The same symbol in Scheme should be mapped
to the same ``schemepy.types.Symbol`` object in Python.

procedure
=========

A procedure/lambda in Scheme can be converted to a callable object in
Python. When converting back, it should be *the same* procedure.

object
======

Most Scheme implementations have OO hierarchy defined. Generic object
in Scheme will be represented in Python as a binary data. This is not
very useful, but it is guaranteed when converting back, it should be
*the same* object to the original one.

big integer
===========

Scheme and Python both have arbitrary precesion integer. But they are
of different representation in memory, currently, they are converted
by first printing to a string and then read back. It is a bit slow but
fairly acceptable when converting back and forth of big integer is not
common.

Shallow vs Deep
===============

When converting from Scheme value, by default, Schemepy use deep
conversion. One can pass the named parameter ``shallow=True`` to get a
shallow conversion. This parameter apply to the following cases:

* cons: Including list, dict and plain cons. If shallow conversion is
  specified, the elements aren't converted to Python value.
* lambda: A Scheme lambda converted to Python callable with deep
  conversion can be called with Python values as parameters,
  otherwise, parameters should be converted to Scheme value before
  passing to the callable. So as to the return value.

Converting from Python to Scheme is always a *deep* conversion.
