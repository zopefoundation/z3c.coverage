=====================
Test Coverage Reports
=====================

The main objective of this package is to convert the text-based coverage
output into an HTML coverage report. This is done by specifying the directory
of the test reports and the desired output directory.

Luckily we already have the text input ready:

    >>> import os
    >>> import z3c.coverage
    >>> inputDir = os.path.join(
    ...     os.path.dirname(z3c.coverage.__file__), 'sampleinput')

Let's create a temporary directory for the output

    >>> import tempfile, shutil
    >>> tempDir = tempfile.mkdtemp(prefix='tmp-z3c.coverage-report-')

The output directory will be created if it doesn't exist already

    >>> outputDir = os.path.join(tempDir, 'report')

We can now create the coverage report as follows:

    >>> from z3c.coverage import coveragereport
    >>> coveragereport.main([inputDir, outputDir, '--quiet'])

Looking at the output directory, we now see several files:

    >>> print('\n'.join(sorted(os.listdir(outputDir))))
    all.html
    z3c.coverage.__init__.html
    z3c.coverage.coveragediff.html
    z3c.coverage.coveragereport.html
    z3c.coverage.html
    z3c.html

Let's clean up

    >>> shutil.rmtree(tempDir)


coverage.py support
~~~~~~~~~~~~~~~~~~~

We also support coverage reports generated by coverage.py 

    >>> inputFile = os.path.join(
    ...     os.path.dirname(z3c.coverage.__file__), 'sampleinput.coverage')

    >>> from z3c.coverage import coveragereport
    >>> coveragereport.main([
    ...     inputFile, outputDir, '-q',
    ...     '--path-alias=/home/mg/src/zopefoundation/z3c.coverage/src/z3c/coverage=%s'
    ...         % os.path.dirname(z3c.coverage.__file__),
    ...     '--strip-prefix=%s'
    ...         % os.path.realpath(os.path.dirname(os.path.dirname(
    ...             os.path.dirname(z3c.coverage.__file__)))),
    ... ])
    >>> print('\n'.join(sorted(os.listdir(outputDir))))
    all.html
    z3c.coverage.__init__.html
    z3c.coverage.coveragediff.html
    z3c.coverage.coveragereport.html
    z3c.coverage.html
    z3c.html

It also works without the --strip-prefix option, but the paths would be uglier
and not necessarily fixed (e.g. src/z3c/coverage/... versus
.tox/lib/python2.X/site/packages/z3c/coverage/..., depending on how you
run the tests).

    >>> coveragereport.main([
    ...     inputFile, outputDir, '-q',
    ...     '--path-alias=/home/mg/src/zopefoundation/z3c.coverage/src/z3c/coverage=%s'
    ...         % os.path.dirname(z3c.coverage.__file__),
    ... ])


`coveragereport.py` is a script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For convenience you can download the ``coveragereport.py`` module and run it
as a script:

  >>> import sys
  >>> sys.argv = ['coveragereport', inputDir, outputDir, '--quiet']

  >>> script_file = os.path.join(
  ...     z3c.coverage.__path__[0], 'coveragereport.py')

  >>> with open(script_file) as f:
  ...     code = compile(f.read(), script_file, 'exec')
  ...     exec(code, dict(__name__='__main__'))

Let's clean up

  >>> shutil.rmtree(tempDir)

