======================================
Type mapping between Python and Scheme
======================================

.. contents::

This document described the type mapping between Scheme and Python.

Cons
====

A cons (a.k.a pair) in Scheme can be regards as many things: pair,
list, alist, plist or even tree. Instead of guessing what it will map
to, it is mapped to a special type ``schemepy.cons``. And helper
methods will be provided by ``schemepy.cons`` to convert into other
types (e.g. list, dict) explicitly.

Both ``car`` and ``cdr`` of a ``schemepy.cons`` will be converted to
Python value automatically and lazily when accessed.

* when it is a valid list, the ``tolist`` method can be called to
  convert it to a list. Or else exception will be thrown. FIXME: define
  the exception hierarchy. So ``(1 2 3)`` can be converted to list but
  not ``(1 2 . 3)``.

  when converted back, it should be still a list instead of a vector.
* when it is a valid alist, the ``todict`` method can be called to
  convert it to a dict. Or esle exception will be thrown.

  when converted back, it should be still an alist instead of a hash.

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
``schemepy.symbol``. The same symbol in Scheme should be mapped to the
same ``schemepy.symbol`` object in Python.

procedure
=========

A procedure/lambda in Scheme can be converted to a callable object in
Python. When converting back, it should be *the same* procedure.

A Python callable can also be converted to a Scheme procedure, which
can be called in Scheme.

object
======

Most Scheme implementations have OO hierarchy defined. Generic object
in Scheme will be represented in Python as a binary data. This is not
very useful, but it is guaranteed when converting back, it should be
*the same* object to the original one.

In the future, automatically mapping between Scheme object and Python
object might be considered.

big integer
===========

Scheme and Python both have arbitrary precesion integer. But they are
of different representation in memory, currently, they are converted
by first printing to a string and then read back. It is a bit slow but
fairly acceptable when converting back and forth of big integer is not
common.


