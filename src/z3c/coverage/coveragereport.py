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
"""Coverage Report

Convert trace.py coverage reports to HTML.

Usage: coveragereport.py [report-directory [output-directory]]

Locates plain-text coverage reports (files named
``dotted.package.name.cover``) in the report directory and produces HTML
reports in the output directory.  The format of plain-text coverage reports is
as follows: the file name is a dotted Python module name with a ``.cover``
suffix (e.g. ``zope.app.__init__.cover``).  Each line corresponds to the
source file line with a 7 character wide prefix.  The prefix is one of

  '       ' if a line is not an executable code line
  '  NNN: ' where NNN is the number of times this line was executed
  '>>>>>> ' if this line was never executed

You can produce such files with the Zope test runner by specifying
``--coverage`` on the command line, or, more generally, by using the
``trace`` module in the standard library.

$Id$
"""
__docformat__ = "reStructuredText"

import sys
import os
import datetime
import cgi
import subprocess
import optparse


HIGHLIGHT_COMMAND = ['enscript', '-q', '--footer', '--header', '-h',
                     '--language=html', '--highlight=python', '--color',
                     '-o', '-']

class CoverageNode(dict):
    """Tree node.

    Leaf nodes have no children (items() == []) and correspond to Python
    modules.  Branches correspond to Python packages.  Child nodes are
    accessible via the Python mapping protocol, as you would normally use
    a dict.  Item keys are non-qualified module names.
    """

    def __str__(self):
        covered, total = self.coverage
        uncovered = total - covered
        return '%s%% covered (%s of %s lines uncovered)' % \
               (self.percent, uncovered, total)

    @property
    def percent(self):
        """Compute the coverage percentage."""
        covered, total = self.coverage
        if total != 0:
            return int(100 * covered / total)
        else:
            return 100

    @property
    def coverage(self):
        """Return (number_of_lines_covered, number_of_executable_lines).

        Computes the numbers recursively for the first time and caches the
        result.
        """
        if not hasattr(self, '_total'): # first-time computation
            self._covered = self._total = 0
            for substats in self.values():
                covered_more, total_more = substats.coverage
                self._covered += covered_more
                self._total += total_more
        return self._covered, self._total

    @property
    def uncovered(self):
        """Compute the number of uncovered code lines."""
        covered, total = self.coverage
        return total - covered


def parse_file(filename):
    """Parse a plain-text coverage report and return (covered, total)."""
    covered = 0
    total = 0
    for line in file(filename):
        if line.startswith(' '*7) or len(line) < 7:
            continue
        total += 1
        if not line.startswith('>>>>>>'):
            covered += 1
    return (covered, total)


def get_file_list(path, filter_fn=None):
    """Return a list of files in a directory.

    If you can specify a predicate (a callable), only file names matching it
    will be returned.
    """
    return filter(filter_fn, os.listdir(path))


def filename_to_list(filename):
    """Return a list of package/module names from a filename.

    One example is worth a thousand descriptions:

        >>> filename_to_list('z3c.coverage.__init__.cover')
        ['z3c', 'coverage', '__init__']

    """
    return filename.split('.')[:-1]


def get_tree_node(tree, index):
    """Return a tree node for a given path.

    The path is a sequence of child node names.

    Creates intermediate and leaf nodes if necessary.
    """
    node = tree
    for i in index:
        node = node.setdefault(i, CoverageNode())
    return node


def create_tree(filelist, path):
    """Create a tree with coverage statistics.

    Takes the directory for coverage reports and a list of filenames relative
    to that directory.  Parses all the files and constructs a module tree with
    coverage statistics.

    Returns the root node of the tree.
    """
    tree = CoverageNode()
    for filename in filelist:
        tree_index = filename_to_list(filename)
        node = get_tree_node(tree, tree_index)
        filepath = os.path.join(path, filename)
        node._covered, node._total = parse_file(filepath)
    return tree


def traverse_tree(tree, index, function):
    """Preorder traversal of a tree.

    ``index`` is the path of the root node (usually []).

    ``function`` gets one argument: the path of a node.
    """
    function(tree, index)
    for key, node in tree.items():
        traverse_tree(node, index + [key], function)


def traverse_tree_in_order(tree, index, function, order_by):
    """Preorder traversal of a tree.

    ``index`` is the path of the root node (usually []).

    ``function`` gets one argument: the path of a node.

    ``order_by`` gets one argument a tuple of (key, node).
    """
    function(tree, index)
    for key, node in sorted(tree.items(), key=order_by):
        traverse_tree_in_order(node, index + [key], function, order_by)


