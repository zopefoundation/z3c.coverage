============
z3c.coverage
============

This package contains tools to work with Python coverage data.

``coveragereport`` produces HTML reports from coverage data, with
syntax-highlighted source code and per-package aggregate numbers.

``coveragediff`` compares two sets of coverage reports and reports
regressions, that is, increases in the number of untested lines of code.

.. contents::


Using coveragereport
====================

::

    $ coveragereport --help
    Usage: coveragereport [options] [inputpath [outputdir]]

    Converts coverage reports to HTML.  If the input path is omitted, it defaults
    to coverage or .coverage, whichever exists.  If the output directory is
    omitted, it defaults to inputpath + /report or ./coverage-reports, depending
    on whether the input path points to a directory or a file.

    Options:
      -h, --help            show this help message and exit
      -q, --quiet           be quiet
      -v, --verbose         be verbose (default)
      --strip-prefix=PREFIX
                            strip base directory from filenames loaded from
                            .coverage
      --path-alias=PATH=LOCALPATH
                            define path mappings for filenames loaded from
                            .coverage

Example use with ``zope.testrunner``::

    $ bin/test --coverage=coverage
    $ coveragereport
    $ ln -s mypackage.html coverage/report/index.html
    $ xdg-open coverage/report/index.html
    $ xdg-open coverage/report/all.html

Example use with ``nose`` and ``coverage.py``::

    $ nosetests --with-coverage --cover-erase
    $ coveragereport --strip-prefix=/full/path/to/source/
    $ ln -s mypackage.html coverage-reports/index.html
    $ xdg-open coverage-reports/index.html
    $ xdg-open coverage-reports/all.html

Sample report:

.. image:: http://i.imgur.com/mkqA3.png

.. note:: You need `enscript <http://www.gnu.org/software/enscript/>`_
          installed and available in your ``$PATH`` if you want syntax
          highlighting.


Using coveragediff
==================

::

    Usage: coveragediff [options] olddir newdir

    Options:
      -h, --help         show this help message and exit
      --include=REGEX    only consider files matching REGEX
      --exclude=REGEX    ignore files matching REGEX
      --email=ADDR       send the report to a given email address (only if
                         regressions were found)
      --from=ADDR        set the email sender address
      --subject=SUBJECT  set the email subject
      --web-url=BASEURL  include hyperlinks to HTML-ized coverage reports at a
                         given URL

Usage example with ``zope.testrunner``::

    $ bin/test --coverage=coverage
    $ vi src/...
    $ mv coverage coverage.old
    $ bin/test --coverage=coverage
    $ coveragediff coverage.old coverage

You cannot use ``coveragediff`` with ``coverage.py`` data.  More on that below.

Output example::

    $ coveragediff coverage.old coverage
    my.package.module: 36 new lines of untested code
    my.package.newmodule: new file with 15 lines of untested code (out of 23)

Output with clickable links::

    $ coveragediff coverage.old coverage --web-url=http://example.com/coverage
    my.package.module: 36 new lines of untested code
    See http://example.com/coverage/my.package.module.html

    my.package.newmodule: new file with 15 lines of untested code (out of 23)
    See http://example.com/coverage/my.package.newmodule.html

Output via email, convenient for continuous integration::

    $ coveragediff coverage.old coverage --web-url=http://example.com/coverage \
                       --email 'Developers <dev@exmaple.com>' \
                       --from 'Buildbot <buildbot@example.com>'

That last example doesn't produce any output, but sends an email (via SMTP
to localhost:25).


Getting coverage data
=====================

zope.testrunner
---------------

`zope.testrunner <http://pypi.python.org/pypi/zope.testrunner>`_ can
produce a directory full of files named ``dotted.package.name.cover``
that contain source code annotated with coverage information.  To get
them, use ::

  bin/test --coverage=outdir/

Both ``coveragereport`` and ``coveragediff`` accept this as inputs.


coverage.py
-----------

`coverage.py <http://pypi.python.org/pypi/coverage>`_ can produce
a ``.coverage`` file, which is actually a Python pickle containing
(incomplete) coverage information.  To get it, use ::

  coverage run bin/testrunner

``coveragereport`` can take the ``.coverage`` file as an input, but it
also needs access to the matching source files.  And you have to manually
specify the absolute pathname prefix of your source tree so that the
report know how to translate filenames into dotted package names.  Also,
it's not enough to have *absolute* pathnames, you need to supply the
*canonical* absolute pathname (with no symlink segments), such as returned
by ``os.path.realpath``.  This is very inconvenient.  Sorry.

``coveragediff`` is unable to compare two ``.coverage`` files and report
regressions.  One reason for that is the incompleteness of the data format
(the pickle contains line numbers of executed statements, but doesn't
say which lines contain code and which ones are
blank/comments/continuation lines/excluded source lines).  The other
reason is simpler: nobody wrote the code. `;)`

Unfortunately ``coverage annotate`` does not produce files compatible
with ``coveragereport``/``coveragediff``.  This could also be remedied
if somebody wrote a patch.


.. note:: If you want to use a ``.coverage`` file produced on another machine
          or simply in a different working directory, you will need to
          tell ``coveragereport`` how to adjust the absolute filenames so that
          the sources can be found.  Use the ``--path-alias`` option for that.
          Alternatively you could use ``coverage combine`` to manipulate the
          ``.coverage`` file itself, as described in the documentation.

.. note:: ``.coverage`` files are Python pickles, which has important
          security ramifications.  You can craft a Pickle file that executes
          arbitrary code during load time.  **Do not ever attempt to use
          pickles received from untrusted sources.**


trace.py
--------

The ``*.cover`` annotated-source format produced by ``zope.testrunner``
actually comes from the Python standard library module `trace.py
<http://docs.python.org/library/trace>`_.  You can probably use trace.py
directly.  I've never tried.


Frequently Asked Questions
==========================

Why use z3c.coverage instead of coverage html?
----------------------------------------------

Some people prefer the look of the reports produced by z3c.coverage.
Some people find per-package coverage summaries or the tree-like navigation
convenient.

Should I use zope.testrunner's built-in coverage, or coverage run bin/test?
-----------------------------------------------------------------------------

``coverage.py`` is *much* faster, but using it (and hooking it up to z3c.coverage)
is perhaps less convenient.  E.g. if you use ``zc.buildout 1.5.x`` with
``zc.recipe.testrunner``, you will be unable to use ``coverage run bin/test``
because of mystic semi-broken site isolation magic of the former.

Did anyone actually ask any of these questions?
-----------------------------------------------

Does asking myself count?
