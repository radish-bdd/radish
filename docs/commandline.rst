Command Line Usage
==================

This chapter describes how to use Radish from the command line. All it's
commands, options and arguments.


Run - Specify Feature files
---------------------------

All arguments which do not belong to any command line option are interpreted
as Feature files or Feature file locations. If the argument is a directory all
files ending with ``.feature`` will be run. It's possible to mix files and
directories:

.. code:: bash

  radish SomeFeature.feature myfeatures/


Run - Specify base directory
----------------------------

Radish searches for and imports *Step* and *Terrain* python files in the
``base directories`` which by default is set to the ``radish`` folder inside the
current working directory (a.k.a ``$PWD/radish``). To specify an alternate path
you may use the ``-b`` or ``--basedir`` command line option:

.. code:: bash

  radish -b tests/radish SomeFeature.feature
  radish --basedir tests/radish SomeFeature.feature

Since version v0.4.2 you can specify ``-b`` multiple times to import Python modules
containing steps and terrain functions from multiple locations:

.. code:: bash

    radish -b tests/radish -b custom/radish SomeFeature.feature

Since version v0.7.0 you can use multiple basedirs within one ``-b`` flag split
by a colon (:). Similar to the possibilities you've got with ``$PATH``.
On Windows it is not possbile to use a colon (:) because it is used
in almost any absolute path, e.g. ``C:\foo\bar``.
Since version v0.11.2 you can use a semicolon (;) on Windows for
multiple basedirs.


Run - Early exit
----------------

By default Radish will try to run all specified Scenarios even if there are
failed Scenarios during the run. If you want to abort the test run after the
first error occurred you can use the ``-e`` or ``--early-exit`` option:

.. code:: bash

  radish SomeFeature.feature -e
  radish SomeFeature.feature --early-exit


Run - Debug Steps
-----------------

Radish provides the ability to debug each step using a debugger. You can
enable that using ``--debug-steps`` command line option.

.. code:: bash

  radish --debug-steps SomeFeature.feature

The IPython debugger is used if present. If it isn't the standard Python debugger
is used instead. Please consult the official
`debugger documentation <https://docs.python.org/3/library/pdb.html>`_ for
the common debugger workflow and commands.

For example you can list the variables available by printing ``locals()``.

.. code:: python

    ipdb> locals()
    {'step': <radish.stepmodel.Step object at 0x7f4d5b6ca400>}

As you can see, when a failure happens inside the Step you can see the step
arguments such as ``step``.


Run - Show traceback on failure
-------------------------------

Radish can display a complete traceback in case a Step fails.
You can use the ``-t`` or ``--with-traceback`` command line option for that:

.. code:: bash

  radish SomeFeature.feature -t
  radish SomeFeature.feature --with-traceback


Run - Use custom marker to uniquely identify test run
-----------------------------------------------------

Radish supports marker functionality which is used to uniquely identify a
specific test run. By default the marker is set to the number of seconds from
the epoch (01/01/1970). You can specify your own marker using the ``-m`` or
``--marker`` command line option.

The marker is also displayed in the summary of a test run:

.. code:: bash

  radish SomeFeature.feature -m "My Marker"
  radish SomeFeature.feature --marker "My Marker"

  ... radish output

  Run My Marker finished within 0:0.001272 minutes

The marker is also passed into all the hooks defined in the terrain files.
To see example code please consult :ref:`terrain <tutorial#terrain_and_hooks>`.


Run - Profile
-------------

Radish allows you to pass custom data to a Terrain hook code or to the Step implementations
using the ``-p`` or ``--profile`` command line option. This can be used to
customize your test runs as needed.

The value specified to the ``-p`` / ``--profile`` command line option is made
available in ``world.config.profile``. Please see :ref:`tutorial#world` for
for an example.

A common usage of ``profile`` s setting it to some environment value such as
``stage`` or ``production``.

.. code:: bash

  radish SomeFeature.feature -p stage
  radish SomeFeature.feature --profile stage

