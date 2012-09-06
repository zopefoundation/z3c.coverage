#!/usr/bin/env python
"""
Test suite for z3c.coverage
"""

import doctest
import os
import re
import shutil
import sys
import tempfile
import unittest

from zope.testing import renormalizing

import z3c.coverage
from z3c.coverage import coveragereport
from z3c.coverage.coveragereport import (
    Lazy, CoverageNode, index_to_nice_name, index_to_name, percent_to_colour,
    traverse_tree_in_order, get_svn_revision, syntax_highlight)


def doctest_Lazy():
    """Test for Lazy

        >>> class MyClass(object):
        ...     @Lazy
        ...     def foo(self):
        ...         print "computing foo"
        ...         return 42

    This is basic lazy evaluation

        >>> obj = MyClass()
        >>> obj.foo
        computing foo
        42

    The difference from @propetry is that the value is only computed once

        >>> obj.foo
        42

    Another difference is that you can override it

        >>> obj.foo = 25
        >>> obj.foo
        25

    To force recomputation, delete the cached value

        >>> del obj.foo
        >>> obj.foo
        computing foo
        42

    You can access the class attribute as well

        >>> MyClass.foo # doctest: +ELLIPSIS
        <z3c.coverage.coveragereport.Lazy object at ...>

    """


def doctest_CoverageNode():
    """Test for CoverageNode

        >>> root = CoverageNode()
        >>> root['z3c'] = CoverageNode()
        >>> root['z3c']['coverage'] = CoverageNode()
        >>> root['z3c']['coverage']['coveragereport'] = CoverageNode()
        >>> root['z3c']['coverage']['coveragereport'].covered = 40
        >>> root['z3c']['coverage']['coveragereport'].total = 134
        >>> root['z3c']['coverage']['coveragediff'] = CoverageNode()
        >>> root['z3c']['coverage']['coveragediff'].covered = 128
        >>> root['z3c']['coverage']['coveragediff'].total = 128
        >>> root['z3c']['coverage']['__init__'] = CoverageNode()
        >>> root['z3c']['coverage']['__init__'].covered = 0
        >>> root['z3c']['coverage']['__init__'].total = 0

    ``covered`` and ``total`` are lazily-computed properties that sum over
    their children, recursively

        >>> root.covered
        168
        >>> root.total
        262

    ``uncovered`` is also a lazily-computed property that computes the
    difference

        >>> root.uncovered
        94

    We can also ask for the percentile

        >>> root.percent
        64

    and avoid division by zero

        >>> root['z3c']['coverage']['__init__'].percent
        100

    There are helpers for traversal

        >>> root.get_at([]) is root
        True
        >>> root.get_at(['z3c', 'coverage']) is root['z3c']['coverage']
        True
        >>> root.get_at(['z3c', 'nosuch'])
        Traceback (most recent call last):
          ...
        KeyError: 'nosuch'

    and helpers for construction

        >>> root.set_at(['z3c', 'somethingelse'], CoverageNode())
        >>> root['z3c']['somethingelse']
        {}

    Finally, we also can get a nice output:

        >>> print root['z3c']
        64% covered (94 of 262 lines uncovered)

    """


def doctest_index_to_nice_name():
    """Test for index_to_nice_name

    Takes an indexed Python path and produces a nice "human-readable" string:

        >>> index_to_nice_name(['z3c', 'coverage', 'coveragereport'])
        '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;coveragereport'

        >>> index_to_nice_name([])
        'Everything'

    """


def doctest_index_to_name():
    """Test for index_to_name

    Takes an indexed Python path and produces a "human-readable" string:

        >>> index_to_name(['z3c', 'coverage', 'coveragereport'])
        'z3c.coverage.coveragereport'

        >>> index_to_name([])
        'everything'

    """


def doctest_percent_to_colour():
    """Test for percent_to_colour

    Given a coverage percentage, this function returns a color to represent the
    coverage:

        >>> percent_to_colour(100)
        'green'
        >>> percent_to_colour(92)
        'yellow'
        >>> percent_to_colour(85)
        'orange'
        >>> percent_to_colour(50)
        'red'

    """


