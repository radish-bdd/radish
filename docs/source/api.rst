API
===

.. module:: radish

This part of the documentation lists the full API reference of all public
classes and functions.

Package Top-Level Exports
-------------------------

The following packages can be imported from the radish package:

.. testcode::

    from radish import (
        # Step Decorators
        given,
        when,
        then,
        step,

        # Hooks & Terrain
        world,
        before,
        after,
        for_all,
        each_feature,
        each_rule,
        each_scenario,
        each_step,

        # Step Pattern Types
        custom_type,
        register_custom_type,
        TypeBuilder,

        # The radish parser
        FeatureFileParser,

        # Models
        Feature,
        Rule,
        DefaultRule,
        Background,
        Scenario,
        ScenarioOutline,
        ScenarioLoop,
        Step,
        Tag,
        PreconditionTag,
        ConstantTag,

        # Exception Types
        RadishError,

        # The radish-bdd package version
        __version__
    )

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

.. autofunction:: radish.for_all

.. autofunction:: radish.each_feature

.. autofunction:: radish.each_rule

.. autofunction:: radish.each_scenario

.. autofunction:: radish.each_step

.. autofunction:: radish.before.all

.. autofunction:: radish.after.all

.. autofunction:: radish.before.each_feature

.. autofunction:: radish.after.each_feature

.. autofunction:: radish.before.each_rule

.. autofunction:: radish.after.each_rule

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