def index_to_url(index):
    """Construct a relative hyperlink to a tree node given its path."""
    if index:
        return '%s.html' % '.'.join(index)
    return 'index.html'


def index_to_filename(index):
    """Construct the plain-text coverage report filename for a node."""
    if index:
        return '%s.cover' % '.'.join(index)
    return ''


def index_to_nice_name(index):
    """Construct an indented name for the node given its path."""
    if index:
        return '&nbsp;' * 4 * (len(index) - 1) + index[-1]
    else:
        return 'Everything'


def index_to_name(index):
    """Construct the full name for the node given its path."""
    if index:
        return '.'.join(index)
    return 'everything'


def percent_to_colour(percent):
    if percent == 100:
        return 'green'
    elif percent >= 90:
        return 'yellow'
    elif percent >= 80:
        return 'orange'
    else:
        return 'red'


def print_table_row(html, node, file_index):
    """Generate a row for an HTML table."""
    covered, total = node.coverage
    uncovered = total - covered
    percent = node.percent
    nice_name = index_to_nice_name(file_index)
    if not node.keys():
        nice_name += '.py'
    else:
        nice_name += '/'
    print >> html, '<tr><td><a href="%s">%s</a></td>' % \
                   (index_to_url(file_index), nice_name),
    print >> html, '<td style="background: %s">&nbsp;&nbsp;&nbsp;&nbsp;</td>' % \
                   (percent_to_colour(percent)),
    print >> html, '<td>covered %s%% (%s of %s uncovered)</td></tr>' % \
                   (percent, uncovered, total)


HEADER = """
    <html>
      <head><title>Test coverage for %(name)s</title>
      <style type="text/css">
        a {text-decoration: none; display: block; padding-right: 1em;}
        a:hover {background: #EFA;}
        hr {height: 1px; border: none; border-top: 1px solid gray;}
        .notcovered {background: #FCC;}
        .footer {margin: 2em; font-size: small; color: gray;}
      </style>
      </head>
      <body><h1>Test coverage for %(name)s</h1>
      <table>
    """


FOOTER = """
      <div class="footer">
      %s
      </div>
    </body>
    </html>"""


def generate_html(output_filename, tree, my_index, info, path, footer=""):
    """Generate HTML for a tree node.

    ``output_filename`` is the output file name.

    ``tree`` is the root node of the tree.

    ``my_index`` is the path of the node for which you are generating this HTML
    file.

    ``info`` is a list of paths of child nodes.

    ``path`` is the directory name for the plain-text report files.
    """
    html = open(output_filename, 'w')
    print >> html, HEADER % {'name': index_to_name(my_index)}
    info = [(get_tree_node(tree, node_path), node_path) for node_path in info]
    def key((node, node_path)):
        return (len(node_path), -node.uncovered, node_path and node_path[-1])
    info.sort(key=key)
    for node, file_index in info:
        if not file_index:
            continue # skip root node
        print_table_row(html, node, file_index)
    print >> html, '</table><hr/>'
    if not get_tree_node(tree, my_index):
        file_path = os.path.join(path, index_to_filename(my_index))
        text = syntax_highlight(file_path)
        def color_uncov(line):
            # The line must start with the missing line indicator or some HTML
            # was put in front of it.
            if line.startswith('&gt;'*6) or '>'+'&gt;'*6 in line:
                return ('<div class="notcovered">%s</div>'
                        % line.rstrip('\n'))
            return line
        text = ''.join(map(color_uncov, text.splitlines(True)))
        print >> html, '<pre>%s</pre>' % text
    print >> html, FOOTER % footer
    html.close()


def syntax_highlight(filename):
    """Return HTML with syntax-highlighted Python code from a file."""
    # TODO: use pygments instead
    try:
        pipe = subprocess.Popen(HIGHLIGHT_COMMAND + [filename],
                            stdout=subprocess.PIPE)
        text, stderr = pipe.communicate()
        if pipe.returncode != 0:
            raise OSError
    except OSError:
        # Failed to run enscript; maybe it is not installed?  Disable
        # syntax highlighting then.
        text = cgi.escape(file(filename).read())
    else:
        text = text[text.find('<PRE>')+len('<PRE>'):]
        text = text[:text.find('</PRE>')]
    return text


