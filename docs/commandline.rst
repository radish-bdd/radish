Command Line Usage
==================

This chapter describes how to use Radish from the command line. All it's
commands, options and arguments.


Run - Specify Feature files
---------------------------

All arguments which doesn't belong to any command line switch are interpreted
as Feature files or Feature file locations. If the argument is a directory all
files ending with ``.feature`` will be run. It's possible to mix files and
directories:

.. code:: bash

  radish SomeFeature.feature myfeatures/


Run - Specify base directory
----------------------------

Radish looks for *Step* and *Terrain* files in the ``base directory``. By
default the ``base directory`` is set to the in the ``radish`` folder within
the current working directory (a.k.a ``$PWD/radish``). Radish imports all
the python files imported.

You can specify an alternate path using the ``-b`` or ``--basedir``
command line switch:

.. code:: bash

  radish -b tests/radish SomeFeature.feature
  radish --basedir tests/radish SomeFeature.feature


Run - Early exit
----------------

By default Radish will try to run all specified Scenarios even if there are
failed Scenarios. If you want to abort the test run after the first error
occurred you can use the ``-e`` or ``--early-exit`` switch:

.. code:: bash

  radish SomeFeature.feature -e
  radish SomeFeature.feature --early-exit


Run - Debug Steps
-----------------

Radish provides ability to debug each step using an IPython debugger. You can
enable that using ``--debug-steps`` command line switch.

.. code:: bash

  radish --debug-steps SomeFeature.feature

If you are unfamiliar with the Python debugger please consult official
`debugger documentation <https://docs.python.org/3/library/pdb.html>`_.

For example can see variables available to by printing ``locals()``.

.. code:: python

    ipdb> locals()
    {'step': <radish.stepmodel.Step object at 0x7f4d5b6ca400>}

As you can see, when failure happens inside the Step you can see the step
arguments such as ``step``.


Run - Show traceback on failure
-------------------------------

Radish can display a complete traceback when a Step fails. You can use the
``-t`` or ``--with-traceback`` command line switch for that:

.. code:: bash

  radish SomeFeature.feature -t
  radish SomeFeature.feature --with-traceback


Run - Use custom marker to uniquely identify test run
-----------------------------------------------------

Radish supports marker functionality which is used to uniquely identify a
specific test run using. By default the marker is set to the number of seconds
from the epoch (01/01/1970). You can specify your own marker using ``-m`` or
``--marker`` command line switch.

The marker is also displayed in the summary of the test runs.

.. code:: bash

  radish SomeFeature.feature -m "My Marker"
  radish SomeFeature.feature --marker "My Marker"

  ... radish output

  Run My Marker finished within 0:0.001272 minutes

The marker is also passed in to all the hooks define in terrain file. To see
example code please read :ref:`terrain <tutorial#terrain_and_hooks>`:


Run - Profile
-------------

Radish allows you to pass custom data to Terrain hook code or to Steps code
using the ``-p`` or ``--profile`` is a command line switch. This can be used to
customize your test runs as needed.

The value specified to the ``-p`` / ``--profile`` command line switch is made
available in ``world.config.profile``. Please see :ref:`tutorial#world` for
for an example.

A common usage of  is to set it to the environment value
such as ``stage`` or ``production``.

.. code:: bash

  radish SomeFeature.feature -p stage
  radish SomeFeature.feature --profile stage


Run - Dry run
-------------

Radish allows you to pass custom flag to Terrain hook code or to Steps code
using the ``-d`` or ``--dry-run`` is a command line switch. This can be used to
customize your test runs as needed.

The ``-d`` / ``--dry-run`` command line switch is made available in
``world.config.dry_run`` which set to ``True``.
Please see :ref:`tutorial#world` for an example.

.. code:: bash

  radish SomeFeature.feature -p -d
  radish SomeFeature.feature --dry-run

Run - Specifying Scenarios by id
--------------------------------

Radish can also runs specific scenarios by id using the ``-s`` or
``--scenarios`` command line switch. The ids are scenarios are indexed by the
parsing order. The first Scenario in the first Feature will have the id 1, the second scenario
the id 2. The Scenario ids are unique over all Features from this run. The
value can be a single Scenario id or a comma separated list of Scenario ids:

You can use ``--write-ids`` command line switch to print Scenario ids.
Please consult `Run - Writing out Scenario and Step ids`_

