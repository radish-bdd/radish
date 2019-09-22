.. _feature_file_syntax:

Feature File Syntax
===================

radish aims to be fully `Gherkin`_ compatible.
The current :class:`Feature File Parser <radish.parser.FeatureFileParser>` fully supports Gherkin v6.

The following sections document the extended Gherkin syntax supported by radish.

radish uses an EBNF grammer to generate a parser. The EBNF file can be found here: `EBNF Grammer`_.


Feature File
------------

A Feature File is a simple plain text file containing a single radish `Feature`_.
One or more Feature Files can be run using the `radish` command line tool.

Feature
-------

A Feature is the single root element of every `Feature File`_.

It consits of a *short description*, an optional *description*, an optional *Background*,zero or more *Rules*, zero or more *Scenarios* and it can have *Tags*.
The Feature syntax can be defined as:

.. code-block:: gherkin

    [optional Tags]
    Feature: <short description>
        [optional multi-line description]

        [optional Background block]

        [optional Rules]

        [optional Scenarios]

A simple Feature with a single Scenario might look like this:

.. code-block:: gherkin

    Feature: Calculator Addition
        In order to support all four elementary
        binary operations the calculator shall
        implement the binary addition operator.

        Scenario: Adding two positive integers
            Given the integer 5
            And the integer 2
            When the integers are added
            Then the sum is 7

Rule
----

A Rule is a logical block in a `Feature`_ to group one or more Scenarios in
a *business rule*. A *business rule* can be used to express additional information
for the Feature and Scenarios.

A Rule consists of a *short description* and zero or more *Scenarios*:

.. code-block:: gherkin
   :emphasize-lines: 4

    Feature: ...
        ...

        Rule: Calcuations with Integers
            [optional Scenarios]


A `Feature`_ always consists of a Default Rule.
This Default Rule has no *short description* and contains all the Scenarios
in a Feature which are not part of an explicit Rule.

A simple Rule for the *Calculator Addition*-Feature might look like this:

.. code-block:: gherkin
   :emphasize-lines: 6, 14

    Feature: Calculator Addition
        In order to support all four elementary
        binary operations the calculator shall
        implement the binary addition operator.

        Rule: Addition with Integers

            Scenario: Adding two positive integers
                Given the integer 5
                And the integer 2
                When the integers are added
                Then the sum is 7

        Rule: Addition with Floating Point Numbers

            Scenario: ...

Background
----------

A Background is a special case of a `Scenario`_ which is executed
prior to every other Scenario in the same `Feature File`_.
The Background can be used to set up a precondition which must be met
before executed the Scenarios.

Prefer a Background over a Hook if the Steps in the Background
matter to the outcome of the Scenarios.

A Background consists of an optional *short description* and Steps:

.. code-block:: gherkin

    Background: [optional short description]
        [zero or more Steps]

A simple Background might look like this:

.. code-block:: gherkin
   :emphasize-lines: 6

    Feature: Calculator Addition
        In order to support all four elementary
        binary operations the calculator shall
        implement the binary addition operator.

        Background:
            Given the calculator is started

        Scenario: Adding two positive integers
            Given the integer 5
            And the integer 2
            When the integers are added
            Then the sum is 7

Scenario
--------

A Scenario or Example is used to express a test-case within a `Feature`_ or `Rule`_.
A Scenario must consist of a *short description* and zero or more Steps and can have
Tags assigned to it:

.. code-block:: gherkin

    [optional Tags]
    [Scenario|Example]: <short description>
        [zero or more Steps]


Scenarios inherit the Tags from the Feature they are declared in.
If a `Background`_ is defined in the same `Feature File`_, the Background
will always be run prior to every Scenario.

Scenario Outline
----------------

A Scenario Outline or Example Outline is used to parametrize a Scenario with
multiple Parameters. Those parameters can be used in the Steps.
A Scenario Outline is not run directly, but the Scenario it generates.
The Scenario Outline Parameters are defined in an Example Table.
Every row in the Example Table will generate a Scenario.

The syntax can be described as the following:

.. code-block:: gherkin

    [optional Tags]
    [Scenario Outline|Example Outline]: <short description>
        [zero or more Steps referencing parameters from the Table]

    Examples:
        [Header Row]
        [one or more Example Rows]

The *Header Row* and *Example Rows* use the vertical bar symbol ``|`` to delimit columns.
The Example Parameters can be used in the Step by their name (defined in the *Header Row*) surrounded by ``<`` and ``>``.

The following snippets shows an example of a Scenario Outline:

.. code-block:: gherkin
   :emphasize-lines: 6

    Feature: Calculator Addition
        In order to support all four elementary
        binary operations the calculator shall
        implement the binary addition operator.

        Scenario Outline: Adding two positive integers
            Given the integer <lhs int>
            And the integer <rhs int>
            When the integers are added
            Then the sum is <sum>

        Examples:
            | lhs int | rhs int | sum |
            | 5       | 2       | 7   |
            | 21      | 21      | 42  |

