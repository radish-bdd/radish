Usage
=====

Feature Files
-------------

The Feature Files are the most important part of a radish run.
A Feature File contains a Feature, Scenarios and Steps which
ultimately represent the tests.

Radish can run one or more Feature Files and even collect them recursively
from a given directory.
The location to the Feature Files is provided to the ``radish`` command line interface
as arguments:

.. code-block:: bash

    radish features/Calculator-Sum.feature features/startup/

The above example ``radish`` call will run the ``features/Calculator-Sum.feature`` Feature File
and all Feature Files (files matching the glob ``**/*.feature``) within the ``features/startup/``
directory.

The Feature File Syntax can be found here: :ref:`feature_file_syntax`

For more information about how to run Feature Files, see: `Running Feature Files`_.

.. _base_directory_usage:

Base Directory
--------------

Radish not only needs a Feature File to run, but also some Python implementation for
the Steps in the Feature File.
All those implementations should be placed in the *radish base directories*.
A Base Directory is nothing more than a plain directory containing Python Modules.
All Python Modules in the directory will be loaded by radish upon start.

By default radish looks for a ``radish`` directory relative to the ``radish`` cli call.
One or more directory can be passed with the ``-b`` or ``--basedir`` option to override
this default:

.. code-block:: bash

    radish features/Calculator-Sum.feature -b steps/

Implementing Steps
------------------

:ref:`Steps <step_syntax>` are the central and only parts which are
executable within a Feature File.
However, a Step is not directly executable, but rather is matched
to an *executable* when it's about to be run.
This *executable* is called a **Step Implementation**.

A Step Implementation is a plain Python function registered with a
Step Pattern and loaded by radish before a run is started.

A simple Step Implementation could look like this:

.. code-block:: python

    from radish import when

    @when("the numbers are added up")
    def add_numbers(step):
        ...

The above example uses the ``when`` `Step Decorator <Step Decorators>`_ which means that only
Steps beginning with the ``When`` keyword can be matched with this Step Implementation.

For radish to be able to load a Python Module containing Step Implementation
you have to place it in a `Base Directory`_.

When the Step Implementation function is ran it can be evaluated to 4 different result states:

* failed
* passed
* pending
* skipped

The **failed** and **passed** states are the most common ones.
A Step will evaluate to **passed** if no exception is raised during the run
and neither the Step is skipped nor marked as pending.
The Step is **failed** in case an exception is raised during the run. For example:

.. code-block:: python
   :caption: let a Step fail with an assertion

    from radish import when

    @when("the numbers are added up")
    def add_numbers(step):
        assert 5 == 7, "5 is not equal to 7"


A Step can be marked as pending with the ``step.pending()`` method:

.. code-block:: python
   :caption: mark a Step as pending

    from radish import when

    @when("the numbers are added up")
    def add_numbers(step):
        step.pending()


This is usful if the Step shouldn't fail but is not implemented yet.

A Step can be skipped with the ``step.skip()`` method:

.. code-block:: python
   :caption: skip a Step

    from radish import when

    @when("the numbers are added up")
    def add_numbers(step):
        step.skip()


A Step Implementation is always registered with a keyword and a pattern.
More details about the keyword can be found in the `Step Decorators`_ section
and for pattern see the `Step Pattern`_ section.


Step Decorators
~~~~~~~~~~~~~~~

A Step can be used with one of the following three keywords:

* ``Given``
* ``When``
* ``Then``

Those keywords indicate in which stage of the Scenario they appear
and what part of the test they represent.

A Step Implementation can be either matched only with ``Given``, ``When`` or ``Then``
Steps or with either one of those.
Radish provides :ref:`decorators to register Step Implementations <register_step_implementations_api>`
for those keywords:

.. code-block:: python
   :caption: register given, when and then Step Implementations

    from radish import given, when, then

    @given("the number {nbr:int}")
    def given_a_number(step, nbr):
        step.context.numbers.append(nbr)


    @when("the numbers are added up")
    def when_sum_numbers(step):
        step.context.sum = sum(step.context.numbers)


    @then("the sum is {result:int}")
    def then_sum_is(step, result):
        assert result == step.context.sum


The above Step Implementations can be matched with the following Steps:

.. code-block:: gherkin

    Given the number 5
    And the number 2
    When the numbers are added up
    Then the sum is 7

It's also possible to register a Step Implementation which is able
to be matched with every Step keyword using the ``@step`` decorator:

.. code-block:: python
   :caption: registered a generic Step Implementation

    import time

    from radish import step

    @step("the execution is delayed")
    def delay(step):
        time.sleep(5)

Thus, this Step Implementation is matched with all of the following Steps:

.. code-block:: gherkin

    Given the execution is delayed
    When the execution is delayed
    Then the execution is delayed

.. _step_pattern_usage:

Step Pattern
~~~~~~~~~~~~

The Step Pattern is one of the most important detail when registering
a Step Implementation.
It's used by radish to match a Step from the Feature File with the
appropriate Step Implementation.

The *Step Pattern* can either be a string in the
`Format String Syntax <https://docs.python.org/3/library/string.html#formatstrings>`_
with some additional syntax described later in this section or
a compiled Regular Expression pattern.

Format String Syntax
....................

This is the preferred way to specify the Step Pattern.
In the simplest variation a Step Pattern is just a plain string
without any placeholders:

.. code-block:: python

    @when("the numbers are added up")
    def when_sum_numbers(step):
        ...

This Step Pattern matches ``When``-Steps with the Step Text:
``the numbers are added up``.

The Step Pattern gets a little more complex when the Step Text
can vary - for example you want to inject a number into the
Step Implementation function (like in the Calculator example in the previous examples):

.. code-block:: python

    @given("the number {nbr:int}")
    def given_a_number(step, nbr):
        ...

The variable in the Step Pattern has the format of ``{name:type}`` whereas
``name`` is the name of the keyword argument in the Step Implementation function
and the ``type`` defines what kind of characters will match in the Step Text.

The following table shows all built-in types:

+-----------------+-------------------------------------------------------------------------------+-------------+
| Type            | Characters matched                                                            | Output type |
+=================+===============================================================================+=============+
| int             | Integers matching ``[-+]?[0-9]+``                                             | int         |
+-----------------+-------------------------------------------------------------------------------+-------------+
| float           | Floating point numbers                                                        | float       |
+-----------------+-------------------------------------------------------------------------------+-------------+
| word            | A single word matching ``\S+``                                                | str         |
+-----------------+-------------------------------------------------------------------------------+-------------+
| bool            | Boolean value:                                                                | bool        |
|                 | True: 1, y, Y, yes, Yes, YES, true, True, TRUE, on, On, ON                    |             |
|                 | False: 0, n, N, no, No, NO, false, False, FALSE, off, Off, OFF                |             |
+-----------------+-------------------------------------------------------------------------------+-------------+
| QuotedString    | String inside double quotes ("). Double quotes inside the string can be       | text        |
|                 | escaped with a backslash                                                      | w/o quotes  |
+-----------------+-------------------------------------------------------------------------------+-------------+
| MathExpression  | Mathematic expression containing: ``[0-9 +\-\*/%.e]+``                        | float       |
+-----------------+-------------------------------------------------------------------------------+-------------+
| w               | Letters and underscore                                                        | str         |
+-----------------+-------------------------------------------------------------------------------+-------------+
| W               | Non-letter and underscore                                                     | str         |
+-----------------+-------------------------------------------------------------------------------+-------------+
| s               | Whitespace                                                                    | str         |
+-----------------+-------------------------------------------------------------------------------+-------------+
| S               | Non-whitespace                                                                | str         |
+-----------------+-------------------------------------------------------------------------------+-------------+
| d               | Digits (effectively integer numbers)                                          | int         |
+-----------------+-------------------------------------------------------------------------------+-------------+
| D               | Non-digit                                                                     | str         |
+-----------------+-------------------------------------------------------------------------------+-------------+
| n               | Numbers with thousands separators (, or .)                                    | int         |
+-----------------+-------------------------------------------------------------------------------+-------------+
| %               | Percentage (converted to value/100.0)                                         | float       |
+-----------------+-------------------------------------------------------------------------------+-------------+
| f               | Fixed-point numbers                                                           | float       |
+-----------------+-------------------------------------------------------------------------------+-------------+
| e               | Floating-point numbers with exponent e.g. 1.1e-10, NAN (all case insensitive) | float       |
+-----------------+-------------------------------------------------------------------------------+-------------+
| g               | General number format (either d, f or e)                                      | float       |
+-----------------+-------------------------------------------------------------------------------+-------------+
| b               | Binary numbers                                                                | int         |
+-----------------+-------------------------------------------------------------------------------+-------------+
| o               | Octal numbers                                                                 | int         |
+-----------------+-------------------------------------------------------------------------------+-------------+
| x               | Hexadecimal numbers (lower and upper case)                                    | int         |
+-----------------+-------------------------------------------------------------------------------+-------------+
| ti              | ISO 8601 format date/time e.g. 1972-01-20T10:21:36Z (“T” and “Z” optional)    | datetime    |
+-----------------+-------------------------------------------------------------------------------+-------------+
| te              | RFC2822 e-mail format date/time e.g. Mon, 20 Jan 1972 10:21:36 1000           | datetime    |
+-----------------+-------------------------------------------------------------------------------+-------------+
| tg              | Global (day/month) format date/time e.g. 20/1/1972 10:21:36 AM 1:00           | datetime    |
+-----------------+-------------------------------------------------------------------------------+-------------+
| ta              | US (month/day) format date/time e.g. 1/20/1972 10:21:36 PM 10:30              | datetime    |
+-----------------+-------------------------------------------------------------------------------+-------------+
| tc              | ctime() format date/time e.g. Sun Sep 16 01:03:52 1973                        | datetime    |
+-----------------+-------------------------------------------------------------------------------+-------------+
| th              | HTTP log format date/time e.g. 21/Nov/2011:00:07:11 +0000                     | datetime    |
+-----------------+-------------------------------------------------------------------------------+-------------+
| ts              | Linux system log format date/time e.g. Nov 9 03:37:44                         | datetime    |
+-----------------+-------------------------------------------------------------------------------+-------------+
| tt              | Time e.g. 10:21:36 PM -5:30                                                   | time        |
+-----------------+-------------------------------------------------------------------------------+-------------+

