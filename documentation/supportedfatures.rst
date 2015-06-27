Supported Features
==================

This is a list of all supported language features of radish.

Feature
-------

A Feature is the most basic thing in a feature file. It makes the feature file what is is.
One feature file must contain exactly **one** Feature.
A Feature can have a description and one or more Scenarios, Scenario Outlines and/or Scenario Loops.

Each Feature should test the same software component with different test cases (Scenarios):

.. code-block:: cucumber

   Feature: Test the calculator package
       In order to guarantee the functionality
       of the projects calculator package
       I test the addition, subtraction,
       multplication and division functions.

       Scenario: Test adding numbers
          Given I ...
          When I ...
          Then I ...

       Scenario: Test dividing numbers:
          ...

Scenario
--------

A Scenario should be a standalone test case for a specific feature.
Each scenario must contain one or multiple steps written in human readable language.

.. code-block:: cucumber

   Feature: Test the calculator package
       In order to guarantee the functionality
       of the projects calculator package
       I test the addition, subtraction,
       multplication and division functions.

       Scenario: Test adding numbers
          Given I have the number 5
          When I add 10 to my number
          Then I expect my number to be 15

       Scenario: Test dividing numbers:
          Given I have the number 42
          When I divide my number by 6
          Then I expect my number to be 7


Scenario Outline
----------------

A Scenario Outline is like a normal Scenario but this Scenario will be run with different data.
The steps in a Scenario Outline can contain placeholders for such data values. These data values are defined in Examples.
Each Example will expand to a normal Scenario with the steps from the Scenario Outline but with the correct data values:

.. code-block:: cucumber

   Feature: Test the calculator package
       In order to guarantee the functionality
       of the projects calculator package
       I test the addition, subtraction,
       multplication and division functions.

    Scenario Outline: Test adding numbers
        Given I have the number <number>
        When I add <delta> to my number
        Then I expect my number to be <result>

    Examples:
        | number | delta | result |
        | 5      | 2     | 7      |
        | 10     | 3     | 13     |
        | 15     | 6     | 21     |


This Scenario Outline will created 3 Scenarios. The placeholder are defined with **<** and **>**. The placeholder name must match one column in the Examples.

Scenario Loop (No standard gherkin)
-----------------------------------

A Scenario Loop is like a normal scenario but it will be run several times.
This Scenario type is especially useful to test the stability of your software.

.. code-block:: cucumber

   Feature: Test the calculator package
       In order to guarantee the functionality
       of the projects calculator package
       I test the addition, subtraction,
       multplication and division functions.

   Scenario Loop 10: Test floating point epsilon
       Given I have the number 3.2316e-10
       When I add 5.31e-9 to my number
       Then I expect my number to be 5.63316e-9

Scenario Preconditions (No standard gherkin)
--------------------------------------------

Sometimes it is very useful when you can define a scenario as precondition for another scenario.
Imagine you have for some really good reason a very long scenario because you have to do a lot of steps until you have the state you need to test your feature. You will end up in a mess: The key point of the scenario is lost somewhere the test maintainer and reviewer does not really care about all these preconditions.
For that radish implements Scenario preconditions:

.. code-block:: cucumber

   Feature: Check users
       I order to guarantee the backends user system
       the insertion and selection of the users is tested.

       @precondition(SetupDatabase.feature: Setup database and insert default values)
       Scenario: Check users
           When I add the user "Timo furrer"
           Then I expect the user "Timo Furrer" in the database

As you can see the *Scenario* is tagged with the *@precondition* tag and some arguments.
Every thing with is before the colon sign is the feature file name relatively to the current feature file. And everything after the colon is the name of the scenario which should be used as precondition.

When you run this Scenario the Steps of the *Setup database and insert default values* Scenario will be run first:

.. image:: /images/supportedfeatures_scenario_preconditions.png

However if you want to send this feature file without dependencies or if you just want to have a standalone feature file you can use the radish *show* command with the *--expand* option:

.. image:: /images/supportedfeatures_scenario_preconditions_expanded.png

Step
----

tbd.

Step Tables
-----------

tbd.

Step Text
---------

tbd.

Tags
----

tbd.

Variables (No standard gherkin)
-------------------------------

tbd.
