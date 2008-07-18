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
    print "Generating homepage part of git log..."
    git_ensure_on_branch("master")
    logs = git_get_short_log(10)
    return git_gen_html(logs)


########################################
# Generate Blog summary
########################################
import feedparser

def blog_format_entry(entry):
    "Format a blog entry"
    return '<h3><a href="' + entry.link + '">' + \
           entry.title + '</a></h3>' + \
           '<small>' + entry.updated + '</small>\n' + \
           '<p>' + entry.summary[:-5] + \
           '<a href="' + entry.link + '">[...]</a></p>'

def blog_format(feed):
    "Format blog feed"
    return '\n'.join([blog_format_entry(entry) \
                      for entry in feed.entries[0:3]])

FEED_ADDR = 'http://pluskid.lifegoo.com/?cat=16&feed=rss2'
def blog_gen():
    print "Generating homepage part of blog posts..."
    feed = feedparser.parse(FEED_ADDR)
    return blog_format(feed)
    

########################################
# Generate mailing list posts
########################################
from urllib import urlopen
from datetime import date
import re

ML_ADDR_FMT = "http://www.thousandparsec.net/tp/pipermail.php/schemepy/%Y-%B/"
ML_PATTERN = r'<LI><A HREF="(\d{6}\.html)">([^>]*)\s</A><A NAME="\d\d">&nbsp;</A>\s<I>([^<]*)\s</I>'

def ml_format(base, posts):
    html = []
    for post in reversed(posts[-8:]):
        html.append('<li><a href="' + base + post[0] + '">' + \
                    post[1] + '</a> <i>' + post[2] + '</i></li>')
    return '<ul>\n' + '\n'.join(html) + '</ul>'

def ml_gen():
    print "Generating homepage part of mailing list posts..."
    base = date.today().strftime(ML_ADDR_FMT)
    doc = urlopen(base + 'date.html').read()
    posts = re.findall(ML_PATTERN, doc)
    return ml_format(base, posts)

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
    <img src="html/schemepy.png" alt="schemepy"
         style="float:right;margin:0 17px 5px 10px;" />
    <h1 class="title">Schemepy</h1>

    <h1>What is Schemepy?</h1>
    <p>Schemepy is a Python module that enables you to embed a Scheme
    interpreter in your program. It supports various native Scheme
    implementations for speed. A fall back pure-Python implementation
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

    <h2>My recent blog posts on Schemepy</h2>
    %s
    <a href="http://pluskid.lifegoo.com/?cat=16">more...</a>

    <h2>Recent posts on mailing list</h2>
    %s
    <a href="http://www.thousandparsec.net/tp/pipermail.php/schemepy/">Mailing list archives</a><br />
    <a href="http://www.thousandparsec.net/tp/mailman.php/listinfo/schemepy">Subscribe</a>
  </body>
</html>
"""

def gen_index():
    "Generate index.html"
    index = open("doc/index.html", "w")
    content = TEMPLATE % (git_gen(), blog_gen(), ml_gen())
    index.write(content)
    index.close()


if __name__ == '__main__':
    gen_index()