All the above types can be combined with a cardinality:

.. code:: text

    "{:type}"     #< Cardinality: 1    (one; the normal case)
    "{:type?}"    #< Cardinality: 0..1 (zero or one  = optional)
    "{:type*}"    #< Cardinality: 0..* (zero or more = many0)
    "{:type+}"    #< Cardinality: 1..* (one  or more = many)

... whereas ``type`` stands for the actual type which should be used.

By default the ``,`` (comma) is used as a separator between multiple occurences
within the cardinality. However, one can specify their own separator.
Let's assume ``and`` should be used instead of ``,``:

.. code:: python

    from radish import custom_type, register_custom_type, TypeBuilder

    @custom_type("User", r"[A-Za-z0-9]+")
    def user_type(text):
        """
        Match a username and retrieve the ``User``
        """
        # some database lookup
        user = User(...)
        return user

    # register the NumberList type
    register_custom_type(UserList=TypeBuilder.with_many(
        user_type, listsep='and'))

Now you can use ``UserList`` as the type in the step pattern.
Follow the documentation to learn more about the ``custom_type()`` decorator.

.. _implementating_custom_step_patterns:

Implementing custom Step Patterns
`````````````````````````````````

Sometimes the built-in types are not sufficient or you want to express certain types
more specific to the domain the Steps are implemented for.
For that radish allows to register custom Step Pattern types.

For example the Step Implementations are to test a software with user accounts
in a database. The Step Pattern should match a username with alphanumeric characters
and return a ``User`` object:

.. code-block:: python

    from radish import custom_type

    @custom_type("User", r"[A-Za-z0-9]+")
    def user_type(text):
        """
        Match a username and retrieve the ``User``
        """
        # some database lookup
        user = User(...)
        return user

This *custom type* can then be used in a Step Pattern when registering
a Step Implementation function:

.. code-block:: python

    @when("the user {user:User} is loaded from the database")
    def when_load_user(step, user):
        ...


Regular Expression Syntax
.........................

Another way to define a Step Pattern is a compiled Regular Expression.
Usually more complex Patterns can be parsed with Regular Expressions.
However, it makes the Pattern less readable and is more error prone.
Thus, whenever possible use the `Format String Syntax`_.

Assume the Calculator example again where an Integer should be
injected into the Step Implementation:

.. code-block:: python

    @given(re.compile(r"the number (?P<nbr>[0-9]+)"))
    def given_a_number(step, nbr):
        ...

Implementing Hooks
------------------

Besides the Step Implementations the Hooks are the second *executable* part
during a radish run.

Hooks can be thought of as *setup* and *teardown* functions for
Features, Scenarios and Steps.

The following :ref:`Hooks <register_hooks_api>` exist:

* ``@for_all``
* ``@each_feature``
* ``@each_rule``
* ``@each_scenario``
* ``@each_step``

The above Hooks are called *Generator Hooks* and the ``setup``
and ``teardown`` part of the Hook is separated with an `yield`-statement:

.. code-block:: python

   from radish import each_scenario

   @each_scenario()
   def manage_db_connection(scenario):
      # setup the browser
      scenario.context.browser = create_mock_browser()
      yield
      # teardown the browser
      scenario.context.browser.destroy()

Or another example which uses a `with`-statement to manage a resource:

.. code-block:: python

   from radish import each_scenario

   @each_scenario()
   def manage_db_connection(scenario):
      # setup the database connection
      with DB.connect() as connection:
         scenario.context.connection = connection
         yield
      # database connection is automatically closed in the teardown part

The followings are simple Hooks which are either run ``before`` or ``after``
the model:

* ``@before.all``
* ``@after.all``
* ``@before.each_feature``
* ``@after.each_feature``
* ``@before.each_rule``
* ``@after.each_rule``
* ``@before.each_scenario``
* ``@after.each_scenario``
* ``@before.each_step``
* ``@after.each_step``

Hooks can be implemented similar to the Step Implementations:

.. code-block:: python

    from radish import before, after

    @before.each_scenario()
    def setup_calculator_numbers(scenario):
        scenario.context.numbers = []


    @after.each_scenario()
    def teardown_calculator_numbers(scenario):
        scenario.context.numbers.clear()


Hooks can also be :ref:`tag_syntax` specific:

.. code-block:: python

    @after.each_scenario(on_tags=["bad_case"])
    def cleanup_left_overs(scenario):
        scenario.context.database.clean()

Thus, the above Hook will only be called after each Scenario
which is tagged with ``@bad_case``


Hooks can be ordered by giving an integer as ``order`` keyword argument:

.. code-block:: python

    @before.each_scenario(order=1)
    def always_first(scenario):
        scenario.context.database.init()

See the detailed API here: :ref:`register_hooks_api`.

Running Feature Files
---------------------

The ``radish`` command line interface has a pretty straight forward
synopsis:

.. code-block:: text

    radish [OPTIONS] [FEATURE_FILES]...

As already briefly described in the `Feature Files`_ section, the
Feature Files which should be run can be passed as arguments to the
``radish`` cli.

A Feature File argument can either be a path to a Feature File or a
directory. If it's a directory it's recursively globbed for ``*.feature``-Files.

The most important option is the `Base Directory`_.
It has to be used if the Radish Python Modules are not in the directory named ``radish``
relative to the ``radish`` cli call.

One or more directories can be specified with the ``-b`` or ``--basedir`` option.

Early Exit on Failure
~~~~~~~~~~~~~~~~~~~~~

A radish run can be aborted immediately upon the first failure with the ``-e`` or ``--early-exit`` flag.

Shuffle the Scenarios
~~~~~~~~~~~~~~~~~~~~~

To ensure that Scenarios are not depending on the order they are run in
radish provides the ``--shuffle`` flag to randomly shuffle the order
of Scenario execution.

Filter specific Scenarios by Id
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Radish allows to run only specific Scenarios by filtering them by their Id.
The Scenario Ids start by ``1`` and are defined during the Parse Stage.

Use the ``-s`` or ``--scenarios`` option to filter. Multiple Scenario Ids
can be specified with commas, e.g.: ``radish -s 1,2 Calculator.feature``.

Filter specific Scenarios by Tag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``--tags`` option to filter for Scenarios matching the given
Tag Expression.

For example to filter for all ``@good_case`` Scenarios which are not
tagged with ``@database``:

.. code-block:: bash

    radish Admin-Panel.feature --tags 'good_case and not database'

Radish uses the `tag-expressions <https://pypi.org/project/tag-expressions>`_ library to evaluate the Tags.

