#!/usr/bin/python

# manage todo items

import sys
import os
import datetime
import re
import shutil

if len(sys.argv) < 2:
    print """\
Usage:
    todo.py todo
    todo.py done item
"""
    sys.exit(1)

def gen_filename(text):
    words = re.split("[^a-zA-Z]+", text)
    if words[-1] == '':
        words.pop()
    words = map(lambda w: w.lower(), words)
    filename = "%s-%s.txt" % (datetime.date.today().strftime("%m-%d"), "-".join(words))
    return os.path.join(os.path.dirname(__file__), "todo", filename)

def todo():
    filename = "/tmp/schemepy-todo-%d" % os.getpid()
    file = open(filename, "w")
    today = datetime.date.today()
    print >> file, """\
One-line description of this task
----------------------------------------------------------------------
                                                planned at: %s

Detailed description.
""" % today.strftime("%Y-%m-%d")
    file.close()
    os.system("vim %s" % filename)
    lines = open(filename, "r").readlines()
    file = open(gen_filename(lines[0]), "w")
    for line in lines:
        file.write(line)

def done(item):
    newname = os.path.basename(item)[5:]
    newname = datetime.date.today().strftime("%m-%d") + newname
    newname = os.path.join(os.path.dirname(__file__), "done", newname)
    shutil.move(item, newname)
    file = open(newname, "a")
    print >> file, """
----------------------------------------------------------------------
                                               finished at: %s

""" % datetime.date.today().strftime("%Y-%m-%d")
    file.close()
    os.system("vim + %s" % newname)

if sys.argv[1] == 'todo':
    todo()
elif sys.argv[1] == 'done':
    if len(sys.argv) < 3:
        print "Should provide the todo item"
        sys.exit(1)
    else:
        done(sys.argv[2])
    