.. code:: bash

  radish SomeFeature.feature -s 1
  radish SomeFeature.feature --scenarios 1,2,5,6


Run - Shuffle Scenarios
-----------------------

Radish can also shuffle the Scenarios by using the ``--shuffle`` command line
switch. This useful when you are trying to detect if any scenario have
unintended side effects on other scenarios.

.. code:: bash

  radish SomeFeature.feature --shuffle


Run - Specify certain Features and/or Scenarios by tags
-------------------------------------------------------

Radish is able to run only a selection of certain Features and/or Scenarios
using the ``--feature-tags`` or ``--scenario-tags`` command line switch and
specifying the tags of Features/Scenarios which should be run. The command line
switch value can be a single tag or a comma separated list of tags:

.. code:: bash

  radish SomeFeature.feature --feature-tags regression
  radish SomeFeature.feature --scenario-tags good_case,in_progress
  radish SomeFeature.feature --scenario-tags good_case --feature-tags regression

To learn how to tag Features and Scenarios please refer to :ref:`tutorial#tags`
section.


Run - Write BDD XML result file
-------------------------------

Radish can write out an XML file with the results of after a test run using
``--bdd-xml`` command line switch. The command line switch value must be a
file path to the output file.

.. code:: bash

  radish SomeFeature.feature --bdd-xml /tmp/result.xml

To understand the format BDD XML consult: `BDD XML Output`_.


Run - Code Coverage
-------------------

Radish can use ``coverage`` package to measure code coverage of the code run
during the tests using ``--with-coverage`` command line switch. You can also
limit which packages it generates metrics for by providing file paths or
package names using ``--cover-packages``. The ``--cover-packages`` switch is
the ``--source`` command line switch used by ``coverage``.
See `coverage documention <https://coverage.readthedocs.io/en/latest/cmd.html#execution>`_

.. note::

    This feature is not yet complete.
    See: https://github.com/radish-bdd/radish/issues/15


Run - Write Cucumber JSON file
------------------------------

Radish can write out a Cucumber style JSON file with the results of after a
test run using ``--cucumber-json`` command line switch. The command line switch
value must be a file path to the output file.

.. code:: bash

  radish SomeFeature.feature --cucumber-json /tmp/result.json

Documentation describing then format of the Cucumber JSON file can be founde
here: https://www.relishapp.com/cucumber/cucumber/docs/formatters/json-output-formatter


Run - Debug code after failure
-------------------------------

Radish debugging mechanisms include ability to drop into either IPython or
Python debugger on code failures using ``--debug-after-failure`` command line
switch. Using IPython is preferred over standard Python debugger.

If you are unfamiliar with the Python debugger please consult official
`debugger documentation <https://docs.python.org/3/library/pdb.html>`_.

.. code:: bash

  radish SomeFeature.feature --debug-after-failure


Please consult `Run - Debug Steps`_ for debugging tips.


Run - Inspect code after failure
--------------------------------

Radish debugging mechanisms include ability to drop into either IPython shell
on code failures using ``--inspect-after-failure`` command line switch.

.. code:: bash

  radish SomeFeature.feature --inspect-after-failure


Please consult `Run - Debug Steps`_ for debugging tips.


Run - Printing results to console
---------------------------------

Note: **Pending** state means "yet to be executed".

Radish console output is powerful and explicit. It also uses ANSI color codes
and line 'overwriting' to format and color the output to make it more user
friendly.

Anatomy of the console output is a follows:

Pending Scenario Steps sentences as well as entries in Scenario Outline Example
and Scenario Loop tables are printed to the console first, coloured in bold
yellow.

As the Scenario Steps, Scenario Outline Example entries and Scenario Loop
iterations are executed the "ansi line jump" is used to replace the printed
yellow line with the outcome of the Step run which is coloured in bold green on
success or bold red in case of failure.

For Scenario Outline Step and Scenario Loop Step sentences the executed Steps
are the "ansi line jump" is used to replace the printed yellow line with the
cyan colour. This is a bug that will be fixed soon.

Exceptions message and trace back are printed on failure under the failed Step,
Scenario Outline Example entry or Scenario Loop Iteration.

Radish provides several command line switches to help you with console output
format.

A common use of Radish is to run it using script or continuous integration
setups. Such setups usually do not support "ansi" colour codes or line jumps.
This is where combined use of ``--no-ansi`` and ``--write-steps-once`` command
line switches are useful.