Mark Feature and Scenarios as Work In Progress
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When working on a feature a Feature or Scenario is expected to fail.
To report this correctly in a run, radish supports the ``--wip`` flag.
In combination with ``--tags wip`` it will report a passed run if all the Scenarios
failed.

For example:

.. code-block:: bash

    radish Work-In-Progress.feature --wip --tags 'wip'

Show full Traceback for Step Failures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``-t`` or ``--with-traceback`` flag to enable full Tracebacks when a Step falis.

Specify the run marker
~~~~~~~~~~~~~~~~~~~~~~

Each radish run has a unique marker. It can be overriden with the ``-m`` or ``--marker`` option.
This marker can be used for logs or reports.

Inject run specific user data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It can be usful to inject specific user data into a radish run.
This can be achieved with the ``-u`` or ``--user-data`` option.
It accepts either a simple key or a key / value pair:

.. code-block:: bash

    radish Admin-Panel.feature -u BASIC_AUTH -u user=admin -u pwd=admin

The user data can be used within Step Implementations or Hooks by accessing
the ``world.config.user_data`` dictionary:

.. code-block:: python

    from radish import when, world

    @when("a user is logged in")
    def when_login(step):
        # check if basic auth is enabled
        if world.config.user_data["BASIC_AUTH"]:
            # login with username and password
            login(
                world.config.user_data["user"],
                world.config.user_data["pwd"]
            )

