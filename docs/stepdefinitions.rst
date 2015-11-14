Step Defintions
===============

Radish doesn't know anything about how your steps should be run. So you have to define some code for each step which is executed once the steps is run.
This code is called a **step definition**. Each step definition gets its own method.
Radish provides some decorators to register these methods as *step definitions*.

+-----------+------------------------------------------------------------------------------------------------------+
| Decorator | Description                                                                                          |
+===========+======================================================================================================+
| @step     | This is most simple decorator radish provides. It takes exactly one argument.                        |
|           | This argument could either be a valid regular expression matching one of your steps                  |
|           | or an *ArgumentExpression* object.                                                                   |
+-----------+------------------------------------------------------------------------------------------------------+
| @given    | This decorator is an alias for @step which adds the **Given** keyword before your regular expression |
+-----------+------------------------------------------------------------------------------------------------------+
| @when     | Same as *@given* but adds the **When** keyword.                                                      |
+-----------+------------------------------------------------------------------------------------------------------+
| @then     | Same as *@given* but adds the **Then** keyword.                                                      |
+-----------+------------------------------------------------------------------------------------------------------+
| @but      | Same as *@given* but adds the **But** keyword.                                                       |
+-----------+------------------------------------------------------------------------------------------------------+

@step(...) Regular Expression as argument
-----------------------------------------

To be compatible with other BDD tools the step-decorator takes per default a Regular Expression which should match one of the steps in the feature file.
This Regular Expression can contain groups. The content of the group will be passed as argument to the step definition method:

.. code-block:: python

   # -*- coding: utf-8 -*-
   from radish.stepregistry import given, step

   @given(r"I startup my calculator")
   def startup(step):
       # do some fancy stuff
       pass


   @step(r"I add (\d+) to my number")  # regex with group
   def add_to_number(step, number):
       step.context.number += number


@step(...) ArgumentExpression as argument
-----------------------------------------

A more powerful and in most cases the easier way is to use an *ArgumentExpression* object as argument for the step decorator.
The *ArgumentExpression* object provides a more readable syntax as normal Regular Expressions. In fact the syntax of an *ArgumentExpression* expression is the reverse as you would use with python's *str.format()* method.
Instead of groups you use *{}*. The exact format specification can be found here: https://github.com/r1chardj0n3s/parse#format-specification

.. code-block:: python

   # -*- coding: utf-8 -*-
   from radish.stepregistry import given, when
   from radish import ArgumentExpression

   @given(ArgumentExpression("I have the number {:g}"))
   def have_number(step, number):
       step.context.number = number


   @when(ArgumentExpression("I add {number:g} to my number"))
   def add_to_number(step, number):
       step.context.number += number


**Note:** with the *ArgumentExpression Registry* you are able to define your own format specification. See: :ref:`argumentexpressions`


Step Definition method arguments
--------------------------------

The step definition methods will get minimum one argument. An instance of the step which should be executed.

The most useful information you can get from the *Step* object:

+-----------------+----------------------------------------------------------------------------------------------------------------------------------+
| Method/Property | Description                                                                                                                      |
+=================+==================================================================================================================================+
| step.context    | A scenario specific context object like the *terrain.world* object. Use this object to store all data you need across your steps |
+-----------------+----------------------------------------------------------------------------------------------------------------------------------+
| step.table      | The table data if your step was defined with a :ref:`steptable`                                                                  |
+-----------------+----------------------------------------------------------------------------------------------------------------------------------+
| step.text       | The text if your step was defined with additional text. see :ref:`steptext`                                                      |
+-----------------+----------------------------------------------------------------------------------------------------------------------------------+

.. code-block:: python

   @step(r"I startup my calculator")
   def startup(step):
       step.context.initialized = True  # add data to scenario's context object
       assert step.table, "This step has no additional table defined"
       assert step.text, "This step has no additional text defined"


In addition to the *Step* object all matching groups from the Regular Expression or Argument Expression will be passed:

.. code-block:: python

   @given(ArgumentExpression("I have the number {:g}"))
   def have_number(step, number):
       step.context.number = number


   @when(r"I add (\d+) to my number")
   def add_to_number(step, number):
       step.context.number += number