Note: ``-p`` / ``--profile`` is being deprecated and will be removed in a future version of Radish. Please use ``-u`` / ``--user-data`` instead.  See :ref:`Arbitrary User Data <commandline#user_data>` for details.


Run - Dry run
-------------

Radish allows you to pass custom flags to a Terrain hook code or to Step implementations
using the ``-d`` or ``--dry-run`` command line option. This can be used to
customize your test runs as needed.

The ``-d`` / ``--dry-run`` command line switch is made available in
``world.config.dry_run`` which is set to ``True``.
Please see :ref:`tutorial#world` for an example.

.. code:: bash

  radish SomeFeature.feature -d
  radish SomeFeature.feature --dry-run

Run - Specifying Scenarios by id
--------------------------------

Radish can also runs specific scenarios by id using the ``-s`` or
``--scenarios`` command line option. The ids are scenarios indexed by the
parsing order. The first Scenario in the first Feature will have the id 1, the
second scenario the id 2. The Scenario ids are unique within all Features from
this run. The value can be a single Scenario id or a comma separated list of
Scenario ids:

You can use ``--write-ids`` command line switch to print Scenario ids.
Please consult `Run - Writing out Scenario and Step ids`_

.. code:: bash

  radish SomeFeature.feature -s 1
  radish SomeFeature.feature --scenarios 1,2,5,6


Run - Shuffle Scenarios
-----------------------

Radish can also shuffle the Scenarios by using the ``--shuffle`` command line
option. This is useful when you are trying to detect if any Scenario has
unintended side effects on other Scenarios.

.. code:: bash

  radish SomeFeature.feature --shuffle


Run - Specify certain Features and/or Scenarios by tags
-------------------------------------------------------

Radish is able to run only a selection of certain Features and/or Scenarios
using the ``--tags`` command line option.
You can specify the tags of Features/Scenarios which should be run. The command line
option value has to be a valid tag expression.
Radish uses `tag-expressions <https://github.com/timofurrer/tag-expressions>`_.
The following are some valid tag expressions:


.. code:: bash

  radish SomeFeature.feature --tags 'regression'
  radish SomeFeature.feature --tags 'good_case and in_progress'
  radish SomeFeature.feature --tags 'good_case'
  radish SomeFeature.feature --tags 'regression and good_case and not real_hardware'
  radish SomeFeature.feature --tags 'database or filesystem and bad_case'

Be aware that Scenarios inherit the tags from the Feature they are defined it.

To learn how to tag Features and Scenarios please refer to :ref:`tutorial#tags`
section.


Run - Work in progress
-------------------------------

Radish is able change the state of the outcome. Scenarios which
are still work in progress and are expected to fail, can be run with:

.. code:: bash

   radish SomeFeature.feature --wip

To count as a success all Scenarios in this Feature need to fail.
If a Scenario passes the run is failed. A suggested workflow is
to tag WIP Scenarios with a `@wip` tag an run your tests twice.

.. code:: bash

   radish SomeFeature.feature --wip --tags wip
   radish SomeFeature.feature --wip --tags 'not wip'



Run - Write BDD XML result file
-------------------------------

Radish can report it's test run results to a XML file after a test run using
the ``--bdd-xml`` command line switch. The command line option value must be
a file path where the XML file should be written to.

To write the XML file ``lxml`` is required. Install it with:

.. code:: bash

    pip install radish-bdd[bddxml]

.. code:: bash

  radish SomeFeature.feature --bdd-xml /tmp/result.xml

To understand the format BDD XML consult: :ref:`tutorial#bdd_xml_report`.


Run - Code Coverage
-------------------

Radish can use the ``coverage`` package to measure code coverage of the code run
during the tests using the ``--with-coverage`` command line option. You can also
limit which packages it generates metrics for by providing file paths or
package names using ``--cover-packages``. The ``--cover-packages`` command line option
is the ``--source`` command line switch used by ``coverage``.
See `coverage documention <https://coverage.readthedocs.io/en/latest/cmd.html#execution>`_

