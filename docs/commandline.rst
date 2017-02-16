Command Line Usage
==================

This chapter describes how to use radish from the command line. All it's
commands, options and arguments.

Run - Specify Feature files
---------------------------

All arguments which doesn't belong to any command line switch are interpreted
as Feature files or Feature file locations. If the argument is a directory all
files ending with ``.feature`` will be run. It's possible to mix files and
directories:

.. code:: bash

  radish SomeFeature.feature myfeatures/

Run - Early exit
----------------

Per default radish will try to run all specified Scenarios even if there are
failed Scenarios. If you want to abort the test run after the first error
occurred you can use the ``-e`` or ``--early-exit`` switch:

.. code:: bash

  radish SomeFeature.feature -e
  radish SomeFeature.feature --early-exit

Run - Debug Steps
-----------------

Run and debugs each step in an IPython debugger. You can then step through all
your code using standard Python debugger
`commands <https://docs.python.org/3/library/pdb.html#debugger-commands>`_.

.. code:: bash

  radish --debug-steps SomeFeature.feature


Run - Show traceback on failure
-------------------------------

Sometimes it's useful to get the complete traceback when a Step fails. Use the
``-t`` or ``--with-traceback`` switch to print them on failure:

.. code:: bash

  radish SomeFeature.feature -t
  radish SomeFeature.feature --with-traceback

Run - Use custom marker to uniquely identify test run
-----------------------------------------------------

Sometimes it is useful to create a marker for a specific test run using ``-m``
or ``--marker`` command line switch. The marker is passed in to all the hooks
define in terrain file. To see example code checkout
:ref:`terrain <tutorial#terrain_and_hooks>`:

The marker is also displayed in the summary of the test runs.

.. code:: bash

  radish SomeFeature.feature -m "My Marker"
  radish SomeFeature.feature --marker "My Marker"

  ... radish output

  Run My Marker finished within 0:0.001272 minutes

To compare, the default marker is the number of seconds from the epoch
(01/01/1970)

.. code:: bash

  # run without custom marker
  radish SomeFeature.feature

  Example, standard::
    Run 1487231904 finished within 0:0.001272 minutes

Run - Profile
-------------

The  ``-p`` or ``--profile`` is a command line switch to set a simple variable
which is then available ``world.config.profile`` and can be used in hooks
(or steps, though not recommended) as needed. Please see :ref:`tutorial#world`.


Run - Specify base directory
----------------------------

The directory where the *Step* and *Terrain* files are located is called the
``base directory``. Per default it points to ``$PWD/radish`` (PWD is your
current folder). All python files within this directory are imported by radish.
You can specify the base directory with the ``-b`` or ``--basedir`` switch:

.. code:: bash

  radish -b tests/radish SomeFeature.feature
  radish --basedir tests/radish SomeFeature.feature

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

User ``--write-ids`` command line switch to print scenarios

.. code:: bash

  radish SomeFeature.feature -s 1
  radish SomeFeature.feature --scenarios 1,2,5,6

Run - Specify certain Features/Scenarios by tags
------------------------------------------------

radish is able to run only a selection of certain Features and/or Scenarios. The Features/Scenarios must be tagged. Use the ``--feature-tags`` or ``--scenario-tags`` to specify the tags of Features/Scenarios which should be run. The value can be a single tag or a comma separated list of tags:

.. code:: bash

  radish SomeFeature.feature --feature-tags regression
  radish SomeFeature.feature --scenario-tags good_case,in_progress
  radish SomeFeature.feature --scenario-tags good_case --feature-tags regression

Run - Shuffle Scenarios
-----------------------

You can shuffle the Scenarios in a specific run by passing the ``--shuffle`` command line switch:

.. code:: bash

  radish SomeFeature.feature --shuffle

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