The ``--no-ansi`` turns of "ansi" codes that make output to console less
readable. However, since doing that also disables line jumping the steps runs
will be printed twice to the screen (first print is pending step, second is
the executed one). Without colours that double print is confusing and can be
turned of using ``--write-steps-once``.

.. code:: bash

  radish SomeFeature.feature --no-ansi
  radish SomeFeature.feature --no-ansi --write-steps-once

The ``--no-line-jump`` command line switch disables the "overwriting" of the
yellow pending lines by the success or failure lines. This helpful to you
during debugging so you can see when steps were pending then executed.

.. code:: bash

  radish SomeFeature.feature --no-line-jump


Run - Writing out Scenario and Step ids
---------------------------------------

Radish provides `--write-ids`` command line switch which can be used to
enumerate Scenarios and Steps.

This can be useful in bug reporting.

.. code:: cucumber

    1. Scenario: Apple Blender
        1. Given I put couple of "apples" in a blender
        2. When I switch the blender on
        3. Then it should transform into "apple juice"

    2. Scenario: Pear Blender
        1. Given I put couple of "pears" in a blender
        2. When I switch the blender on
        3. Then it should transform into "pear juice"

It can also be useful when using ``-s`` / ``--scenarios`` command line switch
since the Scenarios are numbered in the run order.


Show - Expand feature
---------------------

Radish Precondition decorated Scenarios are powerful but can be confusing to
read on the screen. As such Radish provides ``--expand`` command line switch to
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
             [-b=<basedir> | --basedir=<basedir>]
             [-e | --early-exit]
             [--debug-steps]
             [-t | --with-traceback]
             [-m=<marker> | --marker=<marker>]
             [-p=<profile> | --profile=<profile>]
             [-d | --dry-run]
             [-s=<scenarios> | --scenarios=<scenarios>]
             [--shuffle]
             [--feature-tags=<feature_tags>]
             [--scenario-tags=<scenario_tags>]
             [--bdd-xml=<bddxml>]
             [--with-coverage]
             [--cover-packages=<cover_packages>]
             [--cucumber-json=<ccjson>]
             [--debug-after-failure]
             [--inspect-after-failure]
             [--no-ansi]
             [--no-line-jump]
             [--write-steps-once]
             [--write-ids]
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
      -b=<basedir> --basedir=<basedir>            set base dir from where the step.py and terrain.py will be loaded [default: $PWD/radish]
      -d --dry-run                                make dry run for the given feature files
      -s=<scenarios> --scenarios=<scenarios>      only run the specified scenarios (comma separated list)
      --shuffle                                   shuttle run order of features and scenarios
      --feature-tags=<feature_tags>               only run features with the given tags
      --scenario-tags=<scenario_tags>             only run scenarios with the given tags
      --expand                                    expand the feature file (all preconditions)
      --bdd-xml=<bddxml>                          write BDD XML result file after run
      --with-coverage                             enable code coverage
      --cover-packages=<cover_packages>           specify source code package
      --cucumber-json=<ccjson>                    write cucumber json result file after run
      --debug-after-failure                       start python debugger after failure
      --inspect-after-failure                     start python shell after failure
      --no-ansi                                   print features without any ANSI sequences (like colors, line jump)
      --no-line-jump                              print features without line jumps (overwriting steps)
      --write-steps-once                          does not rewrite the steps (this option only makes sense in combination with the --no-ansi flag)
      --write-ids                                 write the feature, scenario and step id before the sentences


BDD XML Output
--------------

Radish can BDD XML output using ``--bdb-xml``. The format of the XML as is
as follows:

**XML declaration**

.. code:: xml

  <?xml version='1.0' encoding='utf-8'?>

**<testrun>** is a top level tag

:agent:
  Agent of the test run composed of the user and hostname of the machine.
  Format: user@hostname
:duration:
  Duration of test run in seconds rounded to the 10 decimal points.
:starttime:
  Start time of the testrun run.
  Format: combined date and time representations, where date and time is separated by
  letter "T". Format: YYYY-MM-DDTHH:MM:SS
:endtime:
  End time of the testrun run.
  Format: combined date and time representations, where date and time is separated by
  letter "T". Format: YYYY-MM-DDTHH:MM:SS

example:

.. code:: xml

  <testrun>
    agent="user@computer"
    duration="0.0005660000"
    starttime="2017-02-18T07:06:55">
    endtime="2017-02-18T07:06:56"
  >

The **<testrun>** contains the following tags

**<feature>** tag

:id:
  Test run index id of the Feature. First feature to run is 1, second is 2 and
  so on.
:sentence:
  Feature sentence.
:result:
  Run state result of Feature run as described in
  :ref:`quickstart#run-state-result`
