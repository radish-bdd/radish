.. _hooks:

Hooks
=====

Radish provides some decorator to register method which are called before features, scenarios and steps.
This methods could be used to setup a specific test environment or similar.

The following hooks are provided:

+-----------------------+----------------------+----------------------------------------------------+
| Decorator             | Arguments            | Description                                        |
+=======================+======================+====================================================+
| @before.all           | *list*: features     | Called once before radish runs the first feature   |
|                       | *str*: marker        |                                                    |
+-----------------------+----------------------+----------------------------------------------------+
| @after.all            | *list*: features     | Called once after radish finished the last feature |
|                       | *str*: marker        |                                                    |
+-----------------------+----------------------+----------------------------------------------------+
| @before.each_feature  | *Feature*: feature   | Called before each feature will start to run       |
+-----------------------+----------------------+----------------------------------------------------+
| @after.each_feature   | *Feature*: feature   | Called after each feature wasrun                   |
+-----------------------+----------------------+----------------------------------------------------+
| @before.each_scenario | *Scenario*: scenario | Called before each scenario will start to run      |
+-----------------------+----------------------+----------------------------------------------------+
| @after.each_scenario  | *Scenario*: scenario | Called after each scenario was run                 |
+-----------------------+----------------------+----------------------------------------------------+
| @before.each_step     | *Step*: step         | Called before each step will start to run          |
+-----------------------+----------------------+----------------------------------------------------+
| @after.each_step      | *Step*: step         | Called after each step was run                     |
+-----------------------+----------------------+----------------------------------------------------+

For example you could use the hooks to setup a test environment

.. code-block:: python

   # -*- coding: utf-8 -*-
   from radish import before, after
   from mock import Mock

   from project.clientregistry import ClientRegistry

   @before.each_scenario
   def setup_test_env(scenario):
       """
           Setup the test environment by mocking the HTTP server.
           And initialize the Client Registry
       """
       scenario.context.server = Mock(send=lambda: True, receive:lambda: {"status": "ok"})
       ClientRegistry().initialize(max_connections=10, protocol=ClientRegistry.Protocols.TCP)


    @after.each_scenario
    def teardown_test_env(scenario):
        """
           Tear down the test environment by resetting the client registry
        """
        ClientRegistry().reset()
