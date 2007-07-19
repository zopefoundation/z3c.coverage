#!/usr/bin/env python
"""
Test suite for z3c.coverage
"""

import unittest

# prefer the zope.testing version, if it is available
try:
    from zope.testing import doctest
except ImportError:
    import doctest


def test_suite():
    return unittest.TestSuite([
                doctest.DocFileSuite('coveragediff.txt'),
                doctest.DocTestSuite('z3c.coverage.coveragediff'),
                doctest.DocTestSuite('z3c.coverage.coveragereport'),
                               ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
