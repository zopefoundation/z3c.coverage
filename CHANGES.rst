Changes
=======

2.1.0 (2017-04-24)
------------------

- Support (and require) coverage.py >= 4.0.

- Fix incorrect highlighting of missed lines when processing coverage.py data
  (broken since 2.0.2).

- Dropped Python 2.6 support.

- Added Python 3.4, 3.5 and 3.6 support.


2.0.3 (2015-11-09)
------------------

- Standardize namespace __init__.


2.0.2 (2013-10-01)
------------------

- Bug: coveragereport now also accepts non-ASCII chars in source files
  (also fix the case when enscript is not available).


2.0.1 (2013-10-01)
------------------

- Bug: coveragereport now also accepts non-ASCII chars in source files.


2.0.0 (2013-02-20)
------------------

- Added Python 3.3 and PyPy 1.9 support.

- Dropped Python 2.4 and 2.5 support.


1.3.1 (2012-10-24)
------------------

- Nicer PyPI description.  Doctests are tests, not docs.

- ``coveragereport`` now accepts ``--path-alias``.

- ``coveragereport``: new color step between yellow (90%) and green (100%), a
  yellowish-green (95%).


1.3.0 (2012-09-06)
------------------

- ``coveragereport`` now accepts ``--help``, ``--verbose`` and ``--quiet``
  options, with verbose being on by default.

- ``coveragereport`` now can handle .coverage files produced by
  http://pypi.python.org/pypi/coverage

- Bugfix: sorting by numbered of uncovered lines was broken in the
  ``all.html`` report.


1.2.0 (2010-02-11)
------------------

- Rename the ``coverage`` script to ``coveragereport``, to avoid name clashes
  with Ned Batchelder's excellent coverage.py.


1.1.3 (2009-07-24)
------------------

- Bug: Doctest did not normalize the whitespace in `coveragediff.txt`. For
  some reason it passes while testing independently, but when running all
  tests, it failed.


1.1.2 (2008-04-14)
------------------

- Bug: When a package path contained anywhere the word "test", it was ignored
  from the coverage report. The intended behavior, however, was to ignore
  files that relate to setting up tests.

- Bug: Sort the results of `os.listdir()` in `README.txt` to avoid
  non-deterministic failures.

- Bug: The logic for ignoring unit and functional test modules also used to
  ignore modules and packages called `testing`.

- Change "Unit test coverage" to "Test coverage" in the title -- it works
  perfectly fine for functional tests too.


1.1.1 (2008-01-31)
------------------

- Bug: When the package was released, the test which tests the availability of
  an SVN revision number failed. Made the test more reliable.


1.1.0 (2008-01-29)
------------------

- Feature: The ``main()`` coverage report function now accepts the arguments
  of the script as a function argument, making it easier to configure the
  script from buildout.

- Feature: When the report directory does not exist, the report generator
  creates it for you.

- Feature: Eat your own dog food by creating a buildout that can create
  coverage reports.

- Bug: Improved the test coverage to 100%.


1.0.1 (2007-09-26)
------------------

- Bug: Fixed meta-data.


1.0.0 (2007-09-26)
------------------

- First public release.


0.2.1
-----

- Feature: Added the ``--web`` option to ``coveragediff``.
- Feature: Added a test suite.


0.2.0
-----

- Feature: Added ``coveragediff.py``.


0.1.0
-----

- Initial release of ``coveragereport.py``.