Dry Run
~~~~~~~

Use the ``-dry-run`` flag to dry run the given Feature Files.
In the dry run mode the Steps are matched with their Step Implementations,
but are not run.


Disable ANSI colors and Step rewrites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default radish colors the output and rewrites the Step when their result
is known.

The Step rewriting can be turned off by using the ``--no-step-rewrites`` flag.

All ANSI escape sequences, including colors, can be turned off by using
the ``--no-ansi`` flag.

Depending on the :ref:`Formatter <formatters_usage>` used one of the above options
might be more useful than the other.

Log Markers to syslog
~~~~~~~~~~~~~~~~~~~~~

Radish can log it's execution to syslog with the ``--with-syslog-markers`` flag.
This can particularly be useful if the software under test does that, too.
It allows to seperate which application logs happened in which Step.

Generating Reports
------------------

cucumber JSON report
~~~~~~~~~~~~~~~~~~~~

jUnit XML report
~~~~~~~~~~~~~~~~

.. _formatters_usage:

Formatters
----------

Gherkin Formatter
~~~~~~~~~~~~~~~~~

Dots Formatter
~~~~~~~~~~~~~~

Testing
-------

Radish provides a tool `radish-test` which can be used to test the :ref:`Step Patterns <step_pattern_usage>`
used in the Step Implementations within a `Base Directory`_.