To use the code coverage feature you have to install the necessary extra dependencies with:

.. code:: bash

    pip install radish-bdd[coverage]

The following options are also available to configure the coverage measurement and report:

:--with-coverage:
    enables the coverage measurement
:--cover-packages:
    specify one or more packages to measure.
    Multiple package names have to be separated
    with a comma.
:--cover-append:
    append the coverage data to previously measured
    data.
:--cover-config-file:
    specify a custom coverage config file.
    By default the ``$PWD.coveragerc`` file
    is read if it exists.
:--cover-branches:
    include branch coverage into the measurement
:--cover-erase:
    erase all previously collected coverage data
:--cover-min-percentage:
    let the radish run file if the given
    coverage percentage is not reached
:--cover-html:
    generate an HTML coverage report
:--cover-xml:
    generate a XML coverage report


Run - Write Cucumber JSON file
------------------------------

Radish can report it's test run results to a Cucumber style JSON file after a
test run using the ``--cucumber-json`` command line option. The command line option
value must be a file path where the JSON file should be written to.

.. code:: bash

  radish SomeFeature.feature --cucumber-json /tmp/result.json

Documentation describing the format of the Cucumber JSON file can be found
here: https://www.relishapp.com/cucumber/cucumber/docs/formatters/json-output-formatter

Run - Write JUnit XML file
------------------------------

Radish can report it's test run results to a JUnit style XML file after a
test run using the ``--junit-xml`` command line option. The command line option
value must be a file path where the XML file should be written to.

.. code:: bash

  radish SomeFeature.feature --junit-xml /tmp/result.xml

Run - Log all features, scenarios, and steps to syslog
------------------------------------------------------

Radish provides the `--syslog` command line option which can be used to log all of your
features, scenarios, and steps to the syslog. The caveat here is this option is only
supported on systems where the Python standard library supports the system logger
(syslog). This command line option works well in UNIX and UNIX-like systems (Linux) but
will not work on Windows machines.

This can be especially useful for consolidating all of your logging data in one central
repository.

.. code:: bash

  radish SomeFeature.feature --syslog

If you are unfamiliar with the syslog feature, please consult the official `syslog
documentation <https://docs.python.org/3/library/syslog.html#module-syslog>`_.

Run - Debug code after failure
------------------------------

Radish debugging mechanisms include the ability to drop into either IPython debugger or
the Python debugger on code failures using the ``--debug-after-failure`` command
line option. Using IPython is preferred over the standard Python debugger.

If you are unfamiliar with the Python debugger please consult the official
`debugger documentation <https://docs.python.org/3/library/pdb.html>`_.

.. code:: bash

  radish SomeFeature.feature --debug-after-failure


Please consult `Run - Debug Steps`_ for debugging tips.


Run - Inspect code after failure
--------------------------------

Radish debugging mechanisms include the ability to drop into a IPython shell
upon code failures using the ``--inspect-after-failure`` command line option.

To inspect code with IPython install the necessary extra dependencies with:

.. code:: bash

    pip install radish-bdd[ipython-debugger]

.. code:: bash

  radish SomeFeature.feature --inspect-after-failure


Please consult `Run - Debug Steps`_ for debugging tips.


Run - Printing results to console
---------------------------------

Note: **Pending** state means "yet to be executed".

The Radish console output is aimed to be powerful and explicit.
It uses ANSI color codes and line 'overwriting' to format and color
the output to make it more user friendly.

The anatomy of the console output is a follows:

Executing Scenario Step sentences as well as entries in the Scenario Outline Example
and Scenario Loop tables are printed to the console first, colored in bold
yellow.

As the Scenario Steps, Scenario Outline Example entries and Scenario Loop
iterations have finished the execution the "ANSI line jump" is used to replace
the printed yellow lines with the outcome of the Step run which is colored in
bold green on success or bold red in case of failure.