def generate_htmls_from_tree(tree, path, report_path, footer=""):
    """Generate HTML files for all nodes in the tree.

    ``tree`` is the root node of the tree.

    ``path`` is the directory name for the plain-text report files.

    ``report_path`` is the directory name for the output files.
    """
    def make_html(node, my_index):
        info = []
        def list_parents_and_children(node, index):
            position = len(index)
            my_position = len(my_index)
            if position <= my_position and index == my_index[:position]:
                info.append(index)
            elif (position == my_position + 1 and
                  index[:my_position] == my_index):
                info.append(index)
            return
        traverse_tree(tree, [], list_parents_and_children)
        output_filename = os.path.join(report_path, index_to_url(my_index))
        if not my_index:
            return # skip root node
        generate_html(output_filename, tree, my_index, info, path, footer)
    traverse_tree(tree, [], make_html)


def generate_overall_html_from_tree(tree, output_filename, footer=""):
    """Generate an overall HTML file for all nodes in the tree."""
    html = open(output_filename, 'w')
    print >> html, HEADER % {'name': ', '.join(sorted(tree.keys()))}
    def print_node(node, file_index):
        if file_index: # skip root node
            print_table_row(html, node, file_index)
    def sort_by((key, node)):
        return (-node.uncovered, key)
    traverse_tree_in_order(tree, [], print_node, sort_by)
    print >> html, '</table><hr/>'
    print >> html, FOOTER % footer
    html.close()


def create_report_path(report_path):
    if not os.path.exists(report_path):
        os.makedirs(report_path)


def filter_fn(filename):
    """Filter interesting coverage files.

        >>> filter_fn('z3c.coverage.__init__.cover')
        True
        >>> filter_fn('z3c.coverage.tests.cover')
        False
        >>> filter_fn('z3c.coverage.tests.test_foo.cover')
        False
        >>> filter_fn('z3c.coverage.ftests.test_bar.cover')
        False
        >>> filter_fn('z3c.coverage.testing.cover')
        True
        >>> filter_fn('z3c.coverage.testname.cover')
        True
        >>> filter_fn('something-unrelated.txt')
        False
        >>> filter_fn('<doctest something-useless.cover')
        False

    """
    parts = filename.split('.')
    return (filename.endswith('.cover') and
            not filename.startswith('<') and
            'tests' not in parts and
            'ftests' not in parts)


def make_coverage_reports(path, report_path, verbose=True):
    """Convert reports from ``path`` into HTML files in ``report_path``."""
    create_report_path(report_path)
    filelist = get_file_list(path, filter_fn)
    if verbose:
        print "Loading coverage reports from %s" % path
    tree = create_tree(filelist, path)
    if verbose:
        print tree
    rev = get_svn_revision(os.path.join(path, os.path.pardir))
    timestamp = str(datetime.datetime.utcnow())+"Z"
    footer = "Generated for revision %s on %s" % (rev, timestamp)
    generate_htmls_from_tree(tree, path, report_path, footer)
    generate_overall_html_from_tree(
        tree, os.path.join(report_path, 'all.html'), footer)
    if verbose:
        print "Generated HTML files in %s" % report_path


def get_svn_revision(path):
    """Return the Subversion revision number for a working directory."""
    try:
        pipe = subprocess.Popen(['svnversion', path], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = pipe.communicate()
        rev = stdout.strip()
    except OSError:
        rev = ""
    if not rev:
        rev = "UNKNOWN"
    return rev


def main(args=None):
    """Process command line arguments and produce HTML coverage reports."""

    parser = optparse.OptionParser(
        "usage: %prog [options] [inputdir [outputdir]]",
        description=
            'Converts trace.py coverage reports to HTML.'
            '  If the input directory is omitted, it defaults to ./coverage.'
            '  If the output directory is omitted, it defaults to'
            ' ./coverage/report.')

    parser.add_option('-q', '--quiet', help='be quiet',
                      action='store_const', const=0, dest='verbose')
    parser.add_option('-v', '--verbose', help='be verbose (default)',
                      action='store_const', const=1, dest='verbose', default=1)

    if args is None:
        args = sys.argv[1:]
    opts, args = parser.parse_args(list(args))

    if len(args) > 0:
        path = args[0]
    else:
        path = 'coverage'

    if len(args) > 1:
        report_path = args[1]
    else:
        report_path = 'coverage/reports'

    if len(args) > 2:
        parser.error("too many arguments")

    make_coverage_reports(path, report_path, verbose=opts.verbose)


if __name__ == '__main__':
    main()