def doctest_traverse_tree_in_order():
    """Test for traverse_tree_in_order

        >>> tree = dict(a=dict(b={}, c={}, d={}), b=dict(x={}, y={}, z={}))
        >>> def pr_index(tree, index):
        ...     print index
        >>> traverse_tree_in_order(tree, [], pr_index, lambda (k, n): k)
        []
        ['a']
        ['a', 'b']
        ['a', 'c']
        ['a', 'd']
        ['b']
        ['b', 'x']
        ['b', 'y']
        ['b', 'z']

    """


def doctest_get_svn_revision():
    """Test for get_svn_revision

    Given a path, the function tries to determine the revision number of the
    file. If it fails, "UNKNOWN" is returned:

        >>> path = os.path.dirname(z3c.coverage.__file__)
        >>> get_svn_revision(path) != 'UNKNOWN'
        ... # This will fail if you don't have svnversion in your $PATH
        True

        >>> get_svn_revision(path + '/nosuchpath')
        'UNKNOWN'

    """


def doctest_syntax_highlight_with_enscript():
    """Test for syntax_highlight

    This function takes a cover file, converts it to a nicely colored HTML output:

        >>> filename = os.path.join(
        ...     os.path.dirname(z3c.coverage.__file__), '__init__.py')

        >>> print syntax_highlight(filename)
        ... # this will fail if you don't have enscript in your $PATH
        <BLANKLINE>
        <I><FONT COLOR="#B22222"># Make a package.
        </FONT></I>

    """


def doctest_syntax_highlight_without_enscript():
    """Test for syntax_highlight

    If the highlighing command is not available, no coloration is done:

        >>> command_orig = coveragereport.HIGHLIGHT_COMMAND
        >>> coveragereport.HIGHLIGHT_COMMAND = ['aflkakhalkjdsjdhf']

        >>> filename = os.path.join(
        ...     os.path.dirname(z3c.coverage.__file__), '__init__.py')

        >>> print syntax_highlight(filename)
        # Make a package.
        <BLANKLINE>

        >>> coveragereport.HIGHLIGHT_COMMAND = command_orig

    """

def doctest_main_default_arguments():
    """Test for main()

    Defaults are chosen when no input and output dir is specified.

        >>> def make_coverage_reports_stub(path, report_path, **kw):
        ...     print path
        ...     print report_path

        >>> make_coverage_reports_orig = coveragereport.make_coverage_reports
        >>> coveragereport.make_coverage_reports = make_coverage_reports_stub

        >>> orig_argv = sys.argv
        >>> sys.argv = ['coveragereport']

        >>> tempDir = tempfile.mkdtemp(prefix='tmp-z3c.coverage-report-')
        >>> orig_cwd = os.getcwd()
        >>> os.chdir(tempDir)
        >>> os.mkdir('coverage')

        >>> coveragereport.main()
        coverage
        coverage/reports

        >>> os.rmdir('coverage')
        >>> coveragereport.main()
        .coverage
        coverage-reports

        >>> coveragereport.make_coverage_reports = make_coverage_reports_orig
        >>> sys.argv = orig_argv
        >>> os.chdir(orig_cwd)
        >>> shutil.rmtree(tempDir)

    """


def test_suite():
    checker = renormalizing.RENormalizing([
                # optparse in Python 2.4 prints "usage:" and "options:",
                # in 2.5 it prints "Usage:" and "Options:".
                (re.compile('^usage:'), 'Usage:'),
                (re.compile('^options:', re.MULTILINE), 'Options:'),
                                           ])
    return unittest.TestSuite([
        doctest.DocFileSuite(
            'README.txt', checker=checker,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite(
            'coveragediff.txt', checker=checker,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        doctest.DocTestSuite(),
        doctest.DocTestSuite(
            'z3c.coverage.coveragediff'),
        doctest.DocTestSuite(
            'z3c.coverage.coveragereport'),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
