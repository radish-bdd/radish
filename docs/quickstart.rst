Quickstart
==========

In this chapter we will write our first feature file and python step implementation. More detailed information about Feature files, Scenarios and Steps can be found in the Tutorial chapter.

Writing the first feature file
------------------------------

Let's assume we've written a really awesome calculator class and want to test it with radish.
Our first feature file should test if the calculator is able to correctly sum numbers.
Feature files are nothing more than a text file containing a *Feature* with one or more *Scenarios*. Each *Scenario* contains one or more *Steps*:

.. code:: cucumber

   Feature: <My feature title>
       ... Some feature description ...

       Scenario: <My scenario title>
           ... Some steps testing our python code ...


To test our *calculator* we could write the following Feature and save it in a file called *features/SumNumbers.feature*:

.. code:: cucumber

   Feature: The calculator should be able to sum numbers
       In order to make sure the calculator
       sums numbers correctly I have the following
       test scenarios:

       Scenario: Test my calculator
           Given I have the numbers 5 and 6
           When I sum them
           Then I expect the result to be 11

Implementing Steps
------------------

In order to run our *SumNumbers.feature* feature file we have to tell radish what to do for each Step in our Scenario.

All Steps are implemented in a python module as functions. These python modules are loaded by radish and the Step implementations are automatically matched with the corresponding Steps in the feature file.

Let's write our first feature file called *radish/steps.py*:

.. code:: python

   # -*- coding: utf-8 -*-

   from radish import given, when, then

   @given("I have the numbers {number1:g} and {number2:g}")
   def have_numbers(step, number1, number2):
       step.context.number1 = number1
       step.context.number2 = number2

   @when("I sum them")
   def sum_numbers(step):
       step.context.result = step.context.calculator.add( \
          step.context.number1, step.context.number2)

   @then("I expect the result to be {result:g}")
   def expect_result(step, result):
       assert step.context.result == result

Each of our Step implementation functions is decorated by radish's *given*, *when* or *then* decorator.
The first argument of these decorators is a *regex-similar* expression. These expressions are used to match the Steps from the feature file. A Step can contain parameters which are parsed by radish and passed after to the step implementation function. The first argument of a step implementation function is always the step object itself. The most interesting part about the *step* object is the *step.context* object. This object represents a *Scenario* wide context with dynamic attributes. Our step implementation already uses this *context object* to store the numbers to sum and a *calculator* instance. This calculator instance is created in a hook in the so called *terrain file* module.

Implementation Terrain
----------------------

In addition to the Step implementations is possible to implement *hooks* which are called during a run by radish. These hooks are usually implemented in a file called *terrain.py* alongside the step implementation modules.
For our *calculator* tests we use the *radish/terrain.py* file to instantiate the calculator object:

.. code:: python

   # -*- coding: utf-8 -*-

   from radish import before, after

   from calculator import Calculator

   @before.each_scenario
   def init_calculator(scenario):
       scenario.context.calculator = Calculator(caching=True)

   @after.each_scenario
   def destory_calculator(scenario):
       del scenario.context.calculator


Yes, to be honest in this case it seems like an overkill to have this hooks implementation. Where it becomes really useful and handy are when database, external resources, etc. are involved.

Run the feature file
--------------------

So far we've got the following files in our project:

.. code:: text

   features/
       SumNumbers.feature
   radish/
       steps.py
       terrain.py

With this setup we can just execute the following command and radish will run our feature file:

.. code:: bash

   radish features/

radish will output the following:

.. code:: cucumber

   Feature: The calculator should be able to sum numbers  # features/SumNumbers.feature
       In order to make sure the calculator
       sums numbers correctly I have the following
       test scenarios:

       Scenario: Test my calculator
           Given I have the numbers 5 and 6
           When I sum them
           Then I expect the result to be 11

   1 features (1 passed)
   1 scenarios (1 passed)
   3 steps (3 passed)
   Run 1447487393 finished within 0:0.000436 minutes

How does radish find my python modules?
radish imports all python modules inside the *basedir*. Per default the *basedir* points to *$PWD/radish* which in our case is perfectly fine. If the python implementation modules are located at another location the *-b* option followed by the path to the files can be given and radish will import the files from this location.


.. _quickstart#run-state-result:

Run state result
----------------

**Step:**

A Step run state can be one of the following values.

* passed
* failed
* skipped
* pending
* untested

**Scenario:**

Scenario run state result is set set as follows:

If any Step in the Scenario is did not "pass" then return the run result of the
**first** Step that did not pass. As such Scenario run state result is always
one of the Step run state values described above.

**Feature:**

If any Scenario in the Feature is did not "pass" then return the run result of
the **first** Step that did not pass. As such Feature run state result is
always one of the Step run state values described above.