The way it works is that one can specify example Step Text and the expectation with which
Step Implementation it should match and which parts of the Step Text are parsed into
which Step Implementation Arguments.

`radish-test` uses YAML *matcher config files* for that.
The following example depicts a matcher config file which asserts that the
`Given there is a Step` Step Text will match the `given_there_is_a_step`
Step Implementation Function.

.. code-block:: yaml

   - step: Given there is a Step
     should_match: given_there_is_a_step


The matcher config file syntax can be dscribed as the following:

.. code-block:: yaml

   - step: <sample-step-text>
   - [should_match | should_not_match]: <step-impl-func>
   [ - with_arguments:
       <args>...
   ]

Let's get into the details of the different testing use-cases in the following sections.

Assert that a Step Text should match a Step Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following matcher config file will assert that the `Given there is a Step`
Step Text matches the `given_there_is_a_step` Step Implementation Function:

.. code-block:: yaml

   - step: Given there is a Step
     should_match: given_there_is_a_step

If that's the case you'll get an output like the following:

.. code-block::

   >> STEP 'Given there is a Step' SHOULD MATCH given_there_is_a_step    ✔

If that's not the case `radish-test` will tell what the exact error was:
either the Step Text wasn't matched against any Step Implementation
or the Step Text was matched against the wrong Step Implementation:

