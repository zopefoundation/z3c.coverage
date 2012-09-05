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

  >>> import tempfile
  >>> tempDir = tempfile.mkdtemp(prefix='tmp-z3c.coverage-report-')

The output directory will be created if it doesn't exist already

  >>> outputDir = os.path.join(tempDir, 'report')

We can now create the coverage report as follows:

  >>> from z3c.coverage import coveragereport
  >>> coveragereport.main([inputDir, outputDir])

Looking at the output directory, we now see several files:

  >>> print '\n'.join(sorted(os.listdir(outputDir)))
  all.html
  z3c.coverage.__init__.html
  z3c.coverage.coveragediff.html
  z3c.coverage.coveragereport.html
  z3c.coverage.html
  z3c.html


API Tests
---------

``CoverageNode`` Class
~~~~~~~~~~~~~~~~~~~~~~

This class represents a node in the source tree. Simple modules are considered
leaves and do not have children. Let's create a node for the `z3c` namespace
first:

  >>> z3cNode = coveragereport.CoverageNode()

Before using the API, let's create a few more nodes and a tree from it:

  >>> coverageNode = coveragereport.CoverageNode()
  >>> z3cNode['coverage'] = coverageNode

  >>> reportNode = coveragereport.CoverageNode()
  >>> reportNode._covered, reportNode._total = 40, 134
  >>> coverageNode['coveragereport'] = reportNode

  >>> diffNode = coveragereport.CoverageNode()
  >>> diffNode._covered, diffNode._total = 128, 128
  >>> coverageNode['coveragediff'] = diffNode

  >>> initNode = coveragereport.CoverageNode()
  >>> initNode._covered, initNode._total = 0, 0
  >>> coverageNode['__init__'] = initNode

Let's now have a look at the coverage of the `z3c` namespace:

  >>> z3cNode.coverage
  (168, 262)

We can also ask for the percentile:

  >>> z3cNode.percent
  64
  >>> initNode.percent
  100

We can ask for the amount of uncovered lines:

  >>> z3cNode.uncovered
  94

Finally, we also can get a nice output:

  >>> print z3cNode
  64% covered (94 of 262 lines uncovered)


`index_to_filename()` function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Takes an indexed Python path and produces the cover filename for it:

  >>> coveragereport.index_to_filename(('z3c', 'coverage', 'coveragereport'))
  'z3c.coverage.coveragereport.cover'

  >>> coveragereport.index_to_filename(())
  ''

`index_to_nice_name()` function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Takes an indexed Python path and produces a nice "human-readable" string:

  >>> coveragereport.index_to_nice_name(('z3c', 'coverage', 'coveragereport'))
  '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;coveragereport'

  >>> coveragereport.index_to_nice_name(())
  'Everything'


`index_to_name()` function
~~~~~~~~~~~~~~~~~~~~~~~~~~

Takes an indexed Python path and produces a "human-readable" string:

  >>> coveragereport.index_to_name(('z3c', 'coverage', 'coveragereport'))
  'z3c.coverage.coveragereport'

  >>> coveragereport.index_to_name(())
  'everything'


`percent_to_colour()` function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Given a coverage percentage, this function returns a color to represent the
coverage:

  >>> coveragereport.percent_to_colour(100)
  'green'
  >>> coveragereport.percent_to_colour(92)
  'yellow'
  >>> coveragereport.percent_to_colour(85)
  'orange'
  >>> coveragereport.percent_to_colour(50)
  'red'


`get_svn_revision()` function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Given a path, the function tries to determine the revision number of the
file. If it fails, "UNKNOWN" is returned:

  >>> path = os.path.split(z3c.coverage.__file__)[0]
  >>> coveragereport.get_svn_revision(path) != 'UNKNOWN'
  True

  >>> coveragereport.get_svn_revision(path + '/__init__.py')
  'UNKNOWN'


`syntax_highlight()` function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This function takes a cover file, converts it to a nicely colored HTML output:

  >>> filename = os.path.join(
  ...     os.path.split(z3c.coverage.__file__)[0], '__init__.py')

  >>> print coveragereport.syntax_highlight(filename)
  <BLANKLINE>
  <I><FONT COLOR="#B22222"># Make a package.
  </FONT></I>

If the highlighing command is not available, no coloration is done:

  >>> command_orig = coveragereport.HIGHLIGHT_COMMAND
  >>> coveragereport.HIGHLIGHT_COMMAND = 'foobar %s'

  >>> print coveragereport.syntax_highlight(filename)
  # Make a package.
  <BLANKLINE>

  >>> coveragereport.HIGHLIGHT_COMMAND = command_orig


`coveragereport.py` is a script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For convenience you can download the ``coveragereport.py`` module and run it
as a script:

  >>> import sys
  >>> sys.argv = ['coveragereport', inputDir, outputDir]

  >>> script_file = os.path.join(
  ...     z3c.coverage.__path__[0], 'coveragereport.py')

  >>> execfile(script_file, dict(__name__='__main__'))

Defaults are chosen when no input and output dir is specified:

  >>> def make_coverage_reports_stub(path, report_path):
  ...     print path
  ...     print report_path

  >>> make_coverage_reports_orig = coveragereport.make_coverage_reports
  >>> coveragereport.make_coverage_reports = make_coverage_reports_stub

  >>> sys.argv = ['coveragereport']
  >>> coveragereport.main()
  coverage
  coverage/reports

  >>> coveragereport.make_coverage_reports = make_coverage_reports_orig

Let's clean up

  >>> import shutil
  >>> shutil.rmtree(tempDir)