Exception messages and tracebacks are printed upon failure below the failed Step,
Scenario Outline Example or Scenario Loop Iteration entry.

Radish provides several command line options to help you with console output
format.

A common use of Radish is to run it using a script or in a continuous integration
setup. Such setups usually do not support "ANSI" color codes or line jumps.
This is where the combined use of ``--no-ansi`` and ``--write-steps-once`` command
line options become handy.

The ``--no-ansi`` turns off every "ANSI" code which might make the output less readable
in a non ANSI ready environment -> like Windows or when redirecting the output to a file.
However, since doing that also disables line jumping the step runs
will be printed twice to the screen (first print is the executing step, the second is
the finished one). Without colors that double print is confusing and can be
turned off using ``--write-steps-once``.

.. code:: bash

  radish SomeFeature.feature --no-ansi
  radish SomeFeature.feature --no-ansi --write-steps-once

The ``--no-line-jump`` command line option disables the "overwriting" of the
yellow executing lines by the success or failure lines. This is helpful when
reviewing and debugging as it shows Steps first executing then finished. It also
allows for "print to console" style debugging to be used without ANSI codes
destroying them.

.. code:: bash

  radish SomeFeature.feature --no-line-jump


Run - dots output formatter
---------------------------

By default the `gherkin` output formatter is used.
This formatter prints the Features in a gherkin style.
In most of the cases that's the same as the input Feature File content.
This gherkin output formatter is rather verbose: all Features, Scenarios and Steps are printed.

You can use the `dots` output formatter with the `-f dots` command line option.
Every passed Scenario will be printed as a dot (`.`).
Other possible symbols are:

* `P` for *pending*
* `U` for *untested*
* `S` for *skipped*
* `F` for *failed*

If a Scenario has failed, the failed Step will be printed in the summary in the end:

.. code:: bash

    $ radish SomeFeature.feature -f dots

    features/SomeFeature.feature: ..FFF..

    Failures:
    features/SomeFeature.feature: Subtract numbers wrongly
        Then I expect the difference to be 3
          AttributeError: 'int' object has no attribute 'step'

    features/SomeFeature.feature: A Scenario Outline - row 0
        Then I expect the sum to be 3
          AssertionError: The expected sum 3 does not match actual sum 11

    features/SomeFeature.feature: A Scenario Outline - row 1
        Then I expect the sum to be 9
          AssertionError: The expected sum 9 does not match actual sum 17


    1 features (0 passed, 1 failed)
    7 scenarios (4 passed, 3 failed)
    20 steps (17 passed, 3 failed)
    Run 1545585467 finished within a moment


Run - Writing out Scenario and Step ids
---------------------------------------

Radish provides the `--write-ids` command line option which can be used to
enumerate Scenarios and Steps.

This can be useful for bug reporting.

.. code:: cucumber

    1. Scenario: Apple Blender
        1. Given I put couple of "apples" in a blender
        2. When I switch the blender on
        3. Then it should transform into "apple juice"

    2. Scenario: Pear Blender
        1. Given I put couple of "pears" in a blender
        2. When I switch the blender on
        3. Then it should transform into "pear juice"

It can also be useful when using the ``-s`` / ``--scenarios`` command line option
since the Scenarios are numbered in the run order.


.. _commandline#user_data:

Run - Specifying Arbitrary User Data on the command-line
--------------------------------------------------------

Radish allows you to specify arbitrary user data on the command-line as ``key=value`` pairs.
You can access the user data from your tests by accessing the ``world.config.user_data`` dictionary.

Note: All keys/values are treated as strings. If you specify the same key more than once, the last occurrence of the key will replace previous occurrences.

.. code:: bash

  radish SomeFeature.feature --user-data="my_key=1" --user-data="my_key2=my_value2" -u "my-key3=value3"


Show - Expand feature
---------------------

Radish Precondition decorated Scenarios are powerful but can be confusing to
read on the screen. For that Radish provides ``--expand`` command line option to
expand all the preconditions.

