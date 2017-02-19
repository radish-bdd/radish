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

Radish allows you to pass custom in the data to terrain hook code or to steps
code using the ``-p`` or ``--profile`` is a command line switch. This can be
used to customize your test runs as needed.

A common usage of ``--profile`` is to set it to the environment value such as
``stage`` or ``production``.

The value specified to the command line switch is made available in
``world.config.profile``. Please see :ref:`tutorial#world` for more
information.


Run - Dry run
-------------

Radish can perform a dry run of Scenarios if you specify ``-d`` or
``--dry-run`` command line switch:

.. code:: bash

  radish SomeFeature.feature -d
  radish SomeFeature.feature --dry-run


Run - Specify certain Scenarios by id
-------------------------------------

Radish can also runs specific scenarios by id using the ``-s`` or
``--scenarios`` command line switch. The ids are scenarios are indexed by the
parsing order. The first Scenario in the first Feature will have the id 1, the second scenario
the id 2. The Scenario ids are unique over all Features from this run. The
value can be a single Scenario id or a comma separated list of Scenario ids:

You can use ``--write-ids`` command line switch to print Scenario ids.

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

The format BDD XML is :ref:`documented here <bdd_xml_output>`.


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
-------------------------------


Radish debugging mechanisms include ability to drop into either IPython shell
on code failures using ``--inspect-after-failure`` command line switch.

.. code:: bash

  radish SomeFeature.feature --inspect-after-failure


Please consult `Run - Debug Steps`_ for debugging tips.


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

    --cucumber-json=<ccjson>                    write cucumber json result file after run

    --debug-after-failure                       start python debugger after failure

    --inspect-after-failure                     start python shell after failure

    --no-ansi                                   print features without any ANSI sequences (like colors, line jump)
    --no-line-jump                              print features without line jumps (overwriting steps)
    --write-steps-once                          does not rewrite the steps (this option only makes sense in combination with the --no-ansi flag)
    --write-ids                                 write the feature, scenario and step id before the sentences


    radish show <features>
           [--expand]
           [--no-ansi]
    radish <features>...

           [--debug-after-failure]
           [--inspect-after-failure]

           [--no-ansi]
           [--no-line-jump]
           [--write-steps-once]
           [--write-ids]
