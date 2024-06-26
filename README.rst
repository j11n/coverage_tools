Coverage Tools
###############

These files are a proof of concept for calculating test-coverage
using decorators to define the scope of each test.

* Run coverage as normal creating the .coverage database.
* Run the recalculate_coverage_using_decorators.py script to calculate 
  new coverage values based on the decorators added to the test files.

The script does the following:

* Parse python source files to get line-numbers for all classes, methods 
  and functions.
* Parse python test files to get the decorator information which defines
  which source code part a specific test-function tests.
* Combine the two parts above to get a dictionary the defines which 
  line-number are allowed for a specific context.
* Read the coverage database and remove contexts not allowed for a specific 
  line-number, output a new database.

The decorators does nothing while running the tests, they are used as
a placeholder for the functions that are tested by the decorated test-function.

bin/run_all.sh can be used to run an example located under the test directory.
Requires, pytest, pytest-cov, coverage see bin/requirements.txt

.. EOF
