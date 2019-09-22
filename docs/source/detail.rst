Implementation Details
======================

This part of the documentation shows radish implementation details.

Stages of a ``radish`` Run
--------------------------

A ``radish`` Run consists of the following Stages:

1. Parsing Command Line Arguments and Configuration
2. Loading Extensions according the the Configuration
3. Parsing Feature Files
4. Loading of User Base Directory Python Modules
5. Running Feature Files

Stage 1 - Parsing Command Line Arguments and Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first Stage of a ``radish`` Run is the parsing of the Command Line Arguments
given by the user.

These Arguments are pre-processed by radish and made available to all components,
including the :ref:`base_directory_usage` Modules, via the ``world.config`` object.

Stage 2 - Loading Extensions according the the Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After parsing of the Configuration in Stage 1, Stage 2
loads all necessary radish Extensions.
Usually Extensions are only loaded if a certain configuration is set.
For example the syslog-marker Extension is only loaded if the ``--with-syslog-markers``
flag is given.

Stage 3 - Parsing Feature Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Stage 3 is responsible of the Feature File parsing.
This Step just parses the Feature File Syntax and transforms it to an Abstract Syntax Tree (AST)
which is then used in later Stages to actually run the Feature File.
At this Stage no Steps are matched with its Step Implementation.

Stage 4 - Loading of User Base Directory Python Modules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If all Feature Files parsed sucessfully the :ref:`base_directory_usage` Modules
are loaded. Thus, all Step Implementations and Hooks are registered.

Stage 5 - Running Feature Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The end Stage is the most important one. It's responsible for running the Feature Files.
This Stage has the following tasks:

1. step through the Feature Files
2. call the appropriate Hooks at the appropriate time
3. call the Step Implementations for the Steps