:testfile:
  Path to the file name containing the feature. The path is relative to
  the ``basedir``.
:duration:
  Duration of Feature run in seconds rounded to the 10 decimal points.
:starttime:
  Start time of the Feature run.
  Format: combined date and time representations, where date and time is separated by
  letter "T". Format: YYYY-MM-DDTHH:MM:SS
:endtime:
  End time of the Feature run.
  Format: combined date and time representations, where date and time is separated by
  letter "T". Format: YYYY-MM-DDTHH:MM:SS

example:

.. code:: xml

    <feature
      id="1"
      sentence="Step Parameters (tutorial03)"
      result="failed"
      testfile="./example.feature"
      duration="0.0008730000"
      starttime="2017-02-18T07:06:55"
      endtime="2017-02-18T07:06:55"
    >

The **<feature>** tag contains the following tags:

**<description>** tag:

:tag content: CDATA enclosed description of the feature.

.. code:: xml

  <description>
    <![CDATA[This feature test following functionality
    - awesomeness
    - more awesomeness
    ]]>
  </description>

**<scenarios>** tag:

Contains list of **<screnario>** tags

example:

.. code:: xml

  <scenarios>

The **<scenarios>** tag contains the following tags:

**<scenario>** tag:

:id:
  Test run index id of the Scenario. First scenario to run is 1, second is 2
  and so on.
:sentence:
  Scenario sentence.
:result:
  Run state result of Scenario run as described in
  :ref:`quickstart#run-state-result`
:testfile:
  Path to the file name containing the Scenario. The path is relative to
  the ``basedir``.
:duration:
  Duration of Scenario run in seconds rounded to the 10 decimal points.
:starttime:
  Start time of the Scenario run.
  Format: combined date and time representations, where date and time is separated by
  letter "T". Format: YYYY-MM-DDTHH:MM:SS
:endtime:
  End time of the Scenario run.
  Combined date and time representations, where date and time is separated by
  letter "T". Format: YYYY-MM-DDTHH:MM:SS

example:

.. code:: xml

  <scenario
    id="1"
    sentence="Blenders"
    result="failed"
    testfile="./example.feature"
    duration="0.0007430000"
    endtime="2017-02-18T07:06:55"
    starttime="2017-02-18T07:06:55"
  >

The **<scenario>** tag contains the following tags:

**<step>** tag:

:id:
  Test run index id of the Step. First Step to run is 1, second is 2
  and so on.
:sentence:
  Step sentence.
:result:
  Run state result of Step run as described in
  :ref:`quickstart#run-state-result`
:testfile:
  Path to the file name containing the Step. The path is relative to
  the ``basedir``.
:duration:
  Duration of Step run in seconds rounded to the 10 decimal points.
:starttime:
  Start time of the Step run.
  Format: combined date and time representations, where date and time is separated by
  letter "T". Format: YYYY-MM-DDTHH:MM:SS
:endtime:
  End time of the Step run.
  Format: combined date and time representations, where date and time is separated by
  letter "T". Format: YYYY-MM-DDTHH:MM:SS


example:

.. code:: xml

  <step
    id="1"
    sentence="Given I put &quot;apples&quot; in a blender"
    result="passed"
    testfile="./example.feature"
    duration="0.0007430000"
    endtime="2017-02-18T07:06:55"
    starttime="2017-02-18T07:06:55"
  >

The **<step>** MAY tag contains the following tags if error has occured:

**<failure>** tag:

:message:
  Test run index id of the Step. First Step to run is 1, second is 2
  and so on.
:type:
  Step sentence.
:tag content:
  CDATA enclosed failure reason specifically excepion traceback.


example:

.. code:: xml

  <failure
    message="hello"
    type="Exception">
      <![CDATA[Traceback (most recent call last):
        File "/tmp/bdd/_env36/lib/python3.6/site-packages/radish/stepmodel.py", line 91, in run
          self.definition_func(self, *self.arguments)  # pylint: disable=not-callable
        File "/tmp/bdd/radish/radish/example.py", line 34, in step_when_switch_blender_on
          raise Exception("show off radish error handling")
      Exception: show off radish error handling
     ]]>
  </failure>

