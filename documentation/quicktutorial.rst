Quick Tutorial
==============

This short tutorial gives you a first introduction in how to write a simple feature file the according steps and running it.

What do I need?
---------------

First you need to install radish.

With pip:
  .. code-block:: bash

     pip install radish-bdd

With easy_install:
  .. code-block:: bash

     easy_install radish-bdd

Radish requires at minimum two files:
  * a feature file to run
  * the step definition file according to your feature file

The feature file
----------------

A feature file must contain exactly one Feature.
This Feature can have a short description and one or more test cases called Scenario.
Each scenario should be a separate test and should be runnable as a standalone test.
The Scenario is composed of multiple Steps. The steps should be written as human readable text. It is highly recommended to avoid
programming language statements. Instead use the keywords *Given*, *When*, *Then* and *But* to bring some flow to the test.

  .. code-block:: cucumber

     Feature: Some fancy feature
         In order to write cool software
         I use behaviour driven development
         with the awesome radish tool

     Scenario: Test adding numbers
         Given I have the number 5
         When I add 2 to my number
         Then I expect the number to be 7

     Scenario: Test adding other numbers
         Given I have the number 10
         When I add 32 to my number
         Then I expect the number to be 42


Step Definition file
--------------------

If you've written an awesome feature file radish does not know how to run it because it does not speak English (or whatever language you've used).
For that you have to define what should be executed for each step in your feature file. The code which should be executed when running a step is called a *step definition*. Radish provides some easy-to-use mechanisms to register your step definitions.
Usually your step definitions are in a file called *steps.py* and could look like the following:

  .. code-block:: python

     # -*- coding: utf-8 -*-
     from radish.stepregistry import step

     @step(r"I have the number (\d+)")
     def have_number(step, number):
         step.context.number = number


     @step(r"I add (\d+) to my number")
     def add_to_number(step, number):
         step.context.number += number


     @step(r"I expect the number to be (\d+)")
     def expect_number(step, number):
         assert step.context.number == number, "Expected number to but {} but is {}".format(
            number, step.context.number)


Run features
------------

Now you have the following files:

  .. code-block:: text

     - numbers.feature
     - radish/
       - steps.py

The most simple radish call to run your feature file is:

  .. code-block:: bash

     radish numbers.feature

Radish automatically imports all python modules inside of *$PWD/radish*. Which in this case is only the steps.py file.

The run will look like:

.. image:: /images/quick_tutorial_numbers_feature.png