.. code:: bash

  radish show SomeFeature.feature --expand

Help Screen
-----------

Use the ``--help`` or ``-h`` option to show the following help screen:

.. code::

  Usage:
      radish show <features>
             [--expand]
             [--no-ansi]
      radish <features>...
             [-b=<basedir> | --basedir=<basedir>...]
             [-e | --early-exit]
             [--debug-steps]
             [-t | --with-traceback]
             [-m=<marker> | --marker=<marker>]
             [-p=<profile> | --profile=<profile>]
             [-d | --dry-run]
             [-s=<scenarios> | --scenarios=<scenarios>]
             [--shuffle]
             [--tags=<tags>]
             [--bdd-xml=<bddxml>]
             [--with-coverage]
             [--cover-packages=<cover_packages>]
             [--cover-append]
             [--cover-config-file=<cover_config_file>]
             [--cover-branches]
             [--cover-erase]
             [--cover-min-percentage=<cover_min_percentage>]
             [--cover-html=<cover_html_dir>]
             [--cover-xml=<cover_xml_file>]
             [--no-ansi]
             [--no-line-jump]
             [--write-steps-once]
             [--write-ids]
             [--cucumber-json=<ccjson>]
             [--junit-xml=<junitxml>]
             [--debug-after-failure]
             [--inspect-after-failure]
             [--syslog]
             [-u=<userdata> | --user-data=<userdata>...]
      radish (-h | --help)
      radish (-v | --version)

  Arguments:
      features                                    feature files to run

  Options:
      -h --help                                   show this screen
      -v --version                                show version
      -e --early-exit                             stop the run after the first failed step
      --debug-steps                               debugs each step
      -t --with-traceback                         show the Exception traceback when a step fails
      -m=<marker> --marker=<marker>               specify the marker for this run [default: time.time()]
      -p=<profile> --profile=<profile>            specify the profile which can be used in the step/hook implementation
      -b=<basedir> --basedir=<basedir>...         set base dir from where the step.py and terrain.py will be loaded. [default: $PWD/radish]
                                                  You can specify -b|--basedir multiple times. All files will be imported.
      -d --dry-run                                make dry run for the given feature files
      -s=<scenarios> --scenarios=<scenarios>      only run the specified scenarios (comma separated list)
      --shuffle                                   shuttle run order of features and scenarios
      --tags=<feature_tags>                       only run Scenarios with the given tags
      --expand                                    expand the feature file (all preconditions)
      --bdd-xml=<bddxml>                          write BDD XML result file after run
      --with-coverage                             enable code coverage
      --cover-packages=<cover_packages>           specify source code package
      --cover-append                              append coverage data to previous collected data
      --cover-config-file=<cover_config_file>     specify coverage config file [default: .coveragerc]
      --cover-branches                            include branch coverage in report
      --cover-erase                               erase previously collected coverage data
      --cover-min-percentage=<cover_min_percentage> fail if the given minimum coverage percentage is not reached
      --cover-html=<cover_html_dir>               specify a directory where to store HTML coverage report
      --cover-xml=<cover_xml_file>                specify a file where to store XML coverage report
      --no-ansi                                   print features without any ANSI sequences (like colors, line jump)
      --no-line-jump                              print features without line jumps (overwriting steps)
      --write-steps-once                          does not rewrite the steps (this option only makes sense in combination with the --no-ansi flag)
      --write-ids                                 write the feature, scenario and step id before the sentences
      --cucumber-json=<ccjson>                    write cucumber json result file after run
      --junit-xml=<junitxml>                      write JUnit XML result file after run
      --debug-after-failure                       start python debugger after failure
      --inspect-after-failure                     start python shell after failure
      --syslog                                    log all of your features, scenarios, and steps to the syslog
      -u=<userdata> | --user-data=<userdata>...   User data as 'key=value' pair. You can specify --user-data multiple times.