Scenario Loop
-------------

A Scenario Loop or Example Loop is used repeat the execution of a Scenario multiple times. This is particularly useful to test for flaky regression bugs.

The number of repetitions can be specified with the ``Iterations`` keyword after the Scenario Loop definition:

.. code-block:: gherkin

    [optional Tags]
    [Scenario Loop|Example Loop]: <short description>
        [zero or more Steps]

    Iterations: <repetitions>

Each repetition will be generated to its own identical Scenario.

Scenario Preconditions
----------------------

A Scenario Precondition is a special `Tag`_ which is used to define
a Precondition Scenario for a Scenario.
This *Precondition Scenario* is always run after the `Background`_ but before the `Scenario`_.
The `Feature File`_ the *Precondition Scenario* is defined in can be any Feature File relativ to the Feature File it's used. It can even be defined in the same Feature File.

.. code-block:: gherkin
   :emphasize-lines: 2

    # NOTE: Make sure batteries are included
    @precondition(Calculator-Setup.feature: Include Batteries)
    Scenario: Addition with Integers
        ...

Use Scenario Preconditions with caution. They introduce additional complexity
and intransparency to your tests - attributes which are definitely in conflict with good BDD tests.

.. _step_syntax:


Step
----

Steps are the central piece of a `Feature File`_.
They are the only parts which can be directly translated to runnable code.

A Step consists of a keyword and a text.
The keyword has to be one of:

* ``Given``
* ``When``
* ``Then``

or

* ``And``
* ``But``

which both indicate that the keyword of the preceeding Step shall be used.

.. code-block:: gherkin

    [Given|When|Then|And|But] <text>

The Step Text is used to describe what the Step shall do.
During a radish run Steps are matched with the Step Implementation.
If the Step Implementation is run and passes the Scenario and eventually the
Feature pass.

.. _tag_syntax:

Tag
---

Tags can be used to annotate Features and Scenarios for filtering and/or
the assignment of special behaviors.
A Tag always starts with the at symbol ``@`` followed by a name without a white space.
Tags can be placed on the same and/or multiple lines:

.. code-block:: gherkin
   :emphasize-lines: 1, 4, 5, 9, 10

    @addition @wip
    Feature: Calculator Addition

        @good-case
        @integers
        Scenario: Addition with Integers
            ...

        @bad-case
        @integers
        Scenario: Addition with an Integer and a Letter
            ...


The radish command line tool is able to filter for Scenarios to run depending
on their assigned Tags. A Scenario always inherits the Tag from the Feature containing it.
Thus, filtering for ``@addition`` will yield both of the above Scenarios even though they
don't contain this Tag directly.

Hooks can also be specialized to only be run for Features or Scenarios that contain special Tags.

Tag Constants
-------------

Features and Scenarios (including `Scenario Outline`_ and `Scenario Loop`_)
can be annotated with *Tag Constants*. Those are Tags which additionally to the
name also have a value:

.. code-block:: gherkin
   :emphasize-lines: 1, 4

    @constant(number: 5)
    Feature: Calculator Addition

        @constant(addend: 5)
        Scenario: Addition with Integers
            ...

A Scenario inherits the Constants from the Feature.
The Constants can be used in in the Steps using the `${name}` syntax:

.. code-block:: gherkin
   :emphasize-lines: 1, 4, 6

    @constant(number: 5)
    Feature: Calculator Addition

        @constant(addend: 2)
        Scenario: Addition with Integers
            When the numbers ${number} and ${addend} are summed
            Then the result is 7

All the Constants are resolved during the Step Implementation Matching Phase.

Comment
-------

A comment is a line in the `Feature File`_ which is not parsed and can be
used to annotate code in the Feature File.
A comment starts with the hashtag symbol ``#`` and lasts until the end of the line.
A comment line mustn't contain anything prior to the hashtag symbol.

.. code-block:: gherkin
   :emphasize-lines: 3

    Feature: Calculator Addition

        # NOTE: that's the most important business rule
        Rule: Addition with Integers

            ...

Language Comments
-----------------

Radish has Multi-Language Support for the parsing of Feature Files.
The language to use to parse a Feature File can be specified on the first line
of the Feature File as a *Language Comment*:

.. code-block:: gherkin
   :emphasize-lines: 1

    # language: <language_code>
    ...

The ``<language_code>`` specifies which language to use.
By default ``en`` is used for English.

Assuming the *Calculator* Feature from above should be written in German:

.. code-block:: gherkin
   :emphasize-lines: 1

    # language: de
    Funktionalität: Taschenrechner Addition

        Szenario: Addieren von Ganzzahlen
            Gegeben sei die Zahl 5
            Und die Zahl 2
            Wenn die Zahlen addiert werden
            Dann soll die Summe 7 ergeben

.. _Gherkin: https://cucumber.io/docs/gherkin/reference/
.. _EBNF Grammer: https://github.com/radish-bdd/radish/blob/master/src/radish/parser/grammer.g
