#!/usr/bin/env python
"""
Test suite for z3c.coverage
"""

import unittest
import doctest
import re

from zope.testing import renormalizing

from z3c.coverage.coveragereport import traverse_tree_in_order


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
