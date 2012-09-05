#!/usr/bin/env python
"""
Test suite for z3c.coverage
"""

import unittest
import doctest
import re

from zope.testing import renormalizing


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
        doctest.DocTestSuite(
            'z3c.coverage.coveragediff'),
        doctest.DocTestSuite(
            'z3c.coverage.coveragereport'),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
