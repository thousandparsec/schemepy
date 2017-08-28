schemepy (pronounced Skimpy)
============================

This is an reimplementation of pyscheme using various supported C scheme
libraries for speed. If no C scheme libraries are available it will fall back to
the much slower pyscheme library.

It was designed to offer faster parsing of Thousand Parsec TPCL programs such
as:
 - tpserver-py
 - tpclient-py*
 - tpruledev

It is written in pure python using the python-ctypes library. This library comes
with python2.5 (it can be downloaded for earlier versions of python).

Planned supporting C scheme libraries (bold are already supported):
http://community.schemewiki.org/?scheme-faq-standards#implementations

 - [x] **guile**
 - [x] **mzscheme**
 - [ ] STklos - http://www.stklos.org/
 - [ ] Chicken
 - [ ] Elk - http://sam.zoy.org/elk/


API
=========================

```python
import schemepy as scheme

# Create a new scheme compiler A compiler converts text strings into
# an internal format, this allows you to compile something once and
# then evaluate it multiple times This is more efficent as parsing and
# compiling the text takes up the most significant amount of time.

c = scheme.Compiler()

<internal scheme structure> = c(<string>)

# Calling the compiler can throw a scheme.CompilerException, these have the
# following attributes,
#  e.lineno   - the line on which the error occured
#  e.position - the position the error was detected at
#  e.message  - a human readable message why this is not valid

# Create a new scheme empty vm
vm = scheme.VM()

# You can then install new functions into the vm using the following
#
# Functions must take <internal scheme structure> arguments and return a
# <internal scheme structure>.
#
# The function MUST NOT store any of the given structures.
vm.install_function(<name>, <python callable>)

# You can then do something like
#
# def myadd(a, b):
#   a = vm.fromscheme(a)
#   b = vm.fromscheme(b)
#
#   return vm.toscheme(a+b)

# You can also have autoconversion by doing the following, then the above
# function could read
#
# def myadd(a, b):
#    return a+b
vm.install_function(<name>, <python callable>, autoconvert=True)

# To evaluate scheme code just use the eval function. It must have been
# previously parsed by the scheme parser.
<internal scheme structure> = vm.eval(<internal scheme structure>)

# Get the python type
<internal scheme structure>.type()

# Convert to a python object - with complex objects this is only does one level.
<internal scheme structure>.topython()

# You can also call functions in the scheme enviroment directly
<internal scheme structure> = i.environment.cdr(<internal scheme structure>)
<internal scheme structure> = i.environment.car(<internal scheme structure>)

# The scheme library also provides some convience functions.

# These two functions allow you to convert from the internal scheme structures
# to python types.
# The functions will automatically map the following types,
#  - bool
#  - int
#  - float
#  - complex
#  - list
#  - dictionary
<internal scheme object> = scheme.toscheme(<python object>)
<python object> = scheme.topython(<internal scheme object>)
```

For further and detailed information of the interface, see
[docs/html/front_end.html](https://thousandparsec.github.io/schemepy/html/front_end.html).

License
=========================
This package is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This package is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this package; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
