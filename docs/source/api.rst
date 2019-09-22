API
===

.. module:: radish

This part of the documentation lists the full API reference of all public
classes and functions.

Decorators
----------

.. _register_step_implementations_api:

Register Step Implementations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: radish.given

.. autofunction:: radish.when

.. autofunction:: radish.then

.. autofunction:: radish.step

.. _register_hooks_api:

Register Hooks
~~~~~~~~~~~~~~

.. autofunction:: radish.before.all

.. autofunction:: radish.after.all

.. autofunction:: radish.before.each_feature

.. autofunction:: radish.after.each_feature

.. autofunction:: radish.before.each_scenario

.. autofunction:: radish.after.each_scenario

.. autofunction:: radish.before.each_step

.. autofunction:: radish.after.each_step


Register Step Pattern Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: radish.custom_type

Utilities
---------

.. autodata:: radish.world
   :annotation:

.. autodecorator:: radish.world.pick

Models
------

.. autoclass:: radish.models.State
   :members:
   :undoc-members:

.. autoclass:: radish.models.Step
   :members:

.. autoclass:: radish.models.Scenario
   :members:

.. autoclass:: radish.models.Feature
   :members:

.. autoclass:: radish.models.Tag
   :members:

Exceptions
----------

.. autoexception:: RadishError


Parser
------

.. autoclass:: radish.parser.FeatureFileParser
   :members:

Runner
------

.. autoclass:: radish.runner.Runner
   :members:
