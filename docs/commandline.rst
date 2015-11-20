Command Line Usage
==================

This chapter describes how to use radish from the command line. All it's commands, options and arguments.

Run - Specify Feature files
---------------------------

All arguments which doesn't belong to any command line switch are interpreted as Feature files or Feature file locations. If the argument is a directory all files ending with ``.feature`` will be run. It's possible to mix files and directories:

.. code:: bash

  radish SomeFeature.feature myfeatures/

Run - Specify base directory
----------------------------

The directory where the *Step* and *Terrain* files are located is called the ``base directory``.
Per default it points to ``$PWD/radish``. All python files within this directory are imported by radish. You can specify the base directory with the ``-b`` or ``--basedir`` switch:

.. code:: bash

  radish -b tests/radish SomeFeature.feature
  radish --basedir tests/radish SomeFeature.feature

Run - Early exit
----------------

Per default radish will try to run all specified Scenarios even if there are failed Scenarios. If you want to abort the test run after the first error occurred you can use the ``-e`` or ``--early-exit`` switch:

.. code:: bash

  radish SomeFeature.feature -e
  radish SomeFeature.feature --early-exit

Run - Dry run
-------------

A make a dry run. Use the ``-d`` or ``--dry-run`` command line switch:

.. code:: bash

  radish SomeFeature.feature -d
  radish SomeFeature.feature --dry-run

Run - Specify certain Scenarios by id
-------------------------------------

radish is able to run only a selection of certain Scenarios. The scenarios are indexed by the parsing order. The first Scenario in the first Feature will have the id 1, the second scenario the id 2. The Scenario ids are unique over all Features from this run. Use the ``-s`` or ``--scenarios`` argument. The value can be a single Scenario id or a comma separated list of Scenario ids:

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

Run - Show traceback on failure
-------------------------------

Sometimes it's useful to get the complete traceback when a Step fails. Use the ``-t`` or ``--with-traceback`` switch to print them on failure:

.. code:: bash

  radish SomeFeature.feature -t
  radish SomeFeature.feature --with-traceback

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
             [--debug-after-failure]
             [--inspect-after-failure]
             [--bdd-xml=<bddxml>]
             [--no-ansi]
             [--no-line-jump]
             [--write-steps-once]
             [--write-ids]
             [-t | --with-traceback]
             [-m=<marker> | --marker=<marker>]
             [-p=<profile> | --profile=<profile>]
             [-d | --dry-run]
             [-s=<scenarios> | --scenarios=<scenarios>]
             [--shuffle]
             [--feature-tags=<feature_tags>]
             [--scenario-tags=<scenario_tags>]
      radish (-h | --help)
      radish (-v | --version)