.. code-block::

   >> STEP 'Given there is a Step' SHOULD MATCH given_there_is_a_step    ✘
     - Expected Step Text didn't match any Step Implementation


.. code-block::

   >> STEP 'Given there is a Step' SHOULD MATCH given_there_is_a_step    ✘
     - Expected Step Text matched another_step instead of given_there_is_a_step


Assert that a Step Text should match a Step Implementation with Arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`radish-test` is also able to test against the particular values of the parsed
arguments from the Step Pattern.

The following matcher config file will assert that the `Given there is the number 42`
will match the `given_there_is_a_number` Step Implementation and that
the `42` argument is correctly passed to the Step Implementation:

.. code-block:: yaml

   - step: Given there is the number 42
     should_match: given_there_is_a_number
     with_arguments:
       - number: 42


For reference the `given_there_is_a_number` Step Implementation could look like the following:

.. code-block:: python

   @given("there is the number {:int}")
   def given_there_is_a_number(step, number):
       ...

If the Step Text matches correctly `radish-test` will output the following:

.. code-block::

   >> STEP 'Given there is the number 42' SHOULD MATCH given_there_is_a_number    ✔

There are several errors that could occur here:

#. the Step Text was matched against non or the wrong Step Implementation
#. the `number` argument was not matched
#. the `number` argument is matched against the wrong argument
#. the `number` argument has the wrong value

In all of the above cases `radish-test` will output the exact error.

Some of those errors will occur because `radish-test` doesn't know how to interpret
the simple argument specification of `- number: 42` - maybe because custom types
where used for the Step Arguments using :ref:`Custom Types <implementating_custom_step_patterns>`.

In this case this simple specification syntax can be extended using the following syntax:

.. code-block:: yaml

   - step: Given there is the User Giovanni
     should_match: given_the_user
     with_arguments:
       - user:
           type: User
           value: User(name=Giovanni)
           use_repr: True


The above `user` argument tells `radish-test` that the parsed Step Argument `user`
will be of the custom type `User` and it's `__repr__`-representation should be `User(name=Giovanni)`.

Assert that a Step Text should not match a Step Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Like `radish-test` can match that a Step Text *should match* a Step Implementation
it can also assert that a Step Text *should not match* a Step Implementation.

For that the `should_not_match` instead of `should_match` keyword can be used:

.. code-block:: yaml

   - step: Given there isn't this Step
     should_not_match: given_there_is_a_step

If the Step Text wasn't matched against the `given_there_is_a_step` `radish-test` will
output the following:

.. code-block::

   >> STEP 'Given there isn't this Step' SHOULD NOT MATCH given_there_is_a_step    ✔


In the error case where it actually matched against `given_there_is_a_step` the following
will be reported:

.. code-block::

   >> STEP 'Given there isn't this Step' SHOULD NOT MATCH given_there_is_a_step    ✘
     - Expected Step Text matched given_there_is_a_step but it shouldn't

Show not covered Step Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`radish-test` provides two useful command line options to help increase the coverage
on the tested Step Implementations.
Those are `--show-missing` and `--show-missing-templates`.

The first one `--show-missing` lists all missing Step Implementations per
module within the Base Directory:

.. code-block::

   Missing from: radish/steps.py
     - given_there_is_a_step:3
     - given_number:8

However, much more useful when trying to increase the coverage is the second option
`--show-missing-templates`. With this flag set `radish-test` will output
templates for a matcher config with which every Step Implementation
is at least covered by a simple test case:

.. code-block::

   Add the following to your matcher-config.yml to cover the missing Step Implementations:

   # testing Step Implementation at .*?/radish/steps.py:3
   - step: "<insert sample Step Text here>"
     should_match: given_there_is_a_step


   # testing Step Implementation at .*?/radish/steps.py:8
   - step: "<insert sample Step Text here>"
     should_match: given_number
     with_arguments:
       - first: <insert argument value here>
       - second: <insert argument value here>
