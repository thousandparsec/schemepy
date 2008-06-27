#!/usr/bin/python

#
# generate index.html
#

import os
import re
import sys

########################################
# Generate git commit log
########################################
def git_ensure_on_branch(branch):
    "Make sure git is on the branch. Die if there's no such branch."
    text = os.popen("git-branch").read()
    if not re.search('^\* %s$' % branch, text, re.MULTILINE):
        if not re.search('^  %s$' % branch, text, re.MULTILINE):
            print "Fatal: no such branch '%s'" % branch
            sys.exit(1)
        os.system("git-checkout %s" % branch)

GIT_LOG_FORMAT = "format:%an\n%ci\n%s\n%H\n"
def git_get_short_log(n):
    "Get short log of the last n commits."
    logs = os.popen('git-log --pretty="%s" "HEAD~%d"..' %
                    (GIT_LOG_FORMAT, n)).read().strip().split("\n\n")
    return [git_parse_log(log) for log in logs]

GIT_LOG_KEYS = ['author', 'date', 'comment', 'hash']
def git_parse_log(log):
    "Parse the log to create a dict."
    return dict(zip(GIT_LOG_KEYS, log.split("\n")))

def git_gen_html(logs):
    "Generate html doc from logs."
    def gen_log(log):
        return "<tr><td>" + log['date'] + \
               "</td><td>" + log['author'] + \
               "</td><td class='comment'>" + log['comment'] + \
               "</td><td>" + gen_url(log) + \
               "</td></tr>"
    def gen_url(log):
        BASE = "http://git.thousandparsec.net/gitweb/gitweb.cgi?p=schemepy.git;a="
        params = ["commit;h=%s" % log['hash'],
                  "commitdiff;h=%s" % log['hash'],
                  "tree;h=%s;hb=%s" % (log['hash'], log['hash']),
                  "snapshot;h=%s" % log['hash']]
        names = ['commit', 'commitdiff', 'tree', 'snapshot']
        urls = ['<a href="%s%s">%s</a>' % (BASE, param, name)
                for param, name in zip(params, names)]
        return ' | '.join(urls)

    return '<table class="git-shortlog">\n' + \
           '\n'.join([gen_log(log) for log in logs]) + \
           '\n</table>'

def git_gen():
    git_ensure_on_branch("master")
    logs = git_get_short_log(10)
    return git_gen_html(logs)




########################################
# Generate index.html
########################################
TEMPLATE = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
	  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <title>Schemepy</title>
    <link href="html/styles.css" rel="stylesheet" type="text/css" />
  </head>
  
  <body>
    <h1 class="title">Schemepy</h1>

    <h1>What is Schemepy?</h1>
    <p>Schemepy is a Python module that enables you to embed a Scheme
    interpreter in your program. It support various native Scheme
    implementations for speed. A fall back pure-Python implementaion
    is also available when no suitable native implementations
    available.</p>

    <h1>Document</h1>
    <ul>
      <li><a href="html/api.html">API</a>: The API of Schemepy.</li>
      <li><a href="html/front_end.html">Front end</a>: Document on the Schemepy front end.</li>
      <li><a href="html/type-mapping.html">Type Mapping</a>: The type mapping between Python value and Scheme value.</li>
    </ul>

    <h1>News</h1>
    <h2>Recent commits to the repository</h2>
    %s
    <a href="http://git.thousandparsec.net/gitweb/gitweb.cgi?p=schemepy.git;a=shortlog">more...</a>

    <h2>Recent post to mailing list</h2>
    <a href="http://www.thousandparsec.net/tp/pipermail.php/schemepy/">Mailing list archives</a>

    <h2>My recent blog posts on Schemepy</h2>
    <a href="http://pluskid.lifegoo.com/?cat=16">My recent blog posts on Schemepy</a>
  </body>
</html>
"""

def gen_index():
    "Generate index.html"
    index = open("doc/index.html", "w")
    content = TEMPLATE % (git_gen())
    index.write(content)
    index.close()


if __name__ == '__main__':
    gen_index()

