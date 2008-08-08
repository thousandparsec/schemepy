#!/usr/bin/python
# A script to do an release of schemepy

import sys
import os
from os import path
sys.path.append(path.join(path.dirname(__file__), '..'))

import schemepy

def compile_backend(bk):
    os.chdir('schemepy/%s' % bk)
    if 'Makefile' in os.listdir('.'):
        if os.system("make") != 0:
            raise Exception("Error compiling backend %s" % bk)
    os.chdir('../..')

BACKENDS = ['guile', 'mzscheme']
os.chdir(path.abspath(path.join(path.dirname(__file__), '..')))

for bk in BACKENDS:
    compile_backend(bk)
os.chdir("..")
os.system(("tar czf schemepy-%d.%d.%d.tar.gz schemepy" % schemepy.version) + \
          " --exclude .git --exclude log_book --exclude '*.pyc'" + \
          " --exclude '*.o' --exclude oldguile --exclude pyscheme" + \
          " --exclude .gitignore")
