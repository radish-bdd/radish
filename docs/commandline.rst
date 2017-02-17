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

The directory where the *Step* and *Terrain* files are located is called the
``base directory``. Per default it points to ``$PWD/radish`` (PWD is your
current folder). All python files within this directory are imported by radish.
You can specify the base directory with the ``-b`` or ``--basedir`` switch:

.. code:: bash

  radish -b tests/radish SomeFeature.feature
  radish --basedir tests/radish SomeFeature.feature


Run - Early exit
----------------

By default radish will try to run all specified Scenarios even if there are
failed Scenarios. If you want to abort the test run after the first error
occurred you can use the ``-e`` or ``--early-exit`` switch:

.. code:: bash

  radish SomeFeature.feature -e
  radish SomeFeature.feature --early-exit


Run - Debug Steps
-----------------

Radish provides ability to debug each step using an IPython debugger. You can
enable that ``--debug-steps`` command line switch.

If you are unfamiliar with the Python debugger please consult official
`debugger documentation <https://docs.python.org/3/library/pdb.html>`_.

.. code:: bash

  radish --debug-steps SomeFeature.feature


Run - Show traceback on failure
-------------------------------

Sometimes it's useful to get the complete traceback when a Step fails. Use the
``-t`` or ``--with-traceback`` command line switch switch to print them on failure:

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

To make a dry run use the ``-d`` or ``--dry-run`` command line switch:

.. code:: bash

  radish SomeFeature.feature -d
  radish SomeFeature.feature --dry-run

Run - Specify certain Scenarios by id
-------------------------------------

Use the ``-s`` or ``--scenarios`` command line switch to run specific selection
of Scenarios. The scenarios are indexed by the parsing order.

The first Scenario in the first Feature will have the id 1, the second scenario
the id 2. The Scenario ids are unique over all Features from this run. The
value can be a single Scenario id or a comma separated list of Scenario ids:

You can use ``--write-ids`` command line switch to print scenarios counts

.. code:: bash

  radish SomeFeature.feature -s 1
  radish SomeFeature.feature --scenarios 1,2,5,6

Run - Shuffle Scenarios
-----------------------

You can shuffle the Scenarios in a specific run by passing the ``--shuffle``
command line switch. This useful when you are trying to detect if any scenario
have unintended side effects on other scenarios.

.. code:: bash

  radish SomeFeature.feature --shuffle

Run - Specify certain Features/Scenarios by tags
------------------------------------------------

radish is able to run only a selection of certain Features and/or Scenarios.
The Features/Scenarios must be tagged. Use the ``--feature-tags`` or
``--scenario-tags`` to specify the tags of Features/Scenarios which should be
run. The value can be a single tag or a comma separated list of tags:

.. code:: bash

  radish SomeFeature.feature --feature-tags regression
  radish SomeFeature.feature --scenario-tags good_case,in_progress
  radish SomeFeature.feature --scenario-tags good_case --feature-tags regression


Show - Expand feature
---------------------

When showing a feature with radish it can be useful to expand all Preconditions. Use the ``--expand`` flag:

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

