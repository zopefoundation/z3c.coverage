#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Compare the test coverage between two versions.  The promary goal is to find
regressions in test coverage (newly added lines of code without tests, or
old lines of code that used to have tests but don't any more).

Usage: coveragediff.py [options] old-dir new-dir

The directories are expected to contain files named '<package>.<module>.cover'
with the format that Python's trace.py produces.
"""
from __future__ import print_function

import os
import re
import smtplib
import optparse

try:
    from email.MIMEText import MIMEText
except ImportError:  # pragma: nocover
    from email.mime.text import MIMEText


def matches(string, list_of_regexes):
    """Check whether a string matches any of a list of regexes.

        >>> matches('foo', map(re.compile, ['x', 'o']))
        True
        >>> matches('foo', map(re.compile, ['x', 'f$']))
        False
        >>> matches('foo', [])
        False

    """
    return any(regex.search(string) for regex in list_of_regexes)


def filter_files(files, include=(), exclude=()):
    """Filters a file list by considering only the include patterns, then
    excluding exclude patterns.  Patterns are regular expressions.

    Examples:

        >>> filter_files(['ivija.food', 'ivija.food.tests', 'other.ivija'],
        ...              include=['^ivija'], exclude=['tests'])
        ['ivija.food']

        >>> filter_files(['ivija.food', 'ivija.food.tests', 'other.ivija'],
        ...              exclude=['tests'])
        ['ivija.food', 'other.ivija']

        >>> filter_files(['ivija.food', 'ivija.food.tests', 'other.ivija'],
        ...              include=['^ivija'])
        ['ivija.food', 'ivija.food.tests']

        >>> filter_files(['ivija.food', 'ivija.food.tests', 'other.ivija'])
        ['ivija.food', 'ivija.food.tests', 'other.ivija']

    """
    if not include:
        include = ['.']  # include everything by default
    if not exclude:
        exclude = []     # exclude nothing by default
    include = list(map(re.compile, include))
    exclude = list(map(re.compile, exclude))
    return [fn for fn in files
            if matches(fn, include) and not matches(fn, exclude)]


def find_coverage_files(dir):
    """Find all test coverage files in a given directory.

    The files are expected to end in '.cover'.  Weird filenames produced
    by tracing "fake" code (like '<doctest ...>') are ignored.
    """
    return [fn for fn in os.listdir(dir)
            if fn.endswith('.cover') and not fn.startswith('<')]


def filter_coverage_files(dir, include=(), exclude=()):
    """Find test coverage files in a given directory matching given patterns.

    The files are expected to end in '.cover'.  Weird filenames produced
    by tracing "fake" code (like '<doctest ...>') are ignored.

    Include/exclude patterns are regular expressions.  Include patterns
    are considered first, then the results are trimmed by the exclude
    patterns.
    """
    return filter_files(find_coverage_files(dir), include, exclude)


def warn(filename, message):
    """Warn about test coverage regression.

        >>> warn('/tmp/z3c.somepkg.cover', '5 untested lines, ouch!')
        z3c.somepkg: 5 untested lines, ouch!

    """
    module = strip(os.path.basename(filename), '.cover')
    print('%s: %s' % (module, message))


def compare_dirs(olddir, newdir, include=(), exclude=(), warn=warn):
    """Compare two directories of coverage files."""
    old_coverage_files = filter_coverage_files(olddir, include, exclude)
    new_coverage_files = filter_coverage_files(newdir, include, exclude)

    old_coverage_set = set(old_coverage_files)
    for fn in sorted(new_coverage_files):
        if fn in old_coverage_set:
            compare_file(os.path.join(olddir, fn),
                         os.path.join(newdir, fn), warn=warn)
        else:
            new_file(os.path.join(newdir, fn), warn=warn)


def count_coverage(filename):
    """Count the number of covered and uncovered lines in a file."""
    covered = uncovered = 0
    with open(filename) as file:
        for line in file:
            if line.startswith('>>>>>>'):
                uncovered += 1
            elif len(line) >= 7 and not line.startswith(' ' * 7):
                covered += 1
    return covered, uncovered


def compare_file(oldfile, newfile, warn=warn):
    """Compare two coverage files."""
    old_covered, old_uncovered = count_coverage(oldfile)
    new_covered, new_uncovered = count_coverage(newfile)
    if new_uncovered > old_uncovered:
        increase = new_uncovered - old_uncovered
        warn(newfile, "%d new lines of untested code" % increase)


def new_file(newfile, warn=warn):
    """Look for uncovered lines in a new coverage file."""
    covered, uncovered = count_coverage(newfile)
    if uncovered:
        total = covered + uncovered
        msg = "new file with %d lines of untested code (out of %d)" % (
                    uncovered, total)
        warn(newfile, msg)


def strip(string, suffix):
    """Strip a suffix from a string if it exists:

        >>> strip('go bar a foobar', 'bar')
        'go bar a foo'
        >>> strip('go bar a foobar', 'baz')
        'go bar a foobar'
        >>> strip('allofit', 'allofit')
        ''

    """
    if string.endswith(suffix):
        string = string[:-len(suffix)]
    return string


def urljoin(base, *suburls):
    """Join base URL and zero or more subURLs.

    This function is best described by examples:

        >>> urljoin('http://example.com')
        'http://example.com/'

        >>> urljoin('http://example.com/')
        'http://example.com/'

        >>> urljoin('http://example.com', 'a', 'b/c', 'd')
        'http://example.com/a/b/c/d'

        >>> urljoin('http://example.com/', 'a', 'b/c', 'd')
        'http://example.com/a/b/c/d'

        >>> urljoin('http://example.com/a', 'b/c', 'd')
        'http://example.com/a/b/c/d'

        >>> urljoin('http://example.com/a/', 'b/c', 'd')
        'http://example.com/a/b/c/d'

    SubURLs should not contain trailing or leading slashes (with one exception:
    the last subURL may have a trailing slash).  SubURLs should not be empty.
    """
    if not base.endswith('/'):
        base += '/'
    return base + '/'.join(suburls)


class MailSender(object):
    """Send emails over SMTP"""

    connection_class = smtplib.SMTP

    def __init__(self, smtp_host='localhost', smtp_port=25):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def send_email(self, from_addr, to_addr, subject, body):
        """Send an email."""
        # Note that this won't handle non-ASCII characters correctly.
        # See http://mg.pov.lt/blog/unicode-emails-in-python.html
        msg = MIMEText(body)
        if from_addr:
            msg['From'] = from_addr
        if to_addr:
            msg['To'] = to_addr
        msg['Subject'] = subject
        smtp = self.connection_class(self.smtp_host, self.smtp_port)
        smtp.sendmail(from_addr, to_addr, msg.as_string())
        smtp.quit()


class ReportPrinter(object):
    """Reporter to sys.stdout."""

    def __init__(self, web_url=None):
        self.web_url = web_url

    def warn(self, filename, message):
        """Warn about test coverage regression."""
        module = strip(os.path.basename(filename), '.cover')
        print('%s: %s' % (module, message))
        if self.web_url:
            url = urljoin(self.web_url, module + '.html')
            print('See ' + url)
            print('')


class ReportEmailer(object):
    """Warning collector and emailer."""

    def __init__(self, from_addr, to_addr, subject, web_url=None,
                 mailer=None):
        if not mailer:
            mailer = MailSender()
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.subject = subject
        self.web_url = web_url
        self.mailer = mailer
        self.warnings = []

    def warn(self, filename, message):
        """Warn about test coverage regression."""
        module = strip(os.path.basename(filename), '.cover')
        self.warnings.append('%s: %s' % (module, message))
        if self.web_url:
            url = urljoin(self.web_url, module + '.html')
            self.warnings.append('See ' + url + '\n')

    def send(self):
        """Send the warnings (if any)."""
        if self.warnings:
            body = '\n'.join(self.warnings)
            self.mailer.send_email(self.from_addr, self.to_addr, self.subject,
                                   body)


def main():
    """Parse command line arguments and do stuff."""
    parser = optparse.OptionParser("usage: %prog [options] olddir newdir")
    parser.add_option('--include', metavar='REGEX',
                      help='only consider files matching REGEX',
                      action='append')
    parser.add_option('--exclude', metavar='REGEX',
                      help='ignore files matching REGEX',
                      action='append')
    parser.add_option('--email', metavar='ADDR',
                      help='send the report to a given email address'
                           ' (only if regressions were found)',)
    parser.add_option('--from', metavar='ADDR', dest='sender',
                      help='set the email sender address')
    parser.add_option('--subject', metavar='SUBJECT',
                      default='Unit test coverage regression',
                      help='set the email subject')
    parser.add_option('--web-url', metavar='BASEURL', dest='web_url',
                      help='include hyperlinks to HTML-ized coverage'
                           ' reports at a given URL')
    opts, args = parser.parse_args()
    if len(args) != 2:
        parser.error("wrong number of arguments")
    olddir, newdir = args
    if opts.email:
        reporter = ReportEmailer(
            opts.sender, opts.email, opts.subject, opts.web_url)
    else:
        reporter = ReportPrinter(opts.web_url)
    compare_dirs(olddir, newdir, include=opts.include, exclude=opts.exclude,
                 warn=reporter.warn)
    if opts.email:
        reporter.send()


if __name__ == '__main__':
    main()
